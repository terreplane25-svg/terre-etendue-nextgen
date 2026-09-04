"""
Tests de decision.py — validation d'images (Tableau 11, §18), régimes
atmosphériques du §19.4, convergence des analystes (§19.5, §25),
dimensionnement d'échantillon (Tableau 18, §27.3), comparaison de modèles
par vraisemblance pénalisée (§27.2), recevabilité (§28.1) et verdict à
trois valeurs (§28.3) — rejoué sur ConditionDiscrimination et
EnveloppeSensibilite réels, comme models.py l'annonçait.
"""

import pytest

from visee_optique.geometry import Cible, IUGG_R1
from visee_optique.models import ConditionDiscrimination, ModeleSpherique, ModeleSurfacePlane
from visee_optique.refraction import HypotheseRefraction
from visee_optique.uncertainty import EnveloppeSensibilite
from visee_optique.decision import (
    CategorieValiditeImage,
    Colonne,
    ComparaisonModeles,
    CriterePenalisation,
    DecisionError,
    DossierVerdict,
    ElementsVerdict,
    Recevabilite,
    RechercheRegime,
    ResultatVerdict,
    SignatureRegime,
    Verdict,
    Z_ALPHA_BILATERAL_0999,
    Z_BETA_PUISSANCE_95,
    classer_validite_image,
    classer_verdict,
    comparer_deux_modeles,
    comparer_modeles,
    convergence_analystes,
    critere_penalise,
    dispersion_analystes,
    ecart_a_enveloppe,
    evaluer_dossier,
    evaluer_recevabilite,
    log_vraisemblance_gaussienne,
    majorer_incertitude_si_reserves,
    taille_echantillon_minimale,
    un_regime_est_etabli,
)


def _hyp(k_min=0.10, k_max=0.50, justification="test"):
    return HypotheseRefraction(k_min=k_min, k_max=k_max, justification=justification)


def _enveloppe(minimum=0.40, maximum=0.55):
    return EnveloppeSensibilite(
        minimum=minimum,
        maximum=maximum,
        combinaison_minimale={"k": 0.10},
        combinaison_maximale={"k": 0.50},
        methode="grille complète",
        n_evaluations=25,
    )


def _condition(satisfaite=True):
    return ConditionDiscrimination(
        delta=0.20 if satisfaite else 0.001,
        combinaison_defavorable={"k": 0.50},
        u_f=0.01,
        facteur=5.0,
        satisfaite=satisfaite,
    )


def _elements(**overrides):
    valeurs = dict(
        fraction_observee=0.47,
        enveloppe_prediction=_enveloppe(),
        u_mesure=0.02,
        seuil_refutation=0.06,
        discrimination=_condition(True),
        regimes_recherches=(),
        toutes_occultations_attribuees=True,
        caracteristique_resolue=True,
        bord_mesurable=True,
        donnees_atmospheriques_suffisantes=True,
        mesures_analystes=(10.0, 10.2, 9.9),
        resolution_effective=1.0,
    )
    valeurs.update(overrides)
    return ElementsVerdict(**valeurs)


# --- §18 : Tableau 11 ---

def test_classer_validite_image_valide_si_tout_colonne_1():
    postes = {"mise_au_point": Colonne.VALIDE, "flou_bouge": Colonne.VALIDE, "turbulence": Colonne.VALIDE}
    assert classer_validite_image(postes) == CategorieValiditeImage.VALIDE


def test_classer_validite_image_reserves_si_aucun_colonne_3():
    postes = {"mise_au_point": Colonne.VALIDE, "turbulence": Colonne.RESERVES}
    assert classer_validite_image(postes) == CategorieValiditeImage.VALIDE_AVEC_RESERVES


def test_classer_validite_image_invalide_des_qu_un_poste_colonne_3():
    postes = {"mise_au_point": Colonne.VALIDE, "exposition": Colonne.NON_VALIDE, "turbulence": Colonne.RESERVES}
    assert classer_validite_image(postes) == CategorieValiditeImage.INVALIDE


def test_classer_validite_image_exige_au_moins_un_poste():
    with pytest.raises(DecisionError):
        classer_validite_image({})


def test_majorer_incertitude_si_reserves():
    assert majorer_incertitude_si_reserves(0.02, 1.5, CategorieValiditeImage.VALIDE) == pytest.approx(0.02)
    assert majorer_incertitude_si_reserves(0.02, 1.5, CategorieValiditeImage.VALIDE_AVEC_RESERVES) == pytest.approx(0.03)


def test_majorer_incertitude_rejette_image_invalide():
    with pytest.raises(DecisionError, match="exclue"):
        majorer_incertitude_si_reserves(0.02, 1.5, CategorieValiditeImage.INVALIDE)


