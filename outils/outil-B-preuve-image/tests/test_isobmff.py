"""
Les conteneurs à boîtes : HEIC, AVIF, CR3.

CE QUE CES TESTS ÉTABLISSENT, ET CE QU'ILS N'ÉTABLISSENT PAS
────────────────────────────────────────────────────────────
Les fichiers sont FABRIQUÉS ICI, d'après ISO/IEC 14496-12 et 23008-12. Ils
établissent que le lecteur suit ces structures — pas qu'il lit ce qu'un
iPhone ou un Canon écrivent réellement. Un vrai HEIC porte des MakerNotes
Apple propriétaires que rien ici ne décode, et des tuiles HEVC qu'on ne
décompresse pas.

Ce qui est vérifié, c'est le chemin critique : la boîte `meta` est un FullBox
et non un conteneur ordinaire, les emplacements d'items sont lus avec les
bonnes largeurs de champ, un item rangé hors du fichier n'est PAS localisé au
hasard, et un bloc EXIF de HEIF arrive intact au lecteur EXIF déjà éprouvé.

Confronter le lecteur à des fichiers d'appareils réels reste ouvert, et c'est
noté dans `outils/README.md`.
"""

import struct
from io import BytesIO

import pytest
from PIL import Image

from preuve_image.isobmff import (
    UUID_CANON_CR3,
    IsobmffError,
    analyser_isobmff,
    parcourir_boites,
)
from preuve_image.metadata import lire_exif_depuis_tiff

# ─────────────────────────────────────────────────────────────────────────────
# Fabrication
# ─────────────────────────────────────────────────────────────────────────────


def boite(type_: bytes, charge: bytes) -> bytes:
    return struct.pack(">I", 8 + len(charge)) + type_ + charge


def pleine(type_: bytes, version: int, flags: int, charge: bytes) -> bytes:
    """Une FullBox : version sur un octet, drapeaux sur trois."""
    return boite(type_, struct.pack(">B", version) + flags.to_bytes(3, "big") + charge)


def vignette(largeur: int, hauteur: int) -> bytes:
    t = BytesIO()
    Image.new("RGB", (largeur, hauteur), (30, 70, 110)).save(t, format="JPEG", quality=72)
    return t.getvalue()


def tiff_exif(make="Apple", modele="iPhone 15 Pro", iso=80,
              pixel_x=8064, pixel_y=6048) -> bytes:
    """Un bloc TIFF minimal mais complet, avec un sous-IFD Exif atteignable.

    Les deux dimensions DÉCLARÉES sont écrites, pas seulement la largeur :
    la confrontation avec la mesure demande les deux, et un fixture qui n'en
    donnait qu'une la rendait inévaluable — donc jamais éprouvée.
    """
    def entree(tag, type_, count, valeur):
        return struct.pack("<HHI", tag, type_, count) + valeur.ljust(4, b"\x00")[:4]

    m = make.encode() + b"\x00"
    mo = modele.encode() + b"\x00"
    n0 = 3
    debut_donnees = 8 + (2 + 12 * n0 + 4)
    off_m = debut_donnees
    off_mo = off_m + len(m)
    off_exif = off_mo + len(mo)

    ifd0 = struct.pack("<H", n0) + b"".join([
        entree(0x010F, 2, len(m), struct.pack("<I", off_m)),
        entree(0x0110, 2, len(mo), struct.pack("<I", off_mo)),
        entree(0x8769, 4, 1, struct.pack("<I", off_exif)),
    ]) + struct.pack("<I", 0)

    exif = struct.pack("<H", 3) + b"".join([
        entree(0x8827, 3, 1, struct.pack("<HH", iso, 0)),
        entree(0xA002, 4, 1, struct.pack("<I", pixel_x)),
        entree(0xA003, 4, 1, struct.pack("<I", pixel_y)),
    ]) + struct.pack("<I", 0)

    return b"II" + struct.pack("<HI", 42, 8) + ifd0 + m + mo + exif


