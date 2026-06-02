# GSM Komşu Hücre Analiz Sistemi

## Araçlar
- **gr-gsm**: GNU Radio 3.10 tabanlı GSM alıcı/tarayıcı seti (`bkerler/gr-gsm` fork'u derlenmiştir).
  - `grgsm_scanner`: Aktif CCCH kanallarını ve komşu ARFCN listelerini bulur.
  - `grgsm_livemon_headless`: Belirli bir frekansı dinleyip havadan yakaladığı paketleri GSMTAP formatında yayınlar.
- **SDR**: LimeSDR Mini 2.0
  - Cihaz parametreleri: `--args="driver=lime,serial=1DBB4CC5EE717D"` veya `"--args="driver=lime,serial=1DBB802FAD4EFE"`
- **tshark**: Loopback arayüzünde UDP 4729 portundan akan GSMTAP paketlerini yakalar ve deşifre eder.
- **Obsidian Wiki**: `/home/mobsec/Desktop/netmon/obsidian-lte-wiki` (Karpathy LLM Wiki Pattern)

## Temel Akış
grgsm_scanner ile C0 aktif kanal bulma → ARFCN ve frekans belirleme → grgsm_livemon_headless'ı arka planda başlatma → UDP 4729 loopback GSMTAP yayını → tshark ile pcap formatında canlı doğrulama → Sonuçları wiki'ye aktarma.

## Komut Kullanımı

### 1. Aktif Kanal Tarama (GSM900)
```bash
grgsm_scanner --args="driver=lime,serial=1DBB4CC5EE717D" -g 35 -b GSM900
```

### 2. Belirli Bir Frekansta Canlı Dinleme (GSMTAP Yayını)
```bash
grgsm_livemon_headless -f 947.0e6 --args="driver=lime,serial=1DBB4CC5EE717D" -g 35
```

### 3. GSMTAP Paket Yakalama (Tshark)
```bash
# Canlı terminalde 10 paket yakalayıp ekrana yazdırır
echo "123" | su -c "tshark -i lo -Y gsmtap -c 10"

# 10 saniye boyunca UDP 4729 portundaki paketleri PCAP dosyasına yazar
echo "123" | su -c "timeout 10 tshark -i lo -f 'udp port 4729' -w /tmp/gsm_capture.pcap"
```

## Kurallar
- **SDR Kaynak Yönetimi**: Tarama veya dinleme işlemleri tamamlandığında arka planda kalan `python3` ve `grgsm_*` süreçlerini kesinlikle sonlandırın (`kill -9`).
- **SDR Kilitleme Önlemi**: LTE enb servisi (`waiting-room-enb`) aktifken LimeSDR `1DBB802FAD4EFE` ünitesini meşgul eder. GSM taramasından önce gerekiyorsa servisi durdurun (`systemctl stop waiting-room-enb`), işiniz bitince tekrar başlatın.
- **Wiki Entegrasyonu**: Bulunan tüm yeni GSM hücreleri ve komşu ARFCN ilişkileri Obsidian Wiki üzerindeki `concepts/GSM Komsu Analizi.md` ve ilgili dosyalara eklenerek cross-link edilmelidir.
