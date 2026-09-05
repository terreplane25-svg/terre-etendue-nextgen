"""
document.py — Le document JSON d'ingestion (§16).

Un seul appel, `document_ingestion(octets)`, rend tout ce qu'un fichier déclare,
dans la forme convenue : `file_info`, `exif`, `c2pa`, `thumbnail`.

QUATRE ÉCARTS AU SCHÉMA DEMANDÉ, ET POURQUOI
────────────────────────────────────────────
Le schéma reçu est suivi champ pour champ. Quatre points ne pouvaient pas
l'être tels quels sans écrire des choses fausses ; dans les quatre cas, la clé
demandée existe et une clé voisine porte ce qui manquait.

1. **L'horodatage ne peut pas porter de fuseau que le fichier ne déclare pas.**
   Le schéma demande « 2014-07-31T18:05:43+02:00 ». Or `DateTimeOriginal` est
   une heure locale SANS fuseau : l'offset n'existe que si l'appareil a écrit
   `OffsetTimeOriginal` (tag 0x9011), ce que peu de boîtiers font. Écrire
   « +02:00 » par défaut inventerait une information — et, sur une observation
   horodatée, ce serait exactement le genre d'invention qui décide d'un
   résultat. Donc : offset présent → ISO 8601 complet ; offset absent → heure
   locale sans suffixe, et `offset_declare: false` à côté. La clé `original`
   reste toujours là, et ne ment jamais.

2. **`dpi` est un scalaire, la réalité en a deux.** L'EXIF porte XResolution et
   YResolution, qui peuvent différer, et aucune densité n'est définie quand
   ResolutionUnit vaut 1 (« sans unité » : le nombre est un rapport d'aspect).
   Donc : `dpi` porte la valeur commune quand les deux coïncident, `null`
   sinon, et `dpi_x` / `dpi_y` sont toujours là.

3. **`camera` concatène Make et Model, ce qui ne se défait pas.** « SONY
   ILCE-6000 » ne redonne pas à coup sûr le couple d'origine. La clé est rendue
   telle que demandée, et `make` / `model` restent séparément disponibles.

4. **`c2pa.signature` ne peut pas être une chaîne qui a l'air d'un verdict.**
   Ce module ne vérifie AUCUNE signature. La clé porte donc l'identité DÉCLARÉE
   du signataire — rien de plus — et `verified: false` l'accompagne toujours,
   avec le motif. Une clé nommée « signature » ne doit pas pouvoir se lire
   comme « signature valide ».

Le document ajoute par ailleurs ce que la section 1 du cahier des charges
demandait et que l'exemple n'illustrait pas : XMP, IPTC, chaînes des en-têtes,
zoom numérique, flash, altitude et incertitude GPS.
"""

import hashlib
import struct
from typing import Any, Dict, Optional, Tuple

from .metadata import DonneesExif, MetadataError, decrire_flash, lire_exif_depuis_jpeg
from .metadata import (
    _LIBELLE_COLOR_SPACE,
    _LIBELLE_EXPOSURE_MODE,
    _LIBELLE_EXPOSURE_PROGRAM,
    _LIBELLE_RESOLUTION_UNIT,
    _LIBELLE_SCENE_CAPTURE,
    _LIBELLE_WHITE_BALANCE,
)
from .provenance import AVERTISSEMENT_C2PA, Provenance, analyser_provenance

__all__ = [
    "dimensions_jpeg",
    "horodatage_iso",
    "vitesse_obturation",
    "document_ingestion",
    "MOTIF_SIGNATURE_NON_VERIFIEE",
]

MOTIF_SIGNATURE_NON_VERIFIEE = (
    "Aucune signature n'est vérifiée : ni la validation COSE, ni la chaîne X.509, "
    "ni les empreintes de liaison au contenu. La valeur du champ « signature » est "
    "l'identité que le manifeste DÉCLARE, pas une identité établie."
)

# Marqueurs SOF d'un JPEG. On exclut DHT (0xC4), JPG (0xC8) et DAC (0xCC), qui
# tombent dans la même plage sans être des en-têtes de trame.
_MARQUEURS_SOF = frozenset(
    set(range(0xC0, 0xD0)) - {0xC4, 0xC8, 0xCC}
)


def dimensions_jpeg(donnees: bytes) -> Optional[Tuple[int, int]]:
    """Dimensions d'un JPEG, lues dans son marqueur SOF — sans le décoder.

    Sert à donner les dimensions de la miniature sans la décompresser : on veut
    savoir ce qu'elle DÉCLARE, et une décompression coûterait pour rendre la
    même chose. Rend None si aucun SOF n'est trouvé.
    """
    if len(donnees) < 4 or donnees[0:2] != b"\xff\xd8":
        return None
    pos = 2
    while pos + 4 <= len(donnees):
        if donnees[pos] != 0xFF:
            return None
        marqueur = donnees[pos + 1]
        if marqueur == 0xD8 or 0xD0 <= marqueur <= 0xD7:
            pos += 2
            continue
        if marqueur in (0xD9, 0xDA):
            return None
        longueur = struct.unpack_from(">H", donnees, pos + 2)[0]
        if marqueur in _MARQUEURS_SOF:
            if pos + 9 > len(donnees):
                return None
            hauteur, largeur = struct.unpack_from(">HH", donnees, pos + 5)
            return (largeur, hauteur)
        pos += 2 + longueur
    return None


