import csv
from pathlib import Path

try:
    from market import canli_qiymet_al
    from storage import (
        bronlanmis_miqdar_al,
        emrleri_yukle,
        menfeet_hesabla,
        planlanan_satislari_icra_et,
        portfeli_yukle,
    )
except ImportError:
    from src.market import canli_qiymet_al
    from src.storage import (
        bronlanmis_miqdar_al,
        emrleri_yukle,
        menfeet_hesabla,
        planlanan_satislari_icra_et,
        portfeli_yukle,
    )

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
HESABAT_FAYLI = DATA_DIR / "portfel_hesabati.csv"


def canli_qiymetleri_topla(portfel: list[dict]) -> dict[str, float]:
    """Portfeldəki və PENDING əmrlərdəki bütün simvollar üçün canlı qiymətləri çəkir."""
    simvollar = {a.get("simvol", "").upper() for a in portfel if a.get("simvol")}
    for emr in emrleri_yukle():
        if emr.get("status") == "PENDING" and emr.get("simvol"):
            simvollar.add(emr["simvol"].upper())

    qiymetler: dict[str, float] = {}
    for simvol in simvollar:
        qiymet = canli_qiymet_al(simvol)
        if qiymet is not None:
            qiymetler[simvol] = qiymet
    return qiymetler


def portfel_analizi_et(portfel: list[dict]) -> dict:
    """Əvvəlcə limit satış əmrlərini yoxlayır, sonra yenilənmiş portfelin analizini aparır."""
    qiymetler = canli_qiymetleri_topla(portfel)
    icra_edilen_emrler = planlanan_satislari_icra_et(qiymetler)

    if icra_edilen_emrler:
        portfel = portfeli_yukle()

    setirler = []
    umumi_maya = 0.0
    umumi_cari_deyer = 0.0

    for aktiv in portfel:
        simvol = aktiv.get("simvol", "N/A").upper()
        miqdar = float(aktiv.get("miqdar", 0.0))
        alis_qiymeti = float(aktiv.get("alis_qiymeti", 0.0))
        alis_tarixi = aktiv.get("alis_tarixi", "Qeyd edilməyib")
        bronlanmis = bronlanmis_miqdar_al(simvol)
        serbest = round(max(0.0, miqdar - bronlanmis), 6)

        if simvol in qiymetler:
            cari_qiymet = qiymetler[simvol]
            qiymet_menbeyi = "Canlı"
        else:
            cari_qiymet = alis_qiymeti
            qiymet_menbeyi = "Alış (Oflayn)"

        maya, cari_deyer, menfeet, menfeet_faiz = menfeet_hesabla(
            miqdar, alis_qiymeti, cari_qiymet
        )

        umumi_maya += maya
        umumi_cari_deyer += cari_deyer

        setirler.append(
            {
                "simvol": simvol,
                "miqdar": miqdar,
                "serbest_miqdar": serbest,
                "bronlanmis_miqdar": bronlanmis,
                "alis_tarixi": alis_tarixi,
                "alis_qiymeti": alis_qiymeti,
                "cari_qiymet": cari_qiymet,
                "qiymet_menbeyi": qiymet_menbeyi,
                "maya": maya,
                "cari_deyer": cari_deyer,
                "menfeet": menfeet,
                "menfeet_faiz": menfeet_faiz,
                "pay_faizi": 0.0,
            }
        )

    risk_xeberdarliqlari = []
    for s in setirler:
        if umumi_cari_deyer > 0:
            pay = round((s["cari_deyer"] / umumi_cari_deyer) * 100, 2)
        else:
            pay = 0.0
        s["pay_faizi"] = pay

        if pay > 50.0:
            risk_xeberdarliqlari.append(
                f"DİQQƏT: {s['simvol']} portfelin {pay}%-ni təşkil edir (50% limitini aşır)!"
            )

    umumi_maya = round(umumi_maya, 2)
    umumi_cari_deyer = round(umumi_cari_deyer, 2)
    umumi_menfeet = round(umumi_cari_deyer - umumi_maya, 2)
    umumi_menfeet_faiz = (
        round((umumi_menfeet / umumi_maya) * 100, 2) if umumi_maya > 0 else 0.0
    )

    return {
        "setirler": setirler,
        "umumi_maya": umumi_maya,
        "umumi_cari_deyer": umumi_cari_deyer,
        "umumi_menfeet": umumi_menfeet,
        "umumi_menfeet_faiz": umumi_menfeet_faiz,
        "risk_xeberdarliqlari": risk_xeberdarliqlari,
        "icra_edilen_emrler": icra_edilen_emrler,
    }


def csv_ixrac_et(analiz: dict) -> Path:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    basliqlar = [
        "Simvol",
        "Ümumi Miqdar",
        "Sərbəst Miqdar",
        "Bronlanmış Miqdar",
        "Alış Tarixi",
        "Alış Qiyməti ($)",
        "Cari Qiymət ($)",
        "Maya Dəyəri ($)",
        "Cari Dəyər ($)",
        "Mənfəət/Zərər ($)",
        "Mənfəət/Zərər (%)",
        "Portfel Payı (%)",
    ]

    with open(HESABAT_FAYLI, "w", newline="", encoding="utf-8-sig") as f:
        yazici = csv.writer(f)
        yazici.writerow(basliqlar)
        for s in analiz["setirler"]:
            yazici.writerow(
                [
                    s["simvol"],
                    s["miqdar"],
                    s["serbest_miqdar"],
                    s["bronlanmis_miqdar"],
                    s["alis_tarixi"],
                    s["alis_qiymeti"],
                    s["cari_qiymet"],
                    s["maya"],
                    s["cari_deyer"],
                    s["menfeet"],
                    s["menfeet_faiz"],
                    s["pay_faizi"],
                ]
            )
    return HESABAT_FAYLI