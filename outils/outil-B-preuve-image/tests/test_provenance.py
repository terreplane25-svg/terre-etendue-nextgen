"""
Lecture des déclarations de provenance : CBOR, JUMBF/C2PA, XMP, IPTC, chaînes.

CE QUE CES TESTS ÉTABLISSENT, ET CE QU'ILS N'ÉTABLISSENT PAS
────────────────────────────────────────────────────────────
Le décodeur CBOR est confronté aux vecteurs de l'annexe A de la RFC 8949 :
c'est une référence EXTÉRIEURE au code, écrite par d'autres, et un décodeur qui
les passe tous décode réellement du CBOR.

Il n'en va pas de même du C2PA. Les conteneurs employés ici sont construits
dans ce fichier, à partir de la structure d'ISO/IEC 19566-5 et de la
spécification C2PA. Ils établissent donc que le lecteur suit LA STRUCTURE
DÉCRITE — pas qu'il lit ce qu'une implémentation C2PA réelle produit. Confronter
le lecteur à un fichier signé par un outil du marché reste à faire, et c'est
noté comme tel dans `outils/README.md`. Un fichier de référence externe vaudrait
mieux que ces fixtures, et rien ici ne prétend le contraire.

Aucun de ces tests ne vérifie une signature : le module ne le fait pas, ne
prétend pas le faire, et `test_aucune_signature_n_est_verifiee` s'assure qu'il
continue de le dire.
"""

import struct

import pytest

from preuve_image.provenance import (
    AVERTISSEMENT_C2PA,
    ProvenanceError,
    analyser_boites_jumbf,
    analyser_provenance,
    decoder_cbor,
    extraire_c2pa,
    extraire_chaines,
    extraire_iptc,
    extraire_xmp,
)

# ─────────────────────────────────────────────────────────────────────────────
# CBOR — vecteurs de la RFC 8949, annexe A
# ─────────────────────────────────────────────────────────────────────────────

VECTEURS_RFC8949 = [
    ("00", 0),
    ("01", 1),
    ("0a", 10),
    ("17", 23),
    ("1818", 24),
    ("1903e8", 1000),
    ("1a000f4240", 1_000_000),
    ("20", -1),
    ("29", -10),
    ("3863", -100),
    ("3903e7", -1000),
    ("40", b""),
    ("4401020304", b"\x01\x02\x03\x04"),
    ("60", ""),
    ("6161", "a"),
    ("6449455446", "IETF"),
    ("62225c", '"\\'),
    ("80", []),
    ("83010203", [1, 2, 3]),
    ("8301820203820405", [1, [2, 3], [4, 5]]),
    ("a0", {}),
    ("a201020304", {1: 2, 3: 4}),
    ("a26161016162820203", {"a": 1, "b": [2, 3]}),
    ("826161a161626163", ["a", {"b": "c"}]),
    ("f4", False),
    ("f5", True),
    ("f6", None),
    # Longueurs indéfinies
    ("5f42010243030405ff", b"\x01\x02\x03\x04\x05"),
    ("7f657374726561646d696e67ff", "streaming"),
    ("9fff", []),
    ("9f018202039f0405ffff", [1, [2, 3], [4, 5]]),
    ("bf61610161629f0203ffff", {"a": 1, "b": [2, 3]}),
]


@pytest.mark.parametrize("hexa,attendu", VECTEURS_RFC8949)
def test_cbor_vecteurs_rfc8949(hexa, attendu):
    """Le décodeur est jugé par une table qu'il n'a pas écrite."""
    assert decoder_cbor(bytes.fromhex(hexa)) == attendu


def test_cbor_refuse_un_flux_tronque():
    with pytest.raises(ProvenanceError):
        decoder_cbor(bytes.fromhex("1903"))  # entier sur 2 octets, un seul fourni


def test_cbor_refuse_une_imbrication_sans_fin():
    """Mille tableaux imbriqués : le décodeur s'arrête au lieu de dérouler la pile."""
    with pytest.raises(ProvenanceError):
        decoder_cbor(b"\x81" * 1000 + b"\x00")


def test_cbor_conserve_l_etiquette():
    # 0xc0 = étiquette 0 (date-time), suivie d'une chaîne.
    v = decoder_cbor(bytes.fromhex("c06131"))
    assert v == {"_etiquette_cbor": 0, "valeur": "1"}


