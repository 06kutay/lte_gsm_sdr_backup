# LTE Komşu Hücre Analiz Sistemi

## Araçlar
- lte-sib-parser: Docker konteyner içinde, srsRAN tabanlı SIB parser
- SDR: LimeSDR Mini 2.0, parametreler: -d soapy -a "rxant=LNAH" (yüksek bandlar >= 1.5 GHz) / -a "rxant=LNAW" (düşük bandlar < 1.5 GHz)
- Obsidian Wiki: /home/mobsec/Desktop/netmon/obsidian-lte-wiki — Karpathy LLM Wiki Pattern

## Temel Akış
EARFCN listesi → earfcn doğrulama → sib-scan.sh → SQLite → sonuç analizi → wiki'ye kaydet

## sib-scan.sh Kullanımı
- Yüksek Bandlar (>=1.5 GHz): ./sib-scan.sh -d soapy -a "rxant=LNAH" -g 35 -q "100 1300 1444 1620 3350 3450" -D /vol/output/scan_20260601_high.sqlite
- Düşük Bandlar (<1.5 GHz): ./sib-scan.sh -d soapy -a "rxant=LNAW" -g 35 -q "6200 6300" -D /vol/output/scan_20260601_low.sqlite

## Kurallar
- Tüm bilgi birikimi wiki'de tutulur
- Her tarama sonucu wiki'ye ingest edilir
- Komşu ilişkileri [[wikilink]] ile bağlanır
- Script'ler küçük, tek iş yapan, pipe-friendly olmalı
