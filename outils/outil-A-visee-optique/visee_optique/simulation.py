"""
simulation.py — Ce que le simulateur de visée rend au visiteur.

GÉOMÉTRIE PURE : PLUS AUCUN MODÈLE DE TERRAIN
─────────────────────────────────────────────
Le simulateur ne consulte plus de profil altimétrique et ne détecte plus
d'obstacle local. Le calcul porte exclusivement sur la ligne de visée théorique
entre les deux altitudes saisies.

Ce n'est pas un renoncement, c'est un partage des rôles : chercher ce qui
bouche la vue depuis un poste donné relève du contrôle de l'analyste SUR
L'IMAGE RÉELLE — une haie, un cargo, un bâtiment récent ne figurent dans aucun
modèle numérique de terrain. Un simulateur qui prétendrait trancher cette
question donnerait une fausse assurance ; il vaut mieux qu'il dise ce que la
géométrie implique, et rien de plus.

CE QUE CE MODULE AJOUTE, ET CE QU'IL N'AJOUTE PAS
─────────────────────────────────────────────────
Il n'ajoute AUCUNE physique. La géodésie vient de `geodesy.py`, l'occultation
de `geometry.py` — tous deux déjà éprouvés et épinglés.

Ce qu'il ajoute est une RÈGLE DE LECTURE : à partir de quel écart entre les
deux modèles peut-on dire qu'une visée permet de les départager. Ce n'est pas
une loi physique, c'est une convention. Elle est donc écrite ici en constante
nommée, affichée à l'écran, et contestable — plutôt que cachée dans une
condition au milieu d'un composant d'interface.

CE QUI SE MESURE : LE PIED DE LA CIBLE, PAS SON SOMMET
──────────────────────────────────────────────────────
C'est le PIED de la cible qui disparaît en premier sous l'horizon, et c'est là
que les deux modèles divergent en premier. La grandeur jugée est donc `c` — la
hauteur masquée EN PARTANT DE LA BASE — et non la part visible du sommet, qui
reste à 100 % longtemps après que la divergence est devenue mesurable.

`c` n'est PAS bornée à la hauteur de la cible : au-delà de la distance limite,
elle continue de croître et dit de combien la cible est passée sous l'horizon.
La borner à H perdrait cette information au moment précis où elle devient la
plus parlante — « 2 042 m de base occultés » sur une cible de 300 m dit que la
cible est enfouie sept fois sa hauteur sous l'horizon géométrique.

LE MODÈLE PLAT N'A PAS DE PARAMÈTRE
────────────────────────────────────
Il masque 0 m à la base, à toute distance, par construction. Ce n'est pas une
approximation ni un cas particulier : c'est ce que le modèle dit. L'écart entre
les deux prédictions est donc exactement `c`, ce qui rend la comparaison
directe et le seuil facile à énoncer.
"""

from dataclasses import dataclass

