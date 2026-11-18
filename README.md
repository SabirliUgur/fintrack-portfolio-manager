# FinTrack — Portfel İdarəetmə, Limit Əmr və Risk Auditi Sistemi

**FinTrack**, səhm və kriptovalyuta investisiyalarını vahid mərkəzdən izləmək, tarixi və canlı bazar qiymətlərini avtomatik çəkmək, bazar/limit satış əmrlərini idarə etmək və portfel konsentrasiya riskini analiz etmək üçün hazırlanmış modul tipli Python CLI tətbiqidir.

## Əsas Xüsusiyyətlər (v2.0.0)

* **Zero-Dependency Bazar Mühərriki:** Xarici kitabxana (`pandas`, `yfinance`) tələb etmədən birbaşa Python standart kitabxanaları (`urllib.request`, `json`) vasitəsilə Yahoo Finance API-dən canlı qiymətləri çəkir.
* **Tarix və Saata Görə Avtomatik Alış Qiyməti:** İstifadəçinin daxil etdiyi tarixə (`YYYY-MM-DD` və ya `DD.MM.YYYY HH:MM`) uyğun tarixi bazar qiymətini tapır (qeyri-iş günləri üçün ən yaxın birja gününü müəyyən edir).
* **Çəkili Orta Alış Qiyməti:** Mövcud aktivə əlavə alış edildikdə yeni orta maya dəyərini avtomatik hesablayır.
* **Bazar və Limit Satış Əmrləri (Order Matching Engine):**
  * **Bazar Əmri:** Cari bazar qiyməti ilə dərhal tam və ya hissəvi satış (*Fractional Sell*) icra edir və **Realized P&L** ($ və %) hesablayır.
  * **Planlanan Limit Satış:** Cari bazar qiymətindən yüksək hədəf təyin edildikdə aktiv miqdarını bronlayır (`PENDING`), portfel yoxlanıldıqda hədəf qiymətə çatdıqda əmri avtomatik icra edir (`EXECUTED`) və ya ləğv etməyə (`CANCELLED`) imkan verir.
* **Konsentrasiya Riski Auditi:** Portfeldə hər hansı aktivin 50%-lik konsentrasiya limitini aşmasını yoxlayır.
* **Excel Uyğunluqlu CSV İxracı:** Ümumi, sərbəst və bronlanmış balanslar daxil olmaqla hesabatı `utf-8-sig` formatında `data/portfel_hesabati.csv` faylına ixrac edir.

## Layihə Strukturu

```text
fintrack-portfolio-manager/
├── src/
│   ├── main.py          # İstifadəçi interfeysi (CLI menyu və əməliyyat axınları)
│   ├── market.py        # Canlı və tarixi bazar qiymətləri API modulu
│   ├── storage.py       # JSON yaddaş, orta qiymət və limit əmr mühərriki
│   └── analytics.py     # P&L hesablamaları, risk auditi və CSV ixracı
├── data/                # Lokal portfel, limit əmrlər və CSV faylları (.gitignore)
├── requirements.txt     # Asılılıq qeydi (Zero external dependencies)
├── .gitignore           # Şəxsi data və mühit fayllarının filtrasiyası
└── README.md            # Layihə sənədləşməsi
```

## Quraşdırma və İşə Salma

1. **Repozitoriyanı klonlayın və qovluğa keçin:**
   ```bash
   git clone https://github.com/SabirliUgur/fintrack-portfolio-manager.git
   cd fintrack-portfolio-manager
   ```

2. **Tətbiqi işə salın (Python 3.10+ kifayətdir, əlavə paket tələb olunmur):**
   ```bash
   python src/main.py
   ```