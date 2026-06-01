---
title: SIB5
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - mobility
---

# SIB5 (System Information Block Type 5)

**SIB5**, LTE sistemindeki **Farklı Frekanslı (Inter-frequency)** komşu hücrelerin bilgilerini taşıyan sistem bilgi bloğudur. Cihazın bağlı olduğu mevcut servis hücresinden farklı bir [[EARFCN]] (frekans kanalı) değerindeki komşu LTE hücrelerini tanımlar.

[[Komşu Hücre Analizi]] sürecinde operatörün frekans katmanları arasındaki geçiş stratejilerini (örneğin 800 MHz kapsama katmanından 1800 MHz kapasite katmanına geçiş kuralları) gösterdiği için en kritik SIB olarak kabul edilir.

---

## 1. Kritik Parametreler ve Anlamları

SIB5, `InterFreqCarrierFreqList` adı verilen bir liste yapısı barındırır. Her bir inter-frequency komşu taşıyıcı (carrier) için şu kritik parametreler yayınlanır:

- **dl-CarrierFreq (EARFCN)**: Komşu LTE taşıyıcısının Downlink [[EARFCN]] değeri.
- **allowedMeasBandwidth**: Komşu hücrelerin ölçümü sırasında cihazın kullanabileceği maksimum bant genişliği (6, 15, 25, 50, 75 veya 100 kaynak bloğu - RB).
- **cellReselectionPriority**: Komşu frekansın yeniden seçim öncelik değeridir (0 ile 7 arası). Cihaz her zaman en yüksek öncelikli frekanstaki hücreye bağlanmaya çalışır.
- **q-RxLevMin**: Komşu frekanstaki hücrelere bağlanabilmek için gereken minimum RSRP sinyal gücü.
- **threshX-High**: Mevcut servis hücresinin kalitesinden bağımsız olarak, cihazın daha yüksek öncelikli bu komşu frekansa geçmesi için komşu hücre sinyalinin aşması gereken RSRP eşiğidir.
- **threshX-Low**: Eğer bu komşu frekans servis frekansından daha düşük önceliğe sahipse, servis hücresi sinyali `threshServingLow` altına indiğinde, bu komşu hücre sinyalinin geçiş için aşması gereken RSRP eşiğidir.

---

## 2. lte-sib-parser ve get-info.py Tarafından Çözümlenmesi

[[lte-sib-parser]] aracı havadan yakaladığı SIB5 verisini SQLite veritabanındaki `cells` tablosunun `sib5` sütununa JSON formatında kaydeder. [[dbparsers]] paketindeki `get-info.py` scripti bu JSON'u parse ederek aşağıdaki şekilde komşu listesini raporlar:

```bash
|-  neighbours
|-  earfcn      allowedMeasBandwidth    Priority
|
|-> 1300        mbw100                  6
|-> 6300        mbw50                   3
```

Yukarıdaki örnek çıktıda:
1.  Servis hücresinin SIB5 yayını içerisinde iki adet inter-frequency komşu taşıyıcı tanımlanmıştır: EARFCN `1300` (Band 3 - 1800 MHz, 20 MHz BW, yüksek öncelik: 6) ve EARFCN `6300` (Band 20 - 800 MHz, 10 MHz BW, düşük öncelik: 3).
2.  Cihaz boşta moddayken, önceliği `6` olan 1800 MHz katmanına geçmek için her zaman komşu RSRP değerini ölçer. Eğer 1800 MHz sinyali iyi durumdaysa, servis hücresinin kalitesine bakmaksızın oraya geçer.

---

## 3. Akıştaki Önemi (sib-scan.sh Rekürsif Tarama)

[[sib-scan.sh]] tarama scriptinde yer alan rekürsif tarama mekanizması doğrudan SIB5'e dayanır:
1.  Script ilk olarak cell_search ile bir hücre bulur ve onun SIB5'ini çözümler.
2.  SIB5 içerisindeki inter-frequency komşu listesinden çıkan yeni EARFCN'ler (örneğin yukarıdaki 1300 ve 6300) otomatik olarak **taranacaklar kuyruğuna (earfcn_need_scan)** eklenir.
3.  Böylece sistem, çevredeki tüm LTE frekans katmanlarını zincirleme bir şekilde (rekürsif olarak) keşfetmiş olur.
