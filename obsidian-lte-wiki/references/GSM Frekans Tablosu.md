---
title: GSM Frekans Tablosu
source: BTK Tahsis Kuralları / 3GPP TS 45.005
created_date: 2026-06-02
tags:
  - gsm
  - rf
  - table
  - reference
---

# GSM ARFCN — Frekans Lookup Tablosu (Türkiye)

Bu referans tablosu, Türkiye'deki GSM-900 ve DCS-1800 şebekelerinde kullanılan kanal numaralarının (**ARFCN**), gerçek downlink taşıyıcı merkez frekanslarının ve bu kanalların tahsis edildiği standart operatörlerin hızlı eşleşmesini sağlar.

---

## 1. GSM-900 Hızlı Lookup Tablosu (Downlink)

GSM-900 bandında kanal aralığı 200 kHz, duplex offset aralığı ise 45 MHz'dir.

| ARFCN | Downlink Frekansı | Standard Operatör Tahsisi | Not / Durum |
| :---: | :---: | :---: | :--- |
| **1** | 935.2 MHz | **Turkcell** | P-GSM-900 Başlangıcı |
| **10** | 937.0 MHz | **Turkcell** | |
| **20** | 939.0 MHz | **Turkcell** | |
| **30** | 941.0 MHz | **Turkcell** | |
| **35** | 942.0 MHz | **Turkcell** | Turkcell Band Sonu |
| **36** | 942.2 MHz | **Vodafone TR** | Vodafone Band Başlangıcı |
| **45** | 944.0 MHz | **Vodafone TR** | |
| **50** | 945.0 MHz | **Vodafone TR** | |
| **60** | 947.0 MHz | **Vodafone TR** | **Faz 1'de Keşfedilen Turkcell Hücresi** (Bkz: [[Cell_GSM_ARFCN60]]) |
| **70** | 949.0 MHz | **Vodafone TR** | Vodafone Band Sonu |
| **71** | 949.2 MHz | **Türk Telekom** | Türk Telekom Band Başlangıcı |
| **80** | 951.0 MHz | **Türk Telekom** | |
| **90** | 953.0 MHz | **Türk Telekom** | |
| **100** | 955.0 MHz | **Türk Telekom** | |
| **105** | 956.0 MHz | **Türk Telekom** | Türk Telekom Band Sonu / P-GSM Sonu |

---

## 2. DCS-1800 Hızlı Lookup Tablosu (Downlink)

DCS-1800 bandında kanal aralığı 200 kHz, duplex offset aralığı 95 MHz'dir.

| ARFCN | Downlink Frekansı | Standard Operatör Tahsisi | Not / Durum |
| :---: | :---: | :---: | :--- |
| **512** | 1805.2 MHz | **Vodafone TR** | DCS-1800 Başlangıcı |
| **550** | 1812.8 MHz | **Vodafone TR** | |
| **586** | 1820.0 MHz | **Vodafone TR** | Vodafone DCS Band Sonu |
| **587** | 1820.2 MHz | **Türk Telekom** | Türk Telekom DCS Band Başlangıcı |
| **620** | 1826.8 MHz | **Türk Telekom** | |
| **661** | 1835.0 MHz | **Türk Telekom** | Türk Telekom DCS Band Sonu |
| **662** | 1835.2 MHz | **Turkcell** | Turkcell DCS Band Başlangıcı |
| **700** | 942.8 MHz / 1842.8 MHz | **Turkcell** | |
| **736** | 1850.0 MHz | **Turkcell** | Turkcell DCS Band Sonu |

---

## 3. Sistem İçi Kullanımı
Bu lookup tablosu, `grgsm_scanner` ve `grgsm_livemon_headless` çıktılarını okuyan parser yazılımları tarafından, yakalanan ham ARFCN değerlerini doğrudan frekansa ve operatör ismine map etmek amacıyla arka plandaki veri sözlüğü olarak kullanılır.

---

## 4. İlgili Bağlantılar
* [[GSM ARFCN]] — Dönüşüm matematiksel formülleri.
* [[GSM Bandlar]] — Spektrum dağılım detayları.
* [[Frekans Tablosu]] — LTE tarafındaki ana frekans tablosu.
* [[Cell_GSM_ARFCN60]] — Canlı taranan hücre raporu.
