"""
relief.py — Le terrain entre l'observateur et la cible (§9.1.3).

POURQUOI CE MODULE EXISTE
─────────────────────────
Le reste du paquet répond à une question de géométrie pure : à cette distance,
sur cette surface, quelle fraction de la cible reste au-dessus de l'horizon ?
Cette question suppose une surface lisse entre les deux points.

Le terrain, lui, n'est pas lisse. Une colline à mi-chemin peut masquer une
cible que la courbure laisserait entièrement visible, et le §9.1.3 est
explicite : un relief qui dépasse la ligne de visée rend le masquage
TOPOGRAPHIQUE, pas géométrique. Confondre les deux, c'est attribuer à la forme
de la Terre ce qui revient à une colline — et l'erreur va dans les deux sens :
on peut aussi bien conclure « le globe masque » là où c'est un talus, que
« rien ne masque » en oubliant le talus.

Ce module sépare donc les deux causes, et les rapporte séparément.

CE QU'IL FAIT, ET CE QU'IL NE FAIT PAS
──────────────────────────────────────
Il fait : placer la ligne de visée exactement dans le repère de la surface
adoptée, comparer le terrain à cette ligne échantillon par échantillon,
nommer l'obstacle le plus gênant, et faire tout cela pour les deux modèles.

Il ne fait pas : produire le profil. Un profil de terrain est une DONNÉE, pas
un calcul — elle vient d'un modèle numérique de terrain, avec une résolution,
une date et une incertitude qui lui sont propres. Ce module la reçoit et dit
ce qu'elle implique ; il n'en invente aucune. Un profil absent donne un
résultat qui déclare le relief NON ÉVALUÉ, jamais un résultat qui déclare
l'absence d'obstacle (§15.4 : une information indisponible se déclare, elle ne
s'estime pas). Les deux ne sont pas la même chose, et les confondre
transformerait une lacune en preuve.

Il ne fait pas non plus : la réfraction du trajet rasant au-dessus du relief.
Le rayon effectif R/(1−k) est appliqué à la ligne de visée comme partout
ailleurs dans ce paquet, ce qui suppose k homogène le long du trajet. Au
voisinage d'un sol chaud, il ne l'est pas.
"""

import math
from dataclasses import dataclass
from typing import List, Optional, Sequence, Tuple

from .geometry import Cible, GeometryError, fraction_visible, hauteur_occultee

__all__ = [
    "ReliefError",
    "PointProfil",
    "ProfilTerrain",
    "Obstacle",
    "AnalyseRelief",
    "altitude_ligne_de_visee",
    "altitude_ligne_de_visee_plane",
    "analyser_relief",
    "RELIEF_NON_EVALUE",
    "Occlusion",
    "grouper_occlusions",
]


class ReliefError(ValueError):
    """Profil incohérent, ou géométrie hors du domaine défini."""


#: Ce que dit un résultat quand aucun profil n'a été fourni. Ce n'est PAS
#: « aucun obstacle » : c'est « personne n'a regardé ».
RELIEF_NON_EVALUE = "relief non évalué — aucun profil de terrain fourni"


@dataclass(frozen=True)
class PointProfil:
    """Un échantillon du terrain le long de la géodésique.

    distance_m : distance depuis l'observateur, mesurée le long de la surface.
    altitude_m : altitude du terrain au-dessus de la même surface de référence
                 que h et z_b. Mélanger une altitude ellipsoïdale à une
                 altitude orthométrique introduit ici une erreur de plusieurs
                 dizaines de mètres, muette et systématique (§12.1).
    """

    distance_m: float
    altitude_m: float


