def portfel_icmali(portfel: list[dict]) -> dict:
    umumi_maya = 0.0
    umumi_deyer = 0.0

    for aktiv in portfel:
        umumi_maya += aktiv["alis_qiymeti"] * aktiv["miqdar"]
        umumi_deyer += aktiv["cari_qiymet"] * aktiv["miqdar"]

    xalis_menfeet = umumi_deyer - umumi_maya

    if umumi_maya > 0:
        menfeet_faizi = (xalis_menfeet / umumi_maya) * 100
    else:
        menfeet_faizi = 0.0

    return {
        "umumi_maya": round(umumi_maya, 2),
        "umumi_deyer": round(umumi_deyer, 2),
        "xalis_menfeet": round(xalis_menfeet, 2),
        "menfeet_faizi": round(menfeet_faizi, 2)
    }

def risk_analizi(portfel: list[dict], maksimum_ceki_faizi: float = 50.0) -> list[dict]:
    umumi_deyer = portfel_icmali(portfel)["umumi_deyer"]
    if umumi_deyer <= 0:
        return []
    riskli_aktivler = []
    for aktiv in portfel:
        aktiv_deyeri = aktiv["cari_qiymet"] * aktiv["miqdar"]
        ceki_faizi = (aktiv_deyeri / umumi_deyer) * 100
        if ceki_faizi > maksimum_ceki_faizi:
            riskli_aktivler.append({
                "simvol": aktiv["simvol"],
                "ceki_faizi": round(ceki_faizi, 2),
                "limit": maksimum_ceki_faizi
            })
    return riskli_aktivler

if __name__ == "__main__":
    test_portfel = [
        {"simvol": "BTC", "alis_qiymeti": 60000.0, "cari_qiymet": 65000.0, "miqdar": 0.5},  # Dəyəri: 32,500
        {"simvol": "NVDA", "alis_qiymeti": 120.0, "cari_qiymet": 135.5, "miqdar": 10.0}  # Dəyəri: 1,355
    ]
    print("Portfel icmalı:", portfel_icmali(test_portfel))
    print("Risk auditi:", risk_analizi(test_portfel))
    print("Boş portfel auditi:", risk_analizi([]))