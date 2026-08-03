#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere les schemas du dispositif de la campagne cote, dans public/schemas/.

  1. dispositif-ensemble.svg    — les trois perches sur le plan d'eau
  2. puits-tranquillisation.svg — coupe d'une perche et de son puits
  3. lecture-visee.svg          — ce que voit l'observateur dans la lunette

Fond sombre #0d1117, police mono, palette Observatoire. Chaque fichier porte
data-zoomable="true" : la valeur est OBLIGATOIRE, un .svg autonome etant parse
en XML strict et non en HTML, ou l'attribut nu serait accepte.

Le script verifie deux choses avant d'ecrire :
  - aucun texte ne sort du viewBox ;
  - aucun texte n'en chevauche un autre (boites englobantes).
"""
import math, os, re, sys

BG, GRID, INK, MUT = "#0d1117", "#1f2733", "#c9d4e0", "#7b8a9c"
CY, RO, GO, LV, OP = "#3B8FD4", "#C45E6A", "#B8941F", "#8B7EC8", "#3D9E7C"
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"
CHW = 0.605          # largeur d'un caractere, en fraction de la taille de police

class Vue:
    """Accumule le SVG et les boites de texte, pour le controle de collision."""
    def __init__(self, w, h, titre, sous, aria):
        self.w, self.h, self.g, self.boxes = w, h, [], []
        self.rect(0, 0, w, h, BG)
        self.txt(28, 36, titre, INK, 16, "700")
        self.txt(28, 58, sous, MUT, 11.5)
        self.aria = aria

    def raw(self, s): self.g.append(s)
    def rect(self, x, y, w, h, fill, stroke=None, sw=1, rx=0, op=1):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
        self.g.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" '
                      f'fill="{fill}" opacity="{op}"{st}/>')
    def line(self, x1, y1, x2, y2, col, sw=1, dash=None, cap=None):
        d = f' stroke-dasharray="{dash}"' if dash else ''
        c = f' stroke-linecap="{cap}"' if cap else ''
        self.g.append(f'<line x1="{x1:.1f}" y1="{y1:.1f}" x2="{x2:.1f}" y2="{y2:.1f}" '
                      f'stroke="{col}" stroke-width="{sw}"{d}{c}/>')
    def circ(self, cx, cy, r, fill="none", stroke=None, sw=1, op=1):
        st = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
        self.g.append(f'<circle cx="{cx:.1f}" cy="{cy:.1f}" r="{r}" fill="{fill}" opacity="{op}"{st}/>')

    def txt(self, x, y, s, fill=INK, size=12, weight="400", anchor="start"):
        larg = len(s) * size * CHW
        x0 = x - larg / 2 if anchor == "middle" else (x - larg if anchor == "end" else x)
        self.boxes.append((x0, y - size * 0.80, x0 + larg, y + size * 0.28, s))
        a = f' text-anchor="{anchor}"' if anchor != "start" else ''
        self.g.append(f'<text x="{x:.1f}" y="{y:.1f}" fill="{fill}" font-family="{MONO}" '
                      f'font-size="{size}" font-weight="{weight}"{a}>{s}</text>')

    def bloc(self, x, y, lignes, inter=19):
        """Paragraphe d'annotation : liste de (texte, couleur, taille, graisse)."""
        for i, l in enumerate(lignes):
            t, c, sz, w = (l + (None,) * 4)[:4]
            self.txt(x, y + i * inter, t, c or MUT, sz or 11.5, w or "400")
        return y + (len(lignes) - 1) * inter

    def amorce(self, x1, y1, x2, y2, col=MUT):
        """Ligne d'amorce entre une annotation et l'element qu'elle designe."""
        self.line(x1, y1, x2, y2, col, 0.9, "3 3")

    def cote_h(self, x1, x2, y, label, col=MUT, size=11):
        self.line(x1, y, x2, y, col, 1)
        for x in (x1, x2): self.line(x, y - 4, x, y + 4, col, 1)
        self.txt((x1 + x2) / 2, y - 7, label, col, size, anchor="middle")

    def cote_v(self, x, y1, y2, label, col=MUT, size=11):
        self.line(x, y1, x, y2, col, 1)
        for y in (y1, y2): self.line(x - 4, y, x + 4, y, col, 1)
        self.txt(x - 8, (y1 + y2) / 2 + 4, label, col, size, anchor="end")

    def rendu(self):
        return (f'<svg viewBox="0 0 {self.w} {self.h}" xmlns="http://www.w3.org/2000/svg" '
                f'data-zoomable="true" role="img" aria-label="{self.aria}">\n'
                + "\n".join(self.g) + "\n</svg>\n")

    def controle(self, nom):
        pb = 0
        for x0, y0, x1, y1, s in self.boxes:
            if x0 < -1 or x1 > self.w + 1 or y0 < 0 or y1 > self.h:
                print(f"  [{nom}] HORS CADRE  «{s[:46]}»  x[{x0:.0f},{x1:.0f}] y[{y0:.0f},{y1:.0f}]")
                pb += 1
        for i in range(len(self.boxes)):
            for j in range(i + 1, len(self.boxes)):
                a, b = self.boxes[i], self.boxes[j]
                ox = min(a[2], b[2]) - max(a[0], b[0])
                oy = min(a[3], b[3]) - max(a[1], b[1])
                if ox > 2 and oy > 1:
                    print(f"  [{nom}] CHEVAUCHE   «{a[4][:34]}» / «{b[4][:34]}»  ({ox:.0f}x{oy:.0f} px)")
                    pb += 1
        return pb


