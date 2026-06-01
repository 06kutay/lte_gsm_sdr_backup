---
title: "LTE Komşu Hücre Analiz Sistemi — Bilgi Deposu Dizini"
created_date: "2026-06-01"
---

# LTE Komşu Hücre Analiz Sistemi — Bilgi Deposu Dizini

*Bu dizin, LTE neighbor cell analysis projesi kapsamındaki tüm domain bilgisini, kod tabanı mimarisini, SIB detaylarını, donanım kılavuzlarını, canlı tarama kayıtlarını ve Faz 4 kapsamında kurulan otomatik ingest akışını kategorize edilmiş şekilde listeler.*

- **Toplam Wiki Sayfa Sayısı**: **42**
- **Son Güncelleme Tarihi**: `2026-06-01 14:56:56`

---

## 📚 Concepts (LTE Teorisi ve Protokoller)
- [[EARFCN]]
- [[Komşu Hücre Analizi]]
- [[LTE Bandlar]]
- [[SIB Genel]]
- [[SIB1]]
- [[SIB3]]
- [[SIB4]]
- [[SIB5]]
- [[SIB6]]
- [[SIB7]]
- [[UARFCN]]

---

## 🛠️ Entities (Donanım, Araçlar ve Keşfedilen Hücreler)
- [[LimeSDR Mini 2.0]]
- [[lte-sib-parser]]
- [[srsRAN]]

### 📡 Keşfedilen Canlı Hücreler (Discovered Cells)
- [[Cell_EARFCN6200_PCI210]] (Band 20, RSRP -100 dBm)
- [[Cell_EARFCN100_PCI265]] (Band 1, RSRP -100 dBm)
- [[Cell_EARFCN3350_PCI112]] (Band 7, RSRP -100 dBm)
- [[Cell_EARFCN1444_PCI82]] (Band 3, RSRP -100 dBm)
- [[Cell_EARFCN1300_PCI45]] (Band 3, RSRP -100 dBm)
- [[Cell_EARFCN2850_PCI192]] (Band 7, RSRP -100 dBm)
- [[Cell_EARFCN6400_PCI189]] (Band 20, RSRP -100 dBm)

---

## ⚙️ Skills (Uygulama ve Kod Kılavuzları)
- [[Docker Kurulum]]
- [[dbparsers]]
- [[earfcn-validator]]
- [[neighbor-reporter]]
- [[rescan-feeder]]
- [[sib-result-reader]]
- [[sib-scan-builder]]
- [[sib-scan.sh]]

### 🧬 Özel LTE Otomasyon Skills (Faz 3 & 4)
- [[earfcn-validator]] — Girdi EARFCN listesini parse eder ve LimeSDR limitlerini denetler.
- [[sib-scan-builder]] — Tarama komutunu (`sib-scan.sh`) parametrik olarak inşa eder.
- [[sib-result-reader]] — SQLite veritabanından hücre listesini JSON formatına çevirir.
- [[neighbor-reporter]] — SIB4/5/6/7 kontrol yayınlarından komşu ilişkilerini raporlar.
- [[rescan-feeder]] — Keşfedilen yeni kanalları recursive tarama döngüsüne sokar.
- [[wiki-ingest-pipeline]] — Tarama sonuçlarını otomatik olarak Obsidian Wiki sayfalarına ingest eder.

---

## 📊 References (Referans Verileri, Tablolar ve Günlükler)
- [[Frekans Tablosu]]
- [[Komşu Haritası]] — Tüm komşuluk ilişkilerini gösteren master veri tabanı matrisi.
- [[Tarama Log]] — Yapılan tüm tarama geçmişini ve özet verilerini tutan defter.

---

## 🧬 Synthesis (Uçtan Uca Analizler)
- [[Sistem Mimarisi]]

---

*Not: Tüm sayfalar birbirine çift yönlü `[[wikilink]]` bağlantılarıyla bağlanmış olup, Karpathy LLM Wiki 3-layer prensibine göre yönetilmektedir.*
