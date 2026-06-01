---
title: SIB6
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - 3g
  - utran
---

# SIB6 (System Information Block Type 6)

**SIB6**, LTE sisteminden **UTRAN (Universal Terrestrial Radio Access Network - 3G/WCDMA)** sistemine doğru yapılacak olan teknolojik geçişler (Inter-RAT - Radio Access Technology mobility) için gerekli komşu hücre parametrelerini taşır. 

Cihazın (UE) kapsama alanı zayıfladığında veya operatörün ses/veri yönlendirme stratejilerine göre 3G şebekesine geçiş kurallarını tanımlar.

---

## 1. Görevi ve Inter-RAT Hücre Yeniden Seçimi

LTE boşta (idle) moddayken, cihaz mevcut LTE hücresinin kalitesi [[SIB3]] içindeki `threshServingLow` sınırının altına indiğinde, daha düşük öncelikli olan UTRAN (3G) frekanslarını ölçmeye ve aramaya başlar. 
- Hangi 3G taşıyıcı frekanslarının ([[UARFCN]]) taranacağı ve bunlara ait parametreler **SIB6** üzerinden cihaza bildirilir.

---

## 2. İçerdiği Kritik Parametreler

SIB6, `carrierFreqListUTRA-FDD` (veya TDD şebekeleri için UTRA-TDD) listesini barındırır. Her bir UTRA taşıyıcı frekansı için tanımlanan parametreler şunlardır:

- **carrierFreq (UARFCN)**: Komşu UTRAN (3G) hücresinin Downlink taşıyıcı frekans kanal numarası (**UARFCN - UTRA Absolute Radio Frequency Channel Number**).
- **cellReselectionPriority**: UTRAN frekansının reselection öncelik değeridir (0 ile 7 arası). LTE operatörleri genellikle 3G frekans önceliklerini LTE frekanslarından ([[SIB5]]) daha düşük tutarak cihazların öncelikle LTE'de kalmasını sağlarlar.
- **q-RxLevMin**: 3G hücresine bağlanabilmek için gereken minimum CPICH RSCP (Received Signal Code Power) seviyesidir (dBm cinsinden).
- **threshX-High** / **threshX-Low**: LTE'den bu 3G frekansına geçebilmek için 3G sinyal gücünün aşması gereken reselection eşik sınırlarıdır.

---

## 3. Komşu İlişkileri

- SIB6 inter-RAT 3G komşuluklarını yönetirken, inter-RAT 2G (GSM) komşulukları için [[SIB7]], farklı frekanstaki LTE komşulukları için ise [[SIB5]] mesajları kullanılır.
- [[Komşu Hücre Analizi]] sürecinde, tarayıcımız tarafından SQLite veritabanına kaydedilen SIB6 parametreleri, LTE hücresinin 3G yedeklilik (fallback) planını anlamamızı sağlar.
- [[Sistem Mimarisi]] kapsamında, çözümlenen UARFCN değerleri komşu teknolojilerle `[[wikilink]]` bağlantısı kurularak haritalandırılır.
