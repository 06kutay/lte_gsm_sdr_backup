---
name: neighbor-reporter
description: >
  Processes the JSON output of sib-result-reader to extract and map all neighbor cell relationships (SIB4, SIB5, SIB6, SIB7).
  Analyzes link types (bidirectional vs unidirectional) and flags all unscanned inter-frequency EARFCNs for subsequent rescans.
---

# `neighbor-reporter` Skill

Bu skill, `sib-result-reader` tarafından üretilen yapılandırılmış hücre listesini girdi olarak alır, her bir servis hücresinin (serving cell) SIB4, SIB5, SIB6 ve SIB7 kontrol bloklarını tarayarak komşu listesini çıkarır. Şebeke mobilitesinin haritasını çıkararak **çift yönlü (bidirectional)**, **tek yönlü (unidirectional)** ilişkileri ve taranmamış **yeni EARFCN kanallarını (unscanned_earfcns)** tespit eder.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Tarama verileri okunduktan sonra komşu hücre analizi ve şebeke topolojisi çıkarma isteği oluştuğunda (örn: *"Komşu hücre ilişkilerini çıkar"*, *"Taranmamış hangi komşu kanalları var raporla"*).
- `sib-result-reader` çıktısı alındıktan sonra zincirleme olarak tetiklenir.

---

## 2. Girdi Formatı (Input Format - JSON)

`sib-result-reader` tarafından sağlanan hücre listesini ve özet yapısını girdi olarak kabul eder:

```json
{
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
          {"dl-CarrierFreq": 1675, "cellReselectionPriority": 6, "allowedMeasBandwidth": "mbw100"}
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
          {"dl-CarrierFreq": 3350, "cellReselectionPriority": 7, "allowedMeasBandwidth": "mbw100"}
        ]
      }
    }
  ]
}
```

---

## 3. Analiz ve Komşu Çıkarma Mantığı

### A. SIB Bazlı Komşu Sınıflandırması
- **SIB4 (Intra-frequency)**: Aynı EARFCN üzerinde yer alan komşu hücre PCI listesi ve `q-OffsetCell` parametreleri.
- **SIB5 (Inter-frequency)**: Farklı LTE band ve frekanslarındaki komşu **[[EARFCN]]** listeleri, `cellReselectionPriority` (yeniden seçim önceliği) ve `allowedMeasBandwidth` değerleri.
- **SIB6 (UTRAN - 3G)**: 3G komşu kanalları (**UARFCN**) ve `scramblingCode` (kodlama grupları).
- **SIB7 (GERAN - 2G)**: 2G komşu kanalları (**ARFCN**), `bsic` (Base Station Identity Code) ve `ncc-Permitted` parametreleri.

### B. Komşuluk İlişki Türleri (Topoloji Analizi)
- **Bidirectional (Karşılıklı / Çift Yönlü)**: A hücresi B hücresini komşu gösterirken, B hücresi de kendi SIB yayınında A hücresini (veya A'nın frekansını) komşu olarak duyuruyorsa ilişki karşılıklıdır.
- **Unidirectional (Tek Yönlü)**: Yalnızca bir hücre diğerini komşu olarak yayınlıyor fakat karşı taraf komşuluk listesinde bu hücreyi belirtmiyorsa ilişki tek yönlüdür (asimetrik yük devri veya hatalı konfigürasyon işareti olabilir).
- **Unscanned EARFCNs (Taranmamış Frekanslar)**: SIB5'ten elde edilen komşu EARFCN listesinde yer alan ancak mevcut `cells` veritabanında (taranmış hücreler listesinde) henüz kaydı bulunmayan **yeni keşif kanallarıdır**.

---

## 4. Çıktı Formatı (Output Format - JSON)

Ayrıştırma işlemi sonucunda aşağıdaki yapılandırılmış rapor döner:

```json
{
  "topology_summary": {
    "cells_analyzed": 2,
    "total_intra_freq_neighbors": 0,
    "total_inter_freq_neighbors": 2,
    "total_inter_rat_3g_neighbors": 0,
    "total_inter_rat_2g_neighbors": 0,
    "unscanned_earfcns_count": 2
  },
  "unscanned_earfcns": [1675, 3350],
  "relations": [
    {
      "serving_cell": "Cell_EARFCN1300_PCI45",
      "earfcn": 1300,
      "pci": 45,
      "neighbors": {
        "intra_freq": [],
        "inter_freq": [
          {
            "earfcn": 1675,
            "priority": 6,
            "bandwidth": "mbw100",
            "scanned": false,
            "link_type": "unidirectional"
          }
        ],
        "utran_3g": [],
        "geran_2g": []
      }
    },
    {
      "serving_cell": "Cell_EARFCN1444_PCI82",
      "earfcn": 1444,
      "pci": 82,
      "neighbors": {
        "intra_freq": [],
        "inter_freq": [
          {
            "earfcn": 3350,
            "priority": 7,
            "bandwidth": "mbw100",
            "scanned": false,
            "link_type": "unidirectional"
          }
        ],
        "utran_3g": [],
        "geran_2g": []
      }
    }
  ]
}
```

---

## 5. Hata Yönetimi (Error Management)

- Girdide hiçbir hücre veya SIB verisi bulunamazsa, boş bir `unscanned_earfcns` listesi ve `topology_summary` sıfırlanmış olarak döner.
- `sib5_raw` verisi bulunmayan hücreler analiz edilirken hata verilmez, sadece o hücreye ait inter-freq komşu listesi boş bırakılır.

---

## 6. Kullanım ve Doğrulama Örneği (Verification Test Run)

### Veritabanından Komşu İlişki Okuma
`sib-result-reader` çıktısındaki `sib5_raw` içindeki `interFreqCarrierFreqList` dizileri taranarak `unscanned_earfcns` dizisine eklenir. Zaten taranmış olan `1300`, `1444` gibi EARFCN'ler listeden çıkartılarak net taranacaklar listesi elde edilir.

---

## 7. Wiki Referansları

- [[SIB4]] — Intra-frequency komşuluk teorisi.
- [[SIB5]] — Inter-frequency komşuluk ve EARFCN geçiş detayları.
- [[SIB6]] / [[SIB7]] — 3G ve 2G RAT geçişleri.
- [[Komşu Hücre Analizi]] — Hücre mobilitesi ve topoloji analizi.
