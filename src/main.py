try:
    from analytics import (
        canli_qiymetleri_topla,
        csv_ixrac_et,
        portfel_analizi_et,
    )
    from market import canli_qiymet_al, tarixi_qiymet_al
    from storage import (
        aktiv_elave_et,
        aktiv_sat_ve_ya_sil,
        bronlanmis_miqdar_al,
        emrleri_yukle,
        limit_emri_legv_et,
        limit_satis_elave_et,
        planlanan_satislari_icra_et,
        portfeli_yukle,
    )
except ImportError:
    from src.analytics import (
        canli_qiymetleri_topla,
        csv_ixrac_et,
        portfel_analizi_et,
    )
    from src.market import canli_qiymet_al, tarixi_qiymet_al
    from src.storage import (
        aktiv_elave_et,
        aktiv_sat_ve_ya_sil,
        bronlanmis_miqdar_al,
        emrleri_yukle,
        limit_emri_legv_et,
        limit_satis_elave_et,
        planlanan_satislari_icra_et,
        portfeli_yukle,
    )


def _musbet_eded_al(sorgu: str) -> float | None:
    metn = input(sorgu).strip().replace(",", ".")
    try:
        deyer = float(metn)
        return deyer if deyer > 0 else None
    except ValueError:
        return None


def _menfeet_formatla(mebleg: float, faiz: float) -> str:
    isare = "+" if mebleg >= 0 else ""
    return f"{isare}{mebleg:.2f}$ ({isare}{faiz:.2f}%)"


def _avtomatik_icra_bildirisi_goster(icra_edilenler: list[dict]) -> None:
    if not icra_edilenler:
        return
    print("\n" + "*" * 68)
    print("  [AVTOMATİK İCRA] Hədəf qiymətə çatan limit satış əmrləri tamamlandı:")
    for emr in icra_edilenler:
        pz = _menfeet_formatla(emr["real_menfeet"], emr["real_faiz"])
        print(
            f"  • Əmr #{emr['id']}: {emr['satilan_miqdar']:g} {emr['simvol']} "
            f"(Hədəf: {emr['hedef_qiymet']:.2f}$ -> İcra: {emr['satis_qiymeti']:.2f}$) | "
            f"Real P&L: {pz}"
        )
    print("*" * 68)


def menyu_goster() -> None:
    print("\n" + "=" * 58)
    print("   FINTRACK v2.0 — PORTFEL, LİMİT ƏMR VƏ RİSK AUDİTİ")
    print("=" * 58)
    print("1. Portfelə bax (Canlı Qiymətlər, P&L və Limit Yoxlanışı)")
    print("2. Yeni aktiv əlavə et (Tarixə görə avtomatik qiymət)")
    print("3. Portfel konsentrasiya riskini yoxla (Audit)")
    print("4. Hesabatı CSV (Excel) faylına ixrac et")
    print("5. Aktiv sat (Bazar / Limit əmri) və ya portfeldən sil")
    print("6. Planlanan limit satış əmrlərinə bax / Ləğv et")
    print("0. Çıxış")
    print("-" * 58)


def portfeli_goster() -> None:
    portfel = portfeli_yukle()
    if not portfel and not any(e.get("status") == "PENDING" for e in emrleri_yukle()):
        print("\n[Məlumat] Portfeliniz hazırda boşdur.")
        return

    print("\nBazar qiymətləri və planlanan əmrlər yoxlanılır...")
    analiz = portfel_analizi_et(portfel)
    _avtomatik_icra_bildirisi_goster(analiz["icra_edilen_emrler"])

    if not analiz["setirler"]:
        print("\n[Məlumat] Aktiv portfelinizdə mövqe qalmayıb.")
        return

    print("\n" + "-" * 106)
    print(
        f"{'Simvol':<8} {'Ümumi':<9} {'Sərbəst':<9} {'Alış ($)':<10} {'Cari ($)':<10} "
        f"{'Dəyər ($)':<11} {'Mənfəət / Zərər':<22} {'Pay (%)':<8}"
    )
    print("-" * 106)

    for s in analiz["setirler"]:
        pz_metni = _menfeet_formatla(s["menfeet"], s["menfeet_faiz"])
        print(
            f"{s['simvol']:<8} {s['miqdar']:<9.4g} {s['serbest_miqdar']:<9.4g} "
            f"{s['alis_qiymeti']:<10.2f} {s['cari_qiymet']:<10.2f} "
            f"{s['cari_deyer']:<11.2f} {pz_metni:<22} {s['pay_faizi']:<7.1f}%"
        )

    print("-" * 106)
    umumi_pz = _menfeet_formatla(
        analiz["umumi_menfeet"], analiz["umumi_menfeet_faiz"]
    )
    print(f"Ümumi Maya Dəyəri:   {analiz['umumi_maya']:.2f}$")
    print(f"Ümumi Cari Dəyər:    {analiz['umumi_cari_deyer']:.2f}$")
    print(f"Ümumi Mənfəət/Zərər: {umumi_pz}")