# ─────────────────────────────────────────────────────────────────────────────
# Construction de conteneurs JUMBF, d'après ISO/IEC 19566-5
# ─────────────────────────────────────────────────────────────────────────────

UUID_CBOR = bytes.fromhex("6362 6f72 0011 0010 8000 00aa 0038 9b71".replace(" ", ""))


def boite(type_: bytes, charge: bytes) -> bytes:
    """LBox (4 octets, gros-boutiste) + TBox (4 caractères) + charge."""
    return struct.pack(">I", 8 + len(charge)) + type_ + charge


def description(label: str, uuid_type: bytes = UUID_CBOR) -> bytes:
    """Boîte `jumd` : UUID de type, drapeaux, puis le label terminé par NUL."""
    return boite(b"jumd", uuid_type + bytes([0x03]) + label.encode() + b"\x00")


def superboite(label: str, contenu: bytes) -> bytes:
    return boite(b"jumb", description(label) + contenu)


def encoder_cbor_map(table: dict) -> bytes:
    """Encodeur CBOR minuscule, pour fabriquer les fixtures — jamais employé en production."""
    def enc(v):
        if isinstance(v, bool):
            return b"\xf5" if v else b"\xf4"
        if v is None:
            return b"\xf6"
        if isinstance(v, int):
            if v < 24:
                return bytes([v])
            if v < 256:
                return bytes([0x18, v])
            return b"\x19" + struct.pack(">H", v)
        if isinstance(v, str):
            b = v.encode()
            return (bytes([0x60 + len(b)]) if len(b) < 24 else bytes([0x78, len(b)])) + b
        if isinstance(v, list):
            return bytes([0x80 + len(v)]) + b"".join(enc(x) for x in v)
        if isinstance(v, dict):
            return bytes([0xA0 + len(v)]) + b"".join(enc(k) + enc(x) for k, x in v.items())
        raise TypeError(type(v))
    return enc(table)


def manifeste_c2pa_synthetique() -> bytes:
    """Un magasin de manifestes conforme à la structure décrite par la spécification."""
    actions = superboite(
        "c2pa.actions",
        boite("cbor".encode(), encoder_cbor_map({
            "actions": [
                {"action": "c2pa.created", "softwareAgent": "Appareil d'essai 1.0"},
                {"action": "c2pa.color_adjustments", "softwareAgent": "Retoucheur 2.4"},
                {"action": "c2pa.cropped"},
            ],
        })),
    )
    creative = superboite(
        "stds.schema-org.CreativeWork",
        boite("json".encode(), b'{"@context":"https://schema.org","author":[{"name":"Anonyme"}]}'),
    )
    assertions = superboite("c2pa.assertions", actions + creative)
    revendication = superboite(
        "c2pa.claim",
        boite("cbor".encode(), encoder_cbor_map({
            "claim_generator": "essai-c2pa/0.1",
            "alg": "ps256",
            "dc:format": "image/jpeg",
        })),
    )
    signature = superboite("c2pa.signature", boite("cbor".encode(), b"\x43\x00\x01\x02"))
    manifeste = superboite("urn:uuid:0000-essai", assertions + revendication + signature)
    return superboite("c2pa", manifeste)


def jpeg_avec_app11(charge_jumbf: bytes, taille_fragment: int = 60_000) -> bytes:
    """JPEG minimal portant un conteneur JUMBF, fragmenté comme le veut la norme."""
    out = [b"\xff\xd8"]
    numero = 1
    for i in range(0, len(charge_jumbf), taille_fragment):
        fragment = charge_jumbf[i : i + taille_fragment]
        corps = b"JP" + struct.pack(">H", 1) + struct.pack(">I", numero) + fragment
        out.append(b"\xff\xeb" + struct.pack(">H", len(corps) + 2) + corps)
        numero += 1
    out.append(b"\xff\xda\x00\x02")  # SOS
    out.append(b"\xff\xd9")
    return b"".join(out)


# ─────────────────────────────────────────────────────────────────────────────
# JUMBF
# ─────────────────────────────────────────────────────────────────────────────


def test_boite_simple():
    b = analyser_boites_jumbf(boite(b"cbor", b"\x01\x02"))
    assert len(b) == 1
    assert b[0].type_ == "cbor"
    assert b[0].charge == b"\x01\x02"
    assert b[0].taille == 10


