"""
simulation.py — Ce que le simulateur de visée rend au visiteur.

CE QUE CE MODULE AJOUTE, ET CE QU'IL N'AJOUTE PAS
─────────────────────────────────────────────────
Il n'ajoute AUCUNE physique. La géodésie vient de `geodesy.py`, l'occultation
de `geometry.py`, le relief de `relief.py` — tous déjà éprouvés et épinglés.

Ce qu'il ajoute est une RÈGLE DE LECTURE : à partir de quel écart entre les
deux modèles peut-on dire qu'une visée permet de les départager. Cette règle
n'est pas une loi physique, c'est une convention. Elle est donc écrite ici en
une constante nommée, affichée à l'écran, et contestable — plutôt que cachée
dans une condition au milieu d'un composant d'interface.

POURQUOI UN SEUIL, ET POURQUOI CELUI-LÀ
───────────────────────────────────────
Sans seuil, une visée où la courbure cache trois centimètres serait déclarée
« discriminante », ce qu'aucune photographie ne pourrait vérifier. Avec un
seuil en mètres absolus, la même règle serait sévère sur un phare de 10 m et
laxiste sur une falaise de 300 m.

Le seuil retenu est donc RELATIF à la hauteur de la cible : le modèle sphérique
doit en cacher au moins 1 %. Sur une cible de 110 m cela fait 1,1 m, une
différence qu'une photographie ordinaire montre. C'est un plancher de
lisibilité choisi ici, pas une valeur issue d'une norme, et il est nommé pour
qu'on puisse le discuter sans relire le code.

LE CAS QUE CE MODULE EXISTE POUR NE PAS CONFONDRE
─────────────────────────────────────────────────
Quand le relief masque la cible, les deux modèles prédisent la même chose —
rien de visible — et pour la même raison, qui n'est pas la courbure. Une visée
pareille ne départage rien, même si l'écart de courbure est énorme. Le confondre
avec une visée discriminante attribuerait à la forme de la Terre ce qui revient
à un talus.
"""

from dataclasses import dataclass
from typing import Optional, Tuple

from .relief import AnalyseRelief

__all__ = [
    "SEUIL_DISCRIMINATION_FRACTION",
    "K_STANDARD",
    "K_ENVELOPPE_MIN",
    "K_ENVELOPPE_MAX",
    "MOTIF_SEUIL",
    "MOTIF_REFRACTION",
    "Verdict",
    "juger",
]

#: Le plancher de lisibilité. Le modèle sphérique doit cacher au moins cette
#: FRACTION de la hauteur de la cible pour qu'on déclare la visée capable de
#: départager les deux modèles.
#:
#: 1 %, c'est-à-dire 1,1 m sur une cible de 110 m. Convention de lecture, pas
#: valeur normative : la changer change les verdicts, et c'est pour cela
#: qu'elle est ici plutôt que dans une condition d'interface.
SEUIL_DISCRIMINATION_FRACTION = 0.01

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

MOTIF_SEUIL = (
    "Une visée est dite discriminante quand, même à la réfraction la plus "
    "défavorable, le modèle sphérique cache au moins 1 % de la hauteur de la "
    "cible. Ce plancher est une convention de lecture, pas une norme : sous "
    "1 %, l'écart entre les deux modèles devient trop petit pour qu'une "
    "photographie ordinaire le montre, et annoncer « discriminante » "
    "promettrait une mesure que personne ne pourrait faire."
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


@dataclass(frozen=True)
class Verdict:
    """Ce que la configuration permet de conclure, avant toute observation."""

    discriminante: bool
    #: Le motif, en une phrase lisible par quelqu'un qui n'a lu aucun protocole.
    motif: str
    #: La part de la cible que la courbure cache, au bord le plus favorable au
    #: modèle plan (donc le plus défavorable à la discrimination).
    fraction_cachee_min: float
    fraction_cachee_max: float
    hauteur_cachee_min_m: float
    hauteur_cachee_max_m: float
    #: Vrai quand le relief masque la cible dans les deux modèles : ce n'est
    #: alors plus la courbure qui décide, et rien ne se départage.
    masque_par_le_relief: Optional[bool]
    seuil_applique: float = SEUIL_DISCRIMINATION_FRACTION


def juger(
    globe_min: AnalyseRelief,
    globe_max: AnalyseRelief,
    hauteur_cible_m: float,
) -> Verdict:
    """Le verdict, à partir des deux bornes de l'enveloppe de réfraction.

    `globe_min` et `globe_max` sont l'analyse du modèle sphérique aux deux
    bornes de k. Peu importe laquelle cache le plus : le module les trie, parce
    que l'ordre dépend du signe d'une dérivée que l'appelant n'a pas à connaître.
    """
    if hauteur_cible_m <= 0:
        raise ValueError("La hauteur de la cible doit être strictement positive.")

    cachees = sorted((
        1.0 - globe_min.fraction_visible_courbure,
        1.0 - globe_max.fraction_visible_courbure,
    ))
    cachee_min, cachee_max = cachees[0], cachees[1]

    # Le relief d'abord : quand il masque, la question de la courbure ne se
    # pose plus. Les deux modèles prédisent la même chose, pour la même raison,
    # et cette raison n'est pas la forme de la Terre.
    masque = globe_min.masque_par_le_relief
    if masque:
        return Verdict(
            discriminante=False,
            motif=(
                "Le relief coupe la visée : les deux modèles prédisent une cible "
                "cachée, pour la même raison, qui n'est pas la courbure. Cette "
                "visée ne permet de départager ni l'un ni l'autre."
            ),
            fraction_cachee_min=cachee_min,
            fraction_cachee_max=cachee_max,
            hauteur_cachee_min_m=cachee_min * hauteur_cible_m,
            hauteur_cachee_max_m=cachee_max * hauteur_cible_m,
            masque_par_le_relief=True,
        )

    if cachee_min >= SEUIL_DISCRIMINATION_FRACTION:
        return Verdict(
            discriminante=True,
            motif=(
                "Les deux modèles prédisent des choses différentes, et l'écart "
                "reste visible sur toute l'enveloppe de réfraction. Une "
                "photographie de cette cible depuis ce point peut les départager."
            ),
            fraction_cachee_min=cachee_min,
            fraction_cachee_max=cachee_max,
            hauteur_cachee_min_m=cachee_min * hauteur_cible_m,
            hauteur_cachee_max_m=cachee_max * hauteur_cible_m,
            masque_par_le_relief=masque,
        )

    return Verdict(
        discriminante=False,
        motif=(
            "À la réfraction la plus favorable, le modèle sphérique ne cache "
            "presque rien : les deux modèles prédisent la même chose, à trop peu "
            "près pour qu'une photographie les sépare. Il faut viser plus loin, "
            "ou plus bas, ou une cible plus courte."
        ),
        fraction_cachee_min=cachee_min,
        fraction_cachee_max=cachee_max,
        hauteur_cachee_min_m=cachee_min * hauteur_cible_m,
        hauteur_cachee_max_m=cachee_max * hauteur_cible_m,
        masque_par_le_relief=masque,
    )
