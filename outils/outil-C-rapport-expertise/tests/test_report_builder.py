"""
Tests de report_builder.py — la fiche standard d'observation (§33), ses neuf
blocs et la discipline « une vraie valeur, ou indisponible, jamais omis ».
Construit volontairement certains blocs avec de vraies instances de types
d'Outil A (visee_optique) et d'Outil B (preuve_image), pour vérifier que
l'intégration entre les trois projets fonctionne réellement, pas seulement
sur le papier.
"""

from datetime import datetime, timezone

import pytest

from preuve_image.metadata import DonneesExif, FicheGrossissement
from preuve_image.metadata import INDISPONIBLE as INDISPONIBLE_META
from visee_optique.decision import Verdict
from visee_optique.geodesy import GrandeurGeodesique
from visee_optique.refraction import HypotheseRefraction

from rapport_expertise.report_builder import (
    Atmosphere,
    Cible,
    FicheObservation,
    Geometrie,
    Identification,
    Images,
    INDISPONIBLE,
    Mesures,
    PosteObservation,
    RapportError,
    Resultat,
    SystemePhotographique,
    champs_indisponibles,
    declarer,
    resume_verdicts,
)


def _identification(**overrides):
    valeurs = dict(
        identifiant_dossier="OBS-2026-001",
        date_heure_utc_serie=datetime(2026, 9, 3, 7, 0, tzinfo=timezone.utc),
        ecart_horloge_mesure=0.3,
        operateur="A. Dupont",
        campagne_et_reference_preenregistrement="campagne-2026-littoral#003",
    )
    valeurs.update(overrides)
    return Identification(**valeurs)


def _poste_observation_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in PosteObservation.__dataclass_fields__}
    valeurs.update(overrides)
    return PosteObservation(**valeurs)


def _cible_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in Cible.__dataclass_fields__}
    valeurs.update(overrides)
    return Cible(**valeurs)


def _geometrie_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in Geometrie.__dataclass_fields__}
    valeurs.update(overrides)
    return Geometrie(**valeurs)


def _systeme_photo_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in SystemePhotographique.__dataclass_fields__}
    valeurs.update(overrides)
    return SystemePhotographique(**valeurs)


def _atmosphere_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in Atmosphere.__dataclass_fields__}
    valeurs.update(overrides)
    return Atmosphere(**valeurs)


def _images_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in Images.__dataclass_fields__}
    valeurs.update(overrides)
    return Images(**valeurs)


def _mesures_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in Mesures.__dataclass_fields__}
    valeurs.update(overrides)
    return Mesures(**valeurs)


def _resultat_indisponible(**overrides):
    valeurs = {champ: INDISPONIBLE for champ in Resultat.__dataclass_fields__}
    valeurs.update(overrides)
    return Resultat(**valeurs)


def _fiche_toute_indisponible(**overrides_par_section):
    sections = dict(
        identification=_identification(),
        poste_observation=_poste_observation_indisponible(),
        cible=_cible_indisponible(),
        geometrie=_geometrie_indisponible(),
        systeme_photographique=_systeme_photo_indisponible(),
        atmosphere=_atmosphere_indisponible(),
        images=_images_indisponible(),
        mesures=_mesures_indisponible(),
        resultat=_resultat_indisponible(),
    )
    sections.update(overrides_par_section)
    return FicheObservation(**sections)


# --- declarer / INDISPONIBLE ---

def test_declarer_accepte_valeur_reelle_et_sentinel():
    assert declarer("Phare de Cordouan", "designation") == "Phare de Cordouan"
    assert declarer(INDISPONIBLE, "designation") == INDISPONIBLE


def test_declarer_rejette_none_et_chaine_vide():
    with pytest.raises(RapportError, match="designation"):
        declarer(None, "designation")
    with pytest.raises(RapportError, match="designation"):
        declarer("", "designation")


def test_declarer_accepte_objets_reels_typiques_de_ce_projet():
    # Un objet réel n'est jamais confondu avec une absence — même un enum ou
    # une dataclass dont __eq__ pourrait, en théorie, mal réagir à `== ""`.
    assert declarer(Verdict.COMPATIBLE, "verdict") == Verdict.COMPATIBLE


# --- Chaque section rejette un champ omis et accepte INDISPONIBLE partout ---

def test_identification_rejette_champ_omis():
    with pytest.raises(RapportError, match="operateur"):
        _identification(operateur=None)


def test_poste_observation_accepte_tout_indisponible():
    poste = _poste_observation_indisponible()
    assert poste.observateur == INDISPONIBLE


def test_poste_observation_rejette_champ_omis():
    with pytest.raises(RapportError, match="hauteur_axe_optique"):
        _poste_observation_indisponible(hauteur_axe_optique="")


def test_cible_rejette_champ_omis():
    with pytest.raises(RapportError, match="hauteur_totale_H_et_source"):
        _cible_indisponible(hauteur_totale_H_et_source=None)


def test_geometrie_accepte_grandeur_geodesique_reelle():
    distance = GrandeurGeodesique(
        nom="distance", valeur=42_000.0, unite="m", referentiel="WGS84",
        source="calcul géodésique (Karney, 2013)", incertitude=5.0,
    )
    geometrie = _geometrie_indisponible(distance_D_algorithme_et_incertitude=distance)
    assert geometrie.distance_D_algorithme_et_incertitude is distance


