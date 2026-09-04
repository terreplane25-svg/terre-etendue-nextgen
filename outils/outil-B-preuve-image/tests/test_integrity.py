"""
Tests de integrity.py — empreintes SHA-256 sur de vrais fichiers temporaires,
statut de l'horodatage (§17.1), discipline des opérations admises/exclues
(§17.2), journal en ajout seul, et empreinte de manifeste (§34).
"""

import hashlib
from datetime import datetime, timedelta, timezone

import pytest

from preuve_image.integrity import (
    CopieDeTravail,
    DeclarationIntegrite,
    EcartManifeste,
    HorodatageTiers,
    IntegrityError,
    JournalOperations,
    OPERATIONS_ADMISES,
    OPERATIONS_EXCLUES,
    OperationJournal,
    calculer_manifeste,
    classer_operation,
    comparer_manifestes,
    empreinte_fichier,
    empreinte_manifeste,
    statut_horodatage,
    verifier_chaine_operations,
    verifier_integrite,
)


def _horodatage(jour=3, heure=10):
    return datetime(2026, 9, jour, heure, 0, tzinfo=timezone.utc)


# --- empreinte_fichier / verifier_integrite ---

def test_empreinte_fichier_correspond_a_hashlib(tmp_path):
    fichier = tmp_path / "photo.raw"
    contenu = b"contenu binaire simule d'une prise de vue" * 1000
    fichier.write_bytes(contenu)

    attendu = hashlib.sha256(contenu).hexdigest()
    assert empreinte_fichier(fichier) == attendu


def test_empreinte_fichier_par_petits_blocs_donne_le_meme_resultat(tmp_path):
    fichier = tmp_path / "gros_fichier.raw"
    contenu = bytes(range(256)) * 5000
    fichier.write_bytes(contenu)

    attendu = hashlib.sha256(contenu).hexdigest()
    assert empreinte_fichier(fichier, taille_bloc=17) == attendu  # bloc volontairement petit et non aligné


def test_empreinte_fichier_leve_si_fichier_absent(tmp_path):
    with pytest.raises(IntegrityError):
        empreinte_fichier(tmp_path / "inexistant.raw")


def test_verifier_integrite(tmp_path):
    fichier = tmp_path / "photo.raw"
    fichier.write_bytes(b"donnees")
    empreinte = empreinte_fichier(fichier)

    assert verifier_integrite(fichier, empreinte) is True
    assert verifier_integrite(fichier, empreinte.upper()) is True  # insensible à la casse
    assert verifier_integrite(fichier, "0" * 64) is False


def test_verifier_integrite_rejette_empreinte_malformee(tmp_path):
    fichier = tmp_path / "photo.raw"
    fichier.write_bytes(b"donnees")
    with pytest.raises(IntegrityError):
        verifier_integrite(fichier, "pas-une-empreinte")


# --- DeclarationIntegrite ---

def test_declaration_integrite_normalise_la_casse(tmp_path):
    fichier = tmp_path / "photo.raw"
    fichier.write_bytes(b"donnees")
    empreinte = empreinte_fichier(fichier)

    d = DeclarationIntegrite(
        fichier="photo.raw", empreinte=empreinte.upper(), date_calcul=_horodatage(), operateur="A. Dupont"
    )
    assert d.empreinte == empreinte.lower()


def test_declaration_integrite_exige_fichier_et_operateur():
    with pytest.raises(IntegrityError):
        DeclarationIntegrite(fichier="", empreinte="0" * 64, date_calcul=_horodatage(), operateur="op")
    with pytest.raises(IntegrityError):
        DeclarationIntegrite(fichier="photo.raw", empreinte="0" * 64, date_calcul=_horodatage(), operateur=" ")


def test_declaration_integrite_rejette_empreinte_malformee():
    with pytest.raises(IntegrityError):
        DeclarationIntegrite(fichier="photo.raw", empreinte="xyz", date_calcul=_horodatage(), operateur="op")


# --- HorodatageTiers et statut_horodatage ---