def test_majorer_incertitude_exige_facteur_declare_au_moins_un():
    with pytest.raises(DecisionError):
        majorer_incertitude_si_reserves(0.02, 0.5, CategorieValiditeImage.VALIDE_AVEC_RESERVES)


# --- §19.4 : régimes atmosphériques ---

def test_regime_etabli_seulement_si_les_trois_conditions_tiennent():
    complet = RechercheRegime(SignatureRegime.LOOMING, True, True, True)
    assert complet.etabli is True

    sans_recherche_prealable = RechercheRegime(SignatureRegime.LOOMING, False, True, True)
    assert sans_recherche_prealable.etabli is False  # « jamais introduit après coup »

    sans_signature = RechercheRegime(SignatureRegime.MIRAGE_INFERIEUR, True, False, True)
    assert sans_signature.etabli is False

    sans_donnees = RechercheRegime(SignatureRegime.CONDUIT_OPTIQUE, True, True, False)
    assert sans_donnees.etabli is False


def test_un_regime_est_etabli_sur_une_liste():
    aucun = (RechercheRegime(SignatureRegime.LOOMING, True, True, False),)
    assert un_regime_est_etabli(aucun) is False
    au_moins_un = aucun + (RechercheRegime(SignatureRegime.DEFORMATION_VERTICALE, True, True, True),)
    assert un_regime_est_etabli(au_moins_un) is True


def test_un_regime_est_etabli_liste_vide_est_faux():
    assert un_regime_est_etabli(()) is False


# --- §19.5 / §25 : convergence des analystes ---

def test_dispersion_analystes():
    assert dispersion_analystes([10.0, 10.0, 10.0]) == pytest.approx(0.0)
    assert dispersion_analystes([9.0, 10.0, 11.0]) == pytest.approx(1.0)


def test_dispersion_analystes_exige_au_moins_deux_mesures():
    with pytest.raises(DecisionError):
        dispersion_analystes([10.0])


def test_convergence_analystes_exige_au_moins_trois_mesures():
    with pytest.raises(DecisionError, match="trois"):
        convergence_analystes([10.0, 10.1], resolution_effective=1.0)


def test_convergence_analystes_vraie_si_dispersion_sous_la_resolution():
    assert convergence_analystes([10.0, 10.2, 9.9], resolution_effective=1.0) is True


def test_convergence_analystes_fausse_si_dispersion_depasse_la_resolution():
    assert convergence_analystes([5.0, 10.0, 15.0], resolution_effective=1.0) is False


def test_convergence_analystes_rejette_resolution_non_positive():
    with pytest.raises(DecisionError):
        convergence_analystes([10.0, 10.1, 9.9], resolution_effective=0.0)


# --- §27.3 : Tableau 18 ---

@pytest.mark.parametrize(
    "sigma_sur_delta,n_attendu",
    [(0.20, 1.0), (0.33, 2.7), (0.50, 6.1), (0.75, 13.7), (1.00, 24.4)],
)
def test_taille_echantillon_minimale_reproduit_tableau_18(sigma_sur_delta, n_attendu):
    n = taille_echantillon_minimale(sigma=sigma_sur_delta, delta=1.0)
    assert n == pytest.approx(n_attendu, abs=0.05)


def test_taille_echantillon_minimale_utilise_les_z_deposes():
    facteur_attendu = (Z_ALPHA_BILATERAL_0999 + Z_BETA_PUISSANCE_95) ** 2
    assert taille_echantillon_minimale(1.0, 1.0) == pytest.approx(facteur_attendu)


def test_taille_echantillon_minimale_rejette_domaine_invalide():
    with pytest.raises(DecisionError):
        taille_echantillon_minimale(0.0, 1.0)
    with pytest.raises(DecisionError):
        taille_echantillon_minimale(1.0, 0.0)


# --- §27.2 : vraisemblance pénalisée ---

def test_log_vraisemblance_gaussienne_maximale_a_residu_nul():
    meilleure = log_vraisemblance_gaussienne([0.0, 0.0], [0.02, 0.02])
    moins_bonne = log_vraisemblance_gaussienne([0.05, -0.05], [0.02, 0.02])
    assert meilleure > moins_bonne


def test_log_vraisemblance_gaussienne_rejette_domaine_invalide():
    with pytest.raises(DecisionError):
        log_vraisemblance_gaussienne([0.0, 0.0], [0.02])
    with pytest.raises(DecisionError):
        log_vraisemblance_gaussienne([], [])
    with pytest.raises(DecisionError):
        log_vraisemblance_gaussienne([0.0], [0.0])


