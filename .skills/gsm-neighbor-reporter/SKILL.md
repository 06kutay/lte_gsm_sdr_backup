---
name: gsm-neighbor-reporter
description: >
  Formulates comprehensive, human-readable markdown reports of discovered GSM neighbor cells.
  Processes the validated ARFCN list and parsed GSMTAP neighbor data to map relationships.
---

# `gsm-neighbor-reporter` Skill

Bu skill, `gsmtap-parser` ve `arfcn-validator` adımlarından elde edilen ham hücre ve komşu ARFCN verilerini birleştirerek, **insan okuyabilir, yapılandırılmış ve 3GPP/BTK standartlarına uygun komşu hücre ilişkileri raporları** üretir. 

LTE tarafındaki `neighbor-reporter` skill'inin doğrudan 2G karşılığıdır.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Canlı veya offline tarama verileri `gsmtap-parser` ve `arfcn-validator` ile parse edilip geçerli veriler doğrulandıktan sonra otomatik olarak zincirlenir.
- Kullanıcı belirli bir GSM hücresi için komşu raporu oluşturmak istediğinde tetiklenir (örn: *"ARFCN 60 hücresinin komşu raporunu oluştur"*, *"Yakalanan 2G komşu verilerini tablola"*).

---

## 2. Raporlama ve Hesaplama Kuralları

1.  **Kaynak Hücre Tespiti:** Raporda ana hücrenin MCC, MNC, LAC, CID, frekans ve sinyal gücü (`signal_dbm`) en üstte özet kartı olarak sunulmalıdır.
2.  **Komşu Hücrelerin Frekanslarının Hesaplanması:** Her bir komşu ARFCN için 3GPP formülleri kullanılarak merkez downlink frekansı hesaplanır ve `MHz` cinsinden tabloya işlenir.
3.  **Bant ve Spektrum Eşleştirmesi:** Her frekansın hangi banda (GSM-900 vs DCS-1800) girdiği ve BTK spektrum aralıklarına göre hangi Türkiye operatörüne ait olduğu tahmini tabloya eklenir.
4.  **Edge-Case Uyarısı:** Eğer komşular arasında ARFCN 0 varsa, tabloda uyarı sembolüyle (`⚠️`) işaretlenir ve dipnot eklenir.

---

## 3. Kullanım ve Doğrulama Örneği (Faz 1 Canlı Veri Raporu)

### Girdi (Parsed JSON):
```json
{
  "cell_info": {
    "arfcn": 60,
    "freq_mhz": 947.0,
    "signal_dbm": -66,
    "mcc": "286",
    "mnc": "01",
    "lac": 33006,
    "cid": 7349,
    "operator": "Turkcell"
  },
  "neighbors": [48, 54, 55, 56, 57, 58, 59, 60, 61]
}
```

### Üretilen Rapor Çıktısı (Markdown):

```markdown
# GSM Komşu Hücre İlişkileri Raporu — ARFCN 60

## 📡 Kaynak Hücre Özeti
*   **Hücre Kimliği (Cell ID):** 7349
*   **Location Area Code (LAC):** 33006
*   **Mobil Şebeke Kodu (PLMN):** 286-01 (Turkcell)
*   **Birincil Taşıyıcı (ARFCN):** 60 (Downlink: 947.0 MHz)
*   **Sinyal Gücü:** -66 dBm

## 🗺️ Komşu Hücre Matrisi (BA Listesi)
Kaynak baz istasyonu tarafından yayınlanan Sistem Bilgisi (SI2) paketlerinden çözümlenen aktif 9 komşu hücre listesi:

| Komşu ARFCN | Frekans Bandı | Downlink Frekansı | Spektrum Operatör Tahmini | Rol / Durum |
| :---: | :---: | :---: | :---: | :--- |
| **48** | GSM-900 | 944.6 MHz | Vodafone TR | Reselection Komşusu |
| **54** | GSM-900 | 945.8 MHz | Vodafone TR | Reselection Komşusu |
| **55** | GSM-900 | 946.0 MHz | Vodafone TR | Reselection Komşusu |
| **56** | GSM-900 | 946.2 MHz | Vodafone TR | Reselection Komşusu |
| **57** | GSM-900 | 946.4 MHz | Vodafone TR | Reselection Komşusu |
| **58** | GSM-900 | 946.6 MHz | Vodafone TR | Reselection Komşusu |
| **59** | GSM-900 | 946.8 MHz | Vodafone TR | Reselection Komşusu |
| **60** | GSM-900 | 947.0 MHz | Vodafone TR (Actual: Turkcell) | Kaynak Hücre (Self-Loop) |
| **61** | GSM-900 | 947.2 MHz | Vodafone TR | Reselection Komşusu |

> [!NOTE]
> BTK tahsisat listesine göre normalde ARFCN 36-70 aralığı Vodafone TR spektrumundadır. Ancak bu bölgede ARFCN 60 taşıyıcısının `286-01` (Turkcell) olarak yayın yapması, yerel bir test kurulumu veya özel bir frekans paylaşım protokolü olduğunu göstermektedir.
```

---

## 4. Wiki Referansları

- [[Cell_GSM_ARFCN60]] — Canlı taranan hücrenin detay sayfası.
- [[GSM Bandlar]] — Operatör spektrum atamaları.
- [[GSM vs LTE Komşu Tespiti]] — İki teknoloji arasındaki mantıksal eşleşmeler.
