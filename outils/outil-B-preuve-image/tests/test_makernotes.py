"""
Les notes propriétaires : leur structure, jamais leur sens.

CE QUE CES TESTS ÉTABLISSENT
────────────────────────────
Que le constructeur est reconnu à sa signature — qui est dans les octets —,
que la base des offsets est VÉRIFIÉE contre les données au lieu d'être
présumée, et que le sens des tags n'est jamais affirmé.

Le test qui compte le plus est celui de la base : se tromper d'origine ne lève
aucune erreur, on lit simplement des octets quelconques qui ressemblent à des
données. C'est le mode de défaillance silencieuse le plus dangereux de tout ce
paquet, et il est éprouvé en fabriquant la MÊME note sous deux bases
différentes et en vérifiant que le lecteur retrouve la bonne dans les deux cas.
"""

import struct

import pytest

from preuve_image.makernotes import (
    MOTIF_AUCUN_SENS,
    SENS_CONNUS,
    SIGNATURES,
    analyser_makernote,
    reconnaitre_constructeur,
)

# ─────────────────────────────────────────────────────────────────────────────
# Fabrication
# ─────────────────────────────────────────────────────────────────────────────


def ifd(entrees, endian="<", base=0, debut_ifd=0, charge_avant=b""):
    """Fabrique un IFD et ses valeurs longues.

    `base` est ce qu'on AJOUTE aux offsets écrits : 0 pour des offsets comptés
    depuis le début de la note, une position quelconque pour simuler des
    offsets comptés depuis l'en-tête TIFF du fichier. C'est ce paramètre qui
    permet d'éprouver la détermination de la base.

    `entrees` est une suite de (tag, type, cardinalité, octets de la valeur).
    """
    n = len(entrees)
    corps = struct.pack(endian + "H", n)
    zone = b""
    # Les valeurs longues sont rangées après l'IFD et son pointeur de suite.
    debut_zone = debut_ifd + 2 + 12 * n + 4
    for tag, type_, cardinalite, valeur in entrees:
        if len(valeur) <= 4:
            champ = valeur.ljust(4, b"\x00")
        else:
            champ = struct.pack(endian + "I", base + debut_zone + len(zone))
            zone += valeur
        corps += struct.pack(endian + "HHI", tag, type_, cardinalite) + champ
    corps += struct.pack(endian + "I", 0)
    return charge_avant + corps + zone


ENTREES = [
    (0x0001, 3, 1, struct.pack("<H", 42)),                    # SHORT en ligne
    (0x0004, 4, 1, struct.pack("<I", 123456)),                # LONG en ligne
    (0x0010, 2, 24, b"EssaiCorp Firmware 2.1\x00\x00"),       # ASCII hors ligne
    (0x0095, 7, 40, b"\xde\xad\xbe\xef" * 10),                # UNDEFINED opaque
    (0x00A7, 5, 1, struct.pack("<II", 7, 2)),                 # RATIONAL hors ligne
]


def note_sans_signature(base=0, decalage=0):
    """Une note qui commence directement par un IFD, comme celles de Canon."""
    return ifd(ENTREES, "<", base, decalage, b"\x00" * decalage)


def note_apple():
    """Apple : en-tête de 14 octets, gros-boutien imposé, offsets depuis la note."""
    entrees = [
        (0x0001, 3, 1, struct.pack(">H", 7)),
        (0x0003, 7, 24, b"bplist00" + b"\x00" * 16),
        (0x000A, 2, 16, b"iPhone 15 Pro\x00\x00\x00"),
    ]
    return ifd(entrees, ">", 0, 14, b"Apple iOS\x00\x00\x01MM")


def note_fujifilm(debut=12):
    """Fujifilm : l'offset de l'IFD est écrit en clair aux octets 8 à 11.

    `debut` par défaut vaut 12, c'est-à-dire juste après l'offset — le cas
    ordinaire, où le décalage publié suffirait. Un autre `debut` éprouve que
    c'est bien l'offset ÉCRIT qui fait autorité.
    """
    corps = ifd(ENTREES, "<", 0, debut, b"\x00" * (debut - 12))
    return b"FUJIFILM" + struct.pack("<I", debut) + corps


