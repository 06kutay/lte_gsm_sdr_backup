---
title: Docker Kurulum
source: /home/mobsec/Desktop/netmon/lte-sib-parser/worker/Dockerfile, docker-compose.yml
created_date: 2026-06-01
tags:
  - docker
  - installation
  - virtualization
  - hardware-access
---

# Docker Kurulumu ve Donanım Geçiş (USB Passthrough) Kılavuzu

[[lte-sib-parser]] aracı, düşük seviyeli donanım sürücüleri (UHD, SoapySDR, LimeSuite) ve C++ tabanlı [[srsRAN]] protokol yığınını içerdiğinden, derleme karmaşıklığını önlemek ve host işletim sistemini kirletmemek adına **Docker** konteyner yapısı içerisinde çalıştırılır.

Bu dökümanda, çok aşamalı Docker imaj derlemesi, konteyner mimarisi ve en kritik konu olan SDR cihazının hosttan konteynere kesintisiz aktarılması (**USB Passthrough**) adımları açıklanmıştır.

---

## 1. Çok Aşamalı (Multi-stage) Dockerfile Derleme Adımları

`/home/mobsec/Desktop/netmon/lte-sib-parser/worker/Dockerfile` dosyası, srsRAN_4G projesini `sib_logger.patch` yaması uygulanmış şekilde sıfırdan derler. Derleme adımları şu şekildedir:

1.  **Temel İmaj**: `ubuntu:22.04` (Stabil C++ derleyici ve kütüphane desteği için).
2.  **Bağımlılıkların Kurulması**: Derleme için gerekli araçlar (`cmake`, `make`, `gcc`, `g++`, `git`) ile SDR kütüphaneleri (`libsoapysdr-dev`, `libuhd-dev`, `soapysdr-module-lms7`) kurulur.
3.  **srsRAN_4G Klonlama**: `srsRAN_4G` reposu klonlanır.
4.  **Yamalama (Patching)**: SIB paketlerinin binary olarak çözülüp loglanmasını sağlayan `sib_logger.patch` yaması repo üzerine uygulanır.
5.  **Derleme ve Kurulum**: CMake ile proje yapılandırılarak `make -j$(nproc)` ile işlemci çekirdek sayısı oranında paralel derlenir ve `/usr/local/bin` altına kurulur.
6.  **Yardımcı Araçlar**: `cell_search` binary dosyası hızlı erişim için `/usr/bin/` altına kopyalanır.
7.  **Giriş Noktası (Entrypoint)**: Başlangıçta UHD cihaz imajlarını kopyalayan ve ardından interaktif bash kabuğu başlatan ENTRYPOINT betiği kurulur.

---

## 2. Docker Compose Konfigürasyonu (`docker-compose.yml`)

Konteynerin çalıştırılması, gerekli hacim (volume) eşlemeleri ve donanım yetkilendirmeleri doğrudan `docker-compose.yml` dosyası üzerinden yönetilir:

```yaml
version: '3'
services:
  worker:
    build: 
      context: ./worker
      dockerfile: Dockerfile
    image: lte-sib-parser_worker:latest
    container_name: lte-sib-parser_worker
    privileged: true
    network_mode: "host"
    volumes:
      - ./vol:/vol
    devices:
      - "/dev/bus/usb:/dev/bus/usb"
    restart: unless-stopped
    stdin_open: true
    tty: true
```

---

## 3. Donanım Yetkilendirme ve USB Passthrough Mantığı

SDR cihazları ([[LimeSDR Mini 2.0]]) host işletim sistemine fiziksel USB portu üzerinden bağlanır. Docker konteynerinin bu USB cihazlarına doğrudan erişebilmesi ve sinyal kaybı (overflow/underflow) yaşamadan yüksek hızda veri transferi yapabilmesi için iki temel ayar yapılmıştır:

### A. Ayrıcalıklı Mod (`privileged: true`)
Konteynere host sistemin tüm çekirdek yetenekleri (root yetkileri ve donanım kontrol yetkileri) verilir. Bu parametre olmadan konteyner içindeki srsRAN doğrudan hostun RF donanım saatine ve USB arabirimlerine müdahale edemez.

### B. USB Aygıt Eşlemesi (`/dev/bus/usb:/dev/bus/usb`)
Host işletim sistemindeki tüm USB veri yolları (`/dev/bus/usb`) doğrudan konteyner içine aynı yolla map edilir. 
- Bu sayede hosta LimeSDR kartı takıldığında veya çıkarıldığında, konteyner içindeki `SoapySDR` veya `LimeSuite` sürücüleri donanımı anında algılar.
- Host üzerinde `udev` kurallarının ayarlanması veya konteynerin yeniden başlatılması gerekmez.

### C. Network Mod (`network_mode: "host"`)
Konteynerin ağ arabirimleri sanallaştırılmadan doğrudan hostun ağ kartıyla eşleştirilir. Bu durum, srsue'nun ağ bağlantılarını test etmek ve potansiyel olarak host ağ kaynaklarını gecikmesiz kullanmak için gereklidir.

---

## 4. Konteyneri Yönetme Komutları

### İmajı Derlemek (Build)
```bash
# lte-sib-parser dizininde
echo "123" | su -c 'docker-compose build' root
```

### Konteyneri Başlatmak ve Giriş Yapmak (Run & Attach)
```bash
echo "123" | su -c 'docker-compose run --rm worker' root
```
*Bu komut konteyneri başlatır, LimeSDR USB geçişini sağlar ve sizi doğrudan tarama yapabileceğiniz interaktif `/vol` çalışma dizinine sokar.*

### Konteyner İçinde Donanımı Doğrulama
Konteyner içerisine girdiğinizde, SDR donanımının başarıyla algılandığından emin olmak için şu komutları koşturabilirsiniz:
```bash
# SoapySDR üzerinden LimeSDR Mini'yi sorgulama
SoapySDRUtil --find="driver=lime"

# srsRAN araçlarının donanıma erişebildiğini doğrulama
cell_search --help
```

- Konteyner içinde tarama başlatmak için [[sib-scan.sh]] scriptinin parametrelerini inceleyebilirsiniz.
- Çözümlenen verilerin nasıl işlendiğini görmek için [[dbparsers]] sayfasına göz atabilirsiniz.
- Sistemin genel akışını görmek için ise [[Sistem Mimarisi]] dökümanına başvurabilirsiniz.
