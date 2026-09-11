"""
fiche_terrain.py — La fiche que le volontaire emporte sur place.

CE QU'ELLE EST
──────────────
Une page, dérivée d'une simulation déjà faite, qui dit trois choses et pas
plus : ce sur quoi la simulation a tourné, ce qu'il faut mesurer sur place
pour que la sortie serve à quelque chose, et comment cadrer.

Elle est écrite pour quelqu'un qui n'a lu aucun protocole et qui a les mains
froides. D'où deux règles de rédaction tenues partout :

  · CHAQUE champ demandé porte, en une phrase, POURQUOI il est demandé. Un
    formulaire dont on ne comprend pas l'utilité est rempli au hasard ou pas
    du tout, et une valeur remplie au hasard est pire qu'une case vide.
  · AUCUN champ n'est demandé « pour la forme ». Ce qui n'entre ni dans le
    calcul, ni dans la possibilité de le refaire, ni dans la possibilité de le
    contester, n'est pas sur la fiche. La liste de ce qui a été ÉCARTÉ est
    rendue elle aussi, pour qu'on puisse discuter l'omission.

LA PRÉDICTION EST EN BAS, ET SÉPARÉE
────────────────────────────────────
Le protocole exige une analyse en aveugle. Une fiche qui afficherait en tête
« la courbure doit masquer 40 m » ferait mesurer 40 m : l'œil trouve ce qu'on
lui a annoncé, sans mauvaise foi, et le résultat ne vaudrait plus rien.

La prédiction est donc rassemblée dans un DERNIER bloc, marqué comme à ne pas
lire avant la prise de vue. Ce n'est pas une précaution symbolique : c'est la
seule raison pour laquelle la fiche a deux parties au lieu d'une.

Et ce bloc dit ce qu'il ne prouve pas. L'horodatage qu'il porte est celui de
la machine qui a généré la fiche ; il n'atteste aucune antériorité vis-à-vis
d'un tiers. Le faire croire serait exactement le défaut que le préenregistrement
existe pour empêcher.

LE MILIEU NE CHANGE AUCUN CALCUL
────────────────────────────────
Lac, mer ou terre : la géométrie est la même, et la fiche le dit. Ce que le
milieu change est réel mais ailleurs — le NIVEAU DE RÉFÉRENCE auquel les
hauteurs sont comptées, les grandeurs qui le font bouger (la marée), et ce que
l'observation pourra établir. Une visée terrestre est structurellement plus
faible, parce que le sol intermédiaire n'est pas une surface de référence et
que cet outil ne modélise aucun relief. C'est écrit sur la fiche plutôt que
laissé à deviner.

AUCUNE HORLOGE, AUCUN ALÉA
──────────────────────────
`construire_fiche` reçoit son horodatage en paramètre et ne lit jamais
l'heure. Un module qui consulte la sienne n'est pas reproductible, ne peut pas
être épinglé par des vecteurs d'or, et son port dériverait sans que rien ne le
signale.
"""

from dataclasses import dataclass, field
from math import ceil, pi
from typing import List, Optional, Tuple

from .simulation import (
    K_ENVELOPPE_MAX,
    K_ENVELOPPE_MIN,
    K_STANDARD,
    Verdict,
    format_k,
    format_metres,
    format_pourcent,
)

__all__ = [
    "MILIEUX",
    "PIXELS_MIN_ECART",
    "LARGEUR_TXT",
    "MOTIF_MILIEU_SANS_EFFET",
    "MOTIF_AVEUGLE",
    "MOTIF_HORODATAGE",
    "CHAMPS_ECARTES",
    "FicheError",
    "Champ",
    "Section",
    "FicheTerrain",
    "construire_fiche",
    "rendre_txt",
    "nom_fichier",
]


class FicheError(ValueError):
    """Paramètre de fiche hors du domaine couvert."""


