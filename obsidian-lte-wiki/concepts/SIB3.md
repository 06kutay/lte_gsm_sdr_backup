---
title: SIB3
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - mobility
---

# SIB3 (System Information Block Type 3)

**SIB3**, LTE boşta mod (RRC_IDLE) mobilite yönetimi için kritik bir mesajdır. Hücre seçimi (cell selection) ve hücre yeniden seçimi (cell reselection) için tüm hücreye özel ve ortak parametreleri tanımlar. 

Cihaz, mevcut servis hücresinden başka bir hücreye geçip geçmeyeceğine karar verirken SIB3 parametrelerini kullanır.

---

## 1. Kritik Hücre Seçim ve Yeniden Seçim Parametreleri

### A. cellReselectionServingFreqInfo (Servis Frekansı Parametreleri)
- **cellReselectionPriority**: Mevcut servis frekansının (EARFCN) öncelik değeridir (0 ile 7 arası bir tamsayı). `7` en yüksek önceliği, `0` en düşük önceliği gösterir. Operatörler cihazları yüksek bantlara (örn: Band 7 - 2600 MHz) yönlendirmek için buralara yüksek öncelik verir.
- **s-NonIntraSearch**: Servis dışı/Farklı frekanstaki (non-intra-frequency/inter-freq) hücreleri arama eşiğidir. Cihazın farklı frekanstaki veya diğer teknolojilerdeki ([[SIB5]], [[SIB6]], [[SIB7]]) komşuları taramaya başlaması için gereken sinyal sınırını belirler.
  - Formül: $S_{NonIntraSearch} = s\text{-}NonIntraSearch \times 2$ (dB)
- **threshServingLow**: Servis hücresinin kalitesinin altına düşmesi gereken eşik değeridir. Eğer servis kalitesi bu değerin altına düşerse, cihaz daha düşük öncelikli frekanslardaki komşuları aramaya başlar.

### B. intraFreqCellReselectionInfo (Aynı Frekans Seçim Parametreleri)
- **q-RxLevMin**: Hücrede kalabilmek (servis alabilmek) için gereken minimum RSRP (Reference Signal Received Power) seviyesidir (formülü [[SIB1]] ile aynıdır: $\text{dBm} = q\text{-}RxLevMin \times 2$).
- **s-IntraSearch**: Aynı frekanstaki (intra-frequency) komşu hücreleri ([[SIB4]]) arama eşiğidir. Servis hücresi kalitesi bu sınırın altına düşmediği sürece cihaz gereksiz pil tüketimini önlemek için komşu taraması yapmaz.
  - Formül: $S_{IntraSearch} = s\text{-}IntraSearch \times 2$ (dB)

---

## 2. Arama Koşullarının Hesaplanması (Measurement Conditions)

Aşağıdaki matematiksel eşikler, cihazın komşu hücre araması yapıp yapmayacağını belirler. Bu hesaplamalar [[dbparsers]] altındaki `get-info.py` tarafından otomatik olarak yapılır:

### Aynı Frekans Arama Koşulu (Intra-frequency meas condition)
Cihazın, servis hücresiyle aynı EARFCN'deki komşuları aramaya başlaması için mevcut RSRP değerinin şu eşikten küçük veya eşit olması gerekir:
$$\text{Ölçüm Eşiği (dBm)} = S_{IntraSearch} + (q\text{-}RxLevMin \times 2)$$
*Örnek*: SIB3'te `s-IntraSearch = 29` (yani $29 \times 2 = 58$ dB) ve `q-RxLevMin = -64` (yani $ -64 \times 2 = -128$ dBm) ise:
$$\text{Ölçüm Başlama Sınırı} = 58 + (-128) = \mathbf{-70\text{ dBm}}$$
*Sonuç*: Servis hücresinin RSRP değeri $-70$ dBm altına inmediği sürece, cihaz aynı frekanstaki komşuları taramaz.

### Farklı Frekans Arama Koşulu (Inter-frequency meas condition)
Cihazın, farklı EARFCN'lerdeki ([[SIB5]]) komşuları aramaya başlaması için mevcut RSRP değerinin şu eşikten küçük veya eşit olması gerekir:
$$\text{Ölçüm Eşiği (dBm)} = (s\text{-}NonIntraSearch \times 2) + (q\text{-}RxLevMin \times 2)$$
*Örnek*: `s-NonIntraSearch = 20` ($40$ dB) ve `q-RxLevMin = -64` ($-128$ dBm) ise:
$$\text{Ölçüm Başlama Sınırı} = 40 + (-128) = \mathbf{-88\text{ dBm}}$$
*Sonuç*: Servis hücresi RSRP değeri $-88$ dBm altına inmediği sürece, cihaz farklı frekanstaki komşuları taramaz.

---

## 3. Komşuluk İlişkileriyle Bağlantı

- SIB3, cihazın komşuları arayıp aramayacağına karar veren "bekçi" parametreleri taşır.
- Eğer tarama şartları sağlanırsa, aynı frekanstaki komşular için [[SIB4]], farklı frekanstaki LTE komşuları için [[SIB5]], 3G için [[SIB6]] ve 2G için [[SIB7]] okunur.
- [[Komşu Hücre Analizi]] sürecinde bu reselection öncelikleri (priority) mobilitenin kalbini oluşturur.