def yeni_aktiv_axini() -> None:
    simvol = input("\nAktiv simvolu (məs: AMZN, ETH, BTC): ").strip().upper()
    if not simvol:
        print("[Xəta] Simvol boş ola bilməz.")
        return

    miqdar = _musbet_eded_al("Alınan miqdar (məs: 2 və ya 0.3): ")
    if miqdar is None:
        print("[Xəta] Miqdar müsbət ədəd olmalıdır.")
        return

    print("Alış tarixini daxil edin (məs: 2025-05-15 və ya 15.05.2025 16:30)")
    tarix_giris = input("Tarix (boş buraxsanız cari bazar qiyməti yoxlanılacaq): ").strip()

    teklif_qiymet = None
    qeyd_tarix = "Qeyd edilməyib"

    if tarix_giris:
        print("Tarixi bazar məlumatı axtarılır...")
        tapilan = tarixi_qiymet_al(simvol, tarix_giris)
        if tapilan is not None:
            teklif_qiymet, uygun_tarix = tapilan
            qeyd_tarix = uygun_tarix
            print(f"[Tapıldı] {uygun_tarix} tarixinə uyğun bazar qiyməti: {teklif_qiymet:.2f}$")
        else:
            print("[Xəbərdarlıq] Daxil edilən tarix üzrə qiymət tapılmadı.")
    else:
        canli = canli_qiymet_al(simvol)
        if canli is not None:
            teklif_qiymet = canli
            print(f"[Canlı Bazar] {simvol} cari qiyməti: {teklif_qiymet:.2f}$")

    if teklif_qiymet is not None:
        secim = input(
            f"Alış qiyməti kimi {teklif_qiymet:.2f}$ təsdiqlənsin? "
            "(Enter = Bəli, və ya öz qiymətinizi yazın): "
        ).strip().replace(",", ".")
        if not secim:
            alis_qiymeti = teklif_qiymet
        else:
            try:
                alis_qiymeti = float(secim)
                if alis_qiymeti <= 0:
                    raise ValueError
            except ValueError:
                print("[Xəta] Yanlış qiymət daxil edildi.")
                return
    else:
        alis_qiymeti = _musbet_eded_al("Alış qiymətini ($) əl ilə daxil edin: ")
        if alis_qiymeti is None:
            print("[Xəta] Qiymət müsbət ədəd olmalıdır.")
            return

    aktiv_elave_et(simvol, miqdar, alis_qiymeti, qeyd_tarix)
    print(f"[Uğurlu] {miqdar:g} vahid {simvol} ({alis_qiymeti:.2f}$) portfelə əlavə edildi.")


def risk_auditi_goster() -> None:
    portfel = portfeli_yukle()
    if not portfel:
        print("\n[Məlumat] Analiz üçün portfeldə aktiv yoxdur.")
        return

    analiz = portfel_analizi_et(portfel)
    _avtomatik_icra_bildirisi_goster(analiz["icra_edilen_emrler"])

    print("\n--- PORTFEL KONSENTRASİYA RİSKİ AUDİTİ ---")
    for s in analiz["setirler"]:
        print(f"• {s['simvol']}: {s['pay_faizi']:.1f}% ({s['cari_deyer']:.2f}$)")

    if analiz["risk_xeberdarliqlari"]:
        print()
        for xeberdarliq in analiz["risk_xeberdarliqlari"]:
            print(f"⚠ {xeberdarliq}")
    else:
        print("\n[OK] Portfel balanslaşdırılıb — heç bir aktiv 50% limitini aşmır.")


def csv_hesabat_axini() -> None:
    portfel = portfeli_yukle()
    if not portfel:
        print("\n[Məlumat] İxrac ediləcək aktiv yoxdur.")
        return

    analiz = portfel_analizi_et(portfel)
    _avtomatik_icra_bildirisi_goster(analiz["icra_edilen_emrler"])
    fayl_yolu = csv_ixrac_et(analiz)
    print(f"\n[Uğurlu] Hesabat yaradıldı: {fayl_yolu}")