# ═══════════════════════════════════════════════════════════════════════════
# 1. VUE D'ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════
def vue_ensemble():
    v = Vue(1040, 600,
            "DISPOSITIF A TROIS MIRES — VUE D'ENSEMBLE",
            "Courbure verticale fortement exageree. A 10 km la fleche reelle vaut 1,96 m pour 4,00 m de perche.",
            "Vue d ensemble du dispositif a trois perches sur un plan d eau")

    XA, XB, XC = 150, 500, 850
    EAU_MIL, BOMBE, HP = 420, 58, 150     # y de l'eau au milieu, bombement, hauteur perche
    def eau(x):
        t = (x - XB) / (XC - XB)
        return EAU_MIL + BOMBE * t * t

    yA, yB, yC = eau(XA), eau(XB), eau(XC)
    sA, sB, sC = yA - HP, yB - HP, yC - HP
    sMid = (sA + sC) / 2                   # la corde, a l'aplomb de B

    # ── plan d'eau ────────────────────────────────────────────────────────
    pts = " ".join(f"{x},{eau(x):.1f}" for x in range(70, 971, 10))
    v.raw(f'<path d="M 70,{eau(70):.1f} L {pts.replace(" ", " L ")} L 970,{v.h-70} L 70,{v.h-70} Z" '
          f'fill="{CY}" opacity="0.055"/>')
    v.raw(f'<polyline points="{pts}" fill="none" stroke="{CY}" stroke-width="2.5"/>')

    # ── perches ───────────────────────────────────────────────────────────
    def perche(x, yb, ys, col, graduee=False):
        v.line(x, yb, x, ys, col, 3.5, cap="round")
        v.rect(x - 9, yb - 22, 18, 46, "none", OP, 1.6, 3)          # puits
        for dy in (10, 17, 24):
            v.line(x - 9, yb + dy, x - 4.5, yb + dy, OP, 1)
            v.line(x + 4.5, yb + dy, x + 9, yb + dy, OP, 1)
        v.rect(x - 12, yb + 28, 24, 8, MUT, rx=2, op=0.55)          # lest
        if graduee:
            for i in range(13):
                yy = ys + i * 8
                v.line(x + 3, yy, x + 3 + (11 if i % 4 == 0 else 6), yy, GO, 1.3)

    perche(XA, yA, sA, INK)
    perche(XB, yB, sB, GO, graduee=True)
    perche(XC, yC, sC, INK)
    v.txt(XA, yA + 52, "A", INK, 15, "700", "middle")
    v.txt(XB, yB + 52, "B", GO, 15, "700", "middle")
    v.txt(XC, yC + 52, "C", INK, 15, "700", "middle")

    # ── visee et fleche ───────────────────────────────────────────────────
    v.line(XA, sA, XC, sC, RO, 2, "8 5")
    v.circ(XB, sB, 4.5, GO); v.circ(XB, sMid, 4.5, RO)
    # cote laterale : sans elle, la fleche se confond avec le mat
    XF = XB - 26
    v.line(XB - 6, sB, XF - 8, sB, GO, 0.9, "3 3")
    v.line(XB - 6, sMid, XF - 8, sMid, GO, 0.9, "3 3")
    v.line(XF, sB, XF, sMid, GO, 2.4)
    v.line(XF - 6, sB, XF + 6, sB, GO, 2)
    v.line(XF - 6, sMid, XF + 6, sMid, GO, 2)
    v.txt(XF - 12, (sB + sMid) / 2 + 5, "f", GO, 15, "700", "end")

    # lunette
    v.circ(XA, sA, 7, "none", LV, 2)
    v.line(XA - 24, sA - 15, XA - 7, sA - 4, LV, 2)

    # ── annotations, toutes au-dessus de la visee ou hors du dessin ───────
    v.txt(XA - 30, sA - 20, "lunette", LV, 11.5, anchor="end")
    v.txt(360, 120, "ligne de visee A vers C", RO, 13, "700")
    v.txt(360, 139, "une droite — rien ne la recale en chemin", MUT, 11.5)
    v.amorce(430, 146, 430, sA - 4, RO)

    v.txt(560, 214, "f — LA FLECHE", GO, 13, "700")
    v.txt(560, 233, "de combien le sommet de B", MUT, 11.5)
    v.txt(560, 252, "depasse la corde A-C", MUT, 11.5)
    v.txt(560, 271, "c'est le seul nombre a relever", INK, 11.5)
    v.amorce(552, 240, XB + 8, (sB + sMid) / 2, GO)

    v.txt(772, 120, "puits de tranquillisation", OP, 12, "700")
    v.txt(772, 139, "a la base de chaque perche", MUT, 11.5)
    v.amorce(850, 146, XC - 6, yC - 26, OP)

    v.txt(268, eau(410) - 22, "plan d'eau sans maree", CY, 11.5)

    # ── cotes ─────────────────────────────────────────────────────────────
    v.line(XC, sC, XC + 62, sC, MUT, 0.8, "3 3")
    v.line(XC, yC, XC + 62, yC, MUT, 0.8, "3 3")
    v.cote_v(XC + 56, sC, yC, "4,00 m", MUT, 12)

    v.cote_h(XA, XB, v.h - 54, "D / 2")
    v.cote_h(XB, XC, v.h - 54, "D / 2")
    v.cote_h(XA, XC, v.h - 20, "D  =  1 · 1,5 · 2 · 3 · 5 · 7 · 10 km — sept configurations", GO, 12)

    # ── encart des deux predictions, en haut a gauche (zone libre) ────────
    v.rect(28, 92, 300, 92, "none", GRID, 1, 6)
    v.txt(44, 114, "MODELE PLAN", RO, 11.5, "700")
    v.txt(44, 133, "f = 0 — la lecture vaut 4,000 m", INK, 11.5)
    v.txt(44, 152, "a toute distance", INK, 11.5)
    v.txt(44, 173, "SPHERIQUE   f = (1-k) · D² / 8R", CY, 11.5, "700")
    return v


