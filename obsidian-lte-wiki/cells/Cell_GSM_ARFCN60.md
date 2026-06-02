---
arfcn: 60
band: "GSM900"
freq_mhz: 947.0
cell_id: 7349
lac: 33006
mcc: 286
mnc: 1
operator_name: "Turkcell"
rssi_dbm: -64
tags: ["gsm", "cell", "turkcell"]
first_seen: "2026-06-02 10:32:09"
last_seen: "2026-06-02 11:31:07"
---

# GSM Hücre Detayı: Cell_GSM_ARFCN60

Bu sayfa, [[gr-gsm]] aracıyla yapılan pasif GSM taramalarında keşfedilen hücreye ait System Information (SI) parametrelerini, kanal yapılandırmalarını ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SI3)
- **Merkez Frekans**: 947.0 MHz (Band GSM900 - [[GSM Bandlar]] / [[GSM Frekans Tablosu]])
- **Operatör**: Turkcell (MCC-MNC: `286_01`)
- **LAC (Location Area Code)**: `33006`
- **Cell Identity (16-bit)**: `7349`
- **Sinyal Seviyesi (RSSI)**: `-64 dBm`

---

## 2. Kanal Yapılandırması (Control & Traffic Channels)
- **CCCH Config**: `1 CCCH, not combined`
- **Cell ARFCNs (Frekans Atlama Listesi)**: `[60]`
- **SDCCH Config (Adanmış Kontrol Kanalı)**:
  - Tip: `SDCCH/8`, Timeslot: `1`, TSC: `5`, MAIO: `0`, HSN: `32`
- **A5 Şifreleme Versiyonu**: `A5/1` (Aktif Ses/Veri Güvenliği)

---

## 3. Komşu Hücre İlişkileri (SI2 / SI2quater)

### A. 2G GSM Komşuları (SI2 BA Listesi)
Kaynak baz istasyonu tarafından yayınlanan SI2 bekleme listesindeki komşu ARFCN'ler:

| Komşu ARFCN | Frekans Bandı | Downlink Frekansı | Spektrum Operatör Tahmini | Rol / Durum |
| :---: | :---: | :---: | :---: | :--- |
| **48** | GSM900 | 944.6 MHz | Turkcell | ARFCN 48 (henüz taranmamış) |
| **54** | GSM900 | 945.8 MHz | Turkcell | ARFCN 54 (henüz taranmamış) |
| **55** | GSM900 | 946.0 MHz | Turkcell | ARFCN 55 (henüz taranmamış) |
| **56** | GSM900 | 946.2 MHz | Turkcell | ARFCN 56 (henüz taranmamış) |
| **57** | GSM900 | 946.4 MHz | Turkcell | ARFCN 57 (henüz taranmamış) |
| **58** | GSM900 | 946.6 MHz | Turkcell | ARFCN 58 (henüz taranmamış) |
| **59** | GSM900 | 946.8 MHz | Turkcell | ARFCN 59 (henüz taranmamış) |
| **60** | GSM900 | 947.0 MHz | Turkcell | [[Cell_GSM_ARFCN60]] |
| **61** | GSM900 | 947.2 MHz | Turkcell | ARFCN 61 (henüz taranmamış) |


---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[GSM Tarama Log]] sayfasında mevcuttur.
