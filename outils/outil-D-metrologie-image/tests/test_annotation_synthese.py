"""
Les trois clics, la synthèse, et l'identité qui valide la chaîne entière.

Le test central est `test_fraction_mesuree_egale_la_fraction_modele` : il ferme
la boucle entre le comptage de pixels, l'étalonnage angulaire, l'inversion et
la géométrie de l'outil A. Une erreur dans n'importe lequel des quatre le fait
tomber.
"""

import json
import math

import pytest
from visee_optique.geometry import Cible, fraction_visible
from visee_optique.refraction import RegimeRefraction, rayon_effectif

from metrologie_image.annotation import (
    FACTEUR_ELARGISSEMENT,
    Pointes,
    angle_portion_emergente,
    controler_horizon,
    dispersion_pointes,
)
from metrologie_image.inversion import (
    Plage,
    StatutK,
    angle_portion_visible,
    coefficient_refraction_effectif,
)
from metrologie_image.optique import (
    INDISPONIBLE,
    Cadrage,
    Capteur,
    MetrologieError,
    Objectif,
    cadrage_plein_capteur,
    ordonnee_point_principal_px,
    pas_angulaire_rad,
)
from metrologie_image.synthese import (
    CE_QUE_CA_N_ETABLIT_PAS,
    altitude_pour_elevation,
    assembler,
    hauteur_emergente_mesuree,
    hauteur_emergente_petit_angle,
    interpreter,
    sources_manquantes,
)

R0 = 6_371_008.8
CAPTEUR = Capteur(largeur_mm=36.0, largeur_native_px=6000, hauteur_native_px=4000)
OBJECTIF = Objectif(focale_mm=300.0)
PLEIN = cadrage_plein_capteur(CAPTEUR)
Y_PP = ordonnee_point_principal_px(CAPTEUR, PLEIN)

H, Z_B, HOBS, D = 60.0, 0.0, 30.0, 40_000.0
CIBLE = Cible(H=H, z_b=Z_B)
K_VRAI = 0.13


def pointes_synthetiques(k=K_VRAI, sigma=3.0, decalage_horizon_px=0.0):
    """Fabrique des pointés à partir d'une scène connue, à l'envers de la mesure.

    On part de k, on calcule l'angle que le modèle prédit, on le convertit en
    pixels, et on place les trois clics. La chaîne doit alors retrouver k. Ce
    n'est pas une tautologie : le chemin aller (géométrie → angle → pixels) et
    le chemin retour (pixels → angle → inversion) n'empruntent pas les mêmes
    fonctions.
    """
    R = rayon_effectif(R0, k)
    angle = angle_portion_visible(D, HOBS, CIBLE, R)
    r = pas_angulaire_rad(CAPTEUR, PLEIN, OBJECTIF)
    y_base = Y_PP  # le bas visible placé sur l'axe : angle exact = paraxial
    y_sommet = y_base - angle / r
    return Pointes(
        y_horizon=y_base + decalage_horizon_px,
        y_base=y_base,
        y_sommet=y_sommet,
        sigma_px=sigma,
    )


def plages_montagne():
    """Le Monte Cinto à 140 km : une cible qui ne s'éteint pas dans le domaine."""
    return (
        Plage("distance", 140_000.0, 139_500.0, 140_500.0, "IGN, calcul géodésique"),
        Plage("altitude_observateur", HOBS, HOBS - 0.5, HOBS + 0.5, "IGN RGE ALTI 1 m"),
        Plage("hauteur_cible", 2706.0, 2705.0, 2707.0, "IGN, altitude du sommet"),
        Plage("altitude_base", 0.0, 0.0, 0.0, "niveau moyen des mers adopté"),
    )


def plages_standard():
    return (
        Plage("distance", D, D - 200.0, D + 200.0, "SHOM, calcul géodésique Vincenty"),
        Plage("altitude_observateur", HOBS, HOBS - 0.5, HOBS + 0.5, "IGN RGE ALTI 1 m"),
        Plage("hauteur_cible", H, H - 1.0, H + 1.0, "fiche d'ouvrage du phare"),
        Plage("altitude_base", 0.0, 0.0, 0.0, "niveau moyen des mers adopté"),
    )


