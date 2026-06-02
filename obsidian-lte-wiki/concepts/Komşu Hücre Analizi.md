---
title: Komşu Hücre Analizi
source: 3GPP TS 36.304, 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - radio
  - mobility
  - concepts
---

# Komşu Hücre (Neighbor Cell) Analizi ve Ağ Mobilitesi

LTE ve diğer tüm hücresel şebekelerde mobil cihazların (UE) kesintisiz hizmet alabilmesi, hareket halindeyken bağlantının kopmaması (handover/reselection) ve ağ kaynaklarının dengeli dağıtılması için hücrelerin birbirleriyle tanımlı coğrafi komşuluk ilişkileri bulunmalıdır.

**Komşu Hücre Analizi**, bir baz istasyonunun (eNodeB) yayınladığı sistem bilgi blokları ([[SIB4]], [[SIB5]], [[SIB6]], [[SIB7]]) çözümlenerek, servis verilen hücre etrafındaki diğer hücrelerin ve teknolojilerin haritalandırılması sürecidir.

---

## 1. Komşuluk İlişkileri Türleri

Komşuluk ilişkileri frekans ve teknoloji durumuna göre üç ana gruba ayrılır:

### A. Aynı Frekanslı Komşuluklar (Intra-frequency Neighbors)
- **Açıklama**: Servis hücresi ile aynı [[EARFCN]] değerine sahip komşu hücrelerdir.
- **Yayın Kanalı**: [[SIB4]]
- **Mekanizma**: Cihaz, aynı frekanstaki hücreleri ayırt etmek için fiziksel hücre kimliği olan **PCI (Physical Cell Identity)** değerini kullanır. 
- **Önemi**: Aynı frekansta oldukları için cihaz bu hücreleri sürekli olarak arka planda ölçer. Girişim (interference) analizi ve hızlı reselection için en kritik gruptur.

