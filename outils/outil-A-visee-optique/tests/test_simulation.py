"""
La règle de lecture du simulateur : quand une visée départage, et quand non.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que la grandeur jugée est bien l'occultation À LA BASE de la cible, non bornée
à la hauteur de celle-ci ; que le seuil est appliqué à sa valeur nommée, des
deux côtés ; et que le modèle plat masque zéro, à toute distance.

CE QU'ILS N'ONT PLUS À ÉTABLIR
──────────────────────────────
Rien sur le relief. Le simulateur ne consulte plus de modèle de terrain : ce
qui bouche réellement la vue depuis un poste se constate sur l'image, pas dans
un fichier d'altitudes. `relief.py` garde ses propres tests ; il n'est
simplement plus consulté ici.
"""

import math

import pytest

from visee_optique.simulation import (
    K_ENVELOPPE_MAX,
    K_ENVELOPPE_MIN,
    K_PLANCHER_ADMIS,
    K_STANDARD,
    MASQUE_MODELE_PLAT_M,
    MOTIF_CONDUIT_OPTIQUE,
    MOTIF_REFRACTION_STANDARD,
    SEUIL_DISCRIMINATION_FRACTION,
    juger,
    motif_refraction,
    verifier_k,
)

H = 100.0


# ── Ce qui est jugé : la base, pas le sommet ────────────────────────────────


def test_c_est_l_occultation_a_la_base_qui_est_rendue():
    """Et elle N'EST PAS bornée à la hauteur de la cible.

    Au-delà de la distance limite, `c` continue de croître : la borner à H
    perdrait l'information au moment où elle devient la plus parlante.
    """
    v = juger(2042.0, 300.0)
    assert v.hauteur_masquee_base_m == pytest.approx(2042.0)
    assert v.fraction_masquee_base > 1.0, "la fraction a été bornée à 1"
    assert v.discriminante is True


def test_le_sommet_encore_visible_n_empeche_pas_de_discriminer():
    """Le pied disparaît bien avant le sommet : c'est lui qu'on regarde.

    15 m masqués sur 100 m : le sommet reste entièrement visible, et pourtant
    les deux modèles prédisent des choses nettement différentes.
    """
    v = juger(15.0, H)
    assert v.discriminante is True
    assert v.hauteur_masquee_base_m == pytest.approx(15.0)


# ── Le modèle plat n'a pas de paramètre ─────────────────────────────────────


def test_le_modele_plat_masque_zero_a_toute_distance():
    """Par construction, pas par approximation.

    L'écart entre les deux prédictions vaut donc exactement l'occultation
    sphérique — c'est ce qui rend la comparaison directe.
    """
    for masquee in (0.0, 11.0, 2042.0):
        v = juger(masquee, H)
        assert v.hauteur_masquee_plat_m == MASQUE_MODELE_PLAT_M == 0.0
        assert v.ecart_entre_modeles_m == pytest.approx(masquee)


# ── Le seuil, aux deux bords ────────────────────────────────────────────────


def test_au_seuil_exact_la_visee_discrimine():
    """10 % pile passe : le seuil est inclusif, et ici l'égalité est atteignable."""
    v = juger(H * SEUIL_DISCRIMINATION_FRACTION, H)
    assert v.fraction_masquee_base == pytest.approx(SEUIL_DISCRIMINATION_FRACTION)
    assert v.discriminante is True
    assert v.seuil_applique == SEUIL_DISCRIMINATION_FRACTION


def test_juste_sous_le_seuil_la_visee_ne_discrimine_pas():
    v = juger(math.nextafter(H * SEUIL_DISCRIMINATION_FRACTION, 0.0), H)
    assert v.discriminante is False
    assert "sous le seuil" in v.motif


def test_une_cible_intacte_ne_departage_rien():
    """Rien de masqué : les deux modèles prédisent la même chose."""
    v = juger(0.0, H)
    assert v.discriminante is False
    assert v.fraction_masquee_base == pytest.approx(0.0)
    assert v.ecart_entre_modeles_m == pytest.approx(0.0)


def test_le_seuil_suit_la_hauteur_de_la_cible():
    """11 m masqués : discriminant sur une cible de 110 m, pas sur 300 m.

    Un seuil en mètres absolus serait sévère sur un phare et laxiste sur une
    falaise ; c'est pour cela qu'il est relatif.
    """
    assert juger(11.0, 110.0).discriminante is True
    assert juger(11.0, 300.0).discriminante is False


# ── Les motifs affichés ─────────────────────────────────────────────────────


def test_le_motif_nomme_les_deux_predictions():
    """Le visiteur doit lire la comparaison, pas seulement le verdict."""
    v = juger(38.5, 110.0)
    assert "modèle sphérique masque 38,5 m" in v.motif
    assert "plat n'en masque aucun" in v.motif
    assert "35,0 %" in v.motif


def test_le_motif_du_refus_dit_le_seuil():
    v = juger(2.0, H)
    assert "2,0 m" in v.motif
    assert "10,0 %" in v.motif


# ── Les refus ───────────────────────────────────────────────────────────────


def test_hauteur_nulle_refusee():
    """Diviser par une hauteur nulle rendrait des fractions infinies."""
    with pytest.raises(ValueError):
        juger(10.0, 0.0)


def test_occultation_negative_refusee():
    """Elle n'a aucun sens physique et trahirait une erreur d'appel."""
    with pytest.raises(ValueError):
        juger(-1.0, H)


# ── Le coefficient de réfraction, standard ou personnalisé ──────────────────