@dataclass(frozen=True)
class ProfilTerrain:
    """Le terrain échantillonné, et ce qu'on sait de sa provenance.

    La source et le pas ne sont pas décoratifs : le §33 les exige tous les
    deux dans la fiche, et un obstacle détecté par un profil au pas de 5 km ne
    veut pas dire la même chose qu'un obstacle détecté au pas de 25 m.
    """

    points: Tuple[PointProfil, ...]
    source: str
    pas_m: Optional[float] = None
    #: Incertitude verticale annoncée par le producteur de la donnée, si elle
    #: l'est. Elle borne ce qu'une marge faible permet de conclure.
    incertitude_verticale_m: Optional[float] = None

    def __post_init__(self):
        if len(self.points) < 2:
            raise ReliefError(
                "Un profil de terrain demande au moins deux points : "
                "un point isolé ne décrit aucun trajet."
            )
        if not self.source or not self.source.strip():
            raise ReliefError(
                "Le profil doit déclarer sa source (§33) : un relief sans "
                "provenance ne permet de conclure ni dans un sens ni dans l'autre."
            )
        precedent = -math.inf
        for p in self.points:
            if p.distance_m < 0:
                raise ReliefError("Une distance de profil ne peut pas être négative.")
            if p.distance_m <= precedent:
                raise ReliefError(
                    "Les points du profil doivent être strictement croissants en "
                    "distance : un profil non ordonné se lit de travers sans jamais "
                    "lever d'erreur."
                )
            precedent = p.distance_m

    @property
    def portee_m(self) -> float:
        return self.points[-1].distance_m - self.points[0].distance_m


@dataclass(frozen=True)
class Obstacle:
    """Un point du terrain qui dépasse la ligne de visée.

    manque_m est POSITIF : c'est de combien le terrain dépasse la ligne. Un
    point qui ne dépasse pas n'est pas un obstacle et n'apparaît pas ici ; sa
    marge est rendue séparément.
    """

    distance_m: float
    altitude_terrain_m: float
    altitude_visee_m: float
    manque_m: float


@dataclass(frozen=True)
class AnalyseRelief:
    """Ce que le relief change, pour un modèle donné.

    `masque_par_le_relief` et `hauteur_occultee_courbure_m` répondent à deux
    questions distinctes, et c'est le point du module : une cible peut être
    intégralement au-dessus de l'horizon géométrique ET intégralement cachée
    par une colline. Les rapporter ensemble sous un seul « invisible »
    perdrait ce qui distingue les deux causes.
    """

    modele: str
    rayon_effectif_m: Optional[float]
    #: Occultation due à la seule courbure, sans le relief (§9.3).
    hauteur_occultee_courbure_m: float
    fraction_visible_courbure: float
    #: Le relief, ou son absence d'évaluation.
    relief_evalue: bool
    motif_relief_non_evalue: Optional[str]
    obstacles: Tuple[Obstacle, ...]
    obstacle_le_plus_genant: Optional[Obstacle]
    #: Marge minimale de la visée au-dessus du terrain, sur tout le trajet.
    #: Négative s'il y a obstacle. None si le relief n'a pas été évalué.
    marge_minimale_m: Optional[float]
    distance_marge_minimale_m: Optional[float]

    @property
    def masque_par_le_relief(self) -> Optional[bool]:
        """None quand le relief n'a pas été évalué — jamais False par défaut."""
        if not self.relief_evalue:
            return None
        return self.obstacle_le_plus_genant is not None


