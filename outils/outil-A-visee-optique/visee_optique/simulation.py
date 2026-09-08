"""
simulation.py — Ce que le simulateur de visée rend au visiteur.

CE QUE CE MODULE AJOUTE, ET CE QU'IL N'AJOUTE PAS
─────────────────────────────────────────────────
Il n'ajoute AUCUNE physique. La géodésie vient de `geodesy.py`, l'occultation
de `geometry.py`, le relief de `relief.py` — tous déjà éprouvés et épinglés.

Ce qu'il ajoute est une RÈGLE DE LECTURE : à partir de quel écart entre les
deux modèles peut-on dire qu'une visée permet de les départager, et à quel pas
échantillonner le terrain. Ce ne sont pas des lois physiques, ce sont des
conventions. Elles sont donc écrites ici en constantes nommées, affichées à
l'écran, et contestables — plutôt que cachées dans une condition au milieu d'un
composant d'interface.

CE QUI SE MESURE : LE PIED DE LA CIBLE, PAS SON SOMMET
──────────────────────────────────────────────────────
C'est le PIED de la cible qui disparaît en premier sous l'horizon, et c'est là
que les deux modèles divergent en premier. La grandeur mise en avant est donc
`c` — la hauteur masquée EN PARTANT DE LA BASE — et non la part visible du
sommet, qui reste à 100 % longtemps après que la divergence est devenue
mesurable.

`c` n'est PAS bornée à la hauteur de la cible : au-delà de la distance limite,
elle continue de croître et dit de combien la cible est passée sous l'horizon.
La borner à H perdrait cette information au moment précis où elle devient la
plus parlante — « 2 042 m de base occultés » sur une cible de 300 m dit que la
cible est enfouie sept fois sa hauteur sous l'horizon géométrique.

LE CAS QUE CE MODULE EXISTE POUR NE PAS CONFONDRE
─────────────────────────────────────────────────
Quand le relief masque la cible, les deux modèles prédisent la même chose —
rien de visible — et pour la même raison, qui n'est pas la courbure. Une visée
pareille ne départage rien, même si l'écart de courbure est énorme. Le
confondre avec une visée discriminante attribuerait à la forme de la Terre ce
qui revient à un talus.

Une colline à 500 m du poste bloque le pied de la cible dans les DEUX modèles.
Elle empêche donc d'évaluer la courbure à grande distance, et c'est cela qu'il
faut dire — pas « la cible est cachée », qui laisserait croire à une
occultation par la Terre.
"""

from dataclasses import dataclass
from typing import Optional

from .relief import AnalyseRelief

__all__ = [
    "SEUIL_DISCRIMINATION_FRACTION",
    "K_STANDARD",
    "K_ENVELOPPE_MIN",
    "K_ENVELOPPE_MAX",
    "PAS_COURT_M",
    "PAS_MOYEN_M",
    "PAS_LONG_M",
    "SEUIL_DISTANCE_MOYENNE_M",
    "SEUIL_DISTANCE_LONGUE_M",
    "MOTIF_SEUIL",
    "MOTIF_REFRACTION",
    "MOTIF_RESERVE_RELIEF",
    "Verdict",
    "juger",
    "pas_echantillonnage_m",
]

#: Le seuil critique. La courbure doit masquer au moins cette FRACTION de la
#: hauteur de la cible, EN PARTANT DE LA BASE, pour qu'on déclare la visée
#: capable de départager les deux modèles.
#:
#: 10 %, c'est-à-dire 11 m sur une cible de 110 m : une différence qu'une
#: photographie montre sans ambiguïté, et qu'aucune incertitude ordinaire sur
#: la hauteur déclarée de la cible n'efface. Convention de lecture, pas valeur
#: normative : la changer change les verdicts, et c'est pour cela qu'elle est
#: ici plutôt que dans une condition d'interface.
SEUIL_DISCRIMINATION_FRACTION = 0.10

#: La réfraction moyenne appliquée par défaut, et son enveloppe.
#:
#: 0,13 correspond à une atmosphère bien mélangée. Les bornes 0,10 et 0,40
#: encadrent ce qu'on peut rencontrer au-dessus de l'eau sans avoir mesuré le
#: profil vertical de température — et on ne l'a jamais mesuré ici. Le calcul
#: est donc conduit sur l'ENVELOPPE, pas sur la seule valeur centrale : rendre
#: un chiffre unique le ferait passer pour mieux connu qu'il ne l'est.
K_STANDARD = 0.13
K_ENVELOPPE_MIN = 0.10
K_ENVELOPPE_MAX = 0.40

