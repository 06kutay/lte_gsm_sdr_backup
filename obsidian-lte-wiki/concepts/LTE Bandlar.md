---
title: LTE Bandlar
source: BTK, 3GPP TS 36.101
created_date: 2026-06-01
tags:
  - lte
  - rf
  - turkey
  - regulations
---

# Türkiye'de Kullanılan LTE Bandları ve Operatör Dağılımları

Türkiye mobil haberleşme pazarında faaliyet gösteren üç büyük operatör (**Turkcell, Vodafone, Türk Telekom**), Bilgi Teknolojileri ve İletişim Kurumu (BTK) tarafından yetkilendirildikleri spektrum sınırları dahilinde LTE hizmeti sunmaktadır. Türkiye'de LTE (4.5G) servisleri temel olarak **FDD (Frequency Division Duplex)** yapısında çalışmaktadır.

Radyo taramaları sırasında en çok karşılaştığımız ve [[Sistem Mimarisi]] kapsamında [[lte-sib-parser]] ile çözümlediğimiz 5 temel LTE bandı şunlardır:

---

## 1. Kullanılan Temel LTE Bandları

### A. Band 3 (1800 MHz - FDD)
- **Frekans Aralığı**: UL: 1710–1785 MHz | DL: 1805–1880 MHz
- **Karakteristik**: Yüksek veri kapasitesi ve makul kapsama alanının bir arada sunulduğu, Türkiye'deki en yaygın taşıyıcı banddır. Operatörler bu bandda genellikle 20 MHz genişliğinde geniş kanallar (Carrier Aggregation ana bandı olarak) kullanırlar.
- **EARFCN Aralığı**: 1200 - 1949

### B. Band 20 (800 MHz - FDD)
- **Frekans Aralığı**: UL: 832–862 MHz | DL: 791–821 MHz
- **Karakteristik**: Düşük frekans avantajı sayesinde mükemmel kapsama alanı ve yüksek bina içi penetrasyon sağlar. Genellikle kırsal alanlarda ana şebeke, şehir içlerinde ise derin bina içi kapsama katmanı olarak kullanılır. Genişliği 10 MHz ile sınırlıdır.
- **EARFCN Aralığı**: 6150 - 6449

### C. Band 1 (2100 MHz - FDD)
- **Frekans Aralığı**: UL: 1920–1980 MHz | DL: 2110–2170 MHz
- **Karakteristik**: Geçmişte 3G (UMTS) için tahsis edilen bu band, günümüzde hızla LTE şebekelerine refarm (yeniden tahsis) edilmektedir. Orta-yüksek kapasite katmanı olarak kullanılır.
- **EARFCN Aralığı**: 0 - 599

### D. Band 7 (2600 MHz - FDD)
- **Frekans Aralığı**: UL: 2500–2570 MHz | DL: 2620–2690 MHz
- **Karakteristik**: Çok yüksek veri hızları ve kapasite sunar. Ancak yüksek frekans nedeniyle kapsama alanı dar ve bina içi penetrasyonu zayıftır. Yoğun şehir merkezleri, stadyumlar, AVM'ler gibi yoğun insan trafiğinin olduğu yerlerde ek kapasite (capacity booster) olarak konumlandırılır.
- **EARFCN Aralığı**: 2750 - 3449

### E. Band 8 (900 MHz - FDD)
- **Frekans Aralığı**: UL: 880–890 MHz | DL: 925–935 MHz (BTK tahsis sınırları)
- **Karakteristik**: Başlangıçta 2G (GSM 900) için kullanılan bu frekanslar, özellikle Vodafone ve Turkcell tarafından kısmen LTE 900 şebekesine dönüştürülmüştür. Düşük frekanslı ek bir kapsama katmanı sunar.
- **EARFCN Aralığı**: 3450 - 3799

---

## 2. Operatör Spektrum Dağılım Özeti (BTK 2015 İhalesi Sonrası)

Türkiye'de operatörlerin LTE bandlarındaki spektrum genişlikleri (MHz cinsinden FDD çift yönlü kanal genişlikleri) yaklaşık olarak şöyledir:

1.  **Turkcell**:
    - Band 3 (1800 MHz): 29.8 MHz FDD (Geniş spektrum avantajıyla CA lideri)
    - Band 7 (2600 MHz): 25 MHz FDD (+ 10 MHz TDD)
    - Band 1 (2100 MHz): 19.8 MHz FDD (Kısmen LTE'ye refarm edildi)
    - Band 8 (900 MHz): 15 MHz FDD (Kısmen LTE refarm)
    - Band 20 (800 MHz): 10 MHz FDD (Kapsama katmanı)

2.  **Vodafone**:
    - Band 3 (1800 MHz): 12.4 MHz FDD
    - Band 7 (2600 MHz): 15 MHz FDD (+ 10 MHz TDD)
    - Band 1 (2100 MHz): 15 MHz FDD (Kısmen LTE)
    - Band 8 (900 MHz): 12.4 MHz FDD (Geniş bir kısmı LTE 900 için kullanılır)
    - Band 20 (800 MHz): 10 MHz FDD (Kapsama katmanı)

3.  **Türk Telekom**:
    - Band 3 (1800 MHz): 32.8 MHz FDD (En geniş Band 3 spektrumu)
    - Band 7 (2600 MHz): 20 MHz FDD
    - Band 1 (2100 MHz): 15 MHz FDD (Kısmen LTE)
    - Band 8 (900 MHz): 10 MHz FDD (Sadece belirli bölgelerde LTE 900)
    - Band 20 (800 MHz): 10 MHz FDD (Kapsama katmanı)

---

## 3. Komşu Analizi ve Ağ Stratejileri

Operatörler, [[SIB3]] ve [[SIB5]] reselection öncelik ayarları vasıtasıyla cihazları bu bandlar arasında dinamik olarak yönlendirirler:
- Cihaz sinyali iyi olduğu sürece önceliği yüksek olan Band 7 (2600 MHz) veya Band 3 (1800 MHz) kapasite katmanlarında tutulur.
- Sinyal zayıfladığında cihaz otomatik olarak Band 20 (800 MHz) veya Band 8 (900 MHz) kapsama katmanına kaydırılır (cell reselection).
- Bu geçiş eşikleri ve öncelikleri [[Komşu Hücre Analizi]] sayfasında detaylandırılmıştır.
- Tüm bu bantların somut EARFCN aralıkları ve Downlink merkez frekansları için [[Frekans Tablosu]] referans dökümanına başvurabilirsiniz.
