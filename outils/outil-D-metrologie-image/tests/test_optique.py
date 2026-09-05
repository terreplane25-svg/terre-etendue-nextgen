"""
Étalonnage spatial : les trois pièges du cahier des charges, éprouvés un à un.
"""

import math

import pytest

from metrologie_image.optique import (
    LARGEUR_24x36_MM,
    Cadrage,
    Capteur,
    MetrologieError,
    Objectif,
    angle_entre_lignes,
    angle_entre_lignes_enveloppe,
    angle_entre_lignes_paraxial,
    cadrage_plein_capteur,
    capteur_equivalent_35mm,
    echelle_m_par_px,
    ordonnee_point_principal_px,
    pas_angulaire_rad,
    pas_pixel_livre_mm,
    resolution_angulaire_limite_rad,
)

# Un plein format 24×36 de 6000×4000, objectif de 300 mm : la configuration de
# référence de tous les tests qui suivent.
CAPTEUR = Capteur(largeur_mm=36.0, largeur_native_px=6000, hauteur_native_px=4000)
OBJECTIF = Objectif(focale_mm=300.0)
PLEIN = cadrage_plein_capteur(CAPTEUR)


def test_pas_pixel_vient_du_capteur():
    assert CAPTEUR.pas_pixel_mm == pytest.approx(0.006)


def test_pas_angulaire_vaut_environ_quatre_secondes():
    """36/6000/300 = 2·10⁻⁵ rad, soit 4,1″. Ordre de grandeur d'un téléobjectif."""
    r = pas_angulaire_rad(CAPTEUR, PLEIN, OBJECTIF)
    assert r == pytest.approx(2e-5, rel=1e-6)
    assert math.degrees(r) * 3600.0 == pytest.approx(4.125, abs=0.01)


def test_le_recadrage_ne_change_pas_le_pas_pixel():
    """LE piège du cahier des charges.

    Sa formule prend la largeur du fichier livré. Une image recadrée de 6000
    à 1500 px lui donnerait un pas pixel quatre fois trop grand, donc un angle
    quatre fois trop grand, donc une hauteur émergente quatre fois trop
    grande — sans qu'aucun garde-fou ne le signale.
    """
    recadre = Cadrage(1500, 1000, 1500, 1000, origine_x_px=2250, origine_y_px=1500)
    assert pas_pixel_livre_mm(CAPTEUR, recadre) == pytest.approx(
        pas_pixel_livre_mm(CAPTEUR, PLEIN)
    )
    naif = (CAPTEUR.largeur_mm / recadre.largeur_px) / OBJECTIF.focale_mm
    juste = pas_angulaire_rad(CAPTEUR, recadre, OBJECTIF)
    assert naif / juste == pytest.approx(4.0, rel=1e-5)


def test_le_reechantillonnage_divise_le_pas():
    """Un fichier agrandi ×2 a des pixels deux fois plus fins, sans plus d'information."""
    agrandi = Cadrage(3000, 2000, 1500, 1000, origine_x_px=2250, origine_y_px=1500)
    assert agrandi.facteur_reechantillonnage == pytest.approx(2.0)
    assert pas_pixel_livre_mm(CAPTEUR, agrandi) == pytest.approx(0.003)


def test_reechantillonnage_anisotrope_refuse():
    with pytest.raises(MetrologieError, match="anisotrope"):
        Cadrage(3000, 1000, 1500, 1000, origine_x_px=0, origine_y_px=0)


def test_origine_partielle_refusee():
    with pytest.raises(MetrologieError, match="entière ou pas du tout"):
        Cadrage(6000, 4000, 6000, 4000, origine_x_px=0)


def test_point_principal_apres_recadrage():
    """Le centre du capteur, exprimé dans le fichier livré."""
    recadre = Cadrage(1500, 1000, 1500, 1000, origine_x_px=2250, origine_y_px=1800)
    # Centre natif à y = 2000 ; recadrage à partir de 1800 → 200 dans le fichier.
    assert ordonnee_point_principal_px(CAPTEUR, recadre) == pytest.approx(200.0)


