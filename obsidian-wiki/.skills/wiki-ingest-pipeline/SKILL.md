---
name: wiki-ingest-pipeline
description: >
  Automates the ingestion of passive LTE scan result JSON databases into structured Obsidian Wiki directories.
  Converts result listings to individual cells, PLMN operators, LTE band summaries, and appends scan details to logs.
  Supports a --dry-run validation flag to preview proposed changes before committing writes.
---

# `wiki-ingest-pipeline` Skill

Bu skill, pasif LTE tarama sonuçlarının [[lte-sib-parser]] SQLite veritabanından çekilip [[dbparsers]] ve [[neighbor-reporter]] aracılığıyla JSON formatına dönüştürüldükten sonra otomatik olarak Obsidian Wiki dizin yapısına aktarılmasını sağlar. 

Kullanıcı müdahalesi olmadan otomatik sayfa oluşturma, güncelleme, akıllı birleştirme (merge), operatör ve band sayfalarını yeniden oluşturma ve index güncelleme adımlarını yürütür.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- `neighbor-reporter` analiz adımı tamamlandıktan sonra sonuçların wikiye yazılması için otomatik olarak zincirlenir.
- Kullanıcı tarama sonuçlarını doğrudan wiki deposuna işlemek istediğinde tetiklenir (örn: *"Tarama verilerini wikiye aktar"*, *"Son tarama sonuçlarını dry-run olarak doğrula"*).

---

## 2. Dizin Yapısı (Target Directory Layout)

Bu skill çalıştırıldığında wiki kasasında (`obsidian-lte-wiki`) aşağıdaki yapıyı oluşturur veya günceller:

- `/cells/` -> Tekil hücre sayfaları (`Cell_EARFCNXXXX_PCIYY.md`)
- `/operators/` -> Operatör özet sayfaları (`Operator_MCC_MNC.md`)
- `/bands/` -> Frekans band özetleri (`Band_X.md`)
- `/logs/` -> Consolidated `Tarama Log.md` ve her tarama için bağımsız `scan_YYYYMMDD_iterX.md` dosyaları.
- `/references/` -> Master [[Komşu Haritası]] tablosu (`Komşu Haritası.md`).
- `/index.md` -> Tüm klasörlerdeki sayfa envanterini sayan otomatik rebuilder.

---

## 3. Parametreler ve Çalıştırma Modları

- **`results_json`** (zorunlu): `wiki_ingest_pipeline.py` tarafından okunacak tam veya göreli JSON sonuç dosyasının yolu.
- **`vault_path`** (zorunlu): Obsidian LTE Wiki kasa dizininin yolu (`/home/mobsec/Desktop/netmon/obsidian-lte-wiki`).
- **`--dry-run`** (opsiyonel): Etkinleştirildiğinde, dosyalar üzerinde hiçbir yazma/değişiklik yapmaz. Sadece gerçekleştirilecek eylemlerin (CREATE/UPDATE/APPEND) listesini yapılandırılmış JSON formatında CLI çıktısı olarak döner.

---

## 4. Kullanım ve Doğrulama Örneği (Dry-Run ve Ingest)

### A. Dry-Run Önizleme Modu
Gerçek bir yazma işlemi yapmadan önce eylemleri doğrulamak için:
```bash
python3 /home/mobsec/Desktop/netmon/obsidian-wiki/scripts/wiki_ingest_pipeline.py /tmp/mock_results.json /home/mobsec/Desktop/netmon/obsidian-lte-wiki --dry-run
```

### B. Gerçek Ingestion Çalıştırması
Tüm dosyaları diske yazmak ve dizinleri güncellemek için:
```bash
python3 /home/mobsec/Desktop/netmon/obsidian-wiki/scripts/wiki_ingest_pipeline.py /tmp/mock_results.json /home/mobsec/Desktop/netmon/obsidian-lte-wiki
```

---

## 5. Hata Yönetimi ve Idempotency Kuralları

- **Mükerrerlik Koruması**: Aynı tarama verisi üst üste çalıştırılsa bile duplicate kayıtlar veya sayfalar oluşmaz. `earfcn + pci` anahtarı ile hücre kimlikleri korunur.
- **Akıllı Birleştirme (Merging)**: Hücre sayfası mevcutsa üzerine yazılmaz. Sadece `last_seen` tarihi güncellenir. Eğer yeni taranan SIB blokları veya TAC değişiklikleri varsa, sayfanın altındaki `## Değişiklik Günlüğü (Changelog)` bölümüne tarih damgasıyla eklenir.

---

## 6. Wiki Referansları

- [[lte-sib-parser]] — SQLite veritabanı şeması.
- [[Sistem Mimarisi]] — RF katmanından wiki bilgi tabanına veri akışı.
- [[Komşu Hücre Analizi]] — Topoloji ve komşu haritası ilişkileri.
