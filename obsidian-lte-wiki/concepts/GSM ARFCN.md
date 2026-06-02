---
title: GSM ARFCN
source: 3GPP TS 45.005
created_date: 2026-06-02
tags:
  - gsm
  - rf
  - radio
  - mathematical
---

# GSM ARFCN (Absolute Radio Frequency Channel Number)

**ARFCN**, GSM hücresel şebekelerinde havadan iletilen downlink (indirme) ve uplink (yükleme) radyo kanallarını ve bunların merkez frekanslarını benzersiz şekilde tanımlayan mutlak radyo frekansı kanal numarasıdır.

GSM sistemi, frekans kanallarını doğrudan MHz cinsinden belirtmek yerine, **200 kHz (0.2 MHz)** düzeyindeki kanal aralığını (channel spacing) ve kanal rasterını temel alan bu tam sayı dizilim indeksleme yöntemini kullanır.

---

## 1. GSM ARFCN Matematiksel Formülleri

3GPP TS 45.005 standardına göre, tanımlı farklı GSM bantlarındaki ARFCN ($n$) kanal değeri ile gerçek taşıyıcı merkez frekansı ($F_{DL}$ ve $F_{UL}$, MHz cinsinden) arasındaki dönüşümler aşağıdaki formüllerle gerçekleştirilir:

### 1.1 GSM-900 Bandı (P-GSM & E-GSM)
* **P-GSM (Primary GSM-900):** $1 \le n \le 124$ (Duplex Aralığı / Offset: 45 MHz)
  * Downlink Frekansı: $F_{DL}(n) = 935.0 + 0.2 \times n$
  * Uplink Frekansı: $F_{UL}(n) = 890.0 + 0.2 \times n$
* **E-GSM (Extended GSM-900):** $0 \le n \le 124$ veya $975 \le n \le 1023$
  * $0 \le n \le 124$:
    * Downlink: $F_{DL}(n) = 935.0 + 0.2 \times n$
    * Uplink: $F_{UL}(n) = 890.0 + 0.2 \times n$
  * $975 \le n \le 1023$ (Sanal Offset: $n - 1024$ uygulanır):
    * Downlink: $F_{DL}(n) = 935.0 + 0.2 \times (n - 1024)$
    * Uplink: $F_{UL}(n) = 890.0 + 0.2 \times (n - 1024)$

### 1.2 DCS-1800 Bandı (GSM-1800)
* Kanal Aralığı: $512 \le n \le 885$ (Duplex Aralığı / Offset: 95 MHz)
  * Downlink Frekansı: $F_{DL}(n) = 1805.2 + 0.2 \times (n - 512)$
  * Uplink Frekansı: $F_{UL}(n) = 1710.2 + 0.2 \times (n - 512)$

### 1.3 GSM-850 Bandı
* Kanal Aralığı: $128 \le n \le 251$ (Duplex Aralığı / Offset: 45 MHz)
  * Downlink Frekansı: $F_{DL}(n) = 869.2 + 0.2 \times (n - 128)$
  * Uplink Frekansı: $F_{UL}(n) = 824.2 + 0.2 \times (n - 128)$

### 1.4 PCS-1900 Bandı (GSM-1900)
* Kanal Aralığı: $512 \le n \le 810$ (Duplex Aralığı / Offset: 80 MHz)
  * Downlink Frekansı: $F_{DL}(n) = 1930.2 + 0.2 \times (n - 512)$
  * Uplink Frekansı: $F_{UL}(n) = 1850.2 + 0.2 \times (n - 512)$

---

## 2. Örnek Hesaplamalar

### Örnek 1: ARFCN'den Downlink Frekansı Bulma (GSM-900)
Elimizde ARFCN **60** değeri var. Bunun Downlink merkez frekansını hesaplayalım:
1.  Kanal numarası $1 \le 60 \le 124$ aralığında olduğu için P-GSM formülünü kullanırız.
2.  Formülü uyguluyoruz:
    $$F_{DL} = 935.0 + 0.2 \times 60$$
    $$F_{DL} = 935.0 + 12.0 = \mathbf{947.0\text{ MHz}}$$
3.  *Sonuç*: ARFCN 60, merkez frekansı 947.0 MHz olan bir downlink taşıyıcı kanalıdır (Faz 1'de keşfedilen Turkcell hücresi).

### Örnek 2: Frekanstan ARFCN Bulma (DCS-1800)
Ölçülen bir baz istasyonunun downlink frekansı **1820.0 MHz** düzeyindedir. Bunun DCS-1800 ARFCN değerini bulalım:
1.  Frekans DCS-1800 downlink aralığında ($1805.2 \le 1820.0 \le 1880.0$) olduğu için DCS-1800 formülünü tersten işletiriz:
    $$F_{DL} = 1805.2 + 0.2 \times (n - 512)$$
    $$1820.0 = 1805.2 + 0.2 \times (n - 512)$$
    $$14.8 = 0.2 \times (n - 512)$$
    $$74 = n - 512$$
    $$n = 74 + 512 = \mathbf{586}$$
2.  *Sonuç*: 1820.0 MHz downlink frekansının DCS-1800 bandındaki ARFCN karşılığı 586'dır.

---

## 3. İlgili Bağlantılar
* [[GSM Bandlar]] — Türkiye spektrum atamaları ve operatör ARFCN sınırları.
* [[GSM Frekans Tablosu]] — Detaylı ARFCN ve frekans karşılıkları hızlı lookup listesi.
* [[EARFCN]] — LTE bandındaki eşdeğer kanal yapısı.
* [[UARFCN]] — 3G bandındaki eşdeğer kanal yapısı.