# --- Pointés ---


def test_sommet_sous_la_base_refuse():
    with pytest.raises(MetrologieError, match="au-dessus"):
        Pointes(y_horizon=2000, y_base=1800, y_sommet=1900)


def test_sigma_nul_refuse():
    with pytest.raises(MetrologieError):
        Pointes(y_horizon=2000, y_base=2000, y_sommet=1900, sigma_px=0.0)


def test_dispersion_exige_trois_pointes():
    with pytest.raises(MetrologieError, match="trois"):
        dispersion_pointes((1900.0, 1902.0))


def test_dispersion_est_l_ecart_type_experimental():
    """Contre-épreuve à la main : sur (10, 12, 14), s = 2."""
    assert dispersion_pointes((10.0, 12.0, 14.0)) == pytest.approx(2.0)


def test_incertitude_angulaire_composee_de_deux_pointes():
    """u = 2·√2·σ·r — deux pointés indépendants, facteur d'élargissement 2."""
    p = pointes_synthetiques(sigma=3.0)
    a = angle_portion_emergente(p, CAPTEUR, PLEIN, OBJECTIF)
    attendu = FACTEUR_ELARGISSEMENT * math.sqrt(2.0) * 3.0 * pas_angulaire_rad(
        CAPTEUR, PLEIN, OBJECTIF
    )
    assert a.incertitude == pytest.approx(attendu)


# --- Contrôle d'horizon ---


def test_controle_horizon_satisfait_quand_les_clics_coincident():
    p = pointes_synthetiques(decalage_horizon_px=0.0)
    c = controler_horizon(
        p, CAPTEUR, PLEIN, OBJECTIF, D, HOBS, CIBLE, rayon_effectif(R0, K_VRAI)
    )
    assert c.coherent
    assert c.ecart_predit_px == pytest.approx(0.0, abs=1e-6)
    assert c.causes_possibles == ()


def test_controle_horizon_tolere_le_bruit_de_pointe():
    """Deux pixels d'écart, pour σ = 3 px : dans la tolérance."""
    p = pointes_synthetiques(sigma=3.0, decalage_horizon_px=2.0)
    c = controler_horizon(
        p, CAPTEUR, PLEIN, OBJECTIF, D, HOBS, CIBLE, rayon_effectif(R0, K_VRAI)
    )
    assert c.coherent


def test_controle_horizon_signale_un_ecart_franc():
    """Quarante pixels d'écart : le contrôle échoue et nomme les causes possibles.

    C'est la seule chose que le clic 1 sait faire — et le cahier des charges
    lui demandait une hauteur.
    """
    p = pointes_synthetiques(sigma=3.0, decalage_horizon_px=40.0)
    c = controler_horizon(
        p, CAPTEUR, PLEIN, OBJECTIF, D, HOBS, CIBLE, rayon_effectif(R0, K_VRAI)
    )
    assert not c.coherent
    assert len(c.causes_possibles) == 5
    assert any("mirage" in cause for cause in c.causes_possibles)


def test_tolerance_du_controle_suit_le_sigma():
    serre = controler_horizon(
        pointes_synthetiques(sigma=1.0, decalage_horizon_px=6.0),
        CAPTEUR, PLEIN, OBJECTIF, D, HOBS, CIBLE, rayon_effectif(R0, K_VRAI),
    )
    large = controler_horizon(
        pointes_synthetiques(sigma=6.0, decalage_horizon_px=6.0),
        CAPTEUR, PLEIN, OBJECTIF, D, HOBS, CIBLE, rayon_effectif(R0, K_VRAI),
    )
    assert not serre.coherent
    assert large.coherent


# --- Hauteur émergente ---


def test_altitude_pour_elevation_inverse_elevation():
    from metrologie_image.inversion import elevation

    R = rayon_effectif(R0, K_VRAI)
    for z in (0.0, 12.5, 60.0, 500.0):
        e = elevation(z, D, HOBS, R)
        assert altitude_pour_elevation(e, D, HOBS, R) == pytest.approx(z, abs=1e-6)


