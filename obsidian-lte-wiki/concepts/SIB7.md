---
title: SIB7
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - 2g
  - geran
---

# SIB7 (System Information Block Type 7)

**SIB7**, LTE sisteminden **GERAN (GSM EDGE Radio Access Network - 2G)** şebekesine doğru yapılacak olan teknolojik geçişler (Inter-RAT mobility) için gerekli komşu GSM hücre parametrelerini ve hücre yeniden seçim kurallarını taşır.

Özellikle VoLTE (Voice over LTE) kapsama alanının bulunmadığı veya sinyalin çok zayıf olduğu bölgelerde acil durum veya ses aramalarının 2G şebekesine düşürülmesi (**CSFB - Circuit Switched Fallback**) sürecinde yedek ağ planlaması için kullanılır.

---

## 1. Görevi ve GERAN Hücre Yeniden Seçimi

LTE boşta (idle) moddayken, mevcut LTE hücresinin kalitesi aşırı düştüğünde, cihaz daha düşük öncelikli olan GERAN (2G) taşıyıcılarını taramaya başlar. Hangi GSM taşıyıcı frekans gruplarının taranacağı, bunlara ait baz istasyonu kimlik kuralları ve yeniden seçim kriterleri **SIB7** üzerinden cihaza bildirilir.

---

## 2. İçerdiği Kritik Parametreler

SIB7, `carrierFreqsInfoListGERAN` adı verilen bir liste yapısını barındırır. Bu listedeki temel parametreler şunlardır:

- **carrierFreqs (ARFCN Listesi)**: Komşu GERAN (2G) hücrelerinin taşıyıcı frekans numaraları listesi (**ARFCN - Absolute Radio Frequency Channel Number**).
- **commonInfo**: GERAN hücre grubu için ortak olan reselection parametreleridir:
  - **cellReselectionPriority**: GERAN frekans grubunun yeniden seçim öncelik değeridir (0 ile 7 arası). Genellikle 2G önceliği LTE ([[SIB5]]) ve 3G ([[SIB6]]) önceliklerinden çok daha düşük (çoğunlukla `0` veya `1`) tutulur.
  - **ncc-Permitted**: Cihazın hangi **NCC (Network Colour Code)** değerlerine sahip baz istasyonlarını aramasına izin verildiğini belirten bit dizisidir (8-bitlik maske).
- **q-RxLevMin**: 2G hücresine bağlanabilmek için gereken minimum sinyal alım gücü seviyesidir (dBm).
- **threshX-High** / **threshX-Low**: 2G hücresine geçiş için GSM sinyal kalitesinin aşması gereken eşik limitleridir.

---

## 3. Komşu İlişkileri ve CSFB Süreci

- SIB7 2G komşuluklarını yönetirken, 3G komşulukları için [[SIB6]], farklı frekanstaki LTE komşulukları için ise [[SIB5]] mesajları kullanılır.
- **CSFB (Circuit Switched Fallback)** durumunda, cihazda VoLTE aktif değilse veya eNodeB ses çağrısı geldiğinde LTE şebekesinde ses taşıyamıyorsa, cihazı doğrudan 2G (veya 3G) katmanına yönlendirir. SIB7, boşta modda cihazın bu 2G komşuları tanıyabilmesi için tek kaynaktır.
- [[Komşu Hücre Analizi]] sürecinde, tarayıcımız tarafından SQLite veritabanına kaydedilen SIB7 verileri, servis hücresinin 2G şebekesiyle olan komşuluk ve coğrafi yedeklilik ilişkilerini `[[wikilink]]` bağlantıları aracılığıyla haritalandırır.
