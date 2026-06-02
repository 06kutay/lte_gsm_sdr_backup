---
title: GSM Bandlar
source: BTK Spektrum Tahsis Raporları (Türkiye)
created_date: 2026-06-02
tags:
  - gsm
  - band
  - spectrum
  - turkey
---

# Türkiye'de Kullanılan GSM Bandları ve Operatör Spektrum Dağılımı

Türkiye'deki hücresel ağlarda GSM servisleri iki ana frekans bandında aktif olarak sunulmaktadır: **GSM-900** ve **DCS-1800**. Bilgi Teknolojileri ve İletişim Kurumu (BTK) tarafından üç büyük operatöre (Turkcell, Vodafone TR, Türk Telekom) tahsis edilen ARFCN kanal ve spektrum sınırları aşağıda detaylandırılmıştır.

---

## 1. GSM-900 Bandı Dağılımı

GSM-900 bandı, geniş kapsama alanı (coverage) avantajı nedeniyle kırsal bölgelerde ve bina içi sızma sinyallerinde ana taşıyıcı bant olarak rol oynar. Standart kanal aralığı 200 kHz olup, operatörlerin ARFCN tahsisatları şu şekildedir:

| Operatör | MCC / MNC | ARFCN Kanal Aralığı | Frekans Aralığı (Downlink) | Genişlik |
| :--- | :---: | :---: | :---: | :---: |
| **Turkcell** | 286 / 01 | `1 - 35` | 935.2 MHz - 942.0 MHz | 7.0 MHz |
| **Vodafone TR** | 286 / 02 | `36 - 70` | 942.2 MHz - 949.0 MHz | 7.0 MHz |
| **Türk Telekom** | 286 / 03 | `71 - 105` | 949.2 MHz - 956.0 MHz | 7.0 MHz |

> [!NOTE]
> * Faz 1 doğrulamaları sırasında **ARFCN 60 (947.0 MHz)** kanalında çalışan ve Turkcell MNC (`01`) değerini bildiren aktif bir hücre tespit edilmiştir. 
> * Bu durum, normal BTK spektrum haritasında ARFCN 60'ın Vodafone'a ait olmasına rağmen, **yerel test şebekelerinde** veya laboratuvar test istasyonlarında esnek spektrum lisanslaması/frekans kaydırması yapıldığını göstermektedir.

---

## 2. DCS-1800 Bandı (GSM-1800) Dağılımı

DCS-1800 bandı, daha yüksek frekansı nedeniyle kapsama alanının dar ama kapasitenin yüksek olduğu şehir merkezlerinde ve yoğun nüfuslu bölgelerde ek kapasite (capacity) sağlamak üzere konumlandırılmıştır.

| Operatör | MCC / MNC | ARFCN Kanal Aralığı | Frekans Aralığı (Downlink) | Genişlik |
| :--- | :---: | :---: | :---: | :---: |
| **Vodafone TR** | 286 / 02 | `512 - 586` | 1805.2 MHz - 1820.0 MHz | 15.0 MHz |
| **Türk Telekom** | 286 / 03 | `587 - 661` | 1820.2 MHz - 1835.0 MHz | 15.0 MHz |
| **Turkcell** | 286 / 01 | `662 - 736` | 1835.2 MHz - 1850.0 MHz | 15.0 MHz |

---

## 3. Komşu Hücre Aramalarındaki Önemi
Taramalar sırasında, `grgsm_scanner` ve `grgsm_livemon_headless` araçlarına anten ayarı yapılırken:
* **GSM-900** taranıyorsa sinyaller $< 1.5$ GHz olduğu için LimeSDR Mini üzerindeki **`LNAW`** (Low/Wide Band) anten portu seçilmelidir.
* **DCS-1800** taranıyorsa sinyaller $\ge 1.5$ GHz olduğu için **`LNAH`** (High Band) anten portu seçilmelidir.

---

## 4. İlgili Bağlantılar
* [[GSM ARFCN]] — Frekans formülleri ve hesaplama detayları.
* [[GSM Frekans Tablosu]] — Operatör-ARFCN hızlı lookup tablosu.
* [[LTE Bandlar]] — LTE tarafındaki bant ve spektrum paylaşımları.
* [[Cell_GSM_ARFCN60]] — Gerçek Turkcell ARFCN 60 hücre raporu.