#: Le pas d'échantillonnage du terrain, par tranche de distance.
#:
#: Aucune longueur de visée n'est refusée. Ce qui croît avec la distance, ce
#: n'est pas la difficulté du calcul — la géodésie et l'occultation ne coûtent
#: rien — mais le NOMBRE de points d'altitude à demander. Un pas fixe de 250 m
#: sur 2 000 km ferait 8 000 points ; le pas s'élargit donc avec la distance,
#: ce qui ramène cette visée à 1 000 points.
#:
#: L'élargissement ne PLAFONNE pas le nombre de points, il le freine : à
#: 20 000 km, la moitié du tour de la Terre, il en reste 10 000. Une visée
#: pareille n'a aucun sens physique — la cible serait des milliers de
#: kilomètres sous l'horizon — mais elle n'est pas refusée pour autant, et il
#: vaut mieux écrire ce qu'elle coûte que laisser croire à une borne qui
#: n'existe pas.
#:
#: Contrepartie assumée et affichée : sur une visée longue, une colline étroite
#: peut passer entre deux points de mesure. Un relief manqué ne se rattrape
#: pas, et c'est pourquoi le pas retenu est écrit dans le résultat.
PAS_COURT_M = 250.0
PAS_MOYEN_M = 500.0
PAS_LONG_M = 2000.0
SEUIL_DISTANCE_MOYENNE_M = 100_000.0
SEUIL_DISTANCE_LONGUE_M = 500_000.0

MOTIF_SEUIL = (
    "Une visée est dite discriminante quand DEUX conditions sont réunies : la "
    "courbure masque au moins 10 % de la hauteur de la cible en partant de sa "
    "base, même à la réfraction la plus défavorable ; et le relief intermédiaire "
    "laisse la visée entièrement dégagée. La première condition écarte les "
    "visées où les deux modèles prédisent presque la même chose ; la seconde "
    "écarte celles où c'est une colline, et non la forme de la Terre, qui "
    "décide de ce qu'on voit. Ce seuil de 10 % est une convention de lecture, "
    "pas une norme."
)

MOTIF_REFRACTION = (
    "La réfraction atmosphérique courbe les rayons lumineux et fait voir "
    "un peu plus loin que la géométrie pure. Faute de profil vertical de "
    "température mesuré sur le trajet, le calcul est conduit sur toute "
    "l'enveloppe plausible au-dessus de l'eau — de 0,10 à 0,40, valeur "
    "moyenne 0,13 — et les résultats sont rendus comme un intervalle. Un "
    "chiffre unique laisserait croire cette grandeur mieux connue qu'elle "
    "ne l'est."
)

MOTIF_RESERVE_RELIEF = (
    "Le relief intermédiaire n'a pas pu être évalué : la seconde condition de "
    "discrimination n'est donc pas vérifiée, seulement présumée. Ce n'est pas "
    "« aucun obstacle » — c'est « on ne sait pas », et un talus non vu "
    "invaliderait la visée sans rien changer à la courbure."
)


def pas_echantillonnage_m(distance_m: float) -> float:
    """Le pas d'échantillonnage du terrain, choisi d'après la distance.

    Aucune distance n'est refusée : cette fonction ne borne rien, elle règle
    seulement la finesse du relevé pour que le nombre de points reste tenable.
    """
    if distance_m <= 0:
        raise ValueError("La distance doit être strictement positive.")
    if distance_m < SEUIL_DISTANCE_MOYENNE_M:
        return PAS_COURT_M
    if distance_m < SEUIL_DISTANCE_LONGUE_M:
        return PAS_MOYEN_M
    return PAS_LONG_M


@dataclass(frozen=True)
class Verdict:
    """Ce que la configuration permet de conclure, avant toute observation."""

    discriminante: bool
    #: Le motif, en une phrase lisible par quelqu'un qui n'a lu aucun protocole.
    motif: str
    #: La hauteur masquée EN PARTANT DE LA BASE, aux deux bornes de réfraction.
    #: Non bornée à H : au-delà de la distance limite elle continue de croître,
    #: et dit de combien la cible est passée sous l'horizon.
    hauteur_masquee_base_min_m: float
    hauteur_masquee_base_max_m: float
    #: La même chose en fraction de la hauteur de la cible. Peut dépasser 1.
    fraction_masquee_base_min: float
    fraction_masquee_base_max: float
    #: Vrai quand le relief masque la cible dans les deux modèles ; None quand
    #: le relief n'a pas été évalué — jamais False par défaut.
    masque_par_le_relief: Optional[bool]
    #: Où se trouve l'obstacle qui bloque, quand il y en a un.
    distance_obstacle_m: Optional[float]
    #: Vrai quand le verdict porte sur la courbure seule, faute d'avoir pu
    #: vérifier la seconde condition.
    reserve_relief: bool
    seuil_applique: float = SEUIL_DISCRIMINATION_FRACTION


