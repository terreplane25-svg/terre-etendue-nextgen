#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or de l'extraction — quantification JPEG et télémétrie de vol.

Le vérificateur du site tourne dans le navigateur, donc en TypeScript, mais la
référence reste le paquet Python. Ce script fait calculer au Python une série de
cas et écrit entrées et résultats attendus dans un fichier que
`scripts/verifier-port-extraction.mjs` rejoue en TypeScript.

Les fichiers et les paquets XMP sont construits par les mêmes fonctions que les
tests du paquet, pas réécrites ici : un fixture qui divergerait de ce que les
tests éprouvent ne vérifierait rien.

CONTRÔLE AVANT ÉCRITURE
───────────────────────
Le script revérifie que ses cas discriminent : que les qualités couvrent les
deux branches de l'algorithme IJG (au-dessus et au-dessous de 50), qu'au moins
un cas n'est PAS conforme IJG, que les empreintes diffèrent quand les tables
diffèrent, et que le cas DJI porte bien l'orthographe fautive et elle seule.

    python3 scripts/generer-vecteurs-or-extraction.py
"""
import base64
import json
import os
import sys
from datetime import datetime, timezone

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
PAQUET_B = os.path.join(RACINE, "outils", "outil-B-preuve-image")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-extraction.json")

sys.path.insert(0, PAQUET_B)
try:
    import preuve_image  # noqa: F401
except ImportError:
    if not os.path.exists(VENV):
        sys.exit("venv des outils absent : %s (voir outils/README.md)" % VENV)
    os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from tests.test_quantification import jpeg  # noqa: E402
from tests.test_telemetrie import (  # noqa: E402
    XMP_DJI, XMP_PARROT, XMP_SANS_TELEMETRIE,
)
from preuve_image.quantification import (  # noqa: E402
    MOTIF_AUCUNE_SIGNATURE, TABLE_LUMINANCE_ANNEXE_K,
    analyser_quantification, qualite_ijg_estimee, table_ijg,
)
from preuve_image.telemetrie import (  # noqa: E402
    AVERTISSEMENT_ALTITUDE_RELATIVE, MOTIF_STATION_SOL_ABSENTE,
    extraire_telemetrie,
)


def jpeg_non_ijg() -> bytes:
    """Un JPEG dont les tables ne viennent d'aucun facteur IJG entier.

    C'est le cas de tout appareil photo. Sans ce cas, rien ne distinguerait un
    lecteur qui rend l'écart d'un lecteur qui le tait.
    """
    brut = bytearray(jpeg(qualite=90))
    i = brut.find(b"\xff\xdb")
    for k in range(5, 12):
        brut[i + k] = min(255, brut[i + k] + 7)
    return bytes(brut)


def jpeg_gris() -> bytes:
    """Un JPEG à une seule composante. « 4:x:x » n'y a pas de sens."""
    from io import BytesIO
    from PIL import Image
    t = BytesIO()
    Image.new("L", (32, 32), 128).save(t, format="JPEG", quality=80)
    return t.getvalue()


def jpeg_16_bits() -> bytes:
    """Une table de précision 16 bits : la lire en 8 donnerait n'importe quoi."""
    import struct
    valeurs = tuple(range(1, 65))
    corps = b"\x10" + struct.pack(">64H", *valeurs)
    return (b"\xff\xd8"
            + b"\xff\xdb" + struct.pack(">H", 2 + len(corps)) + corps
            + b"\xff\xc0" + struct.pack(">H", 8) + b"\x08" + struct.pack(">HH", 16, 16)
            + b"\x01" + b"\x01\x11\x00"
            + b"\xff\xda" + struct.pack(">H", 2))


