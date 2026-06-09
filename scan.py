#!/usr/bin/env python3
import os
import sys
import subprocess
import time
import re
import json
import select
from datetime import datetime

# Helper function to get band and DL frequency for an EARFCN (3GPP TS 36.101)
def get_earfcn_info(earfcn):
    # Band 1: 0 - 599
    if 0 <= earfcn <= 599:
        return 1, 2110.0 + 0.1 * (earfcn - 0)
    # Band 3: 1200 - 1949
    elif 1200 <= earfcn <= 1949:
        return 3, 1805.0 + 0.1 * (earfcn - 1200)
    # Band 7: 2750 - 3449
    elif 2750 <= earfcn <= 3449:
        return 7, 2620.0 + 0.1 * (earfcn - 2750)
    # Band 20: 6150 - 6449
    elif 6150 <= earfcn <= 6449:
        return 20, 791.0 + 0.1 * (earfcn - 6150)
    # Band 28: 9210 - 9659
    elif 9210 <= earfcn <= 9659:
        return 28, 758.0 + 0.1 * (earfcn - 9210)
    return None, None

def get_operator_name(plmn):
    if plmn == "28601":
        return "Turkcell"
    elif plmn == "28603":
        return "Türk Telekom"
    elif plmn == "28602":
        return "Vodafone"
    return f"Bilinmeyen ({plmn})"

def strip_ansi(text):
    return re.sub(r'\033\[[0-9;]*m', '', text)

def format_table(headers, rows, color_code="36"):
    # Calculate column widths based on values
    widths = [len(h) for h in headers]
    for row in rows:
        for idx, val in enumerate(row):
            widths[idx] = max(widths[idx], len(str(val)))
            
    # Draw horizontal separator
    border = "+" + "+".join("-" * (w + 2) for w in widths) + "+"
    
    # Draw header row
    header_row = "|" + "|".join(f" \033[1;{color_code}m{h:<{widths[idx]}}\033[0m " for idx, h in enumerate(headers)) + "|"
    
    # Draw data rows
    data_rows = []
    for row in rows:
        data_row = "|" + "|".join(f" {str(val):<{widths[idx]}} " for idx, val in enumerate(row)) + "|"
        data_rows.append(data_row)
        
    res = [border, header_row, border] + data_rows + [border]
    return "\n".join(res)

def update_progress_line(idx, total, earfcn, decoded, n_neigh=0):
    mib_b = "\033[1;32m✅ MIB\033[0m" if "MIB" in decoded else "\033[1;30m⏳ MIB\033[0m"
    sib1_b = "\033[1;32m✅ SIB1\033[0m" if "SIB1" in decoded else "\033[1;30m⏳ SIB1\033[0m"
    sib5_b = f"\033[1;32m✅ SIB5 ({n_neigh} komşu bulundu)\033[0m" if "SIB5" in decoded else "\033[1;30m⏳ SIB5\033[0m"
    print(f"\r[{idx}/{total}] EARFCN {earfcn} taraniyor... {mib_b} {sib1_b} {sib5_b}", end="", flush=True)