def note_ifd_leurre():
    """Un IFD-leurre à l'offset 0, dont aucune entrée n'est lisible.

    Son unique entrée porte un type hors norme, donc écartée : l'IFD se
    retrouve vide. Le vrai IFD est douze octets plus loin, et c'est lui qui
    doit être retenu. Les deux derniers octets de l'en-tête du leurre sont le
    compteur du vrai IFD — ils ne sont jamais lus comme une valeur, puisque le
    type du leurre est inconnu.

    Les champs libres du leurre sont mis à zéro pour que les décalages
    intermédiaires essayés — 2, 4, 6, 8, 10 — y lisent un compteur nul ou
    délirant et soient écartés. Sans cette précaution, le leurre serait bien
    rejeté mais un décalage voisin serait retenu par accident, et le test
    n'éprouverait pas ce qu'il annonce.
    """
    entete = struct.pack("<H", 1) + struct.pack("<HHI", 0, 99, 0) + b"\x00\x00"
    assert len(entete) == 12
    return ifd(ENTREES, "<", 0, 12, entete)


def note_nikon():
    """Nikon type 3 : dix octets, puis un en-tête TIFF COMPLET.

    C'est la seule famille dans ce cas, et les offsets partent de cet en-tête
    interne — pas du début de la note, pas de l'en-tête TIFF du fichier.
    """
    entete = b"Nikon\x00\x02\x10\x00\x00"
    interne = b"II" + struct.pack("<HI", 42, 8)
    corps = ifd(ENTREES, "<", 0, 8, b"")
    return entete + interne + corps


# ─────────────────────────────────────────────────────────────────────────────
# La reconnaissance du constructeur
# ─────────────────────────────────────────────────────────────────────────────


@pytest.mark.parametrize("fabrique,attendu", [
    (note_apple, "Apple"),
    (note_fujifilm, "Fujifilm"),
    (note_nikon, "Nikon (type 3)"),
])
def test_constructeur_reconnu_a_sa_signature(fabrique, attendu):
    """La signature est DANS les octets : c'est une lecture, pas une déduction."""
    assert reconnaitre_constructeur(fabrique()).nom == attendu


def test_note_sans_signature_n_est_attribuee_a_personne():
    """Canon n'a pas de signature : sa note commence par un IFD.

    Deviner « Canon » parce qu'aucune autre signature ne correspond lui
    attribuerait toutes les notes des constructeurs qu'on ne connaît pas.
    """
    assert reconnaitre_constructeur(note_sans_signature()) is None
    a = analyser_makernote(note_sans_signature())
    assert a.constructeur is None
    # Elle est quand même LUE : c'est la structure qui compte, pas le nom.
    assert a.nombre_de_tags == 5


def test_signatures_les_plus_longues_en_premier():
    """« OLYMP\\0 » est un préfixe de « OLYMPUS\\0 » : l'ordre décide du résultat.

    Sans cet ordre, un OLYMPUS serait reconnu comme un OLYMP, avec un décalage
    d'IFD faux — et la lecture donnerait des octets quelconques.
    """
    vus = {}
    for s in SIGNATURES:
        for autre, i in vus.items():
            assert not s.magie.startswith(autre), (
                f"« {s.nom} » est précédé de « {list(vus)[i]!r} » dont il est un "
                "sur-ensemble : il ne sera jamais reconnu"
            )
        vus[s.magie] = len(vus)


# ─────────────────────────────────────────────────────────────────────────────
# LA BASE DES OFFSETS — le piège principal
# ─────────────────────────────────────────────────────────────────────────────


def test_base_depuis_la_note_retrouvee():
    a = analyser_makernote(note_sans_signature(base=0), offset_dans_le_tiff=1000)
    assert a.base_retenue == "note"
    assert a.nombre_de_tags == 5