def test_le_motif_nomme_le_k_reellement_employe():
    """Une phrase figée qui dirait 0,13 sur un calcul mené à 0,18 serait un
    mensonge d'affichage — le genre qui survit parce que personne ne relit la
    prose."""
    assert motif_refraction(K_STANDARD) == MOTIF_REFRACTION_STANDARD
    m = motif_refraction(0.18)
    assert "0,18" in m
    assert "PERSONNALISÉ" in m
    assert m != MOTIF_REFRACTION_STANDARD


def test_le_motif_personnalise_dit_que_la_valeur_est_declaree():
    """L'outil ne mesure pas la réfraction : il applique ce qu'on lui donne.

    Le dire est la seule façon d'éviter qu'un k saisi passe pour un k mesuré.
    """
    m = motif_refraction(0.08)
    assert "déclarée, pas mesurée" in m
    assert "Aucune enveloppe" in m


def test_le_motif_standard_annonce_l_enveloppe():
    assert "0,10" in MOTIF_REFRACTION_STANDARD
    assert "0,40" in MOTIF_REFRACTION_STANDARD


@pytest.mark.parametrize("k", [0.0, 0.08, 0.13, 0.20, 0.40, 0.99, K_PLANCHER_ADMIS])
def test_les_k_admis_passent(k):
    verifier_k(k)
    assert isinstance(motif_refraction(k), str)


@pytest.mark.parametrize("k", [1.0, 1.5, 42.0])
def test_le_regime_de_conduit_optique_est_refuse(k):
    """k >= 1 : le rayon épouse la surface, la construction ne s'applique plus.

    Le refus vient de `rayon_effectif`, pas d'un second contrôle écrit ici :
    deux messages pour la même règle divergeraient le jour où l'un change.
    """
    with pytest.raises(ValueError) as e:
        verifier_k(k)
    assert str(e.value) == MOTIF_CONDUIT_OPTIQUE
    # Le message du protocole ne doit PAS remonter au visiteur : le simulateur
    # n'a plus aucun renvoi de paragraphe, et en réintroduire un par un
    # message d'erreur reviendrait à défaire le nettoyage par la petite porte.
    for jargon in ("§", "Tableau"):
        assert jargon not in str(e.value), jargon


@pytest.mark.parametrize("k", [-1.01, -2.0, -100.0])
def test_sous_le_plancher_est_refuse(k):
    with pytest.raises(ValueError, match="plancher"):
        verifier_k(k)


@pytest.mark.parametrize("k", [float("nan"), float("inf"), float("-inf")])
def test_un_k_qui_n_est_pas_un_nombre_est_refuse(k):
    with pytest.raises(ValueError, match="nombre"):
        verifier_k(k)


@pytest.mark.parametrize("k", [1.0, 2.0, -5.0, float("nan")])
def test_le_motif_refuse_aussi_un_k_impossible(k):
    """Sinon l'outil produirait une belle phrase sur un calcul impossible.

    `motif_refraction` est appelé par l'interface juste avant l'affichage :
    s'il ne contrôlait pas, un k hors domaine donnerait un texte plausible
    pendant que le calcul, lui, aurait levé ailleurs — ou pire, pas levé.
    """
    with pytest.raises(Exception):
        motif_refraction(k)


def test_les_deux_motifs_ne_se_confondent_pas():
    """Deux textes distincts, et distincts sur toute la plage utile.

    Un port qui rendrait toujours le texte standard passerait un test qui ne
    compare qu'une seule valeur : on balaie donc la plage.
    """
    for k in (0.0, 0.05, 0.08, 0.10, 0.12, 0.14, 0.18, 0.20, 0.40, 0.90):
        m = motif_refraction(k)
        assert m != MOTIF_REFRACTION_STANDARD, k
        assert ("%.2f" % k).replace(".", ",") in m, k
    assert motif_refraction(K_STANDARD) == MOTIF_REFRACTION_STANDARD


# ── Les constantes ──────────────────────────────────────────────────────────


def test_les_constantes_sont_nommees_et_coherentes():
    """Seuil et réfraction sont des conventions : elles doivent être lisibles."""
    assert SEUIL_DISCRIMINATION_FRACTION == 0.10
    assert K_ENVELOPPE_MIN < K_STANDARD < K_ENVELOPPE_MAX
    assert K_PLANCHER_ADMIS < K_ENVELOPPE_MIN


def test_le_module_ne_depend_plus_du_relief():
    """La suppression du MNT doit se voir dans les DÉPENDANCES du module.

    Chercher des mots dans le fichier ne marcherait pas : la documentation
    explique justement pourquoi le relief a été retiré, et elle le nomme. Ce
    qui compte, ce sont les imports — un import résiduel finirait par être
    réutilisé, et le relief reviendrait par la porte de service.
    """
    import ast

    import visee_optique.simulation as mod

    arbre = ast.parse(open(mod.__file__, encoding="utf-8").read())
    modules = set()
    for noeud in ast.walk(arbre):
        if isinstance(noeud, ast.ImportFrom) and noeud.module:
            modules.add(noeud.module)
        elif isinstance(noeud, ast.Import):
            modules.update(a.name for a in noeud.names)
    assert not any("relief" in m or "altim" in m for m in modules), modules
    # Et aucun nom du relief n'est employé dans le code.
    noms = {n.id for n in ast.walk(arbre) if isinstance(n, ast.Name)}
    noms |= {n.attr for n in ast.walk(arbre) if isinstance(n, ast.Attribute)}
    for interdit in ("AnalyseRelief", "masque_par_le_relief", "obstacle_le_plus_genant",
                     "pas_echantillonnage_m", "profil"):
        assert interdit not in noms, "« %s » est encore employé" % interdit