def heic(avec_auxiliaire=True, avec_xmp=True, marque=b"heic", methode=0,
         nom_auxiliaire=b"urn:com:apple:photo:2020:aux:hdrgainmap\x00",
         second_apercu=False, decalage_exif=6, largeur_offset=4,
         boite_aberrante=False, avec_ispe=True, indices_ipma_16=False,
         essentiel_partout=False, ispe_principale=(8064, 6048),
         ispe_auxiliaire=(2016, 1512), propriete_imbriquee=False) -> bytes:
    """Un HEIF minimal : ftyp + meta(iinf, iloc, pitm, iref, iprp) + mdat.

    Les offsets d'`iloc` sont ABSOLUS dans le fichier, donc calculés après coup
    en deux temps : on assemble d'abord pour connaître la taille de `meta`,
    puis on réécrit les offsets. Les deviner produirait un fichier incohérent
    que les tests liraient de travers sans jamais le signaler.

    Les paramètres qui suivent existent parce que, sans eux, plusieurs ruptures
    délibérées du lecteur passaient inaperçues. Chacun isole UNE dimension.
    """
    bloc_exif = b"Exif\x00\x00" + tiff_exif()
    # Le décalage jusqu'à l'en-tête TIFF. 6 est la valeur normale (« Exif\0\0 ») ;
    # le paramétrer permet d'éprouver que le lecteur le VÉRIFIE au lieu de le suivre.
    charge_exif = struct.pack(">I", decalage_exif) + bloc_exif
    xmp = b'<?xpacket begin="\xef\xbb\xbf"?><x:xmpmeta xmlns:x="adobe:ns:meta/"></x:xmpmeta>'
    principal = vignette(640, 480)
    aux = b"\x00\x11\x22\x33" * 40  # tuiles HEVC : opaques, et c'est le propos

    items = [(1, b"hvc1", None, principal), (2, b"Exif", None, charge_exif)]
    if avec_xmp:
        items.append((3, b"mime", b"application/rdf+xml\x00", xmp))
    if avec_auxiliaire:
        items.append((4, b"hvc1", nom_auxiliaire, aux))
    if second_apercu:
        # Un second aperçu, PLUS PETIT : sans deux aperçus de tailles
        # différentes, l'ordre de tri ne s'observe pas — un tri inversé
        # passerait tous les contrôles.
        items.append((5, b"hvc1", None, vignette(160, 120)))

    infes = b""
    for ident, type_item, nom, _ in items:
        charge = struct.pack(">HH", ident, 0) + type_item + (nom or b"\x00")
        infes += pleine(b"infe", 2, 0, charge)
    iinf = pleine(b"iinf", 0, 0, struct.pack(">H", len(items)) + infes)

    # iloc version 1 : offsets 32 bits par défaut, longueurs 32 bits, pas de base.
    def bloc_iloc(offsets):
        # Largeurs d'offset et de longueur DISSYMÉTRIQUES quand on le demande :
        # avec 4 et 4, intervertir les deux nibbles ne change rien, et une
        # lecture fausse des largeurs passerait inaperçue.
        corps = struct.pack(">BB", (largeur_offset << 4) | 4, (0 << 4) | 0)
        corps += struct.pack(">H", len(items))
        for (ident, _, _, charge), off in zip(items, offsets):
            corps += struct.pack(">H", ident)
            corps += struct.pack(">H", methode)  # méthode de construction
            corps += struct.pack(">H", 0)        # data_reference_index
            corps += struct.pack(">H", 1)        # un seul extent
            corps += off.to_bytes(largeur_offset, "big") + struct.pack(">I", len(charge))
        return pleine(b"iloc", 1, 0, corps)

    # ── Les propriétés d'image : `ipco` les range, `ipma` les associe ────────
    #
    # L'`ispe` de l'image principale est la DERNIÈRE propriété d'`ipco`, et
    # celle de l'auxiliaire la précède. Sans cette inversion, « la première
    # `ispe` du fichier » donnerait la bonne réponse et l'heuristique
    # passerait tous les contrôles au lieu d'être prise en défaut.
    def bloc_iprp():
        ispe_p = pleine(b"ispe", 0, 0, struct.pack(">II", *ispe_principale))
        ispe_a = pleine(b"ispe", 0, 0, struct.pack(">II", *ispe_auxiliaire))
        pasp = boite(b"pasp", struct.pack(">II", 1, 1))
        hvcc = boite(b"hvcC", b"\x01" + b"\x00" * 21)
        proprietes = [("pasp", pasp), ("ispe_aux", ispe_a),
                      ("hvcC", hvcc), ("ispe_principale", ispe_p)]
        if propriete_imbriquee:
            # Une propriété qui est elle-même un CONTENEUR, et qui cache une
            # `ispe` un niveau plus bas. Les indices d'`ipma` comptent les
            # enfants DIRECTS d'`ipco` : un lecteur qui prendrait tous les
            # descendants verrait cette `ispe` cachée s'intercaler et décalerait
            # tout le reste. Placée en tête, elle rend ce décalage observable —
            # en queue, il ne changerait aucun indice.
            proprietes.insert(0, ("leurre", boite(
                b"moov", pleine(b"ispe", 0, 0, struct.pack(">II", 111, 222)))))
        # Les indices sont DÉRIVÉS de l'ordre réel, jamais écrits en dur : un
        # fixture qui gagne une propriété renuméroterait tout silencieusement.
        indice = {nom: i + 1 for i, (nom, _) in enumerate(proprietes)}
        ipco = boite(b"ipco", b"".join(o for _, o in proprietes))

        largeur_index = 2 if indices_ipma_16 else 1
        # Le bit `essential` occupe le bit de poids fort du champ d'indice. Le
        # spécifier sur hvcC est conforme ; `essentiel_partout` le met aussi
        # sur les `ispe` — non conforme, mais c'est la SEULE configuration où
        # un masque oublié se voit, et un lecteur doit masquer partout.
        bit = 0x8000 if largeur_index == 2 else 0x80

        def assoc(indice, essentiel):
            v = indice | (bit if (essentiel or essentiel_partout) else 0)
            return v.to_bytes(largeur_index, "big")

        entrees = [(1, [(indice["pasp"], False),
                        (indice["ispe_principale"], False),
                        (indice["hvcC"], True)])]
        if avec_auxiliaire:
            entrees.append((4, [(indice["hvcC"], True), (indice["ispe_aux"], False)]))
        corps = struct.pack(">I", len(entrees))
        for ident, liste in entrees:
            corps += struct.pack(">HB", ident, len(liste))
            corps += b"".join(assoc(i, e) for i, e in liste)
        ipma = pleine(b"ipma", 0, 1 if indices_ipma_16 else 0, corps)
        return boite(b"iprp", ipco + ipma)

    iprp = bloc_iprp() if avec_ispe else b""

    pitm = pleine(b"pitm", 0, 0, struct.pack(">H", 1))
    # L'item auxiliaire renvoie vers l'image principale.
    iref = pleine(b"iref", 0, 0, boite(b"auxl", struct.pack(">HHH", 4, 1, 1))) if avec_auxiliaire else b""
    hdlr = pleine(b"hdlr", 0, 0, b"\x00" * 4 + b"pict" + b"\x00" * 12 + b"\x00")

    ftyp = boite(b"ftyp", marque + struct.pack(">I", 0) + b"mif1" + b"heic")

    # Deux passes : la taille de `meta` dépend d'`iloc`, dont le contenu dépend
    # de la taille de `meta`. On itère jusqu'au point fixe — deux tours
    # suffisent, et l'assertion finale le vérifie plutôt que de le supposer.
    offsets = [0] * len(items)
    for _ in range(4):
        meta = pleine(b"meta", 0, 0, hdlr + pitm + iinf + bloc_iloc(offsets) + iref + iprp)
        debut_mdat = len(ftyp) + len(meta) + 8
        courant = debut_mdat
        nouveaux = []
        for _, _, _, charge in items:
            nouveaux.append(courant)
            courant += len(charge)
        if nouveaux == offsets:
            break
        offsets = nouveaux
    meta = pleine(b"meta", 0, 0, hdlr + pitm + iinf + bloc_iloc(offsets) + iref + iprp)
    mdat = boite(b"mdat", b"".join(c for _, _, _, c in items))
    fichier = ftyp + meta + mdat

    # Contrôle : chaque item doit être là où `iloc` l'annonce. Sans cela, un
    # décalage d'un octet ferait lire des tests sur des données fausses.
    if methode == 0:
        for (ident, _, _, charge), off in zip(items, offsets):
            assert fichier[off : off + len(charge)] == charge, f"item {ident} mal placé"
    if boite_aberrante:
        # Une boîte qui annonce dix mégaoctets dans un fichier qui n'en fait
        # pas dix kilo : elle ne doit ni être suivie, ni emporter le reste.
        fichier += struct.pack(">I", 10_000_000) + b"junk" + b"\x00" * 16
    return fichier


