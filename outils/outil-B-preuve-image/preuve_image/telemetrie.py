"""
telemetrie.py — La télémétrie de vol écrite dans le XMP (§16, §12).

CE QUE CE MODULE LIT
────────────────────
Les aéronefs civils écrivent leur état de vol dans le paquet XMP de chaque
image : position, altitude, attitude du porteur et de la nacelle. Ce sont des
champs d'espaces de noms propriétaires mais PUBLIÉS — DJI, Parrot et Autel les
documentent — donc lisibles sans conjecture.

Pour le protocole, ces champs comptent doublement. L'altitude relative donne la
hauteur de l'axe optique au-dessus du point de décollage, qui est la grandeur
`h` du §12 ; et le tangage de la nacelle dit si la visée était horizontale, ce
sans quoi aucune mesure d'angle n'a de sens.

CE QU'IL N'ÉTABLIT PAS
──────────────────────
Rien de ce qui est lu ici n'est vérifié. Un champ XMP s'écrit et se modifie
comme n'importe quel texte ; ces valeurs sont ce que l'appareil DÉCLARE avoir
mesuré, et un GPS de drone se trompe, dérive, ou perd sa constellation.

Deux pièges nommés plutôt que tus :

  · L'ALTITUDE RELATIVE est comptée depuis le point de DÉCOLLAGE, pas depuis le
    sol survolé ni depuis le niveau de la mer. Un décollage depuis une colline
    fausse la lecture de plusieurs dizaines de mètres, et rien dans le fichier
    ne dit d'où l'appareil est parti.

  · La POSITION DE LA STATION SOL n'est presque jamais écrite. Ce que le
    fichier porte, c'est la position du drone. Le champ demandé par le cahier
    des charges — station sol contre position drone — n'existe pas dans le cas
    courant : c'est dit, plutôt que rempli par la position du drone sous une
    autre étiquette.
"""

import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

__all__ = [
    "TelemetrieError",
    "ChampTelemetrie",
    "TelemetrieVol",
    "extraire_telemetrie",
    "ESPACES_CONNUS",
    "MOTIF_STATION_SOL_ABSENTE",
    "AVERTISSEMENT_ALTITUDE_RELATIVE",
]


class TelemetrieError(ValueError):
    """Bloc de télémétrie malformé."""


#: Les espaces de noms de télémétrie qu'on sait nommer, et le fabricant
#: qui les publie. Un préfixe absent de cette table est relevé quand même,
#: sous son nom brut : savoir qu'il y a de la télémétrie qu'on ne sait pas
#: attribuer vaut mieux que de l'écarter.
ESPACES_CONNUS = {
    "drone-dji": "DJI",
    "drone-parrot": "Parrot",
    "Camera": "espace « Camera » (Parrot, Autel, et DJI pour l'attitude)",
    "drone": "espace « drone » générique (Autel)",
    "FLIR": "FLIR (imagerie thermique)",
    "GPano": "panorama sphérique (Google)",
}

MOTIF_STATION_SOL_ABSENTE = (
    "La position de la station sol n'est pas écrite dans le fichier. Ce que "
    "l'aéronef enregistre est SA position ; le point de décollage ne l'est "
    "qu'exceptionnellement, et jamais par les modèles courants. La renseigner "
    "avec la position du drone sous une autre étiquette donnerait un champ "
    "rempli et faux."
)

AVERTISSEMENT_ALTITUDE_RELATIVE = (
    "L'altitude relative est comptée depuis le POINT DE DÉCOLLAGE, pas depuis "
    "le sol survolé ni depuis le niveau de la mer. Un décollage depuis une "
    "colline la décale d'autant, et le fichier ne dit pas d'où l'appareil est "
    "parti. Pour servir de hauteur h au sens du §12, elle demande l'altitude "
    "du point de décollage, qui est une donnée EXTÉRIEURE au fichier."
)


@dataclass(frozen=True)
class ChampTelemetrie:
    """Un champ de télémétrie, tel qu'il est écrit.

    `brut` est conservé à côté de la valeur convertie : DJI écrit ses altitudes
    avec un signe explicite (« +12.30 »), et rendre uniquement le nombre
    perdrait la forme exacte du fichier — celle qu'un autre outil relira.
    """

    prefixe: str
    nom: str
    brut: str
    valeur: Optional[float] = None

    @property
    def cle(self) -> str:
        return f"{self.prefixe}:{self.nom}"


