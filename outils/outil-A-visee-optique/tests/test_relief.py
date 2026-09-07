"""
Le relief entre l'observateur et la cible.

CE QUI EST ÉPROUVÉ, ET PAR QUEL MOYEN
─────────────────────────────────────
La ligne de visée est vérifiée par une voie INDÉPENDANTE de son
implémentation : l'approximation classique du bombement, d(D−d)/2R, qui est
le premier terme du développement de la construction exacte. Comparer la
fonction à elle-même ne prouverait rien ; comparer à une formule tirée d'une
autre source, si.

Deux termes séparent les deux voies, et ils sont traités séparément plutôt
que noyés dans une tolérance choisie pour passer : un terme de PENTE, en
(z−h)²·d(D−d)/(R·D²), qui domine à courte portée et qu'on vérifie à 1 % près
en le PRÉDISANT ; et un terme de courbure d'ordre supérieur, qui prend le
relais au-delà de quelques dizaines de kilomètres et qu'on isole en testant
une visée horizontale, où le premier s'annule. Une tolérance unique aurait
été trop lâche à 1 km et trop serrée à 100 km — et l'ajuster jusqu'à ce
qu'elle passe aurait fait un test qui ne teste rien.

La séparation courbure / relief est éprouvée par des cas où les deux causes
sont DISSOCIÉES : une cible entièrement au-dessus de l'horizon mais masquée
par une colline, et une cible sous l'horizon sur un trajet parfaitement plat.
Un module qui confondrait les deux passerait tous les tests où elles vont
ensemble.
"""

import math

import pytest

from visee_optique.geometry import Cible, GeometryError
from visee_optique.relief import (
    Obstacle,
    PointProfil,
    ProfilTerrain,
    ReliefError,
    RELIEF_NON_EVALUE,
    altitude_ligne_de_visee,
    altitude_ligne_de_visee_plane,
    analyser_relief,
    profil_depuis_couples,
)

R_TERRE = 6371008.8


# ─────────────────────────────────────────────────────────────────────────────
# La ligne de visée, confrontée à une formule d'une autre origine
# ─────────────────────────────────────────────────────────────────────────────


def bombement_classique(d, D, R):
    """L'approximation usuelle des bilans de liaison : d(D−d)/2R.

    Elle ne vient pas de ce paquet. C'est ce qui en fait un contrôle.
    """
    return d * (D - d) / (2.0 * R)


def terme_de_pente(d, D, h, z, R):
    """Le second terme négligé par la formule classique, quand la visée est inclinée.

    La formule d(D−d)/2R suppose la visée quasi horizontale. Dès que les deux
    extrémités sont à des altitudes différentes, elle omet un terme en
    (z−h)²·d(D−d)/(R·D²). Il n'est pas ajusté ici : il est PRÉDIT, puis
    confronté à l'écart réellement observé.
    """
    return (z - h) ** 2 * d * (D - d) / (R * D ** 2)


@pytest.mark.parametrize("h,z", [(0.0, 98.0), (12.0, 110.0), (0.0, 300.0), (50.0, 450.0)])
@pytest.mark.parametrize("frac", [0.2, 0.5, 0.8])
def test_l_ecart_a_la_formule_classique_est_le_terme_de_pente_predit(h, z, frac):
    """À courte portée, l'écart n'est pas un résidu vague : c'est un terme connu.

    Vérifier « l'écart est petit » ne prouverait presque rien — n'importe
    quelle erreur de signe sur un terme d'ordre supérieur passerait. On
    vérifie donc que l'écart VAUT ce que la théorie prédit, à 1 % près, sur
    quatre géométries et trois positions le long du trajet.

    La portée est courte (2 km) pour que le terme de courbure d'ordre suivant,
    qui prend le relais au-delà, reste négligeable devant celui-ci : c'est ce
    qui permet d'isoler celui qu'on teste.
    """
    D = 2_000.0
    d = frac * D
    exact = altitude_ligne_de_visee(d, D, h, z, R_TERRE)
    classique = h + (z - h) * (d / D) - bombement_classique(d, D, R_TERRE)
    predit = -terme_de_pente(d, D, h, z, R_TERRE)
    assert (exact - classique) == pytest.approx(predit, rel=0.01)


