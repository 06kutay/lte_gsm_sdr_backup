---
title: GSM SI5ter
source: 3GPP TS 44.018 Section 9.1.39
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 5ter (SI5ter)

**System Information Type 5ter (SI5ter)**, çoklu frekans bandında (GSM-900 + DCS-1800) çalışan şebekelerde, aktif bir çağrı durumundaki (**Dedicated Mode**) mobil cihaza, el değiştirme (handover) yapabileceği farklı bantlardaki (özellikle **DCS-1800** veya **PCS-1900**) komşu hücre listesini iletmek üzere **SACCH** kanalı üzerinden gönderilen mesajdır.

---

## 1. Mimarideki Rolü ve Handover Süreci

Aktif görüşme sırasında şebekenin yük dağılımını optimize etmek veya kapsama alanını genişletmek amacıyla bantlar arası geçişler (Inter-band Handover) sıkça kullanılır:
* Cihaz GSM-900 bandında konuşurken, baz istasyonu **SACCH** üzerinden **SI5ter** paketlerini gönderir.
* SI5ter içindeki **DCS-1800 komşu ARFCN listesi** ($512 \le n \le 885$) çözülerek cihaz tarafından izlenir.
* Cihaz bu DCS-1800 frekanslarının sinyal kalitesini ölçerek baz istasyonuna raporlar.
* Sinyal kalitesi yeterli seviyedeyse görüşme kesilmeden cihaz DCS-1800 hücresine aktarılır (GSM900 -> DCS1800 Handover).

---

## 2. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information ve dedicated mod kavramları.
* [[GSM SI5]] — Aktif mod temel GSM-900 komşu listesi.
* [[GSM SI2ter]] — Bekleme (idle) modundaki DCS-1800 komşu listesi karşılığı.
* [[GSM Bandlar]] — Operatörlerin Türkiye'deki DCS-1800 tahsisat sınırları.