#: Les champs dont on connaît le sens, par nom (le préfixe varie selon le
#: constructeur). La valeur est ce que le champ désigne, en clair.
_SENS = {
    "AbsoluteAltitude": "altitude absolue déclarée (au-dessus du niveau de référence GNSS)",
    "RelativeAltitude": "altitude au-dessus du point de décollage",
    "AboveGroundAltitude": "altitude au-dessus du sol survolé",
    "GpsLatitude": "latitude du porteur",
    "GpsLongitude": "longitude du porteur",
    "GpsLongtitude": "longitude du porteur (orthographe DJI)",
    "GpsAltitude": "altitude GNSS du porteur",
    "GimbalRollDegree": "roulis de la nacelle",
    "GimbalYawDegree": "lacet de la nacelle",
    "GimbalPitchDegree": "tangage de la nacelle",
    "FlightRollDegree": "roulis du porteur",
    "FlightYawDegree": "lacet du porteur",
    "FlightPitchDegree": "tangage du porteur",
    "FlightXSpeed": "vitesse selon X",
    "FlightYSpeed": "vitesse selon Y",
    "FlightZSpeed": "vitesse verticale",
    "Yaw": "lacet",
    "Pitch": "tangage",
    "Roll": "roulis",
    "GPSXYAccuracy": "incertitude horizontale annoncée",
    "GPSZAccuracy": "incertitude verticale annoncée",
    "RtkFlag": "état de la correction RTK",
    "RtkStdLon": "écart-type RTK en longitude",
    "RtkStdLat": "écart-type RTK en latitude",
    "RtkStdHgt": "écart-type RTK en altitude",
    "CalibratedFocalLength": "focale étalonnée déclarée",
    "DewarpFlag": "correction de distorsion appliquée",
    "DewarpData": "coefficients de correction de distorsion",
    "GimbalReverse": "nacelle retournée",
    "CamReverse": "caméra retournée",
    "SelfData": "champ libre du constructeur",
}

#: Le tangage de nacelle, quel que soit le constructeur. C'est le champ qui
#: décide si une visée peut servir : une mesure d'angle sur une image prise en
#: plongée ne veut pas dire la même chose qu'à l'horizontale.
_NOMS_TANGAGE = ("GimbalPitchDegree", "Pitch")


@dataclass
class TelemetrieVol:
    """Ce que le fichier déclare de son vol. Rien n'est vérifié."""

    present: bool
    #: Le fabricant déduit des espaces de noms trouvés, ou None.
    origine: Optional[str] = None
    prefixes: Tuple[str, ...] = ()
    champs: Tuple[ChampTelemetrie, ...] = ()
    #: Les grandeurs que le protocole utilise, extraites nommément.
    latitude_deg: Optional[float] = None
    longitude_deg: Optional[float] = None
    altitude_absolue_m: Optional[float] = None
    altitude_relative_m: Optional[float] = None
    altitude_sol_m: Optional[float] = None
    tangage_nacelle_deg: Optional[float] = None
    lacet_nacelle_deg: Optional[float] = None
    roulis_nacelle_deg: Optional[float] = None
    #: Ce que le fichier ne porte pas, et pourquoi c'est dit.
    station_sol: None = None
    motif_station_sol: str = MOTIF_STATION_SOL_ABSENTE
    avertissement_altitude: str = AVERTISSEMENT_ALTITUDE_RELATIVE
    sens: Dict[str, str] = field(default_factory=dict)

    @property
    def visee_horizontale(self) -> Optional[bool]:
        """Vrai si le tangage de nacelle est à moins d'un degré de l'horizontale.

        None quand le tangage n'est pas déclaré — jamais False par défaut : une
        absence de mesure n'établit pas que la visée était inclinée.
        """
        if self.tangage_nacelle_deg is None:
            return None
        return abs(self.tangage_nacelle_deg) <= 1.0


def _nombre(brut: str) -> Optional[float]:
    """Convertit une valeur XMP en nombre, ou rend None si ce n'en est pas un.

    Les constructeurs écrivent volontiers un signe explicite (« +12.30 ») et
    parfois une unité collée. On extrait le nombre en tête ; s'il n'y en a pas,
    on ne convertit pas plutôt que de rendre zéro.
    """
    m = re.match(r"\s*([+-]?[0-9]+(?:\.[0-9]+)?(?:[eE][+-]?[0-9]+)?)", brut)
    if not m:
        return None
    try:
        return float(m.group(1))
    except ValueError:
        return None


