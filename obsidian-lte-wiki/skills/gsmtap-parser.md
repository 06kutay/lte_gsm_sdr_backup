---
title: "gsmtap-parser"
source: "Özel GSM Otomasyon Skill"
tags: ["skill", "automation", "gsm"]
---

# gsmtap-parser

UDP 4729 loopback akan GSMTAP paketlerini süzerek, dahili sıfır bağımlılıklı Python raw socket ve `struct.unpack` başlık çözücü veya `tshark` ikincil fallback filtresi ile Layer 3 System Information (SI2/SI3/SI5) paketlerini çözümler.

---

## ⚙️ Fonksiyon ve Kullanım
Bu skill, canlı dinleme sırasında akan ham Um arayüzü kontrol paketlerini yakalamak ve deşifre etmek için kullanılır. Detaylı teknik kılavuzu projenin [SKILL.md](file:///home/mobsec/Desktop/netmon/.skills/gsmtap-parser/SKILL.md) dosyasında yer almaktadır.

## 🔗 İlgili Sayfalar
- [[GSMTAP]]
- [[GSM SI Genel]]
- [[index]]
