---
name: gsmtap-parser
description: >
  Parses live or pcap-captured GSMTAP UDP packets (port 4729) on loopback.
  Implements a primary zero-dependency Python raw socket UDP receiver using struct.unpack to decode the 16-byte GSMTAP header.
  Includes a secondary tshark/Wireshark filter script fallback for deep packet analysis.
---

# `gsmtap-parser` Skill

Bu skill, alıcı SDR'ın (`grgsm_livemon_headless`) loopback arayüzüne (UDP Port `4729`) gerçek zamanlı olarak gönderdiği **GSMTAP** (GSM Test Access Point) paketlerini yakalar ve mantıksal katman deşifresini gerçekleştirir.

Sistem, ortamda `tshark` kurulu olmasa dahi sıfır bağımlılıkla çalışabilmek amacıyla **Python Raw Socket ve `struct.unpack`** mekanizmasını birincil yöntem olarak kullanır. `tshark` ise sadece detaylı protokol analizi ve Layer 3 (RRC) hata ayıklamaları için ikincil fallback olarak kurgulanmıştır.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Canlı `grgsm_livemon_headless` yayını başlatıldıktan sonra loopback arayüzünden akan paketleri gerçek zamanlı deşifre etmek için tetiklenir.
- Bir PCAP dosyasındaki GSMTAP verilerini offline olarak süzmek için tetiklenir.

---

## 2. Birincil Çözüm: Python Raw Socket UDP Alıcısı (Sıfır Bağımlılık)

GSMTAP v2 başlığı standart olarak **16 byte** uzunluğundadır. Python socket kütüphanesi ile UDP 4729 portunu dinleyip, başlığı `struct.unpack` ile şu şekilde ayrıştırırız:

### GSMTAP v2 Başlık Yapısı (16 Bytes)
*   **Version** (1 byte - `B`): GSMTAP sürümü (Genelde `0x02`).
*   **Header Length** (1 byte - `B`): 4-byte'lık kelime cinsinden başlık boyutu (Genelde `0x04` yani 16 byte).
*   **Payload Type** (2 bytes - `H`): `0x01` = GSM Um arayüzü.
*   **Timeslot** (2 bytes - `H`): Mantıksal kanal zaman dilimi ($0 \dots 7$).
*   **ARFCN** (4 bytes - `I`): Kanal numarası (Örn: `60`).
*   **Frame Number** (4 bytes - `I`): GSM çerçeve numarası.
*   **Signal Level** (1 byte - `b`): Sinyal seviyesi (Signed dBm, Örn: `-66`).
*   **SNR** (1 byte - `b`): İşaret/gürültü oranı (Signed dB).
*   **Reserved** (2 bytes - `H`): Rezerve / sub_type alanı.

### Dahili Python Alıcı Kodu (Primary Parser)

Aşağıdaki Python kodu doğrudan çalıştırılarak canlı paketlerin başlığını çözer ve LAPDm payload'unu deşifre edilmesi için dışarı aktarır:

```python
import socket
import struct
import sys

def listen_gsmtap(host="127.0.0.1", port=4729):
    # UDP Soketi Oluştur
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.bind((host, port))
        print(f"[*] GSMTAP UDP listener started on {host}:{port}...")
    except Exception as e:
        print(f"[-] Bind failed: {e}")
        sys.exit(1)

    while True:
        data, addr = sock.recvfrom(2048)
        if len(data) < 16:
            continue
            
        # 16-byte GSMTAP v2 Header Unpack: '!BBHHIIbbH'
        # !: Network byte order (big-endian)
        # B: 1 byte, H: 2 bytes, I: 4 bytes, b: signed 1 byte
        gsmtap_header = data[:16]
        payload = data[16:]
        
        version, hdr_len, payload_type, timeslot, arfcn, frame_num, signal_dbm, snr, reserved = struct.unpack(
            "!BBHHIIbbH", gsmtap_header
        )
        
        if version == 2:
            print(f"[GSMTAP] ARFCN: {arfcn} | TS: {timeslot} | FN: {frame_num} | Signal: {signal_dbm} dBm | Payload: {payload.hex()}")
            # LAPDm deşifre motoruna gönder...

if __name__ == "__main__":
    listen_gsmtap()
```

---

## 3. İkincil Çözüm: tshark Entegrasyonu (Debug Fallback)

Eğer sistemde `tshark` yüklüyse ve System Information (SI2, SI2quater) Layer 3 paketlerinin içerisindeki komşu ARFCN bitmap'lerini tam detaylı olarak insan okuyabilir formatta raporlamak gerekirse şu komut dizisi koşturulur:

```bash
tshark -i lo -f "udp port 4729" -Y "gsmtap" -T fields \
  -e gsmtap.arfcn \
  -e gsmtap.signal_dbm \
  -e gsm_a.ccch \
  -e gsm_a.dtap.cld_cell_spec
```

---

## 4. Çözümlenen Canlı Test Sonuçları (Faz 1)

Canlı ortamda dinlenen ARFCN 60 (947.0 MHz) Turkcell hücresinden yakalanan ham verinin çözümlenmiş çıktı modeli:

*   **Header Analizi:**
    *   `arfcn`: `60`
    *   `signal_dbm`: `-66`
    *   `payload_type`: `1` (GSM Um)
*   **System Information Type 2 (SI2) Deşifresi:**
    *   Yayınlanan BA-List Komşu ARFCN'leri: `48, 54, 55, 56, 57, 58, 59, 61`
*   **System Information Type 3 (SI3) Deşifresi:**
    *   MCC/MNC: `286-01` (Turkcell)
    *   LAC: `33006`
    *   Cell ID: `7349`

---

## 5. Çıktı Şeması (Parsed Output - JSON)

Çözümleyici çalıştıktan sonra komşu analizörüne iletilmek üzere aşağıdaki JSON çıktısını üretir:

```json
{
  "cell_info": {
    "arfcn": 60,
    "freq_mhz": 947.0,
    "signal_dbm": -66,
    "mcc": "286",
    "mnc": "01",
    "lac": 33006,
    "cid": 7349,
    "operator": "Turkcell"
  },
  "neighbors": [48, 54, 55, 56, 57, 58, 59, 60, 61],
  "parser_metadata": {
    "engine": "python_raw_socket",
    "packets_analyzed": 413,
    "status": "SUCCESS"
  }
}
```

---

## 6. Wiki Referansları

- [[GSMTAP]] — Protokol başlık alanları ve UDP yapılandırması.
- [[GSM SI Genel]] — System Information mesaj yapıları.
- [[Cell_GSM_ARFCN60]] — Faz 1 canlı analiz raporu.
