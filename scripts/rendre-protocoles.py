#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Rendu des protocoles de terrain en PDF.

Les sources vivent dans content/protocoles/. Ce sont des pages HTML autonomes,
mises en page pour le papier — format A4, sauts de page contrôlés, figures en
SVG inline. Le rendu passe par Chromium en mode impression, ce qui conserve les
figures en vectoriel et le texte en texte sélectionnable.

Les polices
───────────
Spectral, IBM Plex Sans et IBM Plex Mono sont intégrées en base64 dans
content/protocoles/polices.css, et injectées au rendu à la place du repère
« @@POLICES@@ ». Elles ne sont donc PAS dupliquées dans chaque source : le bloc
pèse 290 ko et il y a trois documents.

Ce détour vient d'une contrainte réelle : la politique réseau de l'environnement
de travail bloque fonts.googleapis.com, et un rendu sans polices retombait sur
Liberation et DejaVu sans le signaler. Les intégrer garantit que le PDF sort
identique partout, et qu'il se reconstruit sans accès réseau.
Récupérées depuis npm (@fontsource/*), licence SIL OFL.

Chromium
────────
Playwright est utilisé pour piloter Chromium, mais la version de navigateur
qu'il télécharge par défaut n'est pas celle qui est préinstallée ici. On lui
passe donc le chemin explicite, découvert sous /opt/pw-browsers.

    pip install playwright pymupdf
    python3 scripts/rendre-protocoles.py            # les protocoles actifs
    python3 scripts/rendre-protocoles.py soleil     # y compris un suspendu
"""

import glob
import os
import pathlib
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCES = RACINE / "content" / "protocoles"
SORTIE = RACINE / "content" / "protocoles" / "pdf"
MARQUE = "/* @@POLICES@@ — injecté au rendu depuis polices.css */"

DOCUMENTS = {
    "horizon-fr": (
        "horizon-fr.html",
        "Protocole-depression-horizon.pdf",
        "Mesure de la dépression de l'horizon marin — protocole ouvert v1.9",
    ),
    "horizon-en": (
        "horizon-en.html",
        "Horizon-Dip-Protocol.pdf",
        "Measuring the dip of the sea horizon — open protocol v1.9",
    ),
    "soleil": (
        "soleil-bilingue.html",
        "Protocole-diametre-solaire.pdf",
        "Diamètre angulaire du Soleil — Angular diameter of the Sun — v1.4",
    ),
    "ballon": (
        "ballon-bilingue.html",
        "Protocole-ballon-stratospherique.pdf",
        "Dépression de l'horizon depuis un ballon — Horizon dip from a balloon — v1.1",
    ),
    "pole": (
        "pole-celeste-bilingue.html",
        "Protocole-pole-celeste.pdf",
        "Hauteur du pôle céleste — Altitude of the celestial pole — v1.3",
    ),
    "krequis": (
        "k-requis-bilingue.html",
        "Protocole-refraction-exigee.pdf",
        "Quelle réfraction faudrait-il pour voir cet objet — What refraction would be needed",
    ),
    "photo": (
        "analyse-photo-bilingue.html",
        "Protocole-analyse-photographique.pdf",
        "Photographie d'un objet éloigné — Photograph of a distant object — v2.1",
    ),
    "court": (
        "masquage-court.html",
        "Protocole-court-masquage.pdf",
        "Compatibilité d'une observation avec R = 6 371 km — protocole de terrain",
    ),
    "visee": (
        "visee-terrestre-bilingue.html",
        "Protocole-portion-masquee.pdf",
        "Portion masquée d'un objet éloigné — Hidden portion of a distant object — v3.0",
    ),
}

# Protocoles SUSPENDUS : les sources restent, le rendu par défaut les ignore.
#
# Le diamètre solaire et la hauteur du pôle céleste ont été écrits sans que
# leur auteur ait transmis tout ce qu'il sait de ces deux expériences. Un
# protocole incomplet qui a l'air fini est pire qu'un protocole absent : on le
# diffuse, on le dépose, et l'erreur voyage. Ils sont donc gelés jusqu'à ce que
# les informations manquantes arrivent.
#
# Ils restent rendables à la demande — « rendre-protocoles.py soleil » — mais
# ne sortent plus quand on lance le script sans argument.
SUSPENDUS = {"soleil", "pole", "visee", "court", "krequis"}


def chromium():
    """Chemin du Chromium préinstallé, ou None pour laisser Playwright choisir."""
    for motif in ("/opt/pw-browsers/chromium-*/chrome-linux/chrome",
                  "/opt/pw-browsers/chromium/chrome-linux/chrome"):
        trouve = sorted(glob.glob(motif))
        if trouve:
            return trouve[-1]
    return None


def preparer(source):
    """Rend le HTML complet, polices injectées, dans un fichier temporaire.

    Le fichier temporaire est écrit à côté de la source : Chromium le charge par
    une URL file://, et les chemins relatifs doivent rester valides.
    """
    polices = (SOURCES / "polices.css").read_text(encoding="utf-8")
    html = (SOURCES / source).read_text(encoding="utf-8")
    if MARQUE not in html:
        raise SystemExit("  ✗ repère de polices absent de %s" % source)
    html = html.replace(MARQUE, polices, 1)
    tmp = SOURCES / ("._rendu_" + source)
    tmp.write_text(html, encoding="utf-8")
    return tmp


def rendre(cle):
    from playwright.sync_api import sync_playwright

    source, pdf, entete = DOCUMENTS[cle]
    tmp = preparer(source)
    SORTIE.mkdir(parents=True, exist_ok=True)
    cible = SORTIE / pdf
    exe = chromium()
    try:
        with sync_playwright() as p:
            nav = p.chromium.launch(executable_path=exe, args=["--no-sandbox"])
            page = nav.new_page()
            page.goto(tmp.resolve().as_uri(), wait_until="networkidle")
            # Les @font-face en base64 sont décodées de façon asynchrone ; sans
            # cette attente le premier rendu sort parfois en police de repli.
            page.wait_for_timeout(1500)
            page.emulate_media(media="print")
            page.pdf(
                path=str(cible), format="A4", print_background=True,
                margin={"top": "19mm", "bottom": "16mm",
                        "left": "17mm", "right": "17mm"},
                display_header_footer=True,
                header_template=(
                    '<div style="font-size:7px;color:#8b96a0;width:100%;'
                    'padding:0 17mm;font-family:sans-serif;">' + entete + '</div>'),
                footer_template=(
                    '<div style="font-size:7px;color:#8b96a0;width:100%;'
                    'padding:0 17mm;text-align:right;font-family:sans-serif;">'
                    '<span class="pageNumber"></span> / '
                    '<span class="totalPages"></span></div>'),
            )
            nav.close()
    finally:
        tmp.unlink(missing_ok=True)

    pages = "?"
    try:
        import pymupdf
        pages = pymupdf.open(str(cible)).page_count
    except Exception:
        pass
    print("  ✓ %-34s %s pages, %d ko"
          % (pdf, pages, cible.stat().st_size // 1024))


def main():
    demandes = sys.argv[1:] or [c for c in DOCUMENTS if c not in SUSPENDUS]
    inconnus = [d for d in demandes if d not in DOCUMENTS]
    if inconnus:
        print("  ✗ inconnu : %s" % ", ".join(inconnus))
        print("    disponibles : %s" % ", ".join(DOCUMENTS))
        return 1
    print("Rendu des protocoles → %s" % os.path.relpath(SORTIE, RACINE))
    exe = chromium()
    print("  Chromium : %s" % (exe or "celui de Playwright"))
    for cle in demandes:
        rendre(cle)
    return 0


if __name__ == "__main__":
    sys.exit(main())
