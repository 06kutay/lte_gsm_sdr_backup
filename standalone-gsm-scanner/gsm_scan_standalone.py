#!/usr/bin/env python3
"""
standalone_gsm_scanner.py
-------------------------
A self-contained, lightweight Python script for GSM frequency scanning, 
cell identity decoding (CID, LAC, MCC, MNC), and neighbor cell discovery (2G/3G/4G).

Prerequisites:
  - gr-gsm (grgsm_scanner, grgsm_livemon_headless)
  - tshark (for offline SI2quater LTE/3G neighbor decoding)
  - python3

No complex microservices, docker containers, or gRPC frameworks required.
"""

import os
import sys
import time
import re
import json
import socket
import struct
import argparse
import subprocess
from datetime import datetime

# Helper: DL Frequency Calculator
def get_arfcn_info(arfcn):
    # GSM900 Band
    if 1 <= arfcn <= 124:
        return "GSM900", 935.0 + 0.2 * arfcn
    elif 975 <= arfcn <= 1023:
        return "GSM900", 935.0 + 0.2 * (arfcn - 1024)
    elif arfcn == 0:
        return "GSM900", 935.0
    # DCS1800 Band
    elif 512 <= arfcn <= 885:
        return "DCS1800", 1805.2 + 0.2 * (arfcn - 512)
    return "Unknown", 0.0

# Helper: DL Frequency to Band & Frequency for LTE EARFCNs (3GPP TS 36.101)
def get_earfcn_info_lte(earfcn):
    if 0 <= earfcn <= 599:
        return 1, 2110.0 + 0.1 * earfcn
    elif 1200 <= earfcn <= 1949:
        return 3, 1805.0 + 0.1 * (earfcn - 1200)
    elif 2750 <= earfcn <= 3449:
        return 7, 2620.0 + 0.1 * (earfcn - 2750)
    elif 6150 <= earfcn <= 6449:
        return 20, 791.0 + 0.1 * (earfcn - 6150)
    elif 9210 <= earfcn <= 9659:
        return 28, 758.0 + 0.1 * (earfcn - 9210)
    return None, None

# Helper: DL Frequency to Band & Frequency for UMTS UARFCNs (3GPP TS 25.104)
def get_uarfcn_info_umts(uarfcn):
    if 10562 <= uarfcn <= 10838:
        return 1, 2110.0 + 0.2 * (uarfcn - 10562)
    elif 2937 <= uarfcn <= 3088:
        return 8, 925.0 + 0.2 * (uarfcn - 2937)
    elif uarfcn == 2997:
        return 1, 2110.0
    elif uarfcn == 10813:
        return 8, 940.0
    return None, None

# Helper: Estimate mobile network operator based on ARFCN (Turkey Specific)
def estimate_operator(arfcn, band):
    if band == "GSM900":
        if 1 <= arfcn <= 35:
            return "Turkcell"
        elif 36 <= arfcn <= 70:
            return "Vodafone"
        elif 71 <= arfcn <= 105:
            return "Turk Telekom"
    elif band == "DCS1800":
        if 512 <= arfcn <= 586:
            return "Vodafone"
        elif 587 <= arfcn <= 661:
            return "Turk Telekom"
        elif 662 <= arfcn <= 736:
            return "Turkcell"
    return "Unknown"