#: Les trois milieux, avec ce que chacun change RÉELLEMENT.
#:
#: La clé est l'identifiant employé par l'interface ; la valeur donne le nom
#: affiché, le nom du niveau de référence auquel les hauteurs sont comptées, et
#: la réserve propre au milieu. Ce dernier texte n'est pas décoratif : il dit
#: ce que le milieu retire ou ajoute à ce que l'observation pourra établir.
MILIEUX = {
    "lac": {
        "nom": "Lac",
        "reference": "niveau de l'eau du lac",
        "reserve": (
            "Un lac est le meilleur cas : sa surface est un plan d'eau au "
            "repos, donc une surface de référence sans relief, et son étendue "
            "limitée réduit les écarts de température le long du trajet. Ce "
            "qui reste à surveiller est l'air juste au-dessus de l'eau, où la "
            "réfraction s'écarte le plus de la moyenne employée par le "
            "calcul — d'où les deux températures demandées."
        ),
    },
    "mer": {
        "nom": "Mer",
        "reference": "niveau de la mer à l'heure de la prise de vue",
        "reserve": (
            "La mer est une surface de référence sans relief, mais son niveau "
            "BOUGE : la marée le déplace de plusieurs mètres en quelques "
            "heures. Une hauteur d'objectif relevée sans l'heure ne veut donc "
            "rien dire, et c'est la raison pour laquelle l'heure et la marée "
            "sont demandées ensemble."
        ),
    },
    "terre": {
        "nom": "Terre",
        "reserve": (
            "Une visée terrestre est structurellement plus faible, et il faut "
            "le savoir avant de partir. Le sol entre les deux points n'est pas "
            "une surface de référence : il monte et il descend, et ce "
            "simulateur ne modélise AUCUN relief. Une base masquée peut l'être "
            "par un pli de terrain plutôt que par la courbure, et l'image "
            "seule ne les distingue pas. Une conclusion demande donc, en plus, "
            "de montrer que la ligne de visée passe au-dessus de tout le "
            "terrain intermédiaire — un profil altimétrique que cet outil ne "
            "fournit pas."
        ),
        "reference": "niveau du sol au poste d'observation",
    },
}

#: Le nom du niveau de référence est stocké SANS article, et les phrases le
#: reprennent en « le / du / au ». Toutes les valeurs commencent par « niveau »,
#: un masculin à consonne, ce qui rend ces trois contractions correctes sans
#: qu'aucune règle de grammaire soit devinée. Un test le vérifie : ajouter un
#: milieu dont la référence commencerait par « la » ou par une voyelle
#: produirait « au eau » ou « du la surface », et il vaut mieux que ce soit un
#: échec de test qu'une faute sur une fiche imprimée.
PREFIXE_REFERENCE_ATTENDU = "niveau "

#: Combien de pixels l'écart entre les deux modèles doit occuper sur l'image
#: pour être MESURÉ et non estimé à l'œil.
#:
#: Vingt pixels, c'est-à-dire de quoi placer le bord de la cible à un ou deux
#: pixels près sur une transition qui n'est jamais franche. Convention, comme
#: le seuil de discrimination : elle est nommée ici pour qu'on puisse la
#: contester, et elle sert à calculer la seule exigence de cadrage que la
#: fiche donne en chiffres.
PIXELS_MIN_ECART = 20

#: La largeur du rendu texte. 72 colonnes tiennent dans un terminal, dans un
#: courriel et sur une feuille A4 en corps 11 sans réglage.
LARGEUR_TXT = 72

MOTIF_MILIEU_SANS_EFFET = (
    "Le milieu ne change AUCUN chiffre de la simulation : la géométrie est la "
    "même sur un lac, en mer et sur terre. Il change le niveau auquel les "
    "hauteurs sont comptées, les grandeurs qui font bouger ce niveau, et ce "
    "que l'observation pourra établir."
)

MOTIF_AVEUGLE = (
    "À ne pas lire avant la prise de vue. Une mesure faite en connaissant la "
    "valeur attendue la retrouve, sans mauvaise foi de personne : l'œil place "
    "le bord là où on lui a dit de le chercher. Mesurez d'abord, comparez "
    "ensuite."
)

MOTIF_HORODATAGE = (
    "Cet horodatage est celui de la machine qui a produit la fiche. Il "
    "n'atteste aucune antériorité devant un tiers, et le présenter comme une "
    "preuve de dépôt serait exactement le défaut que le préenregistrement "
    "existe pour empêcher. Pour une antériorité opposable, il faut déposer "
    "l'empreinte du fichier auprès d'un service d'horodatage — c'est la "
    "procédure du protocole complet, pas celle de cette fiche."
)