def test_critere_penalise_aic_et_bic():
    lv = log_vraisemblance_gaussienne([0.01, -0.01], [0.02, 0.02])
    aic = critere_penalise(lv, nombre_parametres=1, n_observations=2, critere=CriterePenalisation.AIC)
    assert aic == pytest.approx(2 * 1 - 2 * lv)
    bic = critere_penalise(lv, nombre_parametres=1, n_observations=2, critere=CriterePenalisation.BIC)
    import math

    assert bic == pytest.approx(1 * math.log(2) - 2 * lv)


def test_critere_penalise_rejette_parametres_negatifs():
    with pytest.raises(DecisionError):
        critere_penalise(0.0, nombre_parametres=-1, n_observations=5, critere=CriterePenalisation.AIC)


def test_comparer_modeles_favorise_le_meilleur_ajustement_a_parametres_egaux():
    lv_bon = log_vraisemblance_gaussienne([0.01, -0.01, 0.005], [0.02, 0.02, 0.02])
    lv_mauvais = log_vraisemblance_gaussienne([0.1, -0.12, 0.11], [0.02, 0.02, 0.02])
    comp = comparer_modeles("S", lv_bon, 1, "P", lv_mauvais, 1, n_observations=3)
    assert comp.modele_favorise == "S"


def test_comparer_modeles_penalise_les_parametres_a_ajustement_egal():
    # Même vraisemblance pour les deux : seul le nombre de paramètres doit décider.
    lv = log_vraisemblance_gaussienne([0.01, -0.02, 0.015], [0.02, 0.02, 0.02])
    comp = comparer_modeles("avec_parametre", lv, 1, "sans_parametre", lv, 0, n_observations=3)
    assert comp.modele_favorise == "sans_parametre"


def test_comparer_modeles_est_symetrique_dans_l_ordre_des_arguments():
    lv_a = log_vraisemblance_gaussienne([0.01, -0.01], [0.02, 0.02])
    lv_b = log_vraisemblance_gaussienne([0.2, -0.2], [0.02, 0.02])
    direct = comparer_modeles("A", lv_a, 1, "B", lv_b, 0, n_observations=2)
    inverse = comparer_modeles("B", lv_b, 0, "A", lv_a, 1, n_observations=2)
    assert direct.modele_favorise == inverse.modele_favorise == "A"
    assert direct.ecart == pytest.approx(inverse.ecart)


def test_comparer_modeles_egalite_stricte_ne_favorise_personne():
    lv = log_vraisemblance_gaussienne([0.01], [0.02])
    comp = comparer_modeles("A", lv, 1, "B", lv, 1, n_observations=1)
    assert comp.modele_favorise is None


def test_comparer_deux_modeles_lit_le_nombre_de_parametres_sur_les_modeles():
    cible = Cible(H=20.0, z_b=0.0)
    modele_s = ModeleSpherique(R=IUGG_R1, cible=cible, hypothese_k=_hyp())
    modele_p = ModeleSurfacePlane()
    lv_s = log_vraisemblance_gaussienne([0.01, -0.01], [0.02, 0.02])
    lv_p = log_vraisemblance_gaussienne([0.2, -0.2], [0.02, 0.02])
    comp = comparer_deux_modeles(modele_s, lv_s, modele_p, lv_p, n_observations=2)
    assert comp.nom_a == modele_s.nom
    assert comp.nom_b == modele_p.nom
    assert comp.modele_favorise == modele_s.nom


# --- §28.1 : recevabilité ---

def test_evaluer_recevabilite_recevable_si_tout_est_reuni():
    r = evaluer_recevabilite(True, True, CategorieValiditeImage.VALIDE, True)
    assert r.recevable is True
    assert r.motifs_exclusion == ()


def test_evaluer_recevabilite_avec_reserves_reste_recevable():
    r = evaluer_recevabilite(True, True, CategorieValiditeImage.VALIDE_AVEC_RESERVES, True)
    assert r.recevable is True


def test_evaluer_recevabilite_irrecevable_liste_tous_les_motifs():
    r = evaluer_recevabilite(False, False, CategorieValiditeImage.INVALIDE, False)
    assert r.recevable is False
    assert len(r.motifs_exclusion) == 4


def test_evaluer_recevabilite_un_seul_motif_manquant():
    r = evaluer_recevabilite(True, True, CategorieValiditeImage.VALIDE, False)
    assert r.recevable is False
    assert r.motifs_exclusion == ("occultation visible non identifiée ou non attribuée",)


# --- ecart_a_enveloppe ---

def test_ecart_a_enveloppe_nul_a_l_interieur():
    env = _enveloppe(0.40, 0.55)
    assert ecart_a_enveloppe(env, 0.47) == 0.0
    assert ecart_a_enveloppe(env, 0.40) == 0.0
    assert ecart_a_enveloppe(env, 0.55) == 0.0