def aktiv_satis_axini() -> None:
    portfel = portfeli_yukle()
    if not portfel:
        print("\n[Məlumat] Portfeliniz boşdur.")
        return

    print("\n--- AKTİV SATIŞI (BAZAR VƏ YA LİMİT ƏMRİ) ---")
    for idx, aktiv in enumerate(portfel, start=1):
        simvol = aktiv["simvol"].upper()
        umumi = float(aktiv["miqdar"])
        bron = bronlanmis_miqdar_al(simvol)
        serbest = round(max(0.0, umumi - bron), 6)
        print(
            f"{idx}. {simvol} — Ümumi: {umumi:g} | Sərbəst: {serbest:g} "
            f"(Bronlanmış: {bron:g}) | Orta alış: {aktiv['alis_qiymeti']:.2f}$"
        )

    secim = input("\nSatmaq istədiyiniz aktivin nömrəsi və ya simvolu: ").strip().upper()
    secilen_aktiv = None

    if secim.isdigit():
        indeks = int(secim) - 1
        if 0 <= indeks < len(portfel):
            secilen_aktiv = portfel[indeks]
    else:
        for aktiv in portfel:
            if aktiv["simvol"].upper() == secim:
                secilen_aktiv = aktiv
                break

    if secilen_aktiv is None:
        print("[Xəta] Belə bir aktiv tapılmadı.")
        return

    simvol = secilen_aktiv["simvol"].upper()
    movcud_miqdar = float(secilen_aktiv["miqdar"])
    bron_miqdar = bronlanmis_miqdar_al(simvol)
    serbest_miqdar = round(max(0.0, movcud_miqdar - bron_miqdar), 6)

    if serbest_miqdar <= 1e-8:
        print(
            f"[Xəbərdarlıq] {simvol} üzrə bütün balansınız ({bron_miqdar:g} vahid) "
            "planlanan limit əmrlərində bronlanıb. Yeni satış üçün əvvəlcə əmri ləğv edin (Menyu 6)."
        )
        return

    miqdar_metni = input(
        f"Neçə vahid {simvol} satmaq istəyirsiniz? "
        f"(Maks sərbəst: {serbest_miqdar:g} | Hamısı üçün 'hamisi' yazın): "
    ).strip().lower().replace(",", ".")

    if miqdar_metni in {"hamisi", "hamısı", "all"}:
        satilan_miqdar = serbest_miqdar
    else:
        try:
            satilan_miqdar = float(miqdar_metni)
        except ValueError:
            print("[Xəta] Yanlış miqdar daxil edildi.")
            return

    if satilan_miqdar <= 0 or satilan_miqdar > serbest_miqdar + 1e-8:
        print(f"[Xəta] Miqdar 0 ilə {serbest_miqdar:g} (sərbəst balans) arasında olmalıdır.")
        return

    canli_qiymet = canli_qiymet_al(simvol)

    if canli_qiymet is not None:
        qiymet_giris = input(
            f"{simvol} cari bazar qiyməti {canli_qiymet:.2f}$-dır.\n"
            "• Dərhal bazar qiyməti ilə satmaq üçün Enter basın\n"
            "• Planlanan limit satış qiyməti təyin etmək üçün hədəf qiyməti yazın: "
        ).strip().replace(",", ".")

        if not qiymet_giris:
            hedef_qiymet = canli_qiymet
        else:
            try:
                hedef_qiymet = float(qiymet_giris)
                if hedef_qiymet <= 0:
                    raise ValueError
            except ValueError:
                print("[Xəta] Yanlış qiymət daxil edildi.")
                return

        # 1. Hədəf qiymət cari bazar qiymətindən YÜKSƏKDİRSƏ -> Dərhal satılmır, LIMIT ORDER olur
        if hedef_qiymet > canli_qiymet + 1e-8:
            emr = limit_satis_elave_et(simvol, satilan_miqdar, hedef_qiymet, canli_qiymet)
            if emr is None:
                print("[Xəta] Limit əmri yaradıla bilmədi.")
                return

            print("\n--- PLANLANAN LİMİT SATIŞ ƏMRİ QEYDƏ ALINDI ---")
            print(f"Əmr ID:               #{emr['id']} (Status: PENDING / Gözləmədə)")
            print(f"Aktiv:                {emr['simvol']}")
            print(f"Bronlanan miqdar:     {emr['miqdar']:g} vahid")
            print(f"Cari bazar qiyməti:   {canli_qiymet:.2f}$")
            print(f"Hədəf satış qiyməti:  {emr['hedef_qiymet']:.2f}$")
            print(
                f"Qeyd: Cari bazar qiyməti hədəfdən aşağı olduğu üçün satış dərhal icra olunmadı. "
                f"{simvol} qiyməti {emr['hedef_qiymet']:.2f}$ səviyyəsinə çatdıqda əməliyyat avtomatik tamamlanacaq."
            )
            return

        # 2. Hədəf qiymət cari bazar qiymətinə BƏRABƏR və ya AŞAĞIDIRSA -> Dərhal bazar qiyməti ilə icra olunur
        if hedef_qiymet < canli_qiymet - 1e-8:
            print(
                f"\n[Bazar İcrası] Cari bazar qiyməti ({canli_qiymet:.2f}$) daxil etdiyiniz "
                f"minimum qiymətdən ({hedef_qiymet:.2f}$) yüksək olduğu üçün əmr dərhal "
                "cari bazar qiyməti ilə icra edilir."
            )
        icra_qiymeti = canli_qiymet

    else:
        print("[Xəbərdarlıq] Canlı bazar qiyməti alına bilmədi (Oflayn rejim).")
        icra_qiymeti = _musbet_eded_al("Satış qiymətini ($) əl ilə daxil edin: ")
        if icra_qiymeti is None:
            print("[Xəta] Qiymət müsbət ədəd olmalıdır.")
            return

    hesabat = aktiv_sat_ve_ya_sil(simvol, satilan_miqdar, icra_qiymeti)
    if hesabat is None:
        print("[Xəta] Əməliyyat zamanı xəta baş verdi.")
        return

    pz_metni = _menfeet_formatla(hesabat["real_menfeet"], hesabat["real_faiz"])
    print("\n--- BAZAR SATIŞ QƏBZİ (İCRA EDİLDİ) ---")
    print(f"Aktiv:                {hesabat['simvol']}")
    print(f"Satılan miqdar:       {hesabat['satilan_miqdar']:g} vahid")
    print(f"İcra qiyməti:         {hesabat['satis_qiymeti']:.2f}$")
    print(f"Ümumi satış məbləği:  {hesabat['satis_meblegi']:.2f}$")
    print(f"Real Mənfəət/Zərər:   {pz_metni}")
    if hesabat["tam_silindi"]:
        print("Status:               Aktiv tam satıldı və portfeldən çıxarıldı.")
    else:
        print(f"Portfeldə qalan pay:  {hesabat['qalan_miqdar']:g} vahid")