def corde_exacte(d, D, h, R):
    """Altitude d'une corde entre deux points de MÊME rayon — forme fermée exacte.

    Les deux extrémités sont au rayon R+h, séparées de θ_D. La corde est
    symétrique : sa perpendiculaire depuis le centre tombe au milieu, et son
    rayon à l'angle θ vaut (R+h)·cos(θ_D/2)/cos(θ−θ_D/2).

    Ce n'est pas une approximation, et cela ne passe par aucune des fonctions
    testées : c'est de la trigonométrie de collège sur un triangle isocèle. La
    concordance attendue est donc celle des flottants, pas celle d'un
    développement tronqué.
    """
    theta_d, theta = D / R, d / R
    return (R + h) * math.cos(theta_d / 2) / math.cos(theta - theta_d / 2) - R


@pytest.mark.parametrize("D", [1_000.0, 10_000.0, 35_000.0, 100_000.0, 300_000.0])
def test_visee_horizontale_egale_la_corde_exacte(D):
    """Le contrôle le plus fort disponible : une forme fermée indépendante.

    Sur un trajet horizontal, la ligne de visée EST la corde du cercle passant
    par les deux extrémités, dont l'altitude a une expression exacte. Les deux
    doivent coïncider au niveau du bruit de calcul — à 10⁻⁹ m sur des rayons de
    6,4·10⁶ m, soit l'epsilon machine.

    C'est plus sévère que la comparaison à la formule classique, qui n'est
    qu'un développement tronqué : celle-ci laisse passer les erreurs d'ordre
    supérieur, celle-là non.
    """
    h = 12.0
    for frac in (0.1, 0.25, 0.5, 0.75, 0.9):
        d = frac * D
        assert altitude_ligne_de_visee(d, D, h, h, R_TERRE) == pytest.approx(
            corde_exacte(d, D, h, R_TERRE), abs=1e-8)


@pytest.mark.parametrize("D", [1_000.0, 10_000.0, 35_000.0])
def test_visee_horizontale_concorde_aussi_avec_le_bombement_classique(D):
    """Et le pont vers la littérature : d(D−d)/2R, dans son domaine de validité.

    Ce test est plus faible que le précédent — c'est voulu. Il vérifie que la
    construction exacte est bien LA MÊME CHOSE que la formule que tout le monde
    emploie, et pas une quantité voisine issue d'une convention différente.
    Au-delà de quelques dizaines de kilomètres, l'approximation décroche : ce
    n'est pas un défaut de la construction, et le domaine est borné ici plutôt
    que la tolérance élargie jusqu'à ne plus rien dire.
    """
    h = 12.0
    for frac in (0.1, 0.25, 0.5, 0.75, 0.9):
        d = frac * D
        bombement = bombement_classique(d, D, R_TERRE)
        assert altitude_ligne_de_visee(d, D, h, h, R_TERRE) == pytest.approx(
            h - bombement, abs=1e-5 * bombement + 1e-9)


def test_ligne_de_visee_passe_par_ses_deux_extremites():
    """Aux deux bouts, la visée est à l'altitude des points qu'elle joint."""
    D, h, z = 35_610.7, 12.0, 110.0
    assert altitude_ligne_de_visee(0.0, D, h, z, R_TERRE) == pytest.approx(h, abs=1e-9)
    assert altitude_ligne_de_visee(D, D, h, z, R_TERRE) == pytest.approx(z, abs=1e-6)


def test_la_visee_plane_est_une_droite():
    D, h, z = 20_000.0, 5.0, 105.0
    assert altitude_ligne_de_visee_plane(0.0, D, h, z) == pytest.approx(5.0)
    assert altitude_ligne_de_visee_plane(D / 2, D, h, z) == pytest.approx(55.0)
    assert altitude_ligne_de_visee_plane(D, D, h, z) == pytest.approx(105.0)


