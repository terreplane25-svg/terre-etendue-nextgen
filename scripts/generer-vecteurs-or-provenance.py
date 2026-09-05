#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Vecteurs d'or du module d'ingestion : EXIF étendu, C2PA, XMP, IPTC, chaînes.

Pourquoi ce fichier existe
──────────────────────────
L'ingestion tourne dans le navigateur — le fichier de l'opérateur ne doit pas
en sortir — donc en TypeScript, alors que la référence testée est le paquet
Python `preuve_image` (outil B). Deux implémentations de la même formule, c'est
le défaut que ce dépôt passe son temps à corriger.

Ce script fait produire au Python un jeu de cas couvrant chaque lecteur porté,
et `scripts/verifier-port-provenance.mjs` refait les mêmes lectures en
TypeScript et compare.

Ce qui est couvert
──────────────────
  · CBOR : les vecteurs de l'annexe A de la RFC 8949, une référence extérieure ;
  · JUMBF : boîte simple, superboîte étiquetée, taille étendue, taille nulle,
    boîte tronquée ;
  · C2PA : manifeste complet, fragments APP11 recollés, fragments en désordre,
    conteneur PNG, absence de manifeste ;
  · XMP et IPTC : champs relevés, libellés IIM ;
  · chaînes : ASCII, UTF-16LE, arrêt au SOS, marqueurs logiciels ;
  · EXIF étendu : miniature de l'IFD1, DPI, champs codés et leurs libellés.

Les fichiers d'essai sont fabriqués ici, en octets, à partir des structures des
normes. Ils sont écrits dans le fichier de vecteurs en hexadécimal, pour que le
TypeScript lise EXACTEMENT les mêmes octets que le Python — sans quoi la
comparaison ne prouverait rien.

    python3 scripts/generer-vecteurs-or-provenance.py