def test_altitude_pour_elevation_refuse_hors_domaine():
    R = rayon_effectif(R0, K_VRAI)
    # Sous la dépression de l'horizon : aucune altitude positive ne la rend.
    with pytest.raises(MetrologieError, match="hors du domaine"):
        altitude_pour_elevation(-0.5, D, HOBS, R)
    # Au-dessus de ce que z_max = 100 km permet à 40 km de distance.
    with pytest.raises(MetrologieError, match="hors du domaine"):
        altitude_pour_elevation(1.4, D, HOBS, R)


def test_hauteur_emergente_proche_du_petit_angle_sans_lui_etre_egale():
    """D·tan(θ) approche la forme exacte, mais pas au point de s'y substituer.

    L'écart est de l'ordre du pour-cent sur cette visée : invisible sur un
    tableau de bord, décisif dans un bilan d'incertitude. Les deux sont
    rendues côte à côte plutôt que l'une supposée égale à l'autre.
    """
    R = rayon_effectif(R0, K_VRAI)
    angle = angle_portion_visible(D, HOBS, CIBLE, R)
    exacte = hauteur_emergente_mesuree(angle, D, HOBS, CIBLE, R)
    approchee = hauteur_emergente_petit_angle(angle, D)
    assert exacte == pytest.approx(approchee, rel=0.05)
    assert exacte != pytest.approx(approchee, rel=1e-6)


# --- La chaîne complète ---


def test_la_chaine_retrouve_le_k_de_la_scene():
    """Aller-retour complet : scène → pixels → angle → k."""
    s = assembler(
        pointes_synthetiques(K_VRAI), CAPTEUR, PLEIN, OBJECTIF, *plages_standard(), R0=R0
    )
    assert s.resultat_k.statut is StatutK.DETERMINE
    assert s.resultat_k.k == pytest.approx(K_VRAI, abs=1e-6)


def test_fraction_mesuree_egale_la_fraction_modele():
    """L'identité qui ferme la boucle.

    La fraction déduite de l'image (hauteur émergente / H) et celle que la
    géométrie de l'outil A prédit au k retenu doivent coïncider. Elles sont
    calculées par des chemins disjoints : l'une remonte de l'angle à
    l'altitude par `altitude_pour_elevation`, l'autre descend de la distance à
    la hauteur occultée par `hauteur_occultee`. Une erreur de signe, de rayon
    ou de convention d'ordonnée dans l'un des deux les sépare.
    """
    s = assembler(
        pointes_synthetiques(K_VRAI), CAPTEUR, PLEIN, OBJECTIF, *plages_standard(), R0=R0
    )
    assert s.fraction_visible_mesuree == pytest.approx(s.fraction_visible_modele, abs=1e-9)
    R = rayon_effectif(R0, s.resultat_k.k)
    assert s.fraction_visible_modele == pytest.approx(
        fraction_visible(D, HOBS, CIBLE, R), abs=1e-12
    )


@pytest.mark.parametrize("k", [-0.2, 0.0, 0.13, 0.3, 0.5])
def test_identite_tenue_sur_tout_le_domaine(k):
    s = assembler(
        pointes_synthetiques(k), CAPTEUR, PLEIN, OBJECTIF, *plages_standard(), R0=R0
    )
    assert s.resultat_k.k == pytest.approx(k, abs=1e-6)
    assert s.fraction_visible_mesuree == pytest.approx(s.fraction_visible_modele, abs=1e-9)


def test_source_absente_n_empeche_plus_le_calcul():
    """La source est relevée, plus exigée.

    Une chaîne saisie dans un champ n'est pas une source vérifiée, et l'analyste
    qui reprend le dossier refait le travail : le verrou ne garantissait rien et
    empêchait de calculer. Ce qui compte est que l'absence RESTE VISIBLE.
    """
    p = Plage("distance", D, D - 1, D + 1, "")
    assert p.source_declaree is False
    assert p.valeur == D