def test_point_principal_peut_sortir_du_cadre():
    """Un recadrage en bord de champ rejette l'axe optique hors de l'image.

    Ce n'est pas une erreur : c'est un fait dont le calcul d'angle doit tenir
    compte, et qu'une supposition de centre effacerait.
    """
    bord = Cadrage(800, 600, 800, 600, origine_x_px=0, origine_y_px=0)
    assert ordonnee_point_principal_px(CAPTEUR, bord) == pytest.approx(2000.0)


def test_origine_inconnue_refuse_le_point_principal():
    inconnu = Cadrage(1500, 1000, 1500, 1000)
    assert not inconnu.point_principal_connu
    with pytest.raises(MetrologieError, match="indisponible"):
        ordonnee_point_principal_px(CAPTEUR, inconnu)


def test_exact_et_paraxial_coincident_au_centre():
    """Sur l'axe, les deux formes sont indiscernables — c'est ce qui rend
    l'approximation du cahier des charges acceptable dans le cas courant."""
    y_pp = ordonnee_point_principal_px(CAPTEUR, PLEIN)
    exact = angle_entre_lignes(y_pp - 50, y_pp + 50, CAPTEUR, PLEIN, OBJECTIF)
    parax = angle_entre_lignes_paraxial(y_pp - 50, y_pp + 50, CAPTEUR, PLEIN, OBJECTIF)
    assert exact == pytest.approx(parax, rel=1e-6)


def test_paraxial_surestime_hors_axe():
    """Loin de l'axe, la forme paraxiale surestime : c'est ce qu'il faut voir.

    Un segment de 100 px placé à 1900 px de l'axe — le bord du champ d'un
    24×36 — donne un angle inférieur de plusieurs pour mille à ce que la
    forme paraxiale annonce.
    """
    y_pp = ordonnee_point_principal_px(CAPTEUR, PLEIN)
    haut, bas = y_pp - 1950, y_pp - 1850
    exact = angle_entre_lignes(haut, bas, CAPTEUR, PLEIN, OBJECTIF)
    parax = angle_entre_lignes_paraxial(haut, bas, CAPTEUR, PLEIN, OBJECTIF)
    assert parax > exact
    assert (parax - exact) / exact > 1e-3


def test_angle_decroit_avec_l_excentrement():
    """La propriété sur laquelle repose l'enveloppe : l'angle est maximal au centre."""
    y_pp = ordonnee_point_principal_px(CAPTEUR, PLEIN)
    angles = [
        angle_entre_lignes(y_pp + d - 50, y_pp + d + 50, CAPTEUR, PLEIN, OBJECTIF)
        for d in (0, 400, 800, 1200, 1600)
    ]
    assert all(b < a for a, b in zip(angles, angles[1:]))


def test_enveloppe_encadre_la_verite_quand_le_recadrage_est_inconnu():
    """L'angle vrai, calculé avec l'origine réelle, tombe dans l'enveloppe
    calculée sans elle. C'est tout ce qu'on demande à une enveloppe."""
    connu = Cadrage(1500, 1000, 1500, 1000, origine_x_px=2250, origine_y_px=1200)
    inconnu = Cadrage(1500, 1000, 1500, 1000)
    vrai = angle_entre_lignes(300.0, 400.0, CAPTEUR, connu, OBJECTIF)
    basse, haute = angle_entre_lignes_enveloppe(300.0, 400.0, CAPTEUR, inconnu, OBJECTIF)
    assert basse <= vrai <= haute
    assert basse < haute


def test_enveloppe_encadre_toutes_les_origines_possibles():
    """Balayage exhaustif : aucune origine admissible ne sort de l'enveloppe."""
    inconnu = Cadrage(1500, 1000, 1500, 1000)
    basse, haute = angle_entre_lignes_enveloppe(300.0, 400.0, CAPTEUR, inconnu, OBJECTIF)
    for y0 in range(0, CAPTEUR.hauteur_native_px - 1000 + 1, 25):
        c = Cadrage(1500, 1000, 1500, 1000, origine_x_px=0, origine_y_px=y0)
        a = angle_entre_lignes(300.0, 400.0, CAPTEUR, c, OBJECTIF)
        assert basse - 1e-15 <= a <= haute + 1e-15


def test_enveloppe_degeneree_quand_le_point_principal_est_connu():
    basse, haute = angle_entre_lignes_enveloppe(1900.0, 2100.0, CAPTEUR, PLEIN, OBJECTIF)
    assert basse == haute


