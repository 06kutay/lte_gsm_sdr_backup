---
title: lte-sib-parser
source: /home/mobsec/Desktop/netmon/lte-sib-parser
created_date: 2026-06-01
tags:
  - tool
  - software
  - lte
  - parser
---

# lte-sib-parser

**lte-sib-parser**, radyo frekans (RF) ortamındaki LTE baz istasyonlarının havadan yayınladığı **MIB** ve **SIB1 - SIB13** kontrol mesajlarını (sistem bilgi bloklarını) gerçek zamanlı olarak yakalayıp, çözümleyip (decode) ve yapılandırılmış bir SQLite veritabanına kaydeden, srsRAN tabanlı dockerize edilmiş açık kaynaklı bir araçtır.

Bu araç, hücresel şebeke mobilitesini, operatör frekans yapılanmalarını ve komşu hücre ilişkilerini analiz etmek için tasarlanmıştır.

---

## 1. Mimari ve Çalışma Mekanizması

lte-sib-parser, uçtan uca radyo verisi işleme akışını üç katmanda gerçekleştirir:

1.  **Radyo Sinyali Alımı (SDR Layer)**:
    - [[LimeSDR Mini 2.0]] donanımı vasıtasıyla havadan gelen radyo dalgaları I/Q veri setine dönüştürülür.
    - Soapysdr kütüphanesi yardımıyla sinyaller yazılım katmanına aktarılır.
2.  **Sinyal Arama ve Emülasyon (srsRAN Layer)**:
    - [[srsRAN]] paketinde yer alan `cell_search` modülü ile ortamdaki aktif LTE kanalları ([[EARFCN]] değerleri) taranıp keşfedilir.
    - Ardından, bulunan her bir kanal için `srsue` (UE emülatörü) başlatılarak ilgili baz istasyonunun DL-SCH kanalı dinlenir ve SIB binary paketleri elde edilir.
3.  **Kaydetme ve Raporlama (Parsing Layer)**:
    - eNodeB tarafından yayınlanan binary SIB verileri `srsue` log dosyasına yazılır.
    - [[dbparsers]] altındaki Python parser scriptleri, bu logları yakalayıp ASN.1 standartlarına göre çözerek insan tarafından okunabilir **JSON** formatına çevirir ve SQLite veritabanına yazar.

---

## 2. SQLite Veritabanı Şeması (`cells.sqlite`)

Araç tarafından toplanan tüm hücre ve komşuluk verileri `/vol/output/cells.sqlite` dosyasında saklanır. Veritabanında yer alan `cells` tablosunun ana şeması şöyledir:

- **band**: Çözümlenen hücrenin LTE Bandı (Örn: `3`, `20`).
- **earfcn**: Downlink taşıyıcı frekans numarası ([[EARFCN]]).
- **rsrp**: Sinyal gücü seviyesi (Reference Signal Received Power, dBm cinsinden).
- **mib**: PBCH üzerinden gelen MIB ikili verisi (Bant genişliği vb.).
- **sib1**: PLMN listesi, TAC ve Cell ID içeren [[SIB1]] JSON verisi.
- **sib2**: Genel radyo kaynağı konfigürasyon JSON verisi.
- **sib3**: Yeniden seçim parametrelerini barındıran [[SIB3]] JSON verisi.
- **sib4**: Aynı frekanslı komşu listesini barındıran [[SIB4]] JSON verisi.
- **sib5**: Farklı frekanslı komşu listesini barındıran [[SIB5]] JSON verisi.
- **sib6**: UTRAN (3G) komşu listesini barındıran [[SIB6]] JSON verisi.
- **sib7**: GERAN (2G) komşu listesini barındıran [[SIB7]] JSON verisi.
- **sib8 - sib13**: Diğer özel amaçlı sistem bilgi bloklarının JSON verileri.

---

## 3. Kod Tabanı Yapısı

Dizindeki en kritik dosyalar ve görevleri şunlardır:

- **`vol/sib-scan.sh`**: Tüm akışı yöneten, cell_search ve srsue programlarını koordine eden ana yönetim scriptidir (Ayrıntılı kılavuz için: [[sib-scan.sh]]).
- **`worker/Dockerfile`**: Ubuntu tabanlı, srsRAN ve UHD/SoapySDR bağımlılıklarının derlendiği çok aşamalı Docker dosyası (Detaylar için: [[Docker Kurulum]]).
- **`vol/dbparsers/`**: Veritabanı sorgulamak, analiz yapmak ve komşulukları listelemek için kullanılan Python betikleri (Analiz dökümanı için: [[dbparsers]]).

---

## 4. Kullanım Senaryoları

- **[[Komşu Hücre Analizi]]**: Operatörlerin kapsama alanlarını, reselection öncelik stratejilerini ve band geçiş kurallarını çıkarmak.
- **Kapsama Alanı Doğrulama**: Yeni kurulan baz istasyonlarının veya refarm edilen bandların (örn: 3G'den LTE'ye geçirilen Band 1 frekansları) havadan test edilmesi.
- **Güvenlik Denetimleri**: Çevrede bulunabilecek anormal hücre konfigürasyonlarını veya sahte baz istasyonu (IMSI Catcher) yayılım risklerini analiz etmek.
