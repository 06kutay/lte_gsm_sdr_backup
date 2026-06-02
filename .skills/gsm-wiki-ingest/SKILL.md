---
name: gsm-wiki-ingest
description: >
  Automates the ingestion of passive GSM scan result JSON listings into structured Obsidian Wiki directories.
  Creates or updates cells under cells/Cell_GSM_ARFCN<num>.md and registers them in index.md.
  Supports smart merging of last_seen dates and changes logs to maintain idempotency.
---

# `gsm-wiki-ingest` Skill

Bu skill, pasif GSM tarama sonuçlarının ve çözümlenen komşu hücre ilişkilerinin otomatik olarak Obsidian Wiki dizin yapısına aktarılmasını sağlar. 

Kullanıcı müdahalesi olmadan otomatik sayfa oluşturma, güncelleme, akıllı birleştirme (merge) ve `index.md` dizin envanterini güncelleme adımlarını yürütür. LTE tarafındaki `wiki-ingest-pipeline` skill'inin doğrudan 2G karşılığıdır.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- `gsm-neighbor-reporter` analiz adımı tamamlandıktan sonra sonuçların wikiye yazılması için otomatik olarak zincirlenir.
- Kullanıcı tarama sonuçlarını doğrudan wiki deposuna işlemek istediğinde tetiklenir (örn: *"GSM tarama verilerini wikiye aktar"*, *"Son GSM hücresini wikiye kaydet"*).

---

## 2. Hedef Dizin Yapısı (Target Directory Layout)

Bu skill çalıştırıldığında wiki kasasında (`obsidian-lte-wiki`) aşağıdaki yapıyı oluşturur veya günceller:

- `/cells/` $\rightarrow$ Tekil hücre sayfaları (`Cell_GSM_ARFCN<num>.md`)
- `/index.md` $\rightarrow$ Keşfedilen Canlı Hücreler (Discovered Cells) listesini güncelleyen master rebuilder.

---

## 3. Akıllı Birleştirme ve Idempotency Kuralları

- **Mükerrerlik Koruması (Idempotency):** Aynı tarama verisi üst üste çalıştırılsa bile duplicate kayıtlar veya sayfalar oluşmaz. Hücreler benzersiz `ARFCN` numarası ile saklanır.
- **Akıllı Birleştirme (Merging):** Hücre sayfası mevcutsa üzerine yazılmaz. Sadece `last_seen` tarihi frontmatter'da güncellenir. 
- **Değişiklik Günlüğü (Changelog):** Eğer yeni taranan komşularda bir değişiklik varsa (örn. yeni bir komşu eklenmesi veya çıkarılması), sayfanın altındaki `## Değişiklik Günlüğü (Changelog)` bölümüne tarih damgasıyla eklenir.

---

## 4. Kullanım ve Doğrulama Örneği (Faz 1 Canlı Veri Ingestion)

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

### Yürütülen Adımlar:
1.  **Hücre Dosyası Oluşturma:** `/home/mobsec/Desktop/netmon/obsidian-lte-wiki/cells/Cell_GSM_ARFCN60.md` dosyası oluşturulur (veya mevcutsa birleştirilir).
2.  **Ön Bilgi ve Frontmatter Yazımı:**
    ```yaml
    ---
    title: Cell GSM ARFCN60
    source: Pasif gr-gsm Tarama Sonuçları
    created_date: 2026-06-02
    last_seen: 2026-06-02
    tags:
      - gsm
      - cell
      - turkcell
    ---
    ```
3.  **İçerik Doldurma:** `gsm-neighbor-reporter` tarafından üretilen tablo ve özet kartları hücre sayfasına eklenir. `[[gr-gsm]]`, `[[GSM SI2]]` ve `[[GSM Frekans Tablosu]]` wikilinkleri otomatik yerleştirilir.
4.  **Index Güncellemesi:** `/home/mobsec/Desktop/netmon/obsidian-lte-wiki/index.md` dosyası okunur ve `### 📡 Keşfedilen Canlı Hücreler (Discovered Cells)` başlığı altına eğer yoksa `* [[Cell_GSM_ARFCN60]]` satırı eklenir.

---

## 5. Wiki Referansları

- [[GSM vs LTE Komşu Tespiti]] — Eşdeğer parametre haritası.
- [[GSM Komsu Analizi]] — BA listesi çözme mekanizmaları.
- [[index]] — Güncellenen master indeks sayfası.
