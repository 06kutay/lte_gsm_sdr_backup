---
title: "GSM Komşu Haritası"
source: "Topoloji Matrisi"
created_date: "2026-06-02"
tags: ["topology", "relations", "matrix", "gsm"]
---

# GSM Komşu Haritası Matrisi

Bu sayfa, yapılan tüm GSM taramalarından derlenen ve servis hücrelerinin komşuluk ilişkilerini (BA listeleri) özetleyen master veri tabanı tablosudur.

## 🗺️ Görsel Topoloji Şeması

```mermaid
flowchart TD
  %% Stil Tanımları
  classDef scanned fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#f8fafc;
  classDef unscanned fill:#0f172a,stroke:#475569,stroke-width:1px,stroke-dasharray: 5 5,color:#94a3b8;
  Cell_GSM_60["ARFCN 60\nCID 7349"]:::scanned
  Cell_GSM_48["ARFCN 48\n(Taranmamış)"]:::unscanned
  Cell_GSM_54["ARFCN 54\n(Taranmamış)"]:::unscanned
  Cell_GSM_55["ARFCN 55\n(Taranmamış)"]:::unscanned
  Cell_GSM_56["ARFCN 56\n(Taranmamış)"]:::unscanned
  Cell_GSM_57["ARFCN 57\n(Taranmamış)"]:::unscanned
  Cell_GSM_58["ARFCN 58\n(Taranmamış)"]:::unscanned
  Cell_GSM_59["ARFCN 59\n(Taranmamış)"]:::unscanned
  Cell_GSM_61["ARFCN 61\n(Taranmamış)"]:::unscanned
  Cell_GSM_48 -.-> Cell_GSM_60
  Cell_GSM_54 -.-> Cell_GSM_60
  Cell_GSM_55 -.-> Cell_GSM_60
  Cell_GSM_56 -.-> Cell_GSM_60
  Cell_GSM_57 -.-> Cell_GSM_60
  Cell_GSM_58 -.-> Cell_GSM_60
  Cell_GSM_59 -.-> Cell_GSM_60
  Cell_GSM_60 <--> Cell_GSM_60
  Cell_GSM_60 -.-> Cell_GSM_61
```

## 📊 İlişki Detay Matrisi

| Servis Hücresi | Servis CID | Komşu ARFCN | Komşu Band | Komşu Frekans | Komşu Operatör Tahmini | Yönlendirme | İlk Tespit Tarihi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [[Cell_GSM_ARFCN60]] | 7349 | 48 | GSM900 | 944.6 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 54 | GSM900 | 945.8 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 55 | GSM900 | 946.0 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 56 | GSM900 | 946.2 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 57 | GSM900 | 946.4 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 58 | GSM900 | 946.6 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 59 | GSM900 | 946.8 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 60 | GSM900 | 947.0 MHz | Turkcell | Karşılıklı (Bidirectional) | `2026-06-02` |
| [[Cell_GSM_ARFCN60]] | 7349 | 61 | GSM900 | 947.2 MHz | Turkcell | Taranmamış Keşif (Unscanned) | `2026-06-02` |
