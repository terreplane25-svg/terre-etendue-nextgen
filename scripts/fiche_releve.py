#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""La fiche de relevé de terrain, tenant strictement sur une page A4.

Pourquoi un module à part
─────────────────────────
Une fiche de relevé n'est pas de la prose : c'est un formulaire, et un
formulaire se dimensionne. Le corps du protocole se compose au fil du texte et
peut déborder d'une page sans dommage ; la fiche, elle, doit tenir sur une seule
feuille qu'on emporte, qu'on remplit au stylo et qu'on joint au dossier. La
séparer permet de lui donner sa propre feuille de style, plus serrée, sans
toucher au reste.

Le dimensionnement
──────────────────
A4 avec les marges du gabarit (19 mm en tête, 16 mm en pied, 17 mm de côté)
laisse 262 mm de hauteur utile. La fiche est bâtie pour en occuper environ 200,
ce qui laisse de quoi respirer sans risquer le débordement :

    titre                                    12 mm
    quatre intertitres                       4 × 7 mm
    contextualisation, 5 lignes              38 mm
    mesures, en-tête + 3 lignes              32 mm
    validation et conclusion                 42 mm
    checklist, 5 items                       44 mm
    règle d'analyse                          16 mm

Les traits à remplir sont des bordures basses et non des suites de points : le
stylo suit une ligne droite, et le rendu reste net à l'impression comme à
l'écran.
"""

# Feuille de style de la fiche. Émise une seule fois par document.
STYLE = """<style>
.fiche{font-size:8.7pt; line-height:1.34}
.fiche h2{margin:0 0 10pt}
.fiche h3{
  font-family:"IBM Plex Mono",monospace; font-size:8.2pt; font-weight:600;
  letter-spacing:.13em; text-transform:uppercase; color:var(--globe);
  margin:11pt 0 5pt; padding-bottom:2.5pt; border-bottom:.6pt solid var(--line);
}
.fiche table{width:100%; border-collapse:collapse; margin:0 0 4pt}
.fiche td,.fiche th{padding:4pt 5pt; border:.5pt solid var(--line); vertical-align:middle}
.fiche th{
  background:var(--wash); font-family:"IBM Plex Mono",monospace;
  font-size:7.4pt; font-weight:600; letter-spacing:.05em; text-transform:uppercase;
  color:var(--soft); text-align:center;
}
.fiche td.lab{
  width:21%; background:var(--wash); font-weight:600; color:var(--soft);
  font-size:8.2pt;
}
.fiche td.val{width:29%}
.fiche tr.vide td{height:15pt}
.rem{display:inline-block; border-bottom:.6pt solid var(--line2); min-width:26mm; height:9pt}
.rem.court{min-width:12mm}
.rem.long{min-width:100%}
.case{
  display:inline-block; width:9.5pt; height:9.5pt; border:.8pt solid var(--soft);
  vertical-align:-1.5pt; margin-right:5pt;
}
.fiche ul.just{list-style:none; padding:0; margin:0 0 6pt}
.fiche ul.just li{margin:0 0 5.5pt; padding-left:15pt; text-indent:-15pt; text-align:left}
.fiche p{margin:0 0 5pt; text-align:left}
.fiche .regle{
  border-left:2.4pt solid var(--alert); background:var(--alert-w);
  padding:6pt 9pt; margin-top:7pt; font-size:8.3pt;
}
.fiche .verdict{margin:0 0 4pt; padding-left:2pt}
</style>"""

REM = '<span class="rem"></span>'
REM_COURT = '<span class="rem court"></span>'
REM_LONG = '<span class="rem long"></span>'
CASE = '<span class="case"></span>'


def _ligne(lab1, val1, lab2, val2):
    return ('    <tr><td class="lab">%s</td><td class="val">%s</td>'
            '<td class="lab">%s</td><td class="val">%s</td></tr>'
            % (lab1, val1, lab2, val2))


def fiche(fr, avec_style=True):
    """La fiche complète. `avec_style` n'est vrai que pour la première langue."""
    style = STYLE if avec_style else ""

    if fr:
        titre = "Fiche de relev&#233; terrain"
        s1, s2, s3, s4 = ("1. Contextualisation", "2. Mesures",
                          "3. Validation et conclusion",
                          "4. Pi&#232;ces justificatives &#224; joindre")
        contexte = "\n".join([
            _ligne("Station (lieu)", REM, "Date / heure",
                   REM_COURT + " / " + REM_COURT + " / " + REM_COURT
                   + " &#224; " + REM_COURT + " h"),
            _ligne("Cible", REM, "Appareil / objectif",
                   REM_COURT + " / " + REM_COURT + " mm"),
            _ligne("Distance <em>d</em>", REM_COURT + " km",
                   "Source des rep&#232;res", REM),
            _ligne("Hauteur cible", REM_COURT + " m", "M&#233;t&#233;o T air / T eau",
                   REM_COURT + " &#176;C / " + REM_COURT + " &#176;C"),
            _ligne("Profil d&#233;gag&#233;", CASE + "oui, v&#233;rifi&#233;",
                   "Mar&#233;e / niveau d'eau", REM_COURT + " m"),
        ])
        entetes = ["heure", "hauteur d'&#339;il", "nbr clich&#233;s",
                   "&#233;chelle (m/px)", "c<sub>obs</sub> mesur&#233;",
                   "c<sub>min</sub> (table)"]
        rejet = ("<strong>Condition de rejet.</strong> Cible masqu&#233;e par un "
                 "obstacle physique, bord flou ou diffus, brume&#160;?")
        rejet_choix = (CASE + "<strong>oui</strong> &#8212; mesure invalide"
                       "&#160;&#160;&#160;&#160;" + CASE
                       + "<strong>non</strong> &#8212; mesure exploitable")
        verdict = "<strong>Verdict.</strong>"
        v1 = (CASE + "<strong>Incompatible</strong> avec R = 6&#8239;371&#8239;km "
              "&#8212; <code>c<sub>obs</sub> &lt; c<sub>min</sub> &#8722; 3&#963;</code>")
        v2 = (CASE + "<strong>Compatible</strong> avec R = 6&#8239;371&#8239;km "
              "&#8212; <code>c<sub>obs</sub> &#8805; c<sub>min</sub></code>")
        obs = "<strong>Observations.</strong>"
        pieces = [
            ("Fichiers RAW d'origine", "photos brutes issues de la carte "
             "m&#233;moire, non retouch&#233;es et non recadr&#233;es, "
             "m&#233;tadonn&#233;es EXIF intactes."),
            ("Photo d'amorce", "clich&#233; grand-angle montrant le positionnement "
             "de la station et ses rep&#232;res proches."),
            ("Preuve de la hauteur d'&#339;il", "photo du m&#232;tre ou du jalon "
             "mesurant la distance entre le plan d'eau et l'axe de l'objectif."),
            ("Preuve de g&#233;olocalisation", "capture GPS ou extrait de carte "
             "validant la distance <em>d</em> au dixi&#232;me de kilom&#232;tre."),
            ("Source certifi&#233;e des rep&#232;res", "document officiel, plan "
             "d'architecte ou fiche technique attestant des dimensions r&#233;elles "
             "de la cible."),
        ]
        regle = ("<strong>R&#232;gle d'analyse.</strong> Si une seule pi&#232;ce de "
                 "cette liste manque, ou si les m&#233;tadonn&#233;es EXIF ont "
                 "&#233;t&#233; modifi&#233;es, le relev&#233; est class&#233; "
                 "<strong>&#171;&#160;non &#233;valuable&#160;&#187;</strong> et les "
                 "mesures ne sont pas analys&#233;es.")
    else:
        titre = "Field record sheet"
        s1, s2, s3, s4 = ("1. Context", "2. Measurements",
                          "3. Validation and conclusion",
                          "4. Supporting evidence to attach")
        contexte = "\n".join([
            _ligne("Station (place)", REM, "Date / time",
                   REM_COURT + " / " + REM_COURT + " / " + REM_COURT
                   + " at " + REM_COURT + " h"),
            _ligne("Target", REM, "Camera / lens",
                   REM_COURT + " / " + REM_COURT + " mm"),
            _ligne("Distance <em>d</em>", REM_COURT + " km", "Source of markers", REM),
            _ligne("Target height", REM_COURT + " m", "Weather T air / T water",
                   REM_COURT + " &#176;C / " + REM_COURT + " &#176;C"),
            _ligne("Clear profile", CASE + "yes, verified", "Tide / water level",
                   REM_COURT + " m"),
        ])
        entetes = ["time", "eye height", "frames kept", "scale (m/px)",
                   "c<sub>obs</sub> measured", "c<sub>min</sub> (table)"]
        rejet = ("<strong>Rejection condition.</strong> Target hidden by a physical "
                 "obstacle, blurred or diffuse edge, haze?")
        rejet_choix = (CASE + "<strong>yes</strong> &#8212; measurement invalid"
                       "&#160;&#160;&#160;&#160;" + CASE
                       + "<strong>no</strong> &#8212; measurement usable")
        verdict = "<strong>Verdict.</strong>"
        v1 = (CASE + "<strong>Incompatible</strong> with R = 6&#8239;371&#8239;km "
              "&#8212; <code>c<sub>obs</sub> &lt; c<sub>min</sub> &#8722; 3&#963;</code>")
        v2 = (CASE + "<strong>Compatible</strong> with R = 6&#8239;371&#8239;km "
              "&#8212; <code>c<sub>obs</sub> &#8805; c<sub>min</sub></code>")
        obs = "<strong>Observations.</strong>"
        pieces = [
            ("Original RAW files", "unprocessed frames straight from the memory card, "
             "neither retouched nor cropped, EXIF metadata intact."),
            ("Establishing shot", "wide-angle frame showing the station's position and "
             "its near landmarks."),
            ("Proof of eye height", "photograph of the tape or staff measuring the "
             "distance between the water surface and the lens axis."),
            ("Proof of geolocation", "GPS capture or map extract validating the "
             "distance <em>d</em> to the tenth of a kilometre."),
            ("Certified source of markers", "official document, architect's drawing or "
             "data sheet attesting the target's real dimensions."),
        ]
        regle = ("<strong>Analysis rule.</strong> If a single item of this list is "
                 "missing, or if the EXIF metadata have been altered, the record is "
                 "classified <strong>&#8220;not assessable&#8221;</strong> and the "
                 "measurements are not analysed.")

    lignes_mesures = "\n".join(
        '    <tr class="vide">%s</tr>' % ("<td></td>" * len(entetes))
        for _ in range(3))

    return f"""{style}
<div class="fiche">
<h2 class="brk">{titre}</h2>

<h3>{s1}</h3>
<table>
  <tbody>
{contexte}
  </tbody>
</table>

<h3>{s2}</h3>
<table>
  <thead><tr>{"".join("<th>%s</th>" % e for e in entetes)}</tr></thead>
  <tbody>
{lignes_mesures}
  </tbody>
</table>

<h3>{s3}</h3>
<p>{rejet}</p>
<p class="verdict">{rejet_choix}</p>
<p style="margin-top:7pt">{verdict}</p>
<p class="verdict">{v1}</p>
<p class="verdict">{v2}</p>
<p style="margin-top:7pt">{obs} {REM_LONG}</p>
<p>{REM_LONG}</p>

<h3>{s4}</h3>
<ul class="just">
{chr(10).join('  <li>%s<strong>%s</strong> &#8212; %s</li>' % (CASE, t, d)
              for t, d in pieces)}
</ul>
<div class="regle">{regle}</div>
</div>"""