"""
import json
import os
import struct
import sys
from datetime import datetime, timezone
from io import BytesIO

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENV = os.path.join(RACINE, "outils", ".venv", "bin", "python")
CIBLE = os.path.join(RACINE, "src", "lib", "preuve-image", "vecteurs-or-provenance.json")

if "preuve_image" not in sys.modules:
    try:
        import preuve_image  # noqa: F401
    except ImportError:
        if not os.path.exists(VENV):
            sys.exit("venv des outils absent : %s" % VENV)
        os.execv(VENV, [VENV, os.path.abspath(__file__)] + sys.argv[1:])

from PIL import Image  # noqa: E402
from PIL.TiffImagePlugin import IFDRational  # noqa: E402

from preuve_image.metadata import (  # noqa: E402
    _dpi,
    decrire_flash,
    lire_exif_depuis_jpeg,
    lire_exif_depuis_tiff,
)
from preuve_image.document import (  # noqa: E402
    MOTIF_SIGNATURE_NON_VERIFIEE,
    dimensions_jpeg,
    document_ingestion,
    horodatage_iso,
    vitesse_obturation,
)
from preuve_image.provenance import (  # noqa: E402
    AVERTISSEMENT_C2PA,
    MARQUEURS_LOGICIELS,
    analyser_boites_jumbf,
    analyser_provenance,
    decoder_cbor,
    extraire_c2pa,
    extraire_chaines,
    extraire_iptc,
    extraire_xmp,
)

# Les fixtures sont celles des tests : une seule définition, pour qu'un vecteur
# et un test ne puissent pas diverger.
sys.path.insert(0, os.path.join(RACINE, "outils", "outil-B-preuve-image", "tests"))
from test_provenance import (  # noqa: E402
    VECTEURS_RFC8949,
    XMP_EXEMPLE,
    boite,
    dataset_iim,
    jpeg_avec_app11,
    jpeg_avec_iptc,
    jpeg_avec_xmp,
    jpeg_avec_xmp_etendu,
    manifeste_c2pa_synthetique,
    superboite,
)
from test_metadata_ingestion import MINIATURE_JPEG, tiff_avec_miniature  # noqa: E402


def hexa(b: bytes) -> str:
    return b.hex()


def jsonable(v):
    """Rend une valeur comparable en JSON, en conservant la nature des octets."""
    if isinstance(v, bytes):
        return {"_octets_hex": v.hex()}
    if isinstance(v, dict):
        return {str(k): jsonable(x) for k, x in v.items()}
    if isinstance(v, (list, tuple)):
        return [jsonable(x) for x in v]
    return v


def vecteurs_cbor():
    return [
        {"hex": h, "valeur": jsonable(decoder_cbor(bytes.fromhex(h)))}
        for h, _ in VECTEURS_RFC8949
    ]


def vecteurs_jumbf():
    cas = [
        ("boîte simple", boite(b"cbor", b"\x01\x02")),
        ("superboîte étiquetée", superboite("c2pa.actions", boite(b"cbor", b"\x00"))),
        ("taille étendue (LBox = 1)",
         struct.pack(">I", 1) + b"cbor" + struct.pack(">Q", 18) + b"xy"),
        ("taille nulle (LBox = 0, court jusqu'à la fin)",
         struct.pack(">I", 0) + b"cbor" + b"abcdef"),
        ("boîte tronquée après une bonne",
         boite(b"cbor", b"\x01") + struct.pack(">I", 9999) + b"cbor" + b"\x02"),
    ]
    out = []
    for nom, brut in cas:
        boites = analyser_boites_jumbf(brut)
        out.append({
            "nom": nom,
            "hex": hexa(brut),
            "boites": [
                {
                    "type": b.type_, "taille": b.taille, "offset": b.offset,
                    "label": b.label, "uuid_type": b.uuid_type,
                    "charge_hex": hexa(b.charge), "nb_filles": len(b.filles),
                }
                for b in boites
            ],
        })
    return out


def _c2pa_en_dict(r):
    return {
        "present": r.present,
        "conteneur": r.conteneur,
        "octets": r.octets,
        "signature_verifiee": r.signature_verifiee,
        "avertissement": r.avertissement,
        "motif_non_verifiee": r.motif_non_verifiee,
        "boites": list(r.boites),
        "manifestes": [
            {
                "label": m.label,
                "generateur": m.generateur,
                "algorithme_signature": m.algorithme_signature,
                "signature_presente": m.signature_presente,
                "assertions": sorted(m.assertions),
                "actions": jsonable(m.actions),
                "revendication": jsonable(m.revendication),
            }
            for m in r.manifestes
        ],
    }


def vecteurs_c2pa():
    magasin = manifeste_c2pa_synthetique()

    fragments = [magasin[i : i + 50] for i in range(0, len(magasin), 50)]
    segments = []
    for numero, fragment in enumerate(fragments, start=1):
        corps = b"JP" + struct.pack(">H", 1) + struct.pack(">I", numero) + fragment
        segments.append(b"\xff\xeb" + struct.pack(">H", len(corps) + 2) + corps)
    segments.reverse()
    desordre = b"\xff\xd8" + b"".join(segments) + b"\xff\xda\x00\x02\xff\xd9"

    png = (b"\x89PNG\r\n\x1a\n"
           + struct.pack(">I", len(magasin)) + b"caBX" + magasin + b"\x00\x00\x00\x00"
           + struct.pack(">I", 0) + b"IEND" + b"\x00\x00\x00\x00")

    cas = [
        ("manifeste complet, un seul segment", jpeg_avec_app11(magasin)),
        ("fragments de 40 octets, recollés", jpeg_avec_app11(magasin, taille_fragment=40)),
        ("fragments en désordre", desordre),
        ("conteneur PNG caBX", png),
        ("aucun manifeste", b"\xff\xd8\xff\xda\x00\x02\xff\xd9"),
        ("conteneur tronqué", jpeg_avec_app11(magasin[: len(magasin) // 2])),
    ]
    return [
        {"nom": nom, "hex": hexa(d), "resultat": _c2pa_en_dict(extraire_c2pa(d))}
        for nom, d in cas
    ]


def vecteurs_xmp():
    png_charge = b"XML:com.adobe.xmp\x00\x00\x00\x00\x00" + XMP_EXEMPLE.encode()
    png = (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(png_charge)) + b"iTXt" + png_charge
           + b"\x00\x00\x00\x00" + struct.pack(">I", 0) + b"IEND\x00\x00\x00\x00")
    cas = [
        ("XMP dans un JPEG", jpeg_avec_xmp(XMP_EXEMPLE)),
        ("XMP étendu, en-tête de 40 octets", jpeg_avec_xmp_etendu(XMP_EXEMPLE)),
        ("XMP dans un PNG", png),
        ("aucun XMP", b"\xff\xd8\xff\xda\x00\x02\xff\xd9"),
    ]
    out = []
    for nom, d in cas:
        out.append({
            "nom": nom, "hex": hexa(d),
            "blocs": [
                {"conteneur": b.conteneur, "octets": b.octets, "etendu": b.etendu,
                 "champs": dict(b.champs),
                 # Le début du paquet : c'est lui qui change si l'en-tête de
                 # 40 octets du XMP étendu n'est pas retiré. Les champs, eux,
                 # restent trouvables — la comparaison passerait à côté.
                 "debut": b.brut[:24]}
                for b in extraire_xmp(d)
            ],
        })
    return out


def vecteurs_iptc():
    datasets = (dataset_iim(80, "A. Photographe")
                + dataset_iim(120, "Vue de la digue au lever du jour")
                + dataset_iim(115, "Agence d'essai")
                + dataset_iim(199, "champ inconnu"))
    cas = [
        ("trois champs connus et un inconnu", jpeg_avec_iptc(datasets)),
        ("aucun IPTC", b"\xff\xd8\xff\xda\x00\x02\xff\xd9"),
    ]
    return [
        {
            "nom": nom, "hex": hexa(d),
            "enregistrements": [
                {"jeu": e.jeu, "numero": e.numero, "libelle": e.libelle, "valeur": e.valeur}
                for e in extraire_iptc(d)
            ],
        }
        for nom, d in cas
    ]


def vecteurs_chaines():
    cas = [
        ("JPEG avec XMP Photoshop", jpeg_avec_xmp(XMP_EXEMPLE)),
        ("UTF-16LE dans l'en-tête",
         b"\xff\xd8" + "Marqueur cache".encode("utf-16-le") + b"\xff\xda\x00\x02\xff\xd9"),
        ("texte après le SOS, à ne pas relever",
         b"\xff\xd8\xff\xda\x00\x02" + b"CHAINE_APRES_LE_SOS_A_NE_PAS_RELEVER" + b"\xff\xd9"),
        ("doublons", b"\xff\xd8" + b"RepeteRepete " * 5 + b"\xff\xda\x00\x02\xff\xd9"),
    ]
    return [
        {
            "nom": nom, "hex": hexa(d),
            "chaines": [
                {"offset": c.offset, "encodage": c.encodage, "texte": c.texte,
                 "marqueur": c.marqueur}
                for c in extraire_chaines(d)
            ],
            "marqueurs_logiciels": list(analyser_provenance(d).marqueurs_logiciels),
        }
        for nom, d in cas
    ]


def jpeg_exif_complet() -> bytes:
    img = Image.new("RGB", (64, 48), (20, 30, 40))
    exif = Image.Exif()
    exif[0x010F] = "EssaiCorp"
    exif[0x0110] = "Modele X"
    exif[0x0131] = "Retoucheur 2.4"
    exif[0x0132] = "2026:09:05 11:02:33"
    exif[0x013B] = "A. Photographe"
    exif[0x8298] = "Tous droits reserves"
    exif[0x011A] = IFDRational(300, 1)
    exif[0x011B] = IFDRational(300, 1)
    exif[0x0128] = 2
    exif[0x0100] = 64
    exif[0x0101] = 48
    sous = exif.get_ifd(0x8769)
    sous[0x9003] = "2026:09:05 10:14:22"
    sous[0x9004] = "2026:09:05 10:14:25"
    sous[0x8822] = 2
    sous[0x9209] = 0x19
    sous[0xA001] = 1
    sous[0xA402] = 1
    sous[0xA403] = 0
    sous[0xA404] = IFDRational(2, 1)
    sous[0xA406] = 1
    sous[0x8827] = 200
    sous[0x829D] = IFDRational(28, 10)
    sous[0x829A] = IFDRational(1, 250)
    sous[0x920A] = IFDRational(24, 1)
    sous[0xA405] = 36
    sous[0xA002] = 64
    sous[0xA003] = 48
    tampon = BytesIO()
    img.save(tampon, format="JPEG", exif=exif)
    return tampon.getvalue()


def _exif_en_dict(e):
    m = e.miniature
    return {
        "fabricant": e.fabricant, "modele": e.modele, "logiciel": e.logiciel,
        "artiste": e.artiste, "droits": e.droits,
        "date_heure_original": e.date_heure_original,
        "date_heure_modification": e.date_heure_modification,
        "date_heure_numerisation": e.date_heure_numerisation,
        "sensibilite_iso": e.sensibilite_iso, "ouverture": e.ouverture,
        "temps_pose_s": e.temps_pose_s, "focale_mm": e.focale_mm,
        "focale_equivalente_35mm": e.focale_equivalente_35mm,
        "largeur_px": e.largeur_px, "hauteur_px": e.hauteur_px,
        "largeur_ifd0_px": e.largeur_ifd0_px, "hauteur_ifd0_px": e.hauteur_ifd0_px,
        "resolution_x": e.resolution_x, "resolution_y": e.resolution_y,
        "unite_resolution": e.unite_resolution, "dpi_x": e.dpi_x, "dpi_y": e.dpi_y,
        "espace_colorimetrique": e.espace_colorimetrique,
        "mode_exposition": e.mode_exposition,
        "programme_exposition": e.programme_exposition,
        "balance_blancs": e.balance_blancs,
        "rapport_zoom_numerique": e.rapport_zoom_numerique,
        "type_scene": e.type_scene, "flash": e.flash,
        "libelles": {
            "flash": e.flash_libelle,
            "mode_exposition": e.mode_exposition_libelle,
            "programme_exposition": e.programme_exposition_libelle,
            "balance_blancs": e.balance_blancs_libelle,
            "espace_colorimetrique": e.espace_colorimetrique_libelle,
            "type_scene": e.type_scene_libelle,
            "unite_resolution": e.unite_resolution_libelle,
        },
        "zoom_numerique_applique": e.zoom_numerique_applique,
        "miniature": None if m is None else {
            "offset": m.offset, "longueur": m.longueur,
            "compression": m.compression, "est_jpeg": m.est_jpeg,
            "octets_hex": hexa(m.octets),
        },
    }


def vecteurs_exif():
    img_nue = Image.new("RGB", (8, 8))
    tampon = BytesIO()
    exif_nu = Image.Exif()
    exif_nu[0x010F] = "Nu"
    img_nue.save(tampon, format="JPEG", exif=exif_nu)

    return {
        "jpeg": [
            {"nom": "JPEG complet", "hex": hexa(jpeg_exif_complet()),
             "exif": _exif_en_dict(lire_exif_depuis_jpeg(jpeg_exif_complet()))},
            {"nom": "JPEG sans champs étendus", "hex": hexa(tampon.getvalue()),
             "exif": _exif_en_dict(lire_exif_depuis_jpeg(tampon.getvalue()))},
        ],
        "tiff": [
            {"nom": "TIFF avec miniature IFD1", "hex": hexa(tiff_avec_miniature()),
             "exif": _exif_en_dict(lire_exif_depuis_tiff(tiff_avec_miniature()))},
            {"nom": "TIFF, offset de miniature incohérent",
             "hex": hexa(tiff_avec_miniature(offset_faux=True)),
             "exif": _exif_en_dict(lire_exif_depuis_tiff(tiff_avec_miniature(offset_faux=True)))},
        ],
        "flash": [{"code": c, "libelle": decrire_flash(c)}
                  for c in (0x00, 0x01, 0x05, 0x07, 0x09, 0x10, 0x19, 0x20, 0x41)],
        "dpi": [{"resolution": r, "unite": u, "dpi": _dpi(r, u)}
                for r, u in ((300.0, 2), (300.0, 3), (72.0, 1), (0.0, 2))],
    }


def vecteurs_document():
    """Le document d'ingestion, sur des fichiers qui exercent les quatre écarts."""
    from test_document import jpeg, jpeg_avec_c2pa  # noqa: E402

    cas = [
        ("JPEG complet, sans décalage horaire déclaré", jpeg()),
        ("JPEG avec OffsetTimeOriginal", jpeg(avec_offset=True)),
        ("JPEG à résolutions anisotropes", jpeg(resolution=(300, 150))),
        ("JPEG à unité de résolution « sans dimension »", jpeg(unite=1)),
        ("JPEG avec manifeste C2PA", jpeg_avec_c2pa()),
        ("fichier sans EXIF", b"\xff\xd8\xff\xda\x00\x02\xff\xd9"),
    ]
    return {
        "cas": [
            {"nom": nom, "hex": hexa(d),
             "document": jsonable(document_ingestion(d, nom_fichier="essai.jpg"))}
            for nom, d in cas
        ],
        "dimensions_jpeg": [
            {"nom": "1024×576", "hex": hexa(jpeg(1024, 576)),
             "dimensions": list(dimensions_jpeg(jpeg(1024, 576)))},
            {"nom": "320×240", "hex": hexa(jpeg(320, 240)),
             "dimensions": list(dimensions_jpeg(jpeg(320, 240)))},
            {"nom": "pas un JPEG", "hex": hexa(b"pas un jpeg"), "dimensions": None},
        ],
        "vitesse_obturation": [
            {"secondes": s, "texte": vitesse_obturation(s)}
            # 0,0049 s et 1/3 s : des inverses NON entiers. Un vrai boîtier écrit
            # des valeurs dérivées de l'échelle APEX, qui ne tombent pas rond.
            # Sans elles, une erreur d'arrondi passait inaperçue.
            for s in (1 / 200, 1 / 60, 0.5, 1.0, 2.5, 30.0, 0.0, 0.0049, 1 / 3, 1.7)
        ],
        "horodatage": [
            {"exif": e, "decalage": d, "resultat": horodatage_iso(e, d)}
            for e, d in (
                ("2014:07:31 18:05:43", None),
                ("2014:07:31 18:05:43", "+02:00"),
                ("2014:07:31 18:05:43", "-05:00"),
                (None, None),
                ("", "+02:00"),
            )
        ],
        "motif_signature": MOTIF_SIGNATURE_NON_VERIFIEE,
    }