def juger(
    globe_min: AnalyseRelief,
    globe_max: AnalyseRelief,
    hauteur_cible_m: float,
) -> Verdict:
    """Le verdict, à partir des deux bornes de l'enveloppe de réfraction.

    `globe_min` et `globe_max` sont l'analyse du modèle sphérique aux deux
    bornes de k. Peu importe laquelle masque le plus : le module les trie, parce
    que l'ordre dépend du signe d'une dérivée que l'appelant n'a pas à connaître.
    """
    if hauteur_cible_m <= 0:
        raise ValueError("La hauteur de la cible doit être strictement positive.")

    masquees = sorted((
        globe_min.hauteur_occultee_courbure_m,
        globe_max.hauteur_occultee_courbure_m,
    ))
    bas, haut = masquees[0], masquees[1]
    fraction_bas = bas / hauteur_cible_m
    fraction_haut = haut / hauteur_cible_m

    masque = globe_min.masque_par_le_relief
    obstacle = globe_min.obstacle_le_plus_genant
    distance_obstacle = obstacle.distance_m if obstacle is not None else None

    commun = dict(
        hauteur_masquee_base_min_m=bas,
        hauteur_masquee_base_max_m=haut,
        fraction_masquee_base_min=fraction_bas,
        fraction_masquee_base_max=fraction_haut,
        masque_par_le_relief=masque,
        distance_obstacle_m=distance_obstacle,
    )

    # Le relief d'abord : quand il bloque, la question de la courbure ne se
    # pose plus. Les deux modèles prédisent la même chose, pour la même raison,
    # et cette raison n'est pas la forme de la Terre.
    if masque:
        ou = ("à %s km" % _km(distance_obstacle)) if distance_obstacle is not None else "sur le trajet"
        return Verdict(
            discriminante=False,
            motif=(
                "La cible est bloquée à la base par le relief local (%s) dans "
                "les deux modèles, ce qui empêche d'évaluer la courbure à grande "
                "distance. Ce n'est pas la forme de la Terre qui décide ici, "
                "c'est un obstacle du terrain — et il masque identiquement quel "
                "que soit le modèle." % ou
            ),
            reserve_relief=False,
            **commun,
        )

    if fraction_bas < SEUIL_DISCRIMINATION_FRACTION:
        return Verdict(
            discriminante=False,
            motif=(
                "À la réfraction la plus favorable, la courbure ne masque que "
                "%s m à la base de la cible, soit %s %% de sa hauteur — sous le "
                "seuil de %s %%. Les deux modèles prédisent presque la même "
                "chose. Il faut viser plus loin, ou plus bas, ou une cible plus "
                "courte." % (
                    _m(bas), _pc(fraction_bas),
                    _pc(SEUIL_DISCRIMINATION_FRACTION),
                )
            ),
            reserve_relief=False,
            **commun,
        )

    reserve = masque is None
    detail = (
        "Sur le modèle sphérique, la courbure masque de %s à %s m à la base de "
        "la cible ; sur le modèle plat, rien n'est masqué. " % (_m(bas), _m(haut))
    )
    if reserve:
        detail += (
            "Le relief intermédiaire n'a pas pu être vérifié : la seconde "
            "condition est présumée, pas établie."
        )
    else:
        detail += (
            "Le relief intermédiaire laisse la visée entièrement dégagée : "
            "l'écart observable revient bien à la courbure."
        )
    return Verdict(
        discriminante=True,
        motif=detail,
        reserve_relief=reserve,
        **commun,
    )


def _m(x: float) -> str:
    """Une longueur en mètres, à la décimale, virgule française."""
    return ("%.1f" % x).replace(".", ",")


def _km(x: float) -> str:
    return ("%.2f" % (x / 1000.0)).replace(".", ",")


def _pc(fraction: float) -> str:
    return ("%.1f" % (100.0 * fraction)).replace(".", ",")
