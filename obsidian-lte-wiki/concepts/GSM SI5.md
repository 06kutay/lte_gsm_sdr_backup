---
title: GSM SI5
source: 3GPP TS 44.018 Section 9.1.37
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 5 (SI5)

**System Information Type 5 (SI5)**, aktif arama veya veri çağrısı durumundaki (**Dedicated Mode**) bir mobil cihaza (MS), baz istasyonu tarafından **SACCH** (Slow Associated Control Channel) kanalı üzerinden gönderilen ve cihazın el değiştirme (handover) kararı için dinlemesi gereken temel GSM-900 komşu frekans listesini (**BA listesi**) içeren mesajdır.

---

## 1. Dedicated Mod ve SACCH Üzerinden Komşu İletimi

Bir kullanıcı çağrıya başladığında, cihaz bekleme modundaki BCCH kanallarını dinlemeyi bırakır. Görüşme devam ederken arka planda komşu hücrelerin izlenmesi ve en iyi hücreye kesintisiz el değiştirme (handover) yapılması zorunludur:

1. Baz istasyonu, aktif durumdaki cihaza **SACCH** kontrol kanalı vasıtasıyla **SI5** mesajını gönderir.
2. SI5 mesajı, cihazın dinlemesi gereken **BA(SACCH)** komşu ARFCN listesini taşır.
3. Mobil cihaz, bu listedeki frekansların sinyal güçlerini ölçer ve her 480 ms'de bir baz istasyonuna **Ölçüm Raporu (Measurement Report - RXLEV, RXQUAL)** gönderir.
4. Şebeke (BSC/MSC), bu raporlara dayanarak el değiştirme (handover) komutunu tetikler.

---

## 2. SI2 ve SI5 Arasındaki Fark

* **[[GSM SI2]]**: Bekleme modunda cihaz kamp yapacak hücre arasın diye **BCCH** üzerinden tüm şebekeye genel yayınlanır (BA-BCCH listesi).
* **SI5**: Çağrı sırasında cihaz hangi komşuları dinleyip raporlayacağını bilsin diye **SACCH** üzerinden adanmış kanaldan birebir gönderilir (BA-SACCH listesi).

---

## 3. İlgili Bağlantılar
* [[GSM SI Genel]] — BCCH vs SACCH ve Idle vs Dedicated mod kavramları.
* [[GSM SI5bis]] — Dedicated mod ek komşu listesi.
* [[GSM SI5ter]] — Dedicated mod DCS-1800 komşu frekans iletimi.
* [[GSM Komsu Analizi]] — Komşuluk ilişkileri ve izleme mantığı.
