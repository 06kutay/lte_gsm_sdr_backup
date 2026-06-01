---
title: SIB4
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - mobility
---

# SIB4 (System Information Block Type 4)

**SIB4**, LTE sisteminde **Aynı Frekanslı (Intra-frequency)** komşu hücrelerin bilgilerini içeren sistem bilgi bloğudur. Cihazın (UE) bağlı olduğu mevcut servis hücresi ile aynı [[EARFCN]] değerine sahip, ancak farklı **PCI (Physical Cell Identity)** değerlerindeki çevre hücreleri yönetir.

---

## 1. Görevi ve SIB3 ile İlişkisi

Cihaz boşta (idle) moddayken servis hücresinin kalitesi [[SIB3]] içerisinde belirtilen `s-IntraSearch` eşiğinin altına düşerse, aynı frekanstaki komşu hücreleri aramaya ve ölçmeye başlar. 
- Bu aşamada hangi PCI'ların taranacağı, hangilerine özel öncelik veya offset uygulanacağı ve hangi hücrelerin yasaklı (blacklisted) olduğu bilgisi **SIB4** üzerinden okunur.

---

## 2. İçerdiği Kritik Parametreler

SIB4 temel olarak üç liste yapısı içerir:

### A. Komşu Hücre Listesi (intraFreqNeighCellList)
Aynı frekanstaki komşu hücrelerin listesidir. Her komşu hücre için şu parametreler tanımlanabilir:
- **physCellId (PCI)**: Komşu hücrenin Fiziksel Hücre Kimliği (0 - 503 arası değer alır).
- **q-OffsetCell**: Bu hücreye özel uygulanacak olan seçim offset değeridir. Eğer bu değer pozitifse, cihaz bu hücreyi olduğundan daha iyi sinyal kalitesinde algılar ve bu hücreye geçişi kolaylaşır (Hücre Yük Dengeleme - Load Balancing için kullanılır).

### B. Kara Liste Hücre Listesi (intraFreqBlackCellList)
Cihazın kesinlikle bağlanmaması ve ölçüm yapmaması gereken hücrelerin PCI listesidir. Genellikle şu amaçlarla kullanılır:
- Sadece belirli cihaz gruplarına hizmet veren kapalı hücreler (femtocell/CSG).
- Aşırı parazit yapan veya arızalı hücreler.
- Operatörün test amacıyla yayına aldığı ama genel cihazların erişmesini istemediği hücreler.

---

## 3. Komşu İlişkileri

- SIB4 **Intra-frequency** (Aynı frekans) komşuları yönetirken, **Inter-frequency** (Farklı frekans) komşu ilişkileri için [[SIB5]] kullanılır.
- Aynı EARFCN üzerindeki hücrelerin fiziksel ayrımı yalnızca PCI değerleri üzerinden yapıldığından, SIB4 listesindeki PCI'ların doğru şekilde planlanması (PCI çakışması veya PCI karışıklığı - collision/confusion yaşanmaması) radyo ağ planlamasının temelidir.
- [[Komşu Hücre Analizi]] ve [[Sistem Mimarisi]] kapsamında, taranan hücrelerin çevre ilişkileri çözümlenirken SIB4 verisi SQLite veritabanına işlenerek `[[wikilink]]` ile haritalandırılır.
