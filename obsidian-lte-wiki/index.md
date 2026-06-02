---
title: "LTE Komşu Hücre Analiz Sistemi — Bilgi Deposu Dizini"
created_date: "2026-06-02"
---

# LTE Komşu Hücre Analiz Sistemi — Bilgi Deposu Dizini

*Bu dizin, LTE neighbor cell analysis projesi kapsamındaki tüm domain bilgisini, kod tabanı mimarisini, SIB detaylarını, donanım kılavuzlarını, canlı tarama kayıtlarını ve Faz 4 kapsamında kurulan otomatik ingest akışını kategorize edilmiş şekilde listeler.*

- **Toplam Wiki Sayfa Sayısı**: **74**
- **Son Güncelleme Tarihi**: `2026-06-02 11:31:07`

---

## 📚 Concepts (LTE Teorisi ve Protokoller)
- [[EARFCN]]
- [[GSM ARFCN]]
- [[GSM Bandlar]]
- [[GSM Komsu Analizi]]
- [[GSM SI Genel]]
- [[GSM SI1]]
- [[GSM SI13]]
- [[GSM SI2]]
- [[GSM SI2bis]]
- [[GSM SI2quater]]
- [[GSM SI2ter]]
- [[GSM SI3]]
- [[GSM SI4]]
- [[GSM SI5]]
- [[GSM SI5bis]]
- [[GSM SI5ter]]
- [[GSM vs LTE Komşu Tespiti]]
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
- [[GSMTAP]]
- [[LimeSDR Mini 2.0]]
- [[gr-gsm]]
- [[grgsm_livemon_headless]]
- [[grgsm_scanner]]
- [[lte-sib-parser]]
- [[srsRAN]]

### 📡 Keşfedilen Canlı Hücreler (Discovered Cells)
- **4G LTE Hücreleri:**
  - [[Cell_EARFCN6200_PCI210]] (Band 20, RSRP -100 dBm)
  - [[Cell_EARFCN100_PCI265]] (Band 1, RSRP -100 dBm)
  - [[Cell_EARFCN3350_PCI112]] (Band 7, RSRP -100 dBm)
  - [[Cell_EARFCN1444_PCI82]] (Band 3, RSRP -100 dBm)
  - [[Cell_EARFCN1300_PCI45]] (Band 3, RSRP -100 dBm)
  - [[Cell_EARFCN2850_PCI192]] (Band 7, RSRP -100 dBm)
  - [[Cell_EARFCN6400_PCI189]] (Band 20, RSRP -100 dBm)
- **2G GSM Hücreleri:**
  - [[Cell_GSM_ARFCN60]] (GSM-900, Turkcell, CID 7349, LAC 33006)
  - [[Cell_GSM_ARFCN120]] (GSM-900, Vodafone TR, CID 16528, LAC 50602)

---

## ⚙️ Skills (Uygulama ve Kod Kılavuzları)
- [[Docker Kurulum]]
- [[arfcn-validator]]
- [[dbparsers]]
- [[earfcn-validator]]
- [[gsmtap-parser]]
- [[neighbor-reporter]]
- [[rescan-feeder]]
- [[sib-result-reader]]
- [[sib-scan-builder]]
- [[sib-scan.sh]]
- [[arfcn-validator]]
- [[gsm-scan-builder]]
- [[gsmtap-parser]]
- [[gsm-neighbor-reporter]]
- [[gsm-wiki-ingest]]

### 🧬 Özel Hücresel Otomasyon Skills (Faz 3 & 4)
- **LTE Otomasyon Zinciri:**
  - [[earfcn-validator]] — Girdi EARFCN listesini parse eder ve LimeSDR limitlerini denetler.
  - [[sib-scan-builder]] — Tarama komutunu (`sib-scan.sh`) parametrik olarak inşa eder.
  - [[sib-result-reader]] — SQLite veritabanından hücre listesini JSON formatına çevirir.
  - [[neighbor-reporter]] — SIB4/5/6/7 kontrol yayınlarından komşu ilişkilerini raporlar.
  - [[rescan-feeder]] — Keşfedilen yeni kanalları recursive tarama döngüsüne sokar.
  - [[wiki-ingest-pipeline]] — Tarama sonuçlarını otomatik olarak Obsidian Wiki sayfalarına ingest eder.
- **GSM Otomasyon Zinciri (Phase 3):**
  - [[arfcn-validator]] — Girdi ARFCN listesini parse eder, E-GSM ARFCN 0 uyarısını ve LimeSDR limitlerini denetler.
  - [[gsm-scan-builder]] — `grgsm_scanner` ve `grgsm_livemon_headless` komutlarını anten ve concurrency denetimiyle parametrik inşa eder.
  - [[gsmtap-parser]] — UDP 4729 loopback akan GSMTAP paketlerini Python raw socket / tshark ile süzüp Layer 3 SI çözümler.
  - [[gsm-neighbor-reporter]] — Çözümlenen SI2/SI2quater verilerinden komşu ARFCN matrisini hesaplar ve tablolar.
  - [[gsm-wiki-ingest]] — GSM tarama ve komşu verilerini Karpathy formatında otomatik olarak hücre sayfalarına entegre eder.

---

## 📊 References (Referans Verileri, Tablolar ve Günlükler)
- [[Frekans Tablosu]]
- [[GSM Frekans Tablosu]]
- [[Komşu Haritası]] — Tüm komşuluk ilişkilerini gösteren master veri tabanı matrisi.
- [[GSM Komşu Haritası]] — GSM komşuluk ilişkilerini gösteren master veri tabanı matrisi.
- [[Tarama Log]] — Yapılan tüm tarama geçmişini ve özet verilerini tutan defter.
- [[GSM Tarama Log]] — Yapılan tüm GSM tarama geçmişini ve özet verilerini tutan defter.

---

## 🧬 Synthesis (Uçtan Uca Analizler)
*Klasör boş.*

---

*Not: Tüm sayfalar birbirine çift yönlü `[[wikilink]]` bağlantılarıyla bağlanmış olup, Karpathy LLM Wiki 3-layer prensibine göre yönetilmektedir.*
