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
            # handle strings
            fm_lines.append(f'{k}: "{v}"')
    fm_lines.append("---")
    return "\n".join(fm_lines) + "\n\n" + body.lstrip()

# Helper to map Operator names based on PLMN MCC_MNC
def get_operator_name(plmn):
    mapping = {
        "28601": "Turkcell",
        "28602": "Vodafone",
        "28603": "Türk Telekom",
        "2861": "Turkcell",
        "2862": "Vodafone",
        "2863": "Türk Telekom"
    }
    cleaned = str(plmn).replace("-", "").replace("_", "")
    return mapping.get(cleaned, f"Bilinmeyen Operatör ({plmn})")

# Helper to normalize PLMN formatting
def format_plmn_name(plmn):
    cleaned = str(plmn).replace("-", "").replace("_", "")
    if len(cleaned) == 5:
        return f"{cleaned[:3]}_{cleaned[3:]}"
    return cleaned

class WikiIngestPipeline:
    def __init__(self, vault_path, dry_run=False):
        self.vault_path = os.path.abspath(vault_path)
        self.dry_run = dry_run
        self.actions = []  # For logging dry run actions
        
        # Ensure directories exist
        self.dirs = {
            "cells": os.path.join(self.vault_path, "cells"),
            "operators": os.path.join(self.vault_path, "operators"),
            "bands": os.path.join(self.vault_path, "bands"),
            "logs": os.path.join(self.vault_path, "logs"),
            "references": os.path.join(self.vault_path, "references"),
            "concepts": os.path.join(self.vault_path, "concepts"),
            "entities": os.path.join(self.vault_path, "entities"),
            "skills": os.path.join(self.vault_path, "skills"),
            "synthesis": os.path.join(self.vault_path, "synthesis"),
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
        if self.dry_run:
            print(f"[DRY-RUN] {action_type} -> {description}")
        else:
            print(f"[INGEST] {action_type} -> {description}")

    def write_file(self, path, content):
        if self.dry_run:
            return
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)

    def ingest_tarama_log(self, data):
        # 1. logs/Tarama Log.md and scan logs
        log_dir = self.dirs["logs"]
        tarama_log_path = os.path.join(log_dir, "Tarama Log.md")
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        date_stamp = datetime.now().strftime("%Y%m%d")
        
        command = data.get("command", "./sib-scan.sh -d soapy -a \"rxant=LNAH\" -q \"1300\"")
        db_path = data.get("db_path", f"/vol/output/scan_{date_stamp}.sqlite")
        iteration = data.get("iteration", 1)
        earfcns_list = data.get("earfcns_list", "1300, 1444, 3350, 6200")
        
        summary = data.get("summary", {})
        total_cells = summary.get("total_cells", 0)
        sib5_decoded = summary.get("sib5_decoded", 0)
        unique_plmn = summary.get("unique_plmn", 0)
        relations_count = len(data.get("relations", []))
        
        # Individual scan log path
        scan_log_filename = f"scan_{date_stamp}_iter{iteration}.md"
        scan_log_path = os.path.join(log_dir, scan_log_filename)
        
        # Write individual scan log
        scan_log_content = f"""---
title: "Tarama Detayı - {now_str}"
source: "Tarama Sonucu"
created_date: "{now_str[:10]}"
tags: ["tarama-log", "scan"]
type: "log"
---

# Tarama Raporu: {now_str} (İterasyon: {iteration})

- **Veritabanı Dosyası**: `{db_path}`
- **Taranan EARFCN Listesi**: `{earfcns_list}`
- **Kullanılan Komut**: `{command}`
- **İterasyon**: {iteration}

## 📊 İstatistikler
- Keşfedilen Toplam Hücre: **{total_cells}**
- SIB5 Çözümleme Sayısı: **{sib5_decoded}**
- Benzersiz Operatör (PLMN) Sayısı: **{unique_plmn}**
- Çıkarılan Komşu İlişki Sayısı: **{relations_count}**

## 📡 Keşif Sonuçları
Detaylı hücre ve band analizleri [[index]] üzerinden görüntülenebilir.
"""
        self.log_action("CREATE", scan_log_path, f"Tarama log detayı oluşturuldu: {scan_log_filename}")
        self.write_file(scan_log_path, scan_log_content)

        # Update consolidated logs/Tarama Log.md
        log_entry = f"""

### Tarama: {now_str} (İterasyon: {iteration})
- **Log Detay Raporu**: [[{scan_log_filename[:-3]}]]
- **Veritabanı Dosyası**: `{db_path}`
- **EARFCN Listesi**: `{earfcns_list}`
- **Komut**: `{command}`
- **Özet Metrikler**:
  - Toplam Hücre: **{total_cells}**
  - SIB5 Çözümleme Sayısı: **{sib5_decoded}**
  - Benzersiz PLMN: **{unique_plmn}**
  - Komşu İlişkileri: **{relations_count}**
"""
        
        if os.path.exists(tarama_log_path):
            self.log_action("APPEND", tarama_log_path, "Tarama günlüğüne yeni kayıt eklendi.")
            if not self.dry_run:
                with open(tarama_log_path, "a", encoding="utf-8") as f:
                    f.write(log_entry)
        else:
            self.log_action("CREATE", tarama_log_path, "Tarama Günlüğü (Tarama Log.md) oluşturuldu.")
            tarama_log_init = f"""---
title: "Tarama Log"
source: "Tarama Log Defteri"
created_date: "{now_str[:10]}"
tags: ["tarama-log"]
type: "log"
---

# Tarama Log Defteri

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan her yeni taramanın tarihini, taranan EARFCN listesini ve tarama sonucu elde edilen özet metrikleri tarihsel olarak kayıt altında tutar.

---

## 📅 Tarama Geçmişi
{log_entry}"""
            self.write_file(tarama_log_path, tarama_log_init)

    def ingest_cell(self, cell, relations_map):
        earfcn = cell.get("earfcn")
        pci = cell.get("pci")
        cell_id = cell.get("cell_id", "Bilinmiyor")
        plmn = cell.get("plmn", "Bilinmiyor")
        tac = cell.get("tac", "Bilinmiyor")
        band = cell.get("band", 0)
        freq_mhz = cell.get("freq_mhz", 0.0)
        rsrp = cell.get("rsrp", -100)
        sibs = cell.get("sibs_decoded", [])
        
        cell_name = f"Cell_EARFCN{earfcn}_PCI{pci}"
        cell_path = os.path.join(self.dirs["cells"], f"{cell_name}.md")
        
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        first_seen = now_str
        last_seen = now_str
        changelog = []
        existing_sibs = set(sibs)
        existing_sib5_raw = cell.get("sib5_raw", {})
        
        # Merge if exists
        if os.path.exists(cell_path):
            old_fm, old_body = parse_frontmatter(cell_path)
            first_seen = old_fm.get("first_seen", now_str)
            last_seen = now_str
            
            # Detect changes for changelog
            old_tac = old_fm.get("tac", "Bilinmiyor")
            old_cell_id = old_fm.get("cell_id", "Bilinmiyor")
            
            if old_tac != "Bilinmiyor" and old_tac != tac:
                changelog.append(f" - **{now_str}**: TAC değişti: `{old_tac}` -> `{tac}`")
            if old_cell_id != "Bilinmiyor" and old_cell_id != cell_id:
                changelog.append(f" - **{now_str}**: Cell Identity değişti: `{old_cell_id}` -> `{cell_id}`")
                
            # Merge SIBs list
            old_sibs_raw = old_fm.get("sibs_decoded", [])
            old_sibs = set(int(x) for x in old_sibs_raw if str(x).isdigit())
            new_sibs = set(sibs)
            if new_sibs - old_sibs:
                resolved_sibs = sorted(list(new_sibs - old_sibs))
                changelog.append(f" - **{now_str}**: Yeni SIB blokları çözüldü: `{resolved_sibs}`")
            existing_sibs = old_sibs.union(new_sibs)
            
            # Changelog parsing from existing body
            changelog_section_match = re.search(r"## Değişiklik Günlüğü \(Changelog\)(.*?)(?:\n\n|$)", old_body, re.DOTALL)
            if changelog_section_match:
                existing_changelog = changelog_section_match.group(1).strip()
                if existing_changelog:
                    # prepend new items if any
                    if changelog:
                        changelog = changelog + [existing_changelog]
                    else:
                        changelog = [existing_changelog]
            
            self.log_action("UPDATE", cell_path, f"Hücre sayfası güncellendi: {cell_name}")
        else:
            self.log_action("CREATE", cell_path, f"Hücre sayfası oluşturuldu: {cell_name}")
        
        # Build cell markdown
        fm = {
            "earfcn": earfcn,
            "pci": pci,
            "cell_id": cell_id,
            "plmn": plmn,
            "tac": tac,
            "band": band,
            "freq_mhz": freq_mhz,
            "tags": ["cell", "lte", f"band{band}"],
            "first_seen": first_seen,
            "last_seen": last_seen,
            "sibs_decoded": sorted(list(existing_sibs))
        }
        
        # SIB3 Reselection Params
        sib3_section = "*SIB3 verisi bu taramada çözümlenemedi.*"
        if 3 in existing_sibs:
            sib3_section = f"""- **Minimum Alım Seviyesi (q-RxLevMin)**: `-116 dBm` (varsayılan)
- **Hücre Seçim Önceliği (cellReselectionPriority)**: `6`"""
            
        # SIB5/Komşu Listesi
        neighbors_section = "*Komşu hücre listesi bulunmuyor veya SIB5 çözümlenemedi.*"
        cell_rel = relations_map.get(cell_name, {})
        inter_freq_list = cell_rel.get("neighbors", {}).get("inter_freq", [])
        
        if inter_freq_list:
            neighbors_section = ""
            for item in inter_freq_list:
                n_earfcn = item["earfcn"]
                priority = item.get("priority", "N/A")
                scanned = item.get("scanned", False)
                link_type = item.get("link_type", "unidirectional")
                
                # Check if we have a scanned page name for neighbor
                # Scan cell names to link properly
                status_color = "#2ec4b6" if link_type == "bidirectional" else "#e65c00"
                link_icon = "⇔ ÇİFT YÖNLÜ" if link_type == "bidirectional" else "⇒ TEK YÖNLÜ"
                
                status_text = f'<span style="color: {status_color}; font-weight: bold;">{link_icon}</span>'
                if not scanned:
                    status_text = '<span style="color: #ff4d4d; font-weight: bold;">✗ TARANMAMIŞ</span> (Kuyrukta)'
                
                # Find matching neighbor name from relations
                match_name = f"Cell_EARFCN{n_earfcn}"
                # Let's search if any cell in relations has this earfcn
                found_match = False
                for r_cell_name in relations_map.keys():
                    if r_cell_name.startswith(f"Cell_EARFCN{n_earfcn}_"):
                        match_name = r_cell_name
                        found_match = True
                        break
                
                target_link = f"[[{match_name}]]" if found_match else f"EARFCN {n_earfcn}"
                
                neighbors_section += f"""- Komşu Frekans: **{target_link}**
  - Öncelik: `{priority}`
  - Durum: {status_text}\n"""
                
        changelog_content = ""
        if changelog:
            changelog_content = "\n## Değişiklik Günlüğü (Changelog)\n" + "\n".join(changelog) + "\n"

        body = f"""# Hücre Detayı: {cell_name}

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan pasif LTE taramalarında keşfedilen hücreye ait SIB parametrelerini ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SIB1)
- **Merkez Frekans**: {freq_mhz} MHz (Band {band} - [[LTE Bandlar]] / [[Frekans Tablosu]])
- **Operatör**: {get_operator_name(plmn)} (MCC-MNC: `{format_plmn_name(plmn)}`)
- **TAC (Tracking Area Code)**: `{tac}`
- **Cell Identity (28-bit)**: `{cell_id}`
- **Sinyal Gücü (RSRP)**: `{rsrp} dBm`

---

## 2. Yeniden Seçim Parametreleri (SIB3)
{sib3_section}

---

## 3. Komşu İlişki Raporu (SIB4/SIB5)
{neighbors_section}
{changelog_content}
---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[Tarama Log]] sayfasında mevcuttur.
"""
        full_content = dump_frontmatter(fm, body)
        self.write_file(cell_path, full_content)

    def scan_and_rebuild_summaries(self):
        # Scan cells/ directory to get ALL active pages and compile operator & band pages
        cells_dir = self.dirs["cells"]
        all_cells = []
        
        if os.path.exists(cells_dir):
            for filename in os.listdir(cells_dir):
                if filename.endswith(".md"):
                    cell_path = os.path.join(cells_dir, filename)
                    fm, _ = parse_frontmatter(cell_path)
                    if fm:
                        all_cells.append(fm)
                        
        print(f"[INGEST] Taramada toplam {len(all_cells)} tescilli hücre veri tabanı dosyası okundu.")
        
        # Group by operator
        operators = {}
        for c in all_cells:
            plmn = c.get("plmn", "Bilinmiyor")
            if plmn != "Bilinmiyor":
                plmn_fmt = format_plmn_name(plmn)
                operators.setdefault(plmn_fmt, []).append(c)
                
        # Update operator pages
        for plmn_fmt, cells in operators.items():
            op_name = get_operator_name(plmn_fmt.replace("_", ""))
            op_filename = f"Operator_{plmn_fmt}.md"
            op_path = os.path.join(self.dirs["operators"], op_filename)
            
            # Unique bands & EARFCN ranges
            bands = sorted(list(set(c["band"] for c in cells)))
            earfcns = sorted(list(set(c["earfcn"] for c in cells)))
            
            cells_links = "\n".join(f"- [[Cell_EARFCN{c['earfcn']}_PCI{c['pci']}]] (Band {c['band']}, PCI {c['pci']})" for c in cells)
            
            op_content = f"""---
title: "Operator_{plmn_fmt}"
source: "Şebeke Operatör Analizi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["operator", "plmn", "{op_name.lower().replace(' ', '')}"]
---

# Operatör Profil Raporu: {op_name}

- **Operatör Kodu (MCC-MNC)**: `{plmn_fmt}`
- **Kullanılan Bandlar**: `{", ".join(str(b) for b in bands)}`
- **EARFCN Aralıkları**: `{min(earfcns)} - {max(earfcns)}`
- **Toplam Tespit Edilen Hücre**: **{len(cells)}**
- **En Son Tarama Tarihi**: `{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}`

---

## 📡 Hücre Envanteri
Bu operatöre ait taramalarda keşfedilen aktif canlı hücreler:

{cells_links}
"""
            self.log_action("CREATE/UPDATE", op_path, f"Operatör sayfası güncellendi: {op_filename}")
            self.write_file(op_path, op_content)

        # Group by band
        bands = {}
        for c in all_cells:
            band = c.get("band", 0)
            if band:
                bands.setdefault(band, []).append(c)
                
        # Update band pages
        for band, cells in bands.items():
            band_filename = f"Band_{band}.md"
            band_path = os.path.join(self.dirs["bands"], band_filename)
            
            earfcns = sorted(list(set(c["earfcn"] for c in cells)))
            # Operator distribution
            op_dist = {}
            for c in cells:
                op_name = get_operator_name(c["plmn"])
                op_dist[op_name] = op_dist.get(op_name, 0) + 1
            
            op_dist_str = ", ".join(f"{k}: {v} hücre" for k, v in op_dist.items())
            cells_links = "\n".join(f"- [[Cell_EARFCN{c['earfcn']}_PCI{c['pci']}]] (Operatör: {get_operator_name(c['plmn'])}, PCI {c['pci']})" for c in cells)
            
            band_content = f"""---
title: "Band_{band}"
source: "Frekans Band Analizi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["band", "lte", "spectrum"]
---

# Frekans Band Raporu: Band {band}

- **EARFCN Kullanım Aralığı**: `{min(earfcns)} - {max(earfcns)}`
- **Operatör Dağılım İstatistiği**: `{op_dist_str}`
- **Toplam Hücre Sayısı**: **{len(cells)}**

---

## 📡 Band Hücre Envanteri
Band {band} spektrumunda keşfedilen aktif hücre listesi:

{cells_links}
"""
            self.log_action("CREATE/UPDATE", band_path, f"Band sayfası güncellendi: {band_filename}")
            self.write_file(band_path, band_content)

        # Master neighbor map update
        self.rebuild_neighbor_map(all_cells)

        # Rebuild main index.md
        self.rebuild_index(all_cells)

    def rebuild_neighbor_map(self, all_cells):
        map_path = os.path.join(self.dirs["references"], "Komşu Haritası.md")
        
        # Build relation rows
        # Scan cells to extract neighbor lists
        rows = []
        cells_dir = self.dirs["cells"]
        
        edges = []
        node_labels = {}
        
        for c in all_cells:
            serving_earfcn = c["earfcn"]
            serving_pci = c["pci"]
            
            cell_name = f"Cell_EARFCN{serving_earfcn}_PCI{serving_pci}"
            cell_file = os.path.join(cells_dir, f"{cell_name}.md")
            
            # Read relations from files
            _, body = parse_frontmatter(cell_file)
            
            # Extract neighbor blocks
            # - Komşu Frekans: [[Cell_EARFCN1444_PCI82]] (EARFCN 1444 / Band 3)
            #   - Öncelik: 6
            #   - Durum: bidirectional / unidirectional
            matches = re.finditer(
                r"- Komşu Frekans:\s*\**(?:\[\[Cell_EARFCN(\d+)_PCI(\d+)\]\]|EARFCN\s*(\d+))\**.*?\n\s*-\s*Öncelik:\s*`?([^`\n]+)`?.*?\n\s*-\s*Durum:\s*([^\n]+)",
                body, re.DOTALL
            )
            
            for m in matches:
                n_earfcn = m.group(1) or m.group(3)
                n_pci = m.group(2) or "N/A"
                priority = m.group(4)
                status_text = m.group(5)
                
                direction = "Tek Yönlü (Unidirectional)"
                if "⇔ ÇİFT YÖNLÜ" in status_text or "bidirectional" in status_text.lower():
                    direction = "Karşılıklı (Bidirectional)"
                elif "✗ TARANMAMIŞ" in status_text:
                    direction = "Taranmamış Keşif (Unscanned)"
                    
                rows.append(f"| [[{cell_name}]] | {serving_earfcn} | {serving_pci} | Inter-Freq (LTE) | {n_earfcn} | {n_pci} | {direction} | `{datetime.now().strftime('%Y-%m-%d')}` |")
                
                # Collect details for Mermaid
                source_id = f"Cell_{serving_earfcn}_{serving_pci}"
                target_id = f"Cell_{n_earfcn}_{n_pci.replace('/', '_')}"
                
                node_labels[source_id] = f"EARFCN {serving_earfcn}\\nPCI {serving_pci}"
                if n_pci != "N/A":
                    node_labels[target_id] = f"EARFCN {n_earfcn}\\nPCI {n_pci}"
                else:
                    node_labels[target_id] = f"EARFCN {n_earfcn}\\n(Taranmamış)"
                    
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
            
            # Add nodes
            for nid, label in node_labels.items():
                if "(Taranmamış)" in label:
                    mermaid_lines.append(f'  {nid}["{label}"]:::unscanned')
                else:
                    mermaid_lines.append(f'  {nid}["{label}"]:::scanned')
            
            # Group and deduplicate edges
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
                # Get original direction
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
title: "Komşu Haritası"
source: "Topoloji Matrisi"
created_date: "{datetime.now().strftime('%Y-%m-%d')}"
tags: ["topology", "relations", "matrix"]
---

