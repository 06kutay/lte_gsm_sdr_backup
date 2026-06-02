---
title: GSMTAP
source: Wireshark Wiki / Osmocom GSMTAP Specification
created_date: 2026-06-02
tags:
  - gsm
  - protocol
  - packet
  - encapsulation
---

# GSMTAP (GSM Terminal Adapter Protocol)

**GSMTAP**, GSM, GPRS, EDGE, UMTS, LTE ve diğer hücresel hava arayüzü (Um, Uu vb.) paketlerinin, yazılım tabanlı alıcılar (SDR) tarafından çözümlendikten sonra standart IP ağları üzerinden Wireshark veya tshark gibi paket analizörlerine aktarılması amacıyla geliştirilmiş bir kapsülleme (encapsulation) protokolüdür.

Dinleme aracı olan [[grgsm_livemon_headless]], çözdüğü tüm GSM mantıksal kontrol kanalı çerçevelerini GSMTAP başlığı ile paketleyerek varsayılan **UDP 4729** portundan loopback arayüzüne (127.0.0.1) püskürtür.

---

## 1. GSMTAP v2 Başlık (Header) Yapısı

GSMTAP başlığı sabit **16 byte (128 bit)** boyutundadır. Büyük-soncul (Big-endian / Network Byte Order) bayt düzenindedir. Başlık yapısı aşağıdaki byte offset tablosunda detaylandırılmıştır:

| Byte Offset | Bit Aralığı | Alan Adı | Tip | Değer / Açıklama |
| :---: | :---: | :--- | :---: | :--- |
| **0** | 0 - 7 | `version` | `uint8_t` | GSMTAP Sürümü (Genellikle `0x02` veya `0x01`). |
| **1** | 8 - 15 | `hdr_len` | `uint8_t` | Byte cinsinden GSMTAP başlık uzunluğu (v2 için `0x10` = 16 byte). |
| **2** | 16 - 23 | `type` | `uint8_t` | Kapsüllenen hava arayüzü tipi:<br>`0x01`: GSM Um (Hava arayüzü)<br>`0x02`: GSM Abis<br>`0x03`: GSM A-arayüzü<br>`0x0f`: LTE. |
| **3** | 24 - 31 | `timeslot` | `uint8_t` | Çerçevenin alındığı TDMA Zaman Dilimi (Timeslot, `0 - 7`). |
| **4 - 5** | 32 - 47 | `arfcn` | `uint16_t` | Kanal Numarası (Bit 15 Uplink/Downlink bayrağıdır; `1`: UL, `0`: DL). |
| **6** | 48 - 55 | `signal_dbm` | `int8_t` | Alınan sinyal gücü seviyesi (dBm cinsinden negatif işaretli tamsayı). |
| **7** | 56 - 63 | `snr_db` | `int8_t` | Sinyal-Gürültü Oranı (SNR, dB cinsinden). |
| **8 - 11** | 64 - 95 | `frame_number` | `uint32_t` | GSM TDMA Kare Sayısı (TDMA Frame Number). |
| **12** | 96 - 103 | `sub_type` | `uint8_t` | Mantıksal Kanal Türü:<br>`0x01`: BCCH (Yayın)<br>`0x02`: CCCH (Ortak Kontrol)<br>`0x03`: SDCCH (Yavaş DCCH)<br>`0x08`: TCH/F (Trafik Full). |
| **13** | 104 - 111 | `antenna_nr` | `uint8_t` | Paket yakalamanın yapıldığı fiziksel anten port numarası. |
| **14 - 15** | 112 - 127 | `padding` | `uint16_t` | 32-bit hizalama için boş byte'lar (`0x0000`). |

---

## 2. Pasif Paket Analiz ve Ayrıştırma (Parse) Mantığı

UDP 4729 portundan loopback IP'sine akan bu paketler, wireshark/tshark tarafından otomatik algılanır. Tshark bu paketleri yakalayıp çözümlerken en dıştan en içe doğru şu katmanları soyar:

```text
+-------------------------------------------------------------+
| Ethernet / Loopback Başlığı (lo)                            |
+-------------------------------------------------------------+
| IP Başlığı (Kaynak: 127.0.0.1, Hedef: 127.0.0.1)            |
+-------------------------------------------------------------+
| UDP Başlığı (Hedef Port: 4729)                              |
+-------------------------------------------------------------+
| GSMTAP v2 Başlığı (16 Byte, ARFCN, Timeslot, Sinyal vb.)    |
+-------------------------------------------------------------+
| LAPDm Başlığı (Link Access Protocol on Dm)                  |
+-------------------------------------------------------------+
| GSM L3 Kontrol Mesajı (System Information / CCCH Payload)   |
+-------------------------------------------------------------+
```

---

## 3. Tshark ile Canlı GSMTAP Analiz Komutları

### A. Canlı Akışı Ekranda Göstermek
Frekansa kilitlenmiş bir [[grgsm_livemon_headless]] çalışırken aşağıdaki komut ile deşifre edilmiş mantıksal kontrol mesajlarını okuyabiliriz:
```bash
echo "123" | su -c "tshark -i lo -Y gsmtap"
```

### B. Paketleri Analiz Filtreleriyle Süzmek (Örnekler)
* **Sadece System Information Mesajlarını Listeleme:**
  ```bash
  echo "123" | su -c "tshark -i lo -Y 'gsmtap && gsm_a.dtap'"
  ```
* **Sadece SDCCH Kanallarını İzleme:**
  ```bash
  echo "123" | su -c "tshark -i lo -Y 'gsmtap.sub_type == 3'"
  ```

---

## 4. İlgili Bağlantılar
* [[gr-gsm]] — Kütüphane ana yapısı.
* [[grgsm_livemon_headless]] — GSMTAP yayınını üreten araç.
* [[GSM Komsu Analizi]] — Komşu hücre tespiti ve SI yapıları.
