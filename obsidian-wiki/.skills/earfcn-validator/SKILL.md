---
name: earfcn-validator
description: >
  Validates and parses a raw list of LTE EARFCN numbers against 3GPP TS 36.101 specifications and LimeSDR Mini 2.0 frequency ranges (10 MHz – 3.5 GHz).
  Triggers when the user provides a raw list of EARFCNs to scan or analyze.
  Returns structured JSON classifying each EARFCN into valid, warnings (unsupported hardware), and invalid.
---

# `earfcn-validator` Skill

Bu skill, kullanıcının girdiği ham LTE EARFCN (E-UTRA Absolute Radio Frequency Channel Number) listesini parse edip, **3GPP TS 36.101** standartlarında merkez Downlink frekanslarını ve band numaralarını hesaplar. Aynı zamanda frekansların **LimeSDR Mini 2.0** donanım limitleri (10 MHz – 3.5 GHz) içerisinde taranıp taranamayacağını denetler.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Kullanıcı tarama yapmak için ham EARFCN veya EARFCN listesi sunduğunda (örn: *"Şu EARFCN'leri doğrula"*, *"Taramaya hazırlık için EARFCN listesini kontrol et"*).
- Bir tarama başlatılmadan önce ilk girdi doğrulama aşaması olarak tetiklenir.

---

## 2. Girdi Formatı (Input Format)

Girdi, virgül, boşluk veya yeni satır ile ayrılmış ham EARFCN değerlerinden oluşan bir dizidir (string veya array).
- *Örnek Girdi*: `"1300, 1444, 3350, 6200, 9870, 65535"`

---

## 3. İşlem ve Hesaplama Mantığı

### Downlink Frekans Hesaplama Formülü (3GPP TS 36.101)
$$F_{DL} = F_{DL\_low} + 0.1 \times (N_{DL} - N_{Offs\text{-}DL})$$

### 3GPP LTE Band Eşleştirme Tablosu
Hesaplama sırasında aşağıdaki band aralıkları baz alınır:
- **Band 1**: EARFCN `0 - 599` | $F_{DL\_low} = 2110.0$ MHz | $N_{Offs\text{-}DL} = 0$
- **Band 3**: EARFCN `1200 - 1949` | $F_{DL\_low} = 1805.0$ MHz | $N_{Offs\text{-}DL} = 1200$
- **Band 7**: EARFCN `2750 - 3449` | $F_{DL\_low} = 2620.0$ MHz | $N_{Offs\text{-}DL} = 2750$
- **Band 8**: EARFCN `3450 - 3799` | $F_{DL\_low} = 925.0$ MHz | $N_{Offs\text{-}DL} = 3450$
- **Band 20**: EARFCN `6150 - 6449` | $F_{DL\_low} = 791.0$ MHz | $N_{Offs\text{-}DL} = 6150$
- **Band 31**: EARFCN `9870 - 9919` | $F_{DL\_low} = 462.5$ MHz | $N_{Offs\text{-}DL} = 9870$
- **Band 28**: EARFCN `9210 - 9659` | $F_{DL\_low} = 758.0$ MHz | $N_{Offs\text{-}DL} = 9210$

### Donanımsal Denetim (LimeSDR Mini 2.0 Limit Kontrolü)
- Hesaplanan merkez frekansı ($F_{DL}$) **10 MHz ile 3500 MHz (3.5 GHz)** aralığında olmalıdır.
- Sınırların dışında kalan veya taranamayan bandlar (örn. 450 MHz Band 31 veya donanım limit dışı durumlar) `hw_ok: false` olarak işaretlenir ve `warnings` dizisine yönlendirilir.
- Yukarıdaki band tanımlarında yer almayan veya 3GPP limit dışı olan EARFCN'ler doğrudan `invalid` dizisine aktarılır.

---

## 4. Çıktı Formatı (Output Format - JSON)

Çıktı, üç ana diziden oluşan geçerli bir JSON objesidir:

```json
{
  "valid": [
    {
      "earfcn": 1300,
      "band": 3,
      "freq_mhz": 1815.0,
      "bw": "20MHz",
      "hw_ok": true
    }
  ],
  "warnings": [
    {
      "earfcn": 9870,
      "band": 31,
      "freq_mhz": 462.5,
      "reason": "Bu donanımla taranamaz (Limit dışı / donanım desteklemiyor)"
    }
  ],
  "invalid": [
    {
      "earfcn": 65535,
      "reason": "Tanımsız aralık / 3GPP band eşleşmesi bulunamadı"
    }
  ]
}
```

---

## 5. Hata Yönetimi (Error Management)

- Girdi içinde sayısal olmayan karakterler (harf veya sembol) bulunursa, bu elemanlar elenir ve `invalid` dizisine `reason: "Sayısal olmayan girdi"` açıklamasıyla eklenir.
- Girdi boş olduğunda veya hiçbir geçerli sayı bulunamadığında işlem sonlandırılır ve `"Hata: Doğrulanacak geçerli EARFCN bulunamadı"` uyarısı verilir.

---

## 6. Kullanım ve Doğrulama Örneği (Verification Test Run)

### Ham Girdi Listesi
`"1300, 1444, 3350, 6200, 9870, 65535"`

### Çıktı Üretimi ve Doğrulama
1.  **EARFCN 1300**: Band 3 aralığında ($1200 \dots 1949$).
    $$F_{DL} = 1805.0 + 0.1 \times (1300 - 1200) = 1815.0\text{ MHz}$$
    Frekans aralıkta (10 MHz – 3.5 GHz). Durum: **VALID, hw_ok = true**.
2.  **EARFCN 1444**: Band 3 aralığında ($1200 \dots 1949$).
    $$F_{DL} = 1805.0 + 0.1 \times (1444 - 1200) = 1829.4\text{ MHz}$$
    Frekans aralıkta. Durum: **VALID, hw_ok = true**.
3.  **EARFCN 3350**: Band 7 aralığında ($2750 \dots 3449$).
    $$F_{DL} = 2620.0 + 0.1 \times (3350 - 2750) = 2680.0\text{ MHz}$$
    Frekans aralıkta. Durum: **VALID, hw_ok = true**.
4.  **EARFCN 6200**: Band 20 aralığında ($6150 \dots 6449$).
    $$F_{DL} = 791.0 + 0.1 \times (6200 - 6150) = 796.0\text{ MHz}$$
    Frekans aralıkta. Durum: **VALID, hw_ok = true**.
5.  **EARFCN 9870**: Band 31 aralığında ($9870 \dots 9919$).
    $$F_{DL} = 462.5 + 0.1 \times (9870 - 9870) = 462.5\text{ MHz}$$
    Merkez frekans 462.5 MHz. 700 MHz altında veya donanım limit dışında kaldığından (veya Türkiye spektrumuna uygun olmadığından) durum: **WARNING, reason: "Bu donanımla taranamaz"**.
6.  **EARFCN 65535**: Hiçbir band aralığına girmiyor. Durum: **INVALID, reason: "Tanımsız aralık"**.

---

## 7. Wiki Referansları

- [[EARFCN]] — Dönüşüm formülleri referansı.
- [[LTE Bandlar]] — Operatör ve band aralık detayları.
- [[Frekans Tablosu]] — Spektrum referans haritası ve donanım limitleri.
- [[LimeSDR Mini 2.0]] — Donanımsal alıcı frekans sınırları.
