---
title: GSM SI2
source: 3GPP TS 44.018 Section 9.1.32
created_date: 2026-06-02
tags:
  - gsm
  - system-information
  - concept
  - protocol
---

# GSM System Information Type 2 (SI2)

**System Information Type 2 (SI2)**, bir GSM baz istasyonunun bekleme (idle) modundaki mobil cihazlara izlemeleri ve kamp kurmaları gereken komşu GSM-900 hücre kanallarını (BA listesi) bildirdiği **en kritik komşu hücre kaynağı** olan BCCH mesajıdır.

LTE şebekelerinde komşu hücre listelerini taşıyan [[SIB5]] paketinin GSM'deki doğrudan karşılığıdır.

---

## 1. BA (BCCH Allocation) Listesi ve 128-Bit Bitmap Kodlaması

SI2 mesajı komşu hücre ARFCN kanallarını iletmek için **16 byte (128 bit)** boyutunda özel bir frekans listesi alanı (Neighbor Cells Information) kullanır. Bu alan genellikle bir **128-bit bitmap** olarak kodlanır.

```text
Byte 0      Byte 1      Byte 2                       Byte 15
[00000000]  [00000000]  [00000000]  ...  ...  ...  [00000000]
Bit 0: ARFCN 1          Bit 16: ARFCN 17           Bit 124: ARFCN 125
Bit 1: ARFCN 2          ...                        ...
```

* **Kodlama Mantığı:** Her bir bit pozisyonu sırayla bir ARFCN kanalına karşılık gelir ($1 \le n \le 124$).
* Eğer ilgili bit değeri **`1`** ise, o ARFCN numaralı frekans komşu listesindedir.
* Eğer ilgili bit değeri **`0`** ise, komşu listesinde yoktur.
* Bu bitmap sayesinde, tek bir mesaj bloğu içinde standarda uygun maksimum **124 farklı P-GSM kanalı** arasından komşu frekanslar eksiksiz şekilde listelenebilir.

---

## 2. RACH ve Ağı Engelleme (PLMN Permitted) Parametreleri

SI2 mesajı ayrıca şu ağ kontrol alanlarını taşır:
* **PLMN Permitted:** Hücrenin hangi operatörlerin erişimine izin verdiğini gösteren parametredir. Mobil cihaz kendi SIM kartındaki MCC/MNC ile bu alanı kontrol ederek ağa bağlanma iznini denetler.
* **RACH Control Parameters:** Cihazların bağlantı istek limitlerini belirler (bkz: [[GSM SI1]]).

---

## 3. Komşu Hücre Analizi için Önemi
Pasif analiz sistemimizde `grgsm_scanner` ve `grgsm_livemon_headless` araçları baz istasyonuna bağlandığında, havadan yakalanan ilk paket grupları SI2'dir. Bu paketin 128-bit alanından çözülen BA listesi, çevredeki tüm diğer aktif GSM-900 frekanslarını deşifre ederek tarama sisteminin bir sonraki aşamada hangi frekansları taraması gerektiğini belirler.

---

## 4. İlgili Bağlantılar
* [[GSM SI Genel]] — System Information mimarisi.
* [[GSM SI2bis]] — BA listesi sığmadığında kullanılan ek liste.
* [[GSM SI2ter]] — DCS-1800 bandındaki komşu listeleri.
* [[GSM vs LTE Komşu Tespiti]] — LTE SIB5 ile ayrıntılı karşılaştırma.
* [[SIB5]] — LTE komşu frekans yayını.
