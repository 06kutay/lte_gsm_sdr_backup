# GSM Komşu Hücre Analiz Sistemi — Referans Kılavuzu

Bu doküman, GSM (Global System for Mobile Communications) komşu hücre analiz ve dinleme sistemi için tasarlanmış teorik formülleri, System Information (SI) yapılarını, frekans dağılımlarını, SDR parametrelerini ve GSMTAP protokol yapısını içermektedir.

---

## 1. GSM Frekans ve ARFCN Hesaplama Formülleri

GSM standardında uplink ve downlink kanalları **ARFCN** (Absolute Radio Frequency Channel Number) ile belirlenir. Kanal aralığı (channel spacing) **200 kHz (0.2 MHz)** düzeyindedir.

### 1.1 GSM-900 Bandı (P-GSM & E-GSM)
* **P-GSM (Primary GSM 900):** $1 \le n \le 124$
  * Uplink: $F_{UL}(n) = 890.0 + 0.2 \times n$
  * Downlink: $F_{DL}(n) = F_{UL}(n) + 45.0 = 935.0 + 0.2 \times n$
* **E-GSM (Extended GSM 900):** $0 \le n \le 124$ veya $975 \le n \le 1023$
  * $0 \le n \le 124$:
    * Uplink: $F_{UL}(n) = 890.0 + 0.2 \times n$
    * Downlink: $F_{DL}(n) = 935.0 + 0.2 \times n$
  * $975 \le n \le 1023$:
    * Uplink: $F_{UL}(n) = 890.0 + 0.2 \times (n - 1024)$
    * Downlink: $F_{DL}(n) = 935.0 + 0.2 \times (n - 1024)$

### 1.2 DCS-1800 Bandı
* Kanal aralığı: $512 \le n \le 885$
  * Uplink: $F_{UL}(n) = 1710.2 + 0.2 \times (n - 512)$
  * Downlink: $F_{DL}(n) = F_{UL}(n) + 95.0 = 1805.2 + 0.2 \times (n - 512)$

### 1.3 GSM-850 Bandı
* Kanal aralığı: $128 \le n \le 251$
  * Uplink: $F_{UL}(n) = 824.2 + 0.2 \times (n - 128)$
  * Downlink: $F_{DL}(n) = F_{UL}(n) + 45.0 = 869.2 + 0.2 \times (n - 128)$

### 1.4 PCS-1900 Bandı
* Kanal aralığı: $512 \le n \le 810$
  * Uplink: $F_{UL}(n) = 1850.2 + 0.2 \times (n - 512)$
  * Downlink: $F_{DL}(n) = F_{UL}(n) + 80.0 = 1930.2 + 0.2 \times (n - 512)$

---

## 2. GSM Komşu Hücre Tespiti ve System Information (SI) Mesaj Tipleri

GSM şebekelerinde komşu hücre bilgileri baz istasyonları tarafından belirli **System Information (SI)** mesajları ile yayınlanır. Bu mesajlar mobil istasyona (MS) hangi frekansları izlemesi gerektiğini bildirir.

| SI Tipi | Kanal | Durum | Açıklama |
| :--- | :--- | :--- | :--- |
| **SI 2** | BCCH | IDLE | Ana BA (BCCH Allocation) listesini içerir. Mobil cihaz bekleme modundayken bu listedeki ARFCN'leri izler. |
| **SI 2bis** | BCCH | IDLE | E-GSM veya ek frekanslar sebebiyle BA listesi tek bir SI2'ye sığmadığında gönderilir. |
| **SI 2ter** | BCCH | IDLE | Çoklu bant ortamlarında DCS-1800 / PCS-1900 komşu hücre ARFCN listelerini taşır. |
| **SI 5** | SACCH | DEDICATED | Cihaz aktif bir çağrıda (Dedicated mode) iken dinlemesi gereken BA listesini içerir. |
| **SI 5bis** | SACCH | DEDICATED | Aktif modda BA listesinin sığmadığı durumlarda ek frekansları taşır. |
| **SI 5ter** | SACCH | DEDICATED | Aktif modda çoklu bant (DCS-1800) komşu hücre frekans listesini içerir. |

---

## 3. Türkiye GSM Operatörleri Frekans Dağılımı

Türkiye'deki üç ana operatörün GSM-900 ve DCS-1800 bantlarındaki yaklaşık ARFCN dağılımları aşağıda listelenmiştir.

