# 📡 Standalone GSM/2G/3G/4G Neighbor Cell Discovery Tool

Bu dizin, herhangi bir mikroservis mimarisine, Docker konteynerine veya karmaşık gRPC bağımlılıklarına ihtiyaç duymadan **tek başına (standalone)** çalışan hafif bir Python scripti içerir.

Bu script, `gr-gsm` ve `tshark` araçlarını kullanarak:
1. **Geniş Bant Tarama (Mod 1):** Ortamdaki tüm aktif GSM taşıyıcı frekanslarını (ARFCN) otomatik olarak keşfeder.
2. **Kanal Bazlı Çözümleme (Mod 2):** Belirlenen kanalları dinleyerek baz istasyonu kimliklerini (Cell ID, LAC, MCC, MNC, Operatör) çözer.
3. **Komşu Hücre Analizi:** Baz istasyonlarının yayınladığı System Information (SI2, SI3, SI2quater) mesajlarını analiz ederek **2G (GSM), 3G (UMTS) ve 4G (LTE) komşu hücre frekans listesini** çıkarır.

---

## 🛠️ Sistem Bağımlılıkları ve Kurulum

Geliştiricinin veya entegre edecek sistemin üzerinde aşağıdaki paketlerin kurulu olması gerekmektedir:

### 1. Sistem Paketleri (Debian / Ubuntu / Kali)
```bash
sudo apt update
sudo apt install -y gr-gsm tshark python3
```

### 2. Kullanıcı İzinleri (Önemli)
Script, arka planda yerel UDP paketlerini (GSMTAP) yakalamak için `tshark` (Wireshark terminal versiyonu) kullanır. `tshark`'ın sudo şifresi istemeden paket yakalayabilmesi için şu ayarın yapılması önerilir:
```bash
sudo dpkg-reconfigure wireshark-common
# Çıkan ekranda "Yes / Evet" seçin.
sudo usermod -aG wireshark $USER
# Değişikliklerin aktif olması için terminali kapatıp açın veya oturumu yenileyin.
```

---

## 🚀 Kullanım Kılavuzu

### 1. Otomatik Geniş Bant Tarama + Komşu Keşfi (En Basit Kullanım)
Aşağıdaki komut, öncelikle GSM900 bandını otomatik olarak tarar, aktif kanalları bulur ve ardından her aktif kanalı 15 saniye dinleyerek komşu hücre haritasını çıkarır:
```bash
python3 gsm_scan_standalone.py --sdr usrp --serial 2511171 --gain 35 --band GSM900
```
*Eğer LimeSDR kullanılıyorsa:*
```bash
python3 gsm_scan_standalone.py --sdr limesdr --serial 1DBB4CC5EE717D --gain 40 --band GSM900
```

### 2. Sadece Belirli ARFCN Kanallarını Hedefleyerek Dinleme
Frekans taraması yapmadan, doğrudan bilinen belirli ARFCN kanallarını (örneğin ARFCN 60 ve 120) dinlemek ve analiz etmek için:
```bash
python3 gsm_scan_standalone.py 60 120 --sdr usrp --serial 2511171 --gain 35
```

### 3. Ek Parametreler
* `--antenna`: Anten portunu el ile seçmek için kullanılır (örneğin `--antenna TX/RX` veya `--antenna RX2`).
* `--timeout`: Kanal başına dinleme süresi (saniye) (varsayılan: `15`).
* `--output`: Çıktının kaydedileceği JSON dosyası (varsayılan: `gsm_scan_results.json`).

---

## 📊 Örnek Çıktı Formatı (JSON)

Taramadan sonra üretilen JSON dosyası (`gsm_scan_results.json`) aşağıdaki gibi temiz ve yapılandırılmış bir veri modeli sunar. Geliştiriciniz bu veriyi doğrudan kendi veritabanına veya harita sistemine aktarabilir:

```json
{
  "timestamp": "2026-06-10T11:05:00",
  "sdr": {
    "type": "usrp",
    "serial": "2511171",
    "gain": 35,
    "antenna": "TX/RX"
  },
  "scanned_arfcns": [60, 120],
  "cells": [
    {
      "arfcn": 60,
      "band": "GSM900",
      "freq_mhz": 947.0,
      "success": true,
      "cell_id": 7349,
      "lac": 33006,
      "mcc": "286",
      "mnc": "01",
      "operator": "Turkcell",
      "rssi": -64,
      "neighbors_2g": [58, 62, 64],
      "neighbors_3g_uarfcns": [10562, 10587],
      "neighbors_4g_earfcns": [100, 2850, 6400]
    }
  ]
}
```
