#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Les trois figures de la page « Qu'est-ce qu'un protocole ».

Elles sont générées plutôt qu'écrites à la main parce que deux d'entre elles
portent des grandeurs calculées — la géométrie de la dépression et l'échelle du
budget d'erreur. Une figure dont les coordonnées sont tapées au jugé finit par
mentir sur ce qu'elle illustre.
"""

import math

BG = "#0d1117"
BOITE = "#141b24"
BORD = "#2a3441"
TXT = "#c9d4e0"
MUET = "#7b8a9c"
ROSE = "#C45E6A"
CYAN = "#3B8FD4"
OR = "#B8941F"
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"


def entete(w, titre, sous):
    return (
        f'<rect x="0" y="0" width="{w}" height="100%" fill="{BG}"/>'
        f'<rect x="0" y="0" width="5" height="100%" fill="{ROSE}" opacity="0.85"/>'
        f'<text x="28" y="36" fill="{TXT}" font-family="{MONO}" font-size="16" '
        f'font-weight="700">{titre}</text>'
        f'<text x="28" y="58" fill="{MUET}" font-family="{MONO}" font-size="11.5">{sous}</text>'
    )


# ───────────────────────────── figure 1 : la géométrie ─────────────────────
def figure_geometrie():
    W, H = 1040, 500
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" data-zoomable="true" '
         f'role="img" aria-label="La depression de l horizon : ce que predit une sphere, '
         f'ce que predit un plan">']
    s.append(entete(W, "L&apos;OBSERVABLE — DÉPRESSION DE L&apos;HORIZON",
                    "Courbure très fortement exagérée. À 3 107 m d&apos;altitude, "
                    "δ vaut 100 minutes d&apos;arc, soit 1,7 degré."))

    # ---- panneau A : sphère -------------------------------------------------
    cx, cy, R = 270.0, 1200.0, 920.0
    ax, bx = 50.0, 560.0
    ay = cy - math.sqrt(R * R - (ax - cx) ** 2)
    by = cy - math.sqrt(R * R - (bx - cx) ** 2)
    ox, oy = 150.0, 200.0                       # l'œil
    d = math.hypot(ox - cx, oy - cy)
    theta = math.acos(R / d)                     # demi-angle au centre
    phi = math.atan2(ox - cx, cy - oy)           # direction centre → œil
    hx = cx + R * math.sin(phi + theta)
    hy = cy - R * math.cos(phi + theta)
    delta = math.degrees(math.atan2(hy - oy, hx - ox))

    s.append(f'<text x="50" y="110" fill="{CYAN}" font-family="{MONO}" font-size="12.5" '
             f'font-weight="700">SURFACE SPHÉRIQUE</text>')
    s.append(f'<path d="M {ax:.1f} {ay:.1f} A {R} {R} 0 0 1 {bx:.1f} {by:.1f}" fill="none" '
             f'stroke="{CYAN}" stroke-width="2.5"/>')
    # horizontale vraie
    s.append(f'<line x1="{ox}" y1="{oy}" x2="565" y2="{oy}" stroke="{OR}" stroke-width="1.8" '
             f'stroke-dasharray="7 5"/>')
    s.append(f'<text x="400" y="{oy - 10:.0f}" fill="{OR}" font-family="{MONO}" '
             f'font-size="11">horizontale vraie</text>')
    # ligne de visée
    s.append(f'<line x1="{ox}" y1="{oy}" x2="{hx:.1f}" y2="{hy:.1f}" stroke="{ROSE}" '
             f'stroke-width="2.2"/>')
    # arc de l'angle delta
    r0 = 130.0
    x1, y1 = ox + r0, oy
    x2 = ox + r0 * math.cos(math.radians(delta))
    y2 = oy + r0 * math.sin(math.radians(delta))
    s.append(f'<path d="M {x1:.1f} {y1:.1f} A {r0} {r0} 0 0 1 {x2:.1f} {y2:.1f}" fill="none" '
             f'stroke="{ROSE}" stroke-width="1.6"/>')
    s.append(f'<text x="{ox + r0 + 8:.0f}" y="{oy + 26:.0f}" fill="{ROSE}" font-family="{MONO}" '
             f'font-size="15" font-weight="700">δ &gt; 0</text>')
    # verticale de l'œil et hauteur h
    sy = cy - math.sqrt(R * R - (ox - cx) ** 2)
    s.append(f'<line x1="{ox}" y1="{oy}" x2="{ox}" y2="{sy:.1f}" stroke="{MUET}" '
             f'stroke-width="1.2" stroke-dasharray="3 4"/>')
    s.append(f'<text x="{ox - 42:.0f}" y="{(oy + sy) / 2:.0f}" fill="{MUET}" '
             f'font-family="{MONO}" font-size="13" font-weight="700">h</text>')
    s.append(f'<circle cx="{ox}" cy="{oy}" r="6" fill="{TXT}"/>')
    s.append(f'<text x="{ox - 8:.0f}" y="{oy - 16:.0f}" fill="{TXT}" font-family="{MONO}" '
             f'font-size="12" font-weight="700">œil</text>')
    s.append(f'<circle cx="{hx:.1f}" cy="{hy:.1f}" r="5" fill="{ROSE}"/>')
    s.append(f'<text x="{hx - 150:.0f}" y="{hy + 30:.0f}" fill="{ROSE}" font-family="{MONO}" '
             f'font-size="11">ligne d&apos;horizon</text>')
    s.append(f'<text x="50" y="404" fill="{TXT}" font-family="{MONO}" font-size="13" '
             f'font-weight="700">δ = arccos( R&#8242; / (R&#8242;+h) )  ≈  √(2h/R&#8242;)</text>')
    s.append(f'<text x="50" y="428" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'δ croît comme la racine de l&apos;altitude. 4&#8242; à 5 m, 100&#8242; à 3 107 m.</text>')
    s.append(f'<text x="50" y="450" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'R&#8242; = R/(1−k) absorbe la réfraction atmosphérique.</text>')

    # ---- séparateur ---------------------------------------------------------
    s.append(f'<line x1="588" y1="100" x2="588" y2="470" stroke="{BORD}" stroke-width="1.5"/>')

    # ---- panneau B : plan ---------------------------------------------------
    px0, px1, py = 630.0, 1000.0, 300.0
    pox, poy = 680.0, 200.0
    s.append(f'<text x="630" y="110" fill="{CYAN}" font-family="{MONO}" font-size="12.5" '
             f'font-weight="700">SURFACE PLANE</text>')
    s.append(f'<line x1="{px0}" y1="{py}" x2="{px1}" y2="{py}" stroke="{CYAN}" stroke-width="2.5"/>')
    s.append(f'<line x1="{pox}" y1="{poy}" x2="{px1 + 10}" y2="{poy}" stroke="{OR}" '
             f'stroke-width="1.8" stroke-dasharray="7 5"/>')
    s.append(f'<line x1="{pox}" y1="{poy}" x2="{px1 + 10}" y2="{poy}" stroke="{ROSE}" '
             f'stroke-width="2.2" stroke-dasharray="2 8"/>')
    s.append(f'<text x="790" y="{poy - 10:.0f}" fill="{OR}" font-family="{MONO}" '
             f'font-size="11">horizontale vraie</text>')
    s.append(f'<text x="760" y="{poy + 22:.0f}" fill="{ROSE}" font-family="{MONO}" '
             f'font-size="11">ligne d&apos;horizon, confondue</text>')
    s.append(f'<line x1="{pox}" y1="{poy}" x2="{pox}" y2="{py}" stroke="{MUET}" '
             f'stroke-width="1.2" stroke-dasharray="3 4"/>')
    s.append(f'<text x="{pox - 42:.0f}" y="{(poy + py) / 2:.0f}" fill="{MUET}" '
             f'font-family="{MONO}" font-size="13" font-weight="700">h</text>')
    s.append(f'<circle cx="{pox}" cy="{poy}" r="6" fill="{TXT}"/>')
    s.append(f'<text x="{pox - 8:.0f}" y="{poy - 16:.0f}" fill="{TXT}" font-family="{MONO}" '
             f'font-size="12" font-weight="700">œil</text>')
    s.append(f'<text x="{pox + 130:.0f}" y="{poy + 60:.0f}" fill="{ROSE}" font-family="{MONO}" '
             f'font-size="15" font-weight="700">δ = 0</text>')
    s.append(f'<text x="630" y="404" fill="{TXT}" font-family="{MONO}" font-size="13" '
             f'font-weight="700">δ = 0 à toute altitude</text>')
    s.append(f'<text x="630" y="428" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'Le point de fuite d&apos;un plan est dans le plan</text>')
    s.append(f'<text x="630" y="450" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'horizontal de l&apos;œil, quelle que soit sa hauteur.</text>')
    s.append("</svg>")
    return "".join(s)


# ───────────────────────── figure 2 : le budget d'erreur ───────────────────
def figure_budget():
    W, H = 1040, 520
    ECH = 6.0          # pixels par minute d'arc
    X0 = 258.0
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" data-zoomable="true" '
         f'role="img" aria-label="Ce qui separe les deux modeles, compare a ce que vaut '
         f'l incertitude de mesure">']
    s.append(entete(W, "POURQUOI LA QUESTION EST DÉCIDABLE",
                    "Toutes les barres à la même échelle. Station à 3 107 m d&apos;altitude, "
                    "1 minute d&apos;arc = 6 pixels."))

    lignes = [
        ("Sphère, réfraction standard", 100.1, "k = 0,13", CYAN, True),
        ("Sphère, cas le plus défavorable", 78.2, "k = 0,47", CYAN, True),
        ("Plan", 0.0, "à toute altitude", OR, True),
        (None, None, None, None, None),
        ("Budget instrumental, 1 σ", 2.20, "après retournement", ROSE, False),
        ("Budget total, 1 σ", 3.41, "modèle compris", ROSE, False),
    ]
    y = 132.0
    for nom, val, note, couleur, gros in lignes:
        if nom is None:
            s.append(f'<line x1="40" y1="{y + 6:.0f}" x2="1000" y2="{y + 6:.0f}" '
                     f'stroke="{BORD}" stroke-width="1.2" stroke-dasharray="4 5"/>')
            y += 34
            continue
        h = 26 if gros else 18
        s.append(f'<text x="{X0 - 14:.0f}" y="{y + h - 8:.0f}" fill="{TXT}" font-family="{MONO}" '
                 f'font-size="12" text-anchor="end">{nom}</text>')
        w = val * ECH
        if w < 1.5:
            s.append(f'<line x1="{X0}" y1="{y:.0f}" x2="{X0}" y2="{y + h:.0f}" '
                     f'stroke="{couleur}" stroke-width="3"/>')
        else:
            s.append(f'<rect x="{X0}" y="{y:.0f}" width="{w:.1f}" height="{h}" rx="2" '
                     f'fill="{couleur}" opacity="{0.85 if gros else 1.0}"/>')
        s.append(f'<text x="{X0 + max(w, 4) + 12:.0f}" y="{y + h - 6:.0f}" fill="{couleur}" '
                 f'font-family="{MONO}" font-size="13" font-weight="700">'
                 f'{("%.2f" % val).replace(".", ",") if not gros else ("%.1f" % val).replace(".", ",")}&#8242;</text>')
        s.append(f'<text x="{X0 + max(w, 4) + 78:.0f}" y="{y + h - 6:.0f}" fill="{MUET}" '
                 f'font-family="{MONO}" font-size="11">{note}</text>')
        y += h + 22

    y += 6
    s.append(f'<rect x="40" y="{y:.0f}" width="960" height="118" rx="3" fill="{BOITE}" '
             f'stroke="{BORD}" stroke-width="1"/>')
    s.append(f'<text x="62" y="{y + 30:.0f}" fill="{ROSE}" font-family="{MONO}" font-size="12" '
             f'font-weight="700">CE QUE DIT CE GRAPHIQUE</text>')
    s.append(f'<text x="62" y="{y + 56:.0f}" fill="{TXT}" font-family="{MONO}" font-size="12">'
             f'L&apos;écart entre les deux modèles vaut au minimum 78,2&#8242;. L&apos;incertitude '
             f'sur la mesure vaut 2,20&#8242;.</text>')
    s.append(f'<text x="62" y="{y + 78:.0f}" fill="{TXT}" font-family="{MONO}" font-size="12">'
             f'Rapport signal sur bruit : <tspan fill="{ROSE}" font-weight="700">35,5</tspan>. '
             f'La mesure tranche, et elle tranche largement.</text>')
    s.append(f'<text x="62" y="{y + 100:.0f}" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'C&apos;est ce rapport, calculé avant toute image, qui autorise à monter '
             f'l&apos;expérience. Sans lui, on ne sait pas ce qu&apos;on mesure.</text>')
    s.append("</svg>")
    return "".join(s)


# ─────────────────────── figure 3 : la chaîne des opérations ───────────────
def figure_chaine():
    W = 1040
    PHASES = [
        ("PHASE 0", "avant la première image",
         "Déposer le protocole, obtenir le DOI · fixer le critère de pointé · "
         "choisir l&apos;étagement des stations", True,
         "Tant que le DOI n&apos;est pas publié, ne rien photographier."),
        ("PHASE 1", "plusieurs jours avant",
         "Vérifier l&apos;azimut sur carte · établir l&apos;altitude de l&apos;œil · "
         "repérer la fenêtre · relever la marée", True,
         "Une côte lointaine dans l&apos;axe ne se voit pas sur la photo."),
        ("PHASE 2", "sur place, avant les images",
         "Sécurité · optique réglée, <tspan font-weight='700'>bague immobilisée</tspan> · plateau au repos · "
         "ΔT, mer, pression · cadrage à blanc", True,
         "ΔT, marée et état de la mer se relèvent maintenant, ou jamais."),
        ("PHASE 3", "acquisition",
         "Rafale de 20 images · trois séries à des heures distinctes · croiser les "
         "méthodes · <tspan font-weight='700'>pose de résolution</tspan>", True,
         "La pose de résolution oubliée coûte la soirée entière."),
        ("PHASE 4", "réduction, au bureau",
         "Résoudre le champ · contrôle astre-reflet à 0,5 % · pointer l&apos;horizon · "
         "réduire δ · transmettre", False,
         "Tout s&apos;exprime dans l&apos;échelle du champ : commencer par là."),
        ("PHASE 5", "toutes stations rentrées",
         "Régression pondérée de δ contre √h · ajustement à exposant libre · "
         "publier les brutes", False,
         "L&apos;exposant doit ressortir à 0,500, et sa barre d&apos;erreur le dit."),
    ]
    HB = 82
    ECART = 22
    H = 108 + len(PHASES) * (HB + ECART) + 46
    s = [f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" data-zoomable="true" '
         f'role="img" aria-label="Les six phases du protocole et leur ordre contraignant">']
    s.append(entete(W, "L&apos;ORDRE DES OPÉRATIONS — CE QUI NE SE RATTRAPE PAS",
                    "Chaque phase suppose la précédente accomplie. Les phases marquées "
                    "d&apos;un trait rose sont irréversibles."))
    y = 108.0
    for i, (nom, quand, contenu, irrev, note) in enumerate(PHASES):
        s.append(f'<rect x="40" y="{y:.0f}" width="960" height="{HB}" rx="3" fill="{BOITE}" '
                 f'stroke="{BORD}" stroke-width="1"/>')
        s.append(f'<rect x="40" y="{y:.0f}" width="4" height="{HB}" '
                 f'fill="{ROSE if irrev else CYAN}"/>')
        s.append(f'<text x="66" y="{y + 28:.0f}" fill="{ROSE if irrev else CYAN}" '
                 f'font-family="{MONO}" font-size="13" font-weight="700">{nom}</text>')
        s.append(f'<text x="66" y="{y + 48:.0f}" fill="{MUET}" font-family="{MONO}" '
                 f'font-size="10.5">{quand}</text>')
        s.append(f'<text x="230" y="{y + 30:.0f}" fill="{TXT}" font-family="{MONO}" '
                 f'font-size="11.5">{contenu}</text>')
        s.append(f'<text x="230" y="{y + 58:.0f}" fill="{ROSE if irrev else MUET}" '
                 f'font-family="{MONO}" font-size="10.5" font-style="italic">'
                 f'{"⚠ " if irrev else ""}{note}</text>')
        if i < len(PHASES) - 1:
            ym = y + HB
            s.append(f'<line x1="520" y1="{ym + 3:.0f}" x2="520" y2="{ym + ECART - 6:.0f}" '
                     f'stroke="{BORD}" stroke-width="2"/>')
            s.append(f'<path d="M 514 {ym + ECART - 10:.0f} L 520 {ym + ECART - 2:.0f} '
                     f'L 526 {ym + ECART - 10:.0f}" fill="none" stroke="{BORD}" '
                     f'stroke-width="2"/>')
        y += HB + ECART
    s.append(f'<text x="40" y="{y + 22:.0f}" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'Cinq choses ne se rattrapent jamais : l&apos;horodatage, la vérification '
             f'd&apos;azimut, l&apos;altitude au-dessus de la mer du moment,</text>')
    s.append(f'<text x="40" y="{y + 40:.0f}" fill="{MUET}" font-family="{MONO}" font-size="11">'
             f'les conditions atmosphériques du moment, et l&apos;immobilisation de la bague '
             f'de mise au point.</text>')
    s.append("</svg>")
    return "".join(s)


if __name__ == "__main__":
    import pathlib
    d = pathlib.Path(__file__).parent
    (d / "fig1.svg").write_text(figure_geometrie(), encoding="utf-8")
    (d / "fig2.svg").write_text(figure_budget(), encoding="utf-8")
    (d / "fig3.svg").write_text(figure_chaine(), encoding="utf-8")
    print("ok", [len(x) for x in (figure_geometrie(), figure_budget(), figure_chaine())])
