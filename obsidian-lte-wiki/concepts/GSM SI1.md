---
title: GSM SI1
source: 3GPP TS 44.018 Section 9.1.31
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 1 (SI1)

**System Information Type 1 (SI1)**, GSM baz istasyonunun (BTS) kapsama alanındaki mobil cihazlara (MS) kendi bünyesinde aktif olarak kullandığı tüm radyo frekans kanallarını (Cell Allocation - Hücre Frekans Tahsisatı) ve RACH (Random Access Channel) erişim parametrelerini iletmek için yayınladığı BCCH mesajıdır.

---

## 1. Ana Parametreler ve Veri Yapısı

SI1 mesajı aşağıdaki kritik alanları içerir:

### A. Hücre Frekans Tahsisatı (Cell Allocation - CA List)
Baz istasyonunun frekans atlama (Frequency Hopping) işlemleri sırasında ve kanalları tahsis ederken kullanabileceği tüm aktif ARFCN kanallarının listesini içeren bitmap yapısıdır. Mobil istasyon, hücresel arayüzde frekans atlamalı bir kanala (`TCH` veya `SDCCH`) atandığında bu listedeki frekans dizilimlerini baz alarak eşleşme gerçekleştirir.

### B. RACH Kontrol Parametreleri (RACH Control Parameters)
Mobil cihazların ağa ilk bağlantıyı başlatmak (Random Access) için kullanacağı parametrelerdir:
* **Max Retrans (Maksimum Yeniden Gönderim):** Cihazın şebekeye erişemediğinde en fazla kaç defa RACH isteği gönderebileceğini belirler (`1`, `2`, `4` veya `8` deneme).
* **Tx-Integer (Gönderim Penceresi):** Çakışmaları önlemek için istekler arasına konulacak rastgele zaman boşluğu (TDMA kare sayısı).
* **CELL_BAR_ACCESS:** `1` ise hücre yeni kullanıcı erişimlerine kapatılır (barlanır).
* **RE (Call Re-establishment):** Şebeke bağlantı kopmalarında cihazın aynı hücrede çağrıyı yeniden kurma yetkisi verip vermediğini tanımlar.

---

## 2. Derleme ve Ingest Mantığı
Dinleme sisteminde, `grgsm_livemon_headless` ile yakalanan paketler [[GSMTAP]] başlığı ile sarmalanır. Tshark veya deşifre yazılımı, paketi çözdüğünde SI1 içerisindeki **Cell Allocation** bitmap alanını ayrıştırarak ilgili hücrenin sahip olduğu tüm aktif taşıyıcı frekansların ARFCN listesini doğrudan listeler.

---

## 3. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information mesaj sistemine genel bakış.
* [[GSM SI2]] — Komşu hücre listelerini taşıyan SI2 yapısı.
* [[GSM ARFCN]] — Frekans dönüştürme ve ARFCN yapısı.