def test_superboite_porte_son_label():
    b = analyser_boites_jumbf(superboite("c2pa.actions", boite(b"cbor", b"\x00")))
    assert len(b) == 1
    assert b[0].type_ == "jumb"
    assert b[0].label == "c2pa.actions"


def test_boite_tronquee_ne_perd_pas_les_precedentes():
    """Une boîte annoncée plus longue que le flux arrête le parcours, sans lever.

    Un conteneur partiel doit rester lisible jusqu'où il l'est : lever une
    exception ferait perdre tout ce qui précède, alors que c'est justement ce
    qu'on veut montrer à l'opérateur.
    """
    bon = boite(b"cbor", b"\x01")
    mauvais = struct.pack(">I", 9999) + b"cbor" + b"\x02"
    b = analyser_boites_jumbf(bon + mauvais)
    assert len(b) == 1
    assert b[0].charge == b"\x01"


def test_lbox_zero_court_jusqu_a_la_fin():
    brut = struct.pack(">I", 0) + b"cbor" + b"abcdef"
    b = analyser_boites_jumbf(brut)
    assert b[0].charge == b"abcdef"


def test_lbox_un_utilise_la_taille_etendue():
    charge = b"xy"
    brut = struct.pack(">I", 1) + b"cbor" + struct.pack(">Q", 16 + len(charge)) + charge
    b = analyser_boites_jumbf(brut)
    assert b[0].charge == charge


# ─────────────────────────────────────────────────────────────────────────────
# C2PA
# ─────────────────────────────────────────────────────────────────────────────


def test_absence_de_c2pa_n_est_pas_une_erreur():
    r = extraire_c2pa(b"\xff\xd8\xff\xda\x00\x02\xff\xd9")
    assert r.present is False
    assert r.manifestes == ()
    assert r.conteneur is None


def test_manifeste_lu_dans_un_jpeg():
    r = extraire_c2pa(jpeg_avec_app11(manifeste_c2pa_synthetique()))
    assert r.present
    assert r.conteneur == "JPEG APP11 / JUMBF"
    assert len(r.manifestes) == 1
    m = r.manifestes[0]
    assert m.label == "urn:uuid:0000-essai"
    assert m.generateur == "essai-c2pa/0.1"
    assert m.algorithme_signature == "ps256"
    assert m.signature_presente is True


def test_actions_de_retouche_extraites():
    r = extraire_c2pa(jpeg_avec_app11(manifeste_c2pa_synthetique()))
    actions = [a["action"] for a in r.manifestes[0].actions]
    assert actions == ["c2pa.created", "c2pa.color_adjustments", "c2pa.cropped"]
    assert r.manifestes[0].actions[1]["softwareAgent"] == "Retoucheur 2.4"


def test_assertions_json_et_cbor_toutes_deux_lues():
    r = extraire_c2pa(jpeg_avec_app11(manifeste_c2pa_synthetique()))
    a = r.manifestes[0].assertions
    assert set(a) == {"c2pa.actions", "stds.schema-org.CreativeWork"}
    assert a["stds.schema-org.CreativeWork"]["author"][0]["name"] == "Anonyme"


def test_reassemblage_de_fragments_multiples():
    """Un manifeste plus grand qu'un segment APP11 est réparti, puis recollé.

    Un segment JPEG ne peut pas dépasser 65 533 octets : tout manifeste réel est
    fragmenté. Fragments de 40 octets ici, pour que le recollage soit franchement
    éprouvé.
    """
    magasin = manifeste_c2pa_synthetique()
    r = extraire_c2pa(jpeg_avec_app11(magasin, taille_fragment=40))
    assert r.present
    assert r.octets == len(magasin)
    assert len(r.manifestes) == 1
    assert len(r.manifestes[0].actions) == 3


def test_fragments_dans_le_desordre_sont_remis_en_ordre():
    """Les paquets sont triés par numéro de séquence, pas par ordre d'apparition."""
    magasin = manifeste_c2pa_synthetique()
    fragments = [magasin[i : i + 50] for i in range(0, len(magasin), 50)]
    segments = []
    for numero, fragment in enumerate(fragments, start=1):
        corps = b"JP" + struct.pack(">H", 1) + struct.pack(">I", numero) + fragment
        segments.append(b"\xff\xeb" + struct.pack(">H", len(corps) + 2) + corps)
    segments.reverse()  # ordre d'apparition inversé
    jpeg = b"\xff\xd8" + b"".join(segments) + b"\xff\xda\x00\x02\xff\xd9"
    r = extraire_c2pa(jpeg)
    assert len(r.manifestes) == 1
    assert len(r.manifestes[0].actions) == 3


