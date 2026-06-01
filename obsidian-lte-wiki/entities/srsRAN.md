---
title: srsRAN
source: SRS (Software Radio Systems)
created_date: 2026-06-01
tags:
  - software
  - lte
  - sdr
  - radio
---

# srsRAN_4G

**srsRAN_4G** (eski adıyla srsLTE), Software Radio Systems (SRS) firması tarafından geliştirilen, SDR (Yazılım Tanımlı Radyo) kartları üzerinde çalışan, tamamen yazılımsal ve açık kaynaklı bir 4G/5G hücresel haberleşme protokol yığınıdır (protocol stack).

Bu projede [[lte-sib-parser]] aracının kalbini oluşturan iki ana srsRAN bileşeni kullanılmaktadır: **`cell_search`** ve **`srsue`**.

---

## 1. cell_search: Hızlı Baz İstasyonu Keşfi

`cell_search`, srsRAN paketinde yer alan, RF ortamındaki aktif LTE hücrelerini ve kanallarını çok hızlı bir şekilde taramak için optimize edilmiş pasif bir analiz aracıdır.

### Çalışma Prensibi
1.  **Frekans Tarama**: Belirli bir LTE Bandı ([[LTE Bandlar]]) veya EARFCN aralığında RF spektrumunu dinler.
2.  **Senkronizasyon Sinyallerinin Çözülmesi**:
    - **PSS (Primary Synchronization Signal)**: Sinyal üzerinden 5 ms'lik alt çerçeve sınırını yakalar ve fiziksel hücre kimliği (PCI) grubunun alt indeksini ($N_{ID}^{(2)} \in \{0, 1, 2\}$) belirler.
    - **SSS (Secondary Synchronization Signal)**: 10 ms'lik radyo çerçevesi sınırını yakalar ve hücre kimliği grup indeksini ($N_{ID}^{(1)} \in \{0, 1, \dots, 167\}$) belirler.
3.  **PCI Hesaplama**: Yakalanan PSS ve SSS sinyallerinden nihai Fiziksel Hücre Kimliği (PCI) hesaplanır:
    $$\text{PCI} = 3 \times N_{ID}^{(1)} + N_{ID}^{(2)}$$
    Toplamda 504 adet benzersiz PCI ($0 \dots 503$) değeri üretilebilir.
4.  **MIB Okuma**: PBCH kanalı üzerinden hücrenin Downlink bant genişliğini ve PHICH konfigürasyonunu okur.

Tarayıcı scriptimiz [[sib-scan.sh]], cell_search programını arka planda çalıştırarak ortamdaki aktif [[EARFCN]] değerlerini otomatik olarak tespit eder.

---

## 2. srsue: Kullanıcı Ekipmanı Emülatörü ve SIB Yakalama

`srsue`, srsRAN şebekesinde tam fonksiyonlu bir mobil cihaz (UE - User Equipment) gibi davranan yazılımsal protokol yığınıdır. Katman 1 (Physical), Katman 2 (MAC, RLC, PDCP) ve Katman 3 (RRC, NAS) protokollerini tamamen host işlemcisi üzerinde koordine eder.

### Projedeki Rolü ve Pasif Dinleme (TX Off)
Normalde bir UE baz istasyonuna bağlanmak için sinyal gönderir (Uplink/TX aktiftir). Ancak [[lte-sib-parser]] projesinde mobil cihazın **verici (TX) gücü tamamen kapatılmıştır**. 
- `srsue`, baz istasyonuna hiçbir sinyal göndermeden, tamamen **pasif (passive monitoring)** modda çalışır.
- Yalnızca baz istasyonunun Downlink yayınını (Broadcast) dinler.
- BCCH (Broadcast Control Channel) kanalından akan tüm **MIB** ve **[[SIB Genel]] (SIB1-13)** paketlerini yakalar ve `/tmp/ue.log` dosyasına kaydeder.
- Bu log dosyası daha sonra Python parserlar tarafından JSON formatına dönüştürülerek SQLite veritabanına işlenir.

---

## 3. SoapySDR ve LimeSDR Entegrasyonu

srsRAN araçları, radyo kartıyla iletişim kurmak için **SoapySDR** kütüphanesini kullanır. 
- `cell_search` çalışırken:
  ```bash
  cell_search -b 3 -a "rxant=LNAH" -d soapy -g 35
  ```
- `srsue` çalışırken (ue.conf üzerinden veya inline argümanlarla):
  ```bash
  srsue --rf.device_name soapy --rf.device_args "rxant=LNAH" --rf.rx_gain 35
  ```
  parametreleriyle [[LimeSDR Mini 2.0]] kartını kontrol eder.

---

## 4. Kritik Konfigürasyon Dosyaları

lte-sib-parser veritabanında yer alan `/vol/helpers/ue.conf` dosyası, `srsue`'nun çalışmasını optimize eden parametreleri barındırır:
- **`expert.lte_sample_rates = true`**: LimeSDR Mini'nin standart dışı LTE örnekleme hızlarını (standard sampling rates) zorlayarak RF senkronizasyonunun kaybolmasını engeller.
- **`log.filename = /tmp/ue.log`**: parserın okuyacağı ham SIB verilerinin yazılacağı log dosyasıdır.
- **`log.all_level = info` / `rrc_level = info`**: SIB çözme loglarının detay seviyesini ayarlar.
