---
title: UARFCN
source: 3GPP TS 25.101
created_date: 2026-06-01
tags:
  - lte
  - 3g
  - rf
  - concept
---

# UARFCN (UTRA Absolute Radio Frequency Channel Number)

**UARFCN**, 3G WCDMA/UMTS (UTRAN) mobil iletişim şebekelerinde Downlink ve Uplink merkez frekanslarını benzersiz bir şekilde tanımlayan mutlak radyo frekans kanal numarasıdır.

LTE'de kullanılan [[EARFCN]] yapısının 3G/WCDMA şebekelerindeki doğrudan karşılığıdır.

---

## 1. Frekans Hesaplama
UARFCN numaraları, kanal merkez frekansının ($F_{DL}$ veya $F_{UL}$ in MHz) 5 ile çarpılmasıyla elde edilir. Formül şu şekildedir:

$$UARFCN = 5 \times F$$

Ters formül ile UARFCN değerinden frekans elde edilir:

$$F = 0.2 \times UARFCN$$

---

## 2. Sistem Rolü
- **Inter-RAT Mobilite**: Cihaz (UE) LTE şebekesinden 3G şebekesine geçerken, taranacak hedef 3G kanalları [[SIB6]] mesajı içerisinde **UARFCN** parametresi olarak cihaza bildirilir.
- **Spektrum Planlama**: Operatörlerin 3G/UMTS frekans tahsislerini anlamak ve komşu baz istasyonlarını haritalandırmak için kullanılır.

---

## 🔗 İlgili Sayfalar
- [[EARFCN]] — LTE Absolute Radio Frequency Channel Number.
- [[SIB6]] — UTRAN Inter-RAT Mobility parameters.
- [[Komşu Hücre Analizi]] — Hücreler arası geçiş ve komşu şeması.
