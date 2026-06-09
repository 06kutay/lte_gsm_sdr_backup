---
name: sib-scan-builder
description: >
  Generates a ready-to-execute sib-scan.sh command to run inside the lte-sib-parser Docker container.
  Requires the output of earfcn-validator, taking only 'valid' EARFCNs with 'hw_ok: true'.
  Supports custom parameters for gain, timeout, recursive mode, and database names with date-stamps.
---

# `sib-scan-builder` Skill

Bu skill, `earfcn-validator` tarafından doğrulanmış ve donanım açısından uyumlu (`hw_ok: true`) olarak işaretlenmiş EARFCN listesini girdi olarak alır ve [[lte-sib-parser]] Docker konteyneri içinde çalıştırılacak en uygun **`sib-scan.sh`** komutunu otomatik olarak oluşturur.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Kullanıcı doğrulanmış bir EARFCN listesiyle tarama başlatmak istediğinde (örn: *"Doğrulanan kanallar için tarama komutunu oluştur"*, *"Özel gain=35 ve rekürsif kapalı olacak şekilde tarama hazırla"*).
- `earfcn-validator` çıktısı alındıktan sonra zincirleme işlem olarak çağrılır.

---

## 2. Girdi Formatı (Input Format - JSON)

Girdi olarak `earfcn-validator` çıktısını (özellikle `valid` listesini) ve kullanıcının opsiyonel tarama tercihlerini kabul eder:

```json
{
  "validator_output": {
    "valid": [
      {"earfcn": 1300, "band": 3, "freq_mhz": 1815.0, "bw": "20MHz", "hw_ok": true},
      {"earfcn": 1444, "band": 3, "freq_mhz": 1829.4, "bw": "20MHz", "hw_ok": true},
      {"earfcn": 3350, "band": 7, "freq_mhz": 2680.0, "bw": "20MHz", "hw_ok": true},
      {"earfcn": 6200, "band": 20, "freq_mhz": 796.0, "bw": "10MHz", "hw_ok": true}
    ]
  },
  "options": {
    "gain": 35,
    "timeout": 30,
    "extra_timeout": 30,
    "recursive": true,
    "iteration": 1
  }
}
```

---

## 3. Çalışma ve Komut Oluşturma Mantığı

1.  **Filtreleme**: Sadece `hw_ok: true` olan geçerli EARFCN'leri listeler (Örn: `1300, 1444, 3350, 6200`).
2.  **Band Analizi**: Listelenen EARFCN'lerin hangi LTE bandlarına ait olduğunu çıkarır. Eğer **birden fazla band** varsa (Örn: Band 3, Band 7, Band 20), kullanıcıya şu şekilde bilgi notu verir:
    > "UYARI: Tarama listeniz birden fazla band içeriyor (Band 3, 7, 20). SDR anten kazancı ve LNA port seçimi her band için optimize edilmelidir!"
3.  **Tarih Damgalı Veritabanı Adı**: SQLite dosya ismi o anki tarih baz alınarak oluşturulur.
    - Format: `/vol/output/scan_YYYYMMDD.sqlite`
    - Eğer iterasyon degeri belirtilmişse (Örn: `iteration: 2`): `/vol/output/scan_YYYYMMDD_iter2.sqlite`
4.  **Komut Sentezi**:
    - **Frekans-Bazlı Otomatik Anten Seçimi**: Girdi EARFCN kanallarının hesaplanan downlink frekansı (`freq_mhz`) 1.5 GHz (1500 MHz) ve üzerinde ise otomatik olarak `-a "rxant=LNAH"` (Band 1/3/7 için yüksek band portu), 1.5 GHz altında ise `-a "rxant=LNAW"` (Band 20/8 için düşük band portu) seçilir.
    - Parametre eşleştirmeleri:
      - `-g <gain>` (varsayılan: 30)
      - `-t <timeout>` (varsayılan: 30)
      - `-T <extra_timeout>` (varsayılan: 30)
      - Rekürsif mod kapalı ise: `-n` eklenir. (Varsayılan olarak rekürsif mod açıktır, parametre eklenmez).
      - `-D <db_path>` (varsayılan: `/vol/output/scan_YYYYMMDD.sqlite`)
      - `-q "<EARFCN listesi>"` şeklinde taranacak kanallar gönderilir.

---

## 4. Çıktı Formatı (Output Format - JSON)

Skill çalıştırıldığında kullanıcıya taranacak bandların analizini, oluşturulan tam komutu ve Docker üzerinde çalıştırma talimatını içeren bir JSON ve açıklama döner:

```json
{
  "target_bands": [3, 7, 20],
  "multi_band_warning": true,
  "database_file": "/vol/output/scan_20260601.sqlite",
  "generated_command": "./sib-scan.sh -d soapy -a \"rxant=LNAH\" -g 35 -t 30 -T 30 -D /vol/output/scan_20260601.sqlite -q \"1300 1444 3350 6200\"",
  "docker_run_instruction": "docker-compose run --rm worker ./sib-scan.sh -d soapy -a \"rxant=LNAH\" -g 35 -t 30 -T 30 -D /vol/output/scan_20260601.sqlite -q \"1300 1444 3350 6200\""
}
```

---

## 5. Hata Yönetimi (Error Management)

- Girdide `valid` veya `hw_ok: true` olan hiçbir EARFCN bulunamadığında komut oluşturulamaz ve `"Hata: Komut oluşturmak için donanım uyumlu geçerli EARFCN bulunamadı!"` hatası döner.
- `options` objesi boş gelse bile sistem hata vermez, tüm parametreleri güvenli varsayılan değerlerle (gain: 30, timeout: 30, recursive: true) başlatır.

---

## 6. Kullanım ve Doğrulama Örneği (Verification Test Run)

### Girdi
Doğrulanmış gerçek test kanalları listesi: `1300` (Band 3), `1444` (Band 3), `3350` (Band 7), `6200` (Band 20).
- Opsiyonlar: `gain: 35`, `timeout: 30`, `recursive: true`.

### Üretilen Talimat ve Komut
```bash
docker-compose run --rm worker ./sib-scan.sh -d soapy -a "rxant=LNAH" -g 35 -t 30 -T 30 -D /vol/output/scan_20260601.sqlite -q "1300 1444 3350 6200"
```

---

## 7. Wiki Referansları

- [[sib-scan.sh]] — Script detayları ve tüm parametre kılavuzu.
- [[Docker Kurulum]] — Konteyner çalıştırma ve USB geçiş yetkileri.
- [[Sistem Mimarisi]] — Tarama katmanı akış dökümantasyonu.