def cr3() -> bytes:
    """Un CR3 minimal : ftyp crx + moov contenant l'uuid Canon (CMT1..CMT3) + PRVW."""
    cmt1 = boite(b"CMT1", tiff_exif(make="Canon", modele="EOS R5", iso=400))
    cmt3 = boite(b"CMT3", b"\x00\x1c" + b"MAKERNOTE-CANON-OPAQUE" + b"\x00" * 10)
    cncv = boite(b"CNCV", b"CanonCR3_001/00.09.00/00.00.00")
    prvw = boite(b"PRVW", b"\x00" * 16 + vignette(320, 240))
    uuid_canon = boite(b"uuid", UUID_CANON_CR3 + cmt1 + cmt3 + cncv + prvw)
    moov = boite(b"moov", uuid_canon)
    ftyp = boite(b"ftyp", b"crx " + struct.pack(">I", 0) + b"crx " + b"isom")
    return ftyp + moov + boite(b"mdat", b"\x00" * 64)


@pytest.fixture(scope="module")
def fichier_heic():
    return heic()


@pytest.fixture(scope="module")
def fichier_cr3():
    return cr3()


# ─────────────────────────────────────────────────────────────────────────────
# Le parcours de boîtes
# ─────────────────────────────────────────────────────────────────────────────


