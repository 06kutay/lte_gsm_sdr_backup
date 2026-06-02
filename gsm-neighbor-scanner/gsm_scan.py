#!/usr/bin/env python3
"""
GSM Automatic Scan and Reporting Tool (gsm_scan.py)
GSM counterpart to LTE's scan.py.
Refactored to call the hw-worker-sdr gRPC microservice.
"""
import os
import sys
import time
import re
import json
import argparse
import grpc
from datetime import datetime

# Dynamically import Protobuf definitions from hw-worker-sdr
sys.path.append("/home/mobsec/Desktop/netmon/hw-worker-sdr")
try:
    import proto.sdr_worker_pb2 as pb2
    import proto.sdr_worker_pb2_grpc as pb2_grpc
except ImportError:
    print("[-] Protobuf modulleri yuklenemedi. Lutfen hw-worker-sdr altinda derlendiklerinden emin olun.")
    sys.exit(1)

# Helper function to get DL frequency for an ARFCN in GSM900 and DCS1800
def calculate_freq(arfcn, band="GSM900"):
    if band == "GSM900":
        if 1 <= arfcn <= 124:
            return 935.0 + 0.2 * arfcn
        elif 975 <= arfcn <= 1023:
            return 935.0 + 0.2 * (arfcn - 1024)
        elif arfcn == 0:
            return 935.0
    elif band == "DCS1800":
        if 512 <= arfcn <= 885:
            return 1805.2 + 0.2 * (arfcn - 512)
    return 0.0

def get_arfcn_info(arfcn):
    if 0 <= arfcn <= 124 or 975 <= arfcn <= 1023:
        freq = calculate_freq(arfcn, "GSM900")
        return "GSM900", freq
    elif 512 <= arfcn <= 885:
        freq = calculate_freq(arfcn, "DCS1800")
        return "DCS1800", freq
    return "Bilinmeyen", 0.0

def get_earfcn_info_lte(earfcn):
    if 0 <= earfcn <= 599:
        return 1, 2110.0 + 0.1 * (earfcn - 0)
    elif 1200 <= earfcn <= 1949:
        return 3, 1805.0 + 0.1 * (earfcn - 1200)
    elif 2750 <= earfcn <= 3449:
        return 7, 2620.0 + 0.1 * (earfcn - 2750)
    elif 6150 <= earfcn <= 6449:
        return 20, 791.0 + 0.1 * (earfcn - 6150)
    elif 9210 <= earfcn <= 9659:
        return 28, 758.0 + 0.1 * (earfcn - 9210)
    return None, None

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

def estimate_operator(arfcn, band):
    if band == "GSM900":
        if 1 <= arfcn <= 35:
            return "Turkcell"
        elif 36 <= arfcn <= 70:
            return "Vodafone"
        elif 71 <= arfcn <= 105:
            return "Türk Telekom"
    elif band == "DCS1800":
        if 512 <= arfcn <= 586:
            return "Vodafone"
        elif 587 <= arfcn <= 661:
            return "Türk Telekom"
        elif 662 <= arfcn <= 736:
            return "Turkcell"
    return "Bilinmeyen"

def strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', text)

def format_table(headers, rows, color_code="36"):
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    header_row = "|" + "|".join(f" \033[1;{color_code}m{h:<{widths[idx]}}\033[0m " for idx, h in enumerate(headers)) + "|"
    
    data_rows = []
    for row in rows:
        data_row = "|" + "|".join(f" {str(val):<{widths[idx]}} " for idx, val in enumerate(row)) + "|"
        data_rows.append(data_row)
        
    res = [border, header_row, border] + data_rows + [border]
    return "\n".join(res)

def validate_arfcn(arfcn):
    try:
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.SDRWorkerServiceStub(channel)
            resp = stub.ValidateArfcns(pb2.ArfcnList(arfcns=[arfcn]))
            if resp.validations:
                v = resp.validations[0]
                return {
                    "valid": v.is_valid,
                    "msg": v.error_message if not v.is_valid else f"ARFCN {arfcn} ({v.band} - {v.freq_mhz:.1f} MHz) geçerli."
                }
    except Exception:
        pass
        
    # Local fallback
    band, freq = get_arfcn_info(arfcn)
    if band == "Bilinmeyen":
        return {"valid": False, "msg": f"ARFCN {arfcn} bilinmeyen bir frekans aralığında."}
    if arfcn == 0:
        return {"valid": True, "msg": f"⚠️ ARFCN 0 (E-GSM 935.0 MHz) geçerlidir ancak bazı sistemlerde özel anlam taşır."}
    return {"valid": True, "msg": f"ARFCN {arfcn} ({band} - {freq:.1f} MHz) geçerli."}

