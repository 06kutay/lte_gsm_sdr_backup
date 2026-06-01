#!/usr/bin/env python3
import os

def main():
    skills_dir = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki/skills"
    os.makedirs(skills_dir, exist_ok=True)
    
    skills = {
        "earfcn-validator": {
            "title": "earfcn-validator",
            "desc": "Girdi EARFCN listesini parse eder, downlink frekanslarını ve band numaralarını 3GPP standartlarına göre hesaplar ve LimeSDR Mini 2.0 limitlerini doğrular."
        },
        "sib-scan-builder": {
            "title": "sib-scan-builder",
            "desc": "Doğrulanmış kanallarla SOAPY parametreli `sib-scan.sh` Docker konteyner çalıştırma komutlarını otomatik olarak oluşturur."
        },
        "sib-result-reader": {
            "title": "sib-result-reader",
            "desc": "Tarama sonrasında SQLite veritabanından hücre listesini ve decode edilmiş SIB durumlarını JSON formatına çevirir."
        },
        "neighbor-reporter": {
            "title": "neighbor-reporter",
            "desc": "SIB4/5/6/7 kontrol yayınlarından komşu ilişkilerini, tek yönlü/çift yönlü bağları ve taranmamış kanalları raporlar."
        },
        "rescan-feeder": {
            "title": "rescan-feeder",
            "desc": "Keşfedilen yeni komşu EARFCN kanallarını recursive tarama döngüsüne sokarak recursive aramayı yönetir."
        },
        "wiki-ingest-pipeline": {
            "title": "wiki-ingest-pipeline",
            "desc": "Tarama sonuçlarını ve komşuluk ilişkilerini otomatik olarak cell, operator, band ve log sayfaları halinde Obsidian Wiki'ye ingest eder."
        }
    }
    
    for name, info in skills.items():
        path = os.path.join(skills_dir, f"{name}.md")
        content = f"""---
title: "{info['title']}"
source: "Özel LTE Otomasyon Skill"
tags: ["skill", "automation", "lte"]
---

# {info['title']}

{info['desc']}

---

## ⚙️ Fonksiyon ve Kullanım
Bu skill, pasif LTE tarama zincirinin bir parçası olarak otomatik çalıştırılır. Detaylı teknik kılavuzu projenin `.skills/{name}/SKILL.md` dosyasında yer almaktadır.

## 🔗 İlgili Sayfalar
- [[Sistem Mimarisi]]
- [[index]]
"""
        with open(path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created doc page for skill: {name}")

if __name__ == "__main__":
    main()