def controle(doc):
    """Recalcule ce qui vient d'être écrit, par des identités que le code ne peut
    pas satisfaire par accident."""
    # 1. Les vecteurs CBOR sont exactement ceux de la RFC : même nombre.
    assert len(doc["cbor"]) == len(VECTEURS_RFC8949)

    # 2. Le manifeste complet et les fragments recollés donnent le MÊME résultat.
    complet = next(c for c in doc["c2pa"] if c["nom"].startswith("manifeste complet"))
    recolle = next(c for c in doc["c2pa"] if c["nom"].startswith("fragments de 40"))
    desordre = next(c for c in doc["c2pa"] if c["nom"] == "fragments en désordre")
    for autre in (recolle, desordre):
        assert autre["resultat"]["manifestes"] == complet["resultat"]["manifestes"], autre["nom"]
        assert autre["resultat"]["octets"] == complet["resultat"]["octets"], autre["nom"]

    # 3. Aucun résultat C2PA ne se déclare vérifié, jamais.
    for c in doc["c2pa"]:
        assert c["resultat"]["signature_verifiee"] is False
        assert c["resultat"]["avertissement"] == AVERTISSEMENT_C2PA

    # 4. Le texte placé après le SOS n'est jamais relevé.
    apres_sos = next(c for c in doc["chaines"] if "après le SOS" in c["nom"])
    assert not any("A_NE_PAS_RELEVER" in x["texte"] for x in apres_sos["chaines"])

    # 5. Les chaînes n'ont pas de doublon.
    for c in doc["chaines"]:
        textes = [x["texte"] for x in c["chaines"]]
        assert len(textes) == len(set(textes)), c["nom"]

    # 6. La miniature déclarée est bien celle qu'on a écrite.
    avec = next(t for t in doc["exif"]["tiff"] if "avec miniature" in t["nom"])
    assert avec["exif"]["miniature"]["octets_hex"] == MINIATURE_JPEG.hex()
    sans = next(t for t in doc["exif"]["tiff"] if "incohérent" in t["nom"])
    assert sans["exif"]["miniature"] is None

    # 7. Le DPI n'est calculé que pour les unités qui en définissent un.
    for d in doc["exif"]["dpi"]:
        if d["unite"] == 1 or d["resolution"] == 0.0:
            assert d["dpi"] is None
        else:
            assert d["dpi"] is not None

    # 8. Un code de flash sans éclair possible n'est pas « non déclenché ».
    sans_flash = next(f for f in doc["exif"]["flash"] if f["code"] == 0x20)
    assert sans_flash["libelle"] == "l'appareil n'a pas de flash"

    # 9bis. Le XMP étendu a bien perdu son en-tête : les champs sont relevés.
    etendu = next(x for x in doc["xmp"] if "étendu" in x["nom"])
    assert etendu["blocs"][0]["etendu"] is True
    assert etendu["blocs"][0]["champs"].get("tiff:Make") == "EssaiCorp"

    # 9. Le JPEG sans champs étendus n'en invente aucun.
    nu = next(j for j in doc["exif"]["jpeg"] if "sans champs" in j["nom"])
    for champ in ("logiciel", "flash", "espace_colorimetrique", "dpi_x", "miniature"):
        assert nu["exif"][champ] is None, champ

    # 10. L'horodatage ne porte un fuseau que si le fichier en déclare un.
    for h in doc["document"]["horodatage"]:
        r = h["resultat"]
        if h["decalage"] and h["exif"]:
            assert r["offset_declare"] is True and r["valeur"].endswith(h["decalage"])
        else:
            assert r["offset_declare"] is False
            assert r["valeur"] is None or ("+" not in r["valeur"] and not r["valeur"].endswith("Z"))

    # 11. Aucune tournure affirmative d'authenticité dans le document entier.
    texte = json.dumps(doc["document"], ensure_ascii=False).lower()
    for affirmation in ("est authentique", "signature valide", "provenance vérifiée",
                        "authenticité confirmée", "certifié conforme"):
        assert affirmation not in texte, affirmation

    # 12. `dpi` scalaire seulement quand les deux axes coïncident.
    for c in doc["document"]["cas"]:
        fi = c["document"]["file_info"]
        if fi["dpi"] is not None:
            assert fi["dpi_x"] == fi["dpi_y"] == fi["dpi"], c["nom"]

    # 13. `verified` est faux partout, sans exception.
    for c in doc["document"]["cas"]:
        assert c["document"]["c2pa"]["verified"] is False, c["nom"]

    return 13