def test_base_depuis_l_entete_tiff_retrouvee():
    """La MÊME note, avec des offsets comptés depuis l'en-tête TIFF du fichier.

    C'est le test central du module. Se tromper de base ne lève aucune erreur :
    on lit des octets quelconques qui ressemblent à des données. Le lecteur doit
    donc ESSAYER les bases et retenir celle qui donne un IFD cohérent, au lieu
    de se fier à ce que la documentation dit du constructeur.
    """
    a = analyser_makernote(note_sans_signature(base=5000), offset_dans_le_tiff=5000)
    assert a.base_retenue == "tiff"
    assert a.nombre_de_tags == 5
    # Et les valeurs longues sont bien retrouvées, pas seulement l'IFD.
    texte = next(t for t in a.tags if t.identifiant == 0x0010)
    assert texte.apercu_texte == "EssaiCorp Firmware 2.1"


def test_les_deux_bases_donnent_le_meme_inventaire():
    """Une note lue sous la bonne base rend la même chose, où qu'elle soit.

    Si ce test tombait, c'est que la base change ce qui est lu — donc qu'une
    des deux lectures est fausse, sans qu'aucune n'ait levé d'erreur.
    """
    a = analyser_makernote(note_sans_signature(base=0), offset_dans_le_tiff=0)
    b = analyser_makernote(note_sans_signature(base=5000), offset_dans_le_tiff=5000)
    assert [(t.identifiant, t.octets, t.empreinte) for t in a.tags] \
        == [(t.identifiant, t.octets, t.empreinte) for t in b.tags]


def test_base_conforme_a_ce_qui_etait_attendu():
    a = analyser_makernote(note_apple())
    assert a.base_attendue == "note"
    assert a.base_retenue == "note"
    assert a.base_conforme is True


def test_nikon_a_un_entete_tiff_interne():
    """La seule famille dont les offsets partent d'un en-tête TIFF interne."""
    a = analyser_makernote(note_nikon(), offset_dans_le_tiff=900)
    assert a.constructeur == "Nikon (type 3)"
    assert a.base_retenue == "tiff_interne"
    assert a.base_conforme is True
    assert a.nombre_de_tags == 5


def test_fujifilm_lit_l_offset_ecrit_en_clair():
    a = analyser_makernote(note_fujifilm(), offset_dans_le_tiff=700)
    assert a.constructeur == "Fujifilm"
    assert a.nombre_de_tags == 5
    assert a.boutisme == "petit-boutien"


def test_boutisme_impose_par_le_constructeur():
    """Apple impose le gros-boutien par les deux derniers octets de son en-tête."""
    a = analyser_makernote(note_apple(), boutisme_fichier="<")
    assert a.boutisme == "gros-boutien"
    assert a.nombre_de_tags == 3


def test_structure_illisible_dit_ce_qui_a_ete_essaye():
    """Plusieurs constructeurs emploient des formats propres, ou chiffrent.

    Rendre un inventaire vide laisserait croire que la note ne porte rien.
    """
    a = analyser_makernote(b"\x7f\xff" * 200)
    assert a.present is True
    assert a.tags == ()
    assert a.motif_structure_illisible is not None
    assert "essayées" in a.motif_structure_illisible
    # L'empreinte reste valide : elle ne dépend d'aucune structure comprise.
    assert len(a.empreinte) == 64


def test_une_cardinalite_aberrante_ecarte_la_base():
    """Une cardinalité délirante ne doit produire aucun tag.

    Le module n'a PAS de contrôle dédié à la cardinalité, et c'est délibéré :
    un balayage a établi que toute taille supérieure à la note fait déjà
    déborder le contrôle d'offset, un offset négatif étant écarté à part. Un
    second contrôle se lirait comme une protection qu'il n'apporte pas. Ce
    test éprouve donc le RÉSULTAT, pas le mécanisme.
    """
    mauvaise = ifd([(0x0001, 4, 4_000_000_000, b"\x00" * 8)], "<")
    a = analyser_makernote(mauvaise)
    assert a.tags == () or all(t.cardinalite < 1000 for t in a.tags)


def test_un_ifd_sans_aucune_entree_lisible_n_est_pas_un_ifd():
    """Sinon une mauvaise base serait retenue avec un inventaire vide.

    C'est un échec plus insidieux qu'une erreur : le relevé annoncerait une
    base déterminée, zéro tag, et rien ne dirait que le vrai IFD est ailleurs.
    """
    a = analyser_makernote(note_ifd_leurre())
    assert a.base_retenue is not None
    assert a.nombre_de_tags == 5, "le leurre a été retenu à la place du vrai IFD"