def test_geometrie_rejette_champ_omis():
    with pytest.raises(RapportError, match="azimut_geodesique"):
        _geometrie_indisponible(azimut_geodesique=None)


def test_systeme_photographique_accepte_donnees_exif_et_fiche_grossissement_reelles():
    exif = DonneesExif(
        fabricant="Canon", modele="EOS R5", objectif="RF800mm F11", focale_mm=800.0,
        focale_equivalente_35mm=800, ouverture=11.0, temps_pose_s=0.002, sensibilite_iso=400,
        largeur_px=8192, hauteur_px=5464, date_heure_original="2026:09:03 07:00:00",
        orientation=1, gps=None,
    )
    grossissement = FicheGrossissement(
        focale_optique_reelle=800.0, focale_equivalente=800.0, facteur_grossissement=1.0,
        part_optique_vs_numerique="100% optique", resolution_native=(8192, 5464),
        resolution_fichier=(8192, 5464), recadrage_avant_enregistrement=False,
        traitements_computationnels_actifs=INDISPONIBLE_META, autre_etape_scene_vers_fichier=INDISPONIBLE_META,
    )
    systeme = _systeme_photo_indisponible(
        boitier_objectif_numeros_serie=exif, grossissement=grossissement
    )
    assert systeme.boitier_objectif_numeros_serie is exif
    assert systeme.grossissement is grossissement


def test_systeme_photographique_rejette_champ_omis():
    with pytest.raises(RapportError, match="grossissement"):
        _systeme_photo_indisponible(grossissement=None)


def test_atmosphere_accepte_hypothese_refraction_reelle():
    hyp = HypotheseRefraction(k_min=0.13, k_max=0.20, justification="test")
    atmo = _atmosphere_indisponible(intervalle_k_retenu_et_justification=hyp)
    assert atmo.intervalle_k_retenu_et_justification is hyp


def test_atmosphere_rejette_champ_omis():
    with pytest.raises(RapportError, match="classe_de_chaque_donnee"):
        _atmosphere_indisponible(classe_de_chaque_donnee="")


def test_images_rejette_champ_omis():
    with pytest.raises(RapportError, match="resolution_effective_mesuree"):
        _images_indisponible(resolution_effective_mesuree=None)


def test_mesures_rejette_champ_omis():
    with pytest.raises(RapportError, match="fraction_visible_observee_et_incertitude"):
        _mesures_indisponible(fraction_visible_observee_et_incertitude="")


def test_resultat_accepte_verdicts_reels():
    resultat = _resultat_indisponible(verdict_par_modele={"S": Verdict.COMPATIBLE, "P": Verdict.INCOMPATIBLE})
    assert resultat.verdict_par_modele["S"] == Verdict.COMPATIBLE


def test_resultat_rejette_champ_omis():
    with pytest.raises(RapportError, match="motif_indetermination"):
        _resultat_indisponible(motif_indetermination=None)


# --- FicheObservation / champs_indisponibles ---

def test_fiche_observation_toute_indisponible_sauf_identification_se_construit():
    fiche = _fiche_toute_indisponible()
    assert isinstance(fiche, FicheObservation)


def test_champs_indisponibles_liste_tout_ce_qui_manque():
    fiche = _fiche_toute_indisponible()
    manquants = champs_indisponibles(fiche)
    # cinq sections entièrement indisponibles, chacune avec son nombre de champs propre
    assert "poste_observation.observateur" in manquants
    assert "atmosphere.classe_de_chaque_donnee" in manquants
    assert "resultat.verdict_par_modele" in manquants
    # rien de la section Identification (entièrement renseignée) ne doit apparaître
    assert not any(m.startswith("identification.") for m in manquants)


def test_champs_indisponibles_vide_si_tout_est_renseigne():
    distance = GrandeurGeodesique(
        nom="distance", valeur=1000.0, unite="m", referentiel="WGS84", source="test", incertitude=1.0
    )
    fiche = _fiche_toute_indisponible(
        geometrie=_geometrie_indisponible(
            distance_D_algorithme_et_incertitude=distance,
            azimut_geodesique=distance,
            rayon_courbure_euler=distance,
            profil_intermediaire_source_et_pas="source X, pas 500 m",
            altitude_maximale_profil_et_marge=(120.0, 30.0),
        )
    )
    manquants = champs_indisponibles(fiche)
    assert not any(m.startswith("geometrie.") for m in manquants)


# --- resume_verdicts ---

def test_resume_verdicts_formatte_correctement():
    resume = resume_verdicts({"S": Verdict.COMPATIBLE, "P": Verdict.INCOMPATIBLE})
    assert resume == "S: compatible · P: incompatible"


def test_resume_verdicts_rejette_indisponible():
    with pytest.raises(RapportError, match="indisponible"):
        resume_verdicts(INDISPONIBLE)


def test_resume_verdicts_rejette_mapping_vide_ou_absent():
    with pytest.raises(RapportError):
        resume_verdicts({})
    with pytest.raises(RapportError):
        resume_verdicts("S: compatible")  # une chaîne n'est pas une correspondance


def test_resume_verdicts_rejette_valeur_qui_n_est_pas_un_verdict():
    with pytest.raises(RapportError, match="Verdict"):
        resume_verdicts({"S": "compatible"})