def check_lte_scanned(earfcn, wiki_dir):
    cells_dir = os.path.join(wiki_dir, "cells")
    if os.path.exists(cells_dir):
        for fn in os.listdir(cells_dir):
            if fn.startswith(f"Cell_EARFCN{earfcn}_") and fn.endswith(".md"):
                return f"Evet → [[{fn[:-3]}]]"
    return "Hayır (yeni keşif)"

def check_gsm_scanned(arfcn, wiki_dir):
    cells_dir = os.path.join(wiki_dir, "cells")
    cell_path = os.path.join(cells_dir, f"Cell_GSM_ARFCN{arfcn}.md")
    if os.path.exists(cell_path):
        return "Taranmış"
    return "Taranmamış"

def check_sdr_connection():
    try:
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.SDRWorkerServiceStub(channel)
            resp = stub.GetHealth(pb2.Empty())
            return resp.status == "SERVING"
    except Exception:
        return False

def generate_report(cells, scanned_channels, duration, wiki_dir):
    report_lines = []
    t_header = "=" * 90
    report_lines.append("\n" + t_header)
    report_lines.append("                     📊 GSM TARAMA VE ANALİZ RAPORU (gRPC) 📊")
    report_lines.append(t_header)
    report_lines.append(f"Tarih/Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Toplam Süre: {duration:.1f} saniye")
    report_lines.append(t_header + "\n")
    
    # Tablo 1 — HÜCRE ENVANTERİ
    h_headers = ["ARFCN", "Band", "Frekans", "CID", "LAC", "MCC", "MNC", "Operatör", "RSSI (dBm)", "Config", "A5"]
    h_rows = []
    for c in cells:
        if not c.get("success"):
            continue
        op = estimate_operator(c["arfcn"], c["band"])
        h_rows.append([
            c["arfcn"], c["band"], f"{c['freq_mhz']:.1f} MHz", c["cell_id"], c["lac"], c["mcc"], c["mnc"],
            op, c["rssi_dbm"], c["config"], f"A5/{c['a5_version']}"
        ])
        
    report_lines.append("\033[1;32mTablo 1 — HÜCRE ENVANTERİ\033[0m")
    if h_rows:
        report_lines.append(format_table(h_headers, h_rows, "32"))
    else:
        report_lines.append("*Aktif GSM hücresi bulunamadı.*")
    report_lines.append("\n")
    
    # Tablo 2 — GSM KOMŞU LİSTESİ
    n_headers = ["Serving ARFCN", "Serving CID", "Komşu ARFCN", "Komşu Band", "Komşu Frekans", "Komşu Operatör Tahmini"]
    n_rows = []
    total_neigh = 0
    gsm_discovered = set()
    for c in cells:
        if not c.get("success"):
            continue
        for n in c["neighbors_si2"]:
            n_band, n_freq = get_arfcn_info(n)
            n_op = estimate_operator(n, n_band)
            n_rows.append([
                c["arfcn"], c["cell_id"], n, n_band, f"{n_freq:.1f} MHz" if n_freq else "N/A", n_op
            ])
            total_neigh += 1
            gsm_discovered.add(n)
            
    report_lines.append("\033[1;35mTablo 2 — GSM KOMŞU LİSTESİ (SI2 BA List)\033[0m")
    if n_rows:
        report_lines.append(format_table(n_headers, n_rows, "35"))
    else:
        report_lines.append("*GSM komşu hücre listesi çözümlenemedi veya komşu bulunamadı.*")
    report_lines.append("\n")
    
    # Tablo 3 — INTER-RAT KOMŞULAR
    ir_headers = ["Serving ARFCN", "Serving CID", "Tip", "Komşu Kanal", "Band", "Frekans", "Tarandı mı"]
    ir_rows = []
    total_ir = 0
    earfcns_found = set()
    uarfcns_found = set()
    
    for c in cells:
        if not c.get("success"):
            continue
        si2q = c.get("neighbors_si2quater", {"earfcns": [], "uarfcns": []})
        for earfcn in si2q.get("earfcns", []):
            l_band, l_freq = get_earfcn_info_lte(earfcn)
            scanned = check_lte_scanned(earfcn, wiki_dir)
            ir_rows.append([
                c["arfcn"], c["cell_id"], "4G LTE", earfcn, f"Band {l_band}" if l_band else "N/A",
                f"{l_freq:.1f} MHz" if l_freq else "N/A", scanned
            ])
            total_ir += 1
            earfcns_found.add(earfcn)
            
        for uarfcn in si2q.get("uarfcns", []):
            u_band, u_freq = get_uarfcn_info_umts(uarfcn)
            ir_rows.append([
                c["arfcn"], c["cell_id"], "3G UMTS", uarfcn, f"Band {u_band}" if u_band else "N/A",
                f"{u_freq:.1f} MHz" if u_freq else "N/A", "UMTS komşu (taranmadı)"
            ])
            total_ir += 1
            uarfcns_found.add(uarfcn)
            
    report_lines.append("\033[1;36mTablo 3 — INTER-RAT KOMŞULAR (SI2quater)\033[0m")
    if ir_rows:
        report_lines.append(format_table(ir_headers, ir_rows, "36"))
    else:
        report_lines.append("*Inter-RAT komşu hücresi bulunamadı.*")
    report_lines.append("\n")
    
    # Tablo 4 — KEŞİF ÖZETİ
    d_headers = ["Kaynak", "Tip", "Kanal", "Band", "Frekans", "Durum"]
    d_rows = []
    
    for n in sorted(list(gsm_discovered)):
        sc_status = check_gsm_scanned(n, wiki_dir)
        n_band, n_freq = get_arfcn_info(n)
        status_str = "Taranmış" if sc_status == "Taranmış" else "Taranmamış (yeni keşif)"
        d_rows.append([f"SI2 (BA)", "2G GSM", n, n_band, f"{n_freq:.1f} MHz" if n_freq else "N/A", status_str])
        
    for earfcn in sorted(list(earfcns_found)):
        scanned = check_lte_scanned(earfcn, wiki_dir)
        l_band, l_freq = get_earfcn_info_lte(earfcn)
        status_str = "Taranmış" if "Evet" in scanned else "Taranmamış (yeni keşif)"
        d_rows.append([f"SI2quater", "4G LTE", earfcn, f"Band {l_band}" if l_band else "N/A", f"{l_freq:.1f} MHz" if l_freq else "N/A", status_str])
        
    for uarfcn in sorted(list(uarfcns_found)):
        u_band, u_freq = get_uarfcn_info_umts(uarfcn)
        d_rows.append([f"SI2quater", "3G UMTS", uarfcn, f"Band {u_band}" if u_band else "N/A", f"{u_freq:.1f} MHz" if u_freq else "N/A", "Taranmamış (yeni keşif)"])
        
    report_lines.append("\033[1;31mTablo 4 — KEŞİF ÖZETİ\033[0m")
    if d_rows:
        report_lines.append(format_table(d_headers, d_rows, "31"))
    else:
        report_lines.append("*Yeni keşfedilen taranmamış kanal bulunmamaktadır.*")
    report_lines.append("\n")
    
    # Summary
    found_cells = [x for x in cells if x.get("success")]
    summary_line = f"\033[1;36mTarama tamamlandı. {len(found_cells)} hücre, {total_neigh} GSM komşu, {total_ir} inter-RAT komşu ({len(earfcns_found)} EARFCN + {len(uarfcns_found)} UARFCN) bulundu.\033[0m"
    report_lines.append(summary_line)
    
    ansi_report = "\n".join(report_lines)
    clean_report = strip_ansi(ansi_report)
    
    print(ansi_report)
    
    # Save to report file
    filename = f"gsm_scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join("/home/mobsec/Desktop/netmon", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(clean_report)
    print(f"\n📂 Rapor dosyası başarıyla kaydedildi: {filepath}")