def test_fujifilm_dont_l_ifd_n_est_pas_au_decalage_habituel():
    """L'offset en clair est ce qui fait autorité, pas le décalage publié."""
    a = analyser_makernote(note_fujifilm(debut=24))
    assert a.constructeur == "Fujifilm"
    assert a.nombre_de_tags == 5


# ─────────────────────────────────────────────────────────────────────────────
# L'inventaire : des formes, jamais des sens
# ─────────────────────────────────────────────────────────────────────────────


def test_tags_inventories_par_leur_structure():
    a = analyser_makernote(note_sans_signature())
    par_id = {t.identifiant: t for t in a.tags}
    assert par_id[0x0001].type_nom == "SHORT"
    assert par_id[0x0001].en_ligne is True
    assert par_id[0x0010].type_nom == "ASCII"
    assert par_id[0x0010].octets == 24
    assert par_id[0x0010].en_ligne is False
    assert par_id[0x00A7].type_nom == "RATIONAL"


def test_tags_ordonnes_par_identifiant():
    a = analyser_makernote(note_sans_signature())
    ids = [t.identifiant for t in a.tags]
    assert ids == sorted(ids)


def test_forme_reconnue_jamais_le_sens():
    """Savoir qu'un tag est du texte oriente ; prétendre savoir ce qu'il désigne, non."""
    a = analyser_makernote(note_sans_signature())
    par_id = {t.identifiant: t for t in a.tags}
    assert par_id[0x0010].forme == "texte"
    assert par_id[0x0010].apercu_texte == "EssaiCorp Firmware 2.1"
    # Le tag opaque n'a pas de forme reconnue — et surtout pas de sens inventé.
    assert par_id[0x0095].forme is None
    assert par_id[0x0095].sens is None


def test_liste_de_proprietes_binaire_reconnue_sans_etre_decodee():
    """Apple range des bplist dans ses notes. On le dit, on ne les ouvre pas."""
    a = analyser_makernote(note_apple())
    t = next(x for x in a.tags if x.identifiant == 0x0003)
    assert t.forme == "liste de propriétés binaire (bplist)"


def test_aucun_sens_n_est_jamais_affirme():
    """Le registre est vide, et le motif dit pourquoi ET ce qui reste utilisable."""
    a = analyser_makernote(note_sans_signature())
    assert SENS_CONNUS == {}
    assert all(t.sens is None for t in a.tags)
    assert a.motif_aucun_sens == MOTIF_AUCUN_SENS
    assert "change d'un millésime à l'autre" in MOTIF_AUCUN_SENS
    assert "CONFRONTER deux fichiers" in MOTIF_AUCUN_SENS


def test_empreinte_de_tag_permet_de_confronter_deux_fichiers():
    """C'est le seul usage probatoire honnête d'un tag qu'on ne sait pas lire."""
    a = analyser_makernote(note_sans_signature())
    b = analyser_makernote(note_sans_signature())
    assert [t.empreinte for t in a.tags] == [t.empreinte for t in b.tags]

    entrees = list(ENTREES)
    entrees[3] = (0x0095, 7, 40, b"\xca\xfe\xba\xbe" * 10)
    c = analyser_makernote(ifd(entrees, "<"))
    assert [t.empreinte for t in a.tags] != [t.empreinte for t in c.tags]


def test_empreinte_de_la_note_entiere():
    a = analyser_makernote(note_apple())
    b = analyser_makernote(note_apple())
    assert a.empreinte == b.empreinte
    assert a.empreinte != analyser_makernote(note_fujifilm()).empreinte


def test_note_absente():
    a = analyser_makernote(b"")
    assert a.present is False
    assert a.octets == 0
    assert a.tags == ()


def test_type_inconnu_ecarte_sans_condamner_l_ifd():
    """Un constructeur peut employer un type non normalisé.

    Écarter l'entrée est prudent ; écarter l'IFD entier perdrait tout le reste.
    """
    entrees = list(ENTREES) + [(0x00FF, 99, 1, b"\x00\x00\x00\x00")]
    a = analyser_makernote(ifd(entrees, "<"))
    assert a.nombre_de_tags == 5
    assert 0x00FF not in [t.identifiant for t in a.tags]