def test_parcours_trouve_les_boites_de_premier_niveau(fichier_heic):
    types = [b.type for b in parcourir_boites(fichier_heic) if b.profondeur == 0]
    assert types == ["ftyp", "meta", "mdat"]


def test_meta_est_une_fullbox_pas_un_conteneur_ordinaire(fichier_heic):
    """Le piège classique d'ISOBMFF, et il est silencieux.

    `meta` porte quatre octets de version et de drapeaux avant ses enfants. La
    traiter comme un conteneur ordinaire décale la lecture de quatre octets :
    on ne lève pas d'erreur, on lit simplement des boîtes qui n'existent pas —
    et l'absence d'EXIF passe pour une propriété du fichier.
    """
    types = {b.type for b in parcourir_boites(fichier_heic)}
    assert {"hdlr", "pitm", "iinf", "iloc"} <= types
    # Et la conséquence lisible : décalés de quatre octets, ces enfants
    # n'apparaîtraient pas, et l'absence d'EXIF passerait pour un fait.
    assert analyser_isobmff(fichier_heic).bloc_exif is not None


def test_une_taille_aberrante_arrete_le_niveau_sans_tout_perdre():
    """Une boîte qui déborde ne doit ni être suivie, ni emporter le reste."""
    bon = boite(b"ftyp", b"heic" + b"\x00" * 8)
    menteuse = struct.pack(">I", 10_000_000) + b"junk"
    boites = parcourir_boites(bon + menteuse)
    assert [b.type for b in boites] == ["ftyp"]


