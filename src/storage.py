from datetime import datetime
import json
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
PORTFEL_FAYLI = DATA_DIR / "portfel.json"
EMRLER_FAYLI = DATA_DIR / "limit_emrler.json"


def _json_siyahisi_yukle(fayl_yolu: Path) -> list[dict]:
    if not fayl_yolu.exists():
        return []
    try:
        with open(fayl_yolu, "r", encoding="utf-8") as f:
            melumat = json.load(f)
            return melumat if isinstance(melumat, list) else []
    except (OSError, json.JSONDecodeError):
        return []


def _json_siyahisi_saxla(fayl_yolu: Path, melumat: list[dict]) -> None:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(fayl_yolu, "w", encoding="utf-8") as f:
        json.dump(melumat, f, ensure_ascii=False, indent=4)


def portfeli_yukle() -> list[dict]:
    return _json_siyahisi_yukle(PORTFEL_FAYLI)


def portfeli_saxla(portfel: list[dict]) -> None:
    _json_siyahisi_saxla(PORTFEL_FAYLI, portfel)


def emrleri_yukle() -> list[dict]:
    return _json_siyahisi_yukle(EMRLER_FAYLI)


def emrleri_saxla(emrler: list[dict]) -> None:
    _json_siyahisi_saxla(EMRLER_FAYLI, emrler)


def menfeet_hesabla(
    miqdar: float, alis_qiymeti: float, cari_qiymet: float
) -> tuple[float, float, float, float]:
    """Maya dəyəri, cari dəyər, xalis mənfəət/zərər ($) və faiz (%) qaytarır."""
    maya = round(miqdar * alis_qiymeti, 2)
    cari_deyer = round(miqdar * cari_qiymet, 2)
    menfeet = round(cari_deyer - maya, 2)
    menfeet_faiz = (
        round(((cari_qiymet - alis_qiymeti) / alis_qiymeti) * 100, 2)
        if alis_qiymeti > 0
        else 0.0
    )
    return maya, cari_deyer, menfeet, menfeet_faiz


def bronlanmis_miqdar_al(simvol: str) -> float:
    """Gözləmədə (PENDING) olan limit satış əmrlərindəki ümumi miqdarı qaytarır."""
    temiz_simvol = simvol.strip().upper()
    cem = 0.0
    for emr in emrleri_yukle():
        if (
            emr.get("simvol", "").upper() == temiz_simvol
            and emr.get("status") == "PENDING"
        ):
            cem += float(emr.get("miqdar", 0.0))
    return round(cem, 6)


def aktiv_elave_et(
    simvol: str, miqdar: float, alis_qiymeti: float, alis_tarixi: str = "Qeyd edilməyib"
) -> None:
    portfel = portfeli_yukle()
    temiz_simvol = simvol.strip().upper()

    for aktiv in portfel:
        if aktiv.get("simvol", "").upper() == temiz_simvol:
            kohne_miqdar = float(aktiv.get("miqdar", 0.0))
            kohne_qiymet = float(aktiv.get("alis_qiymeti", 0.0))
            yeni_miqdar = round(kohne_miqdar + miqdar, 6)

            if yeni_miqdar > 0:
                orta_qiymet = (
                    (kohne_miqdar * kohne_qiymet) + (miqdar * alis_qiymeti)
                ) / yeni_miqdar
                aktiv["alis_qiymeti"] = round(orta_qiymet, 2)

            aktiv["miqdar"] = yeni_miqdar
            if alis_tarixi != "Qeyd edilməyib":
                aktiv["alis_tarixi"] = alis_tarixi
            portfeli_saxla(portfel)
            return

    portfel.append(
        {
            "simvol": temiz_simvol,
            "miqdar": round(miqdar, 6),
            "alis_qiymeti": round(alis_qiymeti, 2),
            "alis_tarixi": alis_tarixi,
        }
    )
    portfeli_saxla(portfel)


