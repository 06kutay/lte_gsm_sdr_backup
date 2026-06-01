---
earfcn: 6200
pci: 210
cell_id: 98721201
plmn: "28603"
tac: 54321
band: 20
freq_mhz: 796.0
tags: ["cell", "lte", "band20"]
first_seen: "2026-06-01 12:56:21"
last_seen: "2026-06-01 12:57:16"
sibs_decoded: ["1", "2", "3"]
---

# Hücre Detayı: Cell_EARFCN6200_PCI210

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan pasif LTE taramalarında keşfedilen hücreye ait SIB parametrelerini ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SIB1)
- **Merkez Frekans**: 796.0 MHz (Band 20 - [[LTE Bandlar]] / [[Frekans Tablosu]])
- **Operatör**: Türk Telekom (MCC-MNC: `286_03`)
- **TAC (Tracking Area Code)**: `54321`
- **Cell Identity (28-bit)**: `98721201`
- **Sinyal Gücü (RSRP)**: `-99 dBm`

---

## 2. Yeniden Seçim Parametreleri (SIB3)
- **Minimum Alım Seviyesi (q-RxLevMin)**: `-116 dBm` (varsayılan)
- **Hücre Seçim Önceliği (cellReselectionPriority)**: `6`

---

## 3. Komşu İlişki Raporu (SIB4/SIB5)
*Komşu hücre listesi bulunmuyor veya SIB5 çözümlenemedi.*

---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[Tarama Log]] sayfasında mevcuttur.