def test_boite_de_taille_zero_va_jusqu_a_la_fin():
    """Taille 0 est légal et veut dire « jusqu'au bout ». Fréquent sur mdat."""
    donnees = boite(b"ftyp", b"heic" + b"\x00" * 8) + struct.pack(">I", 0) + b"mdat" + b"\xaa" * 32
    boites = parcourir_boites(donnees)
    assert boites[-1].type == "mdat"
    assert boites[-1].fin_charge == len(donnees)


def test_profondeur_bornee():
    """Un fichier fabriqué peut emboîter des conteneurs à l'infini."""
    charge = b"\x00" * 8
    for _ in range(40):
        charge = boite(b"moov", charge)
    boites = parcourir_boites(boite(b"ftyp", b"heic" + b"\x00" * 8) + charge)
    assert max(b.profondeur for b in boites) <= 13


# ─────────────────────────────────────────────────────────────────────────────
# HEIF
# ─────────────────────────────────────────────────────────────────────────────


def test_marque_et_compatibilites(fichier_heic):
    s = analyser_isobmff(fichier_heic)
    assert s.marque == "heic"
    assert "mif1" in s.marques_compatibles
    assert s.est_heif is True
    assert s.est_avif is False
    assert s.est_cr3 is False


def test_avif_reconnu():
    s = analyser_isobmff(heic(marque=b"avif"))
    assert s.est_avif is True


def test_l_exif_d_un_heif_arrive_intact_au_lecteur_exif(fichier_heic):
    """Le point de tout le module : un HEIC porte un bloc TIFF ordinaire.

    Il n'y a donc pas de second lecteur EXIF à écrire — il faut seulement
    donner le bon bloc au lecteur existant. Ce test le vérifie de bout en
    bout : si l'offset était décalé d'un seul octet, le lecteur lèverait.
    """
    s = analyser_isobmff(fichier_heic)
    assert s.bloc_exif is not None
    e = lire_exif_depuis_tiff(s.bloc_exif)
    assert e.fabricant == "Apple"
    assert e.modele == "iPhone 15 Pro"
    assert e.sensibilite_iso == 80
    assert e.largeur_px == 8064


def test_item_principal_designe(fichier_heic):
    assert analyser_isobmff(fichier_heic).item_principal == 1


# ─────────────────────────────────────────────────────────────────────────────
# Les dimensions : `ispe` associée par `ipma`
# ─────────────────────────────────────────────────────────────────────────────


def test_dimensions_de_l_item_principal_lues_dans_ispe(fichier_heic):
    """La seule MESURE qu'un HEIF porte hors de l'EXIF.

    Sans elle, la cohérence entre les octets et la déclaration EXIF reste
    invérifiable pour toute la famille ISOBMFF — et c'est précisément l'écart
    entre les deux qui établit qu'un fichier a été redimensionné sans que la
    métadonnée suive.
    """
    s = analyser_isobmff(fichier_heic)
    assert (s.largeur, s.hauteur) == (8064, 6048)


def test_les_dimensions_ne_sont_ni_la_premiere_ispe_ni_la_plus_grande():
    """L'association est RÉSOLUE, pas approchée.

    Deux heuristiques suffiraient sur un fichier ordinaire : « la première
    `ispe` » et « la plus grande ». Le fixture met la première en défaut par
    construction — l'`ispe` de l'image principale est la DERNIÈRE d'`ipco`.
    Ce cas met la seconde en défaut en INVERSANT les tailles : l'auxiliaire
    devient la plus grande. Seule une résolution réelle de l'association rend
    2016 × 1512 pour l'image principale.
    """
    s = analyser_isobmff(heic(ispe_principale=(2016, 1512), ispe_auxiliaire=(8064, 6048)))
    assert (s.largeur, s.hauteur) == (2016, 1512)
    aux = [i for i in s.items if i.identifiant == 4][0]
    assert (aux.largeur, aux.hauteur) == (8064, 6048)