def test_ecart_a_enveloppe_positif_hors_bornes():
    env = _enveloppe(0.40, 0.55)
    assert ecart_a_enveloppe(env, 0.30) == pytest.approx(0.10)
    assert ecart_a_enveloppe(env, 0.60) == pytest.approx(0.05)


# --- §28.3 : verdict ---

def test_classer_verdict_compatible():
    resultat = classer_verdict(_elements(fraction_observee=0.47))
    assert resultat.verdict == Verdict.COMPATIBLE
    assert len(resultat.motifs) == 1


def test_classer_verdict_incompatible():
    resultat = classer_verdict(_elements(fraction_observee=0.90))
    assert resultat.verdict == Verdict.INCOMPATIBLE


def test_classer_verdict_indetermine_si_discrimination_non_satisfaite():
    resultat = classer_verdict(_elements(discrimination=_condition(False)))
    assert resultat.verdict == Verdict.INDETERMINE
    assert any("28.2" in motif for motif in resultat.motifs)


def test_classer_verdict_indetermine_si_regime_etabli():
    regime = (RechercheRegime(SignatureRegime.LOOMING, True, True, True),)
    resultat = classer_verdict(_elements(fraction_observee=0.90, regimes_recherches=regime))
    assert resultat.verdict == Verdict.INDETERMINE
    assert any("régime" in motif for motif in resultat.motifs)


def test_classer_verdict_indetermine_si_occultation_non_attribuee_malgre_ecart_franchi():
    resultat = classer_verdict(_elements(fraction_observee=0.90, toutes_occultations_attribuees=False))
    assert resultat.verdict == Verdict.INDETERMINE
    assert any("occultation" in motif for motif in resultat.motifs)


def test_classer_verdict_indetermine_si_divergence_analystes():
    resultat = classer_verdict(_elements(mesures_analystes=(5.0, 10.0, 15.0)))
    assert resultat.verdict == Verdict.INDETERMINE
    assert any("divergence" in motif for motif in resultat.motifs)


def test_classer_verdict_cumule_plusieurs_motifs_indetermine():
    regime = (RechercheRegime(SignatureRegime.LOOMING, True, True, True),)
    resultat = classer_verdict(
        _elements(
            fraction_observee=0.90,
            regimes_recherches=regime,
            mesures_analystes=(5.0, 10.0, 15.0),
            donnees_atmospheriques_suffisantes=False,
        )
    )
    assert resultat.verdict == Verdict.INDETERMINE
    assert len(resultat.motifs) == 3


def test_classer_verdict_indetermine_entre_marge_et_seuil():
    # écart supérieur à u_mesure mais inférieur au seuil de réfutation : ni Compatible ni Incompatible.
    resultat = classer_verdict(_elements(fraction_observee=0.60, u_mesure=0.02, seuil_refutation=0.20))
    assert resultat.verdict == Verdict.INDETERMINE


def test_classer_verdict_rejette_u_mesure_negative():
    with pytest.raises(DecisionError):
        _elements(u_mesure=-0.01)


def test_classer_verdict_rejette_seuil_non_positif():
    with pytest.raises(DecisionError):
        _elements(seuil_refutation=0.0)


# --- DossierVerdict ---

def test_evaluer_dossier_cas_recherche():
    dossier = evaluer_dossier(
        "S", _elements(fraction_observee=0.47), "P", _elements(fraction_observee=0.90)
    )
    assert dossier.cas_recherche is True
    assert dossier.alerte_dispositif is False


def test_evaluer_dossier_alerte_si_compatible_avec_les_deux():
    dossier = evaluer_dossier(
        "S", _elements(fraction_observee=0.47), "P", _elements(fraction_observee=0.47)
    )
    assert dossier.cas_recherche is False
    assert dossier.alerte_dispositif is True


def test_evaluer_dossier_alerte_si_incompatible_avec_les_deux():
    dossier = evaluer_dossier(
        "S", _elements(fraction_observee=0.90), "P", _elements(fraction_observee=0.90)
    )
    assert dossier.alerte_dispositif is True


def test_evaluer_dossier_pas_d_alerte_si_indetermine_des_deux_cotes():
    els = _elements(discrimination=_condition(False))
    dossier = evaluer_dossier("S", els, "P", els)
    assert dossier.resultat_a.verdict == Verdict.INDETERMINE
    assert dossier.resultat_b.verdict == Verdict.INDETERMINE
    assert dossier.alerte_dispositif is False  # l'indéterminé ne compte jamais comme une alerte
    assert dossier.cas_recherche is False