def main():
    doc = {
        "genere_le": datetime.now(timezone.utc).isoformat(),
        "source": "outils/outil-B-preuve-image (paquet Python preuve_image)",
        "avertissement": (
            "Fichier produit par scripts/generer-vecteurs-or-provenance.py. "
            "Ne pas éditer à la main : il n'aurait plus de valeur d'épinglage. "
            "Corriger le Python, puis régénérer."
        ),
        "avertissement_c2pa": AVERTISSEMENT_C2PA,
        "marqueurs_logiciels": list(MARQUEURS_LOGICIELS),
        "cbor": vecteurs_cbor(),
        "jumbf": vecteurs_jumbf(),
        "c2pa": vecteurs_c2pa(),
        "xmp": vecteurs_xmp(),
        "iptc": vecteurs_iptc(),
        "chaines": vecteurs_chaines(),
        "exif": vecteurs_exif(),
        "document": vecteurs_document(),
    }
    n = controle(doc)
    os.makedirs(os.path.dirname(CIBLE), exist_ok=True)
    with open(CIBLE, "w", encoding="utf-8") as f:
        json.dump(doc, f, ensure_ascii=False, indent=1)
        f.write("\n")
    total = (len(doc["cbor"]) + len(doc["jumbf"]) + len(doc["c2pa"]) + len(doc["xmp"])
             + len(doc["iptc"]) + len(doc["chaines"]) + len(doc["document"]["cas"])
             + len(doc["exif"]["jpeg"]) + len(doc["exif"]["tiff"])
             + len(doc["exif"]["flash"]) + len(doc["exif"]["dpi"]))
    print("Vecteurs écrits : %s" % os.path.relpath(CIBLE, RACINE))
    print("  %d cas — %d CBOR, %d JUMBF, %d C2PA, %d XMP, %d IPTC, %d chaînes, %d EXIF"
          % (total, len(doc["cbor"]), len(doc["jumbf"]), len(doc["c2pa"]), len(doc["xmp"]),
             len(doc["iptc"]), len(doc["chaines"]),
             len(doc["exif"]["jpeg"]) + len(doc["exif"]["tiff"])
             + len(doc["exif"]["flash"]) + len(doc["exif"]["dpi"])))
    print("  %d familles d'identités revérifiées avant écriture." % n)
    return 0


if __name__ == "__main__":
    sys.exit(main())
