"""
Tests de archive.py — l'arborescence imposée du §34, le verrou (au mieux) sur
10-originaux/, et les petits types propres à ce module. Vérifie aussi que les
fonctions de preuve_image.integrity sont réellement réexportées, pas
réimplémentées (identité d'objet, pas seulement égalité de comportement).
"""

import stat
from datetime import datetime, timezone

import pytest

import preuve_image.integrity as integrity_module
from rapport_expertise.archive import (
    ARBORESCENCE_IMPOSEE,
    ArchiveError,
    DESCRIPTIONS_REPERTOIRES,
    ElementNonDiffuse,
    calculer_manifeste,
    comparer_manifestes,
    creer_arborescence,
    declarer_empreinte_archive,
    empreinte_manifeste,
    JournalOperations,
    nom_dossier_archive,
    originaux_proteges,
    verifier_arborescence,
    verifier_licence_reprise,
    verrouiller_originaux,
)
from rapport_expertise.report_builder import INDISPONIBLE, RapportError


# --- réexports : mêmes objets que preuve_image.integrity, pas une copie ---

def test_reexports_sont_les_memes_objets_que_preuve_image_integrity():
    assert calculer_manifeste is integrity_module.calculer_manifeste
    assert comparer_manifestes is integrity_module.comparer_manifestes
    assert empreinte_manifeste is integrity_module.empreinte_manifeste
    assert JournalOperations is integrity_module.JournalOperations


# --- arborescence imposée ---

def test_arborescence_imposee_dix_repertoires_dans_l_ordre():
    assert ARBORESCENCE_IMPOSEE == (
        "00-preenregistrement",
        "10-originaux",
        "11-empreintes",
        "20-fiche",
        "30-donnees-externes",
        "40-controles",
        "50-mesures",
        "60-calcul",
        "70-rapport",
        "90-journal",
    )


def test_chaque_repertoire_impose_a_sa_description():
    for nom in ARBORESCENCE_IMPOSEE:
        assert nom in DESCRIPTIONS_REPERTOIRES
        assert DESCRIPTIONS_REPERTOIRES[nom].strip()


def test_nom_dossier_archive():
    assert nom_dossier_archive("OBS-2026-001") == "dossier-OBS-2026-001"


def test_nom_dossier_archive_rejette_identifiant_vide():
    with pytest.raises(ArchiveError):
        nom_dossier_archive("  ")


def test_creer_arborescence_cree_les_dix_repertoires(tmp_path):
    racine = creer_arborescence(tmp_path, "OBS-2026-001")
    assert racine == tmp_path / "dossier-OBS-2026-001"
    for nom in ARBORESCENCE_IMPOSEE:
        assert (racine / nom).is_dir()
    assert verifier_arborescence(racine) == ()


def test_creer_arborescence_refuse_d_ecraser_une_archive_existante(tmp_path):
    creer_arborescence(tmp_path, "OBS-2026-001")
    with pytest.raises(ArchiveError, match="existe déjà"):
        creer_arborescence(tmp_path, "OBS-2026-001")


def test_verifier_arborescence_detecte_repertoire_manquant(tmp_path):
    racine = creer_arborescence(tmp_path, "OBS-2026-002")
    (racine / "40-controles").rmdir()
    manquants = verifier_arborescence(racine)
    assert manquants == ("40-controles",)


def test_verifier_arborescence_leve_si_racine_absente(tmp_path):
    with pytest.raises(ArchiveError):
        verifier_arborescence(tmp_path / "n_existe_pas")


# --- verrouillage (au mieux) de 10-originaux/ ---

