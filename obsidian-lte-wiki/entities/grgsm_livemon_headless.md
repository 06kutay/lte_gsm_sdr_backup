---
title: grgsm_livemon_headless
source: bkerler/gr-gsm GitHub Repository
created_date: 2026-06-02
tags:
  - gsm
  - sdr
  - tool
  - command
---

# grgsm_livemon_headless

**grgsm_livemon_headless**, belirli bir GSM frekansına kilitlenerek havadan gelen mantıksal kontrol paketlerini (BCCH, CCCH vb.) gerçek zamanlı demodüle eden, deşifre eden ve GUI arayüzü olmadan tamamen komut satırı (CLI) üzerinden çalışarak paketleri **[[GSMTAP]]** formatında UDP portuna püskürten bir dinleme (sniffing) aracıdır.

---

## 1. Parametreler ve Argümanlar

Kullanımı: `grgsm_livemon_headless [options]`

| Kısa Parametre | Uzun Parametre | Varsayılan Değer | Açıklama |
| :--- | :--- | :---: | :--- |
| `-f` | `--fc` | `925.8M` | Kilitlenilecek GSM kanalının downlink merkez frekansı (Örn: `947.0e6` veya `947M`). |
| `-g` | `--gain` | `30.0` | RF Alıcı Kazancı (dB cinsinden). LimeSDR için `35` idealdir. |
| `-s` | `--samp-rate` | `2.0M` | Demodülatör giriş örnekleme hızı (GSM için `2.0M` standarttır). |
| `-p` | `--ppm` | `0.0` | SDR donanımsal kristal frekans sapma payı (PPM). |
| `--args` | | `""` | SDR donanım argümanları (Cihaz seçimi için çok önemlidir. Örn: `"driver=lime,serial=1DBB4CC5EE717D"`). |
| `--collector` | | `'localhost'` | Kapsüllenen paketlerin gönderileceği hedef IP/Alan adı. |
| `--collectorport`| | `'4729'` | Paketlerin gönderileceği UDP Portu (Varsayılan [[GSMTAP]] portudur). |
| `-o` | `--shiftoff` | `400.0k` | DC offset'i önlemek için merkez frekanstan kaydırma miktarı. |

---

## 2. Kullanım Örnekleri

### A. LimeSDR ile ARFCN 60 (947.0 MHz) Canlı Dinleme Başlatmak
```bash
grgsm_livemon_headless -f 947.0e6 --args="driver=lime,serial=1DBB4CC5EE717D" -g 35
```

### B. Paketlerin UDP Loopback Portuna Püskürtülmesini İzlemek
grgsm_livemon_headless arka planda çalışırken, `tshark` veya `wireshark` kullanarak loopback arayüzündeki paketleri yakalayabilirsiniz:
```bash
echo "123" | su -c "tshark -i lo -Y gsmtap -c 10"
```

---

## 3. Konsol Çıktısı Analizi

grgsm_livemon_headless, demodüle edip başlıklarını doğruladığı ham mantıksal kontrol paketlerinin (BCCH/CCCH) hex dökümünü konsola yazar:

```text
 15 06 21 00 01 f0 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
 25 06 21 00 05 f4 cb d2 02 18 23 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
 2d 06 22 00 ca e9 b0 94 ee d4 02 aa 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b 2b
```

### Detaylar:
* **`15 06 21`** veya **`25 06`** gibi başlayan paketler GSM standardındaki **LAPDm** (Link Access Protocol on the Dm channel) çerçeveleridir.
* Dolgu (padding) olarak kullanılan **`2b`** (ASCII `+`) karakterleri, GSM havayolu paket boyutunu 23 byte'a tamamlamak için kullanılan dolgu byte'larıdır.
* Bu hex verileri, arkaplandaki soket katmanında doğrudan [[GSMTAP]] başlığı ile sarmalanarak UDP 4729 portundan yayınlanır.

---

## 4. İlgili Bağlantılar
* [[gr-gsm]] — Kütüphane ana yapısı.
* [[grgsm_scanner]] — Baz istasyonunu ve ARFCN frekansını bulmada kullanılan öncü tarayıcı.
* [[GSMTAP]] — Dinlenen paketlerin Wireshark/tshark'a aktarılmasını sağlayan protokol.
* [[Cell_GSM_ARFCN60]] — Canlı dinleme doğrulaması yapılan gerçek baz istasyonu raporu.