# LTE Komşu Haritası Matrisi

Bu sayfa, yapılan tüm taramalardan derlenen ve servis hücrelerinin komşuluk ilişkilerini özetleyen master veri tabanı tablosudur.

## 🗺️ Görsel Topoloji Şeması

{mermaid_str}

## 📊 İlişki Detay Matrisi

| Servis Hücresi | Servis EARFCN | Servis PCI | Komşu Tipi | Komşu EARFCN | Komşu PCI | Yönlendirme | İlk Tespit Tarihi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
{rows_str}
"""
        self.log_action("CREATE/UPDATE", map_path, "Master Komşu Haritası tablosu güncellendi.")
        self.write_file(map_path, map_content)

    def rebuild_index(self, all_cells):
        index_path = os.path.join(self.vault_path, "index.md")
        
        # Scan directories to list files
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
                    elif k == "skills" and not page_name.startswith("wiki-"):
                        skills.append(f"- [[{page_name}]]")
                    elif k == "references" and page_name != "Komşu Haritası":
                        references.append(f"- [[{page_name}]]")
                    elif k == "synthesis":
                        synthesis.append(f"- [[{page_name}]]")

        # Cell links
        cells_links = "\n".join(f"- [[Cell_EARFCN{c['earfcn']}_PCI{c['pci']}]] (Band {c['band']}, RSRP {c.get('rsrp', -100)} dBm)" for c in all_cells)
        
        # Skills list including Phase 3/4
        automation_skills = [
            "- [[earfcn-validator]] — Girdi EARFCN listesini parse eder ve LimeSDR limitlerini denetler.",
            "- [[sib-scan-builder]] — Tarama komutunu (`sib-scan.sh`) parametrik olarak inşa eder.",
            "- [[sib-result-reader]] — SQLite veritabanından hücre listesini JSON formatına çevirir.",
            "- [[neighbor-reporter]] — SIB4/5/6/7 kontrol yayınlarından komşu ilişkilerini raporlar.",
            "- [[rescan-feeder]] — Keşfedilen yeni kanalları recursive tarama döngüsüne sokar.",
            "- [[wiki-ingest-pipeline]] — Tarama sonuçlarını otomatik olarak Obsidian Wiki sayfalarına ingest eder."
        ]

        total_pages = 0
        for d in self.dirs.values():
            if os.path.exists(d):
                total_pages += len([f for f in os.listdir(d) if f.endswith(".md")])
        if os.path.exists(index_path):
            total_pages += 1 # Include index.md itself
            
        concepts_str = "\n".join(concepts) if concepts else "*Klasör boş.*"
        entities_str = "\n".join(entities) if entities else "*Klasör boş.*"
        skills_str = "\n".join(skills) if skills else "*Klasör boş.*"
        references_str = "\n".join(references) if references else "*Klasör boş.*"
        synthesis_str = "\n".join(synthesis) if synthesis else "*Klasör boş.*"
        automation_skills_str = "\n".join(automation_skills)

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
{cells_links if cells_links else "*Henüz hücre taranmadı.*"}

---

## ⚙️ Skills (Uygulama ve Kod Kılavuzları)
{skills_str}

### 🧬 Özel LTE Otomasyon Skills (Faz 3 & 4)
{automation_skills_str}

---

## 📊 References (Referans Verileri, Tablolar ve Günlükler)
{references_str}
- [[Komşu Haritası]] — Tüm komşuluk ilişkilerini gösteren master veri tabanı matrisi.
- [[Tarama Log]] — Yapılan tüm tarama geçmişini ve özet verilerini tutan defter.

---

## 🧬 Synthesis (Uçtan Uca Analizler)
{synthesis_str}

---

*Not: Tüm sayfalar birbirine çift yönlü `[[wikilink]]` bağlantılarıyla bağlanmış olup, Karpathy LLM Wiki 3-layer prensibine göre yönetilmektedir.*
"""
        self.log_action("CREATE/UPDATE", index_path, "Vault Index sayfası (index.md) otomatik olarak yeniden oluşturuldu.")
        self.write_file(index_path, index_content)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="LTE neighbor scan wiki ingest pipeline")
    parser.add_argument("results_json", help="Path to the JSON file containing result-reader and neighbor-reporter output")
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
            
    pipeline = WikiIngestPipeline(args.vault_path, dry_run=args.dry_run)
    
    # 1. Ingest Tarama Log
    pipeline.ingest_tarama_log(data)
    
    # Map neighbor relations by serving cell name
    relations_map = {}
    for rel in data.get("relations", []):
        relations_map[rel["serving_cell"]] = rel
        
    # 2. Ingest Cells
    for cell in data.get("cells", []):
        pipeline.ingest_cell(cell, relations_map)
        
    # 3. Scan cells/ folder, generate operators, bands, neighbor map, and rebuild index
    pipeline.scan_and_rebuild_summaries()
    
    # If dry-run, output the actions JSON as required
    if args.dry_run:
        print("\n=== DRY-RUN ACTIONS JSON ===")
        print(json.dumps(pipeline.actions, indent=2, ensure_ascii=False))