#: Ce que la fiche NE demande PAS, et pourquoi.
#:
#: Rendu au même titre que le reste : une omission qu'on ne peut pas lire ne
#: peut pas être contestée, et la tentation d'ajouter des champs « au cas où »
#: est exactement ce qui rend un protocole inutilisable sur le terrain.
CHAMPS_ECARTES = (
    (
        "Pression atmosphérique",
        "Elle entre dans le coefficient de réfraction, mais très loin derrière "
        "le gradient vertical de température : à pression réaliste, sa "
        "contribution est du second ordre. Notez-la si vous avez un baromètre, "
        "ne faites pas un détour pour elle.",
    ),
    (
        "Focale, ouverture, heure exacte du déclenchement",
        "Le fichier de l'appareil les porte déjà. Les recopier à la main "
        "ajoute une occasion de se tromper sans ajouter d'information — il "
        "suffit de conserver le fichier d'origine.",
    ),
    (
        "Humidité, visibilité annoncée, force du vent",
        "Elles expliquent qu'une image soit belle ou ratée, pas où se trouve "
        "le bord de la cible. Ce qui décide de la recevabilité d'une image se "
        "constate sur l'image.",
    ),
    (
        "Un jugement sur ce que vous voyez",
        "« On voit la base » ou « on ne la voit pas » est précisément la "
        "question que le protocole remplace par une mesure. La fiche ne "
        "demande donc aucune appréciation, seulement des grandeurs.",
    ),
)


@dataclass(frozen=True)
class Champ:
    """Une grandeur à consigner sur place."""

    libelle: str
    #: L'unité attendue, ou None quand la réponse n'est pas un nombre.
    unite: Optional[str]
    #: Pourquoi ce champ est demandé. UNE phrase — la fiche est lue debout.
    pourquoi: str
    #: Faux pour ce qui est utile mais dont l'absence ne perd pas la sortie.
    obligatoire: bool = True


@dataclass(frozen=True)
class Section:
    """Un bloc de la fiche."""

    numero: str
    titre: str
    #: Les valeurs déjà connues, reprises de la simulation. (clé, valeur)
    releves: Tuple[Tuple[str, str], ...] = ()
    #: Les grandeurs à consigner sur place.
    champs: Tuple[Champ, ...] = ()
    #: Les consignes, numérotées à l'affichage.
    consignes: Tuple[str, ...] = ()
    #: Les réserves du bloc, rendues à part et jamais fondues dans la prose.
    reserves: Tuple[str, ...] = ()
    #: Vrai pour le bloc de dépôt, qui ne se lit qu'après la prise de vue.
    sous_scelle: bool = False


@dataclass
class FicheTerrain:
    """La fiche complète, prête à rendre en texte ou en HTML."""

    milieu: str
    milieu_nom: str
    reference_verticale: str
    titre: str
    sous_titre: str
    horodatage: str
    discriminante: bool
    sections: List[Section] = field(default_factory=list)
    champs_ecartes: Tuple[Tuple[str, str], ...] = CHAMPS_ECARTES


# ── Les formateurs propres à la fiche ───────────────────────────────────────
#
# Les grandeurs partagées avec l'écran passent par les formateurs PUBLICS de
# `simulation` : deux implémentations d'un même chiffre finiraient par en
# rendre deux valeurs différentes, et c'est arrivé ailleurs dans ce dépôt.


def _km(m: float) -> str:
    return ("%.2f" % (m / 1000.0)).replace(".", ",")


def _deg(x: float) -> str:
    return ("%.1f" % x).replace(".", ",")


def _coord(latitude: float, longitude: float) -> str:
    return ("%.5f, %.5f" % (latitude, longitude)).replace(".", ",")


def _point(latitude: float, longitude: float, libelle: Optional[str]) -> str:
    """Un point, avec son libellé quand il y en a un.

    Les coordonnées sont TOUJOURS écrites, même quand un libellé existe : sur
    le terrain, c'est le chiffre qu'on entre dans le GPS, et un nom de lieu ne
    se saisit pas dans un appareil.
    """
    brut = _coord(latitude, longitude)
    return "%s (%s)" % (libelle, brut) if libelle else brut


