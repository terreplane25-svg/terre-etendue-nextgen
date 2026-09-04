"""
Tests de sensor_forensics.py — débruitage en ondelettes et corrélation PRNU sur
signaux synthétiques (aucune bibliothèque de référence tierce à comparer : on
construit les propriétés qu'on peut légitimement exiger et on les vérifie),
et détection ELA sur une image JPEG assemblée dans le test.
"""

import io

import numpy as np
import pytest
from PIL import Image

from preuve_image.sensor_forensics import (
    AVERTISSEMENT_ELA,
    EmpreinteCapteur,
    FORMATS_ELA_APPLICABLES,
    ResultatELA,
    ResultatPic,
    SEUIL_PCE_CITE_LITTERATURE,
    SensorForensicsError,
    calculer_empreinte,
    carte_ela,
    charger_luminance,
    correlation_normalisee,
    debruiter_ondelettes,
    intensite_zone,
    interpreter_pce,
    pic_correlation,
    recompresser_jpeg,
    residu_bruit,
    verifier_applicable_ela,
)


# --- debruiter_ondelettes / residu_bruit ---

def test_debruiter_ondelettes_reduit_significativement_le_bruit():
    rng = np.random.default_rng(42)
    taille = 256
    x = np.linspace(0, 1, taille)
    lisse = 100 * np.outer(np.sin(2 * np.pi * x), np.cos(2 * np.pi * x)) + 128
    bruitee = lisse + rng.normal(scale=15, size=(taille, taille))

    debruitee = debruiter_ondelettes(bruitee)

    erreur_avant = np.mean((bruitee - lisse) ** 2)
    erreur_apres = np.mean((debruitee - lisse) ** 2)
    assert erreur_apres < 0.3 * erreur_avant  # net rapprochement du contenu lisse sous-jacent


def test_debruiter_ondelettes_rejette_image_non_2d():
    with pytest.raises(SensorForensicsError):
        debruiter_ondelettes(np.zeros((8, 8, 3)))


def test_residu_bruit_sur_bruit_pur_conserve_l_essentiel_de_la_variance():
    # Sur une image sans aucun contenu de scène (bruit pur), rien à débruiter :
    # le résidu doit rester proche du signal d'origine, pas s'effondrer vers zéro.
    rng = np.random.default_rng(42)
    taille = 256
    bruit_pur = rng.normal(scale=10, size=(taille, taille))
    residu = residu_bruit(bruit_pur)
    assert residu.std() > 0.5 * bruit_pur.std()


# --- corrélation normalisée ---

def test_correlation_normalisee_identite_et_opposition():
    rng = np.random.default_rng(1)
    signal = rng.normal(size=(32, 32))
    assert correlation_normalisee(signal, signal) == pytest.approx(1.0)
    assert correlation_normalisee(signal, -signal) == pytest.approx(-1.0)


def test_correlation_normalisee_signaux_independants_proche_de_zero():
    rng = np.random.default_rng(2)
    a = rng.normal(size=(128, 128))
    b = rng.normal(size=(128, 128))
    assert abs(correlation_normalisee(a, b)) < 0.1


def test_correlation_normalisee_rejette_dimensions_incompatibles():
    with pytest.raises(SensorForensicsError):
        correlation_normalisee(np.zeros((4, 4)), np.zeros((5, 5)))


def test_correlation_normalisee_rejette_signal_constant():
    with pytest.raises(SensorForensicsError):
        correlation_normalisee(np.ones((4, 4)), np.zeros((4, 4)))


# --- EmpreinteCapteur / calculer_empreinte ---

def test_calculer_empreinte_moyenne_correctement():
    a = np.array([[1.0, 2.0], [3.0, 4.0]])
    b = np.array([[3.0, 4.0], [5.0, 6.0]])
    empreinte = calculer_empreinte([a, b], source="deux images de test")
    assert np.allclose(empreinte.motif, np.array([[2.0, 3.0], [4.0, 5.0]]))
    assert empreinte.n_images == 2