def test_horodatage_tiers_exige_tiers_et_reference():
    with pytest.raises(IntegrityError):
        HorodatageTiers(empreinte="0" * 64, tiers="", date_reception=_horodatage(), reference="ref")
    with pytest.raises(IntegrityError):
        HorodatageTiers(empreinte="0" * 64, tiers="Tiers SA", date_reception=_horodatage(), reference=" ")


def test_statut_sans_horodatage():
    d = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(), operateur="op")
    assert statut_horodatage(d, None) == "déclaration de l'opérateur seule — non daté par un tiers"


def test_statut_horodate_le_jour_meme():
    d = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(jour=3, heure=9), operateur="op")
    h = HorodatageTiers(empreinte="a" * 64, tiers="Tiers SA", date_reception=_horodatage(jour=3, heure=18), reference="jeton-123")
    assert statut_horodatage(d, h) == "daté par un tiers le jour même"


def test_statut_horodate_avec_delai():
    d = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(jour=3), operateur="op")
    h = HorodatageTiers(empreinte="a" * 64, tiers="Tiers SA", date_reception=_horodatage(jour=5), reference="jeton-123")
    assert statut_horodatage(d, h) == "daté par un tiers, mais pas le jour même — délai à justifier au rapport"


def test_statut_rejette_horodatage_sur_une_autre_empreinte():
    d = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(), operateur="op")
    h = HorodatageTiers(empreinte="b" * 64, tiers="Tiers SA", date_reception=_horodatage(), reference="jeton-123")
    with pytest.raises(IntegrityError):
        statut_horodatage(d, h)


# --- §17.2 : opérations admises et exclues ---

def test_toutes_les_operations_admises_sont_reconnues():
    for nom in OPERATIONS_ADMISES:
        assert classer_operation(nom) is True


def test_toutes_les_operations_exclues_sont_reconnues():
    for nom in OPERATIONS_EXCLUES:
        assert classer_operation(nom) is False


def test_operation_inconnue_rejetee():
    with pytest.raises(IntegrityError):
        classer_operation("filtre_instagram")


def test_chaine_toute_admise_ne_leve_pas():
    verifier_chaine_operations(["reglage_contraste_luminosite", "recadrage_declare_coordonnees_conservees"])


def test_chaine_avec_une_exclue_leve_et_la_nomme():
    with pytest.raises(IntegrityError, match="reduction_bruit_non_lineaire"):
        verifier_chaine_operations(["reglage_contraste_luminosite", "reduction_bruit_non_lineaire"])


# --- Journal en ajout seul et copie de travail ---

def test_operation_journal_exige_description():
    with pytest.raises(IntegrityError):
        OperationJournal(horodatage=_horodatage(), nom="reglage_contraste_luminosite", description=" ")


def test_operation_journal_rejette_nom_non_reconnu():
    with pytest.raises(IntegrityError):
        OperationJournal(horodatage=_horodatage(), nom="filtre_instagram", description="test")


def test_journal_operations_ajout_seul():
    journal = JournalOperations()
    assert len(journal) == 0
    journal.ajouter(
        OperationJournal(horodatage=_horodatage(), nom="reglage_contraste_luminosite", description="contraste +5%")
    )
    journal.ajouter(
        OperationJournal(horodatage=_horodatage(jour=4), nom="recadrage_declare_coordonnees_conservees", description="recadrage 100x100")
    )
    assert len(journal) == 2
    assert journal.noms_operations() == (
        "reglage_contraste_luminosite",
        "recadrage_declare_coordonnees_conservees",
    )
    # aucune méthode de suppression ou de remplacement n'existe sur la classe (§34 : ajout seul)
    assert not hasattr(journal, "supprimer")
    assert not hasattr(journal, "vider")
    assert not hasattr(journal, "__delitem__")
    assert not hasattr(journal, "__setitem__")


