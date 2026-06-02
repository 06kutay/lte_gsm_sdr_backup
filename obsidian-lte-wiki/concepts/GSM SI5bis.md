---
title: GSM SI5bis
source: 3GPP TS 44.018 Section 9.1.38
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 5bis (SI5bis)

**System Information Type 5bis (SI5bis)**, aktif çağrı durumundaki (**Dedicated Mode**) bir mobil cihaza (MS), baz istasyonu tarafından **SACCH** kanalı üzerinden gönderilen ve [[GSM SI5]] mesajındaki temel BA listesine sığmayan ek **E-GSM** (Extended GSM) komşu frekans kanallarını bildiren mesajdır.

---

## 1. Mimarideki Rolü

Tıpkı bekleme modundaki [[GSM SI2bis]] mesajında olduğu gibi, aktif çağrı durumunda da şebekede E-GSM kanalları ($975 \le n \le 1023$) kullanılıyorsa:
* Temel komşu ARFCN listesi [[GSM SI5]] ile gönderilir.
* SI5 sınırını aşan ek genişletilmiş E-GSM kanalları **SI5bis** üzerinden iletilir.
* Cihaz her iki mesajı birleştirerek el değiştirme (handover) kararı için raporlama yapacağı eksiksiz **BA(SACCH)** listesini oluşturur.

---

## 2. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information yapıları ve SACCH kanalı.
* [[GSM SI5]] — Aktif çağrı modu birincil komşu listesi.
* [[GSM SI5ter]] — Aktif çağrı modu DCS-1800 komşu kanalları.
* [[GSM ARFCN]] — E-GSM ARFCN frekans dönüştürme detayları.