def test_calculer_empreinte_exige_au_moins_deux_residus():
    with pytest.raises(SensorForensicsError):
        calculer_empreinte([np.zeros((4, 4))], source="une seule image")


def test_calculer_empreinte_rejette_dimensions_incoherentes():
    with pytest.raises(SensorForensicsError):
        calculer_empreinte([np.zeros((4, 4)), np.zeros((5, 5))], source="tailles différentes")


def test_empreinte_capteur_exige_source_documentee():
    with pytest.raises(SensorForensicsError):
        EmpreinteCapteur(motif=np.zeros((4, 4)), n_images=5, source=" ")


@pytest.mark.parametrize(
    "n_images,attendu",
    [(5, "faible"), (30, "correcte"), (60, "conforme")],
)
def test_empreinte_capteur_fiabilite_par_palier(n_images, attendu):
    empreinte = EmpreinteCapteur(motif=np.zeros((4, 4)), n_images=n_images, source="lot de test")
    assert attendu in empreinte.fiabilite


# --- pic_correlation / PCE ---

def _fabriquer_scenario_empreinte(alpha=3.0, bruit=5.0, forme=(96, 96), graine=42):
    rng = np.random.default_rng(graine)
    empreinte_reelle = rng.normal(scale=1.0, size=forme)
    residus = [alpha * empreinte_reelle + rng.normal(scale=bruit, size=forme) for _ in range(10)]
    empreinte = calculer_empreinte(residus, source="10 images test")
    return rng, empreinte_reelle, empreinte, alpha, bruit, forme


def test_pic_correlation_distingue_nettement_la_bonne_empreinte():
    rng, empreinte_reelle, empreinte, alpha, bruit, forme = _fabriquer_scenario_empreinte()

    residu_avec_empreinte = alpha * empreinte_reelle + rng.normal(scale=bruit, size=forme)
    residu_etranger = rng.normal(scale=bruit, size=forme)

    resultat_avec = pic_correlation(residu_avec_empreinte, empreinte.motif)
    resultat_sans = pic_correlation(residu_etranger, empreinte.motif)

    assert isinstance(resultat_avec, ResultatPic)
    assert resultat_avec.decalage == (0, 0)
    assert resultat_avec.pce > 10 * SEUIL_PCE_CITE_LITTERATURE
    assert resultat_sans.pce < SEUIL_PCE_CITE_LITTERATURE


def test_pic_correlation_retrouve_un_decalage_spatial():
    rng, empreinte_reelle, empreinte, alpha, bruit, forme = _fabriquer_scenario_empreinte()
    decalage_vrai = (3, -5)
    decalee = np.roll(alpha * empreinte_reelle, shift=decalage_vrai, axis=(0, 1)) + rng.normal(
        scale=bruit, size=forme
    )
    resultat = pic_correlation(decalee, empreinte.motif)
    assert resultat.decalage == decalage_vrai
    assert resultat.pce > 10 * SEUIL_PCE_CITE_LITTERATURE


def test_pic_correlation_rejette_dimensions_incompatibles():
    with pytest.raises(SensorForensicsError):
        pic_correlation(np.zeros((4, 4)), np.zeros((5, 5)))


def test_pic_correlation_rejette_rayon_exclusion_trop_grand():
    with pytest.raises(SensorForensicsError):
        pic_correlation(np.random.default_rng(0).normal(size=(8, 8)), np.random.default_rng(1).normal(size=(8, 8)), rayon_exclusion=100)


def test_interpreter_pce_cite_le_seuil_dans_les_deux_sens():
    au_dessus = interpreter_pce(1000.0)
    en_dessous = interpreter_pce(5.0)
    assert "60" in au_dessus and "Goljan" in au_dessus
    assert "60" in en_dessous
    assert au_dessus != en_dessous
    # ni l'un ni l'autre ne doit affirmer une conclusion définitive
    assert "jamais concluant" in au_dessus or "ne remplace pas" in au_dessus
    assert "n'établit pas" in en_dessous


# --- ELA ---

