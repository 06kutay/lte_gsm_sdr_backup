---
title: GSM SI13
source: 3GPP TS 44.018 Section 9.1.43a
created_date: 2026-06-02
tags:
  - gsm
  - gprs
  - edge
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 13 (SI13)

**System Information Type 13 (SI13)**, GSM baz istasyonunun (BTS) bekleme modundaki mobil cihazlara hücrenin **GPRS** (General Packet Radio Service) ve **EDGE** paket veri yeteneklerini, ağ geçit parametrelerini ve yönlendirme alan kimliğini bildirdiği BCCH mesajıdır.

Hücrenin paket veri (2.5G ve 2.75G) servislerini aktif hale getiren ana parametre bloklarını taşır.

---

## 1. Kritik Parametreler ve GPRS Altyapısı

SI13 mesajı aşağıdaki kritik alanları içerir:

* **GPRS_CELL_OPTIONS:** Hücrenin paket veri iletim kurallarını belirler.
  * **NMO (Network Mode of Operation):** Şebekenin çalışma modudur. Cihazın ses (CS) ve veri (PS) çağrısı kayıtlarını (Location/Routing Area Update) aynı anda mı yoksa ayrı ayrı mı yapacağını belirler (NMO I, II veya III).
  * **T3168 / T3192:** Paket erişim ve sonlandırma işlemlerinde kullanılan zamanlayıcılar (timers).
* **Routing Area Code (RAC):** Hücrenin ait olduğu paket yönlendirme alan kodu (Routing Area ID - RAI'nin bir parçasıdır).
* **SGSN_RELEASE:** Hücrenin bağlı olduğu SGSN (Serving GPRS Support Node) ünitesinin 3GPP sürüm uyumluluğunu gösterir (`Release 99` veya daha yeni).
* **PBCCH (Packet Broadcast Control Channel) Varlığı:** Hücrede GPRS paket kontrol yayın kanalının bulunup bulunmadığını belirtir (Eğer PBCCH yoksa GPRS parametreleri BCCH/SI13 üzerinden okunmaya devam eder).

---

## 2. Ingest ve Sistem İçindeki Önemi
`grgsm_livemon_headless` ile havadan yakalanan paketlerde SI13 çözüldüğünde, hücrenin sadece ses hücresi mi yoksa aktif veri transferine uygun GPRS/EDGE destekli modern bir 2G hücresi mi olduğu tespit edilir. GPRS parametrelerinin eksikliği hücresel erişim kısıtlamalarına neden olabilir.

---

## 3. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information yapıları.
* [[GSM SI3]] — Hücrenin ses (CS) kimliğini (LAC/CID) taşıyan eşdeğer mesaj.
