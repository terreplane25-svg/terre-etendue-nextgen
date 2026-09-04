"""
Tests de chain_of_custody.py — identification, chaîne de détention en ajout
seul, rapport d'acquisition et conformité justifiée, alignés ISO/IEC 27037.
"""

import dataclasses
from datetime import datetime, timedelta, timezone

import pytest

from preuve_image.chain_of_custody import (
    ChainOfCustodyError,
    ChaineDeCustody,
    DossierPreuve,
    ElementPreuve,
    EtatAppareil,
    MethodeAcquisition,
    PRINCIPES_ISO27037,
    RapportAcquisition,
    RegistreConformite,
    RoleIntervenant,
    Transfert,
    description_methode,
    modifie_la_source,
    necessite_specialiste,
)
from preuve_image.metadata import INDISPONIBLE


def _h(heure=9, jour=3):
    return datetime(2026, 9, jour, heure, 0, tzinfo=timezone.utc)


def _element(**overrides):
    valeurs = dict(
        identifiant="EL-001",
        description="smartphone Samsung",
        type_support="téléphone mobile",
        lieu_decouverte="bureau 3",
        date_heure=_h(9),
        identifie_par="A. Dupont",
        etat_appareil=EtatAppareil.ETEINT,
        justification_etat=INDISPONIBLE,
        reference_photographie="IMG_0001.jpg",
    )
    valeurs.update(overrides)
    return ElementPreuve(**valeurs)


# --- ElementPreuve ---

def test_element_preuve_eteint_accepte_justification_indisponible():
    el = _element()
    assert el.etat_appareil == EtatAppareil.ETEINT
    assert el.justification_etat == INDISPONIBLE


def test_element_preuve_allume_exige_justification_reelle():
    with pytest.raises(ChainOfCustodyError, match="justification"):
        _element(etat_appareil=EtatAppareil.ALLUME, justification_etat=INDISPONIBLE)

    el = _element(
        etat_appareil=EtatAppareil.ALLUME,
        justification_etat="maintenu allumé pour préserver la mémoire vive, capture RAM prévue avant extinction",
    )
    assert el.etat_appareil == EtatAppareil.ALLUME


def test_element_preuve_indetermine_exige_aussi_justification_reelle():
    with pytest.raises(ChainOfCustodyError, match="justification"):
        _element(etat_appareil=EtatAppareil.INDETERMINE, justification_etat=INDISPONIBLE)


@pytest.mark.parametrize(
    "champ", ["identifiant", "description", "type_support", "lieu_decouverte", "identifie_par"]
)
def test_element_preuve_rejette_champs_textuels_vides(champ):
    with pytest.raises(ChainOfCustodyError, match=champ):
        _element(**{champ: "  "})


def test_element_preuve_rejette_photographie_omise():
    with pytest.raises(ChainOfCustodyError, match="reference_photographie"):
        _element(reference_photographie=None)


# --- Transfert / ChaineDeCustody ---

def test_transfert_rejette_champs_vides_et_cedant_egal_receveur():
    with pytest.raises(ChainOfCustodyError):
        Transfert(horodatage=_h(), cedant="", receveur="B", raison="r", lieu="l")
    with pytest.raises(ChainOfCustodyError, match="distincts"):
        Transfert(horodatage=_h(), cedant="A", receveur="A", raison="r", lieu="l")


def test_chaine_de_custody_transfert_valide_met_a_jour_le_detenteur():
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    assert chaine.detenteur_actuel == "A. Dupont"
    assert len(chaine) == 0

    chaine.transferer(
        Transfert(horodatage=_h(10), cedant="A. Dupont", receveur="Labo central", raison="transport", lieu="véhicule scellé")
    )
    assert chaine.detenteur_actuel == "Labo central"
    assert len(chaine) == 1
    assert chaine.historique[0].receveur == "Labo central"


def test_chaine_de_custody_rejette_transfert_hors_detenteur_actuel():
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    with pytest.raises(ChainOfCustodyError, match="Rupture de la chaîne"):
        chaine.transferer(
            Transfert(horodatage=_h(10), cedant="Quelqu'un d'autre", receveur="X", raison="r", lieu="l")
        )
    # un transfert rejeté ne doit rien modifier (atomicité)
    assert chaine.detenteur_actuel == "A. Dupont"
    assert len(chaine) == 0


