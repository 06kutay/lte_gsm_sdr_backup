---
title: GSM SI3
source: 3GPP TS 44.018 Section 9.1.35
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 3 (SI3)

**System Information Type 3 (SI3)**, GSM baz istasyonunun (BTS) bekleme modundaki tüm mobil cihazlara (MS) kendi **ağ ve hücre kimliklerini** (PLMN ID, Cell ID, LAC) ve hücre seçimi (Cell Selection) için gereken minimum sinyal sınır parametrelerini bildirdiği BCCH mesajıdır.

LTE şebekesinde hücre kimliği ve kısıtlamalarını taşıyan [[SIB1]] paketinin GSM hava arayüzündeki doğrudan karşılığıdır.

---

## 1. Ağ ve Hücre Kimlik Parametreleri

SI3 mesajı, bir mobil cihazın hangi şebekeye bağlandığını anlamasını sağlayan şu temel kimlik alanlarını taşır:

* **Hücre Kimliği (Cell Identity - CID):** Hücreyi şebeke içinde benzersiz kılan 16-bit tamsayı kimlik değeri.
* **Konum Alan Kodu (Location Area Code - LAC):** Hücrenin ait olduğu çağrı/konum alan kodu (16-bit).
* **MCC (Mobile Country Code):** Ülke kodu (Türkiye için `286`).
* **MNC (Mobile Network Code):** Operatör kodu (`01`: Turkcell, `02`: Vodafone, `03`: Türk Telekom).

---

## 2. Hücre Seçimi (Cell Selection) Parametreleri

Cihazın hücreye kamp kurabilmesi (Cell Selection) için aşması gereken donanımsal ve sinyalsel sınırlar bu mesajla belirlenir:

* **RXLEV-ACCESS-MIN:** Mobil cihazın bu hücreye kamp kurabilmesi için havadan ölçmesi gereken en düşük sinyal alım seviyesidir (dBm cinsinden negatif değer). Sinyal bu değerin altındaysa cihaz hücreyi kapsama dışı sayar.
* **MS-TXPWR-MAX-CCH:** Mobil cihazın ortak kontrol kanallarına (`RACH` gibi) ilk erişim isteği gönderirken kullanabileceği maksimum RF verici çıkış gücüdür (dBm). Cihazın şebekeyi aşırı güçle boğmasını veya pilini hızla tüketmesini önler.
* **CELL-RESELECT-HYSTERESIS (Hücre Yeniden Seçim Histerezisi):** Cihazın komşu bir hücreye geçmeden önce, komşu hücrenin kendi hücre seviyesinden ne kadar daha iyi olması gerektiğini belirleyen dB cinsinden gecikme/histerezis payıdır. Cihazın iki hücre arasında sürekli git-gel yapmasını (ping-pong etkisi) engeller.

---

## 3. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information yapısı.
* [[GSM SI4]] — Hücre seçimini tamamlayan ek blok.
* [[GSM vs LTE Komşu Tespiti]] — LTE SIB1 ile detaylı mimari karşılaştırması.
* [[SIB1]] — LTE hücre kimliği ve sınır yayını.