def save_and_ingest_to_wiki(cells, command_str, serial, antenna, wiki_dir, no_wiki=False):
    found_cells = [x for x in cells if x.get("success")]
    
    scan_results = {
        "command": command_str,
        "timestamp": datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        "sdr_serial": serial,
        "antenna": antenna,
        "cells": found_cells
    }
    
    results_path = "/home/mobsec/Desktop/netmon/gsm-neighbor-scanner/live_scan_results.json"
    with open(results_path, "w", encoding="utf-8") as f:
        json.dump(scan_results, f, indent=2)
        
    print(f"\n📂 Tarama sonuçları JSON dosyasına yazıldı: {results_path}")
    
    if no_wiki:
        print("[*] Wiki ingestion es geçildi (--no-wiki).")
        return
        
    print("[*] Wiki ingestion pipeline motoru çalıştırılıyor...")
    pipeline_script = "/home/mobsec/Desktop/netmon/gsm-neighbor-scanner/scripts/gsm_wiki_ingest_pipeline.py"
    
    if not os.path.exists(pipeline_script):
        print(f"[-] Pipeline script bulunamadı: {pipeline_script}")
        return
        
    try:
        pipeline_cmd = f"python3 {pipeline_script} {results_path} {wiki_dir}"
        output = subprocess.check_output(pipeline_cmd, shell=True, text=True, stderr=subprocess.STDOUT)
        
        n_pages = len(re.findall(r"UPDATE|CREATE", output))
        print(f"\033[1;32mWiki başarıyla güncellendi. {n_pages} sayfa oluşturuldu/güncellendi.\033[0m")
        print("Boru hattı çıktı detayları:")
        for line in output.splitlines():
            if "[INGEST]" in line:
                print(f"  {line}")
    except subprocess.CalledProcessError as e:
        print(f"\033[1;31m[-] Wiki ingestion hatası: {e.output}\033[0m")

