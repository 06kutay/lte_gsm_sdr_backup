---
title: SIB Genel
source: 3GPP TS 36.331
created_date: 2026-06-01
tags:
  - lte
  - sib
  - radio
  - telecommunication
---

# SIB (System Information Block) Genel

LTE (Long Term Evolution) sistemlerinde, baz istasyonları (eNodeB) mobil cihazların (UE - User Equipment) hücreye bağlanabilmesi, hücrede kalabilmesi ve hücreler arası geçiş (mobility/handover) yapabilmesi için gerekli olan tüm sistem parametrelerini **Hücre Yayını (Broadcast)** şeklinde havadan yayınlar. Bu bilgilere toplu olarak **Sistem Bilgileri (System Information - SI)** denir.

Sistem Bilgileri, taşıdıkları verinin aciliyetine ve boyutuna göre iki ana gruba ayrılır:
1. **MIB (Master Information Block)**: Fiziksel katman parametrelerini içerir.
2. **SIB (System Information Block)**: Protokol ve radyo kaynak parametrelerini içerir.

---

## 1. MIB ve SIB Ayrımı

### MIB (Master Information Block)
- **Kanal**: BCCH (Broadcast Control Channel) -> BCH (Broadcast Channel) -> PBCH (Physical Broadcast Channel) üzerinden iletilir.
- **Periyot**: Her 40 ms'de bir güncellenir ancak her 10 ms'de bir (System Frame Number - SFN mod 4 = 0 olan alt çerçevelerde) tekrarlanır.
- **İçerik**: Sınırlı ama kritik parametreler içerir:
  - Hücrenin bant genişliği (Downlink Bandwidth - 1.4, 3, 5, 10, 15, 20 MHz).
  - PHICH (Physical Hybrid-ARQ Indicator Channel) konfigürasyonu.
  - Sistem Çerçeve Numarası (SFN - System Frame Number) en anlamlı 8 biti.
  - Anten port sayısı.

### SIB (System Information Block)
- **Kanal**: BCCH -> DL-SCH (Downlink Shared Channel) -> PDSCH (Physical Downlink Shared Channel) üzerinden dinamik olarak iletilir.
- **Periyot**: SIB tipine bağlı olarak değişken periyotlarda yayınlanır.
- **İçerik**: Hücre seçimi, komşuluklar, frekanslar, PLMN bilgileri gibi üst katman parametreleri içerir.

---

## 2. SIB Türleri ve Görevleri

3GPP TS 36.331 standartlarına göre tanımlanmış çok sayıda SIB bulunmaktadır. Bu projede, özellikle [[lte-sib-parser]] ve [[srsRAN]] ile dinlediğimiz ve komşu hücre analizinde kullandığımız kritik SIB'ler şunlardır:

*   **[[SIB1]] (Hücreye Erişim ve Planlama)**: PLMN kimlikleri, TAC (Tracking Area Code), Hücre Kimliği (Cell ID) ve diğer SIB'lerin zamanlama/planlama (scheduling) bilgilerini içerir. Her 80 ms'de bir yayınlanır.
*   **[[SIB3]] (Hücre Seçimi ve Yeniden Seçim)**: Hücre seçimi ve yeniden seçimi (cell reselection) için ortak parametreleri tanımlar.
*   **[[SIB4]] (Aynı Frekans Komşuluklar - Intra-frequency)**: Aynı [[EARFCN]] üzerindeki komşu hücrelerin PCI (Physical Cell Identity) listesini ve kara listeye alınmış hücreleri içerir.
*   **[[SIB5]] (Farklı Frekans Komşuluklar - Inter-frequency)**: Farklı [[EARFCN]] değerlerindeki LTE komşu hücrelerini, onların önceliklerini ve reselection parametrelerini içerir. [[Komşu Hücre Analizi]] için en kritik SIB'dir.
*   **[[SIB6]] (UTRAN / 3G Komşuluklar)**: 3G (WCDMA/UMTS) komşu hücre bilgilerini taşır.
*   **[[SIB7]] (GERAN / 2G Komşuluklar)**: 2G (GSM) komşu hücre bilgilerini taşır.

---

## 3. Zamanlama ve Planlama (Scheduling)

SIB1 dışındaki tüm SIB'ler (SIB2'den başlayarak SIB21'e kadar), **System Information (SI) Mesajları** şeklinde gruplandırılarak iletilir. 
- Hangi SIB'lerin hangi SI mesajı içinde gruplanacağı ve bunların yayınlanma periyotları **[[SIB1]]** içerisinde yer alan `schedulingInfoList` parametresi ile belirlenir.
- SI mesajlarının iletim zamanları (transmission window), alt çerçeveler (subframe) düzeyinde dinamik olarak PDCCH (Physical Downlink Control Channel) üzerinde **SI-RNTI (System Information Radio Network Temporary Identifier)** aranarak UE tarafından çözümlenir.

## 4. Cihaz Durumları (RRC States) ve SIB Kullanımı

- **RRC_IDLE (Boşta Mod)**: UE, eNodeB ile aktif bir bağlantıya sahip değildir. Enerji tasarrufu için uykudadır. Ancak arka planda sürekli olarak [[SIB1]], [[SIB3]], [[SIB4]], [[SIB5]], [[SIB6]] ve [[SIB7]] mesajlarını dinleyerek en iyi sinyale sahip hücreyi seçmeye (cell reselection) çalışır.
- **RRC_CONNECTED (Aktif Bağlantı Modu)**: UE, aktif olarak veri transferi yapmaktadır. Bu modda mobilite eNodeB tarafından yönetilen **Handover** mekanizması ile gerçekleştirilir. UE, eNodeB'den gelen ölçüm konfigürasyonlarına (Measurement Control) göre çevre hücreleri ölçer ve raporlar. SIB'lerden ziyade doğrudan RRC bağlantı mesajlarını dinler.
