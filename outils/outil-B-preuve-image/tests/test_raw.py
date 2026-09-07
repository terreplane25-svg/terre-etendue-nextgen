"""
Fichiers bruts d'appareil photo : détection du conteneur et lecture.

CE QUE CES TESTS ÉTABLISSENT, ET CE QU'ILS N'ÉTABLISSENT PAS
────────────────────────────────────────────────────────────
Les fichiers sont FABRIQUÉS ICI, à partir des structures publiées : un RAW
TIFF est un TIFF, un RAF porte son en-tête Fujifilm, un CR3 commence par une
boîte `ftyp`. Ces tests établissent donc que le lecteur suit les structures
décrites — pas qu'il lit ce qu'un boîtier réel écrit.

C'est une limite qu'il faut dire : un vrai CR2 de Canon fait 25 Mo et porte des
MakerNotes propriétaires que rien ici ne décode. Ce qui est vérifié, c'est que
l'EXIF standard et les prévisualisations d'un conteneur TIFF sont atteints, et
qu'un conteneur non implémenté est REFUSÉ EN SE NOMMANT plutôt que lu de
travers. Confronter le lecteur à des fichiers de boîtiers réels reste ouvert,
et c'est noté dans `outils/README.md`.
"""

import struct
from io import BytesIO

import pytest
from PIL import Image