def _arcmin(ecart_m: float, distance_m: float) -> str:
    """La taille angulaire de l'écart, en minutes d'arc.

    C'est la grandeur qui dit si l'écart est photographiable : deux modèles qui
    diffèrent de 40 m à 35 km diffèrent de près de 4 minutes d'arc, ce qu'un
    téléobjectif montre sans peine ; les mêmes 40 m à 3 000 km ne feraient plus
    rien de mesurable.
    """
    if distance_m <= 0:
        raise FicheError("La distance doit être strictement positive.")
    return ("%.2f" % (ecart_m / distance_m * 10800.0 / pi)).replace(".", ",")


def _hauteur_apparente_min_px(seuil: float) -> Optional[int]:
    """Combien de pixels de haut la cible doit occuper sur l'image.

    LE CALCUL PART DU SEUIL, PAS DU RÉSULTAT — et c'est tout le point.
    Une première version divisait PIXELS_MIN_ECART par la fraction RÉELLEMENT
    masquée. Le nombre obtenu était juste, et il annonçait au volontaire la
    grandeur même qu'il doit mesurer : à 20 pixels d'écart pour 55 pixels de
    cible, la fraction se retrouve en une division. Le bloc sous scellé
    n'aurait plus rien scellé.

    Le seuil, lui, ne dépend pas du résultat. Et il suffit : une visée
    discriminante masque par définition au moins `seuil` de la hauteur, donc
    exige MOINS de pixels que ce que le seuil demande. Viser le nombre issu du
    seuil met donc à l'abri dans tous les cas retenus, sans rien révéler.

    None quand le seuil n'est pas strictement positif — il n'y aurait alors
    aucune exigence à formuler.
    """
    if seuil <= 0:
        return None
    return int(ceil(PIXELS_MIN_ECART / seuil))


