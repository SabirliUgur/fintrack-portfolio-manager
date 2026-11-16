# FinTrack — Portfel İdarəetmə və Risk Auditi Sistemi

**FinTrack**, səhm və kriptovalyuta investisiyalarını izləmək, canlı bazar qiymətlərini avtomatik çəkmək, xalis mənfəət/zərəri hesablamaq və portfel konsentrasiya riskini analiz etmək üçün Python dilində hazırlanmış modul tipli konsol (CLI) tətbiqidir.

## Əsas Xüsusiyyətlər

* **Avtomatik Canlı Qiymət İnteqrasiyası (API):** `yfinance` kitabxanası vasitəsilə səhm (`AMZN`, `GOOGL`) və kriptovalyutaların (`BTC-USD`) real vaxt bazar qiymətlərini çəkir. Şəbəkə kəsildikdə və ya naməlum simvol daxil edildikdə əl ilə giriş (*fallback*) imkanı təqdim edir.
* **Maliyyə İcmalı və P&L Analizi:** Ümumi maya dəyəri, cari bazar dəyəri, xalis mənfəət/zərər ($) və gəlirlilik faizini (%) dəqiq hesablayır.
* **Konsentrasiya Riski Auditi:** Portfeldəki hər hansı bir aktivin ümumi payı müəyyən edilmiş risk limitini (standart `50.0%`) aşdıqda avtomatik xəbərdarlıq verir.
* **Davamlı Məlumat Saxlanması (JSON):** Bütün əməliyyatlar `data/portfel.json` faylında strukturlaşdırılmış şəkildə saxlanılır.
* **Excel / CSV İxracı:** Portfel hesabatını bir kliklə Microsoft Excel və Google Sheets ilə tam uyğun (`utf-8-sig`) `.csv` cədvəli kimi ixrac edir.

## Layihə Arxitekturası

Layihə **Məsuliyyətlərin Bölünməsi (*Separation of Concerns*)** prinsipinə əsasən 4 müstəqil moduldan ibarətdir:

```text
fintrack-portfolio-manager/
├── data/
│   ├── portfel.json             # Aktivlərin saxlandığı əsas JSON verilənlər bazası
│   └── portfel_hesabati.csv     # İxrac edilmiş Excel uyğunluqlu hesabat faylı
├── src/
│   ├── storage.py               # Verilənlər qatı: JSON CRUD əməliyyatları və CSV ixracı
│   ├── analytics.py             # Biznes məntiqi: mənfəət/zərər və risk analizi
│   ├── market.py                # API qatı: Yahoo Finance üzərindən canlı qiymət sorğuları
│   └── main.py                  # UI qatı: interaktiv terminal menyusu və modulların koordinasiyası
├── requirements.txt             # Layihənin xarici asılılıqları
└── README.md                    # Layihə sənədləşməsi
```

## Quraşdırma və İşə Salma

1. **Repozitoriyanı klonlayın və qovluğa keçin:**
   ```bash
   git clone https://github.com/SabirliUgur/fintrack-portfolio-manager.git
   cd fintrack-portfolio-manager
   ```

2. **Virtual mühit yaradın və aktivləşdirin (Windows):**
   ```bash
   python -m venv .venv
   .venv\Scripts\activate
   ```

3. **Lazımi kitabxananı quraşdırın:**
   ```bash
   python -m pip install -r requirements.txt
   ```

4. **Proqramı kök qovluqdan işə salın:**
   ```bash
   python src/main.py
   ```

## İstifadə Olunan Texnologiyalar

* **Dil:** Python 3.10+ (Type Hints, Guard Clauses, Defensive Programming)
* **Bazar Məlumatları:** `yfinance`
* **Verilənlər Formatı:** JSON, CSV (`pathlib`, `json`, `csv`, `logging`)