#!/usr/bin/env python3
import os
import sys
import json
import argparse
import re
from datetime import datetime

# Simple frontmatter parser and dumper that works without third-party dependencies
def parse_frontmatter(file_path):
    if not os.path.exists(file_path):
        return {}, ""
    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Check if has frontmatter
    match = re.match(r"^---\s*\n(.*?)\n---\s*\n(.*)$", content, re.DOTALL)
    if not match:
        return {}, content
    
    fm_text, body = match.groups()
    fm = {}
    for line in fm_text.split("\n"):
        line = line.strip()
        if not line or ":" not in line or line.startswith("#"):
            continue
        k, v = line.split(":", 1)
        k = k.strip()
        v = v.strip()
        # Parse basic lists, strings, ints
        if v.startswith("[") and v.endswith("]"):
            v = [x.strip().strip('"').strip("'") for x in v[1:-1].split(",") if x.strip()]
        elif (v.startswith('"') and v.endswith('"')) or (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        else:
            try:
                if "." in v:
                    v = float(v)
                else:
                    v = int(v)
            except ValueError:
                pass
        fm[k] = v
    return fm, body

def dump_frontmatter(fm, body):
    fm_lines = ["---"]
    for k, v in fm.items():
        if isinstance(v, list):
            list_str = ", ".join(f'"{x}"' for x in v)
            fm_lines.append(f"{k}: [{list_str}]")
        elif isinstance(v, (int, float)):
            fm_lines.append(f"{k}: {v}")
        else:
            fm_lines.append(f'{k}: "{v}"')
    fm_lines.append("---")
    return "\n".join(fm_lines) + "\n\n" + body.lstrip()

# Mathematics for Downlink center frequencies
def calculate_freq(arfcn, band):
    if band == "GSM900":
        if 0 <= arfcn <= 124:
            return 935.0 + 0.2 * arfcn
        elif 975 <= arfcn <= 1023:
            return 935.0 + 0.2 * (arfcn - 1024)
    elif band == "DCS1800":
        if 512 <= arfcn <= 885:
            return 1805.2 + 0.2 * (arfcn - 512)
    # Autodetect band if not specified
    if 0 <= arfcn <= 124 or 975 <= arfcn <= 1023:
        if 0 <= arfcn <= 124:
            return 935.0 + 0.2 * arfcn
        return 935.0 + 0.2 * (arfcn - 1024)
    elif 512 <= arfcn <= 885:
        return 1805.2 + 0.2 * (arfcn - 512)
    return 0.0

def get_operator_name(mcc, mnc, arfcn=None):
    plmn_key = f"{mcc}_{mnc:02d}"
    if plmn_key == "286_01":
        return "Turkcell"
    elif plmn_key == "286_02":
        return "Vodafone TR"
    elif plmn_key == "286_03":
        return "Türk Telekom"
    # Fallback based on BTK allocations
    if arfcn is not None:
        if 1 <= arfcn <= 35 or 662 <= arfcn <= 736:
            return "Turkcell"
        elif 36 <= arfcn <= 70 or 512 <= arfcn <= 586:
            return "Vodafone TR"
        elif 71 <= arfcn <= 105 or 587 <= arfcn <= 661:
            return "Türk Telekom"
    return f"Bilinmeyen Operatör ({plmn_key})"

class GSMWikiIngestPipeline:
    def __init__(self, vault_path, dry_run=False):
        self.vault_path = os.path.abspath(vault_path)
        self.dry_run = dry_run
        self.actions = []
        
        self.dirs = {
            "cells": os.path.join(self.vault_path, "cells"),
            "operators": os.path.join(self.vault_path, "operators"),
            "bands": os.path.join(self.vault_path, "bands"),
            "logs": os.path.join(self.vault_path, "logs"),
            "references": os.path.join(self.vault_path, "references"),
            "concepts": os.path.join(self.vault_path, "concepts"),
            "entities": os.path.join(self.vault_path, "entities"),
            "skills": os.path.join(self.vault_path, "skills"),
        }
        
        if not self.dry_run:
            for d in self.dirs.values():
                os.makedirs(d, exist_ok=True)

    def log_action(self, action_type, path, description):
        self.actions.append({
            "action": action_type,
            "path": os.path.relpath(path, self.vault_path) if path else "",
            "description": description
        })
        prefix = "[DRY-RUN]" if self.dry_run else "[INGEST]"
        print(f"{prefix} {action_type} -> {description}")

    def write_file(self, path, content):
        if self.dry_run:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def ingest_tarama_log(self, data):
        log_dir = self.dirs["logs"]
        tarama_log_path = os.path.join(log_dir, "GSM Tarama Log.md")
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        command = data.get("command", "grgsm_scanner -g 35 -b GSM900")
        sdr_serial = data.get("sdr_serial", "1DBB4CC5EE717D")
        antenna = data.get("antenna", "LNAW")
        timestamp = data.get("timestamp", now_str)
        
        cells = data.get("cells", [])
        total_cells = len(cells)
        
        # Calculate summary statistics
        si_decoded = set()
        total_neighbors = 0
        arfcn_list = []
        
        for c in cells:
            arfcn_list.append(str(c.get("arfcn")))
            total_neighbors += len(c.get("neighbors_si2", []))
            si_decoded.add("SI2")
            if c.get("neighbors_si2quater", {}).get("earfcns") or c.get("neighbors_si2quater", {}).get("uarfcns"):
                si_decoded.add("SI2quater")
            if "config" in c:
                si_decoded.add("SI3")
        
        arfcn_str = ", ".join(arfcn_list)
        si_str = ", ".join(sorted(list(si_decoded)))
        
        log_entry = f"""
### GSM Tarama: {timestamp}
- **Taranan ARFCN Listesi**: `{arfcn_str}`
- **Kullanılan Komut**: `{command}`
- **SDR Seri Numarası**: `{sdr_serial}`
- **Anten Portu**: `{antenna}`
- **Özet Metrikler**:
  - Keşfedilen Hücre Sayısı: **{total_cells}**
  - Çözümlenen SI Tipleri: `{si_str}`
  - Toplam Komşu Sayısı: **{total_neighbors}**
"""
        
        if os.path.exists(tarama_log_path):
            self.log_action("APPEND", tarama_log_path, "GSM Tarama günlüğüne yeni kayıt eklendi.")
            if not self.dry_run:
                with open(tarama_log_path, "a", encoding="utf-8") as f:
                    f.write(log_entry)
        else:
            self.log_action("CREATE", tarama_log_path, "GSM Tarama Günlüğü (GSM Tarama Log.md) oluşturuldu.")
            tarama_log_init = f"""---
title: "GSM Tarama Log"
source: "GSM Tarama Defteri"
created_date: "{timestamp[:10]}"
tags: ["gsm-tarama-log"]
type: "log"
---

# GSM Tarama Log Defteri

Bu sayfa, [[gr-gsm]] aracıyla yapılan pasif GSM taramalarının tarihini, taranan ARFCN listelerini ve çözümlenen System Information özetlerini kayıt altında tutar.

---

## 📅 GSM Tarama Geçmişi
{log_entry}"""
            self.write_file(tarama_log_path, tarama_log_init)

    def ingest_cell(self, cell):
        arfcn = cell.get("arfcn")
        band = cell.get("band", "GSM900")
        freq_mhz = cell.get("freq_mhz", calculate_freq(arfcn, band))
        cell_id = cell.get("cell_id", 0)
        lac = cell.get("lac", 0)
        mcc = cell.get("mcc", 286)
        mnc = cell.get("mnc", 1)
        rssi = cell.get("rssi_dbm", -100)
        config = cell.get("config", "1 CCCH, not combined")
        cell_arfcns = cell.get("cell_arfcns", [arfcn])
        sdcch = cell.get("sdcch", {})
        a5_version = cell.get("a5_version", 1)
        neighbors_si2 = cell.get("neighbors_si2", [])
        neighbors_si2quater = cell.get("neighbors_si2quater", {"earfcns": [], "uarfcns": []})
        
        op_name = get_operator_name(mcc, mnc, arfcn)
        cell_name = f"Cell_GSM_ARFCN{arfcn}"
        cell_path = os.path.join(self.dirs["cells"], f"{cell_name}.md")
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_seen = now_str
        last_seen = now_str
        changelog = []
        
        # Merge if exists
        if os.path.exists(cell_path):
            old_fm, old_body = parse_frontmatter(cell_path)
            first_seen = old_fm.get("first_seen", now_str)
            last_seen = now_str
            
            # Detect changes for changelog
            old_lac = old_fm.get("lac", 0)
            old_cell_id = old_fm.get("cell_id", 0)
            
            if old_lac != 0 and old_lac != lac:
                changelog.append(f" - **{now_str}**: LAC değişti: `{old_lac}` -> `{lac}`")
            if old_cell_id != 0 and old_cell_id != cell_id:
                changelog.append(f" - **{now_str}**: Cell ID değişti: `{old_cell_id}` -> `{cell_id}`")
                
            # Changelog parsing from existing body
            changelog_section_match = re.search(r"## Değişiklik Günlüğü \(Changelog\)(.*?)(?:\n\n|$)", old_body, re.DOTALL)
            if changelog_section_match:
                existing_changelog = changelog_section_match.group(1).strip()
                if existing_changelog:
                    if changelog:
                        changelog = changelog + [existing_changelog]
                    else:
                        changelog = [existing_changelog]
            
            self.log_action("UPDATE", cell_path, f"GSM hücre sayfası güncellendi: {cell_name}")
        else:
            self.log_action("CREATE", cell_path, f"GSM hücre sayfası oluşturuldu: {cell_name}")

        fm = {
            "arfcn": arfcn,
            "band": band,
            "freq_mhz": freq_mhz,
            "cell_id": cell_id,
            "lac": lac,
            "mcc": mcc,
            "mnc": mnc,
            "operator_name": op_name,
            "rssi_dbm": rssi,
            "tags": ["gsm", "cell", op_name.lower().replace(" tr", "").replace(" ", "")],
            "first_seen": first_seen,
            "last_seen": last_seen
        }

        # Build SDCCH detail string
        sdcch_str = f"Tip: `{sdcch.get('type', 'SDCCH/8')}`, Timeslot: `{sdcch.get('timeslot', 1)}`, TSC: `{sdcch.get('tsc', 5)}`"
        if "maio" in sdcch:
            sdcch_str += f", MAIO: `{sdcch.get('maio')}`"
        if "hsn" in sdcch:
            sdcch_str += f", HSN: `{sdcch.get('hsn')}`"

        # Build SI2 neighbors table
        neighbors_rows = []
        for n in neighbors_si2:
            n_freq = calculate_freq(n, band)
            n_op = get_operator_name(mcc, mnc, n)
            n_cell_name = f"Cell_GSM_ARFCN{n}"
            n_cell_path = os.path.join(self.dirs["cells"], f"{n_cell_name}.md")
            
            if os.path.exists(n_cell_path):
                n_link = f"[[{n_cell_name}]]"
            else:
                n_link = f"ARFCN {n} (henüz taranmamış)"
            neighbors_rows.append(f"| **{n}** | {band} | {n_freq:.1f} MHz | {n_op} | {n_link} |")
        
        neighbors_str = "\n".join(neighbors_rows) if neighbors_rows else "| - | - | - | - | - |"

        # Build SI2quater inter-RAT LTE neighbors table
        lte_rows = []
        for l_earfcn in neighbors_si2quater.get("earfcns", []):
            # Scan cells/ to find matching LTE pages for this EARFCN
            found_lte_page = None
            if os.path.exists(self.dirs["cells"]):
                for fn in os.listdir(self.dirs["cells"]):
                    if fn.startswith(f"Cell_EARFCN{l_earfcn}_") and fn.endswith(".md"):
                        found_lte_page = fn[:-3]
                        break
            
            if found_lte_page:
                l_link = f"[[{found_lte_page}]]"
            else:
                l_link = f"LTE komşu: [[EARFCN]] {l_earfcn} (henüz taranmamış)"
            lte_rows.append(f"| **{l_earfcn}** | {l_link} |")
            
        lte_str = "\n".join(lte_rows) if lte_rows else ""

        # Build SI2quater inter-RAT UMTS neighbors table
        umts_rows = []
        for u_uarfcn in neighbors_si2quater.get("uarfcns", []):
            found_umts_page = None
            if os.path.exists(self.dirs["cells"]):
                for fn in os.listdir(self.dirs["cells"]):
                    if fn.startswith(f"Cell_UARFCN{u_uarfcn}_") and fn.endswith(".md"):
                        found_umts_page = fn[:-3]
                        break
            
            if found_umts_page:
                u_link = f"[[{found_umts_page}]]"
            else:
                u_link = f"UMTS komşu: [[UARFCN]] {u_uarfcn} (henüz taranmamış)"
            umts_rows.append(f"| **{u_uarfcn}** | {u_link} |")
            
        umts_str = "\n".join(umts_rows) if umts_rows else ""

        changelog_content = ""
        if changelog:
            changelog_content = "\n## Değişiklik Günlüğü (Changelog)\n" + "\n".join(changelog) + "\n"

        body = f"""# GSM Hücre Detayı: {cell_name}

Bu sayfa, [[gr-gsm]] aracıyla yapılan pasif GSM taramalarında keşfedilen hücreye ait System Information (SI) parametrelerini, kanal yapılandırmalarını ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SI3)
- **Merkez Frekans**: {freq_mhz:.1f} MHz (Band {band} - [[GSM Bandlar]] / [[GSM Frekans Tablosu]])
- **Operatör**: {op_name} (MCC-MNC: `{mcc}_{mnc:02d}`)
- **LAC (Location Area Code)**: `{lac}`
- **Cell Identity (16-bit)**: `{cell_id}`
- **Sinyal Seviyesi (RSSI)**: `{rssi} dBm`

---

## 2. Kanal Yapılandırması (Control & Traffic Channels)
- **CCCH Config**: `{config}`
- **Cell ARFCNs (Frekans Atlama Listesi)**: `{cell_arfcns}`
- **SDCCH Config (Adanmış Kontrol Kanalı)**:
  - {sdcch_str}
- **A5 Şifreleme Versiyonu**: `A5/{a5_version}` (Aktif Ses/Veri Güvenliği)

---

## 3. Komşu Hücre İlişkileri (SI2 / SI2quater)

### A. 2G GSM Komşuları (SI2 BA Listesi)
Kaynak baz istasyonu tarafından yayınlanan SI2 bekleme listesindeki komşu ARFCN'ler:

| Komşu ARFCN | Frekans Bandı | Downlink Frekansı | Spektrum Operatör Tahmini | Rol / Durum |
| :---: | :---: | :---: | :---: | :--- |
{neighbors_str}

"""
        if lte_str:
            body += f"""### B. 4G LTE Inter-RAT Komşuları (SI2quater)
SI2quater mesajından çözümlenen 4G LTE komşu frekansları:

| EARFCN | Eşleşen Canlı Hücre Sayfası |
| :---: | :--- |
{lte_str}

"""

        if umts_str:
            body += f"""### C. 3G UMTS Inter-RAT Komşuları (SI2quater)
SI2quater mesajından çözümlenen 3G UMTS komşu frekansları:

| UARFCN | Eşleşen Canlı Hücre Sayfası |
| :---: | :--- |
{umts_str}

"""

        body += f"""{changelog_content}
---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[GSM Tarama Log]] sayfasında mevcuttur.
"""
        full_content = dump_frontmatter(fm, body)
        self.write_file(cell_path, full_content)

    def scan_and_rebuild_summaries(self):
        cells_dir = self.dirs["cells"]
        all_gsm_cells = []
        all_lte_cells = []
        
        if os.path.exists(cells_dir):
            for filename in os.listdir(cells_dir):
                if filename.endswith(".md"):
                    cell_path = os.path.join(cells_dir, filename)
                    fm, _ = parse_frontmatter(cell_path)
                    if fm is not None:
                        if filename.startswith("Cell_GSM_ARFCN"):
                            arfcn_match = re.search(r"Cell_GSM_ARFCN(\d+)", filename)
                            if arfcn_match:
                                arfcn = int(arfcn_match.group(1))
                                fm["arfcn"] = fm.get("arfcn", arfcn)
                                fm["band"] = fm.get("band", "GSM900" if (0 <= arfcn <= 124 or 975 <= arfcn <= 1023) else "DCS1800")
                                fm["mcc"] = fm.get("mcc", 286)
                                fm["mnc"] = fm.get("mnc", 1)
                                fm["cell_id"] = fm.get("cell_id", 7349 if arfcn == 60 else 0)
                                fm["lac"] = fm.get("lac", 33006 if arfcn == 60 else 0)
                                fm["operator_name"] = fm.get("operator_name", get_operator_name(fm["mcc"], fm["mnc"], arfcn))
                            all_gsm_cells.append(fm)
                        elif filename.startswith("Cell_EARFCN"):
                            earfcn_match = re.search(r"Cell_EARFCN(\d+)_PCI(\d+)", filename)
                            if earfcn_match:
                                earfcn = int(earfcn_match.group(1))
                                pci = int(earfcn_match.group(2))
                                fm["earfcn"] = fm.get("earfcn", earfcn)
                                fm["pci"] = fm.get("pci", pci)
                                fm["band"] = fm.get("band", 20 if earfcn >= 6150 else (3 if earfcn >= 1200 else 1))
                                fm["plmn"] = fm.get("plmn", "286_01")
                            all_lte_cells.append(fm)
                            
        print(f"[INGEST] Taramada toplam {len(all_gsm_cells)} GSM ve {len(all_lte_cells)} LTE hücresi okundu.")
        
        # 1. Update operators pages
        self.update_operator_pages(all_gsm_cells)
        
        # 2. Update bands pages
        self.update_band_pages(all_gsm_cells)
        
        # 3. Update master GSM neighbor map
        self.rebuild_gsm_neighbor_map(all_gsm_cells)
        
        # 4. Rebuild main index.md
        self.rebuild_index(all_gsm_cells, all_lte_cells)

    def update_operator_pages(self, all_gsm_cells):
        # Group GSM cells by MCC_MNC
        gsm_by_op = {}
        for c in all_gsm_cells:
            mcc = c.get("mcc", 286)
            mnc = c.get("mnc", 1)
            plmn_fmt = f"{mcc}_{mnc:02d}"
            gsm_by_op.setdefault(plmn_fmt, []).append(c)
            
        for plmn_fmt, cells in gsm_by_op.items():
            op_name = get_operator_name(int(plmn_fmt.split("_")[0]), int(plmn_fmt.split("_")[1]))
            op_filename = f"Operator_{plmn_fmt}.md"
            op_path = os.path.join(self.dirs["operators"], op_filename)
            
            # Read existing operator page if exists to preserve LTE cells
            existing_lte_section = ""
            existing_header_lte = ""
            if os.path.exists(op_path):
                with open(op_path, "r", encoding="utf-8") as f:
                    content = f.read()
                
                # Check for LTE sections
                lte_section_match = re.search(r"(## 📡 Hücre Envanteri.*?)(?=## 📡 2G GSM Hücre Envanteri|$)", content, re.DOTALL)
                if lte_section_match:
                    existing_lte_section = lte_section_match.group(1).strip()
                else:
                    # Maybe it is just ## 📡 Hücre Envanteri
                    lte_section_match = re.search(r"(## 📡 Hücre Envanteri.*)$", content, re.DOTALL)
                    if lte_section_match:
                        existing_lte_section = lte_section_match.group(1).strip()
                
                # Try to extract existing LTE header details
                match_bands = re.search(r"- \*\*Kullanılan Bandlar\*\*: `([^`\n]+)`", content)
                if match_bands:
                    existing_header_lte = match_bands.group(1)
            
            # Formulate the GSM section
            gsm_bands = sorted(list(set(c["band"] for c in cells)))
            gsm_arfcns = sorted(list(set(c["arfcn"] for c in cells)))
            
            gsm_links = "\n".join(f"- [[Cell_GSM_ARFCN{c['arfcn']}]] (Band {c['band']}, ARFCN {c['arfcn']})" for c in cells)
            
            gsm_section = f"""## 📡 2G GSM Hücre Envanteri
Bu operatöre ait taramalarda keşfedilen aktif 2G GSM hücreleri:

- **Toplam GSM Hücre Sayısı**: **{len(cells)}**
- **GSM Band Dağılımı**: `{", ".join(gsm_bands)}`
- **Aktif GSM ARFCN Listesi**: `{", ".join(str(a) for a in gsm_arfcns)}`

### Hücre Listesi:
{gsm_links}"""

            # If the file didn't exist or didn't have LTE section, generate a clean one
            if not existing_lte_section:
                existing_lte_section = f"""## 📡 Hücre Envanteri
Bu operatöre ait taramalarda keşfedilen aktif canlı hücreler:
*(Henüz taranmış LTE hücresi bulunmuyor)*"""
                
            combined_bands = existing_header_lte if existing_header_lte else "Bilinmiyor"
            if gsm_bands:
                combined_bands = f"{combined_bands} (LTE) | {', '.join(gsm_bands)} (GSM)"
                
            op_content = f"""---
title: "Operator_{plmn_fmt}"
source: "Şebeke Operatör Analizi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["operator", "plmn", "{op_name.lower().replace(' tr', '').replace(' ', '')}"]
---

# Operatör Profil Raporu: {op_name}

- **Operatör Kodu (MCC-MNC)**: `{plmn_fmt}`
- **Kullanılan Bandlar**: `{combined_bands}`
- **En Son Tarama Tarihi**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

---

{existing_lte_section}

---

{gsm_section}
"""
            self.log_action("CREATE/UPDATE", op_path, f"Operatör profil sayfası güncellendi (LTE + GSM): {op_filename}")
            self.write_file(op_path, op_content)

    def update_band_pages(self, all_gsm_cells):
        gsm_by_band = {}
        for c in all_gsm_cells:
            band = c.get("band", "GSM900")
            gsm_by_band.setdefault(band, []).append(c)
            
        for band in ["GSM900", "DCS1800"]:
            cells = gsm_by_band.get(band, [])
            band_filename = f"GSM_Band_{band}.md"
            band_path = os.path.join(self.dirs["bands"], band_filename)
            
            if not cells:
                # Write placeholder if no cells found yet
                band_content = f"""---
title: "GSM_Band_{band}"
source: "Frekans Band Analizi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["band", "gsm", "spectrum"]
---

# GSM Frekans Band Raporu: {band}

- **ARFCN Kullanım Aralığı**: `N/A`
- **Operatör Dağılım İstatistiği**: `0 hücre`
- **Toplam Hücre Sayısı**: **0**

---

## 📡 Band Hücre Envanteri
{band} spektrumunda henüz aktif GSM hücresi keşfedilmedi.
"""
                self.log_action("CREATE/UPDATE", band_path, f"GSM Band sayfası boş olarak güncellendi: {band_filename}")
                self.write_file(band_path, band_content)
                continue
                
            arfcns = sorted(list(set(c["arfcn"] for c in cells)))
            
            # Operator distribution
            op_dist = {}
            for c in cells:
                op_n = c.get("operator_name", "Bilinmeyen")
                op_dist[op_n] = op_dist.get(op_n, 0) + 1
            
            op_dist_str = ", ".join(f"{k}: {v} hücre" for k, v in op_dist.items())
            cells_links = "\n".join(f"- [[Cell_GSM_ARFCN{c['arfcn']}]] (Operatör: {c['operator_name']}, ARFCN {c['arfcn']})" for c in cells)
            
            band_content = f"""---
title: "GSM_Band_{band}"
source: "Frekans Band Analizi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["band", "gsm", "spectrum"]
---

# GSM Frekans Band Raporu: {band}

- **ARFCN Kullanım Aralığı**: `{min(arfcns)} - {max(arfcns)}`
- **Operatör Dağılım İstatistiği**: `{op_dist_str}`
- **Toplam Hücre Sayısı**: **{len(cells)}**

---

## 📡 Band Hücre Envanteri
{band} spektrumunda keşfedilen aktif GSM hücre listesi:

{cells_links}
"""
            self.log_action("CREATE/UPDATE", band_path, f"GSM Band sayfası güncellendi: {band_filename}")
            self.write_file(band_path, band_content)

    def rebuild_gsm_neighbor_map(self, all_gsm_cells):
        map_path = os.path.join(self.dirs["references"], "GSM Komşu Haritası.md")
        
        rows = []
        edges = []
        node_labels = {}
        
        # Build relation rows and Mermaid diagram
        for c in all_gsm_cells:
            serving_arfcn = c["arfcn"]
            serving_cid = c.get("cell_id", "Bilinmiyor")
            serving_band = c.get("band", "GSM900")
            serving_cell_name = f"Cell_GSM_ARFCN{serving_arfcn}"
            
            # Get neighbors from markdown body (to keep it completely robust and parsed from files)
            cell_file = os.path.join(self.dirs["cells"], f"{serving_cell_name}.md")
            _, body = parse_frontmatter(cell_file)
            
            # Extract BA lists from markdown tables
            # Pattern matches table row format: | **48** | GSM900 | 944.6 MHz | Vodafone TR | [[Cell_GSM_ARFCN48]] |
            matches = re.finditer(
                r"\|\s*\*\*(\d+)\*\*\s*\|\s*([^\s|]+)\s*\|\s*([^\s|]+)\s*MHz\s*\|\s*([^|]+)\s*\|\s*([^|\n]+)\s*\|",
                body
            )
            
            for m in matches:
                n_arfcn = int(m.group(1))
                n_band = m.group(2).strip()
                n_freq = m.group(3).strip()
                n_op = m.group(4).strip()
                status_link = m.group(5).strip()
                
                n_cell_name = f"Cell_GSM_ARFCN{n_arfcn}"
                n_cell_path = os.path.join(self.dirs["cells"], f"{n_cell_name}.md")
                
                direction = "Tek Yönlü (Unidirectional)"
                # Check bidirectionality
                if os.path.exists(n_cell_path):
                    _, n_body = parse_frontmatter(n_cell_path)
                    # Check if neighbor also lists serving in its table
                    n_matches = re.findall(rf"\|\s*\*\*{serving_arfcn}\*\*\s*\|", n_body)
                    if n_matches:
                        direction = "Karşılıklı (Bidirectional)"
                else:
                    direction = "Taranmamış Keşif (Unscanned)"
                
                # Row format
                rows.append(f"| [[{serving_cell_name}]] | {serving_cid} | {n_arfcn} | {n_band} | {n_freq} MHz | {n_op} | {direction} | `{datetime.now().strftime('%Y-%m-%d')}` |")
                
                # Flowchart details
                source_id = f"Cell_GSM_{serving_arfcn}"
                target_id = f"Cell_GSM_{n_arfcn}"
                
                node_labels[source_id] = f"ARFCN {serving_arfcn}\\nCID {serving_cid}"
                if os.path.exists(n_cell_path):
                    # Get neighbor CID if exists
                    n_fm, _ = parse_frontmatter(n_cell_path)
                    n_cid = n_fm.get("cell_id", "Bilinmiyor")
                    node_labels[target_id] = f"ARFCN {n_arfcn}\\nCID {n_cid}"
                else:
                    node_labels[target_id] = f"ARFCN {n_arfcn}\\n(Taranmamış)"
                    
                edges.append((source_id, target_id, direction))

        rows_str = "\n".join(rows) if rows else "| - | - | - | - | - | - | - | - |"
        
        # Build Mermaid code block
        mermaid_lines = []
        if edges:
            mermaid_lines.append("```mermaid")
            mermaid_lines.append("flowchart TD")
            mermaid_lines.append("  %% Stil Tanımları")
            mermaid_lines.append("  classDef scanned fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#f8fafc;")
            mermaid_lines.append("  classDef unscanned fill:#0f172a,stroke:#475569,stroke-width:1px,stroke-dasharray: 5 5,color:#94a3b8;")
            
            for nid, label in node_labels.items():
                if "(Taranmamış)" in label:
                    mermaid_lines.append(f'  {nid}["{label}"]:::unscanned')
                else:
                    mermaid_lines.append(f'  {nid}["{label}"]:::scanned')
            
            seen_pairs = {}
            for src, tgt, direction in edges:
                pair = tuple(sorted([src, tgt]))
                if direction == "Karşılıklı (Bidirectional)":
                    seen_pairs[pair] = "<-->"
                else:
                    if pair not in seen_pairs:
                        if direction == "Taranmamış Keşif (Unscanned)":
                            seen_pairs[pair] = "-.->"
                        else:
                            seen_pairs[pair] = "-->"
                            
            for (src, tgt), arrow in seen_pairs.items():
                orig_src, orig_tgt = src, tgt
                for s, t, d in edges:
                    if tuple(sorted([s, t])) == (src, tgt):
                        if d != "Taranmamış Keşif (Unscanned)":
                            orig_src, orig_tgt = s, t
                            break
                mermaid_lines.append(f"  {orig_src} {arrow} {orig_tgt}")
            mermaid_lines.append("```")
            
        mermaid_str = "\n".join(mermaid_lines) if mermaid_lines else "*Henüz çizilecek bağlantı bulunamadı.*"
        
        map_content = f"""---
title: "GSM Komşu Haritası"
source: "Topoloji Matrisi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["topology", "relations", "matrix", "gsm"]
---

# GSM Komşu Haritası Matrisi

Bu sayfa, yapılan tüm GSM taramalarından derlenen ve servis hücrelerinin komşuluk ilişkilerini (BA listeleri) özetleyen master veri tabanı tablosudur.

## 🗺️ Görsel Topoloji Şeması

{mermaid_str}

## 📊 İlişki Detay Matrisi

| Servis Hücresi | Servis CID | Komşu ARFCN | Komşu Band | Komşu Frekans | Komşu Operatör Tahmini | Yönlendirme | İlk Tespit Tarihi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{rows_str}
"""
        self.log_action("CREATE/UPDATE", map_path, "Master GSM Komşu Haritası tablosu güncellendi.")
        self.write_file(map_path, map_content)

    def rebuild_index(self, all_gsm_cells, all_lte_cells):
        index_path = os.path.join(self.vault_path, "index.md")
        
        concepts = []
        entities = []
        skills = []
        references = []
        synthesis = []
        
        for k, d in self.dirs.items():
            if not os.path.exists(d):
                continue
            for f in sorted(os.listdir(d)):
                if f.endswith(".md"):
                    page_name = f[:-3]
                    if k == "concepts":
                        concepts.append(f"- [[{page_name}]]")
                    elif k == "entities" and not page_name.startswith("Cell_"):
                        entities.append(f"- [[{page_name}]]")
                    elif k == "skills" and not page_name.startswith("wiki-") and not page_name.startswith("gsm-"):
                        skills.append(f"- [[{page_name}]]")
                    elif k == "references" and page_name not in ["Komşu Haritası", "GSM Komşu Haritası"]:
                        references.append(f"- [[{page_name}]]")
                    elif k == "synthesis":
                        synthesis.append(f"- [[{page_name}]]")

        # Cell links
        lte_links = "\n".join(f"  - [[Cell_EARFCN{c['earfcn']}_PCI{c['pci']}]] (Band {c['band']}, RSRP {c.get('rsrp_dbm', c.get('rsrp', -100))} dBm)" for c in all_lte_cells)
        gsm_links = "\n".join(f"  - [[Cell_GSM_ARFCN{c['arfcn']}]] (GSM-{c['band'].replace('GSM', '')}, {c['operator_name']}, CID {c['cell_id']}, LAC {c['lac']})" for c in all_gsm_cells)
        
        # Unified automation lists
        lte_automation = [
            "  - [[earfcn-validator]] — Girdi EARFCN listesini parse eder ve LimeSDR limitlerini denetler.",
            "  - [[sib-scan-builder]] — Tarama komutunu (`sib-scan.sh`) parametrik olarak inşa eder.",
            "  - [[sib-result-reader]] — SQLite veritabanından hücre listesini JSON formatına çevirir.",
            "  - [[neighbor-reporter]] — SIB4/5/6/7 kontrol yayınlarından komşu ilişkilerini raporlar.",
            "  - [[rescan-feeder]] — Keşfedilen yeni kanalları recursive tarama döngüsüne sokar.",
            "  - [[wiki-ingest-pipeline]] — Tarama sonuçlarını otomatik olarak Obsidian Wiki sayfalarına ingest eder."
        ]
        
        gsm_automation = [
            "  - [[arfcn-validator]] — Girdi ARFCN listesini parse eder, E-GSM ARFCN 0 uyarısını ve LimeSDR limitlerini denetler.",
            "  - [[gsm-scan-builder]] — `grgsm_scanner` ve `grgsm_livemon_headless` komutlarını anten ve concurrency denetimiyle parametrik inşa eder.",
            "  - [[gsmtap-parser]] — UDP 4729 loopback akan GSMTAP paketlerini Python raw socket / tshark ile süzüp Layer 3 SI çözümler.",
            "  - [[gsm-neighbor-reporter]] — Çözümlenen SI2/SI2quater verilerinden komşu ARFCN matrisini hesaplar ve tablolar.",
            "  - [[gsm-wiki-ingest]] — GSM tarama ve komşu verilerini Karpathy formatında otomatik olarak hücre sayfalarına entegre eder."
        ]

        total_pages = 0
        for d in self.dirs.values():
            if os.path.exists(d):
                total_pages += len([f for f in os.listdir(d) if f.endswith(".md")])
        if os.path.exists(index_path):
            total_pages += 1 # index.md itself
            
        concepts_str = "\n".join(concepts) if concepts else "*Klasör boş.*"
        entities_str = "\n".join(entities) if entities else "*Klasör boş.*"
        skills_str = "\n".join(skills) if skills else "*Klasör boş.*"
        references_str = "\n".join(references) if references else "*Klasör boş.*"
        synthesis_str = "\n".join(synthesis) if synthesis else "*Klasör boş.*"

        lte_auto_str = "\n".join(lte_automation)
        gsm_auto_str = "\n".join(gsm_automation)

        index_content = f"""---
title: "LTE Komşu Hücre Analiz Sistemi — Bilgi Deposu Dizini"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
---

# LTE Komşu Hücre Analiz Sistemi — Bilgi Deposu Dizini

*Bu dizin, LTE neighbor cell analysis projesi kapsamındaki tüm domain bilgisini, kod tabanı mimarisini, SIB detaylarını, donanım kılavuzlarını, canlı tarama kayıtlarını ve Faz 4 kapsamında kurulan otomatik ingest akışını kategorize edilmiş şekilde listeler.*

- **Toplam Wiki Sayfa Sayısı**: **{total_pages}**
- **Son Güncelleme Tarihi**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

---

## 📚 Concepts (LTE Teorisi ve Protokoller)
{concepts_str}

---

## 🛠️ Entities (Donanım, Araçlar ve Keşfedilen Hücreler)
{entities_str}

### 📡 Keşfedilen Canlı Hücreler (Discovered Cells)
- **4G LTE Hücreleri:**
{lte_links if lte_links else "  *(Henüz 4G hücresi taranmadı)*"}
- **2G GSM Hücreleri:**
{gsm_links if gsm_links else "  *(Henüz 2G hücresi taranmadı)*"}

---

## ⚙️ Skills (Uygulama ve Kod Kılavuzları)
{skills_str}
- [[arfcn-validator]]
- [[gsm-scan-builder]]
- [[gsmtap-parser]]
- [[gsm-neighbor-reporter]]
- [[gsm-wiki-ingest]]

### 🧬 Özel Hücresel Otomasyon Skills (Faz 3 & 4)
- **LTE Otomasyon Zinciri:**
{lte_auto_str}
- **GSM Otomasyon Zinciri (Phase 3):**
{gsm_auto_str}

---

## 📊 References (Referans Verileri, Tablolar ve Günlükler)
{references_str}
- [[Komşu Haritası]] — Tüm komşuluk ilişkilerini gösteren master veri tabanı matrisi.
- [[GSM Komşu Haritası]] — GSM komşuluk ilişkilerini gösteren master veri tabanı matrisi.
- [[Tarama Log]] — Yapılan tüm tarama geçmişini ve özet verilerini tutan defter.
- [[GSM Tarama Log]] — Yapılan tüm GSM tarama geçmişini ve özet verilerini tutan defter.

---

## 🧬 Synthesis (Uçtan Uca Analizler)
{synthesis_str}

---

*Not: Tüm sayfalar birbirine çift yönlü `[[wikilink]]` bağlantılarıyla bağlanmış olup, Karpathy LLM Wiki 3-layer prensibine göre yönetilmektedir.*
"""
        self.log_action("CREATE/UPDATE", index_path, "Vault Index sayfası (index.md) otomatik olarak yeniden oluşturuldu.")
        self.write_file(index_path, index_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="GSM neighbor scan wiki ingest pipeline")
    parser.add_argument("results_json", help="Path to the JSON file containing grgsm parser and reporter outputs")
    parser.add_argument("vault_path", help="Path to the Obsidian LTE Wiki vault directory")
    parser.add_argument("--dry-run", action="store_true", help="Print actions and output JSON without writing files")
    
    args = parser.parse_args()
    
    if not os.path.exists(args.results_json):
        print(f"Error: Results JSON file not found: {args.results_json}")
        sys.exit(1)
        
    with open(args.results_json, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
        except Exception as e:
            print(f"Error parsing JSON: {e}")
            sys.exit(1)
            
    pipeline = GSMWikiIngestPipeline(args.vault_path, dry_run=args.dry_run)
    
    # 1. Ingest GSM Tarama Log
    pipeline.ingest_tarama_log(data)
    
    # 2. Ingest GSM Cells
    for cell in data.get("cells", []):
        pipeline.ingest_cell(cell)
        
    # 3. Scan cells/ folder, generate operators, bands, neighbor map, and rebuild index
    pipeline.scan_and_rebuild_summaries()
    
    # If dry-run, output the actions JSON as required
    if args.dry_run:
        print("\n=== DRY-RUN ACTIONS JSON ===")
        print(json.dumps(pipeline.actions, indent=2, ensure_ascii=False))