# Native Python GSMTAP Header & Layer 3 Parser
def parse_gsmtap_packet(data: bytes):
    if len(data) < 16:
        return None
    
    # GSMTAP Header parsing
    version = data[0]
    hdr_len = data[1]
    header_size = hdr_len * 4
    
    if len(data) < header_size:
        return None
        
    arfcn_raw = (data[4] << 8) | data[5]
    arfcn = arfcn_raw & 0x7fff
    
    signal_dbm = -100
    if len(data) >= 14:
        signal_dbm = struct.unpack('b', bytes([data[13]]))[0]
        
    payload = data[header_size:]
    
    # Ensure it is a Layer 3 Radio Resource Management (RR) packet
    # payload[0] = LAPDm address (0x01/0x03), payload[1] = LAPDm control (UI=0x03) or protocol discriminator 0x06 directly
    # Depending on gr-gsm framing:
    l3_msg = None
    if len(payload) >= 3 and payload[1] == 0x06:
        l3_msg = payload
    elif len(payload) >= 5 and payload[3] == 0x06:
        l3_msg = payload[2:]
        
    if not l3_msg or len(l3_msg) < 3:
        return None
        
    msg_type = l3_msg[2]
    
    # 1. System Information Type 3 (SI3) -> CID, LAC, MCC, MNC
    if msg_type == 0x1b:
        try:
            cell_id = (l3_msg[3] << 8) | l3_msg[4]
            mcc_d1 = l3_msg[5] & 0x0f
            mcc_d2 = (l3_msg[5] >> 4) & 0x0f
            mcc_d3 = l3_msg[6] & 0x0f
            mcc = f"{mcc_d1}{mcc_d2}{mcc_d3}"
            
            mnc_d1 = l3_msg[7] & 0x0f
            mnc_d2 = (l3_msg[7] >> 4) & 0x0f
            mnc_d3 = (l3_msg[6] >> 4) & 0x0f
            mnc = f"{mnc_d1}{mnc_d2}" if mnc_d3 == 0x0f else f"{mnc_d1}{mnc_d2}{mnc_d3}"
            lac = (l3_msg[8] << 8) | l3_msg[9]
            
            return {
                "type": "SI3",
                "arfcn": arfcn,
                "cell_id": cell_id,
                "lac": lac,
                "mcc": mcc,
                "mnc": mnc,
                "plmn": f"{mcc}{mnc}",
                "signal_dbm": signal_dbm
            }
        except Exception:
            pass
            
    # 2. System Information Type 2 (SI2) -> 2G Neighbor List (BA list)
    elif msg_type == 0x1a:
        try:
            # Format 0 cell channel description
            if (l3_msg[6] & 0xc0) == 0x00:
                ba_list = []
                for i in range(16):
                    byte_val = l3_msg[6 + i]
                    for bit in range(8):
                        if (byte_val >> bit) & 1:
                            ba_list.append(i * 8 + bit + 1)
                return {
                    "type": "SI2",
                    "arfcn": arfcn,
                    "ba_list": sorted(ba_list),
                    "signal_dbm": signal_dbm
                }
        except Exception:
            pass
            
    return None

# ASCII Table Formatting Helper
def print_table(headers, rows):
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    print(border)
    print("|" + "|".join(f" {h:<{widths[idx]}} " for idx, h in enumerate(headers)) + "|")
    print(border)
    for row in rows:
        print("|" + "|".join(f" {str(val):<{widths[idx]}} " for idx, val in enumerate(row)) + "|")
    print(border)

# Main Scan Orchestration
def run_gsm_scanner(sdr_type, serial, gain, band, speed):
    print(f"\n[*] Geniş bant tarama başlatılıyor ({band})...")
    
    # Auto-detect driver arguments
    args_str = f"driver=lime,serial={serial}" if sdr_type == "limesdr" else f"usrp,serial={serial}"
    cmd = f"grgsm_scanner --args=\"{args_str}\" -g {gain} -b {band} --speed={speed} -v"
    
    print(f"[CMD] {cmd}")
    process = subprocess.Popen(
        cmd,
        shell=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )
    
    detected_arfcns = []
    while True:
        line = process.stdout.readline()
        if not line:
            if process.poll() is not None:
                break
            continue
            
        line_strip = line.strip()
        print(f"  [RAW] {line_strip}")
        
        # Parse output: "ARFCN:   60, Freq:  947.0M, CID:  7349, LAC: 33006, MCC: 286, MNC:   1, Pwr: -64"
        m = re.search(r"ARFCN:\s*(\d+)", line_strip)
        if m:
            arfcn = int(m.group(1))
            if arfcn not in detected_arfcns:
                detected_arfcns.append(arfcn)
                
    process.wait()
    return sorted(detected_arfcns)

