from datetime import datetime, timezone
import json
import urllib.error
import urllib.parse
import urllib.request

KRIPTO_SIMVOLLAR = {
    "BTC", "ETH", "SOL", "BNB", "XRP", "ADA",
    "DOGE", "AVAX", "DOT", "LINK", "MATIC", "LTC",
}

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
}


def _namized_tickerler(simvol: str) -> list[str]:
    temiz_simvol = simvol.strip().upper()
    if not temiz_simvol:
        return []
    if temiz_simvol in KRIPTO_SIMVOLLAR:
        return [f"{temiz_simvol}-USD", temiz_simvol]
    return [temiz_simvol, f"{temiz_simvol}-USD"]


def _tarixi_oxu(tarix_metni: str) -> tuple[datetime, bool] | None:
    """Daxil edilən tarix/saat mətnini datetime obyektinə çevirir."""
    metn = tarix_metni.strip()
    formatlar = [
        ("%Y-%m-%d %H:%M", True),
        ("%d.%m.%Y %H:%M", True),
        ("%Y-%m-%d", False),
        ("%d.%m.%Y", False),
    ]
    for fmt, saat_var in formatlar:
        try:
            dt = datetime.strptime(metn, fmt)
            if not saat_var:
                dt = dt.replace(hour=16, minute=0)
            return dt.replace(tzinfo=timezone.utc), saat_var
        except ValueError:
            continue
    return None


def _yahoo_canli_sorgu(ticker_adi: str) -> float | None:
    kodlanmis = urllib.parse.quote(ticker_adi)
    url = (
        f"https://query1.finance.yahoo.com/v8/finance/chart/"
        f"{kodlanmis}?interval=1d&range=1d"
    )
    sorgu = urllib.request.Request(url, headers=HEADERS)

    with urllib.request.urlopen(sorgu, timeout=6) as cavab:
        data = json.loads(cavab.read().decode("utf-8"))

    neticeler = data.get("chart", {}).get("result")
    if not neticeler:
        return None

    meta = neticeler[0].get("meta", {})
    qiymet = meta.get("regularMarketPrice")

    if qiymet is None:
        baglanislar = (
            neticeler[0]
            .get("indicators", {})
            .get("quote", [{}])[0]
            .get("close", [])
        )
        kecerli = [q for q in baglanislar if q is not None]
        if kecerli:
            qiymet = kecerli[-1]

    return round(float(qiymet), 2) if qiymet is not None else None


def canli_qiymet_al(simvol: str) -> float | None:
    """Aktivin cari bazar qiymətini qaytarır."""
    for ticker_adi in _namized_tickerler(simvol):
        try:
            qiymet = _yahoo_canli_sorgu(ticker_adi)
            if qiymet is not None:
                return qiymet
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ):
            continue
    return None


def _yahoo_tarixi_sorgu(
    ticker_adi: str, hedef_dt: datetime, saat_var: bool
) -> tuple[float, str] | None:
    kodlanmis = urllib.parse.quote(ticker_adi)
    hedef_ts = int(hedef_dt.timestamp())
    indi_ts = int(datetime.now(timezone.utc).timestamp())

    # Son 700 gün ərzində saat dəqiqliyi istənilibsə, 1 saatlıq şamları yoxlayırıq
    if saat_var and (indi_ts - hedef_ts) < 700 * 86400:
        sorgu_planlari = [("1h", hedef_ts - 7200, hedef_ts + 7200)]
    else:
        sorgu_planlari = []

    # Həftəsonu və bayram günlərini əhatə etmək üçün +-4 günlük pəncərə
    sorgu_planlari.append(("1d", hedef_ts - 4 * 86400, hedef_ts + 4 * 86400))

    for interval, p1, p2 in sorgu_planlari:
        url = (
            f"https://query1.finance.yahoo.com/v8/finance/chart/{kodlanmis}"
            f"?period1={p1}&period2={p2}&interval={interval}"
        )
        sorgu = urllib.request.Request(url, headers=HEADERS)

        with urllib.request.urlopen(sorgu, timeout=6) as cavab:
            data = json.loads(cavab.read().decode("utf-8"))

        neticeler = data.get("chart", {}).get("result")
        if not neticeler:
            continue

        zamanlar = neticeler[0].get("timestamp", [])
        baglanislar = (
            neticeler[0]
            .get("indicators", {})
            .get("quote", [{}])[0]
            .get("close", [])
        )

        namized_noqteler: list[tuple[int, float]] = []
        for ts, q in zip(zamanlar, baglanislar):
            if isinstance(ts, (int, float)) and isinstance(q, (int, float)):
                namized_noqteler.append((int(ts), float(q)))

        if not namized_noqteler:
            continue

        en_yaxin_ts, en_yaxin_qiymet = min(
            namized_noqteler, key=lambda x: abs(x[0] - hedef_ts)
        )
        uygun_dt = datetime.fromtimestamp(en_yaxin_ts, tz=timezone.utc)
        fmt = "%Y-%m-%d %H:%M UTC" if interval == "1h" else "%Y-%m-%d"
        return round(en_yaxin_qiymet, 2), uygun_dt.strftime(fmt)
    return None


def tarixi_qiymet_al(simvol: str, tarix_metni: str) -> tuple[float, str] | None:
    """Verilmiş tarixə (və saata) ən yaxın bazar qiymətini və tapılan tarixi qaytarır."""
    oxunmus = _tarixi_oxu(tarix_metni)
    if oxunmus is None:
        return None

    hedef_dt, saat_var = oxunmus

    for ticker_adi in _namized_tickerler(simvol):
        try:
            netice = _yahoo_tarixi_sorgu(ticker_adi, hedef_dt, saat_var)
            if netice is not None:
                return netice
        except (
            urllib.error.URLError,
            urllib.error.HTTPError,
            TimeoutError,
            OSError,
            json.JSONDecodeError,
            KeyError,
            IndexError,
            TypeError,
            ValueError,
        ):
            continue
    return None