def test_source_declaree_reconnue():
    assert Plage("distance", D, D - 1, D + 1, "SHOM").source_declaree is True
    assert Plage("distance", D, D - 1, D + 1, "   ").source_declaree is False


def test_sources_manquantes_les_liste():
    plages = [
        Plage("distance", D, D - 1, D + 1, "SHOM"),
        Plage("altitude_observateur", HOBS, HOBS - 1, HOBS + 1, ""),
        Plage("hauteur_cible", H, H - 1, H + 1, "   "),
        Plage("altitude_base", 0.0, 0.0, 0.0, "niveau moyen"),
    ]
    assert sources_manquantes(plages) == ("altitude_observateur", "hauteur_cible")


def test_valeur_hors_enveloppe_toujours_refusee():
    """Ce qui reste refusé : une incohérence, pas une lacune."""
    with pytest.raises(MetrologieError, match="enveloppe"):
        Plage("distance", D, D + 10, D + 20, "SHOM")


def test_synthese_porte_les_sources_manquantes():
    sans_source = (
        Plage("distance", D, D - 200.0, D + 200.0, "SHOM"),
        Plage("altitude_observateur", HOBS, HOBS - 0.5, HOBS + 0.5, ""),
        Plage("hauteur_cible", H, H - 1.0, H + 1.0, "fiche d'ouvrage"),
        Plage("altitude_base", 0.0, 0.0, 0.0, ""),
    )
    s = assembler(pointes_synthetiques(K_VRAI), CAPTEUR, PLEIN, OBJECTIF, *sans_source, R0=R0)
    assert s.sources_manquantes == ("altitude_observateur", "altitude_base")
    d = s.en_dict()
    assert d["traçabilité"]["sources_manquantes"] == ["altitude_observateur", "altitude_base"]
    # Les sources déclarées, elles, restent listées.
    assert set(d["traçabilité"]["sources"]) == {"distance", "hauteur_cible"}
    assert "DÉCLARATION" in d["traçabilité"]["avertissement_sources"]


# --- Export ---


def test_export_json_serialisable_et_complet():
    s = assembler(
        pointes_synthetiques(K_VRAI), CAPTEUR, PLEIN, OBJECTIF, *plages_standard(),
        R0=R0, empreinte_sha256="a" * 64, nom_fichier="visee.jpg",
        diametre_pupille_m=0.050,
    )
    d = s.en_dict()
    json.dumps(d)  # doit passer sans convertisseur
    assert d["traçabilité"]["sha256"] == "a" * 64
    assert set(d["traçabilité"]["sources"]) == {
        "distance", "altitude_observateur", "hauteur_cible", "altitude_base"
    }
    assert d["refraction"]["statut"] == "déterminé"
    assert d["controle_horizon_base"]["coherent"] is True
    assert len(d["ce_que_ca_n_etablit_pas"]) == len(CE_QUE_CA_N_ETABLIT_PAS)


def test_export_porte_indisponible_et_non_un_chiffre():
    """La règle du dépôt, à l'endroit où elle se joue.

    Sans diamètre de pupille déclaré, la limite de diffraction n'est pas
    calculable. Elle sort `indisponible` — jamais zéro, jamais une valeur
    typique.
    """
    s = assembler(
        pointes_synthetiques(K_VRAI), CAPTEUR, PLEIN, OBJECTIF, *plages_standard(), R0=R0
    )
    d = s.en_dict()
    assert d["étalonnage"]["limite_diffraction_arcsec"] == INDISPONIBLE
    assert d["étalonnage"]["pas_sous_la_limite_de_diffraction"] == INDISPONIBLE
    assert d["traçabilité"]["sha256"] == INDISPONIBLE
    assert d["traçabilité"]["fichier"] == INDISPONIBLE