CAS_JPEG = [
    # Les deux branches de l'algorithme IJG : l'échelle change de formule à 50.
    ("qualité 1 (branche basse, saturation)", jpeg(qualite=1)),
    ("qualité 25 (branche basse)", jpeg(qualite=25)),
    ("qualité 50 (charnière)", jpeg(qualite=50)),
    ("qualité 75 (branche haute)", jpeg(qualite=75)),
    ("qualité 95 (branche haute)", jpeg(qualite=95)),
    ("qualité 100", jpeg(qualite=100)),
    ("sous-échantillonnage 4:4:4", jpeg(qualite=88, sous_ech=0)),
    ("sous-échantillonnage 4:2:2", jpeg(qualite=88, sous_ech=1)),
    ("sous-échantillonnage 4:2:0", jpeg(qualite=88, sous_ech=2)),
    ("progressif", jpeg(qualite=80, progressif=True)),
    ("tables non conformes IJG", jpeg_non_ijg()),
    ("précision 16 bits", jpeg_16_bits()),
    # Une seule composante : la notation « 4:x:x » n'a alors pas de sens, et
    # sans ce cas rien ne distinguerait un lecteur qui le sait d'un lecteur qui
    # rend une notation inventée.
    ("niveaux de gris (une composante)", jpeg_gris()),
]

#: « Camera » sans espace constructeur : l'origine doit rester nulle. Sans ce
#: cas, attribuer « Camera » à un fabricant passerait inaperçu.
XMP_CAMERA_SEUL = XMP_PARROT.replace(
    b'xmlns:drone-parrot="http://www.parrot.com/drone-parrot/1.0/"', b"")

CAS_XMP = [
    ("DJI, forme attribut", XMP_DJI),
    ("Camera seul, sans constructeur", XMP_CAMERA_SEUL),
    # Deux paquets où GimbalPitchDegree ET Pitch coexistent avec des valeurs
    # DIFFÉRENTES : c'est le seul cas où l'ordre de priorité s'observe.
    ("DJI et Parrot fusionnés", XMP_DJI + b"\n" + XMP_PARROT),
    ("Parrot, forme élément", XMP_PARROT),
    ("sans télémétrie", XMP_SANS_TELEMETRIE),
    ("préfixe de drone hors table", XMP_DJI.replace(b"drone-dji", b"drone-inconnu")),
    ("valeur illisible", XMP_DJI.replace(
        b'drone-dji:RelativeAltitude="+87.50"',
        b'drone-dji:RelativeAltitude="indisponible"')),
    ("tangage absent", XMP_DJI.replace(b'drone-dji:GimbalPitchDegree="-0.40"', b"")),
]

REFUS_JPEG = [
    ("pas un JPEG", b"\x89PNG\r\n\x1a\n" + b"\x00" * 32),
    ("JPEG sans DQT", b"\xff\xd8\xff\xe0\x00\x10JFIF\x00" + b"\x00" * 11 + b"\xff\xd9"),
]


