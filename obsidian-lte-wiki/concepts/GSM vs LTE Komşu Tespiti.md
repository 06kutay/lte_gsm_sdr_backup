---
title: GSM vs LTE Komşu Tespiti
source: 3GPP TS 44.018 / 3GPP TS 36.331
created_date: 2026-06-02
tags:
  - gsm
  - lte
  - comparison
  - concept
---

# GSM vs LTE Komşu Hücre Tespiti ve Karşılaştırma Analizi

Mobil haberleşme standartlarının evrimi süresince, mobil cihazların (MS/UE) en iyi sinyal veren hücreye kesintisiz şekilde kamp kurmasını (cell reselection) ve aktif çağrı geçişlerini (handover) yönetme mantığı temelde benzer kalmış olsa da, protokol katmanlarındaki uygulama detayları, mesaj tipleri ve kullanılan parametre isimleri ciddi ölçüde değişmiştir.

Bu analiz, **GSM (2G)** ve **LTE (4G)** şebekelerindeki komşu hücre tespiti, yayın mekanizmaları, analiz araçları ve çıktı formatları arasındaki farkları karşılaştırmalı olarak sunar.

---

## 1. Protokol ve Mesaj Eşleşme Tablosu

Aşağıdaki tablo, iki teknoloji arasında doğrudan kavramsal ve işlevsel olarak eşleşen kontrol bloklarını listeler:

| İşlev | GSM (2G) Dünyası | LTE (4G) Dünyası | Eşleşme ve Analiz Notları |
| :--- | :--- | :--- | :--- |
| **Genel Sistem Yayını** | **System Information (SI)** | **System Information Block (SIB)** | Her iki yapıda havadan periyodik olarak yayınlanan kontrol/konfigürasyon mesaj gruplarıdır. (Bkz: [[GSM SI Genel]] & [[SIB Genel]]) |
| **Hücre Kimliği & Seçimi**| **[[GSM SI3]]** | **[[SIB1]]** | Hücrenin kimlik bilgilerini (LAC/CID vs PLMN/TAC/CellID) ve hücre seçimi sınır güç eşiklerini barındırır. (Bkz: [[GSM SI3]] & [[SIB1]]) |
| **Komşu Hücre Listesi** | **BA (BCCH Allocation) List** | **interFreqCarrierFreqList** | Cihazın bekleme modunda tarayacağı komşu frekans taşıyıcı listesidir. GSM'de bitmap ile iletilirken, LTE'de ASN.1 dizi nesnesi olarak iletilir. |
| **Aynı Teknolojiden Komşu**| **[[GSM SI2]]** | **[[SIB5]]** | Kendi frekans bandındaki veya diğer intra/inter-frequency komşu hücre listelerini taşır. |
| **Ek Genişletilmiş Komşu**| **[[GSM SI2bis]]** | — (LTE içinde dinamik liste) | GSM'de bitmap alanı yetmediği için SI2bis/ter kullanılır. LTE'de dinamik ASN.1 boyutu sayesinde tek bir SIB5 içine tüm frekanslar sığdırılır. |
| **Farklı Teknolojiden Komşu**| **[[GSM SI2quater]]** | **[[SIB6]]** (3G) / **[[SIB7]]** (2G) | Inter-RAT (farklı radyo teknolojileri) komşu listelerini taşır. (Bkz: [[GSM SI2quater]], [[SIB6]], [[SIB7]]) |
| **GPRS / LTE Veri Yapısı**| **[[GSM SI13]]** | **SIB2** | Hücrenin paket veri (GPRS/LTE PS) parametrelerini, ortak kanal sınırlarını ve yönlendirme kurallarını barındırır. |

---

## 2. Analiz Araçları Karşılaştırması

Projemiz kapsamında geliştirilen analiz sistemlerinde kullanılan yazılımların yetenek karşılaştırması:

| Mukayese Alanı | gr-gsm (2G Analiz Aracı) | lte-sib-parser (4G Analiz Aracı) |
| :--- | :--- | :--- |
| **Temel Görevi** | GSM hava arayüzü kontrol kanallarını çözmek ve dinlemek. | LTE SIB paketlerini yakalamak, SQLite'a yazmak ve ayrıştırmak. |
| **Yazılım Mimarisi** | GNU Radio 3.10 pybind11 C++ / Python modülleri. | srsRAN tabanlı, Docker konteyner içinde çalışan sarmalanmış C++ motoru. |
| **Donanım Erişimi** | SoapySDR / gr-osmosdr katmanı (LimeSDR Mini 2.0). | srsRAN UHD / SoapySDR katmanı (LimeSDR Mini 2.0). |
| **Tarama Modu** | `grgsm_scanner` ile aktif BCCH frekanslarını ve komşuları hızlıca listeleme yeteneği. | `sib-scan.sh` ve `cell_search` ile tanımlı EARFCN aralığında hücre arama. |
| **Canlı Yayın Yeteneği** | `grgsm_livemon_headless` ile havadan canlı **[[GSMTAP]]** (UDP 4729) yayını. | `srsue` tabanlı PCAP formatında kablolu/kablosuz paket kaydı imkanı. |
| **Çözümleme Derinliği** | LAPDm katmanından itibaren L3 (RRC) mesajlarını Wireshark/tshark yardımıyla tamamen deşifre edebilir. | ASN.1 formatındaki ham SIB1, SIB3, SIB4, SIB5, SIB6, SIB7 yapılarını doğrudan JSON/SQLite olarak ayrıştırır. |

---

## 3. Girdi ve Çıktı Formatları Karşılaştırması

* **Girdi Parametreleri:**
  * GSM tarafında taranacak hedefler **[[GSM ARFCN]]** kanal numaralarıdır (Örn: `1 - 1023`). Formüller 200 kHz raster genişliğindedir.
  * LTE tarafında taranacak hedefler **[[EARFCN]]** kanal numaralarıdır (Örn: `0 - 262143`). Formüller 100 kHz raster genişliğindedir.
* **Çıktı Formatları:**
  * GSM'de komşu hücreler saf bir ARFCN listesi olarak döner (Örn: `Neighbours: 48, 54, 55...`). Operatör eşleşmeleri frekans tablosundan tahmin edilmek zorundadır.
  * LTE'de komşu hücreler çok daha yapılandırılmış biçimde; EARFCN, hücre önceliği, sinyal eşikleri ve PCI (Physical Cell Identity) filtre aralıklarıyla birlikte raporlanır.

---

## 4. İlgili Bağlantılar
* [[GSM Komsu Analizi]] — GSM tarafındaki komşuluk mekanizması detayları.
* [[Komşu Hücre Analizi]] — LTE ve genel komşu analizi.
* [[gr-gsm]] — 2G analiz aracı.
* [[lte-sib-parser]] — 4G analiz aracı.
* [[GSM Frekans Tablosu]] & [[Frekans Tablosu]] — İki şebekenin frekans lookup kılavuzları.