# ═══════════════════════════════════════════════════════════════════════════
# 2. PUITS DE TRANQUILLISATION — coupe
# ═══════════════════════════════════════════════════════════════════════════
def vue_puits():
    v = Vue(1080, 640,
            "LE PUITS DE TRANQUILLISATION — COUPE D'UNE PERCHE",
            "La piece qui decide de tout : sans elle, la lecture de la ligne d'eau vaut 100 mm et ecrase le signal.",
            "Coupe d une perche et de son puits de tranquillisation")

    XT, EAU = 300, 330          # axe de la perche, niveau moyen
    TR, SOM, FOND = 44, 108, 560   # demi-largeur du tube, sommet, fond du tube
    COL = 470                   # colonne d'annotations
    BOX = 790                   # encart chiffre

    # ── eau libre, de part et d'autre du tube ─────────────────────────────
    BORD_EAU = 452                # le plan d'eau s'arrete avant la colonne de texte
    v.rect(40, EAU, BORD_EAU - 40, v.h - EAU - 46, CY, op=0.06)
    for x0, x1 in ((40, XT - TR), (XT + TR, BORD_EAU)):
        d = f"M {x0} {EAU}"
        for x in range(int(x0), int(x1), 12):
            d += f" Q {x+3},{EAU-11} {x+6},{EAU} T {x+12},{EAU}"
        v.raw(f'<path d="{d}" fill="none" stroke="{CY}" stroke-width="2.2"/>')

    # ── tube ──────────────────────────────────────────────────────────────
    v.rect(XT - TR, EAU - 54, 2 * TR, FOND - EAU + 54, BG, OP, 2.4, 5)
    v.rect(XT - TR, EAU - 54, 2 * TR, 54, OP, op=0.05)
    v.line(XT - TR, EAU, XT + TR, EAU, OP, 2.8)
    for i in range(6):
        yy = EAU + 62 + i * 30
        v.circ(XT - TR, yy, 3.4, "none", OP, 1.4)
        v.circ(XT + TR, yy, 3.4, "none", OP, 1.4)

    # ── perche et mire ────────────────────────────────────────────────────
    v.line(XT, FOND - 20, XT, SOM, GO, 5, cap="round")
    for i in range(23):
        yy = SOM + i * 8.6
        v.line(XT + 6, yy, XT + 6 + (17 if i % 5 == 0 else 10), yy, GO, 1.4)
    v.circ(XT, SOM, 5.5, RO)
    v.rect(XT - 34, v.h - 40, 68, 12, MUT, rx=3, op=0.6)

    # ── cote 4,00 m, a gauche, dans une bande libre ───────────────────────
    v.line(XT - 6, SOM, XT - 136, SOM, INK, 0.8, "3 3")
    v.line(XT - TR, EAU, XT - 136, EAU, INK, 0.8, "3 3")
    v.cote_v(XT - 130, SOM, EAU, "4,00 m", INK, 13)

    # ── colonne d'annotations ─────────────────────────────────────────────
    v.txt(COL, 118, "sommet — origine de la mesure", RO, 12, "700")
    v.amorce(COL - 10, 114, XT + 10, SOM, RO)

    y = v.bloc(COL, 166, [("mire graduee au millimetre", GO, 12, "700"),
                          ("sur les 2,50 m superieurs", None, 11.5, None),
                          ("perche B uniquement", None, 11.5, None)])
    v.amorce(COL - 10, 170, XT + 26, 180, GO)

    y = v.bloc(COL, 258, [("eau calme dans le tube  ±5 mm", OP, 12, "700"),
                          ("c'est la ligne que l'on lit", None, 11.5, None)])
    v.amorce(COL - 10, 262, XT + TR + 6, EAU, OP)

    y = v.bloc(COL, 330, [("puits de tranquillisation", OP, 12, "700"),
                          ("tube PVC de 75 a 100 mm,", None, 11.5, None),
                          ("solidaire de la perche", None, 11.5, None)])
    v.amorce(COL - 10, 334, XT + TR + 6, EAU + 40, OP)

    y = v.bloc(COL, 428, [("percements fins de 8 mm", OP, 12, "700"),
                          ("ils laissent passer le niveau", None, 11.5, None),
                          ("moyen, pas les vagues", None, 11.5, None)])
    v.amorce(COL - 10, 432, XT + TR + 6, EAU + 122, OP)

    v.txt(COL, 526, "lest et ancrage sur le fond", MUT, 12, "700")
    v.amorce(COL - 10, 522, XT + 40, v.h - 34, MUT)

    v.txt(48, EAU + 46, "clapot libre  ±100 mm", CY, 12, "700")
    v.txt(48, EAU + 65, "la ligne d'eau y est", MUT, 11)
    v.txt(48, EAU + 82, "indeterminee", MUT, 11)
    v.txt(48, 556, "tout se mesure", MUT, 11)
    v.txt(48, 573, "DEPUIS la ligne d'eau,", MUT, 11)
    v.txt(48, 590, "jamais depuis le fond", MUT, 11)

    # ── encart chiffre ────────────────────────────────────────────────────
    v.rect(BOX, 100, 262, 168, "none", GRID, 1, 6)
    v.txt(BOX + 16, 126, "CE QUE CA CHANGE, A 1 km", GO, 11.5, "700")
    v.txt(BOX + 16, 152, "fleche attendue", CY, 11)
    v.txt(BOX + 16, 170, "19,6 mm", CY, 13, "700")
    v.txt(BOX + 16, 198, "sans puits      70,9 mm   S/B  0,3", MUT, 10.5)
    v.txt(BOX + 16, 218, "avec puits       5,9 mm   S/B  2,9", INK, 10.5)
    v.txt(BOX + 16, 238, "+ 10 seances     1,9 mm   S/B 10,5", OP, 10.5, "700")
    v.txt(BOX + 16, 258, "ecart-type d'une lecture", MUT, 10)
    return v