def test_la_visee_spherique_passe_toujours_sous_la_visee_plane():
    """C'est la définition même du bombement : au milieu, l'écart est maximal.

    Si ce test tombait, le signe de la correction serait inversé — et un relief
    serait déclaré franchi là où il masque.
    """
    D, h, z = 50_000.0, 10.0, 200.0
    for frac in (0.2, 0.5, 0.8):
        d = frac * D
        assert altitude_ligne_de_visee(d, D, h, z, R_TERRE) < altitude_ligne_de_visee_plane(d, D, h, z)


def test_un_rayon_effectif_plus_grand_releve_la_visee():
    """k > 0 courbe le rayon vers le sol : à surface donnée, la visée passe plus haut."""
    D, h, z, d = 40_000.0, 10.0, 150.0, 20_000.0
    sans = altitude_ligne_de_visee(d, D, h, z, R_TERRE)
    avec = altitude_ligne_de_visee(d, D, h, z, R_TERRE / (1 - 0.13))
    assert avec > sans


def test_domaine_refuse():
    with pytest.raises(ReliefError):
        altitude_ligne_de_visee(0.0, 1000.0, 0.0, 0.0, 0.0)
    with pytest.raises(ReliefError):
        altitude_ligne_de_visee(0.0, 0.0, 0.0, 0.0, R_TERRE)
    with pytest.raises(GeometryError):
        # Un quart de circonférence : la construction n'y a plus de sens.
        altitude_ligne_de_visee(0.0, R_TERRE * math.pi / 2, 0.0, 0.0, R_TERRE)


# ─────────────────────────────────────────────────────────────────────────────
# Le profil : ce qu'il refuse d'être
# ─────────────────────────────────────────────────────────────────────────────


def test_profil_exige_une_source():
    with pytest.raises(ReliefError, match="source"):
        ProfilTerrain(points=(PointProfil(0, 0), PointProfil(10, 0)), source="  ")


def test_profil_exige_deux_points():
    with pytest.raises(ReliefError, match="deux points"):
        ProfilTerrain(points=(PointProfil(0, 0),), source="essai")


def test_profil_exige_des_distances_croissantes():
    """Un profil désordonné se lirait de travers sans jamais lever d'erreur."""
    with pytest.raises(ReliefError, match="croissants"):
        profil_depuis_couples([(0, 0), (500, 10), (200, 5)], source="essai")


# ─────────────────────────────────────────────────────────────────────────────
# Courbure et relief : deux causes, jamais confondues
# ─────────────────────────────────────────────────────────────────────────────


def plat(D, n=50, altitude=0.0):
    return profil_depuis_couples(
        [(D * i / n, altitude) for i in range(n + 1)],
        source="profil d'essai, terrain plat",
        pas_m=D / n,
    )


def test_relief_non_evalue_n_est_pas_absence_d_obstacle():
    """Sans profil, le résultat déclare l'ignorance — il ne conclut pas.

    C'est le point le plus important du module : rendre False ici
    transformerait une lacune de donnée en constat d'absence d'obstacle.
    """
    a = analyser_relief(30_000.0, 10.0, Cible(H=110.0), R_TERRE, profil=None)
    assert a.relief_evalue is False
    assert a.masque_par_le_relief is None
    assert a.motif_relief_non_evalue == RELIEF_NON_EVALUE
    assert a.obstacles == ()
    assert a.marge_minimale_m is None
    # La courbure, elle, est bien calculée : les deux sont indépendantes.
    assert a.hauteur_occultee_courbure_m > 0


def test_terrain_plat_ne_masque_rien():
    D = 30_000.0
    a = analyser_relief(D, 10.0, Cible(H=110.0), R_TERRE, profil=plat(D))
    assert a.relief_evalue is True
    assert a.masque_par_le_relief is False
    assert a.obstacle_le_plus_genant is None
    assert a.marge_minimale_m > 0