#: Les deux formes d'écriture du XMP. Un même champ peut apparaître en
#: attribut d'un élément rdf:Description, ou en élément à part entière — les
#: constructeurs emploient les deux, parfois dans le même fichier.
def _relever(texte: str, prefixes: Tuple[str, ...]) -> List[ChampTelemetrie]:
    trouves: Dict[str, ChampTelemetrie] = {}
    for prefixe in prefixes:
        p = re.escape(prefixe)
        # Forme attribut : prefixe:Nom="valeur"
        for nom, brut in re.findall(p + r':([A-Za-z0-9_]+)\s*=\s*"([^"]*)"', texte):
            c = ChampTelemetrie(prefixe, nom, brut, _nombre(brut))
            trouves.setdefault(c.cle, c)
        # Forme élément : <prefixe:Nom>valeur</prefixe:Nom>
        for nom, brut in re.findall(p + r":([A-Za-z0-9_]+)[^>]*>([^<]{0,200})<", texte):
            c = ChampTelemetrie(prefixe, nom, brut.strip(), _nombre(brut))
            trouves.setdefault(c.cle, c)
    return sorted(trouves.values(), key=lambda c: c.cle)


def _premier(champs: List[ChampTelemetrie], *noms: str) -> Optional[float]:
    """La première valeur numérique parmi ces noms, quel que soit le préfixe."""
    for nom in noms:
        for c in champs:
            if c.nom == nom and c.valeur is not None:
                return c.valeur
    return None


def extraire_telemetrie(paquets_xmp) -> TelemetrieVol:
    """Relève la télémétrie de vol dans un ou plusieurs paquets XMP.

    Accepte des `bytes` ou des `str`, un paquet ou une suite : les paquets
    viennent selon les cas de `provenance.extraire_xmp`, de
    `conteneurs.inventorier` ou de `isobmff.analyser_isobmff`, et leur imposer
    une forme unique déplacerait seulement la conversion chez l'appelant.
    """
    if isinstance(paquets_xmp, (bytes, bytearray, str)):
        paquets_xmp = [paquets_xmp]
    textes = []
    for p in paquets_xmp:
        if isinstance(p, (bytes, bytearray)):
            textes.append(bytes(p).decode("utf-8", errors="replace"))
        else:
            textes.append(str(p))
    texte = "\n".join(textes)

    prefixes_vus = []
    for prefixe in ESPACES_CONNUS:
        if re.search(re.escape(prefixe) + r"\s*[:=]", texte):
            prefixes_vus.append(prefixe)
    # Un préfixe de télémétrie hors table est relevé sous son nom brut : savoir
    # qu'il y a de la télémétrie qu'on ne sait pas attribuer vaut mieux que de
    # l'écarter en silence.
    for prefixe in re.findall(r'xmlns:([A-Za-z0-9_-]*[Dd]rone[A-Za-z0-9_-]*)\s*=', texte):
        if prefixe not in prefixes_vus:
            prefixes_vus.append(prefixe)

    if not prefixes_vus:
        return TelemetrieVol(present=False)

    champs = _relever(texte, tuple(prefixes_vus))
    if not champs:
        return TelemetrieVol(present=False, prefixes=tuple(prefixes_vus))

    origines = [ESPACES_CONNUS[p] for p in prefixes_vus if p in ESPACES_CONNUS]
    # « Camera » seul ne désigne aucun constructeur : c'est un espace partagé.
    # L'annoncer comme une origine serait une attribution sans fondement.
    specifiques = [o for p, o in zip(prefixes_vus, origines)
                   if p in ("drone-dji", "drone-parrot", "FLIR")]

    return TelemetrieVol(
        present=True,
        origine=specifiques[0] if specifiques else None,
        prefixes=tuple(prefixes_vus),
        champs=tuple(champs),
        latitude_deg=_premier(champs, "GpsLatitude"),
        # DJI écrit « GpsLongtitude », avec un t de trop. C'est une faute de
        # frappe du constructeur, présente dans tous ses fichiers depuis des
        # années : ne traiter que l'orthographe correcte ferait perdre la
        # longitude sur la majorité des images de drone en circulation.
        longitude_deg=_premier(champs, "GpsLongitude", "GpsLongtitude"),
        altitude_absolue_m=_premier(champs, "AbsoluteAltitude", "GpsAltitude"),
        altitude_relative_m=_premier(champs, "RelativeAltitude"),
        altitude_sol_m=_premier(champs, "AboveGroundAltitude"),
        tangage_nacelle_deg=_premier(champs, *_NOMS_TANGAGE),
        lacet_nacelle_deg=_premier(champs, "GimbalYawDegree", "Yaw"),
        roulis_nacelle_deg=_premier(champs, "GimbalRollDegree", "Roll"),
        sens={c.cle: _SENS[c.nom] for c in champs if c.nom in _SENS},
    )
