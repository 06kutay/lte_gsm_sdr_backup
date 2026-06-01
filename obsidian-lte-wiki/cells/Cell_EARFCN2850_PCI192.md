---
earfcn: 2850
pci: 192
cell_id: 8848920
plmn: "28601"
tac: 8481
band: 7
freq_mhz: 2630.0
tags: ["cell", "lte", "band7"]
first_seen: "2026-06-01 13:51:47"
last_seen: "2026-06-01 14:56:56"
sibs_decoded: ["1", "2", "3"]
---

# Hücre Detayı: Cell_EARFCN2850_PCI192

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan pasif LTE taramalarında keşfedilen hücreye ait SIB parametrelerini ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SIB1)
- **Merkez Frekans**: 2630.0 MHz (Band 7 - [[LTE Bandlar]] / [[Frekans Tablosu]])
- **Operatör**: Turkcell (MCC-MNC: `286_01`)
- **TAC (Tracking Area Code)**: `8481`
- **Cell Identity (28-bit)**: `8848920`
- **Sinyal Gücü (RSRP)**: `-73.8 dBm`

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