def test_manifeste_lu_dans_un_png():
    magasin = manifeste_c2pa_synthetique()
    png = (b"\x89PNG\r\n\x1a\n"
           + struct.pack(">I", len(magasin)) + b"caBX" + magasin + b"\x00\x00\x00\x00"
           + struct.pack(">I", 0) + b"IEND" + b"\x00\x00\x00\x00")
    r = extraire_c2pa(png)
    assert r.present
    assert r.conteneur == "PNG caBX / JUMBF"
    assert len(r.manifestes) == 1


def test_aucune_signature_n_est_verifiee():
    """Le module ne doit jamais laisser croire qu'il valide quoi que ce soit.

    Le manifeste d'essai porte une « signature » de quatre octets arbitraires.
    Elle est signalée présente — c'est un fait sur la structure — et le résultat
    dit dans le même souffle qu'elle n'est pas vérifiée.
    """
    r = extraire_c2pa(jpeg_avec_app11(manifeste_c2pa_synthetique()))
    assert r.manifestes[0].signature_presente is True
    assert r.signature_verifiee is False
    assert "Aucune signature n'est vérifiée" in r.avertissement
    assert "COSE" in r.motif_non_verifiee
    # L'avertissement énumère les trois possibilités, dont « authentique » : le
    # mot doit y être. Ce qui est proscrit, c'est de l'AFFIRMER. Un premier jet
    # de ce test bannissait le mot lui-même et rejetait donc la formulation
    # honnête — c'est la tournure affirmative qu'il faut traquer.
    assert "entièrement fabriqué" in r.avertissement
    assert "ne les distingue pas" in r.avertissement
    for affirmation in (
        "est authentique", "est valide", "est certifié", "signature valide",
        "provenance vérifiée", "image authentifiée",
    ):
        assert affirmation not in r.avertissement.lower()