| Operatör | MCC / MNC | GSM-900 ARFCN Aralığı | DCS-1800 ARFCN Aralığı |
| :--- | :--- | :--- | :--- |
| **Turkcell** | 286 / 01 | 1 - 35 | 662 - 736 |
| **Vodafone TR** | 286 / 02 | 36 - 70 | 512 - 586 |
| **Türk Telekom** | 286 / 03 | 71 - 105 | 587 - 661 |

---

## 4. SDR Donanımsal Özellikleri ve Konfigürasyonu

Analiz sisteminde kullanılan SDR (Software Defined Radio) ünitelerinin genel karakteristikleri şu şekildedir:

### 4.1 LimeSDR Mini 2.0
* **Frekans Aralığı:** 10 MHz - 3.5 GHz
* **Maksimum Bant Genişliği (Sample Rate):** 40 MSPS
* **RF Kanalları:** 1 TX, 1 RX (LMS7002M entegresi)
* **Anten Seçimi:**
  * `LNAH` (High Band): $\ge 1.5$ GHz sinyaller için (DCS-1800 / PCS-1900)
  * `LNAW` (Wide Band): $< 1.5$ GHz sinyaller için (GSM-900 / GSM-850)
* **Sürücü Altyapısı:** `SoapySDR` (lime), `LimeSuite`

### 4.2 USRP B205mini-i
* **Frekans Aralığı:** 70 MHz - 6.0 GHz
* **Maksimum Bant Genişliği (Sample Rate):** 61.44 MSPS
* **RF Kanalları:** 1 TX, 1 RX (AD9364 entegresi)
* **Sürücü Altyapısı:** `UHD` (Universal Hardware Driver)

---

## 5. GSMTAP Protokol Yapısı

**GSMTAP** (GSM Terminal Adapter Protocol), GSM ve diğer hücresel protokol hava arayüzü (Um) paketlerini UDP üzerinden kapsülleyerek Wireshark ve tshark gibi paket analizörlerine aktarmaya yarar. Paketin varsayılan portu **4729 (UDP)**'dur.

### 5.1 GSMTAP v2 Başlık (Header) Yapısı
GSMTAP başlığı sabit **16 byte** boyutundadır ve aşağıdaki alanlardan oluşur:

| Byte Offset | Boyut | Alan Adı | Açıklama |
| :---: | :---: | :--- | :--- |
| 0 | 1 | `version` | GSMTAP Versiyonu (Genellikle `0x02`) |
| 1 | 1 | `hdr_len` | Başlık Boyutu (v2 için 16'dır: `0x10`) |
| 2 | 1 | `type` | Kapsüllenen Protokol Tipi (`0x01`: GSM Um, `0x02`: GSM Abis) |
| 3 | 1 | `timeslot` | Havadan yakalanan burst'ün zaman dilimi (0 - 7) |
| 4 - 5 | 2 | `arfcn` | Kanal Numarası (Bit 15 Uplink/Downlink bayrağıdır) |
| 6 | 1 | `signal_dbm` | Sinyal Seviyesi (dBm cinsinden negatif değer) |
| 7 | 1 | `snr_db` | Sinyal-Gürültü Oranı (dB cinsinden) |
| 8 - 11 | 4 | `frame_number` | GSM TDMA Kare Numarası (Multi-frame sayacı) |
| 12 | 1 | `sub_type` | Kanal Alt Tipi (`0x01`: BCCH, `0x02`: CCCH, `0x03`: SDCCH, `0x08`: TCH/F) |
| 13 | 1 | `antenna_nr` | Verinin alındığı anten kanalı |
| 14 - 15 | 2 | `padding` | Hizalama için boş alan (0x0000) |

---

## 6. gr-gsm Derleme ve Kurulum Detayları
Sistem GNU Radio 3.10.5.1 altyapısı üzerine derlenmiştir.
* **Kullanılan Fork:** `bkerler/gr-gsm` (GNU Radio 3.10 ve PyBind11 tam uyumlu)
* **Bağımlılıklar:** `libosmocoding`, `libosmodsp`, `libgnuradio-osmosdr`
* **Kurulum Dizinleri:**
  * İkili Dosyalar (Binaries): `/usr/local/bin/` (`grgsm_livemon_headless`, `grgsm_scanner`, `grgsm_decode`)
  * Python Paketleri: `/usr/local/lib/python3.11/dist-packages/gnuradio/gsm`