def test_chaine_de_custody_historique_chainé_sur_plusieurs_transferts():
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    chaine.transferer(Transfert(horodatage=_h(10), cedant="A. Dupont", receveur="Labo", raison="transport", lieu="véhicule"))
    chaine.transferer(Transfert(horodatage=_h(11), cedant="Labo", receveur="Expert B", raison="analyse", lieu="labo"))
    assert chaine.detenteur_actuel == "Expert B"
    assert len(chaine) == 2
    assert [t.receveur for t in chaine.historique] == ["Labo", "Expert B"]


def test_chaine_de_custody_est_en_ajout_seul():
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    assert not hasattr(chaine, "supprimer")
    assert not hasattr(chaine, "vider")
    assert not hasattr(chaine, "__delitem__")
    assert not hasattr(chaine, "__setitem__")


def test_chaine_de_custody_exige_element_id_et_detenteur_initial():
    with pytest.raises(ChainOfCustodyError):
        ChaineDeCustody("", "A. Dupont")
    with pytest.raises(ChainOfCustodyError):
        ChaineDeCustody("EL-001", " ")


# --- MethodeAcquisition ---

def test_description_methode_couvre_les_trois_methodes():
    for methode in MethodeAcquisition:
        texte = description_methode(methode)
        assert isinstance(texte, str) and texte.strip()


def test_modifie_la_source_seulement_pour_acquisition_en_direct():
    assert modifie_la_source(MethodeAcquisition.ACQUISITION_EN_DIRECT) is True
    assert modifie_la_source(MethodeAcquisition.COPIE_BIT_A_BIT) is False
    assert modifie_la_source(MethodeAcquisition.COPIE_LOGIQUE) is False


# --- RapportAcquisition ---

def _rapport(**overrides):
    valeurs = dict(
        element_id="EL-001",
        methode=MethodeAcquisition.COPIE_BIT_A_BIT,
        outil="FTK Imager",
        version_outil="4.7.1",
        empreinte_source="a" * 64,
        empreinte_copie="a" * 64,
        debut=_h(12),
        fin=_h(13),
        operateur="Labo central",
        justification_modification_source=INDISPONIBLE,
    )
    valeurs.update(overrides)
    return RapportAcquisition(**valeurs)


def test_rapport_acquisition_integrite_verifiee_si_empreintes_identiques():
    rapport = _rapport()
    assert rapport.integrite_verifiee is True


def test_rapport_acquisition_integrite_non_verifiee_si_empreintes_differentes():
    rapport = _rapport(empreinte_copie="b" * 64)
    assert rapport.integrite_verifiee is False


def test_rapport_acquisition_normalise_la_casse_des_empreintes():
    rapport = _rapport(empreinte_source=("A" * 64).upper(), empreinte_copie="a" * 64)
    assert rapport.empreinte_source == "a" * 64
    assert rapport.integrite_verifiee is True


def test_rapport_acquisition_rejette_empreinte_malformee():
    with pytest.raises(ChainOfCustodyError, match="SHA-256"):
        _rapport(empreinte_source="pas-une-empreinte")


def test_rapport_acquisition_rejette_fin_anterieure_ou_egale_au_debut():
    with pytest.raises(ChainOfCustodyError, match="postérieure"):
        _rapport(debut=_h(13), fin=_h(12))
    with pytest.raises(ChainOfCustodyError, match="postérieure"):
        _rapport(debut=_h(13), fin=_h(13))


@pytest.mark.parametrize("champ", ["element_id", "outil", "version_outil", "operateur"])
def test_rapport_acquisition_rejette_champs_textuels_vides(champ):
    with pytest.raises(ChainOfCustodyError, match=champ):
        _rapport(**{champ: " "})


def test_rapport_acquisition_direct_exige_justification_reelle():
    with pytest.raises(ChainOfCustodyError, match="justification"):
        _rapport(methode=MethodeAcquisition.ACQUISITION_EN_DIRECT, justification_modification_source=INDISPONIBLE)

    rapport = _rapport(
        methode=MethodeAcquisition.ACQUISITION_EN_DIRECT,
        justification_modification_source="système en production, extinction impossible ; RAM capturée avant copie disque",
    )
    assert rapport.methode == MethodeAcquisition.ACQUISITION_EN_DIRECT


