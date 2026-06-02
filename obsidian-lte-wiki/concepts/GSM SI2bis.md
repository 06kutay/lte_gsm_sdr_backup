---
title: GSM SI2bis
source: 3GPP TS 44.018 Section 9.1.33
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 2bis (SI2bis)

**System Information Type 2bis (SI2bis)**, baz istasyonunun bekleme (idle) modundaki mobil cihazlara ilettiği komşu hücre listesinin (**BA listesi**) tek bir [[GSM SI2]] paketine sığmadığı durumlarda, özellikle **E-GSM** (Extended GSM) frekans bandı genişletmeleri kullanıldığında yayınlanan ek BCCH mesajıdır.

---

## 1. Neden İhtiyaç Duyulur?

Standart GSM-900 bandında (P-GSM) ARFCN değerleri `1` ile `124` arasındadır ve bu değerler [[GSM SI2]] içerisindeki 128-bit bitmap alanına rahatlıkla sığar. 

Ancak E-GSM genişletme bandı devreye girdiğinde:
1. `975` ile `1023` arasındaki ek ARFCN kanalları da kullanılmaya başlar.
2. Toplam komşu frekans sayısı artar ve tek bir SI2 mesajının 23 byte'lık sınırını aşar.
3. Bu durumda baz istasyonu, P-GSM komşularını SI2 ile yayınlarken, ek genişletilmiş E-GSM komşu ARFCN kanallarını **SI2bis** mesajıyla duyurur.

---

## 2. Ingest ve Kod Çözme (Decoding)
Pasif dinleme sırasında, eğer şebekede E-GSM kanalları komşu olarak tanımlıysa, tshark ve deşifre kütüphaneleri hem SI2 hem de SI2bis paketlerini birleştirerek **bütünleşik bir BA komşu haritası** çıkarır. Sadece SI2 dinlenirse, genişletilmiş bandda çalışan komşu hücreler gözden kaçırılabilir.

---

## 3. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information sistemi.
* [[GSM SI2]] — Birincil bekleme modu komşu listesi.
* [[GSM SI2ter]] — DCS-1800 bandındaki çoklu bant komşuları.
* [[GSM ARFCN]] — E-GSM ARFCN hesaplama kuralları.