def altitude_ligne_de_visee(
    distance_m: float, D: float, h: float, z_vise: float, R: float
) -> float:
    """Altitude de la ligne de visée droite, au-dessus de la surface de référence.

    Construction EXACTE, sans développement en série. L'observateur est au
    rayon R+h à l'angle 0 ; le point visé au rayon R+z_vise à l'angle θ_D=D/R.
    La visée est le SEGMENT DROIT entre les deux, dans l'espace — c'est bien
    une droite : c'est la surface qui est courbe, pas le rayon. On cherche à
    quel rayon ce segment passe au-dessus de l'angle θ = distance/R, et on en
    retire R.

    L'approximation usuelle « bombement = d(D−d)/2R » est le premier terme de
    ce calcul. Elle est excellente aux distances usuelles, mais elle est une
    approximation, et le reste de ce paquet n'en fait pas d'autres : les
    mélanger rendrait incomparables des résultats issus des deux voies.

    R est le rayon EFFECTIF quand la réfraction est prise en compte : c'est à
    l'appelant de substituer R/(1−k), comme partout ailleurs ici.
    """
    if R <= 0:
        raise ReliefError("Le rayon doit être strictement positif.")
    if D <= 0:
        raise ReliefError("La distance à la cible doit être strictement positive.")
    theta_d = D / R
    theta = distance_m / R
    if theta_d >= math.pi / 2:
        raise GeometryError(
            "Trajet hors du domaine défini (theta = D/R >= pi/2) : la "
            "construction en segment droit n'y a plus de sens."
        )

    r_a = R + h
    r_b = R + z_vise
    # Repère plan : l'observateur sur l'axe vertical, le trajet balayé vers x.
    bx = r_b * math.sin(theta_d)
    by = r_b * math.cos(theta_d)
    ax, ay = 0.0, r_a

    # Paramètre t du segment A→B au niveau angulaire θ. Voir l'en-tête : t se
    # tire de tan θ = P_x / P_y, qui est linéaire en t.
    tan_t = math.tan(theta)
    denominateur = (bx - ax) - tan_t * (by - ay)
    if abs(denominateur) < 1e-12:
        raise ReliefError(
            "Géométrie dégénérée : la ligne de visée est radiale à cette distance."
        )
    t = (tan_t * ay - ax) / denominateur
    px = ax + t * (bx - ax)
    py = ay + t * (by - ay)
    return math.hypot(px, py) - R


def altitude_ligne_de_visee_plane(distance_m: float, D: float, h: float, z_vise: float) -> float:
    """Modèle P (§4.2) : la surface est plane, la visée est une droite dessus.

    Aucune courbure, donc aucun bombement à retrancher : l'altitude de la
    visée est l'interpolation linéaire entre les deux extrémités. Le relief,
    lui, masque exactement de la même façon dans les deux modèles — c'est
    précisément ce qui permet de le distinguer de la courbure.
    """
    if D <= 0:
        raise ReliefError("La distance à la cible doit être strictement positive.")
    return h + (z_vise - h) * (distance_m / D)


def _obstacles_le_long(
    profil: ProfilTerrain,
    D: float,
    h: float,
    z_vise: float,
    R: Optional[float],
    marge_requise_m: float,
    altitude_reference_m: float,
) -> Tuple[List[Obstacle], float, float]:
    """Compare le terrain à la visée, point par point. Rend aussi la marge minimale.

    CE QUI COMPTE COMME OBSTACLE, ET POURQUOI PAS TOUT
    ──────────────────────────────────────────────────
    Un point ne devient obstacle que s'il coupe la visée ET s'élève au-dessus
    de la surface de référence. La seconde condition n'est pas un détail :
    sans elle, dès que la courbure occulte quoi que ce soit, la mer elle-même
    coupe la visée dirigée vers le sommet — et serait rapportée comme un
    « obstacle de relief ». La distinction que ce module existe pour établir
    s'effondrerait exactement dans les cas où elle sert.

    La conséquence assumée : un terrain plat AU NIVEAU de la surface de
    référence est traité comme la surface elle-même, et son masquage est
    imputé à la courbure. C'est correct — il est géométriquement
    indiscernable de la mer — mais il faut le dire, car une plaine à l'altitude
    zéro ne sera jamais nommée comme obstacle.
    """
    obstacles: List[Obstacle] = []
    marge_min = math.inf
    distance_marge_min = 0.0
    for p in profil.points:
        # Les deux extrémités sont l'observateur et la cible eux-mêmes : les
        # compter comme obstacles ferait qu'un poste posé au sol se masquerait
        # lui-même.
        if p.distance_m <= 0.0 or p.distance_m >= D:
            continue
        if R is None:
            z_visee = altitude_ligne_de_visee_plane(p.distance_m, D, h, z_vise)
        else:
            z_visee = altitude_ligne_de_visee(p.distance_m, D, h, z_vise, R)
        marge = z_visee - p.altitude_m
        if marge < marge_min:
            marge_min = marge
            distance_marge_min = p.distance_m
        if marge < marge_requise_m and p.altitude_m > altitude_reference_m:
            obstacles.append(Obstacle(
                distance_m=p.distance_m,
                altitude_terrain_m=p.altitude_m,
                altitude_visee_m=z_visee,
                manque_m=marge_requise_m - marge,
            ))
    if marge_min is math.inf:
        marge_min = math.nan
    return obstacles, marge_min, distance_marge_min