def test_copie_de_travail_valide_si_operations_admises():
    origine = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(), operateur="op")
    copie = CopieDeTravail(origine=origine)
    copie.journal.ajouter(
        OperationJournal(horodatage=_horodatage(), nom="conversion_lineaire_sans_accentuation", description="dev. RAW")
    )
    assert copie.est_valide_pour_mesure() is True
    assert copie.operation_disqualifiante() is None


def test_copie_de_travail_invalide_si_operation_exclue():
    origine = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(), operateur="op")
    copie = CopieDeTravail(origine=origine)
    copie.journal.ajouter(
        OperationJournal(horodatage=_horodatage(), nom="conversion_lineaire_sans_accentuation", description="dev. RAW")
    )
    copie.journal.ajouter(
        OperationJournal(horodatage=_horodatage(), nom="accentuation_agressive", description="netteté +80")
    )
    assert copie.est_valide_pour_mesure() is False
    assert copie.operation_disqualifiante() == "accentuation_agressive"


def test_chaque_copie_de_travail_a_son_propre_journal():
    origine = DeclarationIntegrite(fichier="photo.raw", empreinte="a" * 64, date_calcul=_horodatage(), operateur="op")
    copie_1 = CopieDeTravail(origine=origine)
    copie_2 = CopieDeTravail(origine=origine)
    copie_1.journal.ajouter(
        OperationJournal(horodatage=_horodatage(), nom="reglage_contraste_luminosite", description="test")
    )
    assert len(copie_1.journal) == 1
    assert len(copie_2.journal) == 0  # le default_factory ne partage pas l'instance


# --- §34 : manifeste et empreinte de l'archive ---

def test_calculer_manifeste(tmp_path):
    (tmp_path / "a.raw").write_bytes(b"aaa")
    (tmp_path / "sous_dossier").mkdir()
    (tmp_path / "sous_dossier" / "b.raw").write_bytes(b"bbb")

    manifeste = calculer_manifeste(tmp_path)

    assert set(manifeste) == {"a.raw", "sous_dossier/b.raw"}
    assert manifeste["a.raw"] == hashlib.sha256(b"aaa").hexdigest()
    assert manifeste["sous_dossier/b.raw"] == hashlib.sha256(b"bbb").hexdigest()


def test_calculer_manifeste_filtre_par_suffixe(tmp_path):
    (tmp_path / "a.raw").write_bytes(b"aaa")
    (tmp_path / "notes.txt").write_bytes(b"notes")

    manifeste = calculer_manifeste(tmp_path, suffixes=[".raw"])
    assert set(manifeste) == {"a.raw"}


def test_calculer_manifeste_dossier_absent(tmp_path):
    with pytest.raises(IntegrityError):
        calculer_manifeste(tmp_path / "n_existe_pas")


def test_empreinte_manifeste_independante_de_lordre_dinsertion():
    m1 = {"a.raw": "1" * 64, "b.raw": "2" * 64}
    m2 = {"b.raw": "2" * 64, "a.raw": "1" * 64}
    assert empreinte_manifeste(m1) == empreinte_manifeste(m2)


def test_empreinte_manifeste_change_si_contenu_change():
    m1 = {"a.raw": "1" * 64}
    m2 = {"a.raw": "2" * 64}
    assert empreinte_manifeste(m1) != empreinte_manifeste(m2)


def test_comparer_manifestes():
    attendu = {"a.raw": "1" * 64, "b.raw": "2" * 64, "c.raw": "3" * 64}
    actuel = {"a.raw": "1" * 64, "b.raw": "ff" * 32, "d.raw": "4" * 64}  # b modifié, c manquant, d nouveau

    ecart = comparer_manifestes(attendu, actuel)

    assert ecart.manquants == ("c.raw",)
    assert ecart.modifies == ("b.raw",)
    assert ecart.nouveaux == ("d.raw",)
    assert ecart.identique is False


def test_comparer_manifestes_identiques():
    m = {"a.raw": "1" * 64}
    ecart = comparer_manifestes(m, dict(m))
    assert ecart.identique is True
    assert isinstance(ecart, EcartManifeste)
