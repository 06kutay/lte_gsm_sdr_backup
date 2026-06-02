---
title: "gsm-wiki-ingest"
source: "Özel GSM Otomasyon Skill"
tags: ["skill", "automation", "gsm"]
---

# gsm-wiki-ingest

GSM tarama ve komşuluk verilerini Karpathy 3-layer wiki formatına uygun şekilde otomatik olarak `cells/Cell_GSM_ARFCN<num>.md` sayfalarına entegre eder. Idempotency kuralları ile `last_seen` ve changelog bilgilerini akıllı birleştirir (merge).

---

## ⚙️ Fonksiyon ve Kullanım
Bu skill, elde edilen canlı GSM baz istasyonu verilerini ve komşu listelerini otomatik olarak bilgi deposuna yazarak envanteri güncel tutar. Detaylı teknik kılavuzu projenin [SKILL.md](file:///home/mobsec/Desktop/netmon/.skills/gsm-wiki-ingest/SKILL.md) dosyasında yer almaktadır.

## 🔗 İlgili Sayfalar
- [[GSM Komsu Analizi]]
- [[index]]