def test_cible_entierement_visible_mais_masquee_par_une_colline():
    """Les deux causes dissociées, premier sens.

    À 8 km, la courbure n'occulte rien d'une cible de 110 m vue de 10 m. Une
    colline de 200 m à mi-chemin la cache pourtant entièrement. Un module qui
    ne distinguerait pas les deux dirait « visible ».
    """
    D = 8_000.0
    cible = Cible(H=110.0)
    couples = [(D * i / 40, 0.0) for i in range(41)]
    couples[20] = (D / 2, 200.0)
    profil = profil_depuis_couples(couples, source="essai — colline à mi-parcours")

    a = analyser_relief(D, 10.0, cible, R_TERRE, profil=profil)
    assert a.hauteur_occultee_courbure_m == 0.0
    assert a.fraction_visible_courbure == 1.0
    assert a.masque_par_le_relief is True
    assert a.obstacle_le_plus_genant.distance_m == pytest.approx(D / 2)
    assert a.obstacle_le_plus_genant.altitude_terrain_m == 200.0
    assert a.obstacle_le_plus_genant.manque_m > 100.0


def test_cible_sous_l_horizon_sur_un_trajet_parfaitement_plat():
    """Les deux causes dissociées, second sens — et le piège qu'il révèle.

    À 60 km, une cible de 110 m vue de 10 m est largement entamée par la
    courbure. Le terrain, lui, est au niveau zéro partout.

    Ici, la visée dirigée vers le sommet PASSE SOUS le niveau de la mer à
    mi-parcours : c'est ce que veut dire « occulté par la courbure ». Une
    comparaison naïve terrain/visée déclarerait donc la mer « obstacle de
    relief », et l'outil imputerait à une topographie ce qui revient à la
    forme de la surface — dans le cas même où la distinction sert le plus.

    La marge minimale est donc bien négative, ET la liste d'obstacles est
    vide : ce sont deux faits distincts, et les deux sont rapportés.
    """
    D = 60_000.0
    a = analyser_relief(D, 10.0, Cible(H=110.0), R_TERRE, profil=plat(D))
    assert a.hauteur_occultee_courbure_m > 100.0
    assert a.fraction_visible_courbure < 0.1
    assert a.marge_minimale_m < 0
    assert a.masque_par_le_relief is False
    assert a.obstacles == ()


def test_un_terrain_a_peine_au_dessus_du_zero_redevient_un_obstacle():
    """La frontière est bien à la surface de référence, pas ailleurs.

    Le même trajet, avec un terrain relevé d'un mètre : ce mètre est du relief,
    et il est nommé. Sans ce test, le filtre pourrait écarter n'importe quoi
    sans qu'on le voie.
    """
    D = 60_000.0
    a = analyser_relief(D, 10.0, Cible(H=110.0), R_TERRE, profil=plat(D, altitude=1.0))
    assert a.masque_par_le_relief is True
    assert a.obstacle_le_plus_genant.altitude_terrain_m == 1.0


def test_le_modele_plan_n_occulte_rien_mais_voit_le_relief():
    """Le relief masque IDENTIQUEMENT dans les deux modèles.

    C'est ce qui en fait un discriminant utilisable : ce que les deux modèles
    prédisent différemment, c'est la courbure seule.
    """
    D = 8_000.0
    couples = [(D * i / 40, 0.0) for i in range(41)]
    couples[20] = (D / 2, 200.0)
    profil = profil_depuis_couples(couples, source="essai")

    plan = analyser_relief(D, 10.0, Cible(H=110.0), None, profil=profil, modele="plan")
    assert plan.hauteur_occultee_courbure_m == 0.0
    assert plan.fraction_visible_courbure == 1.0
    assert plan.masque_par_le_relief is True
    assert plan.rayon_effectif_m is None


def test_les_extremites_ne_se_masquent_pas_elles_memes():
    """Un poste posé au sol ne doit pas se déclarer masqué par le sol.

    Le premier point du profil EST l'observateur, le dernier EST la cible :
    les compter comme obstacles rendrait tout trajet masqué.
    """
    D = 20_000.0
    couples = [(0.0, 400.0)] + [(D * i / 20, 0.0) for i in range(1, 20)] + [(D, 300.0)]
    profil = profil_depuis_couples(couples, source="essai — extrémités hautes")
    a = analyser_relief(D, 400.0, Cible(H=50.0, z_b=300.0), R_TERRE, profil=profil)
    assert a.masque_par_le_relief is False


