---
title: "Komşu Haritası"
source: "Topoloji Matrisi"
created_date: "2026-06-01"
tags: ["topology", "relations", "matrix"]
---

# LTE Komşu Haritası Matrisi

Bu sayfa, yapılan tüm taramalardan derlenen ve servis hücrelerinin komşuluk ilişkilerini özetleyen master veri tabanı tablosudur.

## 🗺️ Görsel Topoloji Şeması

```mermaid
flowchart TD
  %% Stil Tanımları
  classDef scanned fill:#1e293b,stroke:#0ea5e9,stroke-width:2px,color:#f8fafc;
  classDef unscanned fill:#0f172a,stroke:#475569,stroke-width:1px,stroke-dasharray: 5 5,color:#94a3b8;
  Cell_100_265["EARFCN 100\nPCI 265"]:::scanned
  Cell_2850_192["EARFCN 2850\nPCI 192"]:::scanned
  Cell_550_N_A["EARFCN 550\n(Taranmamış)"]:::unscanned
  Cell_1651_N_A["EARFCN 1651\n(Taranmamış)"]:::unscanned
  Cell_1795_N_A["EARFCN 1795\n(Taranmamış)"]:::unscanned
  Cell_6400_189["EARFCN 6400\nPCI 189"]:::scanned
  Cell_3350_112["EARFCN 3350\nPCI 112"]:::scanned
  Cell_6200_210["EARFCN 6200\nPCI 210"]:::scanned
  Cell_1675_N_A["EARFCN 1675\n(Taranmamış)"]:::unscanned
  Cell_1444_82["EARFCN 1444\nPCI 82"]:::scanned
  Cell_1300_45["EARFCN 1300\nPCI 45"]:::scanned
  Cell_100_265 --> Cell_2850_192
  Cell_100_265 -.-> Cell_550_N_A
  Cell_100_265 -.-> Cell_1651_N_A
  Cell_100_265 -.-> Cell_1795_N_A
  Cell_100_265 <--> Cell_6400_189
  Cell_3350_112 --> Cell_6200_210
  Cell_1675_N_A -.-> Cell_3350_112
  Cell_1444_82 <--> Cell_1300_45
  Cell_1444_82 --> Cell_3350_112
  Cell_6400_189 --> Cell_2850_192
  Cell_550_N_A -.-> Cell_6400_189
  Cell_1651_N_A -.-> Cell_6400_189
  Cell_1795_N_A -.-> Cell_6400_189
```

## 📊 İlişki Detay Matrisi

| Servis Hücresi | Servis EARFCN | Servis PCI | Komşu Tipi | Komşu EARFCN | Komşu PCI | Yönlendirme | İlk Tespit Tarihi |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| [[Cell_EARFCN100_PCI265]] | 100 | 265 | Inter-Freq (LTE) | 2850 | 192 | Tek Yönlü (Unidirectional) | `2026-06-01` |
| [[Cell_EARFCN100_PCI265]] | 100 | 265 | Inter-Freq (LTE) | 550 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
| [[Cell_EARFCN100_PCI265]] | 100 | 265 | Inter-Freq (LTE) | 1651 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
| [[Cell_EARFCN100_PCI265]] | 100 | 265 | Inter-Freq (LTE) | 1795 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
| [[Cell_EARFCN100_PCI265]] | 100 | 265 | Inter-Freq (LTE) | 6400 | 189 | Karşılıklı (Bidirectional) | `2026-06-01` |
| [[Cell_EARFCN3350_PCI112]] | 3350 | 112 | Inter-Freq (LTE) | 6200 | 210 | Tek Yönlü (Unidirectional) | `2026-06-01` |
| [[Cell_EARFCN3350_PCI112]] | 3350 | 112 | Inter-Freq (LTE) | 1675 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
| [[Cell_EARFCN1444_PCI82]] | 1444 | 82 | Inter-Freq (LTE) | 1300 | 45 | Karşılıklı (Bidirectional) | `2026-06-01` |
| [[Cell_EARFCN1444_PCI82]] | 1444 | 82 | Inter-Freq (LTE) | 3350 | 112 | Tek Yönlü (Unidirectional) | `2026-06-01` |
| [[Cell_EARFCN1300_PCI45]] | 1300 | 45 | Inter-Freq (LTE) | 1444 | 82 | Karşılıklı (Bidirectional) | `2026-06-01` |
| [[Cell_EARFCN6400_PCI189]] | 6400 | 189 | Inter-Freq (LTE) | 2850 | 192 | Tek Yönlü (Unidirectional) | `2026-06-01` |
| [[Cell_EARFCN6400_PCI189]] | 6400 | 189 | Inter-Freq (LTE) | 100 | 265 | Karşılıklı (Bidirectional) | `2026-06-01` |
| [[Cell_EARFCN6400_PCI189]] | 6400 | 189 | Inter-Freq (LTE) | 550 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
| [[Cell_EARFCN6400_PCI189]] | 6400 | 189 | Inter-Freq (LTE) | 1651 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
| [[Cell_EARFCN6400_PCI189]] | 6400 | 189 | Inter-Freq (LTE) | 1795 | N/A | Taranmamış Keşif (Unscanned) | `2026-06-01` |