def test_chaque_item_porte_ses_propres_dimensions(fichier_heic):
    """La carte de gain HDR n'a pas la taille de la photographie.

    Emprunter les dimensions d'un voisin donnerait la taille de la couche
    auxiliaire pour celle de l'image, sans que rien ne le signale.
    """
    s = analyser_isobmff(fichier_heic)
    par_id = {i.identifiant: (i.largeur, i.hauteur) for i in s.items}
    assert par_id[1] == (8064, 6048)
    assert par_id[4] == (2016, 1512)
    # L'item EXIF n'est pas une image : `ipma` ne lui associe aucune `ispe`,
    # et rien ne doit lui en inventer une.
    assert par_id[2] == (None, None)


def test_indices_ipma_sur_seize_bits():
    """Le drapeau 0x1 d'`ipma` fait passer les indices de 8 à 16 bits.

    Lire un octet là où il y en a deux décale tout le reste de la table : les
    associations suivantes deviennent du bruit, sans qu'aucune erreur ne soit
    levée.
    """
    s = analyser_isobmff(heic(indices_ipma_16=True))
    assert (s.largeur, s.hauteur) == (8064, 6048)


def test_le_bit_essential_est_masque_pas_interprete():
    """Le bit de poids fort de chaque indice dit `essential`, pas un indice.

    Ne pas le masquer ajoute 128 (ou 32 768) à l'indice, qui pointe alors hors
    de la liste des propriétés : les dimensions disparaissent en silence, et
    l'absence passe pour une propriété du fichier.
    """
    for large in (False, True):
        s = analyser_isobmff(heic(essentiel_partout=True, indices_ipma_16=large))
        assert (s.largeur, s.hauteur) == (8064, 6048), large


def test_les_indices_comptent_les_enfants_directs_d_ipco():
    """Une `ispe` cachée un niveau plus bas ne doit pas décaler la numérotation.

    Les indices d'`ipma` désignent les enfants DIRECTS d'`ipco`. Un lecteur qui
    compterait tous les descendants verrait la propriété cachée s'intercaler et
    associerait à l'image principale les dimensions d'une autre — sans lever
    d'erreur, et avec un résultat plausible.
    """
    s = analyser_isobmff(heic(propriete_imbriquee=True))
    assert (s.largeur, s.hauteur) == (8064, 6048)
    # Le leurre porte des dimensions qu'aucun item ne doit recevoir.
    assert all((i.largeur, i.hauteur) != (111, 222) for i in s.items)


def test_sans_ispe_les_dimensions_restent_nulles():
    """Pas de repli, pas de devinette : None, et le reste continue d'être lu."""
    s = analyser_isobmff(heic(avec_ispe=False))
    assert s.largeur is None and s.hauteur is None
    assert all(i.largeur is None for i in s.items)
    assert s.bloc_exif is not None


def test_un_cr3_n_a_pas_d_ispe(fichier_cr3):
    """Canon ne range pas ses dimensions là. L'absence est rendue telle quelle."""
    s = analyser_isobmff(fichier_cr3)
    assert s.largeur is None and s.hauteur is None


def test_une_ispe_de_dimension_nulle_est_refusee():
    """Zéro ne décrit aucune image, et diviserait par zéro au rapport d'aspect."""
    s = analyser_isobmff(heic(ispe_principale=(0, 6048)))
    assert s.largeur is None and s.hauteur is None
    # L'auxiliaire, lui, garde les siennes : un refus ne contamine pas le reste.
    assert [i for i in s.items if i.identifiant == 4][0].largeur == 2016


