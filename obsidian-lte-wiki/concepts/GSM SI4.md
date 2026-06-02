---
title: GSM SI4
source: 3GPP TS 44.018 Section 9.1.36
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 4 (SI4)

**System Information Type 4 (SI4)**, GSM baz istasyonunun yayınladığı ve [[GSM SI3]] mesajı ile birlikte hücre seçimi (Cell Selection) parametrelerini tamamlayan, ayrıca hücre içi hücresel yayın kanallarının (**CBCH**) konfigürasyonunu taşıyan BCCH kontrol mesajıdır.

---

## 1. Kritik Parametreler ve CBCH Yapısı

SI4 mesajı içerisinde şu önemli parametre grupları bulunur:

### A. Hücre Yeniden Seçim Ek Parametreleri (Cell Reselection Parameters)
* **CELL_RESELECT_PARAM_IND:** Hücre seçiminde ek parametrelerin (geçici ofsetler vb.) aktif olup olmadığını belirler.
* **TEMPORARY_OFFSET:** Mobil istasyon hücreye yeni bağlandığında, hücreyi ping-pong etkisinden korumak amacıyla kamp kurma formülüne geçici olarak uygulanan yapay sinyal düşürme miktarı (dB).
* **PENALTY_TIME:** Geçici ofset değerinin (TEMPORARY_OFFSET) cihaz kamp kurduktan sonra ne kadar süreyle (saniye) devrede kalacağını belirler.

### B. CBCH Kanal Yapılandırması (Cell Broadcast Channel Configuration)
* CBCH, operatörlerin aynı bölgedeki tüm kullanıcılara acil durum mesajları, konum bilgileri veya kamu duyuruları göndermesini sağlayan ortak hücre yayını kanalıdır.
* SI4 mesajı, CBCH kanalının hangi fiziksel kanaldan ve hangi zaman diliminden (timeslot) yayınlandığına dair yönlendirme parametrelerini (Channel Description) içerir.

---

## 2. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information yapıları.
* [[GSM SI3]] — Hücre seçim ana parametreleri.
* [[GSM Komsu Analizi]] — Hücre yeniden seçimi mantığı.
