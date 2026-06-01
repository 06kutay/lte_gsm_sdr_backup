---
earfcn: 1444
pci: 82
cell_id: 14285702
plmn: "28601"
tac: 12345
band: 3
freq_mhz: 1829.4
tags: ["cell", "lte", "band3"]
first_seen: "2026-06-01 12:56:21"
last_seen: "2026-06-01 12:57:16"
sibs_decoded: ["1", "2", "3", "5"]
---

# Hücre Detayı: Cell_EARFCN1444_PCI82

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan pasif LTE taramalarında keşfedilen hücreye ait SIB parametrelerini ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SIB1)
- **Merkez Frekans**: 1829.4 MHz (Band 3 - [[LTE Bandlar]] / [[Frekans Tablosu]])
- **Operatör**: Turkcell (MCC-MNC: `286_01`)
- **TAC (Tracking Area Code)**: `12345`
- **Cell Identity (28-bit)**: `14285702`
- **Sinyal Gücü (RSRP)**: `-90 dBm`

---

## 2. Yeniden Seçim Parametreleri (SIB3)
- **Minimum Alım Seviyesi (q-RxLevMin)**: `-116 dBm` (varsayılan)
- **Hücre Seçim Önceliği (cellReselectionPriority)**: `6`

---

## 3. Komşu İlişki Raporu (SIB4/SIB5)
- Komşu Frekans: **[[Cell_EARFCN1300_PCI45]]**
  - Öncelik: `6`
  - Durum: <span style="color: #2ec4b6; font-weight: bold;">⇔ ÇİFT YÖNLÜ</span>
- Komşu Frekans: **[[Cell_EARFCN3350_PCI112]]**
  - Öncelik: `7`
  - Durum: <span style="color: #e65c00; font-weight: bold;">⇒ TEK YÖNLÜ</span>


---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[Tarama Log]] sayfasında mevcuttur.