def main():
    parser = argparse.ArgumentParser(description="GSM Automatic Scan and Reporting Tool (gRPC Client)")
    parser.add_argument("inputs", nargs="*", help="Space/comma-separated ARFCN list")
    parser.add_argument("--band", type=str, default="GSM900", choices=["GSM900", "DCS1800", "all"], help="Scan band (default: GSM900)")
    parser.add_argument("--serial", type=str, default="1DBB4CC5EE717D", help="SDR serial number")
    parser.add_argument("--gain", type=int, default=35, help="SDR RX gain (default: 35)")
    parser.add_argument("--no-wiki", action="store_true", help="Skip wiki ingestion")
    
    args = parser.parse_args()
    wiki_dir = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki"
    
    print("=" * 70)
    print("        📡 GSM Pasif Hücre Tarama & Analiz Aracı (gRPC) 📡")
    print("=" * 70)
    print(f"SDR Seri No  : {args.serial}")
    print(f"Sinyal Kazancı: {args.gain} dB")
    print(f"Hedef Wiki   : {wiki_dir}")
    print("=" * 70)
    
    # 1. Check SDR status via gRPC
    if not check_sdr_connection():
        print("\033[1;31m[-] localhost:50051 gRPC mikroservisi çalışmıyor veya SDR bağlı değil.\033[0m")
        sys.exit(1)
        
    start_time = time.time()
    
    # Extract ARFCN inputs
    arfcn_inputs = []
    if args.inputs:
        raw_inputs = " ".join(args.inputs).replace(",", " ").replace(";", " ")
        for val in raw_inputs.split():
            try:
                arfcn_inputs.append(int(val))
            except ValueError:
                pass
                
    command_str = " ".join(sys.argv)
    scan_id = ""
    
    try:
        with grpc.insecure_channel("localhost:50051") as channel:
            stub = pb2_grpc.SDRWorkerServiceStub(channel)
            
            # Mod 2: ARFCN listesi verilirse
            if arfcn_inputs:
                print(f"\n📢 [Mod 2] Özel ARFCN listesi dinleniyor: {arfcn_inputs}")
                
                # Validation check
                valid_arfcns = []
                for a in arfcn_inputs:
                    v_res = validate_arfcn(a)
                    if v_res["valid"]:
                        valid_arfcns.append(a)
                    else:
                        print(f"\033[1;31m[-] Hatalı ARFCN: {v_res['msg']}\033[0m")
                        
                if not valid_arfcns:
                    print("\033[1;31m[-] Dinlenecek geçerli hiçbir ARFCN bulunamadı.\033[0m")
                    sys.exit(1)
                    
                # Call StartGsmScan
                req = pb2.GsmScanRequest(arfcns=valid_arfcns, gain=args.gain, timeout=15)
                resp = stub.StartGsmScan(req)
                if not resp.started:
                    print(f"\033[1;31m[-] Tarama başlatılamadı: {resp.message}\033[0m")
                    sys.exit(1)
                scan_id = resp.scan_id
                
            # Mod 1: Band tarama
            else:
                print(f"\n📢 [Mod 1] Full-band tarama yürütülüyor (Band: {args.band})")
                
                if args.band == "all":
                    # For 'all' band scan, we will perform sequential band scans on the microservice.
                    # Scan GSM900 first
                    print("\n📢 [1/2] GSM900 BANDI TARAMASI BAŞLATILIYOR...")
                    req = pb2.GsmBandScanRequest(band="GSM900", gain=args.gain)
                    resp = stub.StartGsmBandScan(req)
                    if not resp.started:
                        print(f"\033[1;31m[-] GSM900 başlatılamadı: {resp.message}\033[0m")
                        sys.exit(1)
                    scan_id_gsm = resp.scan_id
                    
                    # Poll GSM900 status
                    while True:
                        st = stub.GetScanStatus(pb2.ScanId(scan_id=scan_id_gsm))
                        if st.status in ("COMPLETED", "FAILED", "STOPPED"):
                            break
                        print(f"\r[*] GSM900 Tarama durumu: {st.status} | Aşama: {st.current_step}", end="", flush=True)
                        time.sleep(2.0)
                    print("\n[+] GSM900 taraması tamamlandı.")
                    
                    # Scan DCS1800 second
                    print("\n📢 [2/2] DCS1800 BANDI TARAMASI BAŞLATILIYOR...")
                    req = pb2.GsmBandScanRequest(band="DCS1800", gain=args.gain)
                    resp = stub.StartGsmBandScan(req)
                    if not resp.started:
                        print(f"\033[1;31m[-] DCS1800 başlatılamadı: {resp.message}\033[0m")
                        sys.exit(1)
                    scan_id_dcs = resp.scan_id
                    
                    # Poll DCS1800 status
                    while True:
                        st = stub.GetScanStatus(pb2.ScanId(scan_id=scan_id_dcs))
                        if st.status in ("COMPLETED", "FAILED", "STOPPED"):
                            break
                        print(f"\r[*] DCS1800 Tarama durumu: {st.status} | Aşama: {st.current_step}", end="", flush=True)
                        time.sleep(2.0)
                    print("\n[+] DCS1800 taraması tamamlandı.")
                    
                    # Combine cells from both JSON outputs!
                    cells = []
                    for sid in [scan_id_gsm, scan_id_dcs]:
                        json_file = f"/vol/output/gsm_scan_{sid}.json"
                        if not os.path.exists(json_file):
                            json_file = f"/home/mobsec/Desktop/netmon/lte-sib-parser/vol/output/gsm_scan_{sid}.json"
                        if os.path.exists(json_file):
                            try:
                                with open(json_file, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                    cells.extend(data.get("cells", []))
                            except Exception:
                                pass
                                
                    duration = time.time() - start_time
                    generate_report(cells, [], duration, wiki_dir)
                    save_and_ingest_to_wiki(cells, command_str, args.serial, "LNAH", wiki_dir, args.no_wiki)
                    return
                    
                else: # GSM900 or DCS1800
                    req = pb2.GsmBandScanRequest(band=args.band, gain=args.gain)
                    resp = stub.StartGsmBandScan(req)
                    if not resp.started:
                        print(f"\033[1;31m[-] Tarama başlatılamadı: {resp.message}\033[0m")
                        sys.exit(1)
                    scan_id = resp.scan_id
            
            # Poll status for targeted scan or single band scan
            while True:
                status_resp = stub.GetScanStatus(pb2.ScanId(scan_id=scan_id))
                if status_resp.status in ("COMPLETED", "FAILED", "STOPPED"):
                    break
                print(f"\r[*] Tarama durumu: {status_resp.status} | Kanal: ARFCN {status_resp.current_earfcn} | Aşama: {status_resp.current_step}", end="", flush=True)
                time.sleep(2.0)
                
            print("\n[+] Mikroservis taramayı sonlandırdı.")
            
    except grpc.RpcError as e:
        print(f"\033[1;31m[-] gRPC İletişim Hatası: {e.details()}\033[0m")
        sys.exit(1)
        
    # Read the full persistent JSON output file to fetch accurate, detailed cells list
    cells = []
    json_file = f"/vol/output/gsm_scan_{scan_id}.json"
    if not os.path.exists(json_file):
        json_file = f"/home/mobsec/Desktop/netmon/lte-sib-parser/vol/output/gsm_scan_{scan_id}.json"
        
    if os.path.exists(json_file):
        try:
            with open(json_file, "r", encoding="utf-8") as f:
                camp_data = json.load(f)
                cells = camp_data.get("cells", [])
        except Exception as e:
            print(f"[-] JSON yedek okuma hatası: {e}")
            
    duration = time.time() - start_time
    
    # 3. Report generation
    generate_report(cells, arfcn_inputs, duration, wiki_dir)
    
    # 4. Wiki ingestion
    antenna = "LNAH" if args.band == "DCS1800" else "LNAW"
    save_and_ingest_to_wiki(cells, command_str, args.serial, antenna, wiki_dir, args.no_wiki)

if __name__ == "__main__":
    main()