# ═══════════════════════════════════════════════════════════════════════════
# 3. CE QUE VOIT L'OBSERVATEUR
# ═══════════════════════════════════════════════════════════════════════════
def vue_lecture():
    v = Vue(980, 600,
            "CE QUE VOIT L'OBSERVATEUR — MEME VISEE, DEUX MODELES",
            "Oeil au sommet de A, reticule pose sur le sommet de C. On lit la graduation de B au croisement.",
            "Ce que voit l observateur dans la lunette sous chaque modele")

    CYY, RR = 320, 132
    def oculaire(cx, titre, sous, coul, f_px, lecture):
        v.circ(cx, CYY, RR, "#060a0f", coul, 2.5)
        # reticule : la visee A vers C
        v.line(cx - RR + 12, CYY, cx + RR - 12, CYY, MUT, 1, "5 4")
        v.line(cx, CYY - RR + 12, cx, CYY + RR - 12, MUT, 1, "5 4")
        # mire B, sommet a f_px au-dessus du reticule
        top = CYY - f_px
        v.rect(cx - 7, top, 14, RR - 14 + f_px, GO, op=0.22)
        n = int((RR - 20 + f_px) / 9)
        for i in range(n):
            yy = top + i * 9
            v.line(cx + 7, yy, cx + 7 + (14 if i % 5 == 0 else 8), yy, GO, 1.2)
        v.circ(cx, top, 4.5, GO)
        # sommet de C, sur le reticule
        v.circ(cx + RR - 40, CYY, 5, RO)
        v.txt(cx + RR - 40, CYY + 24, "C", RO, 12, "700", "middle")
        # point de lecture
        v.circ(cx, CYY, 5, coul)
        v.txt(cx, CYY - RR - 44, titre, coul, 14, "700", "middle")
        v.txt(cx, CYY - RR - 24, sous, MUT, 11, anchor="middle")
        v.txt(cx, CYY + RR + 34, lecture, coul, 13, "700", "middle")
        return top

    oculaire(250, "MODELE PLAN", "le sommet de B est sur le reticule", RO, 0,
             "lecture = 4,000 m")
    top = oculaire(730, "MODELE SPHERIQUE", "le sommet de B monte au-dessus", CY, 62,
                   "lecture = 2,293 m   (a 10 km)")
    v.line(730 - 18, CYY, 730 - 18, top, GO, 3)
    v.line(730 - 26, CYY, 730 - 10, CYY, GO, 1.6)
    v.line(730 - 26, top, 730 - 10, top, GO, 1.6)
    v.txt(730 - 34, CYY - 28, "f = 1,707 m", GO, 12.5, "700", anchor="end")

    v.txt(490, 526, "Un seul nombre a relever. Pas d'angle, pas de reduction,", MUT, 12, anchor="middle")
    v.txt(490, 548, "pas de systeme de coordonnees, pas d'unite imposee.", MUT, 12, anchor="middle")
    return v


# ═══════════════════════════════════════════════════════════════════════════
if __name__ == "__main__":
    os.makedirs("public/schemas", exist_ok=True)
    pb = 0
    for nom, fn in [("dispositif-ensemble", vue_ensemble),
                    ("puits-tranquillisation", vue_puits),
                    ("lecture-visee", vue_lecture)]:
        v = fn()
        pb += v.controle(nom)
        s = v.rendu()
        open(f"public/schemas/{nom}.svg", "w", encoding="utf-8").write(s)
        print(f"  ecrit  public/schemas/{nom}.svg  ({len(s)} octets, {v.w}x{v.h}, {len(v.boxes)} textes)")
    print("controle :", "AUCUN DEBORDEMENT NI CHEVAUCHEMENT" if pb == 0 else f"{pb} PROBLEME(S)")
    sys.exit(1 if pb else 0)
