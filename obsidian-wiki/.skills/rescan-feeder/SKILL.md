---
name: rescan-feeder
description: >
  Drives the recursive scan feedback loop. Takes the 'unscanned_earfcns' from neighbor-reporter,
  filters out already scanned channels, validates new targets using earfcn-validator, and builds subsequent
  docker-compose scan commands using sib-scan-builder with incremented iteration counters.
---

# `rescan-feeder` Skill

Bu skill, [[Sistem Mimarisi]] katmanında yer alan rekürsif tarama döngüsünün beynidir. `neighbor-reporter` çıktısındaki `unscanned_earfcns` listesini alır, daha önceki iterasyonlarda zaten taranmış olan kanalları temizler (mükerrer taramayı önler), kalan yeni kanalları sırasıyla `earfcn-validator` ve `sib-scan-builder`'dan geçirerek **bir sonraki iterasyonun tarama komutunu** oluşturur.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- `neighbor-reporter` analizi tamamlandıktan sonra taranmamış yeni komşu kanalları (`unscanned_earfcns`) keşfedildiğinde (örn: *"Bir sonraki iterasyon tarama komutunu hazırla"*, *"Döngüsel keşif sürecini sürdür"*).
- Bir tarama sonrasında recursive keşfi bir sonraki adıma taşımak için tetiklenir.

---

## 2. Girdi Formatı (Input Format - JSON)

Mevcut veritabanındaki taranmış hücre listesini, `neighbor-reporter` çıktısını ve mevcut iterasyon sayısını girdi olarak kabul eder:

```json
{
  "scanned_earfcns": [1300, 1444, 3350, 6200],
  "unscanned_earfcns": [1675],
  "current_iteration": 1,
  "options": {
    "gain": 35,
    "timeout": 30
  }
}
```

---

## 3. Akış ve Döngü Yönetimi Mantığı

1.  **Deduplication (Temizleme)**: `unscanned_earfcns` listesi içinden `scanned_earfcns` listesinde yer alan elemanlar tamamen çıkartılır.
2.  **Döngü Sonlanma Durumu (Termination State)**: 
    - Eğer filtrelenmiş yeni taranacak frekans listesi **boş ise**:
      > "Keşif tamamlandı! {current_iteration} iterasyonda toplam {len(scanned_earfcns)} benzersiz hücre keşfedildi ve çözümlendi."
3.  **İterasyon Kontrolü**: İterasyon sayacı bir artırılır (`current_iteration + 1`).
4.  **Doğrulama ve İnşa**:
    - Uyumlu olan kanallar için `sib-scan-builder` çağrılır. `sib-scan-builder` kanalların frekansına göre otomatik olarak `-a "rxant=LNAH"` (>=1.5 GHz) veya `-a "rxant=LNAW"` (<1.5 GHz) portunu seçerek `_iter{new_iteration}` eki ile yeni SQLite dosyasına kaydedecek şekilde komutu inşa eder:
      - SQLite: `/vol/output/scan_YYYYMMDD_iter2.sqlite`
      - Komut: `./sib-scan.sh -d soapy -a "rxant=LNAH" -g 35 -t 30 -D /vol/output/scan_20260601_iter2.sqlite -q "1675"`

---

## 4. Çıktı Formatı (Output Format - JSON)

Skill çalıştırıldığında döngü durumunu, yeni iterasyon numarasını, yeni taranacak frekansları ve çalıştırılması gereken yeni komutu döner:

```json
{
  "status": "rescan_required",
  "message": "1. İterasyon tamamlandı. Keşfedilen yeni komşu EARFCN'ler için 2. İterasyon taraması başlatılıyor.",
  "new_iteration": 2,
  "earfcns_to_scan": [1675],
  "target_bands": [3],
  "generated_command": "./sib-scan.sh -d soapy -a \"rxant=LNAH\" -g 35 -t 30 -T 30 -D /vol/output/scan_20260601_iter2.sqlite -q \"1675\"",
  "docker_run_instruction": "docker-compose run --rm worker ./sib-scan.sh -d soapy -a \"rxant=LNAH\" -g 35 -t 30 -T 30 -D /vol/output/scan_20260601_iter2.sqlite -q \"1675\""
}
```

Eğer yeni EARFCN kalmadıysa:

```json
{
  "status": "discovery_completed",
  "message": "Keşif tamamlandı! 2 iterasyonda 5 benzersiz hücre başarıyla taranarak veritabanına işlendi.",
  "total_iterations": 2,
  "total_cells_discovered": 5
}
```

---

## 5. Hata Yönetimi (Error Management)

- Girdi parametrelerindeki `current_iteration` eksik ise varsayılan olarak `1` kabul edilir.
- `scanned_earfcns` veya `unscanned_earfcns` listesi geçersiz veya eksik formatta verilirse döngü durdurulur ve hata basılır.

---

## 6. Kullanım ve Doğrulama Örneği (Verification Test Run)

Komşu analizi sonrasında `unscanned_earfcns` içinde `1675` kalırsa, bu skill otomatik olarak `docker-compose run --rm worker ./sib-scan.sh ... -D /vol/output/scan_20260601_iter2.sqlite -q "1675"` komutunu üreterek sistem yöneticisinin tek tıkla ikinci iterasyonu yapmasını sağlar.

---

## 7. Wiki Referansları

- [[Sistem Mimarisi]] — Uçtan uca rekürsif veri akışı.
- [[sib-scan.sh]] — Orkestrasyon parametreleri.
- [[EARFCN]] — EARFCN frekans doğrulama.