def test_equivalent_35mm_donne_le_meme_angle_que_la_focale_reelle():
    """Contre-épreuve entre les deux voies de saisie.

    Un APS-C de 23,5 mm à 200 mm de focale a pour équivalent 35 mm
    200 × 36/23,5 = 306,4 mm. Les deux descriptions doivent rendre le même
    angle pour le même écart de pixels — sans quoi l'une des deux voies
    trompe l'opérateur qui n'a pas l'autre.
    """
    aps = Capteur(largeur_mm=23.5, largeur_native_px=6000, hauteur_native_px=4000)
    aps_cadrage = cadrage_plein_capteur(aps)
    f_reelle = 200.0
    f_eq = f_reelle * LARGEUR_24x36_MM / aps.largeur_mm

    eq = capteur_equivalent_35mm(6000, 4000)
    eq_cadrage = cadrage_plein_capteur(eq)

    a1 = angle_entre_lignes(1900, 2100, aps, aps_cadrage, Objectif(f_reelle))
    a2 = angle_entre_lignes(1900, 2100, eq, eq_cadrage, Objectif(f_eq))
    assert a1 == pytest.approx(a2, rel=1e-12)


def test_echelle_metres_par_pixel():
    """À 40 km, un pixel de 2·10⁻⁵ rad couvre 0,8 m."""
    assert echelle_m_par_px(40_000.0, CAPTEUR, PLEIN, OBJECTIF) == pytest.approx(
        0.8, rel=1e-5
    )


def test_limite_de_diffraction():
    """Rayleigh à 550 nm sur 50 mm de pupille : 2,77″.

    Contre-épreuve par la règle de pouce des opticiens, indépendante du code :
    à 550 nm, 1,22·λ/D exprimé en secondes d'arc vaut environ 138/D(mm), soit
    2,76″ ici.

    Comparée aux 4,1″ du pas pixel, cette limite dit que la configuration est
    limitée par le capteur et non par l'optique : l'information est bien
    enregistrée pixel par pixel, et un écart de pixels y est une mesure.
    """
    limite = resolution_angulaire_limite_rad(550e-9, 0.050)
    arcsec = math.degrees(limite) * 3600.0
    assert arcsec == pytest.approx(2.768, abs=0.01)
    assert arcsec == pytest.approx(138.0 / 50.0, rel=0.01)
    assert limite < pas_angulaire_rad(CAPTEUR, PLEIN, OBJECTIF)


def test_limite_de_diffraction_peut_depasser_le_pas_pixel():
    """Sur une petite pupille, l'optique borne avant le capteur.

    Un objectif de 300 mm ouvert à f/22 n'a que 13,6 mm de pupille : la tache
    de diffraction couvre alors plus d'un pixel, et deux lignes séparées de
    trois pixels ne sont plus deux détails enregistrés. Le tableau de bord
    doit le dire ; c'est à cela que sert la comparaison.
    """
    limite = resolution_angulaire_limite_rad(550e-9, 300.0 / 22.0 / 1000.0)
    assert limite > pas_angulaire_rad(CAPTEUR, PLEIN, OBJECTIF)


def test_refus_de_domaine():
    with pytest.raises(MetrologieError):
        Capteur(largeur_mm=0.0, largeur_native_px=6000, hauteur_native_px=4000)
    with pytest.raises(MetrologieError):
        Capteur(largeur_mm=36.0, largeur_native_px=0, hauteur_native_px=4000)
    with pytest.raises(MetrologieError):
        Objectif(focale_mm=-1.0)
    with pytest.raises(MetrologieError):
        Cadrage(0, 100, 100, 100)
    with pytest.raises(MetrologieError):
        Cadrage(100, 100, 100, 100, origine_x_px=-1, origine_y_px=0)
    with pytest.raises(MetrologieError):
        echelle_m_par_px(0.0, CAPTEUR, PLEIN, OBJECTIF)
    with pytest.raises(MetrologieError):
        resolution_angulaire_limite_rad(550e-9, 0.0)


def test_enveloppe_refuse_un_segment_inverse():
    inconnu = Cadrage(1500, 1000, 1500, 1000)
    with pytest.raises(MetrologieError, match="au-dessus"):
        angle_entre_lignes_enveloppe(400.0, 300.0, CAPTEUR, inconnu, OBJECTIF)