def horodatage_iso(exif_datetime: Optional[str], decalage: Optional[str]) -> Dict[str, Any]:
    """Convertit « AAAA:MM:JJ HH:MM:SS » en ISO 8601, sans inventer de fuseau.

    Le fuseau n'est ajouté que si l'appareil a écrit le tag de décalage
    correspondant. Sinon la valeur est une heure locale nue, et
    `offset_declare` vaut False pour que le lecteur le sache sans avoir à le
    déduire d'une absence de suffixe.
    """
    if not exif_datetime:
        return {"valeur": None, "offset_declare": False, "brut": None}
    brut = exif_datetime.strip()
    partie = brut.replace(":", "-", 2).replace(" ", "T", 1)
    if decalage and decalage.strip():
        return {"valeur": partie + decalage.strip(), "offset_declare": True, "brut": brut}
    return {"valeur": partie, "offset_declare": False, "brut": brut}


def vitesse_obturation(secondes: Optional[float]) -> Optional[str]:
    """« 1/200 » sous la seconde, « 2,5 s » au-delà. Forme d'affichage seulement.

    Le nombre exact reste rendu à côté, dans `shutter_speed_s` : une fraction
    arrondie ne se recalcule pas, et un dossier d'audit doit pouvoir refaire le
    calcul.
    """
    if secondes is None or secondes <= 0:
        return None
    if secondes >= 1:
        return ("%g s" % secondes).replace(".", ",")
    return "1/%d" % round(1.0 / secondes)


def _camera(e: DonneesExif) -> Optional[str]:
    morceaux = [m.strip() for m in (e.fabricant, e.modele) if m and m.strip()]
    return " ".join(morceaux) if morceaux else None


def _code_et_libelle(code: Optional[int], table: Dict[int, str]) -> Dict[str, Any]:
    """Le code ET son libellé. Le libellé est une interprétation, le code un fait."""
    return {"code": code, "libelle": table.get(code) if code is not None else None}


def _bloc_c2pa(prov: Provenance) -> Dict[str, Any]:
    c = prov.c2pa
    actions = []
    signataires = []
    for m in c.manifestes:
        for a in m.actions:
            nom = a.get("action")
            if isinstance(nom, str) and nom not in actions:
                actions.append(nom)
        if m.generateur and m.generateur not in signataires:
            signataires.append(m.generateur)
    return {
        "present": c.present,
        "actions": actions,
        # Identité DÉCLARÉE du signataire. Jamais une identité établie : voir
        # `verified` et `motif` juste en dessous.
        "signature": signataires[0] if signataires else None,
        "verified": False,
        "motif": MOTIF_SIGNATURE_NON_VERIFIEE,
        "avertissement": AVERTISSEMENT_C2PA,
        "conteneur": c.conteneur,
        "octets": c.octets,
        "manifestes": [
            {
                "label": m.label,
                "generateur_declare": m.generateur,
                "algorithme_declare": m.algorithme_signature,
                "bloc_signature_present": m.signature_presente,
                "assertions": sorted(m.assertions),
                "actions": m.actions,
            }
            for m in c.manifestes
        ],
    }


def _bloc_thumbnail(e: Optional[DonneesExif]) -> Dict[str, Any]:
    m = e.miniature if e else None
    if m is None:
        return {"present": False, "dimensions": None}
    dims = dimensions_jpeg(m.octets) if m.est_jpeg else None
    return {
        "present": True,
        "dimensions": list(dims) if dims else None,
        "octets": m.longueur,
        "offset": m.offset,
        "format": "JPEG" if m.est_jpeg else "non reconnu",
        "sha256": hashlib.sha256(m.octets).hexdigest(),
        # Ce que la miniature établit, et ce qu'elle n'établit pas : à joindre
        # au chiffre, sans quoi le chiffre se lit comme une garantie.
        "ce_que_ca_n_etablit_pas": (
            "Une miniature qui concorde avec l'image n'établit rien : tout éditeur "
            "qui la régénère efface la trace. Seul un ÉCART entre elle et l'image "
            "principale est un fait."
        ),
    }


