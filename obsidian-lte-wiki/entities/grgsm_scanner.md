---
title: grgsm_scanner
source: bkerler/gr-gsm GitHub Repository
created_date: 2026-06-02
tags:
  - gsm
  - sdr
  - tool
  - command
---

# grgsm_scanner

**grgsm_scanner**, belirtilen GSM bandındaki aktif kontrol kanallarını (C0/BCCH frekansları) tespit eden, baz istasyonlarının yayınladığı sistem ve ağ parametrelerini çözerek analiz eden bir komut satırı aracıdır.

---

## 1. Parametreler ve Argümanlar

Kullanımı: `grgsm_scanner [options]`

| Kısa Parametre | Uzun Parametre | Varsayılan Değer | Açıklama |
| :--- | :--- | :---: | :--- |
| `-b` | `--band` | `GSM900` | Taranacak GSM bandını belirtir. Sadece şu bantlar geçerlidir: `GSM900`, `DCS1800`, `GSM850`, `PCS1900`, `GSM450`, `GSM480`, `GSM-R`. |
| `-g` | `--gain` | `24.0` | Alıcı RF kazancı (dB cinsinden). LimeSDR için `30.0` - `40.0` arası idealdir. |
| `-s` | `--samp-rate` | `2e6` | Örnekleme hızı (Sadece `çift_sayı * 0.2e6` değerleri alabilir. Örn: `2e6`, `4e6`). |
| `-p` | `--ppm` | `0` | SDR donanımsal frekans kayması düzeltmesi (PPM cinsinden). |
| `--args` | | `""` | SDR donanım argümanları (Cihaz seçimi için çok önemlidir. Örn: `"driver=lime,serial=1DBB4CC5EE717D"`). |
| `--speed` | | `15` | Tarama hızı katsayısı (0 - 29 aralığı). Hız yükseldikçe her frekanstaki dinleme süresi kısalır. |
| `-v` | `--verbose` | `False` | Ayrıntılı mod. Hücre içi ARFCN'leri ve komşu ARFCN listelerini ekrana yazdırır. |
| `-d` | `--debug` | `False` | Hata ayıklama modunu açar ve tüm C++ / Python loglarını görüntüler. |

---

## 2. Kullanım Örnekleri

### A. LimeSDR ile GSM900 Bandında Ayrıntılı Tarama Yapmak
```bash
grgsm_scanner --args="driver=lime,serial=1DBB4CC5EE717D" -g 35 -b GSM900 -v
```

### B. DCS1800 Bandında Yüksek Hızlı Tarama Yapmak
```bash
grgsm_scanner --args="driver=lime,serial=1DBB4CC5EE717D" -g 35 -b DCS1800 --speed=25
```

---

## 3. Çıktı Formatı Analizi

Aktif bir hücre bulunduğunda grgsm_scanner konsola şu formatta çıktı verir:

```text
ARFCN:   60, Freq:  947.0M, CID:  7349, LAC: 33006, MCC: 286, MNC:   1, Pwr: -66
  |---- Configuration: 1 CCCH, not combined
  |---- Cell ARFCNs: 5, 60
  |---- DCCHs:
  |-------- #1 SDCCH/8, Timeslot: 1, Training Sequence: 5, MAIO: 0, HSN: 32, A5/1 Version: 1
  |---- Neighbour Cells: 48, 54, 55, 56, 57, 58, 59, 60, 61
```

### Parametre Deşifreleri:
* **ARFCN**: Baz istasyonunun C0 (BCCH ana taşıyıcı) frekans kanal numarasıdır.
* **Freq**: Downlink merkez frekansı (MHz). (ARFCN 60 için $935.0 + 0.2 \times 60 = 947.0$ MHz).
* **CID (Cell Identity)**: Hücrenin benzersiz 16-bit kimlik numarası (Hücre ID).
* **LAC (Location Area Code)**: Bulunduğu konum alan kodu.
* **MCC (Mobile Country Code)**: Ülke kodu (Türkiye için `286`).
* **MNC (Mobile Network Code)**: Operatör kodu (`01`: Turkcell, `02`: Vodafone, `03`: Türk Telekom).
* **Pwr (Power)**: Sinyal seviyesi (dBm). ($-66$ dBm güçlü bir sinyale işaret eder).
* **Configuration**: CCCH (Ortak Kontrol Kanalı) düzenini bildirir (Combined veya Non-combined).
* **Cell ARFCNs**: Hücrenin frekans atlama (Frequency Hopping) listesinde kendine tahsis ettiği kanallar.
* **Neighbour Cells**: Baz istasyonunun [[GSM SI2]] paketinde MS'e bekleme modunda izlemesini söylediği komşu ARFCN kanalları.

---

## 4. İlgili Bağlantılar
* [[gr-gsm]] — Kütüphane ana yapısı.
* [[grgsm_livemon_headless]] — Canlı dinleme aracı.
* [[GSM Bandlar]] — Türkiye operatör frekans aralıkları ve ARFCN dağılımları.
* [[Cell_GSM_ARFCN60]] — Faz 1'deki gerçek tarama sonucunun analiz raporu.