def test_export_sans_k_ne_fabrique_pas_de_valeur():
    """Relevé sans solution : tous les champs de réfraction sortent `indisponible`.

    Le Monte Cinto à 140 km émerge de ~200 m même au plancher d'exploration.
    Un sommet pointé à un pixel de sa base est donc incompatible avec tout k :
    la chaîne doit rendre `indisponible` plutôt qu'une valeur de bout de
    domaine, qui aurait l'apparence d'une mesure.
    """
    p = Pointes(y_horizon=Y_PP, y_base=Y_PP, y_sommet=Y_PP - 1.0)
    s = assembler(p, CAPTEUR, PLEIN, OBJECTIF, *plages_montagne(), R0=R0)
    assert s.resultat_k.statut is StatutK.MAJORE
    d = s.en_dict()
    assert d["refraction"]["k"] == INDISPONIBLE
    assert d["refraction"]["regime"] == INDISPONIBLE
    assert d["mesure"]["hauteur_emergente_m"] == INDISPONIBLE
    assert d["mesure"]["fraction_visible_mesuree"] == INDISPONIBLE


def test_export_signale_le_recadrage_non_documente():
    inconnu = Cadrage(1500, 1000, 1500, 1000)
    p = Pointes(y_horizon=500.0, y_base=500.0, y_sommet=460.0)
    s = assembler(p, CAPTEUR, inconnu, OBJECTIF, *plages_standard(), R0=R0)
    d = s.en_dict()
    assert d["étalonnage"]["point_principal_connu"] is False
    assert d["mesure"]["angle_emergent_rad"] == INDISPONIBLE
    assert d["mesure"]["ecart_paraxial_rad"] == INDISPONIBLE
    assert (
        d["mesure"]["angle_emergent_borne_basse_rad"]
        < d["mesure"]["angle_emergent_borne_haute_rad"]
    )


# --- Restitution ---


def test_interpretation_ne_nomme_pas_de_regime_quand_l_enveloppe_le_traverse():
    R = rayon_effectif(R0, 0.19)
    angle = angle_portion_visible(D, HOBS, CIBLE, R)
    r = coefficient_refraction_effectif(angle, 3e-5, D, HOBS, CIBLE, R0)
    texte = interpreter(r)
    assert "aucun n'est établi" in texte


def test_interpretation_dit_la_zone_saturee():
    D_court = 8_000.0
    R = rayon_effectif(R0, 0.13)
    angle = angle_portion_visible(D_court, HOBS, CIBLE, R)
    r = coefficient_refraction_effectif(angle, 1e-6, D_court, HOBS, CIBLE, R0)
    texte = interpreter(r)
    assert "minorant" in texte


def test_interpretation_dit_l_extinction():
    r = coefficient_refraction_effectif(0.0, 1e-6, D, HOBS, CIBLE, R0)
    texte = interpreter(r)
    assert "Aucune portion émergente" in texte
    assert "majore k, il ne le mesure pas" in texte


def test_interpretation_n_emploie_jamais_les_libelles_du_cahier_des_charges():
    """« cible surélevée », « cible enfoncée » : des conclusions sur la scène.

    Le cahier des charges les proposait comme interprétation automatique de k.
    Elles sont écartées : ce qui est établi, c'est une valeur de k compatible
    avec un régime, pas un état de la cible.
    """
    for k in (-0.3, 0.0, 0.13, 0.3, 0.5):
        R = rayon_effectif(R0, k)
        angle = angle_portion_visible(D, HOBS, CIBLE, R)
        texte = interpreter(coefficient_refraction_effectif(angle, 1e-7, D, HOBS, CIBLE, R0))
        for interdit in ("surélevée", "enfoncée", "prouve", "démontre"):
            assert interdit not in texte


def test_seuils_du_tableau_8_et_non_ceux_du_cahier_des_charges():
    """k = 0,22 est « réfraction forte » au Tableau 8, et le resterait à 0,25.

    Le cahier des charges plaçait la frontière à 0,25 ; le protocole la place
    à 0,20. Une seule table de régimes dans tout le dépôt, celle de l'outil A.
    """
    R = rayon_effectif(R0, 0.22)
    angle = angle_portion_visible(D, HOBS, CIBLE, R)
    r = coefficient_refraction_effectif(angle, 1e-8, D, HOBS, CIBLE, R0)
    assert r.regime is RegimeRefraction.FORTE
