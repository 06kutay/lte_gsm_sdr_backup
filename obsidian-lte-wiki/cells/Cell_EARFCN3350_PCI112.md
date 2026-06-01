---
earfcn: 3350
pci: 112
cell_id: 28410293
plmn: "28603"
tac: 54321
band: 7
freq_mhz: 2680.0
tags: ["cell", "lte", "band7"]
first_seen: "2026-06-01 12:56:21"
last_seen: "2026-06-01 12:57:16"
sibs_decoded: ["1", "2", "3", "5"]
---

# Hücre Detayı: Cell_EARFCN3350_PCI112

Bu sayfa, [[lte-sib-parser]] aracıyla yapılan pasif LTE taramalarında keşfedilen hücreye ait SIB parametrelerini ve komşuluk ilişkilerini barındırır.

---

## 1. Hücre Tanımlayıcı Bilgileri (SIB1)
- **Merkez Frekans**: 2680.0 MHz (Band 7 - [[LTE Bandlar]] / [[Frekans Tablosu]])
- **Operatör**: Türk Telekom (MCC-MNC: `286_03`)
- **TAC (Tracking Area Code)**: `54321`
- **Cell Identity (28-bit)**: `28410293`
- **Sinyal Gücü (RSRP)**: `-92 dBm`

---

## 2. Yeniden Seçim Parametreleri (SIB3)
- **Minimum Alım Seviyesi (q-RxLevMin)**: `-116 dBm` (varsayılan)
- **Hücre Seçim Önceliği (cellReselectionPriority)**: `6`

---

## 3. Komşu İlişki Raporu (SIB4/SIB5)
- Komşu Frekans: **[[Cell_EARFCN6200_PCI210]]**
  - Öncelik: `3`
  - Durum: <span style="color: #e65c00; font-weight: bold;">⇒ TEK YÖNLÜ</span>
- Komşu Frekans: **EARFCN 1675**
  - Öncelik: `4`
  - Durum: <span style="color: #ff4d4d; font-weight: bold;">✗ TARANMAMIŞ</span> (Kuyrukta)


---
## 4. Sistem Entegrasyonu
Bu hücre, [[Sistem Mimarisi]] tarama döngüsünde çözümlenmiştir. Detaylı log geçmişi [[Tarama Log]] sayfasında mevcuttur.
