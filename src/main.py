from storage import (
    portfeli_yukle,
    aktiv_elave_et,
    aktiv_sil,
    qiymet_yenile,
    hesabati_csv_ixrac_et,
)
from analytics import portfel_icmali, risk_analizi
from market import canli_qiymet_al

def hesabat_goster() -> None:
    portfel = portfeli_yukle()
    if not portfel:
        print("\n[Məlumat] Portfeliniz hazırda boşdur.")
        return

    print("\n--- CARİ AKTİVLƏR ---")
    for aktiv in portfel:
        print(
            f"• {aktiv['simvol']}: {aktiv['miqdar']} ədəd | "
            f"Alış: {aktiv['alis_qiymeti']}$ | Cari: {aktiv['cari_qiymet']}$"
        )

    icmal = portfel_icmali(portfel)
    print("\n--- MALİYYƏ İCMALI ---")
    print(f"Ümumi maya dəyəri: {icmal['umumi_maya']}$")
    print(f"Cari bazar dəyəri: {icmal['umumi_deyer']}$")
    print(f"Xalis mənfəət/zərər: {icmal['xalis_menfeet']}$ ({icmal['menfeet_faizi']}%)")

    riskler = risk_analizi(portfel)
    if riskler:
        print("\n[XƏBƏRDARLIQ] Yüksək konsentrasiya riski:")
        for risk in riskler:
            print(
                f"  ! {risk['simvol']} portfelin {risk['ceki_faizi']}%-ni təşkil edir "
                f"(Limit: {risk['limit']}%)"
            )

def yeni_aktiv_ekrani() -> None:
    print("\n--- YENİ AKTİV ƏLAVƏ ET ---")
    simvol = input("Aktivin simvolu (məs. AAPL, ETH): ").strip().upper()
    if not simvol:
        print("[Xəta] Simvol boş ola bilməz!")
        return

    try:
        alis_qiymeti = float(input("Alış qiyməti ($): "))
        miqdar = float(input("Miqdar: "))
    except ValueError:
        print("[Xəta] Qiymət və miqdar yalnız rəqəm olmalıdır!")
        return

    print(f"[Məlumat] {simvol} üçün canlı bazar qiyməti yoxlanılır...")
    cari_qiymet = canli_qiymet_al(simvol)

    if cari_qiymet is not None:
        print(f"[API] Cari bazar qiyməti avtomatik tapıldı: {cari_qiymet}$")
    else:
        print("[Xəbərdarlıq] Canlı qiymət tapılmadı (offline və ya naməlum simvol).")
        try:
            cari_qiymet = float(input("Cari bazar qiymətini əl ilə daxil edin ($): "))
        except ValueError:
            print("[Xəta] Qiymət yalnız rəqəm olmalıdır!")
            return

    if aktiv_elave_et(simvol, alis_qiymeti, cari_qiymet, miqdar):
        print(f"[Uğurlu] {simvol} portfelə əlavə edildi.")
    else:
        print("[Xəta] Aktiv əlavə edilmədi (artıq mövcuddur və ya dəyərlər 0-dan böyük deyil).")


def aktiv_sil_ekrani() -> None:
    print("\n--- AKTİVİ SİL ---")
    simvol = input("Silinəcək aktivin simvolu: ")
    if aktiv_sil(simvol):
        print(f"[Uğurlu] {simvol.strip().upper()} portfeldən silindi.")
    else:
        print("[Xəta] Bu simvol portfeldə tapılmadı.")


def qiymet_yenile_ekrani() -> None:
    print("\n--- CARİ QİYMƏTİ YENİLƏ ---")
    simvol = input("Qiyməti yenilənəcək aktivin simvolu: ")
    try:
        yeni_qiymet = float(input("Yeni bazar qiyməti ($): "))
    except ValueError:
        print("[Xəta] Qiymət yalnız rəqəm olmalıdır!")
        return

    if qiymet_yenile(simvol, yeni_qiymet):
        print(f"[Uğurlu] {simvol.strip().upper()} üçün yeni qiymət yadda saxlanıldı.")
    else:
        print("[Xəta] Qiymət yenilənmədi (simvol tapılmadı və ya qiymət 0-dan böyük deyil).")


def canli_yenile_ekrani() -> None:
    portfel = portfeli_yukle()
    if not portfel:
        print("\n[Məlumat] Portfeliniz boşdur, yenilənəcək aktiv yoxdur.")
        return

    print("\n--- CANLI BAZAR QİYMƏTLƏRİ YENİLƏNİR ---")
    yenilenen_say = 0

    for aktiv in portfel:
        simvol = aktiv["simvol"]
        yeni_qiymet = canli_qiymet_al(simvol)

        if yeni_qiymet is not None:
            qiymet_yenile(simvol, yeni_qiymet)
            print(f"• {simvol}: {yeni_qiymet}$ (Yeniləndi)")
            yenilenen_say += 1
        else:
            print(f"• {simvol}: Canlı qiymət tapılmadı (köhnə qiymət saxlanıldı)")

    print(f"\n[Yekun] {len(portfel)} aktivdən {yenilenen_say} ədədi canlı qiymətlə yeniləndi.")


def csv_ixrac_ekrani() -> None:
    portfel = portfeli_yukle()
    fayl_yolu = "data/portfel_hesabati.csv"

    if hesabati_csv_ixrac_et(portfel, fayl_yolu):
        print(f"\n[Uğurlu] Hesabat '{fayl_yolu}' faylına ixrac edildi.")
    else:
        print("\n[Xəta] Portfel boş olduğu üçün ixrac ediləcək məlumat yoxdur.")


def esas_menyu() -> None:
    while True:
        print("\n=== FINTRACK PORTFEL İDARƏETMƏ SİSTEMİ ===")
        print("1. Portfelə və risk auditinə bax")
        print("2. Yeni aktiv əlavə et")
        print("3. Cari qiyməti əl ilə yenilə")
        print("4. Canlı bazar qiymətlərini yenilə (API)")
        print("5. Aktivi sil")
        print("6. Hesabatı CSV (Excel) faylına ixrac et")
        print("7. Çıxış")

        secim = input("Seçiminizi daxil edin (1-7): ").strip()

        if secim == "1":
            hesabat_goster()
        elif secim == "2":
            yeni_aktiv_ekrani()
        elif secim == "3":
            qiymet_yenile_ekrani()
        elif secim == "4":
            canli_yenile_ekrani()
        elif secim == "5":
            aktiv_sil_ekrani()
        elif secim == "6":
            csv_ixrac_ekrani()
        elif secim == "7":
            print("Proqramdan çıxılır. Uğurlar!")
            break
        else:
            print("[Xəta] Yanlış seçim! Zəhmət olmasa 1 ilə 7 arasında rəqəm daxil edin.")

if __name__ == "__main__":
    esas_menyu()