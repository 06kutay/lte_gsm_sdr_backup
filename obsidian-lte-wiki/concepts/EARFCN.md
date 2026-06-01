---
title: EARFCN
source: 3GPP TS 36.101
created_date: 2026-06-01
tags:
  - lte
  - rf
  - radio
  - mathematical
---

# EARFCN (E-UTRA Absolute Radio Frequency Channel Number)

**EARFCN**, LTE (E-UTRA) sistemlerinde downlink ve uplink taşıyıcı frekanslarını (carrier frequency) benzersiz şekilde tanımlamak için kullanılan mutlak radyo frekans kanal numarasıdır.

LTE, frekans kanallarını MHz bazında doğrudan belirtmek yerine, 100 kHz (0.1 MHz) kanal rasterı (raster spacing) kullanan bu tamsayı indeksleme yöntemini tercih eder.

---

## 1. EARFCN Hesaplama Formülleri

3GPP TS 36.101 standardına göre, EARFCN ($N_{DL}$ veya $N_{UL}$) ile gerçek taşıyıcı frekansı ($F_{DL}$ veya $F_{UL}$, MHz cinsinden) arasındaki dönüşüm aşağıdaki matematiksel formüllerle gerçekleştirilir:

### A. Downlink (İndirme) Frekansı Hesaplama
Frekansı bilinen bir kanalın EARFCN ($N_{DL}$) değerini bulmak için:
$$N_{DL} = N_{Offs\text{-}DL} + 10 \times (F_{DL} - F_{DL\_low})$$

EARFCN ($N_{DL}$) değeri bilinen bir kanalın merkez frekansını ($F_{DL}$) bulmak için:
$$F_{DL} = F_{DL\_low} + 0.1 \times (N_{DL} - N_{Offs\text{-}DL})$$

### B. Uplink (Yükleme) Frekansı Hesaplama
Frekansı bilinen bir kanalın EARFCN ($N_{UL}$) değerini bulmak için:
$$N_{UL} = N_{Offs\text{-}UL} + 10 \times (F_{UL} - F_{UL\_low})$$

EARFCN ($N_{UL}$) değeri bilinen bir kanalın merkez frekansını ($F_{UL}$) bulmak için:
$$F_{UL} = F_{UL\_low} + 0.1 \times (N_{UL} - N_{Offs\text{-}UL})$$

---

## 2. Formül Parametrelerinin Açıklamaları

- **$N_{DL} / N_{UL}$**: Çözümlenmek istenen Downlink veya Uplink EARFCN kanalı (Tamsayı).
- **$F_{DL} / F_{UL}$**: MHz cinsinden gerçek radyo frekansı (Ondalıklı sayı, örn: 1842.5 MHz).
- **$F_{DL\_low} / F_{UL\_low}$**: İlgili LTE bandının tanımlanmış en düşük downlink/uplink frekans sınırıdır (3GPP Tablosundan alınır).
- **$N_{Offs\text{-}DL} / N_{Offs\text{-}UL}$**: İlgili LTE bandı için belirlenmiş olan kanal numarası başlangıç offset değeridir (3GPP Tablosundan alınır).

---

## 3. Türkiye Operatörlerinin Kullandığı Temel Band Parametreleri

Türkiye'deki operatörler (Turkcell, Vodafone, Türk Telekom) tarafından kullanılan en yaygın bandların parametre tablosu aşağıdadır (Daha geniş detaylar için [[LTE Bandlar]] ve [[Frekans Tablosu]] sayfalarına bakabilirsiniz):

| LTE Bandı | Frekans İsmi | $F_{DL\_low}$ (MHz) | $N_{Offs\text{-}DL}$ | EARFCN Aralığı (Downlink) |
| :---: | :--- | :---: | :---: | :--- |
| **Band 1** | 2100 MHz | 2110 | 0 | 0 - 599 |
| **Band 3** | 1800 MHz | 1805 | 1200 | 1200 - 1949 |
| **Band 7** | 2600 MHz | 2620 | 2750 | 2750 - 3449 |
| **Band 8** | 900 MHz | 925 | 3450 | 3450 - 3799 |
| **Band 20** | 800 MHz | 791 | 6150 | 6150 - 6449 |

---

## 4. Örnek Hesaplamalar

### Örnek 1: EARFCN'den Frekans Bulma (Band 3 Downlink)
Elimizde EARFCN **1675** değeri var. Bunun Downlink merkez frekansını bulalım:
1.  Band 3 için tablodan değerleri alıyoruz: $F_{DL\_low} = 1805$ MHz, $N_{Offs\text{-}DL} = 1200$.
2.  Formülü uyguluyoruz:
    $$F_{DL} = 1805 + 0.1 \times (1675 - 1200)$$
    $$F_{DL} = 1805 + 0.1 \times 475$$
    $$F_{DL} = 1805 + 47.5 = \mathbf{1852.5\text{ MHz}}$$
3.  *Sonuç*: EARFCN 1675, merkez frekansı 1852.5 MHz olan Band 3 downlink taşıyıcısıdır.

### Örnek 2: Frekanstan EARFCN Bulma (Band 20 Downlink)
Mevcut bir operatörün Band 20 downlink merkez frekansı **806.0 MHz** olarak ölçüldü. Bu frekansın EARFCN değerini bulalım:
1.  Band 20 için değerler: $F_{DL\_low} = 791$ MHz, $N_{Offs\text{-}DL} = 6150$.
2.  Formülü uyguluyoruz:
    $$N_{DL} = 6150 + 10 \times (806.0 - 791)$$
    $$N_{DL} = 6150 + 10 \times 15.0$$
    $$N_{DL} = 6150 + 150 = \mathbf{6300}$$
3.  *Sonuç*: 806.0 MHz downlink frekansının EARFCN karşılığı 6300'dür.

---

## 5. Projedeki Rolü

[[sib-scan.sh]] tarama aracı, taranacak kanalları doğrudan EARFCN cinsinden girdi olarak alır (örn: `-q "1675 6300"`). Script içerisindeki Python yardımcı araçları (`earfcn_to_band.py` ve `band_to_earfcn.py`), havadan gelen ham EARFCN değerlerini analiz edip ilgili frekans bandı ile eşleştirerek [[lte-sib-parser]] içindeki `cell_search` ve `srsue` modüllerine doğru parametrelerin gitmesini sağlar.