def aktiv_sat_ve_ya_sil(
    simvol: str, satilan_miqdar: float, satis_qiymeti: float
) -> dict | None:
    """Aktivi dərhal satır (hissəvi və ya tam) və əməliyyat hesabatını qaytarır."""
    portfel = portfeli_yukle()
    temiz_simvol = simvol.strip().upper()

    for indeks, aktiv in enumerate(portfel):
        if aktiv.get("simvol", "").upper() == temiz_simvol:
            movcud_miqdar = float(aktiv.get("miqdar", 0.0))
            alis_qiymeti = float(aktiv.get("alis_qiymeti", 0.0))

            if satilan_miqdar <= 0 or satilan_miqdar > movcud_miqdar + 1e-8:
                return None

            qalan_miqdar = round(movcud_miqdar - satilan_miqdar, 6)
            _, satis_meblegi, real_menfeet, real_faiz = menfeet_hesabla(
                satilan_miqdar, alis_qiymeti, satis_qiymeti
            )

            if qalan_miqdar <= 1e-8:
                qalan_miqdar = 0.0
                portfel.pop(indeks)
                tam_silindi = True
            else:
                aktiv["miqdar"] = qalan_miqdar
                tam_silindi = False

            portfeli_saxla(portfel)
            return {
                "simvol": temiz_simvol,
                "satilan_miqdar": round(satilan_miqdar, 6),
                "qalan_miqdar": qalan_miqdar,
                "alis_qiymeti": alis_qiymeti,
                "satis_qiymeti": round(satis_qiymeti, 2),
                "satis_meblegi": satis_meblegi,
                "real_menfeet": real_menfeet,
                "real_faiz": real_faiz,
                "tam_silindi": tam_silindi,
            }

    return None


def limit_satis_elave_et(
    simvol: str, miqdar: float, hedef_qiymet: float, yaradilma_cari_qiymet: float
) -> dict | None:
    """Bazar qiymətindən yuxarı satışlar üçün PENDING limit əmri yaradır."""
    temiz_simvol = simvol.strip().upper()
    portfel = portfeli_yukle()
    aktiv = next(
        (a for a in portfel if a.get("simvol", "").upper() == temiz_simvol), None
    )
    if aktiv is None:
        return None

    movcud = float(aktiv.get("miqdar", 0.0))
    bronlanmis = bronlanmis_miqdar_al(temiz_simvol)
    serbest = round(movcud - bronlanmis, 6)

    if miqdar <= 0 or miqdar > serbest + 1e-8:
        return None

    emrler = emrleri_yukle()
    yeni_id = max((int(e.get("id", 0)) for e in emrler), default=0) + 1
    indi = datetime.now().strftime("%Y-%m-%d %H:%M")

    yeni_emr = {
        "id": yeni_id,
        "simvol": temiz_simvol,
        "miqdar": round(miqdar, 6),
        "hedef_qiymet": round(hedef_qiymet, 2),
        "yaradilma_qiymeti": round(yaradilma_cari_qiymet, 2),
        "yaradilma_tarixi": indi,
        "status": "PENDING",
        "icra_qiymeti": None,
        "icra_tarixi": None,
        "real_menfeet": None,
    }
    emrler.append(yeni_emr)
    emrleri_saxla(emrler)
    return yeni_emr


def limit_emri_legv_et(emr_id: int) -> bool:
    """PENDING statuslu əmri ləğv edir və bronlanmış miqdarı azad edir."""
    emrler = emrleri_yukle()
    for emr in emrler:
        if int(emr.get("id", 0)) == emr_id and emr.get("status") == "PENDING":
            emr["status"] = "CANCELLED"
            emr["icra_tarixi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
            emrleri_saxla(emrler)
            return True
    return False


def planlanan_satislari_icra_et(qiymet_cedveli: dict[str, float]) -> list[dict]:
    """Canlı qiymət hədəf qiymətə çatdıqda PENDING əmrləri avtomatik icra edir."""
    emrler = emrleri_yukle()
    icra_edilenler = []
    deyisiklik_var = False

    for emr in emrler:
        if emr.get("status") != "PENDING":
            continue

        simvol = emr.get("simvol", "").upper()
        cari_qiymet = qiymet_cedveli.get(simvol)
        hedef_qiymet = float(emr.get("hedef_qiymet", 0.0))
        miqdar = float(emr.get("miqdar", 0.0))

        if cari_qiymet is not None and cari_qiymet >= hedef_qiymet:
            hesabat = aktiv_sat_ve_ya_sil(simvol, miqdar, cari_qiymet)
            if hesabat is not None:
                emr["status"] = "EXECUTED"
                emr["icra_qiymeti"] = cari_qiymet
                emr["icra_tarixi"] = datetime.now().strftime("%Y-%m-%d %H:%M")
                emr["real_menfeet"] = hesabat["real_menfeet"]
                deyisiklik_var = True
                icra_edilenler.append({**emr, **hesabat})
            else:
                emr["status"] = "FAILED"
                deyisiklik_var = True

    if deyisiklik_var:
        emrleri_saxla(emrler)

    return icra_edilenler