import logging
import yfinance as yf

# Yanlış simvollar üçün yfinance-in qırmızı 404 xəbərdarlıqlarını gizlədirik
logging.getLogger("yfinance").setLevel(logging.CRITICAL)

KRIPTO_SIMVOLLAR = {"BTC", "ETH", "SOL", "BNB", "XRP", "ADA", "DOGE", "AVAX", "DOT", "TON"}


def canli_qiymet_al(simvol: str) -> float | None:
    temiz_simvol = simvol.strip().upper()
    if not temiz_simvol:
        return None

    # Kriptovalyutalar üçün əvvəlcə -USD cütlüyünü yoxlayırıq
    if temiz_simvol in KRIPTO_SIMVOLLAR:
        namizedler = [f"{temiz_simvol}-USD", temiz_simvol]
    else:
        namizedler = [temiz_simvol, f"{temiz_simvol}-USD"]

    for ticker_adi in namizedler:
        try:
            melumat = yf.Ticker(ticker_adi).history(period="1d")
            if not melumat.empty:
                son_qiymet = float(melumat["Close"].iloc[-1])
                return round(son_qiymet, 2)
        except Exception:
            continue

    return None


if __name__ == "__main__":
    print("BTC canlı qiymət:", canli_qiymet_al("BTC"))
    print("AMZN canlı qiymət:", canli_qiymet_al("AMZN"))
    print("Yanlış simvol testi:", canli_qiymet_al("BELEBIRAKTIVYOXDUR"))