def test_rapport_acquisition_copie_logique_accepte_indisponible():
    rapport = _rapport(methode=MethodeAcquisition.COPIE_LOGIQUE, justification_modification_source=INDISPONIBLE)
    assert rapport.justification_modification_source == INDISPONIBLE


# --- Compétence ---

@pytest.mark.parametrize(
    "role,methode,attendu",
    [
        (RoleIntervenant.SPECIALISTE, MethodeAcquisition.ACQUISITION_EN_DIRECT, False),
        (RoleIntervenant.SPECIALISTE, MethodeAcquisition.COPIE_BIT_A_BIT, False),
        (RoleIntervenant.PREMIER_INTERVENANT, MethodeAcquisition.COPIE_LOGIQUE, False),
        (RoleIntervenant.PREMIER_INTERVENANT, MethodeAcquisition.COPIE_BIT_A_BIT, True),
        (RoleIntervenant.PREMIER_INTERVENANT, MethodeAcquisition.ACQUISITION_EN_DIRECT, True),
    ],
)
def test_necessite_specialiste(role, methode, attendu):
    assert necessite_specialiste(methode, role) is attendu


# --- RegistreConformite ---

def test_registre_conformite_accepte_valeurs_reelles_et_sentinel():
    registre = RegistreConformite(
        auditabilite="journal horodaté conservé, accessible à un tiers",
        repetabilite="procédure documentée pas à pas, outils et versions consignés",
        reproductibilite=INDISPONIBLE,
        justifiabilite="chaque action motivée dans le rapport d'intervention",
    )
    assert registre.reproductibilite == INDISPONIBLE


def test_registre_conformite_rejette_principe_omis():
    with pytest.raises(ChainOfCustodyError, match="justifiabilite"):
        RegistreConformite(
            auditabilite="ok", repetabilite="ok", reproductibilite="ok", justifiabilite=None
        )


def test_principes_iso27037_correspond_aux_champs_du_registre():
    noms_champs = tuple(champ.name for champ in dataclasses.fields(RegistreConformite))
    assert PRINCIPES_ISO27037 == noms_champs


# --- DossierPreuve ---

def _conformite_complete():
    return RegistreConformite(
        auditabilite="ok", repetabilite="ok", reproductibilite="ok", justifiabilite="ok"
    )


def test_dossier_preuve_sans_acquisition_pas_pret():
    el = _element()
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    dossier = DossierPreuve(element=el, chaine=chaine, conformite=_conformite_complete())
    assert dossier.acquisition is None
    assert dossier.pret_pour_acquisition_numerique() is False


def test_dossier_preuve_avec_acquisition_integre_pret():
    el = _element()
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    dossier = DossierPreuve(
        element=el, chaine=chaine, conformite=_conformite_complete(), acquisition=_rapport()
    )
    assert dossier.pret_pour_acquisition_numerique() is True


def test_dossier_preuve_avec_acquisition_non_integre_pas_pret():
    el = _element()
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    dossier = DossierPreuve(
        element=el,
        chaine=chaine,
        conformite=_conformite_complete(),
        acquisition=_rapport(empreinte_copie="b" * 64),
    )
    assert dossier.pret_pour_acquisition_numerique() is False


def test_dossier_preuve_rejette_chaine_sur_un_autre_element():
    el = _element()
    chaine = ChaineDeCustody("AUTRE-ID", "A. Dupont")
    with pytest.raises(ChainOfCustodyError, match="ne porte pas sur le même élément"):
        DossierPreuve(element=el, chaine=chaine, conformite=_conformite_complete())


def test_dossier_preuve_rejette_acquisition_sur_un_autre_element():
    el = _element()
    chaine = ChaineDeCustody("EL-001", "A. Dupont")
    with pytest.raises(ChainOfCustodyError, match="rapport d'acquisition ne porte pas sur le même élément"):
        DossierPreuve(
            element=el,
            chaine=chaine,
            conformite=_conformite_complete(),
            acquisition=_rapport(element_id="EL-002"),
        )
