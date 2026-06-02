---
title: Frekans Tablosu
source: BTK Spektrum Raporları, 3GPP TS 36.101
created_date: 2026-06-01
tags:
  - reference
  - rf
  - table
  - frequency
---

# LTE Frekans ve EARFCN Referans Tablosu

Bu sayfa, Türkiye mobil şebekelerinde aktif olarak kullanılan LTE bandları ile LimeSDR Mini 2.0 donanım limitleri nedeniyle taranamayan veya sınırda kalan bandların kapsamlı referans tablosudur.

LimeSDR Mini 2.0 alıcı frekans limiti **10 MHz – 3.5 GHz** arasındadır. Bu aralığın dışındaki bandlar **taranamayan band** olarak sınıflandırılmıştır.

---

## 1. Genel Frekans Referans Tablosu

Aşağıdaki tabloda Türkiye'deki operatör dağılımları ve LimeSDR Mini 2.0 donanım uyumluluğu belirtilmiştir. 

> [!WARNING]
> Kırmızı renkle işaretlenmiş olan bandlar **bu donanımla taranamaz** veya donanım limitleri/ülke spektrum planları nedeniyle kapsam dışıdır.

| LTE Bandı | Frekans Adı | Downlink Frekans Aralığı | Downlink EARFCN Aralığı | Operatör Dağılımı (TR) | LimeSDR Mini 2.0 Uyumluluk Durumu |
| :---: | :---: | :---: | :---: | :---: | :--- |
| **Band 20** | 800 MHz | 791.0 – 821.0 MHz | 6150 – 6449 | Turkcell / Vodafone / Türk Telekom | <span style="color: #2ec4b6; font-weight: bold;">✓ TAM UYUMLU</span> (LNAW Anten) |
| **Band 8** | 900 MHz | 925.0 – 935.0 MHz | 3450 – 3799 | Turkcell / Vodafone / Türk Telekom | <span style="color: #2ec4b6; font-weight: bold;">✓ TAM UYUMLU</span> (LNAW/LNAH Anten) |
| **Band 3** | 1800 MHz | 1805.0 – 1880.0 MHz | 1200 – 1949 | Turkcell / Vodafone / Türk Telekom | <span style="color: #2ec4b6; font-weight: bold;">✓ TAM UYUMLU</span> (LNAH Anten) |
| **Band 1** | 2100 MHz | 2110.0 – 2170.0 MHz | 0 – 599 | Turkcell / Vodafone / Türk Telekom | <span style="color: #2ec4b6; font-weight: bold;">✓ TAM UYUMLU</span> (LNAH Anten) |
| **Band 7** | 2600 MHz | 2620.0 – 2690.0 MHz | 2750 – 3449 | Turkcell / Vodafone / Türk Telekom | <span style="color: #2ec4b6; font-weight: bold;">✓ TAM UYUMLU</span> (LNAH Anten) |
| <span style="color: #ff4d4d;">**Band 28**</span> | <span style="color: #ff4d4d;">700 MHz</span> | <span style="color: #ff4d4d;">758.0 – 803.0 MHz</span> | <span style="color: #ff4d4d;">9210 – 9659</span> | <span style="color: #ff4d4d;">Türkiye'de Kullanılmıyor</span> | <span style="color: #ff4d4d; font-weight: bold;">✗ BU DONANIMLA TARANAMAZ</span> (700 MHz altı/donanım limit dışı) |
| <span style="color: #ff4d4d;">**Band 31**</span> | <span style="color: #ff4d4d;">450 MHz</span> | <span style="color: #ff4d4d;">462.5 – 467.5 MHz</span> | <span style="color: #ff4d4d;">9870 – 9919</span> | <span style="color: #ff4d4d;">Türkiye'de Kullanılmıyor</span> | <span style="color: #ff4d4d; font-weight: bold;">✗ BU DONANIMLA TARANAMAZ</span> (450 MHz limit dışı) |
| <span style="color: #ff4d4d;">**Band 42**</span> | <span style="color: #ff4d4d;">3.5 GHz</span> | <span style="color: #ff4d4d;">3400.0 – 3600.0 MHz</span> | <span style="color: #ff4d4d;">41590 – 43589</span> | <span style="color: #ff4d4d;">Türkiye'de Kullanılmıyor (5G Test)</span> | <span style="color: #ff4d4d; font-weight: bold;">✗ BU DONANIMLA TARANAMAZ</span> (3.5 GHz üstü limit dışı) |
| <span style="color: #ff4d4d;">**Band 43**</span> | <span style="color: #ff4d4d;">3.7 GHz</span> | <span style="color: #ff4d4d;">3600.0 – 3800.0 MHz</span> | <span style="color: #ff4d4d;">43590 – 45589</span> | <span style="color: #ff4d4d;">Türkiye'de Kullanılmıyor</span> | <span style="color: #ff4d4d; font-weight: bold;">✗ BU DONANIMLA TARANAMAZ</span> (3.5 GHz üstü limit dışı) |
| <span style="color: #ff4d4d;">**Band 48**</span> | <span style="color: #ff4d4d;">CBRS</span> | <span style="color: #ff4d4d;">3550.0 – 3700.0 MHz</span> | <span style="color: #ff4d4d;">55240 – 56739</span> | <span style="color: #ff4d4d;">Türkiye'de Kullanılmıyor</span> | <span style="color: #ff4d4d; font-weight: bold;">✗ BU DONANIMLA TARANAMAZ</span> (3.5 GHz üstü limit dışı) |