def main():
    v = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "preuve_image.quantification et .telemetrie (paquet Python)",
        "avertissement": (
            "Fichier généré. Ne pas modifier à la main : il est la référence "
            "contre laquelle le port TypeScript est vérifié."
        ),
        "motif_aucune_signature": MOTIF_AUCUNE_SIGNATURE,
        "motif_station_sol": MOTIF_STATION_SOL_ABSENTE,
        "avertissement_altitude": AVERTISSEMENT_ALTITUDE_RELATIVE,
        "table_annexe_k": list(TABLE_LUMINANCE_ANNEXE_K),
        # Les deux branches de l'algorithme, plus les bornes.
        "tables_ijg": [{"qualite": q, "table": list(table_ijg(q))}
                       for q in (1, 2, 10, 25, 49, 50, 51, 75, 90, 99, 100)],
        "qualites_estimees": [],
        "jpeg": [],
        "refus_jpeg": [],
        "xmp": [],
    }

    # L'estimation sur des tables volontairement décalées : c'est l'ÉCART qui
    # est épinglé, autant que la qualité.
    for decalage in (0, 1, 3, 20):
        valeurs = tuple(min(255, x + decalage) for x in TABLE_LUMINANCE_ANNEXE_K)
        q, e = qualite_ijg_estimee(valeurs)
        v["qualites_estimees"].append(
            {"decalage": decalage, "valeurs": list(valeurs), "qualite": q, "ecart": e})

    for nom, donnees in CAS_JPEG:
        a = analyser_quantification(donnees)
        v["jpeg"].append({
            "nom": nom,
            "octets_b64": base64.b64encode(donnees).decode("ascii"),
            "empreinte_ensemble": a.empreinte_ensemble,
            "qualite_ijg": a.qualite_ijg,
            "ecart_a_ijg": a.ecart_a_ijg,
            "conforme_ijg": a.conforme_ijg,
            "sous_echantillonnage": a.sous_echantillonnage,
            "progressif": a.progressif,
            "largeur": a.largeur, "hauteur": a.hauteur,
            "composantes": a.composantes,
            "signature": a.signature,
            "marqueurs": list(a.marqueurs),
            "tables": [
                {"identifiant": t.identifiant, "precision_bits": t.precision_bits,
                 "valeurs": list(t.valeurs), "offset": t.offset,
                 "empreinte": t.empreinte, "somme": t.somme}
                for t in a.tables
            ],
        })

    for nom, donnees in REFUS_JPEG:
        try:
            analyser_quantification(donnees)
            sys.exit("le cas de refus « %s » n'a pas levé côté Python" % nom)
        except Exception as exc:  # noqa: BLE001
            v["refus_jpeg"].append({
                "nom": nom,
                "octets_b64": base64.b64encode(donnees).decode("ascii"),
                "message_python": str(exc),
            })

    for nom, paquet in CAS_XMP:
        t = extraire_telemetrie(paquet)
        v["xmp"].append({
            "nom": nom,
            "paquet_b64": base64.b64encode(paquet).decode("ascii"),
            "present": t.present,
            "origine": t.origine,
            "prefixes": list(t.prefixes),
            "latitude_deg": t.latitude_deg,
            "longitude_deg": t.longitude_deg,
            "altitude_absolue_m": t.altitude_absolue_m,
            "altitude_relative_m": t.altitude_relative_m,
            "altitude_sol_m": t.altitude_sol_m,
            "tangage_nacelle_deg": t.tangage_nacelle_deg,
            "lacet_nacelle_deg": t.lacet_nacelle_deg,
            "roulis_nacelle_deg": t.roulis_nacelle_deg,
            "visee_horizontale": t.visee_horizontale,
            "station_sol": t.station_sol,
            "sens": dict(t.sens),
            "champs": [
                {"prefixe": c.prefixe, "nom": c.nom, "brut": c.brut,
                 "valeur": c.valeur, "cle": c.cle}
                for c in t.champs
            ],
        })

    controle(v)

    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(v, f, ensure_ascii=False, indent=2)
        f.write("\n")
    print("Écrit : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d tables IJG, %d estimations, %d JPEG, %d refus, %d paquets XMP"
          % (len(v["tables_ijg"]), len(v["qualites_estimees"]), len(v["jpeg"]),
             len(v["refus_jpeg"]), len(v["xmp"])))
    return 0