def analyser_relief(
    D: float,
    h: float,
    cible: Cible,
    R: Optional[float],
    profil: Optional[ProfilTerrain] = None,
    modele: str = "sphérique",
    marge_requise_m: float = 0.0,
    altitude_reference_m: float = 0.0,
) -> AnalyseRelief:
    """Ce que la courbure occulte, ce que le relief masque, et les deux séparément.

    R vaut None pour le modèle plan. Passer R=None avec modele='sphérique' ou
    l'inverse ne lève pas : c'est l'appelant qui nomme le modèle, et le nom
    n'entre dans aucun calcul — mais il est rendu tel quel dans le résultat,
    donc une incohérence s'y verrait.

    La visée est dirigée vers le SOMMET de la cible (z_b + H). C'est le point
    le plus favorable : si même lui est masqué par le relief, tout l'est. Le
    dire dans l'autre sens serait faux — qu'il soit visible n'implique pas que
    la base le soit.

    `marge_requise_m` permet d'exiger une garde au-dessus du terrain plutôt
    que le simple contact. Une visée qui frôle un sommet à 20 cm près, avec un
    modèle de terrain donné à ±2 m, ne conclut rien : c'est à l'appelant de
    fixer cette garde d'après l'incertitude de son profil, pas à ce module de
    la deviner.
    """
    if D <= 0:
        raise ReliefError("La distance doit être strictement positive.")
    if marge_requise_m < 0:
        raise ReliefError("La marge requise ne peut pas être négative.")

    if R is None:
        occultee = 0.0
        fraction = 1.0
    else:
        occultee = hauteur_occultee(D, h, cible, R)
        fraction = fraction_visible(D, h, cible, R)

    if profil is None:
        return AnalyseRelief(
            modele=modele,
            rayon_effectif_m=R,
            hauteur_occultee_courbure_m=occultee,
            fraction_visible_courbure=fraction,
            relief_evalue=False,
            motif_relief_non_evalue=RELIEF_NON_EVALUE,
            obstacles=(),
            obstacle_le_plus_genant=None,
            marge_minimale_m=None,
            distance_marge_minimale_m=None,
        )

    z_sommet = cible.z_b + cible.H
    obstacles, marge_min, distance_marge_min = _obstacles_le_long(
        profil, D, h, z_sommet, R, marge_requise_m, altitude_reference_m,
    )
    # Le plus gênant : celui qui manque de le plus. À manque égal, le plus
    # proche de l'observateur — c'est celui qu'on peut aller vérifier.
    pire = None
    if obstacles:
        pire = max(obstacles, key=lambda o: (o.manque_m, -o.distance_m))

    return AnalyseRelief(
        modele=modele,
        rayon_effectif_m=R,
        hauteur_occultee_courbure_m=occultee,
        fraction_visible_courbure=fraction,
        relief_evalue=True,
        motif_relief_non_evalue=None,
        obstacles=tuple(obstacles),
        obstacle_le_plus_genant=pire,
        marge_minimale_m=marge_min,
        distance_marge_minimale_m=distance_marge_min,
    )


def profil_depuis_couples(
    couples: Sequence[Tuple[float, float]], source: str, pas_m: Optional[float] = None,
    incertitude_verticale_m: Optional[float] = None,
) -> ProfilTerrain:
    """Construit un profil depuis des couples (distance, altitude), en mètres."""
    return ProfilTerrain(
        points=tuple(PointProfil(float(d), float(z)) for d, z in couples),
        source=source,
        pas_m=pas_m,
        incertitude_verticale_m=incertitude_verticale_m,
    )


