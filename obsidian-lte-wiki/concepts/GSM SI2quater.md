---
title: GSM SI2quater
source: 3GPP TS 44.018 Section 9.1.34a
created_date: 2026-06-02
tags:
  - gsm
  - lte
  - inter-rat
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 2quater (SI2quater)

**System Information Type 2quater (SI2quater)**, GSM baz istasyonunun yayınladığı ve bekleme (idle) veya aktif çağrı modundaki mobil cihazlara (MS) diğer radyo erişim teknolojilerindeki (**Inter-RAT**: 3G WCDMA ve 4G LTE) komşu hücre listelerini ve geçiş eşik parametrelerini bildiren en gelişmiş BCCH mesajıdır.

GSM şebekesinden 3G/4G şebekelerine kesintisiz geçişi (Cell Reselection / Handover) yöneten ana protokoldür.

---

## 1. Inter-RAT Komşu Listeleri ve Parametreler

SI2quater mesajı, diğer şebeke teknolojilerine ait kanal indekslerini içerir:

### A. 3G (UMTS / WCDMA) Komşu Listesi
* Çevredeki 3G baz istasyonlarının downlink taşıyıcı kanallarını tanımlamak için **[[UARFCN]]** (UTRA Absolute Radio Frequency Channel Number) listesini ve bu kanallara ait scrambling kodlarını (Scrambling Codes) taşır.
* Mobil cihaz, SI2quater'da belirtilen bu **[[UARFCN]]** kanallarını tarayarak uygun sinyal gücü bulduğunda 3G hücresine geçiş yapar.

### B. 4G (LTE) Komşu Listesi
* Çevredeki 4G LTE baz istasyonlarının downlink frekanslarını tanımlamak için **[[EARFCN]]** (E-UTRA Absolute Radio Frequency Channel Number) listesini ve her frekanstaki taranacak fiziksel hücre kimliği (PCI) aralıklarını taşır.
* Cihaz, tanımlanan bu **[[EARFCN]]** taşıyıcı frekanslarını ve hücre sınırlarını sürekli ölçerek 4G şebekesine geri dönüş (Reselection) kurallarını uygular.

---

## 2. GSM'den LTE/3G Şebekelerine Hücre Yeniden Seçim (Cell Reselection) Eşikleri

SI2quater mesajı içerisinde, geçiş kararlarını etkileyen şu dinamik parametreler yayınlanır:

* **Qsearch_I (Query Search Idle):** Bekleme modundaki mobil cihazın, 3G ve 4G hücre aramalarını başlatması için gereken GSM sinyal gücü eşiğidir. (Örneğin GSM sinyali belirli bir seviyenin altına düştüğünde arama başlatılır).
* **Qsearch_C (Query Search Dedicated):** Cihaz aktif çağrıdayken inter-RAT ölçümlerine başlama eşiğidir.
* **GERAN_PRIORITY:** GSM hücresinin öncelik değeri.
* **UTRAN_PRIORITY / E-UTRAN_PRIORITY:** Cihaza 3G ve 4G frekanslarının GSM'den daha yüksek öncelikli olduğunu belirten öncelik indeksleridir (Genellikle 4G önceliği en yükseğe set edilir).

---

## 3. Komşu Hücre Analizindeki Önemi
Faz 1'de gerçekleştirilen canlı `tshark` paket yakalama doğrulaması sırasında **System Information Type 2quater** paketlerinin başarıyla havadan yakalandığı ve çözümlendiği raporlanmıştır. Bu paketlerin çözümlenmesi, pasif bir GSM analiz sistemine çevredeki **tüm aktif LTE ([[EARFCN]]) şebekelerinin ve frekanslarının gizli haritasını** sunar. Bu sayede, hiç LTE taraması yapmadan sadece tek bir GSM hücresini dinleyerek çevredeki LTE bant yapılandırmalarını keşfetmek mümkün hale gelir.

---

## 4. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information ana yapısı.
* [[EARFCN]] — LTE radyo kanalları hesaplama teorisi.
* [[UARFCN]] — 3G radyo kanalları indeks yapısı.
* [[GSM vs LTE Komşu Tespiti]] — İki şebeke arasındaki komşu mantığı karşılaştırması.
* [[SIB6]] — LTE şebekesinden GSM yönüne olan inter-RAT komşu yayını.
