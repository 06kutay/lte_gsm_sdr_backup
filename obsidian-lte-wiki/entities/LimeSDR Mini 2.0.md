---
title: LimeSDR Mini 2.0
source: Lime Microsystems
created_date: 2026-06-01
tags:
  - hardware
  - sdr
  - rf
  - radio
---

# LimeSDR Mini 2.0

**LimeSDR Mini 2.0**, Lime Microsystems tarafından geliştirilen, RF sinyallerini almak ve iletmek (Full Duplex Transceiver) amacıyla kullanılan, yazılım tanımlı radyo (SDR - Software Defined Radio) kartıdır. 

Bu projede [[lte-sib-parser]] aracıyla havadan LTE SIB yayınlarını pasif bir şekilde dinlemek için ana alıcı donanım (receiver) olarak kullanılır.

---

## 1. Donanım Özellikleri

LimeSDR Mini 2.0, orijinal LimeSDR Mini kartının güncellenmiş versiyonudur ve temelde **FTDI FT601 (USB 3.0 controller)** ile **LMS7002M (RF Transceiver)** yongalarını barındırır. Ana fark, FPGA olarak daha gelişmiş bir Lattice ECP5 yongası içermesidir.

### Temel RF Parametreleri
- **Frekans Aralığı**: **10 MHz ile 3.5 GHz** arası. Bu geniş aralık, Türkiye'deki tüm LTE bandlarının ([[LTE Bandlar]] ve [[Frekans Tablosu]]) taranabilmesini sağlar.
- **RF Bant Genişliği (Bandwidth)**: Maksimum **40 MHz**.
- **Kanallar**: 1 TX (İletim), 1 RX (Alım) - FDD çalışmaya uygundur.
- **Örnekleme Hızı (Sample Rate)**: 30.72 MSPS.
- **Güç Beslemesi**: Doğrudan USB 3.0 portundan beslenir.

---

## 2. Anten Portları ve RF Girişleri

Kart üzerinde SMA tipi anten konnektörleri bulunur. RX (Alıcı) tarafında, farklı frekans hassasiyetlerine göre optimize edilmiş 2 adet fiziksel anten kanalı (port seçeneği) mevcuttur:

1.  **LNAH (Low Noise Amplifier High)**: 
    - **Frekans aralığı**: 900 MHz - 3.5 GHz arası yüksek frekanslar için optimize edilmiştir.
    - **Projedeki kullanımı**: Band 1 (2100 MHz), Band 3 (1800 MHz) ve Band 7 (2600 MHz) taramalarında Soapysdr üzerinden `rxant=LNAH` argümanı seçilmelidir.
2.  **LNAW (Low Noise Amplifier Wideband)**:
    - **Frekans aralığı**: Geniş bant aralığı sunar, ancak genellikle alt frekanslara daha duyarlıdır.
    - **Projedeki kullanımı**: Band 20 (800 MHz) ve Band 8 (900 MHz) taramalarında verimi artırmak için `rxant=LNAW` tercih edilebilir.
3.  **LNAL (Low Noise Amplifier Low)**:
    - **Frekans aralığı**: 10 MHz - 900 MHz arası düşük frekanslar için tasarlanmıştır.

> [!TIP]
> Projemizdeki `CLAUDE.md` kurallarına göre, genel taramalar için varsayılan stabil anten parametresi **`-a "rxant=LNAH"`** veya **`LNAW`** olarak sabitlenmiştir.

---

## 3. Host USB Bağlantısı ve Güç Gereksinimleri

LimeSDR Mini 2.0, yoğun veri aktarımı yaptığından mutlaka **USB 3.0 (SuperSpeed)** portuna bağlanmalıdır.
- USB 2.0 portlarında veri taşıma kapasitesi yetersiz kalacağından `srsRAN` ve `cell_search` çalışırken örnek kaçırma (sample drop / overflow `O` veya underflow `U`) hataları oluşur.
- Sanal makine (VM) veya Docker konteynerleri üzerinden erişim sağlanırken USB denetleyicisinin **USB 3.0 / xHCI** olarak seçildiğinden emin olunmalıdır (Detaylar: [[Docker Kurulum]]).

---

## 4. Firmware Güncelleme Adımları

Kartın donanımsal ve yazılımsal uyumluluğunu en üst düzeyde tutmak için host bilgisayar üzerinde `LimeSuite` araçları yüklü olmalıdır.

### A. Cihaz Bağlantısını Doğrulama
```bash
LimeUtil --find
```
Bu komut bağlı olan LimeSDR Mini 2.0 kartını listelemelidir.

### B. Firmware Versiyon Kontrolü ve Güncelleme
Eğer firmware eski ise veya srsRAN kartı tanımakta zorlanıyorsa, internet bağlantısı varken aşağıdaki komutla kartın FPGA ve MCU imajları otomatik olarak en son versiyona güncellenir:
```bash
LimeUtil --update
```

---

## 5. SoapySDR Entegrasyonu

[[srsRAN]] yazılımları LimeSDR donanımıyla doğrudan konuşmak yerine, donanımdan bağımsız bir ara katman olan **SoapySDR** kütüphanesini kullanır.
- Tarama scriptlerimizde kullanılan `-d soapy` parametresi, `srsRAN`'e cihazı Soapy arayüzü üzerinden sürmesini söyler.
- Sürücü tanıma doğrulaması için: `SoapySDRUtil --find="driver=lime"` komutu çalıştırılabilir.
- Cihazın taranamayan veya taranabilen frekans sınırlarını ayrıntılı şekilde incelemek için [[Frekans Tablosu]] sayfasına bakabilirsiniz.
