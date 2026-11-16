import csv
import json
from pathlib import Path

def portfeli_yukle(fayl_yolu: str = "data/portfel.json") -> list[dict]:
    try:
        with open(fayl_yolu, "r", encoding="utf-8") as fayl:
            return json.load(fayl)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        return []

def portfeli_saxla(portfel: list[dict], fayl_yolu: str = "data/portfel.json") -> bool:
    with open(fayl_yolu, "w", encoding="utf-8") as fayl:
        json.dump(portfel, fayl, indent=4, ensure_ascii=False)
    return True

def aktiv_elave_et(
    simvol: str,
    alis_qiymeti: float | int,
    cari_qiymet: float | int,
    miqdar: float | int,
    fayl_yolu: str = "data/portfel.json"
) -> bool:
    temiz_simvol = simvol.strip().upper()
    if not (temiz_simvol and alis_qiymeti > 0 and cari_qiymet > 0 and miqdar > 0): #if not temiz_simvol or alis_qiymeti <= 0 or cari_qiymet <= 0 or miqdar <= 0:
        return False

    portfel = portfeli_yukle(fayl_yolu)
    for aktiv in portfel:
        if aktiv["simvol"] == temiz_simvol:
            return False

    yeni_aktiv = {
        "simvol": temiz_simvol,
        "alis_qiymeti": float(alis_qiymeti),
        "cari_qiymet": float(cari_qiymet),
        "miqdar": float(miqdar)
    }
    portfel.append(yeni_aktiv)
    return portfeli_saxla(portfel, fayl_yolu)

def aktiv_sil(simvol: str, fayl_yolu: str = "data/portfel.json") -> bool:
    temiz_simvol = simvol.strip().upper()
    if not temiz_simvol:
        return False

    portfel = portfeli_yukle(fayl_yolu)
    for aktiv in portfel:
        if aktiv["simvol"] == temiz_simvol:
            portfel.remove(aktiv)
            return portfeli_saxla(portfel, fayl_yolu)
    return False

def qiymet_yenile(
    simvol: str,
    yeni_qiymet: float | int,
    fayl_yolu: str = "data/portfel.json"
) -> bool:
    temiz_simvol = simvol.strip().upper()
    if not (temiz_simvol and yeni_qiymet > 0):
        return False
    portfel = portfeli_yukle(fayl_yolu)
    for aktiv in portfel:
        if aktiv["simvol"] == temiz_simvol:
            aktiv["cari_qiymet"] = float(yeni_qiymet)
            return portfeli_saxla(portfel, fayl_yolu)
    return False

def hesabati_csv_ixrac_et(
    portfel: list[dict],
    fayl_yolu: str = "data/portfel_hesabati.csv"
) -> bool:
    if not portfel:
        return False

    yol = Path(fayl_yolu)
    yol.parent.mkdir(parents=True, exist_ok=True)

    # utf-8-sig kodlaması faylın Excel-də xətasız açılmasını təmin edir
    with open(yol, mode="w", newline="", encoding="utf-8-sig") as fayl:
        yazici = csv.writer(fayl)
        yazici.writerow([
            "Simvol",
            "Miqdar",
            "Alis Qiymeti ($)",
            "Cari Qiymet ($)",
            "Umumi Maya ($)",
            "Cari Deyer ($)",
            "Menfeet/Zerer ($)",
            "Menfeet Faizi (%)"
        ])

        for aktiv in portfel:
            maya = aktiv["alis_qiymeti"] * aktiv["miqdar"]
            deyer = aktiv["cari_qiymet"] * aktiv["miqdar"]
            menfeet = deyer - maya
            faiz = (menfeet / maya * 100) if maya > 0 else 0.0

            yazici.writerow([
                aktiv["simvol"],
                aktiv["miqdar"],
                round(aktiv["alis_qiymeti"], 2),
                round(aktiv["cari_qiymet"], 2),
                round(maya, 2),
                round(deyer, 2),
                round(menfeet, 2),
                round(faiz, 2)
            ])

    return True


if __name__ == "__main__":
    print("1. Cari portfel:", portfeli_yukle())
    print("2. BTC qiyməti yeniləndi:", qiymet_yenile("btc", 72000))
    print("3. Mənfi qiymət cəhdi:", qiymet_yenile("BTC", -100))
    print("4. Yenilənmiş portfel:", portfeli_yukle())
