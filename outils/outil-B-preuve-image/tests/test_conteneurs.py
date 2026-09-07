"""
Les conteneurs hors EXIF : PNG, WebP, GIF, BMP, SVG, et le profil ICC.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que chaque format est parcouru selon sa structure publiée, que les blocs
documentés sont décodés et les autres seulement listés, et surtout que ce qui
est ABSENT le reste : un texte compressé illisible ne devient pas une chaîne
vide silencieuse, un CRC faux est signalé, un format non couvert est refusé en
le disant plutôt que rendu comme un inventaire vide.

Les fichiers sont fabriqués ici. Pillow sert à produire des images réelles là
où c'est utile (PNG, GIF, BMP) ; les blocs de métadonnées sont écrits à la
main, parce que c'est eux qu'on teste et qu'une bibliothèque tierce les
écrirait selon SA lecture de la norme, pas selon la norme.
"""

import binascii
import struct
import zlib
from io import BytesIO

import pytest
from PIL import Image

from preuve_image.conteneurs import (
    ConteneurError,
    inventorier,
    lire_profil_icc,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fabrication
# ─────────────────────────────────────────────────────────────────────────────


def chunk_png(type_: bytes, charge: bytes, crc_faux: bool = False) -> bytes:
    crc = binascii.crc32(type_ + charge) & 0xFFFFFFFF
    if crc_faux:
        crc ^= 0xFFFFFFFF
    return struct.pack(">I", len(charge)) + type_ + charge + struct.pack(">I", crc)


def profil_icc(description="Display P3", classe=b"mntr", espace=b"RGB ") -> bytes:
    """Un profil ICC minimal mais conforme : en-tête de 128 octets + un tag `desc`."""
    desc = description.encode("ascii")
    # Tag `desc` en forme v2 : type(4) + réservé(4) + longueur(4) + texte + NUL
    tag_desc = b"desc" + b"\x00" * 4 + struct.pack(">I", len(desc) + 1) + desc + b"\x00"
    tag_desc += b"\x00" * ((4 - len(tag_desc) % 4) % 4)

    nb_tags = 1
    offset_tag = 132 + nb_tags * 12
    taille = offset_tag + len(tag_desc)

    entete = bytearray(128)
    entete[0:4] = struct.pack(">I", taille)
    entete[8:10] = bytes([2, 0x40])          # version 2.4
    entete[12:16] = classe
    entete[16:20] = espace
    entete[20:24] = b"XYZ "                   # espace de connexion
    entete[24:36] = struct.pack(">6H", 2026, 5, 12, 14, 22, 10)
    entete[36:40] = b"acsp"
    entete[40:44] = b"APPL"
    entete[80:84] = b"ESSA"
    return (bytes(entete)
            + struct.pack(">I", nb_tags)
            + b"desc" + struct.pack(">II", offset_tag, len(tag_desc))
            + tag_desc)


def png(avec_textes=True, avec_icc=True, crc_faux=False, animation=False) -> bytes:
    """Un PNG réel de Pillow, auquel on ajoute les chunks qu'on veut tester."""
    t = BytesIO()
    Image.new("RGB", (64, 48), (20, 90, 140)).save(t, format="PNG")
    brut = t.getvalue()
    # On insère nos chunks juste après l'IHDR, avant les IDAT.
    fin_ihdr = 8 + 25  # signature + IHDR complet (13 octets de charge)
    ajouts = b""
    if avec_textes:
        ajouts += chunk_png(b"tEXt", b"Software\x00EssaiCorp Editeur 3.1")
        ajouts += chunk_png(b"zTXt", b"Comment\x00\x00" + zlib.compress(
            "Texte compressé : invisible à une recherche de chaînes.".encode("latin-1")))
        ajouts += chunk_png(b"iTXt", b"Description\x00\x01\x00fr\x00Description\x00"
                            + zlib.compress("Un commentaire international.".encode("utf-8")))
    ajouts += chunk_png(b"pHYs", struct.pack(">IIB", 11811, 11811, 1))  # 300 DPI
    ajouts += chunk_png(b"tIME", struct.pack(">HBBBBB", 2026, 5, 12, 14, 22, 10))
    if avec_icc:
        ajouts += chunk_png(b"iCCP", b"Display P3\x00\x00" + zlib.compress(profil_icc()),
                            crc_faux=crc_faux)
    if animation:
        ajouts += chunk_png(b"acTL", struct.pack(">II", 7, 3))
    return brut[:fin_ihdr] + ajouts + brut[fin_ihdr:]


def morceau_riff(type_: bytes, charge: bytes) -> bytes:
    bloc = type_ + struct.pack("<I", len(charge)) + charge
    return bloc + (b"\x00" if len(charge) & 1 else b"")


def webp(avec_exif=True, avec_xmp=True, avec_icc=True, animation=False) -> bytes:
    """Un WebP étendu (VP8X), qui est la seule forme portant des métadonnées."""
    drapeaux = 0
    if avec_icc:
        drapeaux |= 0x20
    if avec_exif:
        drapeaux |= 0x08
    if avec_xmp:
        drapeaux |= 0x04
    if animation:
        drapeaux |= 0x02
    vp8x = struct.pack("<B", drapeaux) + b"\x00\x00\x00"
    vp8x += (1279).to_bytes(3, "little") + (959).to_bytes(3, "little")  # 1280×960

    corps = morceau_riff(b"VP8X", vp8x)
    if avec_icc:
        corps += morceau_riff(b"ICCP", profil_icc())
    if animation:
        corps += morceau_riff(b"ANIM", b"\x00\x00\x00\x00" + struct.pack("<H", 5))
        corps += morceau_riff(b"ANMF", b"\x00" * 17)
        corps += morceau_riff(b"ANMF", b"\x00" * 17)
    corps += morceau_riff(b"VP8 ", b"\x00" * 20)
    if avec_exif:
        corps += morceau_riff(b"EXIF", b"Exif\x00\x00" + b"II*\x00" + b"\x08\x00\x00\x00"
                              + struct.pack("<H", 0) + b"\x00\x00\x00\x00")
    if avec_xmp:
        corps += morceau_riff(b"XMP ", b'<x:xmpmeta xmlns:x="adobe:ns:meta/"></x:xmpmeta>')
    return b"RIFF" + struct.pack("<I", 4 + len(corps)) + b"WEBP" + corps


def gif(animation=False, avec_commentaire=True) -> bytes:
    """Un GIF réel de Pillow, plus une extension de commentaire."""
    t = BytesIO()
    # Les trames doivent être RÉELLEMENT différentes : Pillow déduplique les
    # trames identiques, et un premier essai avec trois images unies n'en
    # écrivait qu'une — le test comptait alors une animation absente, sans
    # rien signaler. On dessine donc un carré à une position distincte.
    images = []
    for i in range(3 if animation else 1):
        im = Image.new("P", (32, 24), 0)
        im.putpixel((2 + i * 8, 5 + i * 3), 1)
        im.putpixel((3 + i * 8, 6 + i * 3), 2)
        images.append(im)
    images[0].save(t, format="GIF", save_all=animation,
                   append_images=images[1:] if animation else [], loop=4)
    brut = bytearray(t.getvalue())
    if avec_commentaire:
        texte = b"Produit par EssaiCorp"
        ext = b"\x21\xfe" + bytes([len(texte)]) + texte + b"\x00"
        # Juste avant le terminateur final.
        brut = brut[:-1] + ext + brut[-1:]
    return bytes(brut)


def bmp() -> bytes:
    t = BytesIO()
    Image.new("RGB", (40, 30), (200, 40, 60)).save(t, format="BMP")
    return t.getvalue()


SVG = b"""<?xml version="1.0" encoding="UTF-8"?>
<!-- Generator: EssaiCorp Dessin 12.0, SVG Export Plug-In -->
<svg xmlns="http://www.w3.org/2000/svg" xmlns:inkscape="http://www.inkscape.org/namespaces/inkscape"
     width="800" height="600" viewBox="0 0 800 600">
  <title>Schema d'essai</title>
  <desc>Une description lisible en clair.</desc>
  <metadata><rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#"></rdf:RDF></metadata>
  <rect width="800" height="600" fill="#123456"/>
</svg>
"""


# ─────────────────────────────────────────────────────────────────────────────
# ICC
# ─────────────────────────────────────────────────────────────────────────────


def test_profil_icc_lu():
    """C'est la description qui porte le nom lisible : « Display P3 »."""
    p = lire_profil_icc(profil_icc())
    assert p.description == "Display P3"
    assert p.version == "2.4"
    assert p.classe == "mntr"
    assert p.classe_libelle == "périphérique d'affichage (écran)"
    assert p.espace == "RGB "
    assert p.espace_libelle == "RVB"
    assert p.espace_connexion == "XYZ "
    assert p.plateforme == "APPL"
    assert p.date == "2026-05-12T14:22:10"


def test_profil_icc_v4_en_utf16():
    """Les profils v4 écrivent la description en UTF-16BE dans un tag `mluc`."""
    desc = "sRGB IEC61966-2.1"
    corps = desc.encode("utf-16-be")
    # mluc : type(4) réservé(4) nb(4) taille_enr(4) langue(2) pays(2) longueur(4) offset(4)
    tag = (b"mluc" + b"\x00" * 4 + struct.pack(">II", 1, 12)
           + b"frFR" + struct.pack(">II", len(corps), 28) + corps)
    offset_tag = 144
    entete = bytearray(128)
    entete[0:4] = struct.pack(">I", offset_tag + len(tag))
    entete[8:10] = bytes([4, 0x30])
    entete[12:16] = b"mntr"
    entete[16:20] = b"RGB "
    donnees = (bytes(entete) + struct.pack(">I", 1)
               + b"desc" + struct.pack(">II", offset_tag, len(tag)) + tag)
    p = lire_profil_icc(donnees)
    assert p.description == desc
    assert p.version == "4.3"


def test_profil_icc_trop_court_refuse():
    with pytest.raises(ConteneurError, match="trop court"):
        lire_profil_icc(b"\x00" * 40)


def test_nombre_de_tags_aberrant_borne():
    """Un profil fabriqué peut annoncer quatre milliards de tags."""
    entete = bytearray(128)
    entete[0:4] = struct.pack(">I", 132)
    donnees = bytes(entete) + struct.pack(">I", 0xFFFFFFFF)
    p = lire_profil_icc(donnees)  # ne doit pas boucler
    assert p.description is None


# ─────────────────────────────────────────────────────────────────────────────
# PNG
# ─────────────────────────────────────────────────────────────────────────────


def test_png_chunks_inventories():
    inv = inventorier(png())
    types = [c.type for c in inv.chunks]
    assert types[0] == "IHDR"
    assert types[-1] == "IEND"
    assert {"tEXt", "zTXt", "iTXt", "pHYs", "tIME", "iCCP", "IDAT"} <= set(types)
    # Chaque chunk documenté porte son rôle ; les autres non — plutôt que de
    # leur en inventer un.
    roles = {c.type: c.role for c in inv.chunks}
    assert roles["iCCP"] == "profil ICC intégré"


def test_png_dimensions_et_profondeur():
    inv = inventorier(png())
    assert (inv.largeur, inv.hauteur) == (64, 48)
    assert inv.profondeur_bits == 8
    assert inv.proprietes["type_couleur_libelle"] == "RVB"


def test_png_resolution_convertie_exactement():
    """11811 pixels par mètre = 300 DPI. La conversion est exacte, pas approchée."""
    inv = inventorier(png())
    assert inv.dpi_x == pytest.approx(300.0, abs=0.02)
    assert inv.dpi_y == pytest.approx(300.0, abs=0.02)
    assert inv.proprietes["unite_physique"] == "mètre"


def test_png_date_de_modification():
    assert inventorier(png()).proprietes["derniere_modification"] == "2026-05-12T14:22:10"


def test_png_texte_non_compresse():
    textes = {t.cle: t for t in inventorier(png()).textes}
    assert textes["Software"].valeur == "EssaiCorp Editeur 3.1"
    assert textes["Software"].compresse is False


def test_png_texte_compresse_est_decompresse_et_signale():
    """Un zTXt échappe à une recherche de chaînes dans le fichier brut.

    C'est pourquoi il est décompressé ET marqué compressé : quelqu'un qui
    aurait inspecté le fichier « à la main » ne l'aurait pas vu, et savoir
    qu'il était caché fait partie du constat.
    """
    brut = png()
    assert b"invisible" not in brut, "le texte devait être compressé dans le fichier"
    textes = {t.cle: t for t in inventorier(brut).textes}
    assert "invisible à une recherche" in textes["Comment"].valeur
    assert textes["Comment"].compresse is True


def test_png_itxt_avec_langue():
    textes = {t.cle: t for t in inventorier(png()).textes}
    assert textes["Description"].langue == "fr"
    assert textes["Description"].valeur == "Un commentaire international."
    assert textes["Description"].compresse is True


def test_png_profil_icc_extrait():
    inv = inventorier(png())
    assert inv.proprietes["nom_profil_icc"] == "Display P3"
    assert inv.profil_icc is not None
    assert inv.profil_icc.description == "Display P3"


def test_png_crc_faux_signale():
    """Un CRC faux dit que les octets ont changé depuis l'écriture du chunk.

    Un CRC juste ne dit rien de plus que « celui qui a modifié le chunk a
    recalculé le CRC » — ce que fait tout éditeur. L'asymétrie est le propos.
    """
    inv = inventorier(png(crc_faux=True))
    assert len(inv.chunks_corrompus) == 1
    assert "iCCP" in inv.chunks_corrompus[0]
    assert any(c.type == "iCCP" and c.crc_valide is False for c in inv.chunks)


def test_png_sain_n_a_aucun_chunk_corrompu():
    assert inventorier(png()).chunks_corrompus == ()


def test_png_animation_apng():
    inv = inventorier(png(animation=True))
    assert inv.proprietes["animation"] is True
    assert inv.proprietes["trames_declarees"] == 7
    assert inv.proprietes["boucles"] == 3


def test_png_chunk_qui_deborde_arrete_sans_inventer():
    brut = bytearray(png(avec_textes=False, avec_icc=False))
    # On fait mentir la longueur du premier chunk après l'IHDR.
    brut[33:37] = struct.pack(">I", 10_000_000)
    inv = inventorier(bytes(brut))
    assert [c.type for c in inv.chunks] == ["IHDR"]


# ─────────────────────────────────────────────────────────────────────────────
# WebP
# ─────────────────────────────────────────────────────────────────────────────


def test_webp_morceaux_et_dimensions():
    inv = inventorier(webp())
    assert inv.format == "WebP"
    assert (inv.largeur, inv.hauteur) == (1280, 960)
    types = [c.type for c in inv.chunks]
    assert types[0] == "VP8X"
    assert {"ICCP", "VP8 ", "EXIF", "XMP "} <= set(types)


def test_webp_drapeaux_vp8x():
    inv = inventorier(webp())
    assert inv.proprietes["icc"] is True
    assert inv.proprietes["exif"] is True
    assert inv.proprietes["xmp"] is True
    assert inv.proprietes["animation"] is False
    nu = inventorier(webp(avec_exif=False, avec_xmp=False, avec_icc=False))
    assert nu.proprietes["exif"] is False
    assert nu.bloc_exif is None
    assert nu.paquets_xmp == ()


def test_webp_exif_rendu_sans_le_prefixe():
    """Certains encodeurs préfixent « Exif » + deux nuls, d'autres non.

    Rendre le préfixe avec le bloc ferait échouer le lecteur TIFF sur un
    en-tête qu'il ne reconnaîtrait pas.
    """
    inv = inventorier(webp())
    assert inv.bloc_exif is not None
    assert inv.bloc_exif[:2] == b"II"


def test_webp_xmp_releve():
    inv = inventorier(webp())
    assert len(inv.paquets_xmp) == 1
    assert b"adobe:ns:meta" in inv.paquets_xmp[0]


def test_webp_profil_icc():
    inv = inventorier(webp())
    assert inv.profil_icc is not None
    assert inv.profil_icc.description == "Display P3"


def test_webp_animation():
    inv = inventorier(webp(animation=True))
    assert inv.proprietes["animation"] is True
    assert inv.proprietes["boucles"] == 5
    assert inv.proprietes["trames"] == 2


def test_webp_alignement_sur_deux_octets():
    """Un morceau de longueur impaire est suivi d'un octet de bourrage.

    L'ignorer décalerait tous les morceaux suivants d'un octet — et le
    parcours s'arrêterait sur un type illisible, sans dire pourquoi.
    """
    corps = morceau_riff(b"XMP ", b"abc")  # 3 octets : impair
    corps += morceau_riff(b"VP8 ", b"\x00" * 20)
    donnees = b"RIFF" + struct.pack("<I", 4 + len(corps)) + b"WEBP" + corps
    inv = inventorier(donnees)
    assert [c.type for c in inv.chunks] == ["XMP ", "VP8 "]


# ─────────────────────────────────────────────────────────────────────────────
# GIF
# ─────────────────────────────────────────────────────────────────────────────


def test_gif_entete_et_dimensions():
    inv = inventorier(gif())
    assert inv.format == "GIF"
    assert inv.proprietes["version"] == "89a"
    assert (inv.largeur, inv.hauteur) == (32, 24)


def test_gif_commentaire_releve():
    textes = inventorier(gif()).textes
    assert any("EssaiCorp" in t.valeur for t in textes)


def test_gif_animation_et_boucles():
    inv = inventorier(gif(animation=True))
    assert inv.proprietes["animation"] is True
    assert inv.proprietes["trames"] == 3
    assert inv.proprietes["boucles"] == 4


def test_gif_fixe_n_est_pas_une_animation():
    inv = inventorier(gif(animation=False))
    assert inv.proprietes["trames"] == 1
    assert inv.proprietes["animation"] is False


# ─────────────────────────────────────────────────────────────────────────────
# BMP
# ─────────────────────────────────────────────────────────────────────────────


def test_bmp_entete():
    inv = inventorier(bmp())
    assert inv.format == "BMP"
    assert (inv.largeur, inv.hauteur) == (40, 30)
    assert inv.profondeur_bits == 24
    assert inv.proprietes["compression_libelle"] == "aucune (BI_RGB)"
    assert [c.type for c in inv.chunks][0] == "BITMAPFILEHEADER"


def test_bmp_hauteur_negative_est_un_sens_de_stockage_pas_une_dimension():
    """Une hauteur négative dit que les lignes vont de haut en bas.

    La rendre telle quelle donnerait une image « de hauteur -30 », ce qui n'a
    pas de sens ; la prendre en valeur absolue sans le dire perdrait
    l'information. On fait les deux.
    """
    brut = bytearray(bmp())
    brut[22:26] = struct.pack("<i", -30)
    inv = inventorier(bytes(brut))
    assert inv.hauteur == 30
    assert inv.proprietes["lignes_de_haut_en_bas"] is True
    assert inventorier(bmp()).proprietes["lignes_de_haut_en_bas"] is False


# ─────────────────────────────────────────────────────────────────────────────
# SVG
# ─────────────────────────────────────────────────────────────────────────────


def test_svg_dimensions_et_espaces_de_noms():
    inv = inventorier(SVG)
    assert inv.format == "SVG"
    assert (inv.largeur, inv.hauteur) == (800, 600)
    assert inv.proprietes["viewBox"] == "0 0 800 600"
    # L'espace de noms Inkscape trahit le logiciel d'édition.
    assert "inkscape" in inv.proprietes["xmlns:inkscape"]


def test_svg_commentaire_et_titre():
    textes = {t.origine: t.valeur for t in inventorier(SVG).textes}
    assert "EssaiCorp Dessin 12.0" in textes["SVG commentaire"]
    assert textes["SVG <title>"] == "Schema d'essai"
    assert textes["SVG <desc>"] == "Une description lisible en clair."


def test_svg_metadata_rdf():
    inv = inventorier(SVG)
    assert any(c.type == "metadata" for c in inv.chunks)
    assert len(inv.paquets_xmp) == 1


def test_svg_dimension_non_pixel_n_est_pas_convertie():
    """Une largeur en millimètres n'est pas un nombre de pixels.

    La convertir demanderait de connaître la résolution de rendu, que le
    fichier ne porte pas. On garde l'attribut brut et on laisse la dimension
    nulle plutôt que d'inventer un nombre.
    """
    inv = inventorier(SVG.replace(b'width="800"', b'width="210mm"'))
    assert inv.largeur is None
    assert inv.proprietes["width"] == "210mm"
    assert inv.hauteur == 600


# ─────────────────────────────────────────────────────────────────────────────
# Refus
# ─────────────────────────────────────────────────────────────────────────────


def test_format_non_couvert_refuse_en_le_disant():
    """Un inventaire vide laisserait croire que le fichier ne déclare rien."""
    t = BytesIO()
    Image.new("RGB", (8, 8)).save(t, format="JPEG")
    with pytest.raises(ConteneurError, match="non couvert"):
        inventorier(t.getvalue())


def test_fichier_trop_court_refuse():
    with pytest.raises(ConteneurError, match="trop court"):
        inventorier(b"\x89PNG")