def test_marge_requise_durcit_le_verdict():
    """Une visée qui frôle un sommet ne conclut pas, si la donnée est incertaine.

    Sans garde, la visée passe. Avec une garde de 5 m — l'incertitude annoncée
    du modèle de terrain —, le même relief devient un obstacle. C'est le
    résultat honnête : l'écart est plus petit que ce que la donnée résout.
    """
    D = 10_000.0
    z_visee_milieu = altitude_ligne_de_visee(D / 2, D, 10.0, 110.0, R_TERRE)
    couples = [(D * i / 20, 0.0) for i in range(21)]
    couples[10] = (D / 2, z_visee_milieu - 1.0)  # 1 m sous la visée
    profil = profil_depuis_couples(couples, source="essai", incertitude_verticale_m=5.0)

    sans_garde = analyser_relief(D, 10.0, Cible(H=110.0), R_TERRE, profil=profil)
    assert sans_garde.masque_par_le_relief is False
    assert sans_garde.marge_minimale_m == pytest.approx(1.0, abs=1e-6)

    avec_garde = analyser_relief(
        D, 10.0, Cible(H=110.0), R_TERRE, profil=profil, marge_requise_m=5.0,
    )
    assert avec_garde.masque_par_le_relief is True
    assert avec_garde.obstacle_le_plus_genant.manque_m == pytest.approx(4.0, abs=1e-6)


def test_le_plus_genant_est_celui_qui_manque_le_plus():
    D = 12_000.0
    couples = [(D * i / 60, 0.0) for i in range(61)]
    couples[15] = (D * 15 / 60, 150.0)
    couples[30] = (D * 30 / 60, 400.0)   # le pire
    couples[45] = (D * 45 / 60, 200.0)
    profil = profil_depuis_couples(couples, source="essai — trois bosses")
    a = analyser_relief(D, 10.0, Cible(H=110.0), R_TERRE, profil=profil)
    assert len(a.obstacles) == 3
    assert a.obstacle_le_plus_genant.altitude_terrain_m == 400.0
    assert a.distance_marge_minimale_m == pytest.approx(D * 30 / 60)


def test_marge_requise_negative_refusee():
    D = 10_000.0
    with pytest.raises(ReliefError):
        analyser_relief(D, 10.0, Cible(H=110.0), R_TERRE, profil=plat(D), marge_requise_m=-1.0)


def test_l_observateur_pose_au_sol_ne_se_masque_pas_lui_meme():
    """Le cas où la garde aux extrémités sert vraiment.

    Un premier essai de ce test échouait à éprouver quoi que ce soit : avec un
    observateur surélevé, la marge aux extrémités est positive et la garde
    n'est jamais sollicitée. Retirer la garde du code laissait tous les tests
    au vert — ce qui a été constaté en la retirant pour voir.

    Le cas discriminant est celui-ci : l'axe optique est EXACTEMENT à
    l'altitude du sol sous lui, et l'on exige une garde de 5 m au-dessus du
    terrain. Sans le filtre des extrémités, le sol sous les pieds de
    l'opérateur devient « l'obstacle le plus gênant, à 0 m » — et le même
    raisonnement ferait du pied de la cible un obstacle à sa propre
    observation.
    """
    D = 20_000.0
    couples = [(0.0, 50.0)] + [(D * i / 20, 0.0) for i in range(1, 20)] + [(D, 0.0)]
    profil = profil_depuis_couples(couples, source="essai — poste au ras du sol")
    a = analyser_relief(
        D, 50.0, Cible(H=110.0), R_TERRE, profil=profil, marge_requise_m=5.0,
    )
    assert a.masque_par_le_relief is False
    assert all(o.distance_m not in (0.0, D) for o in a.obstacles)
