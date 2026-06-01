---
title: SIB1
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - protocols
---

# SIB1 (System Information Block Type 1)

**SIB1**, LTE sisteminde hücre yayını olarak iletilen en kritik kontrol mesajlarından biridir. Hücreye erişim (cell access related information) kurallarını ve diğer SIB'lerin zamanlama (scheduling) parametrelerini taşır. 

SIB1 çözümlenmeden bir cihazın (UE) hücreye bağlanması veya diğer sistem bilgilerini (SIB'leri) okuması mümkün değildir.

---

## 1. Zamanlama ve Periyot

- SIB1, **80 ms**'lik sabit bir periyotla yayınlanır.
- Bu periyot içerisinde her **20 ms**'de bir tekrarlanır (SFN mod 8 = 0, subframe 5 olan radyo çerçevelerinde yeni bir SIB1 iletilir; mod 2, 4, 6 olanlarda ise tekrarları gönderilir).
- Dinamik planlama yerine yarı-statik zamanlamaya sahip olduğu için UE tarafından yeri kolayca tespit edilebilir.

---

## 2. İçerdiği Kritik Parametreler

3GPP standartlarında SIB1 yapısı şu temel alanları içerir:

### A. Hücre Erişim Bilgileri (cellAccessRelatedInfo)
- **PLMN-IdentityList**: Hücreyi işleten operatörlerin **PLMN (Public Land Mobile Network)** listesidir. Her PLMN; **MCC (Mobile Country Code)** ve **MNC (Mobile Network Code)** değerlerinden oluşur. Örneğin Türkiye için:
  - Turkcell: MCC `286`, MNC `01`
  - Vodafone: MCC `286`, MNC `02`
  - Türk Telekom: MCC `286`, MNC `03`
- **Tracking Area Code (TAC)**: Hücrenin bağlı olduğu konum takip alan kodu (16-bit tamsayı). Cihaz boşta (idle) moddayken TAC değiştiğinde ağa Tracking Area Update (TAU) yapar.
- **Cell Identity**: Hücreyi ağ genelinde tekil olarak tanımlayan 28-bitlik değerdir. eNodeB ID (en anlamlı 20 bit) ve Hücre ID (en anlamsız 8 bit) birleşiminden oluşur.
- **cellReservedForOperatorUse**: Hücrenin sadece operatör testleri/operasyonu için rezerve edilip edilmediği.
- **cellBarred**: Hücrenin cihaz erişimine kapalı olup olmadığını belirtir (`barred` veya `notBarred`). Eğer barred ise cihaz bu hücreye bağlanamaz.

### B. Hücre Seçim Kriterleri (cellSelectionInfo)
- **q-RxLevMin**: Hücreye bağlanabilmek için gereken minimum RSRP (Reference Signal Received Power) seviyesidir. Cihazın alıcı duyarlılığını belirler. Hesaplama formülü:
  $$\text{Min RSRP (dBm)} = q\text{-}RxLevMin \times 2$$
  *Örnek*: SIB1'de bu değer `-64` ise minimum RSRP $= -64 \times 2 = -128$ dBm olmalıdır.

### C. Planlama Bilgileri (schedulingInfoList)
Diğer tüm SIB'lerin (SIB2, SIB3, SIB4, SIB5, SIB6, SIB7 vb.) hangi **SI (System Information) Mesajları** içinde gruplandığını, yayınlanma periyodunu (80 ms, 160 ms, 320 ms vb.) ve SI pencere genişliğini (si-WindowLength - 1, 2, 5, 10, 15, 20, 40 ms) tanımlar.

---

## 3. lte-sib-parser ve get-info.py Entegrasyonu

[[lte-sib-parser]] aracı ile kaydedilen hücre veritabanında (`cells.sqlite`), SIB1 içeriği JSON formatında saklanır. [[dbparsers]] altında bulunan `get-info.py` scripti SIB1'den şu parametreleri parse ederek ekrana tablo halinde yazar:

```bash
Band    EARFCN  RSRP    TAC     cellIdentity    Priority    MCC     MNC
3       1675    -85     12345   14285701        7           286     01
```

Bu çıktıdaki `TAC` (12345) ve `cellIdentity` (14285701) değerleri doğrudan SIB1'in ikili (binary) verisinden tamsayıya (integer) dönüştürülür.
- [[SIB Genel]] ile ilişkisine göz atarak tüm SIB mekanizmasını anlayabilirsiniz.
- SIB1 sonrasında cihaz, yeniden seçim parametrelerini okumak için [[SIB3]] ve komşuları analiz etmek için [[SIB5]] sayfalarına başvurur.
