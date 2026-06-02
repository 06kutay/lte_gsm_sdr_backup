---
name: gsm-scan-builder
description: >
  Builds structured shell commands for executing grgsm_scanner and grgsm_livemon_headless.
  Manages LimeSDR Mini 2.0 parameters like gain, serial, and correct anten port (LNAW vs LNAH).
  Handles SDR device access concurrency by stopping/starting the SRSENB service.
---

# `gsm-scan-builder` Skill

Bu skill, kullanıcının talepleri doğrultusunda **`grgsm_scanner`** (aktif hücreleri tarama) ve **`grgsm_livemon_headless`** (tek bir hücreyi canlı dinleme ve GSMTAP yayını yapma) araçları için parametrik ve donanım uyumlu kabuk (shell) komut dizileri oluşturur.

Aynı zamanda **SDR aygıt erişim çakışmalarını** önlemek için arka plan servis yönetimini ve frekansa göre fiziksel anten portu (`LNAW` / `LNAH`) eşleştirme kurallarını yönetir.

---

## 1. Tetiklenme Koşulları (Trigger Conditions)

- Kullanıcı canlı bir GSM dinleme veya genel bant taraması yapmak istediğinde (örn: *"947.0 MHz hücresini dinlemek için komut oluştur"*, *"SDR kazancı 35 olan bir GSM taraması hazırla"*).
- `arfcn-validator` adımı tamamlanıp taranacak frekanslar/kanallar kesinleştikten sonra zincirlenir.

---

## 2. SDR Cihaz Erişim ve Concurrency Yönetimi

Sistemde iki adet LimeSDR Mini ünitesi bulunmakta olup, birincil SDR (`1DBB802FAD4EFE`) sürekli olarak arka planda çalışan `waiting-room-enb` (LTE eNodeB) servisi tarafından kilitlenmiş durumdadır. İkinci LimeSDR Mini (`1DBB4CC5EE717D`) ise taramalar için serbest durumdadır.

Donanım kilitlenmelerini engellemek için şu kurallar uygulanır:
1. **İkinci SDR'ı Hedefleme:** Komutlarda mutlaka `--args="driver=lime,serial=1DBB4CC5EE717D"` parametresi kullanılmalıdır.
2. **Hücre Servisini Geçici Durdurma (Opsiyonel / Concurrency Çakışması Varsa):** Eğer serbest olan donanıma da erişim sorunu yaşanırsa, eNodeB servisini durdurmak için şu komut hazırlanır:
   ```bash
   echo "123" | su -c "systemctl stop waiting-room-enb"
   ```
3. **Servisi Geri Açma:** İşlem tamamlandığında, LTE test hücresini tekrar yayına almak için şu komut hazır tutulur:
   ```bash
   echo "123" | su -c "systemctl start waiting-room-enb"
   ```

---

## 3. Frekansa Göre Anten Portu Seçim Kuralları

LimeSDR Mini 2.0 üzerinde iki adet RX portu bulunur. Tarama yapılacak frekans sınırına göre anten portu seçimi komuta veya donanım kılavuzuna eklenmelidir:
* **Frekans $< 1.5$ GHz (GSM-900 / ARFCN 1 - 124):** Geniş / Alçak Frekans anten portu olan **`LNAW`** seçilir.
* **Frekans $\ge 1.5$ GHz (DCS-1800 / ARFCN 512 - 885):** Yüksek Frekans anten portu olan **`LNAH`** seçilir.

---

## 4. Komut Üretim Kuralları ve Canlı Test Örnekleri (Faz 1)

### A. `grgsm_scanner` (Baz İstasyonu Arama Komutu)
* **Görevi:** GSM-900 bandında aktif taşıyıcıları (C0) tarar.
* **Girdiler:** Kazanç (Gain) = `35`, Donanım = LimeSDR `1DBB4CC5EE717D`.
* **Üretilen Komut:**
  ```bash
  grgsm_scanner --args="driver=lime,serial=1DBB4CC5EE717D" -g 35 -b GSM900
  ```

### B. `grgsm_livemon_headless` (Canlı Dinleme ve GSMTAP Aktarım Komutu)
* **Görevi:** Merkez frekansı 947.0 MHz (ARFCN 60) olan hücreyi dinler ve loopback UDP 4729 portuna GSMTAP kontrol paketleri gönderir.
* **Girdiler:** Frekans = `947.0e6` (947.0 MHz), Kazanç = `35`, Donanım = LimeSDR `1DBB4CC5EE717D`.
* **Üretilen Komut:**
  ```bash
  grgsm_livemon_headless -f 947.0e6 --args="driver=lime,serial=1DBB4CC5EE717D" -g 35
  ```

---

## 5. Çıktı Şeması (Output Command Object - JSON)

Komut oluşturucu skill, hedeflenen kabuk eylemlerini içeren yapılandırılmış bir JSON objesi döner:

```json
{
  "stop_conflict_service": "echo \"123\" | su -c \"systemctl stop waiting-room-enb\"",
  "scan_command": "grgsm_scanner --args=\"driver=lime,serial=1DBB4CC5EE717D\" -g 35 -b GSM900",
  "sniff_command": "grgsm_livemon_headless -f 947.0e6 --args=\"driver=lime,serial=1DBB4CC5EE717D\" -g 35",
  "start_conflict_service": "echo \"123\" | su -c \"systemctl start waiting-room-enb\"",
  "hardware": {
    "serial": "1DBB4CC5EE717D",
    "rx_port": "LNAW",
    "optimal_gain": 35
  }
}
```

---

## 6. Wiki Referansları

- [[grgsm_scanner]] — Detaylı CLI parametreleri.
- [[grgsm_livemon_headless]] — Canlı dinleme parametreleri ve portları.
- [[LimeSDR Mini 2.0]] — SDR donanım ve anten port detayları.