def construire_fiche(
    *,
    milieu: str,
    horodatage: str,
    obs_latitude: float,
    obs_longitude: float,
    obs_libelle: Optional[str],
    cible_latitude: float,
    cible_longitude: float,
    cible_libelle: Optional[str],
    distance_m: float,
    azimut_deg: float,
    hauteur_observateur_m: float,
    hauteur_cible_m: float,
    masquee_enveloppe_min_m: float,
    masquee_enveloppe_max_m: float,
    k_employe: float,
    k_personnalise: bool,
    verdict: Verdict,
) -> FicheTerrain:
    """Construit la fiche à partir d'une simulation déjà faite.

    `horodatage` est FOURNI, jamais lu sur l'horloge de la machine : sans cela
    le module ne serait pas reproductible et ses vecteurs d'or n'épingleraient
    rien.
    """
    if milieu not in MILIEUX:
        raise FicheError(
            "Milieu inconnu : %r. Les milieux couverts sont %s."
            % (milieu, ", ".join(sorted(MILIEUX)))
        )
    if distance_m <= 0:
        raise FicheError("La distance doit être strictement positive.")
    if hauteur_cible_m <= 0:
        raise FicheError("La hauteur de la cible doit être strictement positive.")
    if hauteur_observateur_m < 0:
        raise FicheError("La hauteur de l'observateur ne peut pas être négative.")
    if not horodatage.strip():
        raise FicheError(
            "L'horodatage manque : sans lui, le bloc de dépôt ne dit pas à "
            "quel moment la prédiction a été fixée, et il n'a plus d'objet."
        )

    m = MILIEUX[milieu]
    reference = m["reference"]
    aquatique = milieu in ("lac", "mer")

    # ── 01 · Ce sur quoi la simulation a tourné ─────────────────────────────
    releves: List[Tuple[str, str]] = [
        ("Milieu", m["nom"]),
        ("Niveau de référence", "le %s" % reference),
        ("Observateur", _point(obs_latitude, obs_longitude, obs_libelle)),
        ("Hauteur d'objectif employée", "%s m au-dessus du %s"
         % (format_metres(hauteur_observateur_m), reference)),
        ("Cible", _point(cible_latitude, cible_longitude, cible_libelle)),
        ("Hauteur de cible employée", "%s m, base prise au %s"
         % (format_metres(hauteur_cible_m), reference)),
        ("Distance géodésique", "%s km" % _km(distance_m)),
        ("Azimut de départ", "%s°" % _deg(azimut_deg)),
        ("Coefficient de réfraction", "k = %s (%s)" % (
            format_k(k_employe),
            "déclaré par vous" if k_personnalise
            else "moyenne standard, non mesurée",
        )),
    ]
    section_visee = Section(
        numero="01",
        titre="La visée simulée",
        releves=tuple(releves),
        reserves=(MOTIF_MILIEU_SANS_EFFET, m["reserve"]),
    )

    # ── 02 · Ce qu'il faut rapporter ────────────────────────────────────────
    champs: List[Champ] = [
        Champ(
            libelle="Hauteur de l'objectif au-dessus du %s, mesurée" % reference,
            unite="m",
            pourquoi=(
                "C'est le paramètre le plus sensible de toute la visée : près "
                "de la surface, quelques dizaines de centimètres changent "
                "l'occultation de façon visible. La simulation a tourné sur "
                "%s m — si votre mesure diffère, c'est elle qui compte."
                % format_metres(hauteur_observateur_m)
            ),
        ),
        Champ(
            libelle="La même hauteur, remesurée en fin de série",
            unite="m",
            pourquoi=(
                "Une embarcation s'enfonce, une marée monte, un trépied "
                "s'enfonce dans le sable. Deux valeurs qui diffèrent ne "
                "gâchent rien : elles disent que la série porte un intervalle "
                "et non un point."
            ),
        ),
        Champ(
            libelle="Position GPS relevée sur place",
            unite=None,
            pourquoi=(
                "Si elle diffère du point simulé, la distance change, donc la "
                "prédiction. Relever le point réel permet de refaire le calcul "
                "au lieu de jeter la série."
            ),
        ),
        Champ(
            libelle="Date, heure et fuseau du début de série",
            unite=None,
            pourquoi=(
                "Sans l'heure, ni la marée ni les températures ne peuvent être "
                "retrouvées après coup, et l'objection « c'était la "
                "réfraction » devient invérifiable dans les deux sens."
            ),
        ),
    ]

    if milieu == "mer":
        champs.append(Champ(
            libelle="Hauteur de marée à cette heure, et port de référence",
            unite="m",
            pourquoi=(
                "Le niveau de la mer EST le niveau de référence de ce calcul. "
                "Une marée de plusieurs mètres déplace d'autant votre hauteur "
                "d'objectif et la base de la cible."
            ),
        ))
    elif milieu == "lac":
        champs.append(Champ(
            libelle="Cote du lac, si une échelle limnimétrique est visible",
            unite="m",
            pourquoi=(
                "Le niveau d'un lac bouge peu mais il bouge, et une cote "
                "relevée vaut mieux qu'une cote supposée. Notez « non "
                "relevée » plutôt que de deviner."
            ),
            obligatoire=False,
        ))

    champs.append(Champ(
        libelle="Température de l'air à hauteur d'objectif",
        unite="°C",
        pourquoi=(
            "Elle n'entre PAS dans le calcul, qui tourne sur k = %s. Elle "
            "sert à ce qu'un tiers puisse borner k après coup et contester "
            "ce choix." % format_k(K_STANDARD)
        ),
    ))
    champs.append(Champ(
        libelle=("Température de l'eau en surface" if aquatique
                 else "Température de l'air à deux mètres du sol"),
        unite="°C",
        pourquoi=(
            "C'est l'ÉCART entre cette valeur et la précédente qui compte, et "
            "son signe : il dit dans quel sens la réfraction s'écarte de la "
            "moyenne employée. Deux températures sans leur écart ne servent à "
            "rien, et l'écart sans son signe non plus."
        ),
    ))
    champs.append(Champ(
        libelle="Appareil, objectif, et zoom optique ou numérique",
        unite=None,
        pourquoi=(
            "La focale est dans le fichier, le matériel ne l'est pas toujours. "
            "Un zoom numérique n'ajoute aucun détail : le savoir évite de "
            "mesurer un bord qui n'a été qu'agrandi."
        ),
    ))

    px = _hauteur_apparente_min_px(verdict.seuil_applique)
    if px is not None:
        pourquoi_px = (
            "Au seuil de %s %% de la hauteur de la cible comptée depuis sa "
            "base, un écart de %d pixels demande une cible de %d pixels de "
            "haut : zoomez jusque-là. Ce nombre est tiré du SEUIL et "
            "non de votre résultat — le donner à partir du résultat "
            "reviendrait à vous annoncer la grandeur que vous devez mesurer." % (
                format_pourcent(verdict.seuil_applique), PIXELS_MIN_ECART, px,
            )
        )
    else:
        pourquoi_px = (
            "Aucun seuil n'étant appliqué, aucune exigence de cadrage ne peut "
            "être formulée : notez la hauteur en pixels, elle servira à dire "
            "après coup si la mesure était possible."
        )
    champs.append(Champ(
        libelle="Hauteur de la cible sur l'image, en pixels",
        unite="px",
        pourquoi=pourquoi_px,
    ))

    section_mesures = Section(
        numero="02",
        titre="À consigner sur place",
        champs=tuple(champs),
    )

    # ── 03 · Le cadrage ────────────────────────────────────────────────────
    consignes: List[str] = [
        "Trépied, ou appui ferme sur un point fixe. À longue focale, le flou "
        "de bougé se confond avec le bord de la cible — et le bord est "
        "exactement ce qu'on mesure.",
        "Deux photographies par série au minimum : une LARGE qui montre le "
        "contexte et le niveau de référence, une au ZOOM MAXIMAL sur la "
        "cible. La large prouve de quoi on parle, la serrée sert à mesurer.",
        "Vérifier l'horizontalité au niveau à bulle ou au niveau de "
        "l'appareil, et la noter. Une bascule fait paraître masquée une base "
        "qui ne l'est pas.",
        "Photographier le mètre ou la mire au moment où vous mesurez la "
        "hauteur d'objectif. Une hauteur écrite sans image est une "
        "déclaration, pas une mesure.",
        "Ne rien recadrer, rien redresser, pas de HDR ni de correction "
        "automatique. Conserver le fichier d'origine tel que sorti de "
        "l'appareil, en plus de toute version retouchée.",
        "Refaire la série au moins deux fois, à quelques minutes "
        "d'intervalle. La réfraction change vite ; deux séries qui donnent la "
        "même chose valent mieux qu'une série isolée.",
    ]
    if aquatique:
        consignes.append(
            "Photographier la ligne d'eau au pied de la cible si elle est "
            "visible : c'est le repère de la base, et c'est ce repère que la "
            "mesure cherche."
        )
    else:
        consignes.append(
            "Photographier le terrain intermédiaire depuis le poste, aussi "
            "loin que possible. Sur terre, c'est la seule pièce qui permettra "
            "de discuter un pli de terrain — et sans elle la série ne pourra "
            "pas conclure."
        )

    section_cadrage = Section(
        numero="03",
        titre="Consignes de prise de vue",
        consignes=tuple(consignes),
    )

    # ── 04 · Le dépôt, sous scellé ─────────────────────────────────────────
    depot: List[Tuple[str, str]] = [
        ("Fiche générée le", horodatage),
        ("Modèle sphérique — masqué à la base",
         "%s m" % format_metres(verdict.hauteur_masquee_base_m)),
        ("Soit, en fraction de la cible",
         "%s %% de sa hauteur, comptés depuis la base"
         % format_pourcent(verdict.fraction_masquee_base)),
        ("Modèle plat — masqué à la base",
         "%s m" % format_metres(verdict.hauteur_masquee_plat_m)),
        ("Écart entre les deux prédictions",
         "%s m" % format_metres(verdict.ecart_entre_modeles_m)),
        ("Taille angulaire de cet écart",
         "%s minutes d'arc" % _arcmin(verdict.ecart_entre_modeles_m, distance_m)),
        ("Seuil retenu",
         "%s %% de la hauteur de la cible à partir de sa base, soit %s m ici" % (
             format_pourcent(verdict.seuil_applique),
             format_metres(hauteur_cible_m * verdict.seuil_applique),
         )),
        ("Verdict géométrique",
         "visée discriminante" if verdict.discriminante
         else "visée NON discriminante"),
    ]
    if not k_personnalise:
        depot.append((
            "Enveloppe de réfraction",
            "de %s à %s m masqués, pour k entre %s et %s" % (
                format_metres(masquee_enveloppe_min_m),
                format_metres(masquee_enveloppe_max_m),
                format_k(K_ENVELOPPE_MIN), format_k(K_ENVELOPPE_MAX),
            ),
        ))

    reserves_depot: List[str] = [verdict.motif, MOTIF_HORODATAGE]
    if not k_personnalise:
        reserves_depot.append(
            "La conclusion doit tenir sur TOUTE l'enveloppe ci-dessus. Si une "
            "seule valeur admissible de k réconcilie ce que vous avez mesuré "
            "avec la prédiction, le modèle n'est pas départagé — et c'est un "
            "résultat, pas un échec."
        )
    if verdict.fraction_masquee_base >= 1.0:
        reserves_depot.append(
            "La fraction masquée dépasse 100 %% : sur le modèle sphérique, la "
            "cible est entièrement sous l'horizon géométrique, et de %s m "
            "au-delà de son propre sommet. L'observation devient alors "
            "binaire — on voit quelque chose, ou rien — et c'est le cas où la "
            "réfraction explique le plus facilement une visibilité "
            "inattendue. Les deux températures deviennent la pièce "
            "principale." % format_metres(
                verdict.hauteur_masquee_base_m - hauteur_cible_m)
        )

    section_depot = Section(
        numero="05",
        titre="Prédiction déposée — à ne lire qu'après la prise de vue",
        releves=tuple(depot),
        reserves=tuple(reserves_depot),
        sous_scelle=True,
    )

    # ── 05 · Ce que la sortie ne pourra pas établir ────────────────────────
    reserves_finales = [
        "Cette observation ne conclura rien sur la forme de la Terre à elle "
        "seule. Elle confronte une mesure à ce que deux modèles géométriques "
        "prédisent, sur les données que vous aurez rapportées.",
        "Aucun modèle de terrain n'est employé. Une haie, un cargo, un "
        "bâtiment récent ne figurent dans aucun calcul : c'est sur l'image "
        "qu'il faut montrer qu'aucun obstacle ne masque la base.",
        "Un verdict « indéterminé » est un résultat. Il arrive dès que les "
        "données atmosphériques manquent, et le déclarer vaut mieux que de "
        "trancher sans elles.",
    ]
    if not verdict.discriminante:
        reserves_finales.insert(0, (
            "Cette visée n'est PAS discriminante : les deux modèles y "
            "prédisent des choses trop proches pour qu'une photographie les "
            "sépare. La sortie peut se faire, elle ne départagera rien. Viser "
            "plus loin, ou plus bas, ou une cible plus courte."
        ))

    section_limites = Section(
        numero="04",
        titre="Ce que cette sortie ne pourra pas établir",
        reserves=tuple(reserves_finales),
    )

    return FicheTerrain(
        milieu=milieu,
        milieu_nom=m["nom"],
        reference_verticale=reference,
        titre="Fiche protocole terrain",
        sous_titre="%s — visée de %s km, cible de %s m" % (
            m["nom"], _km(distance_m), format_metres(hauteur_cible_m)),
        horodatage=horodatage,
        discriminante=verdict.discriminante,
        sections=[
            section_visee, section_mesures, section_cadrage,
            section_limites,
            # Le dépôt EN DERNIER, pour qu'il soit la partie qu'on replie ou
            # qu'on découpe avant de partir. Au milieu de la page, une
            # consigne « ne pas lire » ne tient pas une seconde.
            section_depot,
        ],
    )


