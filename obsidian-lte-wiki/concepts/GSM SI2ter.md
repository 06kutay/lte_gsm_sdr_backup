---
title: GSM SI2ter
source: 3GPP TS 44.018 Section 9.1.34
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 2ter (SI2ter)

**System Information Type 2ter (SI2ter)**, çoklu frekans bandında (Multi-band) çalışan GSM şebekelerinde, bekleme (idle) modundaki mobil cihazlara (MS) farklı bantlarda yer alan (özellikle **DCS-1800** veya **PCS-1900**) komşu hücre frekans listesini (BA listesi) iletmek amacıyla baz istasyonu tarafından BCCH kanalı üzerinden yayınlanan mesajdır.

---

## 1. Mimarideki Rolü ve Çoklu Bant Geçişi

Bir operatör hem GSM-900 hem de DCS-1800 bantlarında lisansa sahip olduğunda, kapsama alanını ve kapasiteyi optimize etmek için iki bandı birlikte kullanır:
* Cihazlar bekleme modundayken kapsama alanı geniş olan GSM-900 bandına kamp kurma eğilimindedir.
* Ancak yakında daha yüksek kapasiteli bir DCS-1800 hücresi varsa, cihazın o hücreye geçebilmesi (Cell Reselection) gerekir.
* GSM-900 hücresi, kendi BCCH yayınında **SI2ter** mesajını yayınlayarak mobil cihaza çevredeki **DCS-1800 komşu ARFCN kanallarını** ($512 \le n \le 885$) bildirir.

---

## 2. Teknik Kodlama Sınırları
DCS-1800 ARFCN numaraları 512 ile 885 arasındadır ve bu değerler [[GSM SI2]]'nin 128-bit bitmap alanına sığmaz. Bu yüzden SI2ter, DCS-1800 frekanslarını sıkıştırılmış formüller veya özel çoklu frekans listeleri biçiminde taşır.

---

## 3. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information yapıları.
* [[GSM SI2]] — Birincil GSM-900 komşu listesi.
* [[GSM SI2quater]] — Inter-RAT (3G/4G) komşu yayını.
* [[GSM Bandlar]] — Türkiye'deki DCS-1800 operatör frekans aralıkları.
