---
title: Sistem Mimarisi
source: Uçtan Uca Proje Tasarımı
created_date: 2026-06-01
tags:
  - synthesis
  - architecture
  - pipeline
  - data-flow
---

# Uçtan Uca LTE Komşu Hücre Analiz Sistemi Mimarisi

Bu döküman, projemizin donanımsal radyo sinyali alımından (RF Layer) başlayarak, yazılımsal sinyal çözümleme (srsRAN Layer), veritabanı kaydı (Parsing/Database Layer) ve nihai olarak Obsidian Wiki üzerinde Karpathy LLM Wiki formatında bilgi birikimine dönüştürülmesi (Knowledge Layer) adımlarını kapsayan uçtan uca **Sistem Mimarisidir**.

---

## 1. Uçtan Uca Veri Akışı ve Pipeline Şeması

Sistem, birbirini borulama (pipe) veya veritabanı üzerinden besleyen 4 ana katmandan oluşur:

```mermaid
graph TD
    %% RF Layer
    subgraph RF [1. RF Sinyal Katmanı]
        Air[Havadan LTE Yayını] -->|10 MHz - 3.5 GHz| Ant[Anten Portu: LNAH / LNAW]
        Ant --> LimeSDR[LimeSDR Mini 2.0]
        LimeSDR -->|USB 3.0 Passthrough| HostOS[Host Aygıt Arayüzü: /dev/bus/usb]
    end

    %% Software Layer
    subgraph Software [2. Çözümleme ve Tarama Katmanı]
        HostOS -->|SoapySDR Arayüzü| Docker[Docker Konteyner]
        Docker -->|cell_search| CellSearch[Aktif EARFCN / PCI Keşfi]
        CellSearch -->|Otomatik Girdi| StateMachine[sib-scan.sh Orkestrasyonu]
        StateMachine -->|srsue emülasyonu| SRSUE[srsue Pasссив Dinleme]
        SRSUE -->|Ham SIB Blokları Logu| UELog[/tmp/ue.log]
    end

    %% Database Layer
    subgraph Database [3. Veritabanı ve Parsing Katmanı]
        UELog -->|parse_save_sib.py| Parser[Python ASN.1 Parser]
        Parser -->|Yapılandırılmış JSON| SQLite[(cells.sqlite)]
        SQLite -->|get_neigh.py - SIB5 Okuma| StateMachine
    end

    %% Knowledge Layer
    subgraph Knowledge [4. Bilgi ve Wiki Katmanı]
        SQLite -->|dbparsers: list-cells.py / get-info.py| CLIOut[CLI Analiz Çıktıları]
        CLIOut -->|wiki-ingest / wiki-update| WikiVault[Obsidian LTE Wiki]
    end
    
    style RF fill:#f9f,stroke:#333,stroke-width:2px
    style Software fill:#bbf,stroke:#333,stroke-width:2px
    style Database fill:#dfd,stroke:#333,stroke-width:2px
    style Knowledge fill:#ffd,stroke:#333,stroke-width:2px
```

---

## 2. Katmanların Detaylı Rolleri

### 1. RF Sinyal Katmanı (Hardware & Host Virtualization)
- Pasif dinleme yapan [[LimeSDR Mini 2.0]] donanımı, baz istasyonlarının downlink yayın kanallarını yakalar.
- Konteyner sanallaştırma sınırlarını aşmak için `/dev/bus/usb` doğrudan konteynere map edilmiştir. USB 3.0 veri yollarının hızı, sinyal örneklerinin kesintisiz akışı için kritiktir (Detaylar: [[Docker Kurulum]] ve [[LimeSDR Mini 2.0]]).

### 2. Çözümleme ve Tarama Katmanı (Orchestration & srsRAN)
- **[[sib-scan.sh]]** ana kontrolcüsü (orchestrator), tara-keşfet-dinle döngüsünü yönetir.
- **`cell_search`** ile ortamdaki aktif [[EARFCN]] değerleri taranır.
- **`srsue`** pasif dinleme modunda (TX kapalı) çalıştırılarak eNodeB'lerin yaydığı ham ASN.1 kodlu kontrol paketleri yakalanıp `/tmp/ue.log` dosyasına akıtılır (Detaylar: [[srsRAN]]).

### 3. Veritabanı ve Parsing Katmanı (Data Structuring)
- **`parse_save_sib.py`** betiği `/tmp/ue.log` loglarını anlık olarak izler. SIB verilerini byte array formatından kurtarıp JSON'a çevirerek `cells.sqlite` veritabanındaki SIB1-13 kolonlarına işler.
- **Rekürsif Besleme**: Tarama tamamlandığında `get_neigh.py` veritabanından hücrenin [[SIB5]] verisini okur. Komşu EARFCN'leri çekerek `sib-scan.sh` kuyruğuna dinamik olarak ekler. Böylece zincirleme keşif sağlanır (Detaylar: [[dbparsers]] ve [[Komşu Hücre Analizi]]).

### 4. Bilgi ve Wiki Katmanı (Knowledge Engine)
- Veritabanı dolduktan sonra `get-info.py` ve `list-cells.py` gibi araçlar ile şebekenin erişim ve reselection eşikleri hesaplanır (Detaylar: [[SIB1]], [[SIB3]], [[Frekans Tablosu]]).
- CLI çıktısı ve veritabanı analiz raporları, `wiki-ingest` pipeline'ı vasıtasıyla projenin Obsidian Wiki vault'una (`/home/mobsec/Desktop/netmon/obsidian-lte-wiki/`) otomatik olarak aktarılır ve `[[wikilinks]]` ile bağlanır.

---

## 3. Sistem Mimarisinin Avantajları

1.  **Pasif Dinleme Güvenliği**: TX kapalı emülasyon yapısı sayesinde sisteme hiçbir şekilde RF sinyal salınımı (iz bırakma) yapılmaz, tamamen pasif dinlemede kalınır.
2.  **Otomatik Rekürsif Keşif**: Manuel frekans girme ihtiyacını sıfıra indirerek, tek bir başlangıç EARFCN'inden tüm çevre spektrumu otomatik olarak haritalandırılır.
3.  **Karpathy LLM Wiki Entegrasyonu**: Elde edilen tüm radyo frekans parametreleri, birbiriyle ilişkili modüler makaleler şeklinde wiki'ye ingest edilerek kalıcı bilgi tabanı oluşturulur.