# ── Le rendu texte ──────────────────────────────────────────────────────────


def _replier(texte: str, largeur: int, premier: str = "", suite: Optional[str] = None) -> List[str]:
    """Replie un paragraphe, avec une indentation PENDANTE.

    `premier` préfixe la première ligne — « 1. », « [ ] », « · », une clé
    suivie de deux points ; `suite` préfixe les autres, et vaut par défaut
    autant d'espaces que `premier`. Sans cela, la deuxième ligne d'une
    consigne revient à la marge et la numérotation cesse de se lire : la liste
    devient un pavé où l'on ne voit plus où commence chaque point.

    Écrit à la main et non pris dans `textwrap` : le port TypeScript doit
    produire les MÊMES coupures, au caractère près, et les subtilités de
    `textwrap` (tirets, doubles espaces, mots interminables) ne se répliquent
    pas de mémoire. Un mot plus long que la largeur déborde plutôt que d'être
    coupé — une coupure au milieu d'un nombre serait pire que la ligne longue.
    """
    if suite is None:
        suite = " " * len(premier)
    mots = [x for x in texte.split(" ") if x != ""]
    lignes: List[str] = []
    courante = ""
    for mot in mots:
        essai = mot if courante == "" else courante + " " + mot
        marge = premier if not lignes else suite
        if len(marge) + len(essai) <= largeur or courante == "":
            courante = essai
        else:
            lignes.append(marge + courante)
            courante = mot
    if courante != "":
        lignes.append((premier if not lignes else suite) + courante)
    return lignes or [premier.rstrip()]