def controle(v):
    """Revérifie que les vecteurs épinglent bien ce qu'ils prétendent épingler."""
    par_nom = {c["nom"]: c for c in v["jpeg"]}

    # 1. Les deux branches de l'algorithme IJG sont couvertes. L'échelle change
    #    de formule à 50 : sans cas de part et d'autre, une inversion des deux
    #    branches passerait inaperçue.
    qualites = [t["qualite"] for t in v["tables_ijg"]]
    assert any(q < 50 for q in qualites) and any(q > 50 for q in qualites)
    assert 50 in qualites, "la charnière doit être couverte"

    # 2. La saturation à 255 et le plancher à 1 sont atteints quelque part.
    assert max(max(t["table"]) for t in v["tables_ijg"]) == 255
    assert min(min(t["table"]) for t in v["tables_ijg"]) == 1

    # 3. Au moins un cas n'est PAS conforme IJG. Sans lui, rien ne
    #    distinguerait un lecteur qui rend l'écart d'un lecteur qui le tait.
    non_conformes = [c for c in v["jpeg"] if not c["conforme_ijg"]]
    assert non_conformes, "aucun cas non conforme : l'écart n'est pas éprouvé"
    assert par_nom["tables non conformes IJG"]["ecart_a_ijg"] > 0

    # 4. Des tables différentes donnent des empreintes différentes.
    empreintes = {c["empreinte_ensemble"] for c in v["jpeg"]}
    assert len(empreintes) >= len(v["jpeg"]) - 2, (
        "trop de cas partagent la même empreinte : ils ne discriminent plus"
    )

    # 5. Les trois sous-échantillonnages sont distincts.
    ech = {par_nom[f"sous-échantillonnage {n}"]["sous_echantillonnage"]
           for n in ("4:4:4", "4:2:2", "4:2:0")}
    assert ech == {"4:4:4", "4:2:2", "4:2:0"}

    # 6. La précision 16 bits est réellement présente.
    assert par_nom["précision 16 bits"]["tables"][0]["precision_bits"] == 16

    # 7. Le registre de signatures est vide, et aucun cas n'en porte.
    assert all(c["signature"] is None for c in v["jpeg"])

    # 8. Le cas DJI porte l'orthographe fautive ET ELLE SEULE, sinon le test de
    #    l'orthographe ne prouve rien.
    dji = base64.b64decode(
        next(c for c in v["xmp"] if c["nom"] == "DJI, forme attribut")["paquet_b64"])
    assert b"GpsLongtitude" in dji and b"GpsLongitude=" not in dji

    # 9. Le tangage absent donne None, jamais un booléen.
    absent = next(c for c in v["xmp"] if c["nom"] == "tangage absent")
    assert absent["tangage_nacelle_deg"] is None
    assert absent["visee_horizontale"] is None

    # 10. Les deux formes d'écriture XMP donnent chacune des champs.
    for nom in ("DJI, forme attribut", "Parrot, forme élément"):
        c = next(x for x in v["xmp"] if x["nom"] == nom)
        assert c["present"] is True and c["champs"], nom

    # 11. La station sol n'est jamais renseignée.
    assert all(c["station_sol"] is None for c in v["xmp"])

    # 12. Les trois cas ajoutés après coup discriminent bien ce pour quoi ils
    #     existent : sans eux, trois ruptures délibérées du port passaient.
    gris = par_nom["niveaux de gris (une composante)"]
    assert gris["composantes"] == 1
    assert gris["sous_echantillonnage"] is None, (
        "le cas à une composante rend une notation « 4:x:x » : il ne discrimine plus"
    )
    seul = next(c for c in v["xmp"] if c["nom"] == "Camera seul, sans constructeur")
    assert seul["present"] is True and seul["origine"] is None, (
        "le cas « Camera seul » attribue une origine : il ne discrimine plus"
    )
    assert "Camera" in seul["prefixes"]
    fusion = next(c for c in v["xmp"] if c["nom"] == "DJI et Parrot fusionnés")
    valeurs = {c["nom"]: c["valeur"] for c in fusion["champs"]}
    assert "GimbalPitchDegree" in valeurs and "Pitch" in valeurs, (
        "le cas fusionné ne porte pas les deux champs de tangage"
    )
    assert valeurs["GimbalPitchDegree"] != valeurs["Pitch"], (
        "les deux tangages sont égaux : l'ordre de priorité redevient inobservable"
    )
    assert fusion["tangage_nacelle_deg"] == valeurs["GimbalPitchDegree"]

    print("  12 contrôles passés avant écriture.")


if __name__ == "__main__":
    sys.exit(main())