# ── Le regroupement en occlusions ───────────────────────────────────────────


@dataclass(frozen=True)
class Occlusion:
    """Un RELIEF continu qui coupe la visée, et non un point de mesure isolé.

    POURQUOI CE REGROUPEMENT EXISTE
    ───────────────────────────────
    `analyser_relief` rend un obstacle PAR POINT ÉCHANTILLONNÉ dépassant la
    ligne. C'est ce qu'il faut pour calculer, et c'est inutilisable pour dire
    ce qu'on voit : au pas de 250 m, une seule colline large de six kilomètres
    produit vingt-quatre « obstacles ». Annoncer « 24 occlusions » quand il y
    a une colline serait faux dans le seul sens qui compte — celui du nombre.

    Une occlusion, ici, est un intervalle CONTIGU de points qui dépassent tous.
    Deux collines séparées par une trouée où la visée passe font deux
    occlusions ; une colline échantillonnée vingt-quatre fois en fait une.

    CE QUE LE REGROUPEMENT NE SAIT PAS
    ──────────────────────────────────
    Il ne sait pas si deux points consécutifs appartiennent au même relief :
    il ne voit que des échantillons, et une trouée plus étroite que le pas ne
    laisse aucune trace. Deux collines très voisines peuvent donc être comptées
    pour une. Le pas est rendu avec le résultat pour que cette limite se lise.
    """

    #: Distance du PREMIER point qui dépasse, depuis l'observateur.
    debut_m: float
    #: Distance du DERNIER point qui dépasse.
    fin_m: float
    #: Le point le plus gênant de l'intervalle : celui qui dépasse le plus.
    sommet: Obstacle
    #: Combien de points échantillonnés composent cette occlusion.
    nb_points: int

    @property
    def largeur_m(self) -> float:
        """L'étendue mesurée. Nulle quand un seul point dépasse.

        C'est une borne INFÉRIEURE : le relief commence avant le premier point
        qui dépasse et finit après le dernier, quelque part dans les deux
        intervalles d'échantillonnage voisins.
        """
        return self.fin_m - self.debut_m


def grouper_occlusions(obstacles: Sequence[Obstacle], pas_m: Optional[float] = None) -> Tuple[Occlusion, ...]:
    """Regroupe les points qui dépassent en reliefs contigus.

    Deux points appartiennent à la même occlusion quand rien ne les sépare :
    ni un point qui passe sous la visée, ni un trou plus large que le pas.

    `pas_m` sert à décider de la contiguïté quand les points ne sont pas
    consécutifs dans la liste — ce qui arrive dès qu'un point intermédiaire
    passe. Sans lui, la règle retombe sur l'écart observé entre les deux
    premiers points, ce qui reste juste pour un profil régulier et se dégrade
    proprement pour les autres : au pire, deux reliefs sont comptés pour un,
    jamais l'inverse.
    """
    tries = sorted(obstacles, key=lambda o: o.distance_m)
    if not tries:
        return ()

    # La tolérance de contiguïté. Un facteur 1,5 admet le pas nominal et ses
    # irrégularités, sans franchir une trouée d'un pas entier.
    ecart = pas_m
    if ecart is None and len(tries) >= 2:
        ecart = min(b.distance_m - a.distance_m for a, b in zip(tries, tries[1:]))
    tolerance = (ecart or 0.0) * 1.5

    groupes: List[List[Obstacle]] = [[tries[0]]]
    for precedent, courant in zip(tries, tries[1:]):
        if courant.distance_m - precedent.distance_m <= tolerance:
            groupes[-1].append(courant)
        else:
            groupes.append([courant])

    return tuple(
        Occlusion(
            debut_m=g[0].distance_m,
            fin_m=g[-1].distance_m,
            sommet=max(g, key=lambda o: o.manque_m),
            nb_points=len(g),
        )
        for g in groupes
    )