__all__ = [
    "SEUIL_DISCRIMINATION_FRACTION",
    "K_STANDARD",
    "K_ENVELOPPE_MIN",
    "K_ENVELOPPE_MAX",
    "MASQUE_MODELE_PLAT_M",
    "MOTIF_SEUIL",
    "MOTIF_REFRACTION",
    "MOTIF_SANS_RELIEF",
    "Verdict",
    "juger",
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

#: La réfraction appliquée. `K_STANDARD` est la valeur moyenne qui sert au
#: calcul principal et au verdict ; les deux bornes encadrent ce qu'on peut
#: rencontrer au-dessus de l'eau sans avoir mesuré le profil vertical de
#: température, et servent à AFFICHER l'écart que cette ignorance laisse.
#:
#: Le verdict est rendu sur la valeur moyenne, pas sur l'enveloppe : une règle
#: qui exigerait le seuil aux deux bornes serait plus sévère que ce qui est
#: annoncé à l'écran, et l'écart entre les deux se paierait en surprises.
K_STANDARD = 0.13
K_ENVELOPPE_MIN = 0.10
K_ENVELOPPE_MAX = 0.40

#: Ce que le modèle plat masque à la base : rien, à toute distance. Nommé
#: plutôt qu'écrit en dur, pour que la comparaison se lise comme une
#: soustraction entre deux prédictions et non comme un cas particulier.
MASQUE_MODELE_PLAT_M = 0.0

MOTIF_SEUIL = (
    "Une visée est dite discriminante quand la courbure masque au moins 10 % "
    "de la hauteur de la cible en partant de sa base. Sous ce seuil, les deux "
    "modèles prédisent des choses trop proches pour qu'une photographie les "
    "sépare, et annoncer « discriminante » promettrait une mesure que personne "
    "ne pourrait faire. Ce seuil est une convention de lecture, pas une norme."
)

MOTIF_REFRACTION = (
    "La réfraction atmosphérique courbe les rayons lumineux et fait voir "
    "un peu plus loin que la géométrie pure. Le calcul principal emploie le "
    "gradient moyen k = 0,13, celui d'une atmosphère bien mélangée. Faute de "
    "profil vertical de température mesuré sur le trajet, l'écart que cette "
    "ignorance laisse est affiché à part, entre k = 0,10 et k = 0,40."
)

MOTIF_SANS_RELIEF = (
    "Ce simulateur ne consulte aucun modèle de terrain : il calcule la ligne "
    "de visée théorique entre les deux altitudes saisies, et rien d'autre. Ce "
    "qui bouche réellement la vue depuis un poste — une haie, un cargo, un "
    "bâtiment récent — ne figure dans aucun modèle numérique et se constate "
    "sur l'image. C'est le contrôle de l'analyste, pas celui du simulateur."
)


@dataclass(frozen=True)
class Verdict:
    """Ce que la géométrie permet de conclure, avant toute observation."""

    discriminante: bool
    #: Le motif, en une phrase lisible par quelqu'un qui n'a lu aucun protocole.
    motif: str
    #: La hauteur masquée EN PARTANT DE LA BASE sur le modèle sphérique. Non
    #: bornée à H : au-delà de la distance limite elle continue de croître, et
    #: dit de combien la cible est passée sous l'horizon.
    hauteur_masquee_base_m: float
    #: La même chose en fraction de la hauteur de la cible. Peut dépasser 1.
    fraction_masquee_base: float
    #: Ce que le modèle plat masque : rien, à toute distance.
    hauteur_masquee_plat_m: float
    #: L'écart entre les deux prédictions. C'est ce qu'une photographie doit
    #: pouvoir montrer, et c'est exactement `hauteur_masquee_base_m` puisque le
    #: modèle plat ne masque rien.
    ecart_entre_modeles_m: float
    seuil_applique: float = SEUIL_DISCRIMINATION_FRACTION


def juger(hauteur_masquee_base_m: float, hauteur_cible_m: float) -> Verdict:
    """Le verdict, sur la seule occultation à la base.

    `hauteur_masquee_base_m` est `c` calculé au gradient moyen K_STANDARD.
    """
    if hauteur_cible_m <= 0:
        raise ValueError("La hauteur de la cible doit être strictement positive.")
    if hauteur_masquee_base_m < 0:
        raise ValueError("La hauteur masquée ne peut pas être négative.")

    fraction = hauteur_masquee_base_m / hauteur_cible_m
    # L'écart s'écrit comme la SOUSTRACTION des deux prédictions, parce que
    # c'est ce qu'il est. Arithmétiquement, c'est aujourd'hui une identité :
    # le modèle plat masque zéro, donc l'écart vaut l'occultation sphérique.
    # Aucun test ne peut donc distinguer cette ligne de `= hauteur_masquee`,
    # et c'est écrit ici pour que personne ne la prenne pour un garde-fou —
    # ni ne la « simplifie » en croyant corriger un doublon.
    ecart = hauteur_masquee_base_m - MASQUE_MODELE_PLAT_M

    if fraction >= SEUIL_DISCRIMINATION_FRACTION:
        motif = (
            "Le modèle sphérique masque %s m à la base de la cible ; le modèle "
            "plat n'en masque aucun. L'écart entre les deux prédictions est de "
            "%s m, soit %s %% de la hauteur de la cible — assez pour qu'une "
            "photographie les départage." % (
                _m(hauteur_masquee_base_m), _m(ecart), _pc(fraction),
            )
        )
        return Verdict(
            discriminante=True, motif=motif,
            hauteur_masquee_base_m=hauteur_masquee_base_m,
            fraction_masquee_base=fraction,
            hauteur_masquee_plat_m=MASQUE_MODELE_PLAT_M,
            ecart_entre_modeles_m=ecart,
        )

    motif = (
        "Le modèle sphérique ne masque que %s m à la base de la cible, soit "
        "%s %% de sa hauteur — sous le seuil de %s %%. Les deux modèles "
        "prédisent presque la même chose : il faut viser plus loin, ou plus "
        "bas, ou une cible plus courte." % (
            _m(hauteur_masquee_base_m), _pc(fraction),
            _pc(SEUIL_DISCRIMINATION_FRACTION),
        )
    )
    return Verdict(
        discriminante=False, motif=motif,
        hauteur_masquee_base_m=hauteur_masquee_base_m,
        fraction_masquee_base=fraction,
        hauteur_masquee_plat_m=MASQUE_MODELE_PLAT_M,
        ecart_entre_modeles_m=ecart,
    )


def _m(x: float) -> str:
    """Une longueur en mètres, à la décimale, virgule française."""
    return ("%.1f" % x).replace(".", ",")


def _pc(fraction: float) -> str:
    return ("%.1f" % (100.0 * fraction)).replace(".", ",")