def test_xmp_releve(fichier_heic):
    s = analyser_isobmff(fichier_heic)
    assert len(s.paquets_xmp) == 1
    assert b"adobe:ns:meta" in s.paquets_xmp[0]


def test_auxiliaire_nomme_mais_jamais_decode(fichier_heic):
    """Une carte de gain HDR est SIGNALÉE, pas interprétée.

    Savoir qu'un fichier porte une couche qu'on ne sait pas lire est une
    information. La taire n'en est pas une, et prétendre la décoder serait
    pire.
    """
    s = analyser_isobmff(fichier_heic)
    assert len(s.auxiliaires) == 1
    aux = s.auxiliaires[0]
    assert aux.type_auxiliaire == "carte de gain HDR (Apple)"
    assert aux.longueur == 160
    assert aux.reference_vers == (1,)


def test_auxiliaire_inconnu_nomme_tel_quel():
    """Un type auxiliaire hors répertoire est rendu, pas écarté."""
    s = analyser_isobmff(heic(nom_auxiliaire=b"urn:inconnu:2099:aux:quelquechose\x00"))
    assert len(s.auxiliaires) == 1
    assert "non répertorié" in s.auxiliaires[0].type_auxiliaire


def test_apercu_jpeg_embarque_trouve(fichier_heic):
    s = analyser_isobmff(fichier_heic)
    assert len(s.apercus) == 1
    origine, octets = s.apercus[0]
    assert octets[:2] == b"\xff\xd8"
    assert "item 1" in origine


def test_apercus_ordonnes_du_plus_grand_au_plus_petit():
    """Avec un seul aperçu, un tri inversé passerait inaperçu."""
    s = analyser_isobmff(heic(second_apercu=True))
    assert len(s.apercus) == 2
    assert len(s.apercus[0][1]) > len(s.apercus[1][1])


def test_largeurs_iloc_dissymetriques():
    """Offsets sur 8 octets, longueurs sur 4 : intervertir les nibbles se voit."""
    s = analyser_isobmff(heic(largeur_offset=8))
    assert s.bloc_exif is not None
    assert lire_exif_depuis_tiff(s.bloc_exif).fabricant == "Apple"


def test_decalage_exif_menteur_retombe_sur_la_recherche_du_marqueur():
    """Le décalage déclaré est VÉRIFIÉ, pas suivi aveuglément.

    Un décalage qui tombe dans le fichier mais pas sur un en-tête TIFF donnerait,
    suivi tel quel, un bloc décalé — que le lecteur EXIF déclarerait corrompu
    alors que le fichier est sain.
    """
    menteur = analyser_isobmff(heic(decalage_exif=10))
    sain = analyser_isobmff(heic())
    assert menteur.bloc_exif == sain.bloc_exif


def test_item_hors_du_fichier_n_est_pas_localise_au_hasard():
    """Méthode de construction ≠ 0 : l'item est ailleurs, on ne le devine pas.

    Rendre un offset arbitraire placerait des octets quelconques à la place
    d'un bloc EXIF — et le lecteur les interpréterait sans broncher jusqu'à
    ce qu'ils ressemblent à autre chose.
    """
    s = analyser_isobmff(heic(methode=1))
    assert s.bloc_exif is None
    assert all(i.offset is None for i in s.items)
    assert s.apercus == ()
    # Les items restent DÉCLARÉS : on sait qu'ils existent, on ne sait pas où.
    # C'est différent de ne rien savoir, et il faut que ça se voie.
    assert len(s.items) == 4


# ─────────────────────────────────────────────────────────────────────────────
# CR3 — le format que le paquet refusait
# ─────────────────────────────────────────────────────────────────────────────


def test_cr3_reconnu(fichier_cr3):
    s = analyser_isobmff(fichier_cr3)
    assert s.est_cr3 is True
    assert s.version_codec.startswith("CanonCR3_001")