def document_ingestion(donnees: bytes, nom_fichier: Optional[str] = None) -> Dict[str, Any]:
    """Tout ce que le fichier déclare, dans la forme convenue. Rien n'est vérifié."""
    try:
        exif: Optional[DonneesExif] = lire_exif_depuis_jpeg(donnees)
        motif_exif = None
    except MetadataError as err:
        exif = None
        motif_exif = str(err)

    prov = analyser_provenance(donnees)

    largeur = hauteur = None
    if exif is not None:
        largeur = exif.largeur_px if exif.largeur_px is not None else exif.largeur_ifd0_px
        hauteur = exif.hauteur_px if exif.hauteur_px is not None else exif.hauteur_ifd0_px
    if largeur is None or hauteur is None:
        dims = dimensions_jpeg(donnees)
        if dims:
            largeur, hauteur = dims

    dpi_commun = None
    if exif is not None and exif.dpi_x is not None and exif.dpi_y is not None:
        if abs(exif.dpi_x - exif.dpi_y) < 1e-9:
            dpi_commun = exif.dpi_x

    doc: Dict[str, Any] = {
        "outil": "preuve-image (outil B) — ingestion",
        "protocole": "Portion visible d'une cible éloignée au-dessus de la mer v1.0",
        "fichier": nom_fichier,
        "sha256": hashlib.sha256(donnees).hexdigest(),
        "octets": len(donnees),
        "file_info": {
            "dimensions": [largeur, hauteur] if largeur and hauteur else None,
            "color_space": (
                _LIBELLE_COLOR_SPACE.get(exif.espace_colorimetrique)
                if exif and exif.espace_colorimetrique is not None else None
            ),
            "color_space_code": exif.espace_colorimetrique if exif else None,
            # Scalaire seulement quand les deux axes coïncident : sinon, une
            # valeur unique masquerait une anisotropie réelle.
            "dpi": dpi_commun,
            "dpi_x": exif.dpi_x if exif else None,
            "dpi_y": exif.dpi_y if exif else None,
            "resolution_unit": (
                _code_et_libelle(exif.unite_resolution, _LIBELLE_RESOLUTION_UNIT)
                if exif else _code_et_libelle(None, _LIBELLE_RESOLUTION_UNIT)
            ),
        },
        "exif": None,
        "c2pa": _bloc_c2pa(prov),
        "thumbnail": _bloc_thumbnail(exif),
        "xmp": [
            {"conteneur": b.conteneur, "octets": b.octets, "etendu": b.etendu,
             "champs": dict(b.champs)}
            for b in prov.xmp
        ],
        "iptc": [
            {"jeu": e.jeu, "numero": e.numero, "libelle": e.libelle, "valeur": e.valeur}
            for e in prov.iptc
        ],
        "chaines": {
            "nombre": len(prov.chaines),
            "marqueurs_logiciels": list(prov.marqueurs_logiciels),
            "ce_que_ca_n_etablit_pas": (
                "Un marqueur logiciel n'établit pas qu'il y a eu retouche — un "
                "convertisseur de format écrit son nom sans toucher au contenu "
                "visible — et son absence n'établit pas le contraire."
            ),
        },
    }

    if exif is None:
        doc["exif"] = {"lu": False, "motif": motif_exif}
        return doc

    doc["exif"] = {
        "lu": True,
        "camera": _camera(exif),
        "make": exif.fabricant,
        "model": exif.modele,
        "software": exif.logiciel,
        "lens": exif.objectif,
        "artist": exif.artiste,
        "copyright": exif.droits,
        "orientation": exif.orientation,
        "settings": {
            "iso": exif.sensibilite_iso,
            "f_number": exif.ouverture,
            "shutter_speed": vitesse_obturation(exif.temps_pose_s),
            # Le nombre exact : une fraction arrondie ne se recalcule pas.
            "shutter_speed_s": exif.temps_pose_s,
            "focal_length_mm": exif.focale_mm,
            "focal_length_35mm": exif.focale_equivalente_35mm,
            "digital_zoom_ratio": exif.rapport_zoom_numerique,
            "digital_zoom_applied": exif.zoom_numerique_applique,
            "flash": {"code": exif.flash, "libelle": decrire_flash(exif.flash)},
            "exposure_mode": _code_et_libelle(exif.mode_exposition, _LIBELLE_EXPOSURE_MODE),
            "exposure_program": _code_et_libelle(
                exif.programme_exposition, _LIBELLE_EXPOSURE_PROGRAM
            ),
            "white_balance": _code_et_libelle(exif.balance_blancs, _LIBELLE_WHITE_BALANCE),
            "scene_capture_type": _code_et_libelle(exif.type_scene, _LIBELLE_SCENE_CAPTURE),
        },
        "dates": {
            "original": horodatage_iso(exif.date_heure_original, exif.decalage_horaire_original),
            "digitized": horodatage_iso(
                exif.date_heure_numerisation, exif.decalage_horaire_numerisation
            ),
            "modified": horodatage_iso(exif.date_heure_modification, exif.decalage_horaire),
            "ce_que_ca_n_etablit_pas": (
                "Un horodatage EXIF est réglé par l'appareil et se modifie avec un "
                "éditeur de texte : il documente une déclaration, il ne date pas la "
                "prise de vue. Quand `offset_declare` est faux, l'heure est locale et "
                "son fuseau est INCONNU — il n'est pas supposé."
            ),
        },
        "gps": None if exif.gps is None else {
            "latitude": exif.gps.latitude_deg,
            "longitude": exif.gps.longitude_deg,
            "altitude_m": exif.gps.altitude_m,
            # Presque aucun boîtier n'écrit GPSHPositioningError. L'absence est
            # rendue telle quelle : le §15.4 interdit de la combler.
            "incertitude_m": exif.gps.incertitude_m,
            "source": exif.gps.source,
        },
    }
    return doc