def decode_arfcn(arfcn, sdr_type, serial, gain, antenna, timeout):
    band, freq_mhz = get_arfcn_info(arfcn)
    freq_hz = freq_mhz * 1e6
    print(f"\n[*] ARFCN {arfcn} ({band} - {freq_mhz:.1f} MHz) dinleniyor... (Süre: {timeout} saniye)")
    
    pcap_path = f"/tmp/gsm_live_{arfcn}.pcap"
    if os.path.exists(pcap_path):
        os.remove(pcap_path)
        
    # Start TShark loopback capture in background
    tshark_cmd = f"tshark -i lo -f \"udp port 4729\" -w {pcap_path}"
    tshark_proc = subprocess.Popen(tshark_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Start grgsm_livemon_headless
    dev_args = f"driver=lime,serial={serial}" if sdr_type == "limesdr" else f"usrp,serial={serial}"
    if antenna:
        dev_args += f",rxant={antenna}"
        
    livemon_cmd = f"grgsm_livemon_headless -f {freq_hz} --args=\"{dev_args}\" -g {gain}"
    print(f"[CMD] {livemon_cmd}")
    livemon_proc = subprocess.Popen(livemon_cmd, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    
    # Open local UDP socket to sniff GSMTAP packets in real-time
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.settimeout(0.5)
    try:
        sock.bind(("127.0.0.1", 4729))
    except Exception as e:
        print(f"[-] Hata: 4729 UDP portu dinlenemedi: {e}")
        livemon_proc.kill()
        tshark_proc.kill()
        return None
        
    start_time = time.time()
    cell_info = {
        "arfcn": arfcn,
        "band": band,
        "freq_mhz": freq_mhz,
        "success": False,
        "cell_id": "N/A",
        "lac": "N/A",
        "mcc": "N/A",
        "mnc": "N/A",
        "operator": estimate_operator(arfcn, band),
        "rssi": -100,
        "neighbors_2g": [],
        "neighbors_3g_uarfcns": [],
        "neighbors_4g_earfcns": []
    }
    
    has_si3 = False
    has_si2 = False
    
    while time.time() - start_time < timeout:
        try:
            data, addr = sock.recvfrom(2048)
        except socket.timeout:
            continue
            
        parsed = parse_gsmtap_packet(data)
        if parsed:
            cell_info["rssi"] = max(cell_info["rssi"], parsed["signal_dbm"])
            
            if parsed["type"] == "SI3" and not has_si3:
                has_si3 = True
                cell_info["cell_id"] = parsed["cell_id"]
                cell_info["lac"] = parsed["lac"]
                cell_info["mcc"] = parsed["mcc"]
                cell_info["mnc"] = parsed["mnc"]
                cell_info["success"] = True
                print(f"  [+] SI3 Alındı -> CID: {parsed['cell_id']}, LAC: {parsed['lac']}, PLMN: {parsed['plmn']}")
                
            elif parsed["type"] == "SI2" and not has_si2:
                has_si2 = True
                cell_info["neighbors_2g"] = parsed["ba_list"]
                print(f"  [+] SI2 Alındı -> 2G Komşu BA Listesi ({len(parsed['ba_list'])} adet): {parsed['ba_list']}")
                
    sock.close()
    
    # Gracefully terminate livemon and tshark
    livemon_proc.terminate()
    tshark_proc.terminate()
    try:
        livemon_proc.wait(timeout=2)
        tshark_proc.wait(timeout=2)
    except Exception:
        livemon_proc.kill()
        tshark_proc.kill()
        
    # Parse SI2quater (3G/4G Neighbors) offline from the PCAP file using TShark
    if os.path.exists(pcap_path) and os.path.getsize(pcap_path) > 100:
        try:
            tshark_out = subprocess.check_output(f"tshark -r {pcap_path} -V", shell=True, text=True, stderr=subprocess.DEVNULL)
            
            # Extract EARFCNs (4G)
            earfcns = [int(x) for x in re.findall(r"EARFCN:\s*(\d+)", tshark_out)]
            # Extract UARFCNs (3G)
            uarfcns = [int(x) for x in re.findall(r"FDD UARFCN:\s*(\d+)", tshark_out)]
            
            cell_info["neighbors_4g_earfcns"] = sorted(list(set(earfcns)))
            cell_info["neighbors_3g_uarfcns"] = sorted(list(set(uarfcns)))
            
            if earfcns:
                print(f"  [+] SI2quater Alındı -> 4G LTE Komşu EARFCN Listesi: {cell_info['neighbors_4g_earfcns']}")
            if uarfcns:
                print(f"  [+] SI2quater Alındı -> 3G UMTS Komşu UARFCN Listesi: {cell_info['neighbors_3g_uarfcns']}")
        except Exception as e:
            print(f"  [-] TShark PCAP okuma hatası: {e}")
        finally:
            try: os.remove(pcap_path)
            except Exception: pass
            
    return cell_info

def main():
    parser = argparse.ArgumentParser(description="Standalone GSM/2G/3G/4G Neighbor Cell Discovery Tool")
    parser.add_argument("arfcns", nargs="*", type=int, help="Optional specific ARFCN list to scan. If not set, wide scan runs first.")
    parser.add_argument("--sdr", type=str, default="usrp", choices=["usrp", "limesdr"], help="SDR type (default: usrp)")
    parser.add_argument("--serial", type=str, default="2511171", help="SDR USB serial number")
    parser.add_argument("--gain", type=int, default=35, help="SDR RX gain (default: 35)")
    parser.add_argument("--band", type=str, default="GSM900", choices=["GSM900", "DCS1800"], help="Frequency band for auto-scan (default: GSM900)")
    parser.add_argument("--antenna", type=str, default="", help="Antenna port override (e.g. TX/RX, RX2, LNAW, LNAH)")
    parser.add_argument("--timeout", type=int, default=15, help="Listening timeout per channel in seconds (default: 15)")
    parser.add_argument("--speed", type=int, default=20, help="Scan speed parameter for grgsm_scanner (default: 20)")
    parser.add_argument("--output", type=str, default="gsm_scan_results.json", help="Path to save JSON results")
    
    args = parser.parse_args()
    
    # 1. Determine target ARFCNs
    target_arfcns = []
    if args.arfcns:
        target_arfcns = args.arfcns
        print(f"[*] Özel olarak tanımlanmış ARFCN listesi taranacak: {target_arfcns}")
    else:
        # Run wide band scan to discover active ARFCNs
        target_arfcns = run_gsm_scanner(args.sdr, args.serial, args.gain, args.band, args.speed)
        print(f"[*] Geniş bant taramada aktif tespit edilen kanallar: {target_arfcns}")
        
    if not target_arfcns:
        print("[-] Aktif veya taranacak geçerli hiçbir GSM kanalı bulunamadı. Program sonlandırılıyor.")
        sys.exit(0)
        
    # 2. Decode active channels
    cells = []
    for idx, arfcn in enumerate(target_arfcns, 1):
        print(f"\n[Aşama {idx}/{len(target_arfcns)}]")
        res = decode_arfcn(arfcn, args.sdr, args.serial, args.gain, args.antenna, args.timeout)
        if res:
            cells.append(res)
            
    # 3. Print Results Summary
    print("\n" + "=" * 90)
    print("                      📊 GSM STANDALONE SCAN SUMMARY REPORT 📊")
    print("=" * 90)
    
    # Table 1: Cell Inventory
    h_inv = ["ARFCN", "Band", "Frekans", "CID", "LAC", "MCC", "MNC", "Operatör", "RSSI (dBm)"]
    r_inv = []
    for c in cells:
        if c["success"]:
            r_inv.append([
                c["arfcn"], c["band"], f"{c['freq_mhz']:.1f} MHz", c["cell_id"], c["lac"], c["mcc"], c["mnc"],
                c["operator"], f"{c['rssi']} dBm"
            ])
    print("\n[Tablo 1: Aktif Hücre Envanteri]")
    if r_inv:
        print_table(h_inv, r_inv)
    else:
        print("*Aktif hücre detayı çözümlenemedi.*")
        
    # Table 2: 2G/3G/4G Neighbors
    h_neigh = ["Serving ARFCN", "CID", "Operatör", "2G Komşular (ARFCN)", "3G Komşular (UARFCN)", "4G Komşular (EARFCN)"]
    r_neigh = []
    for c in cells:
        if c["success"]:
            r_neigh.append([
                c["arfcn"], c["cell_id"], c["operator"],
                ", ".join(str(x) for x in c["neighbors_2g"]) if c["neighbors_2g"] else "Yok",
                ", ".join(str(x) for x in c["neighbors_3g_uarfcns"]) if c["neighbors_3g_uarfcns"] else "Yok",
                ", ".join(str(x) for x in c["neighbors_4g_earfcns"]) if c["neighbors_4g_earfcns"] else "Yok"
            ])
    print("\n[Tablo 2: Komşu Hücre İlişkileri (2G / 3G / 4G)]")
    if r_neigh:
        print_table(h_neigh, r_neigh)
    else:
        print("*Komşu hücre ilişkisi bulunamadı.*")
        
    # Table 3: New Discovery Sweep Recommendation
    print("\n[Tablo 3: Keşif Özet Tablosu (Yeni Tarama Önerileri)]")
    h_disc = ["Komşu Tip", "Kanal No", "Frekans", "Band", "Durum"]
    r_disc = []
    
    scanned_arfcns_set = set(target_arfcns)
    all_2g_neighbors = set()
    all_3g_neighbors = set()
    all_4g_neighbors = set()
    
    for c in cells:
        all_2g_neighbors.update(c["neighbors_2g"])
        all_3g_neighbors.update(c["neighbors_3g_uarfcns"])
        all_4g_neighbors.update(c["neighbors_4g_earfcns"])
        
    for n in sorted(list(all_2g_neighbors)):
        n_band, n_freq = get_arfcn_info(n)
        status = "Tarandı" if n in scanned_arfcns_set else "Taranmadı (2G Keşif)"
        r_disc.append(["2G GSM", n, f"{n_freq:.1f} MHz" if n_freq else "N/A", n_band, status])
        
    for u in sorted(list(all_3g_neighbors)):
        u_band, u_freq = get_uarfcn_info_umts(u)
        r_disc.append(["3G UMTS", u, f"{u_freq:.1f} MHz" if u_freq else "N/A", f"Band {u_band}" if u_band else "N/A", "Taranmadı (3G Keşif)"])
        
    for e in sorted(list(all_4g_neighbors)):
        e_band, e_freq = get_earfcn_info_lte(e)
        r_disc.append(["4G LTE", e, f"{e_freq:.1f} MHz" if e_freq else "N/A", f"Band {e_band}" if e_band else "N/A", "Taranmadı (4G Keşif)"])
        
    if r_disc:
        print_table(h_disc, r_disc)
    else:
        print("*Yeni taranmamış keşif kanalı bulunmamaktadır.*")
        
    # 4. Save to JSON output file
    output_data = {
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "sdr": {
            "type": args.sdr,
            "serial": args.serial,
            "gain": args.gain,
            "antenna": args.antenna
        },
        "scanned_arfcns": target_arfcns,
        "cells": cells
    }
    
    with open(args.output, "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2)
    print(f"\n[+] Detaylı tarama sonuçları JSON dosyasına başarıyla kaydedildi: {args.output}")

if __name__ == "__main__":
    main()
