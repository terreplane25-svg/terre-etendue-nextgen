#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Met le protocole de photographie d'objet éloigné en avant.

Où, et à la place de quoi
─────────────────────────
Deux emplacements, et dans les deux il prend la place de celui qui y était.

  · Page « Les protocoles », section 07 : il remplace l'encadré de mise en
    avant de la portion masquée. Celle-ci garde sa ligne dans le tableau.
  · Page d'accueil, bloc pleine largeur sombre : il remplace le protocole de
    dépression de l'horizon.

Ce qui est préservé
───────────────────
Le protocole de l'horizon est déposé et porte un DOI Zenodo. Le retirer de la
page d'accueil sans laisser de chemin vers lui rendrait ce dépôt orphelin pour
un visiteur qui arrive par la racine. Le bloc conserve donc une ligne, en pied,
qui y renvoie avec son DOI. Ses fichiers dans public/protocoles/ ne sont pas
touchés.

Le script n'est pas idempotent : chaque ancre est comptée avant écriture, et
une ancre vue autrement qu'une fois arrête tout sans rien modifier.
"""
import json
import os
import shutil
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLE = os.path.join(RACINE, "content", "articles",
                       "les-protocoles-ce-que-c-est-et-pourquoi.json")
ACCUEIL = os.path.join(RACINE, "src", "app", "HomeClient.tsx")
PDF_SOURCE = os.path.join(RACINE, "content", "protocoles", "pdf",
                          "Protocole-analyse-photographique.pdf")
PDF_PUBLIC = os.path.join(RACINE, "public", "protocoles",
                          "Protocole-photographie-objet-eloigne.pdf")
LIEN_PDF = "/protocoles/Protocole-photographie-objet-eloigne.pdf"


def remplacer(texte, vieux, neuf, etiquette):
    n = texte.count(vieux)
    if n != 1:
        sys.exit("ancre « %s » vue %d fois — attendu 1." % (etiquette, n))
    return texte.replace(vieux, neuf)


# ─────────────────────────────────────────────────────────────────────────────
# Page des protocoles
# ─────────────────────────────────────────────────────────────────────────────
VIEIL_ENCADRE = '''<div class="tei-fait experiences">
<span class="tei-fait-label">LE PROTOCOLE &#192; FAIRE EN PREMIER</span>
<p><strong>Portion masqu&#233;e d'un objet &#233;loign&#233;.</strong> C'est le seul de la s&#233;rie qu'on puisse ex&#233;cuter le week-end prochain avec ce qu'on poss&#232;de d&#233;j&#224;&#160;: un appareil photo &#224; long zoom, un tr&#233;pied, un plan d'eau et une cible haute.</p>
<p>Et c'est le seul dont la conclusion ne se discute pas par la m&#233;t&#233;o. &#192; 40&#8211;50&#8239;km, voir la base de la cible exigerait un coefficient de r&#233;fraction de <strong>0,98 &#224; 0,99</strong>, quand un conduit atmosph&#233;rique &#8212; le mirage sup&#233;rieur, le cas le plus extr&#234;me qu'on mesure &#8212; correspond &#224; 1,00. Il faudrait un r&#233;gime qui n'existe pas.</p>
</div>
<p><a href="/protocoles/Protocole-portion-masquee.pdf"><strong>T&#233;l&#233;charger le protocole</strong></a> &#8212; bilingue fran&#231;ais et anglais, 12 pages, PDF. Il contient la grille de choix du site, le mat&#233;riel strictement n&#233;cessaire, la mise en place d&#233;taill&#233;e et une fiche de relev&#233; d'une page &#224; imprimer.</p>
<div class="tei-fait experiences">
<span class="tei-fait-label">CE QUE L'EXP&#201;RIENCE &#201;TABLIT</span>
<p>Depuis 2&#8239;m de hauteur d'&#339;il &#224; 40&#8239;km, une surface de 6&#8239;371&#8239;km masque <strong>au minimum 42&#8239;m</strong> de la base de la cible &#8212; valeur calcul&#233;e sous l'inversion thermique la plus forte jamais mesur&#233;e. La turbulence limite la lecture &#224; deux ou quatre m&#232;tres. <strong>Le rapport reste sup&#233;rieur &#224; dix dans le cas le plus d&#233;favorable.</strong></p>
</div>
'''

NOUVEL_ENCADRE = '''<div class="tei-fait experiences">
<span class="tei-fait-label">LE PROTOCOLE MIS EN AVANT</span>
<p><strong>Photographie d'un objet &#233;loign&#233;.</strong> Deux parties, quatre pages par langue, et pas une ligne de th&#233;orie. La premi&#232;re dit comment prendre un clich&#233; qui ne sera pas &#233;cart&#233; d'entr&#233;e&#160;: format brut conserv&#233; tel quel, tr&#233;pied lourd et lest&#233;, d&#233;clenchement sans contact, vingt vues, focale minimale selon la distance, m&#233;tadonn&#233;es intactes, empreinte SHA-256 calcul&#233;e d&#232;s le transfert.</p>
<p>La seconde dit ce qu'il faut fournir avec le clich&#233;, ce qui est v&#233;rifi&#233;, et &#224; quelle condition une conclusion est rendue. Elle s'applique aussi bien &#224; une photographie prise expr&#232;s qu'&#224; une photographie de vacances retrouv&#233;e des ann&#233;es apr&#232;s.</p>
</div>
<p><a href="''' + LIEN_PDF + '''"><strong>T&#233;l&#233;charger le protocole</strong></a> &#8212; bilingue fran&#231;ais et anglais, 8 pages, PDF. Il contient la grille des focales minimales de 20 &#224; 700&#8239;km, la liste exhaustive des pi&#232;ces &#224; fournir et le bar&#232;me de d&#233;cision.</p>
<div class="tei-fait experiences">
<span class="tei-fait-label">CE QUE LE PROTOCOLE TRANCHE</span>
<p>Trois verdicts, et pas un quatri&#232;me. <strong>Rejet imm&#233;diat</strong> si le fichier brut manque ou a &#233;t&#233; modifi&#233;, si la focale n'est pas v&#233;rifiable, si la cible est douteuse ou la position d'observation non certifi&#233;e. <strong>Non concluant</strong> si un seul &#233;l&#233;ment manque dans la cha&#238;ne de tra&#231;abilit&#233;. <strong>Analyse valide</strong> &#8212; compatible ou incompatible &#8212; seulement si 100&#8239;% des pi&#232;ces et des sources ind&#233;pendantes sont fournies et authentifi&#233;es.</p>
</div>
'''

LIGNE_TABLEAU = (
    '    <tr><td><strong>Photographie d\'un objet &#233;loign&#233;</strong>'
    '</td><td>la recevabilit&#233; d\'un clich&#233; et les pi&#232;ces '
    '&#224; fournir pour qu\'il soit analysable</td><td>bilingue</td>'
    '<td>2.0</td><td>publi&#233;, non d&#233;pos&#233;</td></tr>\n'
)


def page_protocoles():
    with open(ARTICLE, encoding="utf-8") as f:
        data = json.load(f)
    html = data["htmlBody"]

    html = remplacer(html, VIEIL_ENCADRE, NOUVEL_ENCADRE,
                     "encadré de mise en avant de la section 07")
    html = remplacer(
        html,
        "<p>Trois documents sont arrêtés.",
        "<p>Quatre documents sont arrêtés.",
        "décompte des documents arrêtés")
    ancre = ("  <tbody>\n    <tr><td><strong>Portion masqu&#233;e d'un objet "
             "&#233;loign&#233;</strong>")
    html = remplacer(html, ancre,
                     "  <tbody>\n" + LIGNE_TABLEAU + ancre[len("  <tbody>\n"):],
                     "corps du tableau des protocoles")

    data["htmlBody"] = html
    with open(ARTICLE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
        f.write("\n")


# ─────────────────────────────────────────────────────────────────────────────
# Page d'accueil
# ─────────────────────────────────────────────────────────────────────────────
VIEUX_KICKER = "            Protocole déposé — DOI 10.5281/zenodo.22167798\n"
NOUVEAU_KICKER = "            Protocole de recevabilité — version 2.0\n"

VIEUX_TITRE = (
    "            Une mesure que chacun peut refaire, et dont le résultat "
    "était écrit d’avance\n")
NOUVEAU_TITRE = (
    "            Une photographie ne prouve rien tant qu’on ne peut pas dire "
    "d’où elle vient\n")

VIEUX_CORPS = '''          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 18px' }}>
            La dépression de l’horizon marin&nbsp;: l’angle entre l’horizontale du fil à plomb et la
            ligne d’horizon. Une sphère prédit qu’il croît comme la racine de l’altitude. Un plan
            prédit qu’il reste nul, à toute hauteur.
          </p>
          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 34px' }}>
            Depuis 3&nbsp;107 mètres, l’écart entre les deux prédictions vaut au minimum
            <strong style={{ color: '#F4F8FC' }}> 78 minutes d’arc</strong>, pour une incertitude de
            mesure de <strong style={{ color: '#F4F8FC' }}>2,2 minutes d’arc</strong>. C’est ce
            rapport, calculé avant la première image, qui rend la question décidable — et c’est ce
            que la plupart des observations amateurs ne fournissent jamais.
          </p>
'''

NOUVEAU_CORPS = '''          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 18px' }}>
            Deux parties, et pas une ligne de théorie. La première dit comment prendre un cliché
            qui ne sera pas écarté d’entrée&nbsp;: format brut conservé tel quel, trépied lourd et
            lesté, déclenchement sans contact, vingt vues, focale minimale selon la distance,
            métadonnées intactes, empreinte SHA-256 dès le transfert.
          </p>
          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 34px' }}>
            La seconde dit ce qu’il faut fournir avec, ce qui est vérifié, et à quelle condition une
            conclusion est rendue. Trois verdicts, et pas un quatrième&nbsp;:
            <strong style={{ color: '#F4F8FC' }}> rejet immédiat</strong>,
            <strong style={{ color: '#F4F8FC' }}> non concluant</strong>, ou
            <strong style={{ color: '#F4F8FC' }}> analyse valide</strong> — ce dernier seulement si
            100&nbsp;% des pièces et des sources indépendantes sont fournies et authentifiées.
          </p>
'''

VIEUX_BOUTONS = '''            <a href="/protocoles/Protocole-depression-horizon.pdf" style={{
              fontSize: 15, fontWeight: 700, color: '#F4F8FC', background: 'rgba(255,255,255,0.06)',
              padding: '15px 26px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.22)',
            }}>
              Télécharger le PDF · français
            </a>
            <a href="/protocoles/Horizon-Dip-Protocol.pdf" style={{
              fontSize: 15, fontWeight: 700, color: '#F4F8FC', background: 'rgba(255,255,255,0.06)',
              padding: '15px 26px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.22)',
            }}>
              English PDF
            </a>
'''

NOUVEAUX_BOUTONS = '''            <a href="''' + LIEN_PDF + '''" style={{
              fontSize: 15, fontWeight: 700, color: '#F4F8FC', background: 'rgba(255,255,255,0.06)',
              padding: '15px 26px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.22)',
            }}>
              Télécharger le PDF · bilingue
            </a>
'''

VIEUX_PIED = '''          <p style={{ fontSize: 13.5, color: '#6f829c', lineHeight: 1.65, marginTop: 26, maxWidth: 760 }}>
            Version 1.9, 22 pages, français et anglais. Prédictions et critères de décision
            enregistrés publiquement le 30 août 2026, avant toute acquisition de données. Licence
            CC BY 4.0.
          </p>
'''

NOUVEAU_PIED = '''          <p style={{ fontSize: 13.5, color: '#6f829c', lineHeight: 1.65, marginTop: 26, maxWidth: 760 }}>
            Version 2.0, 8 pages, français et anglais dans le même fichier. Licence CC BY 4.0.
          </p>
          <p style={{ fontSize: 13.5, color: '#6f829c', lineHeight: 1.65, marginTop: 10, maxWidth: 760 }}>
            Le protocole de dépression de l’horizon marin, déposé le 30 août 2026 sous le
            DOI 10.5281/zenodo.22167798, reste disponible&nbsp;:{' '}
            <a href="/protocoles/Protocole-depression-horizon.pdf" style={{ color: '#a8b8cc', textDecoration: 'underline' }}>français</a>
            {' · '}
            <a href="/protocoles/Horizon-Dip-Protocol.pdf" style={{ color: '#a8b8cc', textDecoration: 'underline' }}>English</a>.
          </p>
'''


def page_accueil():
    src = open(ACCUEIL, encoding="utf-8").read()
    for vieux, neuf, etiquette in (
            (VIEUX_KICKER, NOUVEAU_KICKER, "bandeau du bloc protocole"),
            (VIEUX_TITRE, NOUVEAU_TITRE, "titre du bloc protocole"),
            (VIEUX_CORPS, NOUVEAU_CORPS, "corps du bloc protocole"),
            (VIEUX_BOUTONS, NOUVEAUX_BOUTONS, "boutons de téléchargement"),
            (VIEUX_PIED, NOUVEAU_PIED, "pied du bloc protocole")):
        src = remplacer(src, vieux, neuf, etiquette)
    open(ACCUEIL, "w", encoding="utf-8").write(src)


def main():
    if not os.path.exists(PDF_SOURCE):
        sys.exit("PDF absent : %s" % PDF_SOURCE)
    os.makedirs(os.path.dirname(PDF_PUBLIC), exist_ok=True)
    shutil.copy2(PDF_SOURCE, PDF_PUBLIC)

    page_protocoles()
    page_accueil()

    print("PDF servi          : %s (%d ko)"
          % (os.path.relpath(PDF_PUBLIC, RACINE),
             os.path.getsize(PDF_PUBLIC) // 1024))
    print("Page des protocoles : encadré remplacé, ligne de tableau, décompte")
    print("Page d'accueil      : bloc remplacé, renvoi au protocole déposé "
          "conservé en pied")
    return 0


if __name__ == "__main__":
    sys.exit(main())