def test_c2pa_tronque_rend_ce_qui_est_lisible():
    """Un conteneur coupé en deux ne doit pas effacer ce qui précède la coupure."""
    magasin = manifeste_c2pa_synthetique()
    jpeg = jpeg_avec_app11(magasin[: len(magasin) // 2])
    r = extraire_c2pa(jpeg)
    assert r.present is True  # le conteneur EST là
    assert r.octets < len(magasin)


# ─────────────────────────────────────────────────────────────────────────────
# XMP
# ─────────────────────────────────────────────────────────────────────────────

XMP_EXEMPLE = (
    '<?xpacket begin="" id="W5M0MpCehiHzreSzNTczkc9d"?>'
    '<x:xmpmeta xmlns:x="adobe:ns:meta/">'
    '<rdf:RDF xmlns:rdf="http://www.w3.org/1999/02/22-rdf-syntax-ns#">'
    '<rdf:Description rdf:about="" '
    'xmlns:xmp="http://ns.adobe.com/xap/1.0/" '
    'xmlns:tiff="http://ns.adobe.com/tiff/1.0/" '
    'xmp:CreatorTool="Adobe Photoshop 25.0 (Windows)" '
    'xmp:ModifyDate="2026-09-05T10:14:22+02:00" '
    'tiff:Make="EssaiCorp">'
    '</rdf:Description></rdf:RDF></x:xmpmeta><?xpacket end="w"?>'
)


def jpeg_avec_xmp(xmp: str) -> bytes:
    corps = b"http://ns.adobe.com/xap/1.0/\x00" + xmp.encode()
    return (b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", len(corps) + 2) + corps
            + b"\xff\xda\x00\x02\xff\xd9")


def test_xmp_localise_et_champs_releves():
    blocs = extraire_xmp(jpeg_avec_xmp(XMP_EXEMPLE))
    assert len(blocs) == 1
    b = blocs[0]
    assert b.conteneur == "JPEG APP1 / XMP"
    assert b.champs["xmp:CreatorTool"] == "Adobe Photoshop 25.0 (Windows)"
    assert b.champs["xmp:ModifyDate"] == "2026-09-05T10:14:22+02:00"
    assert b.champs["tiff:Make"] == "EssaiCorp"
    assert b.brut.startswith("<?xpacket")


def jpeg_avec_xmp_etendu(xmp: str) -> bytes:
    """XMP étendu : 40 octets d'en-tête (GUID de 32 caractères, taille, offset)
    précèdent la charge utile. Les ignorer met 40 octets de binaire en tête du
    paquet et empêche d'y relever le moindre champ."""
    entete = b"A" * 32 + struct.pack(">II", len(xmp), 0)
    corps = b"http://ns.adobe.com/xmp/extension/\x00" + entete + xmp.encode()
    return (b"\xff\xd8" + b"\xff\xe1" + struct.pack(">H", len(corps) + 2) + corps
            + b"\xff\xda\x00\x02\xff\xd9")


def test_xmp_etendu_saute_son_entete():
    blocs = extraire_xmp(jpeg_avec_xmp_etendu(XMP_EXEMPLE))
    assert len(blocs) == 1
    b = blocs[0]
    assert b.etendu is True
    assert b.conteneur == "JPEG APP1 / XMP étendu"
    assert b.brut.startswith("<?xpacket")   # l'en-tête de 40 octets a bien été retiré
    assert b.champs["tiff:Make"] == "EssaiCorp"


def test_xmp_absent_rend_une_liste_vide():
    assert extraire_xmp(b"\xff\xd8\xff\xda\x00\x02\xff\xd9") == []


def test_xmp_dans_un_png():
    charge = b"XML:com.adobe.xmp\x00\x00\x00\x00\x00" + XMP_EXEMPLE.encode()
    png = (b"\x89PNG\r\n\x1a\n" + struct.pack(">I", len(charge)) + b"iTXt" + charge
           + b"\x00\x00\x00\x00" + struct.pack(">I", 0) + b"IEND\x00\x00\x00\x00")
    blocs = extraire_xmp(png)
    assert len(blocs) == 1
    assert blocs[0].champs["tiff:Make"] == "EssaiCorp"


# ─────────────────────────────────────────────────────────────────────────────
# IPTC
# ─────────────────────────────────────────────────────────────────────────────


def dataset_iim(numero: int, valeur: str) -> bytes:
    v = valeur.encode()
    return bytes([0x1C, 0x02, numero]) + struct.pack(">H", len(v)) + v


def jpeg_avec_iptc(datasets: bytes) -> bytes:
    ressource = (b"8BIM" + struct.pack(">H", 0x0404) + b"\x00\x00"
                 + struct.pack(">I", len(datasets)) + datasets
                 + (b"\x00" if len(datasets) % 2 else b""))
    corps = b"Photoshop 3.0\x00" + ressource
    return (b"\xff\xd8" + b"\xff\xed" + struct.pack(">H", len(corps) + 2) + corps
            + b"\xff\xda\x00\x02\xff\xd9")


def test_iptc_libelles_et_valeurs():
    datasets = (dataset_iim(80, "A. Photographe")
                + dataset_iim(120, "Vue de la digue au lever du jour")
                + dataset_iim(115, "Agence d'essai"))
    enr = extraire_iptc(jpeg_avec_iptc(datasets))
    assert [(e.numero, e.valeur) for e in enr] == [
        (80, "A. Photographe"),
        (120, "Vue de la digue au lever du jour"),
        (115, "Agence d'essai"),
    ]
    assert enr[0].libelle == "Auteur"
    assert enr[1].libelle == "Légende"


def test_iptc_champ_inconnu_garde_son_numero():
    enr = extraire_iptc(jpeg_avec_iptc(dataset_iim(199, "valeur")))
    assert enr[0].libelle == "jeu 2, champ 199"


def test_iptc_absent_rend_une_liste_vide():
    assert extraire_iptc(b"\xff\xd8\xff\xda\x00\x02\xff\xd9") == []


# ─────────────────────────────────────────────────────────────────────────────
# Chaînes
# ─────────────────────────────────────────────────────────────────────────────


def test_chaines_ascii_et_marqueur_reconnu():
    jpeg = jpeg_avec_xmp(XMP_EXEMPLE)
    chaines = extraire_chaines(jpeg)
    textes = [c.texte for c in chaines]
    assert any("Adobe Photoshop 25.0" in t for t in textes)
    marqueurs = {c.marqueur for c in chaines if c.marqueur}
    assert "Photoshop" in marqueurs or "Adobe" in marqueurs


def test_chaines_utf16_relevees():
    corps = b"\xff\xd8" + "Marqueur cache".encode("utf-16-le") + b"\xff\xda\x00\x02\xff\xd9"
    chaines = extraire_chaines(corps)
    assert any(c.encodage == "UTF-16LE" and "Marqueur cache" in c.texte for c in chaines)


def test_chaines_s_arretent_au_debut_des_donnees_image():
    """Au-delà du SOS, toute suite « lisible » est un artefact de compression.

    On place un texte manifeste APRÈS le SOS : il ne doit pas être relevé, sinon
    l'outil rapporterait comme métadonnée un hasard de l'entropie JPEG.
    """
    jpeg = (b"\xff\xd8" + b"\xff\xda\x00\x02"
            + b"CHAINE_APRES_LE_SOS_A_NE_PAS_RELEVER" + b"\xff\xd9")
    textes = [c.texte for c in extraire_chaines(jpeg)]
    assert not any("A_NE_PAS_RELEVER" in t for t in textes)


def test_chaines_sans_doublon():
    corps = b"\xff\xd8" + b"RepeteRepete " * 5 + b"\xff\xda\x00\x02\xff\xd9"
    textes = [c.texte for c in extraire_chaines(corps)]
    assert len(textes) == len(set(textes))


def test_longueur_minimale_respectee():
    corps = b"\xff\xd8" + b"abc " + b"suffisamment_long" + b"\xff\xda\x00\x02\xff\xd9"
    textes = [c.texte for c in extraire_chaines(corps, longueur_min=10)]
    assert all(len(t) >= 10 for t in textes)


# ─────────────────────────────────────────────────────────────────────────────
# Assemblage
# ─────────────────────────────────────────────────────────────────────────────


def test_analyse_complete_reunit_les_quatre_familles():
    magasin = manifeste_c2pa_synthetique()
    corps_xmp = b"http://ns.adobe.com/xap/1.0/\x00" + XMP_EXEMPLE.encode()
    datasets = dataset_iim(80, "A. Photographe")
    ressource = (b"8BIM" + struct.pack(">H", 0x0404) + b"\x00\x00"
                 + struct.pack(">I", len(datasets)) + datasets)
    corps_iptc = b"Photoshop 3.0\x00" + ressource
    fragments = [magasin[i : i + 5000] for i in range(0, len(magasin), 5000)]
    app11 = b""
    for numero, fragment in enumerate(fragments, start=1):
        c = b"JP" + struct.pack(">H", 1) + struct.pack(">I", numero) + fragment
        app11 += b"\xff\xeb" + struct.pack(">H", len(c) + 2) + c
    jpeg = (b"\xff\xd8"
            + b"\xff\xe1" + struct.pack(">H", len(corps_xmp) + 2) + corps_xmp
            + b"\xff\xed" + struct.pack(">H", len(corps_iptc) + 2) + corps_iptc
            + app11 + b"\xff\xda\x00\x02\xff\xd9")

    p = analyser_provenance(jpeg)
    assert p.c2pa.present and len(p.c2pa.manifestes) == 1
    assert len(p.xmp) == 1 and p.xmp[0].champs["tiff:Make"] == "EssaiCorp"
    assert len(p.iptc) == 1 and p.iptc[0].valeur == "A. Photographe"
    assert "Photoshop" in p.marqueurs_logiciels or "Adobe" in p.marqueurs_logiciels


def test_analyse_d_un_fichier_sans_rien():
    p = analyser_provenance(b"\xff\xd8\xff\xda\x00\x02\xff\xd9")
    assert p.c2pa.present is False
    assert p.xmp == () and p.iptc == ()
    assert p.marqueurs_logiciels == ()


def test_avertissement_toujours_joint():
    """Même sans C2PA, le résultat porte la phrase qui borne ce qu'il établit."""
    for donnees in (b"\xff\xd8\xff\xda\x00\x02\xff\xd9",
                    jpeg_avec_app11(manifeste_c2pa_synthetique())):
        assert analyser_provenance(donnees).c2pa.avertissement == AVERTISSEMENT_C2PA