---

## 2. Operatör Bazlı Detaylı Frekans ve Kanal Tablosu (TR)

Türkiye'de aktif taranan FDD bandlarındaki operatör alt kanalları ve merkez EARFCN değerleri:

### Band 3 (1800 MHz - Ana Kapasite Katmanı)
- **Turkcell DL**: 1815.0 - 1844.8 MHz | Merkez EARFCN: `1350` (20 MHz BW) veya `1400`
- **Vodafone DL**: 1844.8 - 1857.2 MHz | Merkez EARFCN: `1600` (10 MHz BW)
- **Türk Telekom DL**: 1857.2 - 1880.0 MHz | Merkez EARFCN: `1775` (20 MHz BW)

### Band 20 (800 MHz - Ana Kapsama Katmanı)
- **Türk Telekom DL**: 791.0 – 801.0 MHz | Merkez EARFCN: `6200` (10 MHz BW)
- **Vodafone DL**: 801.0 – 811.0 MHz | Merkez EARFCN: `6300` (10 MHz BW)
- **Turkcell DL**: 811.0 – 821.0 MHz | Merkez EARFCN: `6400` (10 MHz BW)

### Band 7 (2600 MHz - Ultra Kapasite Katmanı)
- **Vodafone DL**: 2620.0 - 2635.0 MHz | Merkez EARFCN: `2825` (15 MHz BW)
- **Türk Telekom DL**: 2635.0 - 2655.0 MHz | Merkez EARFCN: `3000` (20 MHz BW)
- **Turkcell DL**: 2655.0 - 2680.0 MHz | Merkez EARFCN: `3200` (20 MHz BW)

---

## 3. Matematiksel Dönüşüm ve Doğrulama

Radyo taramasında herhangi bir hücre yakalandığında, [[EARFCN]] sayfasındaki matematiksel formüller kullanılarak Downlink merkez frekansı doğrulanır.
- Örneğin, `sib-scan.sh` çalışırken veritabanına `6300` EARFCN kaydedilirse:
  $$F_{DL} = 791.0 + 0.1 \times (6300 - 6150) = 806.0\text{ MHz}$$
  Bu frekans tablomuzdan doğrulanarak **Vodafone Band 20** olarak etiketlenir.
- Detaylı komşuluk ve reselection öncelikleri analizleri için [[Komşu Hücre Analizi]] ve [[Sistem Mimarisi]] sayfalarına bakabilirsiniz.

---

## 4. GSM Frekans Dağılımı ve Lookup Listesi

2G (GSM-900 ve DCS-1800) şebekelerinde kullanılan ARFCN kanal numaraları, downlink frekansları ve operatör spektrum sınırlarının lookup tabloları için **[[GSM Frekans Tablosu]]** sayfasına bakabilirsiniz.