def test_cr3_l_exif_est_lu(fichier_cr3):
    """Le CR3 était refusé en se nommant. Il est maintenant lu.

    Canon range l'IFD0 dans une boîte CMT1, elle-même dans une boîte `uuid`
    sous `moov`. C'est un bloc TIFF complet : le lecteur existant le prend.
    """
    s = analyser_isobmff(fichier_cr3)
    assert s.bloc_exif is not None
    e = lire_exif_depuis_tiff(s.bloc_exif)
    assert e.fabricant == "Canon"
    assert e.modele == "EOS R5"
    assert e.sensibilite_iso == 400


def test_cr3_makernotes_rendus_bruts(fichier_cr3):
    """Les MakerNotes sont rendus TELS QUELS, sans être interprétés ici.

    Les décoder demande un dictionnaire par marque et par millésime ; les
    rendre bruts permet au moins de les compter, de les hacher et de voir
    qu'ils existent.
    """
    s = analyser_isobmff(fichier_cr3)
    assert s.makernotes is not None
    assert b"MAKERNOTE-CANON-OPAQUE" in s.makernotes


def test_cr3_apercu_prvw_extrait(fichier_cr3):
    s = analyser_isobmff(fichier_cr3)
    assert len(s.apercus) == 1
    origine, octets = s.apercus[0]
    assert origine == "boîte PRVW"
    assert octets[:3] == b"\xff\xd8\xff"


# ─────────────────────────────────────────────────────────────────────────────
# Refus
# ─────────────────────────────────────────────────────────────────────────────


def test_sans_ftyp_refuse():
    with pytest.raises(IsobmffError, match="ftyp"):
        analyser_isobmff(b"\x00" * 64)


def test_trop_court_refuse():
    with pytest.raises(IsobmffError):
        analyser_isobmff(b"\x00\x00\x00\x14ft")


# ─────────────────────────────────────────────────────────────────────────────
# Bout en bout : par le point d'entrée du paquet, pas par le module interne
# ─────────────────────────────────────────────────────────────────────────────


def test_lire_exif_lit_un_heic(fichier_heic):
    """Le chemin réel : `lire_exif` sur des octets, sans rien savoir du format."""
    from preuve_image.metadata import detecter_conteneur, lire_exif

    assert detecter_conteneur(fichier_heic) == "HEIC"
    e = lire_exif(fichier_heic)
    assert e.conteneur == "HEIC"
    assert e.fabricant == "Apple"
    assert e.sensibilite_iso == 80
    # L'aperçu du conteneur remonte jusqu'au relevé, alors que le bloc TIFF
    # ne le mentionne nulle part.
    assert len(e.previsualisations) == 1
    assert e.previsualisation_principale.origine.startswith("item 1")


def test_lire_exif_lit_un_cr3(fichier_cr3):
    """Le CR3 était refusé en se nommant. Il est lu."""
    from preuve_image.metadata import detecter_conteneur, lire_exif

    assert detecter_conteneur(fichier_cr3) == "CR3"
    e = lire_exif(fichier_cr3)
    assert e.conteneur == "CR3"
    assert e.fabricant == "Canon"
    assert e.modele == "EOS R5"
    assert e.sensibilite_iso == 400
    assert e.previsualisation_principale.origine == "boîte PRVW"


def test_avif_detecte_comme_tel():
    from preuve_image.metadata import detecter_conteneur

    assert detecter_conteneur(heic(marque=b"avif")) == "AVIF"


def test_un_apercu_present_des_deux_cotes_n_est_pas_compte_deux_fois():
    """Le dédoublonnage porte sur les OCTETS, pas sur les offsets.

    Les offsets d'un aperçu de conteneur et d'un aperçu de bloc TIFF ne sont
    pas dans le même repère : les comparer ferait apparaître deux fois la même
    image. Comparer les octets ne dépend d'aucune convention.
    """
    from preuve_image.metadata import lire_exif

    e = lire_exif(heic())
    octets = [m.octets for m in e.previsualisations]
    assert len(octets) == len(set(octets))