def generate_terminal_and_file_report(cells_data, scanned_earfcns, duration):
    report_lines = []
    
    # Title Banner
    t_header = "=" * 90
    report_lines.append("\n" + t_header)
    report_lines.append("                     📊 LTE TARAMA RAPORU 📊")
    report_lines.append(t_header)
    report_lines.append(f"Tarih/Saat: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report_lines.append(f"Toplam Süre: {duration:.1f} saniye")
    report_lines.append(t_header + "\n")

    # 1. HÜCRE ENVANTERİ
    inventory_headers = ["EARFCN", "Band", "Frekans (MHz)", "PCI", "Cell ID", "PLMN", "Operatör", "TAC", "RSRP (dBm)", "BW"]
    inventory_rows = []
    found_count = 0
    for c in sorted(cells_data.values(), key=lambda x: x["earfcn"]):
        if not c.get("success"):
            continue
        found_count += 1
        op_name = get_operator_name(c["plmn"])
        inventory_rows.append([
            c["earfcn"], c["band"], f"{c['freq_mhz']:.1f}", c["pci"], c["cell_id"], c["plmn"], op_name, c["tac"], c["rsrp"], c["bw"]
        ])
        
    report_lines.append("\033[1;32mTablo 1 — HÜCRE ENVANTERİ\033[0m")
    if inventory_rows:
        report_lines.append(format_table(inventory_headers, inventory_rows, "32")) # Green
    else:
        report_lines.append("*Hücre tespit edilemedi.*")
    report_lines.append("\n")

    # 2. KOMŞU LİSTESİ
    sib5_headers = ["Serving EARFCN", "Serving PCI", "Komşu EARFCN", "Komşu Band", "Komşu Frekans", "Öncelik", "threshX-High", "threshX-Low", "BW", "Komşu Tipi"]
    sib5_rows = []
    total_neighbors = 0
    discovered_neighbors = set()
    
    for c in sorted(cells_data.values(), key=lambda x: x["earfcn"]):
        if not c.get("success"):
            continue
            
        # Parse SIB4 (Intra-frequency neighbors)
        if c.get("sib4") and "intraFreqNeighCellList" in c["sib4"]:
            for neigh in c["sib4"]["intraFreqNeighCellList"]:
                n_earfcn = c["earfcn"]
                n_pci = neigh.get("physCellId", "N/A")
                n_band = c["band"]
                n_freq = c["freq_mhz"]
                sib5_rows.append([
                    c["earfcn"], c["pci"], f"{n_earfcn} (PCI {n_pci})", n_band, f"{n_freq:.1f} MHz", "N/A", "N/A", "N/A", c["bw"], "intra"
                ])
                total_neighbors += 1
                
        # Parse SIB5 (Inter-frequency neighbors)
        if c.get("sib5") and "interFreqCarrierFreqList" in c["sib5"]:
            for neigh in c["sib5"]["interFreqCarrierFreqList"]:
                n_earfcn = int(neigh.get("dl-CarrierFreq", 0))
                n_priority = neigh.get("cellReselectionPriority", "N/A")
                n_bw = neigh.get("allowedMeasBandwidth", "mbw100")
                t_high = neigh.get("threshX-High", "N/A")
                t_low = neigh.get("threshX-Low", "N/A")
                
                n_band, n_freq = get_earfcn_info(n_earfcn)
                sib5_rows.append([
                    c["earfcn"], c["pci"], n_earfcn, n_band or "N/A", f"{n_freq:.1f} MHz" if n_freq else "N/A",
                    n_priority, t_high, t_low, n_bw, "inter"
                ])
                total_neighbors += 1
                discovered_neighbors.add(n_earfcn)
                
    report_lines.append("\033[1;35mTablo 2 — KOMŞU LİSTESİ\033[0m")
    if sib5_rows:
        report_lines.append(format_table(sib5_headers, sib5_rows, "35")) # Magenta
    else:
        report_lines.append("*Komşu hücre listesi çözümlenemedi veya komşu bulunamadı.*")
    report_lines.append("\n")

    # 3. KEŞİF ÖZETİ
    discovery_headers = ["EARFCN", "Band", "Frekans (MHz)", "Anten Portu (LNAH/LNAW)", "Durum (Taranabilir / Donanım limiti dışı)"]
    discovery_rows = []
    
    unscanned_discovered = discovered_neighbors - scanned_earfcns
    for u in sorted(list(unscanned_discovered)):
        u_band, u_freq = get_earfcn_info(u)
        if u_freq:
            port = "LNAH" if u_freq >= 1500.0 else "LNAW"
            hw_ok = "Taranabilir" if (10.0 <= u_freq <= 3500.0) else "Donanım limiti dışı"
        else:
            port = "N/A"
            hw_ok = "Belirsiz"
        discovery_rows.append([u, u_band or "N/A", f"{u_freq:.1f} MHz" if u_freq else "N/A", port, hw_ok])
        
    report_lines.append("\033[1;31mTablo 3 — KEŞİF ÖZETİ\033[0m")
    if discovery_rows:
        report_lines.append(format_table(discovery_headers, discovery_rows, "31")) # Red
    else:
        report_lines.append("*Taranmamış yeni komşu hücre keşfedilmedi.*")
    report_lines.append("\n")

    # Single line summary
    summary_line = f"\033[1;36mTarama tamamlandı. {found_count} hücre bulundu, {total_neighbors} komşu tespit edildi, {len(unscanned_discovered)} yeni keşif.\033[0m"
    report_lines.append(summary_line)
    
    # Generate Output Reports
    ansi_report = "\n".join(report_lines)
    clean_report = strip_ansi(ansi_report)
    
    # Print to stdout
    print(ansi_report)
    
    # Save to file
    filename = f"scan_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
    filepath = os.path.join("/home/mobsec/Desktop/netmon", filename)
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(clean_report)
    print(f"\n📂 Rapor dosyası başarıyla kaydedildi: {filepath}")

def run_scan_with_progress(cmd, cells_data, scanned_earfcns, total_earfcns, cwd=None):
    process = subprocess.Popen(
        cmd,
        shell=True,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

    current_earfcn = None
    decoded_sibs = set()
    n_neighbors = 0
    scanned_idx = len(scanned_earfcns)

    while True:
        retcode = process.poll()
        r, _, _ = select.select([process.stdout], [], [], 0.5)

        if process.stdout in r:
            line = process.stdout.readline()
            if not line:
                if retcode is not None:
                    break
                continue

            line_strip = line.strip()
            if not line_strip:
                continue

            # Switch EARFCN
            m_earfcn = re.search(r"earfcn \(for srsue task\):\s*(\d+)", line_strip)
            if m_earfcn:
                val = int(m_earfcn.group(1))
                if val != current_earfcn:
                    if current_earfcn is not None:
                        print() # Newline for the completed one
                    current_earfcn = val
                    scanned_earfcns.add(current_earfcn)
                    scanned_idx = len(scanned_earfcns)
                    decoded_sibs.clear()
                    n_neighbors = 0
                    
                    band, freq = get_earfcn_info(current_earfcn)
                    cells_data[current_earfcn] = {
                        "earfcn": current_earfcn,
                        "success": False,
                        "rsrp": "N/A",
                        "mib": None,
                        "sib1": None,
                        "sib3": None,
                        "sib4": None,
                        "sib5": None,
                        "cell_id": "N/A",
                        "tac": "N/A",
                        "plmn": "N/A",
                        "pci": "N/A",
                        "bw": "20MHz",
                        "band": band or "N/A",
                        "freq_mhz": freq or 0.0
                    }
                    print(f"[{scanned_idx}/{total_earfcns}] EARFCN {current_earfcn} taraniyor... ⏳ Sinyal bekleniyor...", end="", flush=True)

            # JSON Parsing
            if line_strip.startswith("{") and line_strip.endswith("}"):
                try:
                    data = json.loads(line_strip)
                    if "rsrp" in data:
                        cells_data[current_earfcn]["rsrp"] = data["rsrp"]
                    elif "type" in data:
                        sib_type = data["type"].lower()
                        decoded_sibs.add(sib_type.upper())
                        cells_data[current_earfcn][sib_type] = data["info"]
                        cells_data[current_earfcn]["success"] = True
                        
                        if sib_type == "sib1":
                            info = data["info"]
                            cari = info.get("cellAccessRelatedInfo", {})
                            if "cellIdentity" in cari:
                                cell_id = int(cari["cellIdentity"], 2)
                                cells_data[current_earfcn]["cell_id"] = cell_id
                                cells_data[current_earfcn]["pci"] = cell_id % 504
                            if "trackingAreaCode" in cari:
                                cells_data[current_earfcn]["tac"] = int(cari["trackingAreaCode"], 2)
                            plmn = "28601"
                            if "plmn-IdentityList" in cari and len(cari["plmn-IdentityList"]) > 0:
                                plmn_id = cari["plmn-IdentityList"][0].get("plmn-Identity", {})
                                if "mcc" in plmn_id and "mnc" in plmn_id:
                                    mcc = "".join(str(x) for x in plmn_id["mcc"])
                                    mnc = "".join(str(x) for x in plmn_id["mnc"])
                                    plmn = f"{mcc}{mnc}"
                            cells_data[current_earfcn]["plmn"] = plmn
                        
                        elif sib_type == "sib5":
                            n_neighbors = len(data["info"].get("interFreqCarrierFreqList", []))
                            
                        update_progress_line(scanned_idx, total_earfcns, current_earfcn, decoded_sibs, n_neighbors)
                except Exception:
                    pass

            if "was not scanned" in line_strip:
                print(f"\r[{scanned_idx}/{total_earfcns}] EARFCN {current_earfcn} taraniyor... \033[1;31m❌ Timeout, hücre bulunamadı\033[0m", flush=True)
                current_earfcn = None

        else:
            if retcode is not None:
                break

    if current_earfcn is not None:
        print() # Final newline for the last scanned EARFCN
    process.stdout.close()
    process.wait()
    return process.returncode == 0

def main():
    import argparse
    parser = argparse.ArgumentParser(description="LTE Automatic Scan and Reporting Tool")
    parser.add_argument("inputs", nargs="*", help="Space/comma-separated EARFCN list")
    parser.add_argument("-g", "--gain", type=int, default=None, help="SDR RX gain in dB (default: 40 for LimeSDR, 70 for USRP)")
    parser.add_argument("--sdr", type=str, choices=["limesdr", "usrp", "auto"], default="auto", help="SDR hardware type (default: auto-detect)")
    parser.add_argument("--antenna", type=str, default=None, help="Force antenna port name (e.g. TX/RX)")
    
    args = parser.parse_args()

    # Pre-parse inputs list to handle potential spaces in options like "-- gain 40"
    inputs = list(args.inputs)
    rx_gain = args.gain
    sdr_type = args.sdr.lower() if args.sdr else "auto"
    antenna_forced = args.antenna

    # A helper to extract values from inputs list if passed as positional arguments
    def extract_val(keys):
        nonlocal inputs
        for i, val in enumerate(inputs):
            if val.lower() in keys:
                if i + 1 < len(inputs):
                    value = inputs[i + 1]
                    # remove from inputs
                    inputs.pop(i + 1)
                    inputs.pop(i)
                    return value
                else:
                    inputs.pop(i)
        return None

    # Try extracting options from positional inputs
    extracted_gain = extract_val(["gain", "--gain", "-g"])
    if extracted_gain is not None:
        try:
            rx_gain = int(extracted_gain)
        except ValueError:
            pass

    extracted_sdr = extract_val(["sdr", "--sdr"])
    if extracted_sdr is not None:
        sdr_type = extracted_sdr.lower()

    extracted_ant = extract_val(["antenna", "--antenna"])
    if extracted_ant is not None:
        antenna_forced = extracted_ant

    # Now parse remaining inputs for EARFCNs
    raw_args = " ".join(inputs)
    raw_args = raw_args.replace(",", " ").replace(";", " ")
    earfcns = []
    for x in raw_args.split():
        try:
            earfcns.append(int(x))
        except ValueError:
            pass

    if not earfcns:
        print("Kullanım: python3 scan.py <EARFCN listesi veya tek tek EARFCN'ler> [-g GAIN] [--sdr SDR_TYPE] [--antenna ANTENNA]")
        print("Örnek:   python3 scan.py 100")
        print("Örnek:   python3 scan.py \"100 6400 2850\" -g 42 --sdr usrp")
        sys.exit(1)

    print("=" * 70)
    print("        📡 LTE OTOMATİK TARAMA & RAPORLAMA SİSTEMİ 📡")
    print("=" * 70)
    print(f"Girdi EARFCN Listesi: {earfcns}")
    
    # Auto-detection or force setting SDR type
    if sdr_type == "auto":
        usrp_found = False
        limesdr_found = False
        try:
            lsusb_check = subprocess.run("lsusb", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            # Check USRP
            if "2500:" in lsusb_check.stdout or "Ettus" in lsusb_check.stdout:
                usrp_found = True
            else:
                usrp_check = subprocess.run("uhd_find_devices", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if "product:" in usrp_check.stdout or "type: b2" in usrp_check.stdout:
                    usrp_found = True
            
            # Check LimeSDR
            if "0403:601f" in lsusb_check.stdout or "FT601" in lsusb_check.stdout or "LimeSDR" in lsusb_check.stdout:
                limesdr_found = True
            else:
                lime_check = subprocess.run("LimeUtil --find", shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
                if "LimeSDR" in lime_check.stdout:
                    limesdr_found = True
                else:
                    # Also check if uhd_find_devices detected it via soapy driver
                    if "driver: lime" in usrp_check.stdout:
                        limesdr_found = True
        except Exception:
            pass

        if usrp_found and limesdr_found:
            print("📢 Bilgi: Hem USRP hem de LimeSDR cihazı tespit edildi. Öncelikli olarak USRP seçiliyor.")
            sdr_type = "usrp"
        elif usrp_found:
            sdr_type = "usrp"
        elif limesdr_found:
            sdr_type = "limesdr"
        else:
            print("[HATA] Herhangi bir SDR cihazı (USRP veya LimeSDR) bağlı bulunamadı! Lütfen cihaz bağlantısını kontrol edin.")
            sys.exit(1)
            
    # Set default gain depending on SDR type if user didn't specify one
    if rx_gain is None:
        if sdr_type == "usrp":
            rx_gain = 70
            print("📢 Bilgi: USRP için varsayılan RX Gain değeri otomatik olarak 70 dB olarak ayarlandı.")
        else:
            rx_gain = 40
            print("📢 Bilgi: LimeSDR için varsayılan RX Gain değeri otomatik olarak 40 dB olarak ayarlandı.")

    print(f"Tespit Edilen SDR   : {sdr_type.upper()}")
    print(f"Kullanılan RX Gain  : {rx_gain} dB")
    print("=" * 70)

    # 2. Group EARFCNs by antenna port (LNAH >= 1.5 GHz, LNAW < 1.5 GHz)
    lnah_list = []
    lnaw_list = []
    
    for e in earfcns:
        band, freq = get_earfcn_info(e)
        if band is None:
            print(f"[UYARI] Tanımsız EARFCN es geçildi: {e}")
            continue
        
        # Check SDR frequency limits
        min_freq, max_freq = (70.0, 6000.0) if sdr_type == "usrp" else (10.0, 3500.0)
        if not (min_freq <= freq <= max_freq):
            print(f"[HATA] {sdr_type.upper()} donanım limitleri dışında frekans ({freq} MHz): {e}")
            continue
            
        if freq >= 1500.0:
            lnah_list.append(e)
        else:
            lnaw_list.append(e)

    if sdr_type == "usrp":
        antenna_name = antenna_forced or "TX/RX"
        print(f"-> USRP Yüksek Band Kanalları: {lnah_list} ({antenna_name})")
        print(f"-> USRP Düşük Band Kanalları: {lnaw_list} ({antenna_name})")
    else:
        high_ant = antenna_forced or "LNAH"
        low_ant = antenna_forced or "LNAW"
        print(f"-> LNAH (Yüksek Band - {high_ant}) Kanalları: {lnah_list}")
        print(f"-> LNAW (Düşük Band - {low_ant}) Kanalları: {lnaw_list}")
    print("=" * 70)

    # Output databases
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    high_db = f"/vol/output/scan_{timestamp}_high.sqlite"
    low_db = f"/vol/output/scan_{timestamp}_low.sqlite"
    
    high_db_real = f"/home/mobsec/Desktop/netmon/lte-sib-parser/vol/output/scan_{timestamp}_high.sqlite"
    low_db_real = f"/home/mobsec/Desktop/netmon/lte-sib-parser/vol/output/scan_{timestamp}_low.sqlite"
    
    scanned_dbs = []
    cells_data = {}
    scanned_earfcns = set()
    total_earfcns = len(lnah_list) + len(lnaw_list)
    
    start_total_time = time.time()

    # If USRP, prompt only once at the beginning
    if sdr_type == "usrp" and total_earfcns > 0:
        antenna = antenna_forced or "TX/RX"
        print(f"\n📢 USRP B210 BAĞLANTI UYARISI")
        print(f"👉 Anten kablonuzun USRP üzerindeki '{antenna}' portuna bağlı olduğundan emin olun.")
        input("👉 Hazır olduğunuzda devam etmek için ENTER tuşuna basın...")

    # 3. Execution - LNAH / High band scan
    if lnah_list:
        if sdr_type == "usrp":
            antenna = antenna_forced or "TX/RX"
            print(f"\n📢 [1/2] YÜKSEK BAND TARAMASI (USRP: {antenna})")
        else:
            antenna = antenna_forced or "LNAH"
            print("\n📢 [1/2] LNAH (YÜKSEK BAND) TARAMASI HAZIRLIĞI")
            print(f"👉 Anten kablosunun LimeSDR üzerindeki {antenna} portuna takılı olduğundan emin olun.")
            input("👉 Hazır olduğunuzda devam etmek için ENTER tuşuna basın...")
        
        driver = "uhd" if sdr_type == "usrp" else "soapy"
        timeout_val = 45 if sdr_type == "usrp" else 20
        extra_timeout_val = 15 if sdr_type == "usrp" else 10
        earfcns_str = " ".join(str(x) for x in lnah_list)
        cmd = f"sg docker -c \"docker-compose run --rm --entrypoint bash worker -c 'cp /vol/helpers/uhd_images/*.bin /usr/share/uhd/images/ 2>/dev/null || true; ./sib-scan.sh -d {driver} -a \\\"rxant={antenna}\\\" -g {rx_gain} -q \\\"{earfcns_str}\\\" -n -t {timeout_val} -T {extra_timeout_val} -D {high_db}'\""
        if run_scan_with_progress(cmd, cells_data, scanned_earfcns, total_earfcns, cwd="/home/mobsec/Desktop/netmon/lte-sib-parser"):
            scanned_dbs.append(high_db_real)

    # 4. Execution - LNAW / Low band scan
    if lnaw_list:
        if sdr_type == "usrp":
            antenna = antenna_forced or "TX/RX"
            print(f"\n📢 [2/2] DÜŞÜK BAND TARAMASI (USRP: {antenna})")
        else:
            antenna = antenna_forced or "LNAW"
            print("\n📢 [2/2] LNAW (DÜŞÜK BAND) TARAMASI HAZIRLIĞI")
            print(f"👉 Anten kablosunun LimeSDR üzerindeki {antenna} portuna bağlı olduğundan emin olun.")
            input("👉 Hazır olduğunuzda devam etmek için ENTER tuşuna basın...")
            
        driver = "uhd" if sdr_type == "usrp" else "soapy"
        timeout_val = 45 if sdr_type == "usrp" else 20
        extra_timeout_val = 15 if sdr_type == "usrp" else 10
        earfcns_str = " ".join(str(x) for x in lnaw_list)
        cmd = f"sg docker -c \"docker-compose run --rm --entrypoint bash worker -c 'cp /vol/helpers/uhd_images/*.bin /usr/share/uhd/images/ 2>/dev/null || true; ./sib-scan.sh -d {driver} -a \\\"rxant={antenna}\\\" -g {rx_gain} -q \\\"{earfcns_str}\\\" -n -t {timeout_val} -T {extra_timeout_val} -D {low_db}'\""
        if run_scan_with_progress(cmd, cells_data, scanned_earfcns, total_earfcns, cwd="/home/mobsec/Desktop/netmon/lte-sib-parser"):
            scanned_dbs.append(low_db_real)

    total_duration = time.time() - start_total_time

    # Generate terminal report and file report
    generate_terminal_and_file_report(cells_data, scanned_earfcns, total_duration)

if __name__ == "__main__":
    main()
