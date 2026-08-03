#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Genere les schemas du dispositif de la campagne cote, dans public/schemas/.

Trois vues :
  1. dispositif-ensemble.svg  — les trois perches sur le plan d'eau
  2. puits-tranquillisation.svg — coupe d'une perche et de son puits
  3. lecture-visee.svg        — ce que voit l'observateur dans la lunette

Fond sombre #0d1117, police mono, palette Observatoire. Chaque fichier porte
data-zoomable pour la lightbox du site.
"""
import math, os, re

BG, GRID, INK, MUT = "#0d1117", "#1f2733", "#c9d4e0", "#7b8a9c"
CY, RO, GO, LV, OP = "#3B8FD4", "#C45E6A", "#B8941F", "#8B7EC8", "#3D9E7C"
MONO = "ui-monospace, SFMono-Regular, Menlo, monospace"
R = 6_371_008.8

def txt(x, y, s, fill=INK, size=12, weight="400", anchor="start", style=""):
    a = f' text-anchor="{anchor}"' if anchor != "start" else ""
    st = f' font-style="{style}"' if style else ""
    return (f'<text x="{x}" y="{y}" fill="{fill}" font-family="{MONO}" '
            f'font-size="{size}" font-weight="{weight}"{a}{st}>{s}</text>')

def cote(x1, y1, x2, y2, label, col=MUT, size=11, dy=-6):
    """Ligne de cote avec embouts."""
    g = f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{col}" stroke-width="1"/>'
    if y1 == y2:
        g += (f'<line x1="{x1}" y1="{y1-4}" x2="{x1}" y2="{y1+4}" stroke="{col}" stroke-width="1"/>'
              f'<line x1="{x2}" y1="{y2-4}" x2="{x2}" y2="{y2+4}" stroke="{col}" stroke-width="1"/>')
        g += txt((x1+x2)/2, y1+dy, label, col, size, anchor="middle")
    else:
        g += (f'<line x1="{x1-4}" y1="{y1}" x2="{x1+4}" y2="{y1}" stroke="{col}" stroke-width="1"/>'
              f'<line x1="{x2-4}" y1="{y2}" x2="{x2+4}" y2="{y2}" stroke="{col}" stroke-width="1"/>')
        g += txt(x1+8, (y1+y2)/2+4, label, col, size)
    return g

# ═══════════════════════════════════════════════════════════════════════════
# 1. VUE D'ENSEMBLE
# ═══════════════════════════════════════════════════════════════════════════
W, H = 920, 560
def arc(x):                       # surface de l'eau, courbure exageree
    t = (x - 460) / 380.0
    return 372 + 62 * t * t

pts = " ".join(f"{x},{arc(x):.1f}" for x in range(50, 871, 8))
XA, XB, XC = 110, 460, 810
yA, yB, yC = arc(XA), arc(XB), arc(XC)
HP = 168                          # 4,00 m a l'echelle du dessin
sA, sB, sC = yA - HP, yB - HP, yC - HP
sMid = (sA + sC) / 2

def perche(x, ybase, ysom, coul, lettre, graduee=False):
    g = f'<line x1="{x}" y1="{ybase:.1f}" x2="{x}" y2="{ysom:.1f}" stroke="{coul}" stroke-width="3.5" stroke-linecap="round"/>'
    # puits de tranquillisation
    g += (f'<rect x="{x-9}" y="{ybase-26:.1f}" width="18" height="52" rx="3" fill="none" '
          f'stroke="{OP}" stroke-width="1.6"/>')
    for dy in (12, 19, 26):
        g += (f'<line x1="{x-9}" y1="{ybase+dy:.1f}" x2="{x-4}" y2="{ybase+dy:.1f}" stroke="{OP}" stroke-width="1"/>'
              f'<line x1="{x+4}" y1="{ybase+dy:.1f}" x2="{x+9}" y2="{ybase+dy:.1f}" stroke="{OP}" stroke-width="1"/>')
    # lest
    g += f'<rect x="{x-13}" y="{ybase+30:.1f}" width="26" height="9" rx="2" fill="{MUT}" opacity="0.55"/>'
    if graduee:
        for i in range(11):
            yy = ysom + i * 9
            lg = 11 if i % 5 == 0 else 6
            g += f'<line x1="{x+3}" y1="{yy:.1f}" x2="{x+3+lg}" y2="{yy:.1f}" stroke="{GO}" stroke-width="1.3"/>'
    g += txt(x, ybase + 58, lettre, coul, 15, "700", "middle")
    return g

svg1 = f'''<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" data-zoomable role="img" aria-label="Vue d ensemble du dispositif a trois perches sur un plan d eau">
<rect width="{W}" height="{H}" fill="{BG}"/>
{txt(28, 36, "DISPOSITIF A TROIS MIRES — VUE D'ENSEMBLE", INK, 16, "700")}
{txt(28, 58, "Courbure verticale fortement exageree. A 10 km la fleche reelle vaut 1,96 m pour 4,00 m de perche.", MUT, 11.5)}

<polyline points="{pts}" fill="none" stroke="{CY}" stroke-width="2.5" opacity="0.9"/>
<path d="M50,{arc(50):.1f} {pts.replace(' ', ' L')} L870,{arc(870):.1f} L870,{H-70} L50,{H-70} Z" fill="{CY}" opacity="0.05"/>
{txt(700, arc(760)+78, "plan d'eau sans maree", CY, 11.5)}

{perche(XA, yA, sA, INK, "A")}
{perche(XB, yB, sB, GO, "B", graduee=True)}
{perche(XC, yC, sC, INK, "C")}

<line x1="{XA}" y1="{sA:.1f}" x2="{XC}" y2="{sC:.1f}" stroke="{RO}" stroke-width="2" stroke-dasharray="8 5"/>
{txt(178, sA-16, "ligne de visee A vers C — une droite geometrique", RO, 12, "700")}

<line x1="{XB}" y1="{sB:.1f}" x2="{XB}" y2="{sMid:.1f}" stroke="{GO}" stroke-width="2.5"/>
<circle cx="{XB}" cy="{sB:.1f}" r="4.5" fill="{GO}"/>
<circle cx="{XB}" cy="{sMid:.1f}" r="4.5" fill="{RO}"/>
{txt(XB+16, (sB+sMid)/2+5, "f  =  la fleche", GO, 13, "700")}
{txt(XB+16, (sB+sMid)/2+21, "lecture sur la graduation", MUT, 11)}

<circle cx="{XA}" cy="{sA:.1f}" r="7" fill="none" stroke="{LV}" stroke-width="2"/>
<line x1="{XA-22}" y1="{sA-14:.1f}" x2="{XA-7}" y2="{sA-4:.1f}" stroke="{LV}" stroke-width="2"/>
{txt(XA-30, sA-20, "lunette", LV, 11.5, anchor="end")}

{cote(XA, H-52, XB, H-52, "D / 2")}
{cote(XB, H-52, XC, H-52, "D / 2")}
{cote(XA, H-26, XC, H-26, "D  =  1 · 1,5 · 2 · 3 · 5 · 7 · 10 km — sept configurations", GO, 12)}

{cote(XC+42, sC, XC+42, yC, "4,00 m", MUT)}
<line x1="{XC}" y1="{sC:.1f}" x2="{XC+46}" y2="{sC:.1f}" stroke="{MUT}" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="{XC}" y1="{yC:.1f}" x2="{XC+46}" y2="{yC:.1f}" stroke="{MUT}" stroke-width="0.8" stroke-dasharray="3 3"/>

<rect x="28" y="{H-160}" width="300" height="86" rx="6" fill="none" stroke="{GRID}" stroke-width="1"/>
{txt(42, H-140, "MODELE PLAN", RO, 11, "700")}
{txt(42, H-122, "f = 0. La lecture vaut 4,000 m", INK, 11.5)}
{txt(42, H-106, "a toute distance.", INK, 11.5)}
{txt(42, H-86, "MODELE SPHERIQUE   f = (1-k) D2 / 8R", CY, 11, "700")}
</svg>'''

# ═══════════════════════════════════════════════════════════════════════════
# 2. PUITS DE TRANQUILLISATION — coupe
# ═══════════════════════════════════════════════════════════════════════════
W2, H2 = 900, 620
XT = 300          # axe de la perche
EAU = 300         # niveau moyen

vagues = "M 40 %d" % EAU
for x in range(40, 261, 10):
    vagues += f" Q {x+5},{EAU-13 if (x//10)%2==0 else EAU+13} {x+10},{EAU}"
vagues2 = "M 500 %d" % EAU
for x in range(500, 861, 10):
    vagues2 += f" Q {x+5},{EAU-13 if (x//10)%2==0 else EAU+13} {x+10},{EAU}"

svg2 = f'''<svg viewBox="0 0 {W2} {H2}" xmlns="http://www.w3.org/2000/svg" data-zoomable role="img" aria-label="Coupe d une perche et de son puits de tranquillisation">
<rect width="{W2}" height="{H2}" fill="{BG}"/>
{txt(28, 36, "LE PUITS DE TRANQUILLISATION — COUPE D'UNE PERCHE", INK, 16, "700")}
{txt(28, 58, "La piece qui decide de tout. Sans elle, la lecture de la ligne d'eau vaut 100 mm et ecrase le signal.", MUT, 11.5)}

<rect x="40" y="{EAU}" width="820" height="{H2-EAU-60}" fill="{CY}" opacity="0.07"/>
<path d="{vagues}" fill="none" stroke="{CY}" stroke-width="2.2"/>
<path d="{vagues2}" fill="none" stroke="{CY}" stroke-width="2.2"/>
{txt(60, EAU+46, "clapot libre  ±100 mm", CY, 12, "700")}
{txt(60, EAU+64, "la ligne d'eau est indeterminee", MUT, 11)}
{txt(620, EAU+46, "clapot libre  ±100 mm", CY, 12, "700")}

<rect x="{XT-46}" y="{EAU-58}" width="92" height="{H2-EAU-40}" rx="5" fill="{BG}" stroke="{OP}" stroke-width="2.4"/>
<line x1="{XT-46}" y1="{EAU}" x2="{XT+46}" y2="{EAU}" stroke="{OP}" stroke-width="2.6"/>
{txt(XT+62, EAU+4, "eau calme dans le tube  ±5 mm", OP, 12, "700")}
{txt(XT+62, EAU+22, "-> la ligne d'eau devient lisible", MUT, 11)}

<rect x="{XT-46}" y="{EAU-58}" width="92" height="58" fill="{OP}" opacity="0.05"/>
{txt(XT+62, EAU-30, "puits de tranquillisation", OP, 12, "700")}
{txt(XT+62, EAU-12, "tube PVC 75 a 100 mm", MUT, 11)}

<g>
{"".join(f'<circle cx="{XT-46}" cy="{EAU+40+i*26}" r="3.4" fill="none" stroke="{OP}" stroke-width="1.4"/><circle cx="{XT+46}" cy="{EAU+40+i*26}" r="3.4" fill="none" stroke="{OP}" stroke-width="1.4"/>' for i in range(6))}
</g>
{txt(XT-62, EAU+130, "percements fins", OP, 11, anchor="end")}
{txt(XT-62, EAU+148, "8 mm — ils laissent", MUT, 10.5, anchor="end")}
{txt(XT-62, EAU+166, "passer le niveau moyen,", MUT, 10.5, anchor="end")}
{txt(XT-62, EAU+184, "pas les vagues", MUT, 10.5, anchor="end")}

<line x1="{XT}" y1="{EAU+200}" x2="{XT}" y2="96" stroke="{GO}" stroke-width="5" stroke-linecap="round"/>
<rect x="{XT-38}" y="{H2-56}" width="76" height="14" rx="3" fill="{MUT}" opacity="0.6"/>
{txt(XT+50, H2-44, "lest / ancrage sur le fond", MUT, 11)}

<g>
{"".join(f'<line x1="{XT+6}" y1="{96+i*10.4:.1f}" x2="{XT+(20 if i%5==0 else 13)}" y2="{96+i*10.4:.1f}" stroke="{GO}" stroke-width="1.4"/>' for i in range(25))}
</g>
{txt(XT+30, 118, "mire graduee au millimetre", GO, 12, "700")}
{txt(XT+30, 136, "sur les 2,50 m superieurs", MUT, 11)}
{txt(XT+30, 154, "(perche B uniquement)", MUT, 11)}

<circle cx="{XT}" cy="96" r="5" fill="{RO}"/>
{txt(XT+16, 88, "sommet — origine de la mesure", RO, 11.5, "700")}

{cote(XT-92, 96, XT-92, EAU, "4,00 m", INK, 12)}
<line x1="{XT-96}" y1="96" x2="{XT-6}" y2="96" stroke="{INK}" stroke-width="0.8" stroke-dasharray="3 3"/>
<line x1="{XT-96}" y1="{EAU}" x2="{XT-50}" y2="{EAU}" stroke="{INK}" stroke-width="0.8" stroke-dasharray="3 3"/>
{txt(XT-88, 176, "mesures DEPUIS", MUT, 10.5)}
{txt(XT-88, 192, "la ligne d'eau,", MUT, 10.5)}
{txt(XT-88, 208, "jamais depuis le fond", MUT, 10.5)}

<rect x="560" y="120" width="310" height="132" rx="6" fill="none" stroke="{GRID}" stroke-width="1"/>
{txt(576, 144, "CE QUE CA CHANGE, A 1 km", GO, 11.5, "700")}
{txt(576, 168, "sans puits    sigma = 70,9 mm   S/B  0,3", MUT, 11.5)}
{txt(576, 188, "avec puits    sigma =  5,9 mm   S/B  2,9", INK, 11.5)}
{txt(576, 208, "+ 10 seances  sigma =  1,9 mm   S/B 10,5", OP, 11.5, "700")}
{txt(576, 234, "fleche attendue a 1 km : 19,6 mm", CY, 11.5)}
</svg>'''

# ═══════════════════════════════════════════════════════════════════════════
# 3. CE QUE VOIT L'OBSERVATEUR
# ═══════════════════════════════════════════════════════════════════════════
W3, H3 = 900, 430
CX1, CX2, CYY, RR = 240, 660, 235, 130

def oculaire(cx, titre, coul, lecture, ecart, sous):
    g = f'<circle cx="{cx}" cy="{CYY}" r="{RR}" fill="#070b10" stroke="{coul}" stroke-width="2.5"/>'
    g += f'<line x1="{cx-RR+14}" y1="{CYY}" x2="{cx+RR-14}" y2="{CYY}" stroke="{MUT}" stroke-width="0.9" stroke-dasharray="4 4"/>'
    g += f'<line x1="{cx}" y1="{CYY-RR+14}" x2="{cx}" y2="{CYY+RR-14}" stroke="{MUT}" stroke-width="0.9" stroke-dasharray="4 4"/>'
    # mire B
    bx = cx - 6
    g += f'<rect x="{bx}" y="{CYY-96}" width="13" height="180" fill="{GO}" opacity="0.20"/>'
    for i in range(19):
        yy = CYY - 96 + i * 10
        lg = 15 if i % 5 == 0 else 8
        g += f'<line x1="{bx+13}" y1="{yy}" x2="{bx+13+lg}" y2="{yy}" stroke="{GO}" stroke-width="1.2"/>'
    # sommet de C, sur le reticule
    g += f'<circle cx="{cx+RR-34}" cy="{CYY}" r="5" fill="{RO}"/>'
    g += txt(cx+RR-46, CYY-14, "C", RO, 12, "700", "end")
    # trait de lecture
    g += f'<line x1="{cx-RR+20}" y1="{CYY+ecart}" x2="{cx+RR-20}" y2="{CYY+ecart}" stroke="{coul}" stroke-width="2"/>'
    g += f'<circle cx="{bx+6}" cy="{CYY+ecart}" r="4.5" fill="{coul}"/>'
    g += txt(cx, CYY - RR - 40, titre, coul, 14, "700", "middle")
    g += txt(cx, CYY - RR - 20, sous, MUT, 11, anchor="middle")
    g += txt(cx, CYY + RR + 30, lecture, coul, 13, "700", "middle")
    return g

svg3 = f'''<svg viewBox="0 0 {W3} {H3}" xmlns="http://www.w3.org/2000/svg" data-zoomable role="img" aria-label="Ce que voit l observateur dans la lunette, sous chaque modele">
<rect width="{W3}" height="{H3}" fill="{BG}"/>
{txt(28, 34, "CE QUE VOIT L'OBSERVATEUR — MEME VISEE, DEUX MODELES", INK, 16, "700")}
{txt(28, 56, "Oeil au sommet de A. Le reticule est pose sur le sommet de C. On lit la graduation de B.", MUT, 11.5)}
{oculaire(CX1, "MODELE PLAN", RO, "lecture = 4,000 m", 0, "les trois sommets sont alignes")}
{oculaire(CX2, "MODELE SPHERIQUE", CY, "lecture = 2,293 m  a 10 km", -58, "B depasse la visee de la fleche")}
<line x1="{CX2-6}" y1="{CYY}" x2="{CX2-6}" y2="{CYY-58}" stroke="{GO}" stroke-width="2.5"/>
{txt(CX2+34, CYY-30, "f = 1,707 m", GO, 12.5, "700")}
{txt(450, 400, "Un seul nombre a relever. Pas d'angle, pas de reduction, pas de systeme de coordonnees.", MUT, 11.5, anchor="middle")}
</svg>'''

# ── ecriture + controle de debordement ────────────────────────────────────
os.makedirs("public/schemas", exist_ok=True)
fichiers = {"dispositif-ensemble.svg": svg1,
            "puits-tranquillisation.svg": svg2,
            "lecture-visee.svg": svg3}
bad = 0
for nom, s in fichiers.items():
    vw = int(re.search(r'viewBox="0 0 (\d+)', s).group(1))
    vh = int(re.search(r'viewBox="0 0 \d+ (\d+)', s).group(1))
    for m in re.finditer(r'<text x="([\d.-]+)" y="([\d.-]+)"[^>]*font-size="([\d.]+)"[^>]*>([^<]*)</text>', s):
        x, y, fs, t = float(m.group(1)), float(m.group(2)), float(m.group(3)), m.group(4)
        anc = 'text-anchor="middle"' in m.group(0), 'text-anchor="end"' in m.group(0)
        larg = len(t) * fs * 0.61
        x0 = x - larg / 2 if anc[0] else (x - larg if anc[1] else x)
        if x0 < 0 or x0 + larg > vw or y > vh or y < 0:
            print(f"  DEBORDEMENT {nom}: «{t[:44]}» -> [{x0:.0f}, {x0+larg:.0f}] / {vw}, y={y}")
            bad += 1
    open(f"public/schemas/{nom}", "w", encoding="utf-8").write(s + "\n")
    print(f"  ecrit  public/schemas/{nom}  ({len(s)} octets, {vw}x{vh})")
print("controle debordement :", "OK" if bad == 0 else f"{bad} PROBLEME(S)")
