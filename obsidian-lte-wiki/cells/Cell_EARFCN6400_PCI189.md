---
earfcn: 6400
pci: 189
cell_id: 8848917
plmn: "28601"
tac: 8481
band: 20
freq_mhz: 816.0
tags: ["cell", "lte", "band20"]
first_seen: "2026-06-01 13:51:47"
last_seen: "2026-06-01 14:56:56"
sibs_decoded: ["1", "2", "3", "5"]
---

# Hücre Detayı: Cell_EARFCN6400_PCI189

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan pasif LTE taramalarında keşfedilen hücreye ait SIB parametrelerini ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SIB1)
- **Merkez Frekans**: 816.0 MHz (Band 20 - [[LTE Bandlar]] / [[Frekans Tablosu]])
- **Operatör**: Turkcell (MCC-MNC: `286_01`)
- **TAC (Tracking Area Code)**: `8481`
- **Cell Identity (28-bit)**: `8848917`
- **Sinyal Gücü (RSRP)**: `-61.3 dBm`

---

## 2. Yeniden Seçim Parametreleri (SIB3)
- **Minimum Alım Seviyesi (q-RxLevMin)**: `-116 dBm` (varsayılan)
- **Hücre Seçim Önceliği (cellReselectionPriority)**: `6`

---

## 3. Komşu İlişki Raporu (SIB4/SIB5)
- Komşu Frekans: **[[Cell_EARFCN2850_PCI192]]**
  - Öncelik: `6`
  - Durum: <span style="color: #e65c00; font-weight: bold;">⇒ TEK YÖNLÜ</span>
- Komşu Frekans: **[[Cell_EARFCN100_PCI265]]**
  - Öncelik: `5`
  - Durum: <span style="color: #2ec4b6; font-weight: bold;">⇔ ÇİFT YÖNLÜ</span>
- Komşu Frekans: **EARFCN 550**
  - Öncelik: `5`
  - Durum: <span style="color: #ff4d4d; font-weight: bold;">✗ TARANMAMIŞ</span> (Kuyrukta)
- Komşu Frekans: **EARFCN 1651**
  - Öncelik: `5`
  - Durum: <span style="color: #ff4d4d; font-weight: bold;">✗ TARANMAMIŞ</span> (Kuyrukta)
- Komşu Frekans: **EARFCN 1795**
  - Öncelik: `5`
  - Durum: <span style="color: #ff4d4d; font-weight: bold;">✗ TARANMAMIŞ</span> (Kuyrukta)


---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[Tarama Log]] sayfasında mevcuttur.
