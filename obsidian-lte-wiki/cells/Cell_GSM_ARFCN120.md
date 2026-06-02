---
arfcn: 120
band: "GSM900"
freq_mhz: 959.0
cell_id: 16528
lac: 50602
mcc: 286
mnc: 2
operator_name: "Vodafone TR"
rssi_dbm: -71
tags: ["gsm", "cell", "vodafone"]
first_seen: "2026-06-02 11:31:07"
last_seen: "2026-06-02 11:31:07"
---

# GSM Hücre Detayı: Cell_GSM_ARFCN120

Bu sayfa, [[gr-gsm]] aracıyla yapılan pasif GSM taramalarında keşfedilen hücreye ait System Information (SI) parametrelerini, kanal yapılandırmalarını ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SI3)
- **Merkez Frekans**: 959.0 MHz (Band GSM900 - [[GSM Bandlar]] / [[GSM Frekans Tablosu]])
- **Operatör**: Vodafone TR (MCC-MNC: `286_02`)
- **LAC (Location Area Code)**: `50602`
- **Cell Identity (16-bit)**: `16528`
- **Sinyal Seviyesi (RSSI)**: `-71 dBm`

---

## 2. Kanal Yapılandırması (Control & Traffic Channels)
- **CCCH Config**: `1 CCCH, not combined`
- **Cell ARFCNs (Frekans Atlama Listesi)**: `[120]`
- **SDCCH Config (Adanmış Kontrol Kanalı)**:
  - Tip: `SDCCH/8`, Timeslot: `1`, TSC: `4`, MAIO: `0`, HSN: `0`
- **A5 Şifreleme Versiyonu**: `A5/1` (Aktif Ses/Veri Güvenliği)

---

## 3. Komşu Hücre İlişkileri (SI2 / SI2quater)

### A. 2G GSM Komşuları (SI2 BA Listesi)
Kaynak baz istasyonu tarafından yayınlanan SI2 bekleme listesindeki komşu ARFCN'ler:

| Komşu ARFCN | Frekans Bandı | Downlink Frekansı | Spektrum Operatör Tahmini | Rol / Durum |
| :---: | :---: | :---: | :---: | :--- |
| - | - | - | - | - |


---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[GSM Tarama Log]] sayfasında mevcuttur.