def rendre_txt(fiche: FicheTerrain, largeur: int = LARGEUR_TXT) -> str:
    """La fiche en texte pur, imprimable et lisible dans un courriel.

    Le texte pur est le format qui survit à tout : pas de police à charger,
    pas de visionneuse, pas de mise en page qui casse. C'est aussi celui qui
    se relit dix ans plus tard.
    """
    out: List[str] = []
    out.append(fiche.titre.upper())
    out.append(fiche.sous_titre)
    out.append("Simulateur de Visée — Terre Étendue Islam")
    out.append("=" * largeur)

    for s in fiche.sections:
        out.append("")
        out.append("%s · %s" % (s.numero, s.titre.upper()))
        out.append("-" * largeur)
        if s.sous_scelle:
            out.extend(_replier(MOTIF_AVEUGLE, largeur, "  ! ", "    "))
            out.append("")

        for cle, valeur in s.releves:
            # La clé préfixe la première ligne ; les suivantes s'alignent sous
            # la VALEUR, pas sous la clé, pour que la colonne se lise.
            out.extend(_replier(valeur, largeur, "  %s : " % cle))

        for c in s.champs:
            unite = " (%s)" % c.unite if c.unite else ""
            marque = "[ ] " if c.obligatoire else "[~] "
            out.extend(_replier(
                "%s%s" % (c.libelle, unite), largeur, "  " + marque, "      "))
            out.append("      " + "." * (largeur - 6))
            out.extend(_replier(c.pourquoi, largeur, "      → ", "        "))
            out.append("")

        for i, texte in enumerate(s.consignes, start=1):
            tete = "  %d. " % i
            out.extend(_replier(texte, largeur, tete, " " * len(tete)))
            out.append("")

        for texte in s.reserves:
            out.extend(_replier(texte, largeur, "  · ", "    "))
            out.append("")

    out.append("=" * largeur)
    out.append("CE QUE CETTE FICHE NE DEMANDE PAS, ET POURQUOI")
    out.append("-" * largeur)
    for titre, motif in fiche.champs_ecartes:
        out.extend(_replier(titre, largeur, "  – ", "    "))
        out.extend(_replier(motif, largeur, "      "))
        out.append("")

    # Une ligne finale, et pas de fin de fichier sans saut : un fichier texte
    # se termine par un saut de ligne, c'est la convention et certains outils
    # avalent la dernière ligne sans lui.
    return "\n".join(out).rstrip("\n") + "\n"


def nom_fichier(fiche: FicheTerrain, distance_m: float) -> str:
    """Un nom de fichier sans accent, sans espace et sans surprise.

    Ni l'horodatage ni le libellé du lieu n'y entrent : le premier contient
    des deux-points, refusés par certains systèmes de fichiers, et le second
    des accents et des apostrophes. Le nom sert à retrouver le fichier, pas à
    le décrire.
    """
    return "fiche-terrain-%s-%s-km.txt" % (
        fiche.milieu, ("%.0f" % (distance_m / 1000.0)))