def test_verrouiller_originaux_retire_les_bits_d_ecriture(tmp_path):
    racine = creer_arborescence(tmp_path, "OBS-2026-003")
    originaux = racine / "10-originaux"
    (originaux / "IMG_0001.CR3").write_bytes(b"contenu simule")
    (originaux / "sous_dossier").mkdir()
    (originaux / "sous_dossier" / "IMG_0002.CR3").write_bytes(b"autre contenu")

    assert originaux_proteges(originaux) is False  # pas encore verrouillé
    verrouiller_originaux(originaux)
    assert originaux_proteges(originaux) is True

    bits_ecriture = stat.S_IWUSR | stat.S_IWGRP | stat.S_IWOTH
    for chemin in [originaux, originaux / "IMG_0001.CR3", originaux / "sous_dossier", originaux / "sous_dossier" / "IMG_0002.CR3"]:
        assert not (chemin.stat().st_mode & bits_ecriture), f"{chemin} porte encore un bit d'écriture"

    # Remise en écriture pour laisser pytest nettoyer tmp_path sans erreur.
    originaux.chmod(0o755)
    for chemin in originaux.rglob("*"):
        chemin.chmod(0o755 if chemin.is_dir() else 0o644)


def test_verrouiller_originaux_leve_si_repertoire_absent(tmp_path):
    with pytest.raises(ArchiveError):
        verrouiller_originaux(tmp_path / "n_existe_pas")


def test_originaux_proteges_leve_si_repertoire_absent(tmp_path):
    with pytest.raises(ArchiveError):
        originaux_proteges(tmp_path / "n_existe_pas")


# --- ElementNonDiffuse ---

def test_element_non_diffuse_normalise_la_casse_de_l_empreinte():
    elem = ElementNonDiffuse(nom_fichier="mire.jpg", empreinte=("A" * 64), detenteur="Labo central")
    assert elem.empreinte == "a" * 64


def test_element_non_diffuse_rejette_champs_vides_et_empreinte_malformee():
    with pytest.raises(ArchiveError):
        ElementNonDiffuse(nom_fichier="", empreinte="a" * 64, detenteur="Labo")
    with pytest.raises(ArchiveError):
        ElementNonDiffuse(nom_fichier="mire.jpg", empreinte="a" * 64, detenteur=" ")
    with pytest.raises(ArchiveError):
        ElementNonDiffuse(nom_fichier="mire.jpg", empreinte="pas-une-empreinte", detenteur="Labo")


# --- verifier_licence_reprise ---

def test_verifier_licence_reprise_accepte_texte_reel_et_sentinel():
    assert verifier_licence_reprise("CC-BY-4.0") == "CC-BY-4.0"
    assert verifier_licence_reprise(INDISPONIBLE) == INDISPONIBLE


def test_verifier_licence_reprise_rejette_absence():
    with pytest.raises(RapportError):
        verifier_licence_reprise(None)


# --- déclaration de l'empreinte de l'archive (§34) ---

def test_declarer_empreinte_archive(tmp_path):
    racine = creer_arborescence(tmp_path, "OBS-2026-004")
    (racine / "10-originaux" / "IMG_0001.CR3").write_bytes(b"contenu simule")
    (racine / "20-fiche" / "fiche.txt").write_bytes(b"fiche standard")

    manifeste = calculer_manifeste(racine)
    declaration = declarer_empreinte_archive(
        manifeste, operateur="A. Dupont", date_calcul=datetime(2026, 9, 3, 12, 0, tzinfo=timezone.utc)
    )
    assert declaration.fichier == "SHA256SUMS"
    assert declaration.empreinte == empreinte_manifeste(manifeste)
    assert declaration.operateur == "A. Dupont"


def test_manifeste_et_comparaison_bout_en_bout(tmp_path):
    racine = creer_arborescence(tmp_path, "OBS-2026-005")
    (racine / "10-originaux" / "IMG_0001.CR3").write_bytes(b"contenu simule")

    manifeste_attendu = calculer_manifeste(racine)

    # une modification après coup doit être détectée par le manifeste recalculé
    (racine / "10-originaux" / "IMG_0001.CR3").write_bytes(b"contenu modifie")
    manifeste_actuel = calculer_manifeste(racine)

    ecart = comparer_manifestes(manifeste_attendu, manifeste_actuel)
    assert ecart.identique is False
    assert "10-originaux/IMG_0001.CR3" in ecart.modifies
