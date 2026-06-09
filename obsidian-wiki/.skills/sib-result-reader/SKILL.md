---
name: sib-result-reader
description: >
  Reads, parses, and structurizes SQLite cells database results using list-cells.py, get-info.py, and get-arfcns.py helper scripts.
  Triggers after a scan session completes or when querying current database states.
  Outputs cell listings JSON with dynamic filters (PLMN, band, SIBs parsed) and a global network metrics summary.
---

# `sib-result-reader` Skill

Bu skill, tarama tamamlandıktan sonra `/vol/output/cells.sqlite` (veya tarih damgalı) veritabanına erişerek **[[dbparsers]]** betiklerini (`list-cells.py`, `get-info.py`, `get-arfcns.py`) arka planda çalıştırır. CLI çıktılarını makine tarafından okunabilir ve filtrelenebilir **yapılandırılmış JSON** nesnelerine dönüştürür.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Tarama başarıyla tamamlandığında veya kullanıcı veritabanındaki hücre listesini sorguladığında (örn: *"Tarama sonuçlarını oku"*, *"Veritabanında hangi hücreler çözülmüş listele"*).
- `sib-scan-builder` tarafından oluşturulan komut koşturulup sonuç üretildikten sonra tetiklenir.

---

## 2. Girdi Formatı (Input Format - JSON)

Veritabanı yolunu ve uygulanacak opsiyonel filtre kriterlerini (band, plmn, sib_status) kabul eder:

```json
{
  "database_path": "/vol/output/scan_20260601.sqlite",
  "filters": {
    "band": 3,
    "plmn": "28601",
    "require_sib5": true
  }
}
```

---

## 3. Çalışma ve Ayrıştırma Mekanizması

1.  **Script Çalıştırma**: Belirtilen veritabanı yolu üzerinde `list-cells.py` ve `get-info.py` koşturulur.
2.  **Veritabanı Okuma (Fallback)**: Eğer python scriptleri doğrudan JSON dönmeye uygun değilse, SQLite veritabanına doğrudan bağlanarak `cells` tablosunu sorgular:
    ```sql
    SELECT band, earfcn, rsrp, sib1, sib3, sib5 FROM cells;
    ```
3.  **JSON Ayrıştırma**: `sib1`, `sib3` ve `sib5` hücrelerindeki JSON stringleri deserialize edilir:
    - **PCI** (Fiziksel Hücre Kimliği): SIB1 çözümlenirken loglardan elde edilen PCI.
    - **cell_id**: SIB1 içindeki `cellIdentity` parametresi.
    - **plmn**: SIB1 içindeki `plmn-IdentityList` listesinden derlenen MCC + MNC (Örn: `28601`).
    - **tac**: SIB1 içindeki `trackingAreaCode`.
    - **sibs_decoded**: Boş olmayan SIB kolonlarının listesi (Örn: `[1, 2, 3, 5]`).
4.  **Özet Metrikler**:
    - `total_earfcn`: Taranan benzersiz frekans sayısı.
    - `total_cells`: Bulunan toplam hücre sayısı.
    - `sib5_decoded`: SIB5'i çözülmüş ve komşu listesi alınabilen hücre sayısı.
    - `unique_plmn`: Keşfedilen benzersiz operatör PLMN sayısı.

---

## 4. Çıktı Formatı (Output Format - JSON)

Skill, filtreleri uyguladıktan sonra aşağıdaki standartlaştırılmış JSON çıktısını verir:

```json
{
  "summary": {
    "total_earfcn": 4,
    "total_cells": 4,
    "sib5_decoded": 3,
    "unique_plmn": 2
  },
  "cells": [
    {
      "earfcn": 1300,
      "pci": 45,
      "cell_id": 14285701,
      "plmn": "28601",
      "tac": 12345,
      "band": 3,
      "rsrp": -85,
      "sibs_decoded": [1, 2, 3, 5],
      "sib5_raw": {
        "interFreqCarrierFreqList": [
          {
            "dl-CarrierFreq": 1675,
            "q-RxLevMin": -58,
            "allowedMeasBandwidth": "mbw100",
            "cellReselectionPriority": 6
          }
        ]
      }
    },
    {
      "earfcn": 1444,
      "pci": 82,
      "cell_id": 14285702,
      "plmn": "28601",
      "tac": 12345,
      "band": 3,
      "rsrp": -90,
      "sibs_decoded": [1, 2, 3, 5],
      "sib5_raw": {
        "interFreqCarrierFreqList": [
          {
            "dl-CarrierFreq": 3350,
            "q-RxLevMin": -58,
            "allowedMeasBandwidth": "mbw100",
            "cellReselectionPriority": 7
          }
        ]
      }
    },
    {
      "earfcn": 3350,
      "pci": 112,
      "cell_id": 28410293,
      "plmn": "28603",
      "tac": 54321,
      "band": 7,
      "rsrp": -92,
      "sibs_decoded": [1, 2, 3, 5],
      "sib5_raw": {
        "interFreqCarrierFreqList": [
          {
            "dl-CarrierFreq": 6200,
            "q-RxLevMin": -58,
            "allowedMeasBandwidth": "mbw50",
            "cellReselectionPriority": 3
          }
        ]
      }
    },
    {
      "earfcn": 6200,
      "pci": 210,
      "cell_id": 98721201,
      "plmn": "28603",
      "tac": 54321,
      "band": 20,
      "rsrp": -99,
      "sibs_decoded": [1, 2, 3]
    }
  ]
}
```

---

## 5. Hata Yönetimi (Error Management)

- SQLite veritabanı bulunamazsa veya bozuksa, `"Hata: SQLite veritabanı bulunamadı veya açılamadı: <path>"` hatası döner.
- `cells` tablosu boşsa veya taranmış veri henüz kaydedilmemişse, boş bir `cells` dizisi ve sıfırlanmış `summary` değerleri döner:
  ```json
  {"summary": {"total_earfcn": 0, "total_cells": 0, "sib5_decoded": 0, "unique_plmn": 0}, "cells": []}
  ```

---

## 6. Kullanım ve Doğrulama Örneği (Verification Test Run)

### CLI Çalıştırma Talimatı
```bash
python3 -c "import sqlite3, json; conn = sqlite3.connect('/vol/output/scan_20260601.sqlite'); ... (sorgu ve parse işlemi) ..."
```

---

## 7. Wiki Referansları

- [[dbparsers]] — Sorgu ve veri dönüştürme betikleri.
- [[lte-sib-parser]] — Veritabanı ve tablo şeması.
- [[SIB Genel]] — Çözümlenen SIB bloklarının mantıksal anlamları.
