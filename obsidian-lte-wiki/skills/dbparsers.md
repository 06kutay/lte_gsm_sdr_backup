---
title: dbparsers
source: /home/mobsec/Desktop/netmon/lte-sib-parser/vol/dbparsers
created_date: 2026-06-01
tags:
  - script
  - python
  - database
  - analysis
---

# `dbparsers` Veritabanı Analiz Scriptleri Rehberi

`lte-sib-parser` aracı tarafından toplanan ham radyo parametreleri ve SIB verileri SQLite veritabanına kaydedildikten sonra, bu verileri anlamlandırmak, komşu hücre ilişkilerini haritalandırmak ve reselection parametrelerini analiz etmek amacıyla `/vol/dbparsers/` dizininde 4 adet Python betiği kullanılır.

Bu sayfada, bu scriptlerin veri tabanında koşturduğu SQL sorguları, girdi/çıktı formatları ve sundukları teknik analizler detaylandırılmıştır.

---

## 1. `list-cells.py` (Özet Hücre Listeleme)

### Görevi
Veritabanında bulunan tüm hücrelerin band, EARFCN, RSRP değerlerini, hangi SIB'lerin başarıyla çözümlendiğini ve hücrenin servis öncelik değerini özet tablo halinde listeler.

### SQL Sorgusu ve Akışı
```sql
SELECT band, earfcn, rsrp, mib, sib1, sib2, sib3, sib4, sib5, sib6, sib7, sib8, sib9, sib10, sib11, sib12, sib13 
FROM cells 
ORDER BY rsrp;
```
- Sorgu sonucunda dönen hücre kayıtlarında, `sib1`'den `sib13`'e kadar olan kolonlar kontrol edilir. Eğer kolonda veri varsa (yani o SIB başarıyla çözülmüşse) tabloda ilgili SIB numarası listelenir.
- Hücrenin servis önceliği, `sib3` JSON verisi içerisindeki `cellReselectionServingFreqInfo -> cellReselectionPriority` parametresi parse edilerek ekrana yazdırılır.

### Çalıştırma ve Çıktı Örneği
```bash
python3 list-cells.py -d /vol/output/cells.sqlite
```
**Çıktı Tablosu:**
```text
Band    EARFCN          RSRP    MIB parsed      parsed SIBs     priority
3       1675            -85     True            1 2 3 5         7
20      6300            -98     True            1 2 3           3
```

---

## 2. `get-info.py` (Derinlemesine Parametre ve Komşu Analizi)

### Görevi
Hücre bazında en kritik radyo parametrelerini ve komşuluk ilişkilerini raporlayan en gelişmiş analiz aracıdır. [[SIB1]], [[SIB3]] ve [[SIB5]] verilerini çözerek reselection eşiklerini ve komşu EARFCN'leri listeler.

### SQL Sorgusu ve Akışı
```sql
SELECT band, earfcn, rsrp, sib1, sib3, sib5 
FROM cells 
ORDER BY rsrp;
```

### Yürüttüğü Matematiksel Hesaplamalar ve Mantık:
1.  **Hücre Erişim Detayları (SIB1)**: `sib1` JSON verisinden TAC (Tracking Area Code) ve 28-bit Cell Identity ikili (binary) veriden tamsayıya çevrilir. PLMN-IdentityList içinden MCC ve MNC değerleri listelenir.
2.  **Ölçüm Eşikleri (SIB3)**: `sib3` içindeki reselection parametrelerine göre cihazın hangi sinyal seviyesinde komşu aramaya başlayacağını hesaplar:
    - **Intra-Freq Arama Sınırı**: `s-IntraSearch * 2 + q-RxLevMin * 2` (dBm)
    - **Inter-Freq Arama Sınırı**: `s-NonIntraSearch * 2 + q-RxLevMin * 2` (dBm)
3.  **Farklı Frekans Komşuları (SIB5)**: `sib5` içerisindeki `interFreqCarrierFreqList` listesini parse ederek komşu LTE [[EARFCN]] değerlerini, izin verilen ölçüm bant genişliklerini (`allowedMeasBandwidth`) ve komşu frekans reselection önceliklerini listeler.

### Çalıştırma ve Çıktı Örneği
```bash
python3 get-info.py -d /vol/output/cells.sqlite -e 1675
```
**Analiz Çıktısı:**
```text
----------------------------------------------------------------------------
Band    EARFCN  RSRP    TAC     cellIdentity    Priority        MCC     MNC     
3       1675    -85     12345   14285701        7               286     01

Intra-freq meas condition: cell RSRP <= -70 dBm
Inter-freq meas condition: cell RSRP <= -88 dBm

|-  neighbours
|-  earfcn      allowedMeasBandwidth    Priority
|
|-> 1300        mbw100                  6
|-> 6300        mbw50                   3
----------------------------------------------------------------------------
```

---

## 3. `get-arfcns.py` (EARFCN Listesi Çıkarma)

### Görevi
Veritabanında kayıtlı tüm taranmış/keşfedilmiş hücrelerin [[EARFCN]] değerlerini aralarında boşluk bırakarak tek bir satırda yazdırır.

### SQL Sorgusu
```sql
SELECT earfcn FROM cells;
```

### Kullanım Amacı
Bu script, [[sib-scan.sh]] tarayıcısı tarafından taranmış hücrelerin listesini hızlıca almak ve yeni bir tarama döngüsünde mükerrer taramayı önlemek amacıyla pipe-friendly (borulama uyumlu) bir filtre olarak kullanılır.
```bash
python3 get-arfcns.py -d /vol/output/cells.sqlite
# Çıktı: 1675 6300 3050
```

---

## 4. `get-sib.py` (Ham SIB JSON Dökümü)

### Görevi
Belirli bir hücreye (EARFCN) ve istenen belirli bir SIB türüne ait ham çözümlenmiş JSON verisini ekrana basar.

### SQL Sorgusu
İstenen SIB kolonuna göre dinamik bir SELECT sorgusu çalıştırır:
```sql
SELECT sib<X> FROM cells WHERE earfcn = <EARFCN_DEGERI>;
```

### Kullanım Amacı
Otomatik analiz dışında, belirli bir hücrenin belirli bir sistem bilgi bloğunun (örneğin [[SIB1]]'in tüm içeriğinin) ham yapısını doğrulamak veya harici analiz araçlarına beslemek için ham JSON dökümü almak amacıyla kullanılır.
```bash
python3 get-sib.py -d /vol/output/cells.sqlite -e 1675 -s 1
```
*Bu komut EARFCN 1675 hücresinin SIB1 JSON içeriğini tam formatlı olarak ekrana yazar.*

---

## 5. Projedeki Rolü ve İlişkiler

Bu Python araçları, ham radyo verisini projemizin temel felsefesi olan **[[index]]** ve **[[Sistem Mimarisi]]** katmanına taşır.
- Elde edilen veriler, şebekenin mobilitesini anlamak amacıyla [[Komşu Hücre Analizi]] sürecinde girdi olarak kullanılır.
- Çözümlenen bandların fiziksel gerçeklikleri ise [[LTE Bandlar]] ve [[Frekans Tablosu]] referans sayfalarındaki değerlerle doğrulanır.