### B. Farklı Frekanslı Komşuluklar (Inter-frequency Neighbors)
- **Açıklama**: Servis hücresi ile farklı [[EARFCN]] değerlerindeki komşu LTE hücreleridir. Operatörün diğer LTE bantlarındaki (örn: Band 20'den Band 3'e veya Band 7'ye) hücrelerini kapsar.
- **Yayın Kanalı**: [[SIB5]]
- **Önemi**: Operatörün kapasite ve kapsama katmanları arasındaki yük dağılımını (load balancing) ve geçiş stratejilerini yansıtır.

### C. Farklı Teknolojili Komşuluklar (Inter-RAT Neighbors)
- **Açıklama**: LTE dışındaki diğer radyo teknolojilerini (2G/3G/5G) kapsayan komşuluk ilişkileridir.
- **Yayın Kanalları**:
  - **[[SIB6]]**: UTRAN (3G - UMTS/WCDMA) komşuları.
  - **[[SIB7]]**: GERAN (2G - GSM/GPRS/EDGE) komşuları.
- **Önemi**: LTE kapsama alanının bittiği bölgelerde cihazların 3G veya 2G şebekelerine kesintisiz yedeklenmesini (fallback/CSFB) sağlamak için kritiktir.

---

## 2. Boşta Modda Hücre Yeniden Seçim Mekanizması (Cell Reselection)

Cihaz boşta (idle) durumdayken, hücreler arası geçiş kararı tamamen cihazın kendisi tarafından, baz istasyonundan aldığı reselection parametreleri doğrultusunda verilir. Bu süreçte üç temel kural grubu işler:

### 1. Bekçi Parametreleri (SIB3)
Cihaz, servis hücresi sinyali (RSRP) iyi durumdayken gereksiz tarama yapıp pil tüketmemek için komşuları taramaz. Tarama sınırını belirleyen parametreler [[SIB3]] içindedir:
- Servis RSRP $\le S_{IntraSearch} + Q_{RxLevMin}$ ise aynı frekanslı komşuları ([[SIB4]]) ölçmeye başlar.
- Servis RSRP $\le S_{NonIntraSearch} + Q_{RxLevMin}$ ise farklı frekanslı ([[SIB5]]) ve inter-RAT ([[SIB6]], [[SIB7]]) komşuları ölçmeye başlar.

### 2. Yüksek Öncelikli Hücreye Geçiş (High Priority Reselection)
Eğer komşu frekansın önceliği (`cellReselectionPriority`) mevcut servis frekansının önceliğinden yüksekse (örn: Servis önceliği 3, komşu önceliği 6 ise):
- Cihaz, servis hücresi sinyali çok iyi olsa bile komşu hücre RSRP değerinin [[SIB5]]'te belirtilen `threshX-High` eşiğini aşması durumunda doğrudan yüksek öncelikli komşu hücreye geçiş yapar.
- Operatörlerin cihazları Band 20 (800 MHz) kapsama katmanından hızlıca Band 3 (1800 MHz) kapasite katmanına geçirmek için kullandığı temel yöntem budur.

### 3. Düşük Öncelikli Hücreye Geçiş (Low Priority Reselection)
Eğer komşu frekansın önceliği mevcut servis frekansının önceliğinden düşükse (örn: Servis önceliği 5, komşu önceliği 2 ise):
- Sadece servis hücresi sinyali `threshServingLow` eşiğinin altına indiğinde ve düşük öncelikli komşu sinyali `threshX-Low` eşiğinin üzerine çıktığında bu hücreye geçiş gerçekleşir.

---

## 3. Komşu Hücre Analizinin Önemi

Radyo frekans (RF) planlamasında ve mobil siber güvenlik araştırmalarında komşu hücre analizi şu amaçlarla kritik önem taşır:

1.  **Kapsama Alanı Deliklerinin (Coverage Holes) Tespiti**: Komşu planlaması yapılmayan veya komşu ilişkisi kırık olan bölgelerde sinyal olmasına rağmen cihazlar handover yapamadığı için çağrılar düşer (call drops).
2.  **Fake Base Station (IMSI Catcher) Tespiti**: Sahte baz istasyonları, hedef cihazları üzerlerine çekebilmek için çevre hücrelerin komşuluk ilişkilerini taklit eder veya cihazları daha düşük öncelikli sahte 2G katmanlarına düşürmek için man-in-the-middle saldırıları düzenler. Bu durumlarda sahte hücrelerin komşuluk planları normal şebekeden ciddi şekilde sapar.
3.  **Ağ Yedekliliğinin Analizi**: Şebeke kalitesinin düştüğü kritik anlarda 3G ([[SIB6]]) ve 2G ([[SIB7]]) katmanlarına doğru yedekleme kanallarının aktif olup olmadığını doğrulamak.

---

## 4. GSM (2G) Şebekelerinde Komşu Hücre Analizi

2G (GSM) şebekelerinde komşuluk ilişkileri, LTE'ye kıyasla daha basitleştirilmiş bir bitmap yapısı olan **BA (BCCH Allocation) Listeleri** üzerinden yönetilir.

* **Idle Mod İzleme:** Cihaz bekleme modundayken en iyi 2G hücresine geçiş yapabilmek için [[GSM SI2]], [[GSM SI2bis]] ve [[GSM SI2ter]] mesajlarında taşınan BA(BCCH) listesindeki komşu ARFCN frekanslarını sürekli dinler.
* **Dedicated Mod Raporlama:** Aktif bir çağrı sırasında cihaz, [[GSM SI5]], [[GSM SI5bis]] ve [[GSM SI5ter]] mesajları üzerinden kendisine adanan BA(SACCH) listesindeki komşu frekansları ölçer ve her 480 ms'de bir baz istasyonuna (BTS) **Measurement Report** (Ölçüm Raporu) gönderir.
* **LTE Karşılaştırması:** GSM komşu mimarisi, parametre isimleri ve araç karşılaştırmaları hakkında detaylı teknik analiz için [[GSM vs LTE Komşu Tespiti]] sayfasına bakınız.

