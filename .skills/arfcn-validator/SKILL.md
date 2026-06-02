---
name: arfcn-validator
description: >
  Validates and parses a raw list of GSM ARFCN numbers against 3GPP TS 45.005 specifications and LimeSDR Mini 2.0 frequency ranges (10 MHz – 3.5 GHz).
  Triggers when the user provides a raw list of ARFCNs to validate or analyze.
  Returns structured JSON classifying each ARFCN into valid, warnings (unsupported hardware or edge cases like ARFCN 0), and invalid.
---

# `arfcn-validator` Skill

Bu skill, kullanıcının girdiği ham GSM ARFCN (Absolute Radio Frequency Channel Number) listesini parse edip, **3GPP TS 45.005** standartlarında merkez Downlink frekanslarını ve bant numaralarını hesaplar. Aynı zamanda frekansların **LimeSDR Mini 2.0** donanım limitleri (10 MHz – 3.5 GHz) içerisinde taranıp taranamayacağını denetler ve Türkiye spektrumundaki operatör dağılımlarını eşleştirir.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Kullanıcı tarama yapmak için ham ARFCN veya ARFCN listesi sunduğunda (örn: *"Şu ARFCN'leri doğrula"*, *"Taramaya hazırlık için ARFCN listesini kontrol et"*).
- GSM taraması başlatılmadan önce ilk girdi doğrulama aşaması olarak tetiklenir.

---

## 2. Girdi Formatı (Input Format)

Girdi, virgül, boşluk veya yeni satır ile ayrılmış ham ARFCN değerlerinden oluşan bir dizidir (string veya array).
- *Örnek Girdi*: `"48, 54, 55, 56, 57, 58, 59, 60, 61, 0, 9999"`

---

## 3. İşlem ve Hesaplama Mantığı

### Downlink Frekans Hesaplama Formülleri (3GPP TS 45.005)

Hesaplama sırasında aşağıdaki bant aralıkları baz alınır:
* **P-GSM 900 (Primary GSM-900):** $1 \le n \le 124$
  * Downlink Frekansı: $F_{DL}(n) = 935.0 + 0.2 \times n$
* **E-GSM 900 (Extended GSM-900):** $0 \le n \le 124$ veya $975 \le n \le 1023$
  * $0 \le n \le 124$: $F_{DL}(n) = 935.0 + 0.2 \times n$
  * $975 \le n \le 1023$: $F_{DL}(n) = 935.0 + 0.2 \times (n - 1024)$
* **DCS-1800 (Digital Cellular System 1800):** $512 \le n \le 885$
  * Downlink Frekansı: $F_{DL}(n) = 1805.2 + 0.2 \times (n - 512)$

### Donanımsal ve Özel Edge-Case Denetimleri
1. **LimeSDR Mini 2.0 Limit Kontrolü:** Hesaplanan merkez frekansı ($F_{DL}$) **10 MHz ile 3500 MHz (3.5 GHz)** aralığında olmalıdır.
2. **ARFCN 0 Edge-Case Uyarısı:** ARFCN 0, E-GSM standardında $935.0$ MHz frekansına karşılık gelir ve teknik olarak geçerlidir. Ancak bazı baz istasyonlarında guard band (koruma bandı) veya frekans tahsis sınırı olarak özel amaçla ayrıldığından, `warnings` listesine `reason: "ARFCN 0 E-GSM için geçerli fakat guard band/sınır frekansı olabilir, dikkatli olun"` açıklamasıyla eklenir.
3. **Türkiye Operatör Eşleştirmesi:**
  * Downlink frekansı ve ARFCN aralıklarına göre operatör tahmini yapılır:
    * ARFCN `1 - 35`: **Turkcell**
    * ARFCN `36 - 70`: **Vodafone TR** (Not: ARFCN 60 yerel test ağlarında Turkcell olarak çalışabilir)
    * ARFCN `71 - 105`: **Türk Telekom**
    * ARFCN `512 - 586`: **Vodafone TR** (DCS-1800)
    * ARFCN `587 - 661`: **Türk Telekom** (DCS-1800)
    * ARFCN `662 - 736`: **Turkcell** (DCS-1800)

---

## 4. Çıktı Formatı (Output Format - JSON)

Çıktı, üç ana diziden oluşan geçerli bir JSON objesidir:

```json
{
  "valid": [
    {
      "arfcn": 60,
      "band": "GSM-900",
      "freq_mhz": 947.0,
      "operator_estimate": "Vodafone TR (Actual: Turkcell in local testbed)",
      "hw_ok": true
    }
  ],
  "warnings": [
    {
      "arfcn": 0,
      "band": "E-GSM-900",
      "freq_mhz": 935.0,
      "reason": "ARFCN 0 E-GSM için geçerli fakat guard band/sınır frekansı olabilir, dikkatli olun"
    }
  ],
  "invalid": [
    {
      "arfcn": 9999,
      "reason": "Tanımsız aralık / 3GPP band eşleşmesi bulunamadı"
    }
  ]
}
```

---

## 5. Hata Yönetimi (Error Management)

- Girdi içinde sayısal olmayan karakterler bulunursa, bu elemanlar elenir ve `invalid` dizisine `reason: "Sayısal olmayan girdi"` açıklamasıyla eklenir.
- Girdi boş olduğunda işlem sonlandırılır ve `"Hata: Doğrulanacak geçerli ARFCN bulunamadı"` uyarısı verilir.

---

## 6. Kullanım ve Doğrulama Örneği (Faz 1 Canlı Veri Testi)

### Ham Girdi Listesi
`"48, 54, 55, 56, 57, 58, 59, 60, 61, 0, 9999"`

### Çıktı Üretimi ve Hesaplamalar
1. **ARFCN 60 (Aktif Hücre):** GSM-900 bandında. $F_{DL} = 935.0 + 0.2 \times 60 = 947.0$ MHz. Durum: **VALID, hw_ok = true**.
2. **Komşular (48, 54, 55, 56, 57, 58, 59, 61):** Hepsi GSM-900 bandında.
   * Örn: ARFCN 48: $F_{DL} = 935.0 + 0.2 \times 48 = 944.6$ MHz. Durum: **VALID**.
   * Örn: ARFCN 61: $F_{DL} = 935.0 + 0.2 \times 61 = 947.2$ MHz. Durum: **VALID**.
3. **ARFCN 0 (Edge Case):** $F_{DL} = 935.0$ MHz. Durum: **WARNING (E-GSM guard band/boundary)**.
4. **ARFCN 9999:** Hiçbir 3GPP bant aralığına girmiyor. Durum: **INVALID**.

---

## 7. Wiki Referansları

- [[GSM ARFCN]] — Dönüşüm formülleri detaylı referansı.
- [[GSM Bandlar]] — Operatör spektrum atamaları.
- [[GSM Frekans Tablosu]] — Lookup tablosu.
- [[LimeSDR Mini 2.0]] — SDR donanım frekans aralık limitleri.