def _construire_jpeg(taille=128, graine=7, qualite=85):
    yy, xx = np.mgrid[0:taille, 0:taille]
    base = (80 + 0.5 * xx + 0.3 * yy).astype(np.uint8)
    tableau = np.stack([base] * 3, axis=-1)
    image = Image.fromarray(tableau, mode="RGB")
    tampon = io.BytesIO()
    image.save(tampon, format="JPEG", quality=qualite)
    return tampon.getvalue()


def _construire_jpeg_avec_montage(taille=128, graine=7, qualite=85):
    original = _construire_jpeg(taille=taille, graine=graine, qualite=qualite)
    image = Image.open(io.BytesIO(original)).convert("RGB")
    patch = Image.new("RGB", (24, 24), color=(20, 200, 50))
    image.paste(patch, (80, 10))
    tampon = io.BytesIO()
    image.save(tampon, format="JPEG", quality=qualite)
    return tampon.getvalue()


def test_carte_ela_documente_toujours_son_contexte():
    resultat = carte_ela(_construire_jpeg(), qualite=90)
    assert isinstance(resultat, ResultatELA)
    assert resultat.qualite_recompression == 90
    assert resultat.format_original == "JPEG"
    assert resultat.avertissement == AVERTISSEMENT_ELA
    assert resultat.valeur_max >= resultat.valeur_moyenne >= 0.0


def test_carte_ela_revele_la_zone_montee():
    manipulee = _construire_jpeg_avec_montage()
    resultat = carte_ela(manipulee, qualite=90)

    zone_montage = intensite_zone(resultat.carte, 10, 34, 80, 104)
    zone_intacte = intensite_zone(resultat.carte, 90, 114, 10, 34)

    assert zone_montage > 5 * zone_intacte


def test_carte_ela_image_intacte_reste_globalement_homogene():
    intacte = _construire_jpeg()
    resultat = carte_ela(intacte, qualite=90)
    # sans montage, aucune région ne doit se détacher aussi nettement que dans le cas manipulé
    zone_a = intensite_zone(resultat.carte, 10, 34, 80, 104)
    zone_b = intensite_zone(resultat.carte, 90, 114, 10, 34)
    assert zone_a < 5 * (zone_b + 1e-9)


def test_verifier_applicable_ela_rejette_non_jpeg():
    with pytest.raises(SensorForensicsError, match="JPEG"):
        verifier_applicable_ela("PNG")
    verifier_applicable_ela("JPEG")  # ne lève pas


def test_carte_ela_rejette_source_non_jpeg():
    image = Image.new("RGB", (16, 16), color=(1, 2, 3))
    tampon = io.BytesIO()
    image.save(tampon, format="PNG")
    with pytest.raises(SensorForensicsError, match="JPEG"):
        carte_ela(tampon.getvalue())


def test_recompresser_jpeg_rejette_qualite_hors_bornes():
    image = Image.new("RGB", (8, 8))
    with pytest.raises(SensorForensicsError):
        recompresser_jpeg(image, qualite=0)
    with pytest.raises(SensorForensicsError):
        recompresser_jpeg(image, qualite=101)


def test_intensite_zone_rejette_region_hors_limites():
    carte = np.zeros((10, 10))
    with pytest.raises(SensorForensicsError):
        intensite_zone(carte, 0, 5, 0, 20)
    with pytest.raises(SensorForensicsError):
        intensite_zone(carte, 5, 2, 0, 5)


def test_formats_ela_applicables_ne_contient_que_jpeg():
    assert FORMATS_ELA_APPLICABLES == frozenset({"JPEG"})


# --- charger_luminance ---

def test_charger_luminance_depuis_octets():
    donnees = _construire_jpeg()
    gris = charger_luminance(donnees)
    assert gris.ndim == 2
    assert gris.shape == (128, 128)


def test_charger_luminance_depuis_fichier(tmp_path):
    chemin = tmp_path / "photo.jpg"
    chemin.write_bytes(_construire_jpeg())
    gris = charger_luminance(chemin)
    assert gris.shape == (128, 128)


def test_charger_luminance_rejette_donnees_illisibles():
    with pytest.raises(SensorForensicsError):
        charger_luminance(b"pas une image")