from preuve_image.integrity import empreinte_fichier
from preuve_image.metadata import (
    ConteneurNonSupporte,
    MetadataError,
    detecter_conteneur,
    lire_exif,
    lire_exif_depuis_tiff,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fabrication d'un TIFF/RAW : IFD0 + IFD1 + un sous-IFD, chacun avec un aperçu
# ─────────────────────────────────────────────────────────────────────────────


def vignette(largeur: int, hauteur: int) -> bytes:
    img = Image.new("RGB", (largeur, hauteur), (40, 60, 80))
    t = BytesIO()
    img.save(t, format="JPEG", quality=70)
    return t.getvalue()


def entree(tag: int, type_: int, count: int, valeur: bytes) -> bytes:
    return struct.pack("<HHI", tag, type_, count) + valeur.ljust(4, b"\x00")[:4]


def raw_tiff(magique: int = 42) -> bytes:
    """Un TIFF minimal dans la forme d'un RAW : trois images embarquées.

    IFD0 porte l'aperçu pleine résolution (comme un CR2), l'IFD1 la vignette
    EXIF, et un sous-IFD un aperçu moyen (comme un NEF). Les trois doivent être
    trouvées, et rendues de la plus grande à la plus petite.

    IFD0 pointe aussi vers le sous-IFD Exif (0x8769) et le sous-IFD GPS
    (0x8825) : c'est par là que passent la sensibilité et la position sur un
    RAW, et un fichier d'essai qui écrirait ces blocs sans les rendre
    ATTEIGNABLES laisserait croire qu'ils sont lus alors que rien n'irait les
    chercher.

    Toutes les positions sont CALCULÉES depuis les tailles déclarées, jamais
    écrites en dur : une taille d'IFD retouchée sans décaler les offsets ferait
    un fichier incohérent que les tests liraient quand même de travers.
    """
    grande, moyenne, petite = vignette(640, 480), vignette(320, 240), vignette(160, 120)
    entete = b"II" + struct.pack("<HI", magique, 8)

    def taille(n_entrees: int) -> int:
        return 2 + 12 * n_entrees + 4

    n0, n1, ns, n_exif, n_gps = 7, 3, 3, 3, 4
    debut_ifd0 = 8
    debut_ifd1 = debut_ifd0 + taille(n0)
    debut_sub = debut_ifd1 + taille(n1)
    debut_donnees = debut_sub + taille(ns)

    make = b"EssaiCorp\x00"
    modele = b"RAW-1\x00"
    # Latitude 43° 21′ 0″ N, longitude 5° 33′ 0″ E : trois rationnels de 8
    # octets chacun, trop gros pour tenir dans les 4 octets d'une entrée, donc
    # rangés hors ligne.
    lat = struct.pack("<6I", 43, 1, 21, 1, 0, 1)
    lon = struct.pack("<6I", 5, 1, 33, 1, 0, 1)

    off_make = debut_donnees
    off_modele = off_make + len(make)
    off_exif = off_modele + len(modele)
    off_gps = off_exif + taille(n_exif)
    off_lat = off_gps + taille(n_gps)
    off_lon = off_lat + len(lat)
    off_grande = off_lon + len(lon)
    off_moyenne = off_grande + len(grande)
    off_petite = off_moyenne + len(moyenne)

    ifd0 = struct.pack("<H", n0) + b"".join([
        entree(0x010F, 2, len(make), struct.pack("<I", off_make)),
        entree(0x0110, 2, len(modele), struct.pack("<I", off_modele)),
        entree(0x014A, 4, 1, struct.pack("<I", debut_sub)),          # SubIFDs
        entree(0x0201, 4, 1, struct.pack("<I", off_grande)),          # aperçu pleine déf.
        entree(0x0202, 4, 1, struct.pack("<I", len(grande))),
        entree(0x8769, 4, 1, struct.pack("<I", off_exif)),            # ExifIFDPointer
        entree(0x8825, 4, 1, struct.pack("<I", off_gps)),             # GPSIFDPointer
    ]) + struct.pack("<I", debut_ifd1)

    ifd1 = struct.pack("<H", n1) + b"".join([
        entree(0x0103, 3, 1, struct.pack("<HH", 6, 0)),
        entree(0x0201, 4, 1, struct.pack("<I", off_petite)),
        entree(0x0202, 4, 1, struct.pack("<I", len(petite))),
    ]) + struct.pack("<I", 0)

    # Le sous-IFD emploie l'autre convention : des bandes, pas JpegIFOffset.
    sub = struct.pack("<H", ns) + b"".join([
        entree(0x00FE, 4, 1, struct.pack("<I", 1)),
        entree(0x0111, 4, 1, struct.pack("<I", off_moyenne)),        # StripOffsets
        entree(0x0117, 4, 1, struct.pack("<I", len(moyenne))),       # StripByteCounts
    ]) + struct.pack("<I", 0)

    exif = struct.pack("<H", n_exif) + b"".join([
        entree(0x8827, 3, 1, struct.pack("<HH", 400, 0)),            # ISO
        entree(0xA002, 4, 1, struct.pack("<I", 6000)),
        entree(0xA003, 4, 1, struct.pack("<I", 4000)),
    ]) + struct.pack("<I", 0)

    gps = struct.pack("<H", n_gps) + b"".join([
        entree(0x0001, 2, 2, b"N\x00"),                              # GPSLatitudeRef
        entree(0x0002, 5, 3, struct.pack("<I", off_lat)),            # GPSLatitude
        entree(0x0003, 2, 2, b"E\x00"),                              # GPSLongitudeRef
        entree(0x0004, 5, 3, struct.pack("<I", off_lon)),            # GPSLongitude
    ]) + struct.pack("<I", 0)

    fichier = (entete + ifd0 + ifd1 + sub + make + modele + exif + gps
               + lat + lon + grande + moyenne + petite)

    # Contrôle : les blocs doivent tomber là où les entrées les annoncent.
    # Sans lui, une taille mal calculée donnerait un fichier que le lecteur
    # interpréterait au hasard, et les tests vérifieraient ce hasard.
    assert len(entete + ifd0) == debut_ifd1, "IFD1 n'est pas là où IFD0 l'annonce"
    assert len(entete + ifd0 + ifd1) == debut_sub, "sous-IFD mal placé"
    assert fichier[off_make:off_make + len(make)] == make, "Make mal placé"
    assert fichier[off_exif:off_exif + 2] == struct.pack("<H", n_exif), "IFD Exif mal placé"
    assert fichier[off_gps:off_gps + 2] == struct.pack("<H", n_gps), "IFD GPS mal placé"
    assert fichier[off_lat:off_lat + len(lat)] == lat, "rationnels de latitude mal placés"
    assert fichier[off_grande:off_grande + 2] == b"\xff\xd8", "aperçu principal mal placé"
    assert fichier[off_petite:off_petite + 2] == b"\xff\xd8", "vignette mal placée"
    return fichier


@pytest.fixture(scope="module")
def brut():
    return raw_tiff()


# ─────────────────────────────────────────────────────────────────────────────
# Détection du conteneur
# ─────────────────────────────────────────────────────────────────────────────


def test_detecte_le_jpeg():
    t = BytesIO()
    Image.new("RGB", (8, 8)).save(t, format="JPEG")
    assert detecter_conteneur(t.getvalue()) == "JPEG"


def test_detecte_le_png():
    t = BytesIO()
    Image.new("RGB", (8, 8)).save(t, format="PNG")
    assert detecter_conteneur(t.getvalue()) == "PNG"


def test_detecte_le_tiff_raw(brut):
    assert detecter_conteneur(brut) == "TIFF/RAW"


def test_detecte_le_rw2_a_son_nombre_magique():
    """Panasonic écrit 85 là où les autres écrivent 42. C'est le même TIFF derrière."""
    assert detecter_conteneur(raw_tiff(magique=85)) == "TIFF/RAW"


def test_detecte_le_raf_fujifilm():
    donnees = b"FUJIFILMCCD-RAW" + b"\x00" * 100
    assert detecter_conteneur(donnees) == "RAF"


def test_detecte_le_cr3():
    donnees = struct.pack(">I", 24) + b"ftyp" + b"crx " + b"\x00" * 40
    assert detecter_conteneur(donnees) == "CR3"


def test_conteneur_inconnu():
    assert detecter_conteneur(b"pas un format d'image du tout") == "inconnu"
    assert detecter_conteneur(b"") == "inconnu"


# ─────────────────────────────────────────────────────────────────────────────
# Lecture
# ─────────────────────────────────────────────────────────────────────────────


def test_exif_lu_dans_un_raw_tiff(brut):
    """Il n'y a pas d'APP1 à chercher : l'EXIF est dans le TIFF lui-même."""
    e = lire_exif(brut)
    assert e.fabricant == "EssaiCorp"
    assert e.modele == "RAW-1"


def test_les_trois_apercus_sont_trouves(brut):
    """IFD0, IFD1 et le sous-IFD portent chacun une image. Aucune n'est perdue."""
    e = lire_exif(brut)
    assert len(e.previsualisations) == 3
    origines = {p.origine for p in e.previsualisations}
    assert origines == {"IFD0", "IFD1", "sous-IFD 0"}
    assert all(p.est_jpeg for p in e.previsualisations)


def test_apercus_ordonnes_du_plus_grand_au_plus_petit(brut):
    tailles = [p.longueur for p in lire_exif(brut).previsualisations]
    assert tailles == sorted(tailles, reverse=True)


def test_apercu_principal_est_le_plus_grand(brut):
    e = lire_exif(brut)
    principal = e.previsualisation_principale
    assert principal is not None
    assert principal.longueur == max(p.longueur for p in e.previsualisations)
    assert principal.origine == "IFD0"


def test_la_vignette_exif_reste_celle_de_l_ifd1(brut):
    """`miniature` garde son sens : la vignette EXIF, pas le plus gros aperçu."""
    e = lire_exif(brut)
    assert e.miniature is not None
    assert e.miniature.origine == "IFD1"
    assert e.miniature.longueur < (e.previsualisation_principale or e.miniature).longueur


def test_apercu_du_sous_ifd_lu_par_les_bandes(brut):
    """L'autre convention : StripOffsets / StripByteCounts, et non JpegIFOffset."""
    e = lire_exif(brut)
    sub = next(p for p in e.previsualisations if p.origine == "sous-IFD 0")
    assert sub.est_jpeg
    assert sub.longueur > 0


def test_raf_lit_le_jpeg_embarque():
    """Un RAF n'est pas un TIFF : son EXIF est dans le JPEG qu'il transporte."""
    t = BytesIO()
    img = Image.new("RGB", (64, 48), (10, 20, 30))
    exif = Image.Exif()
    exif[0x010F] = "FUJIFILM"
    exif[0x0110] = "X-T5"
    img.save(t, format="JPEG", exif=exif)
    jpeg = t.getvalue()

    entete = bytearray(b"FUJIFILMCCD-RAW" + b"\x00" * 77)
    offset = len(entete)
    struct.pack_into(">II", entete, 84, offset, len(jpeg))
    donnees = bytes(entete) + jpeg

    e = lire_exif(donnees)
    assert e.fabricant == "FUJIFILM"
    assert e.modele == "X-T5"


def test_raf_tronque_refuse_plutot_que_de_deviner():
    entete = bytearray(b"FUJIFILMCCD-RAW" + b"\x00" * 77)
    struct.pack_into(">II", entete, 84, 92, 999_999)
    with pytest.raises(MetadataError, match="introuvable ou tronqué"):
        lire_exif(bytes(entete))


def test_cr3_sans_exif_refuse_en_disant_ce_qui_manque():
    """Le CR3 est maintenant LU (voir test_isobmff). Reste le cas sans EXIF.

    Ce test disait autrefois que le CR3 était refusé par principe, faute de
    lecteur ISOBMFF. Il y en a un désormais, et l'assertion a été réécrite
    plutôt que conservée : un test qui décrit un comportement disparu ne
    protège plus rien, il fige seulement le passé.

    Ce qui reste vrai, et qui compte : un tronçon de CR3 sans bloc EXIF est
    refusé en DISANT ce qui manque, et en distinguant « aucun EXIF trouvé » de
    « fichier sans métadonnées ». Les deux ne s'établissent pas de la même
    façon, et l'empreinte reste valide dans les deux cas.
    """
    donnees = struct.pack(">I", 24) + b"ftyp" + b"crx " + b"\x00" * 40
    with pytest.raises(ConteneurNonSupporte) as exc:
        lire_exif(donnees)
    message = str(exc.value)
    assert "CR3" in message
    assert "aucun bloc EXIF localisable" in message
    assert "n'est pas la même chose" in message
    assert "empreinte" in message


def test_conteneur_inconnu_refuse():
    with pytest.raises(MetadataError, match="non reconnu"):
        lire_exif(b"ceci n'est pas une image, du tout, vraiment pas")


# ─────────────────────────────────────────────────────────────────────────────
# L'empreinte ne dépend pas du format
# ─────────────────────────────────────────────────────────────────────────────


def test_empreinte_calculee_sur_tout_conteneur(tmp_path, brut):
    """SHA-256 porte sur les octets, pas sur un format compris.

    Un CR3 dont l'EXIF n'est pas lisible garde une empreinte parfaitement
    valide : les deux sont indépendants, et c'est ce qui permet de sceller un
    fichier qu'on ne sait pas encore lire.
    """
    cas = {
        "essai.cr2": brut,
        "essai.raf": b"FUJIFILMCCD-RAW" + b"\x00" * 200,
        "essai.cr3": struct.pack(">I", 24) + b"ftyp" + b"crx " + b"\x00" * 40,
        "essai.inconnu": b"nawak",
    }
    for nom, donnees in cas.items():
        chemin = tmp_path / nom
        chemin.write_bytes(donnees)
        # `empreinte_fichier` rend l'empreinte elle-même, pas un objet.
        assert len(empreinte_fichier(chemin)) == 64
        assert chemin.stat().st_size == len(donnees)


def test_apercu_a_offset_incoherent_ecarte():
    """Un aperçu qui déborde du fichier n'est pas rendu tronqué."""
    entete = b"II" + struct.pack("<HI", 42, 8)
    ifd0 = struct.pack("<H", 2) + b"".join([
        entree(0x0201, 4, 1, struct.pack("<I", 999_999)),
        entree(0x0202, 4, 1, struct.pack("<I", 1000)),
    ]) + struct.pack("<I", 0)
    e = lire_exif_depuis_tiff(entete + ifd0)
    assert e.previsualisations == ()


# ─────────────────────────────────────────────────────────────────────────────
# Le nombre magique : admis pour un RAW, refusé dans un bloc EXIF de JPEG
# ─────────────────────────────────────────────────────────────────────────────


def test_rw2_magique_85_lisible_de_bout_en_bout():
    """Détecter « TIFF/RAW » et refuser ensuite la lecture serait incohérent.

    Panasonic écrit 85 là où la norme TIFF écrit 42. `detecter_conteneur` le
    reconnaît depuis toujours ; encore faut-il que `lire_exif` le lise, sans
    quoi l'outil nomme un format puis échoue dessus avec un message qui parle
    d'en-tête invalide — ce qui envoie l'analyste chercher une corruption qui
    n'existe pas.
    """
    e = lire_exif(raw_tiff(magique=85))
    assert e.fabricant == "EssaiCorp"
    assert e.sensibilite_iso == 400
    assert len(e.previsualisations) == 3


def test_magique_non_standard_refuse_hors_raw():
    """L'élargissement ne doit pas déteindre sur la lecture d'un bloc EXIF.

    Un APP1 de JPEG dont le nombre magique n'est pas 42 est corrompu. Le
    lecteur par défaut doit continuer de le dire : c'est l'appelant qui, ayant
    reconnu un RAW, élargit les valeurs admises.
    """
    with pytest.raises(MetadataError, match="nombre magique"):
        lire_exif_depuis_tiff(raw_tiff(magique=85))


def test_olympus_orf_reconnu():
    """0x4F52 (« RO ») est le nombre magique des ORF Olympus."""
    assert detecter_conteneur(raw_tiff(magique=0x4F52)) == "TIFF/RAW"
    assert lire_exif(raw_tiff(magique=0x4F52)).fabricant == "EssaiCorp"


# ─────────────────────────────────────────────────────────────────────────────
# Le conteneur est rapporté sur le relevé
# ─────────────────────────────────────────────────────────────────────────────


def test_conteneur_inscrit_sur_le_releve(brut):
    """Savoir de quel format vient un relevé fait partie du relevé.

    Deux fichiers peuvent donner le même EXIF sans avoir été lus de la même
    façon : par un APP1 de JPEG, par l'IFD0 d'un RAW, ou par le JPEG qu'un RAF
    embarque. L'analyste doit pouvoir le lire sans redemander le fichier.
    """
    assert lire_exif(brut).conteneur == "TIFF/RAW"

    t = BytesIO()
    Image.new("RGB", (8, 8)).save(t, format="JPEG")
    with pytest.raises(MetadataError):
        # Ce JPEG-là n'a pas d'EXIF du tout : le motif doit rester celui-là.
        lire_exif(t.getvalue())


def test_conteneur_non_inscrit_par_le_lecteur_de_bloc(brut):
    """`lire_exif_depuis_tiff` ne sait pas d'où vient son bloc — il ne l'invente pas.

    Le champ reste None plutôt que d'affirmer « TIFF/RAW » pour un bloc qui
    pourrait tout aussi bien être l'APP1 d'un JPEG.
    """
    assert lire_exif_depuis_tiff(brut).conteneur is None


def test_exif_et_gps_atteints_sur_un_raw(brut):
    """« Lit correctement les en-têtes EXIF/GPS » : les sous-IFD, pas seulement l'IFD0.

    Sur un RAW il n'y a pas d'APP1 : l'IFD0 est à la racine du fichier, et
    c'est de là que partent les pointeurs 0x8769 (Exif) et 0x8825 (GPS). Lire
    le fabricant ne prouve rien sur ces deux-là — ils se vérifient à part.
    """
    e = lire_exif(brut)
    assert e.sensibilite_iso == 400
    assert (e.largeur_px, e.hauteur_px) == (6000, 4000)
    assert e.gps is not None
    assert e.gps.latitude_deg == pytest.approx(43.35, abs=1e-9)
    assert e.gps.longitude_deg == pytest.approx(5.55, abs=1e-9)
    # Rien n'a été inventé : l'altitude n'était pas écrite.
    assert e.gps.altitude_m is None


def test_petit_jpeg_reste_un_jpeg():
    """Un JPEG de huit octets EST un JPEG.

    Le plancher de longueur ne sert qu'à la branche ISO BMFF, qui a besoin de
    douze octets pour lire sa marque. L'appliquer à tout écartait les fichiers
    minuscules, et le motif d'échec parlait alors de « conteneur non reconnu »
    là où il fallait dire « aucun segment EXIF » — ce qui envoie l'analyste
    chercher un problème de format qui n'existe pas.
    """
    minuscule = b"\xff\xd8\xff\xda\x00\x02\xff\xd9"
    assert detecter_conteneur(minuscule) == "JPEG"
    with pytest.raises(MetadataError, match="APP1"):
        lire_exif(minuscule)