def limit_emrleri_menyusu() -> None:
    portfel = portfeli_yukle()
    emrler = emrleri_yukle()
    if not emrler:
        print("\n[Məlumat] Heç bir planlanan limit satış əmri yoxdur.")
        return

    # Əvvəlcə PENDING əmrlər üçün canlı qiymətləri yoxlayırıq
    if any(e.get("status") == "PENDING" for e in emrler):
        print("\nPlanlanan əmrlər üzrə canlı bazar qiymətləri yoxlanılır...")
        qiymetler = canli_qiymetleri_topla(portfel)
        icra_edilenler = planlanan_satislari_icra_et(qiymetler)
        _avtomatik_icra_bildirisi_goster(icra_edilenler)
        emrler = emrleri_yukle()

    print("\n" + "-" * 92)
    print(
        f"{'ID':<5} {'Simvol':<8} {'Miqdar':<10} {'Hədəf ($)':<12} "
        f"{'Status':<12} {'İcra ($)':<11} {'Tarix':<18}"
    )
    print("-" * 92)
    for e in emrler:
        icra_str = f"{e['icra_qiymeti']:.2f}" if e.get("icra_qiymeti") is not None else "-"
        tarix_str = e.get("icra_tarixi") or e.get("yaradilma_tarixi", "-")
        print(
            f"#{e['id']:<4} {e['simvol']:<8} {e['miqdar']:<10.4g} "
            f"{e['hedef_qiymet']:<12.2f} {e['status']:<12} {icra_str:<11} {tarix_str:<18}"
        )
    print("-" * 92)

    pending_var = any(e.get("status") == "PENDING" for e in emrler)
    if pending_var:
        legv_giris = input(
            "Ləğv etmək istədiyiniz PENDING əmrin ID nömrəsi (Geri qayıtmaq üçün Enter): "
        ).strip().lstrip("#")
        if legv_giris.isdigit():
            if limit_emri_legv_et(int(legv_giris)):
                print(f"[Uğurlu] Əmr #{legv_giris} ləğv edildi və bronlanmış miqdar azad edildi.")
            else:
                print("[Xəta] Bu ID ilə aktiv (PENDING) əmr tapılmadı.")


def main() -> None:
    while True:
        menyu_goster()
        secim = input("Seçiminiz (0-6): ").strip()

        if secim == "1":
            portfeli_goster()
        elif secim == "2":
            yeni_aktiv_axini()
        elif secim == "3":
            risk_auditi_goster()
        elif secim == "4":
            csv_hesabat_axini()
        elif secim == "5":
            aktiv_satis_axini()
        elif secim == "6":
            limit_emrleri_menyusu()
        elif secim == "0":
            print("FinTrack bağlanır. Uğurlu investisiyalar!")
            break
        else:
            print("[Xəta] Yanlış seçim! Zəhmət olmasa 0 ilə 6 arasında rəqəm daxil edin.")


if __name__ == "__main__":
    main()