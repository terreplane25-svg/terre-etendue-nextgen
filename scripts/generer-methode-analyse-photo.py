#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Photographie d'un objet éloigné : prise de vue et recevabilité.

Ce que le document est
──────────────────────
Deux parties, et rien d'autre. La première dit à qui veut photographier ce
qu'il doit faire pour que son cliché ne soit pas écarté d'entrée. La seconde dit
à qui reçoit le cliché ce qu'il exige, ce qu'il vérifie, et à quelle condition
il conclut.

Aucune physique n'y figure. Ni courbure, ni coefficient de réfraction, ni
propagation d'incertitude, ni géométrie de visée : cela relève du travail de
l'analyste, pas du protocole qu'on met entre les mains d'un photographe ou d'un
guichet de recevabilité. Le document ne dit pas comment on calcule, il dit ce
qu'on exige avant d'avoir le droit de calculer.

Le grossissement — section 1.4
──────────────────────────────
Un fort zoom est autorisé, y compris numérique. Un premier jet le rejetait, et
c'était une faute : le grossissement ne change ni la distance, ni la trajectoire
des rayons, ni ce qu'une surface interpose entre l'observateur et la cible. Il
rend seulement la cible assez grande sur le capteur pour être mesurée. Confondre
« je ne distinguais pas l'objet sans zoom » et « l'objet était occulté » serait
confondre deux phénomènes sans rapport.

Ce qui compte n'est donc pas zoom ou pas zoom, mais : quelle information a
réellement été enregistrée, et est-elle documentée assez pour être exploitée ?
D'où la distinction, en 1.4.3, entre zoom optique, zoom numérique, recadrage
interne et traitement computationnel ; et la ligne de partage de 1.4.6, entre
agrandir une information enregistrée — acceptable — et reconstruire une
information qui ne l'a pas été — exclu de la mesure.

Cette distinction descend dans le barème : une focale non documentée fait
rejeter le dossier, une focale documentée mais insuffisante le rend non
concluant. Ce ne sont pas les mêmes verdicts, parce que ce ne sont pas les mêmes
défauts.

La grille des focales
─────────────────────
Elle repose sur un seul critère, énoncé en 1.5.1 : l'échelle au sol à la
distance de la cible ne dépasse pas un mètre par pixel du capteur natif, pour un
capteur d'au moins 6 000 pixels sur le grand côté. Sur une image 24×36 de
largeur 36 mm, cela donne une focale équivalente minimale de six millimètres par
kilomètre de distance — 120 mm à 20 km, 4 200 mm à 700 km. Elle porte sur la
chaîne optique seule : le zoom numérique et le recadrage interne n'y comptent
pas, puisqu'ils n'ajoutent aucune information.

Les valeurs du tableau sont recalculées par focale_mini() et vérifiées par
controle() ; elles ne sont pas écrites en dur dans le texte.

Aucune marque et aucun modèle n'est cité, nulle part.
"""
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
CIBLE = os.path.join(PROTOCOLES, "analyse-photo-bilingue.html")
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

VERSION = "3.0"
AUTEUR = "Terre &#201;tendue"
CONTACT = "terre-etendue-islam.fr"
DATE = ("2 septembre 2026", "2 September 2026")
LICENCE = "CC BY 4.0"
LARGEUR_IMAGE = 36.0        # mm — grand côté du format 24×36
PIXELS = 6000               # pixels natifs sur le grand côté
ECHELLE_MAX = 1.0           # m par pixel à la distance de la cible
DISTANCES = [20, 50, 100, 300, 700]   # km
FACTEUR_RESOLU = 3          # la caractéristique mesurée / la structure résolue


def focale_mini(d_km):
    """Focale équivalente minimale, en mm, pour tenir l'échelle de 1.5.1."""
    return LARGEUR_IMAGE * (d_km * 1000.0) / (ECHELLE_MAX * PIXELS)


def echelle(d_km, f_mm):
    """Échelle au sol, en m par pixel, pour une focale équivalente donnée."""
    return (LARGEUR_IMAGE / f_mm) * (d_km * 1000.0) / PIXELS


def controle():
    """Recalcule la grille et vérifie qu'elle tient son propre critère."""
    for d in DISTANCES:
        f = focale_mini(d)
        assert abs(echelle(d, f) - ECHELLE_MAX) < 1e-9, d
    attendu = {20: 120, 50: 300, 100: 600, 300: 1800, 700: 4200}
    for d, f in attendu.items():
        assert abs(focale_mini(d) - f) < 0.5, (d, focale_mini(d))
    # La grille est proportionnelle à la distance : six millimètres par
    # kilomètre. Si le critère de 1.5.1 change, elle reste proportionnelle.
    pentes = {focale_mini(d) / d for d in DISTANCES}
    assert max(pentes) - min(pentes) < 1e-9, pentes
    return True


def nb(x, fr):
    """Un entier avec séparateur de milliers fin."""
    return "{:,.0f}".format(x).replace(",", "&#8239;")


# ─────────────────────────────────────────────────────────────────────────────
# Mise en forme
# ─────────────────────────────────────────────────────────────────────────────
def partie(numero, titre, saut=False):
    return ('<h2%s><span class="n">%s</span>%s</h2>'
            % (' class="brk"' if saut else "", numero, titre))


def sous(titre):
    return "<h3>%s</h3>" % titre


def clause(numero, texte):
    return "<p>%s &#8212; %s</p>" % (numero, texte)


def tab(legende, entetes, lignes, num=()):
    th = "".join('<th%s>%s</th>' % (' class="n"' if i in num else "", e)
                 for i, e in enumerate(entetes))
    return ("<table>\n  <caption>%s</caption>\n  <thead><tr>%s</tr></thead>\n"
            "  <tbody>\n%s\n  </tbody>\n</table>"
            % (legende, th, "\n".join(lignes)))


def rang(cellules, num=(), vedette=False):
    tds = "".join('<td%s>%s</td>' % (' class="n"' if i in num else "", c)
                  for i, c in enumerate(cellules))
    return '    <tr%s>%s</tr>' % (' class="hi"' if vedette else "", tds)


def encadre(etiquette, contenu, genre="warn"):
    return ('<div class="box %s">\n  <span class="lab">%s</span>\n%s\n</div>'
            % (genre, etiquette, contenu))


def masthead(fr):
    kicker = ("Protocole &#183; Prise de vue &#183; Recevabilit&#233;" if fr
              else "Protocol &#183; Image capture &#183; Admissibility")
    titre = ("Photographie d'un objet &#233;loign&#233;" if fr
             else "Photograph of a distant object")
    sous_titre = ("Prise de vue &#183; recevabilit&#233; du dossier &#183; "
                  "analyse et certification coll&#233;giale" if fr else
                  "Image capture &#183; admissibility of the file &#183; "
                  "analysis and collegial certification")
    # Un protocole sans auteur, sans contact et sans date se conteste avant
    # d'être lu. Les quatre cases sont renseignées, pas laissées en blanc.
    valeurs = ((("R&#233;dacteur", AUTEUR), ("Contact", CONTACT),
                ("Version", VERSION), ("Date", DATE[0]),
                ("Licence", LICENCE)) if fr else
               (("Author", AUTEUR), ("Contact", CONTACT),
                ("Version", VERSION), ("Date", DATE[1]),
                ("Licence", LICENCE)))
    cases = "".join("<span>%s<b>%s</b></span>" % c for c in valeurs)
    return ('<div class="masthead">\n  <div class="kicker">%s</div>\n'
            '  <h1>%s</h1>\n  <p class="dek">%s</p>\n'
            '  <div class="byline">\n    %s\n  </div>\n</div>'
            % (kicker, titre, sous_titre, cases))


# Le corps ne contient que des exigences. Ces tournures y signalent une
# digression, et le document est refusé plutôt qu'écrit.
DIGRESSION = [
    r"nous (?:avons|pensons|proposons|croyons)",
    r"version pr[ée]c[ée]dente", r"previous version",
    r"[Cc]orrection apport", r"c'est pourquoi nous",
    r"&#8730;",          # aucune formule dans le corps : la partie 3 exige un
    r"= R / \(1",        # calcul, elle ne l'enseigne pas
]


def ecrire(corps_fr, corps_en):
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    if i < 0:
        raise SystemExit("gabarit sans <div class=\"page\"> : %s" % GABARIT)
    entete = re.sub(r"<title>[^<]*</title>",
                    "<title>Photographie d'un objet &#233;loign&#233; "
                    "&#8212; protocole</title>", modele[:i], count=1)
    doc = (entete + '<div class="page">\n'
           '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
           '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n'
           + corps_fr +
           '\n\n<div class="langbar"><span>FRAN&#199;AIS &#8212; first half'
           '</span><span class="on">ENGLISH</span></div>\n\n'
           + corps_en + '\n</div>\n')
    for motif in DIGRESSION:
        m = re.search(motif, doc)
        if m:
            raise SystemExit("digression théorique : %r"
                             % doc[max(0, m.start() - 70):m.end() + 40])
    open(CIBLE, "w", encoding="utf-8").write(doc)
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# La chaîne optique et numérique à documenter (tableau 2). Une information
# absente n'est pas inventée : elle est déclarée absente.
# ─────────────────────────────────────────────────────────────────────────────
CHAINE_OPTIQUE = [
    ("Focale optique r&#233;elle", "Actual optical focal length",
     "m&#233;tadonn&#233;es EXIF, champ de focale et champ de focale "
     "&#233;quivalente",
     "EXIF metadata, focal length and equivalent focal length fields"),
    ("Facteur de grossissement employ&#233;", "Magnification factor used",
     "r&#233;glage de l'appareil au moment de la prise de vue, report&#233; "
     "par l'op&#233;rateur",
     "the camera setting at the moment of capture, reported by the operator"),
    ("Type de grossissement", "Type of magnification",
     "optique, num&#233;rique, ou les deux combin&#233;s&#160;; "
     "pr&#233;cis&#233; poste par poste",
     "optical, digital, or the two combined; stated stage by stage"),
    ("R&#233;solution native du capteur", "Native sensor resolution",
     "documentation du constructeur, en pixels et en pas de photosite",
     "manufacturer's documentation, in pixels and photosite pitch"),
    ("R&#233;solution du fichier final", "Resolution of the final file",
     "lue dans le fichier remis, et compar&#233;e &#224; la "
     "pr&#233;c&#233;dente",
     "read from the submitted file, and compared with the previous item"),
    ("Recadrage effectu&#233; par l'appareil avant enregistrement",
     "Cropping performed by the camera before recording",
     "mode ou r&#233;glage employ&#233;, et rapport entre la zone "
     "enregistr&#233;e et le capteur entier",
     "the mode or setting used, and the ratio of the recorded area to the "
     "whole sensor"),
    ("Traitements computationnels automatiques",
     "Automatic computational processing",
     "modes de rehaussement, fusion de plusieurs vues, r&#233;duction de "
     "bruit, accentuation, reconnaissance de sujet&#160;; actifs ou non",
     "enhancement modes, multi-frame fusion, noise reduction, sharpening, "
     "subject recognition; on or off"),
    ("Toute autre &#233;tape entre la sc&#232;ne et le fichier",
     "Any other stage between the scene and the file",
     "compl&#233;ment&#160;: convertisseur, adaptateur, filtre, "
     "t&#233;l&#233;convertisseur, logiciel de transfert",
     "supplementary: converter, adapter, filter, teleconverter, transfer "
     "software"),
]


# ─────────────────────────────────────────────────────────────────────────────
# Partie 1 — prise de vue et matériel
# ─────────────────────────────────────────────────────────────────────────────
def bloc_1(fr):
    t_focales = tab(
        ("Tableau&#160;1 &#8212; focale &#233;quivalente minimale de la "
         "cha&#238;ne optique, pour un capteur de 6&#8239;000 pixels sur le "
         "grand c&#244;t&#233;. Pour tout autre capteur, c'est le crit&#232;re "
         "de 1.5.1 qui s'applique, non ces valeurs. Tableau de "
         "pr&#233;paration&#160;: le contr&#244;le d&#233;cisif est celui de "
         "1.5.3."
         if fr else
         "Table&#160;1 &#8212; minimum equivalent focal length of the optical "
         "chain, for a sensor of 6,000 pixels on the long side. For any other "
         "sensor the criterion of 1.5.1 applies, not these values. A planning "
         "table: the decisive check is the one in 1.5.3."),
        (["Distance de vis&#233;e", "Focale &#233;quivalente minimale"] if fr
         else ["Sighting distance", "Minimum equivalent focal length"]),
        [rang(["%s&#8239;km" % nb(d, fr),
               "%s&#8239;mm" % nb(focale_mini(d), fr)], num=(0, 1))
         for d in DISTANCES], num=(0, 1))

    t_chaine = tab(
        ("Tableau&#160;2 &#8212; cha&#238;ne optique et num&#233;rique. Une "
         "information indisponible est d&#233;clar&#233;e indisponible, jamais "
         "estim&#233;e ni laiss&#233;e en blanc."
         if fr else
         "Table&#160;2 &#8212; optical and digital chain. An unavailable item "
         "is declared unavailable, never estimated and never left blank."),
        (["N&#176;", "Information", "O&#249; elle se trouve"] if fr
         else ["No.", "Item", "Where it is found"]),
        [rang(["%02d" % (i + 1), c[0 if fr else 1], c[2 if fr else 3]],
              num=(0,)) for i, c in enumerate(CHAINE_OPTIQUE)], num=(0,))

    if fr:
        return "\n".join([
            partie("1", "Prise de vue et mat&#233;riel"),
            clause("1.1", "La pr&#233;sente partie &#233;nonce les conditions "
                   "dans lesquelles une photographie d'objet &#233;loign&#233; "
                   "est prise pour &#234;tre recevable. Elle s'adresse &#224; "
                   "l'op&#233;rateur."),
            sous("1.2 Enregistrement"),
            clause("1.2.1", "L'enregistrement se fait en format brut lorsque "
                   "l'appareil le permet. Le fichier d'origine, quel que soit "
                   "son format, est conserv&#233; tel qu'il sort de "
                   "l'appareil."),
            clause("1.2.2", "Apr&#232;s la prise de vue, aucune retouche, "
                   "aucun recadrage, aucun r&#233;&#233;chantillonnage, aucune "
                   "conversion et aucune correction de perspective ou de "
                   "distorsion n'est appliqu&#233;e au fichier d'origine."),
            clause("1.2.3", "Si l'appareil produit plusieurs fichiers pour la "
                   "m&#234;me vue &#8212; brut et compress&#233;, avant et "
                   "apr&#232;s traitement interne &#8212; tous sont "
                   "conserv&#233;s et remis ensemble."),
            clause("1.2.4", "Le fichier d'origine n'est jamais ouvert en "
                   "&#233;criture. Toute manipulation ult&#233;rieure se fait "
                   "sur une copie."),
            sous("1.3 Support et stabilit&#233;"),
            clause("1.3.1", "L'appareil est mont&#233; sur un tr&#233;pied "
                   "lourd et ultra-stable. Colonne centrale rentr&#233;e, "
                   "jambes d&#233;ploy&#233;es par les sections les plus "
                   "&#233;paisses, rotule bloqu&#233;e, embase de niveau."),
            clause("1.3.2", "Le tr&#233;pied est lest&#233; et pos&#233; sur un "
                   "sol ferme. Aucune prise de vue &#224; main lev&#233;e, "
                   "depuis un v&#233;hicule, un ponton, un balcon ou tout "
                   "appui susceptible de vibrer n'est recevable."),
            clause("1.3.3", "Le d&#233;clenchement se fait sans contact&#160;: "
                   "retardateur d'au moins deux secondes ou commande &#224; "
                   "distance."),
            clause("1.3.4", "La stabilisation optique ou m&#233;canique est "
                   "d&#233;sactiv&#233;e d&#232;s lors que l'appareil est sur "
                   "tr&#233;pied."),
            clause("1.3.5", "Au moins vingt vues cons&#233;cutives de la "
                   "m&#234;me vis&#233;e sont enregistr&#233;es, sans toucher "
                   "&#224; la mise au point, au cadrage ni au grossissement "
                   "entre les vues. Toutes sont remises&#160;; aucune n'est "
                   "&#233;cart&#233;e par l'op&#233;rateur."),
            sous("1.4 Grossissement &#224; l'acquisition"),
            clause("1.4.1", "Un fort grossissement est autoris&#233;, y "
                   "compris num&#233;rique. Une photographie n'est jamais "
                   "irrecevable au seul motif qu'un zoom important a "
                   "&#233;t&#233; employ&#233;."),
            clause("1.4.2", "Le grossissement ne modifie ni la distance entre "
                   "l'observateur et la cible, ni la g&#233;om&#233;trie du "
                   "terrain, ni la trajectoire physique des rayons lumineux. "
                   "Il ne peut pas rendre visible une partie d'un objet "
                   "r&#233;ellement occult&#233;e par la surface. Il rend la "
                   "cible assez grande sur le capteur pour &#234;tre "
                   "mesur&#233;e, et c'est &#224; cela qu'il sert."),
            clause("1.4.3", "Quatre op&#233;rations sont distingu&#233;es et "
                   "document&#233;es s&#233;par&#233;ment&#160;: le zoom "
                   "optique, le zoom num&#233;rique, le recadrage "
                   "effectu&#233; par l'appareil avant l'enregistrement, et "
                   "les traitements computationnels appliqu&#233;s "
                   "automatiquement par l'appareil."),
            clause("1.4.4", "Les informations du tableau&#160;2 sont "
                   "consign&#233;es lorsqu'elles sont disponibles. Une "
                   "information indisponible est d&#233;clar&#233;e telle et "
                   "n'est jamais remplac&#233;e par une valeur "
                   "plausible."),
            t_chaine,
            clause("1.4.5", "D&#232;s qu'un zoom num&#233;rique, un recadrage "
                   "interne ou un traitement computationnel est "
                   "intervenu, le fichier tel que produit par l'appareil est "
                   "conserv&#233;, et le fichier ant&#233;rieur au traitement "
                   "aussi lorsque l'appareil peut le fournir."),
            clause("1.4.6", "Agrandir une information d&#233;j&#224; "
                   "enregistr&#233;e est acceptable. Reconstruire une "
                   "information qui n'a pas &#233;t&#233; enregistr&#233;e "
                   "&#8212; synth&#232;se de d&#233;tail, rehaussement de "
                   "sujet, fusion inventant une structure absente des vues "
                   "individuelles &#8212; est exclu de la mesure. Les zones "
                   "concern&#233;es ne sont pas mesur&#233;es, et l'op&#233;"
                   "rateur indique quels modes &#233;taient actifs."),
            sous("1.5 R&#233;solution effective"),
            clause("1.5.1", "L'&#233;chelle au sol &#224; la distance de la "
                   "cible ne d&#233;passe pas un m&#232;tre par pixel du "
                   "capteur natif, pour un capteur d'au moins %s pixels sur le "
                   "grand c&#244;t&#233;. Le tableau&#160;1 donne les focales "
                   "&#233;quivalentes correspondantes." % nb(PIXELS, fr)),
            t_focales,
            clause("1.5.2", "Le tableau&#160;1 porte sur la cha&#238;ne "
                   "optique seule. Le zoom num&#233;rique et le recadrage "
                   "interne n'y comptent pas&#160;: ils n'ajoutent aucune "
                   "information. Ils ne disqualifient pas le clich&#233; pour "
                   "autant, et ils ne le qualifient pas non plus."),
            clause("1.5.3", "La plus petite structure r&#233;ellement "
                   "r&#233;solue est mesur&#233;e sur un bord franc de "
                   "dimension connue pr&#233;sent dans le champ. La "
                   "caract&#233;ristique que l'on veut mesurer doit &#234;tre "
                   "au moins %d fois plus grande que cette structure."
                   % FACTEUR_RESOLU),
            clause("1.5.4", "Le contr&#244;le d&#233;cisif est celui de "
                   "1.5.3, conduit sur l'image elle-m&#234;me. Le "
                   "tableau&#160;1 sert &#224; pr&#233;parer la prise de vue. "
                   "Un clich&#233; qui n'atteint pas le tableau&#160;1 mais "
                   "dont la caract&#233;ristique vis&#233;e est r&#233;solue "
                   "reste exploitable&#160;; un clich&#233; qui l'atteint mais "
                   "dont la caract&#233;ristique n'est pas r&#233;solue ne "
                   "l'est pas."),
            clause("1.5.5", "Un bord n'est mesurable que s'il est une "
                   "discontinuit&#233; r&#233;solue. Si la transition entre "
                   "l'objet et son fond s'&#233;tend sur plus de trois fois la "
                   "structure r&#233;solue de 1.5.3, ce n'est pas un bord mais "
                   "un d&#233;grad&#233;&#160;: sa position n'est pas "
                   "mesur&#233;e."),
            clause("1.5.6", "Un clich&#233; dont la caract&#233;ristique "
                   "vis&#233;e n'est pas r&#233;solue, ou dont le bord n'est "
                   "pas mesurable, n'est pas rejet&#233;. Il est class&#233; "
                   "non concluant pour cette caract&#233;ristique, et reste "
                   "utilisable pour une caract&#233;ristique plus grande."),
            sous("1.6 R&#232;gles d'admissibilit&#233; de la prise de vue"),
            clause("1.6.1", "Les m&#233;tadonn&#233;es EXIF brutes sont "
                   "conserv&#233;es intactes. Aucun champ n'est effac&#233;, "
                   "&#233;cras&#233; ni r&#233;&#233;crit, y compris par un "
                   "outil de transfert, une sauvegarde automatique ou un envoi "
                   "par messagerie."),
            clause("1.6.2", "L'horloge de l'appareil est r&#233;gl&#233;e sur "
                   "le temps universel avant la prise de vue. La position "
                   "satellitaire est enregistr&#233;e avec l'image."),
            clause("1.6.3", "La cible est parfaitement identifiable. Le champ "
                   "contient au moins deux &#233;l&#233;ments de "
                   "r&#233;f&#233;rence dont les dimensions r&#233;elles sont "
                   "&#233;tablies par une source ext&#233;rieure&#160;: "
                   "ouvrage r&#233;pertori&#233;, structure cot&#233;e, point "
                   "g&#233;od&#233;sique."),
            clause("1.6.4", "Une vue grand-angle du point de vue est prise "
                   "depuis la m&#234;me position, montrant les rep&#232;res "
                   "proches. Elle est remise avec la s&#233;rie."),
            clause("1.6.5", "L'empreinte SHA-256 de chaque fichier d'origine "
                   "est calcul&#233;e d&#232;s le transfert, avant toute autre "
                   "op&#233;ration, et consign&#233;e avec la date du calcul."),
            clause("1.6.6", "L'empreinte est d&#233;pos&#233;e le jour "
                   "m&#234;me aupr&#232;s d'un tiers qui la date&#160;: "
                   "horodatage &#233;lectronique, publication dat&#233;e, "
                   "registre public. &#192; d&#233;faut, la date de calcul "
                   "n'est qu'une d&#233;claration de l'op&#233;rateur, et le "
                   "rapport le dit."),
            clause("1.6.7", "La position satellitaire du point de vue est "
                   "relev&#233;e et consign&#233;e s&#233;par&#233;ment, avec "
                   "l'incertitude annonc&#233;e par le r&#233;cepteur."),
            encadre("Apr&#232;s la prise de vue, &#224; ne jamais faire",
                    "<p>Ne pas trier les vues, ne pas &#171;&#160;am&#233;"
                    "liorer&#160;&#187; l'image, ne pas la recadrer pour mieux "
                    "montrer la cible, ne pas la r&#233;exporter, ne pas "
                    "l'envoyer par un service qui recompresse. Ce que "
                    "l'appareil a fait avant l'enregistrement se documente "
                    "(1.4)&#160;; ce que l'op&#233;rateur fait apr&#232;s "
                    "d&#233;truit le fichier comme pi&#232;ce.</p>"),
        ])

    return "\n".join([
        partie("1", "Image capture and equipment"),
        clause("1.1", "This part states the conditions under which a "
               "photograph of a distant object is taken in order to be "
               "admissible. It addresses the operator."),
        sous("1.2 Recording"),
        clause("1.2.1", "Recording is in raw format where the camera allows "
               "it. The original file, whatever its format, is kept exactly as "
               "it comes out of the camera."),
        clause("1.2.2", "After the capture, no retouching, no cropping, no "
               "resampling, no conversion and no perspective or distortion "
               "correction is applied to the original file."),
        clause("1.2.3", "If the camera produces several files for the same "
               "view &#8212; raw and compressed, before and after internal "
               "processing &#8212; all are kept and submitted together."),
        clause("1.2.4", "The original file is never opened for writing. Any "
               "later handling is done on a copy."),
        sous("1.3 Support and stability"),
        clause("1.3.1", "The camera is mounted on a heavy, ultra-stable "
               "tripod. Centre column retracted, legs deployed on their "
               "thickest sections, head locked, base levelled."),
        clause("1.3.2", "The tripod is ballasted and set on firm ground. No "
               "frame taken handheld, from a vehicle, a pontoon, a balcony or "
               "any support liable to vibrate is admissible."),
        clause("1.3.3", "The shutter is released without contact: self-timer "
               "of at least two seconds, or remote release."),
        clause("1.3.4", "Optical or mechanical stabilisation is switched off "
               "whenever the camera is on a tripod."),
        clause("1.3.5", "At least twenty consecutive frames of the same "
               "sighting are recorded, without touching focus, framing or "
               "magnification between frames. All are submitted; none is "
               "discarded by the operator."),
        sous("1.4 Magnification at capture"),
        clause("1.4.1", "Strong magnification is permitted, digital "
               "magnification included. A photograph is never inadmissible on "
               "the sole ground that a large zoom was used."),
        clause("1.4.2", "Magnification changes neither the distance between "
               "observer and target, nor the geometry of the ground, nor the "
               "physical path of the light rays. It cannot make visible a part "
               "of an object genuinely occulted by the surface. It makes the "
               "target large enough on the sensor to be measured, and that is "
               "what it is for."),
        clause("1.4.3", "Four operations are distinguished and documented "
               "separately: optical zoom, digital zoom, cropping performed by "
               "the camera before recording, and computational processing "
               "applied automatically by the camera."),
        clause("1.4.4", "The items of table&#160;2 are recorded where "
               "available. An unavailable item is declared as such and is "
               "never replaced by a plausible value."),
        t_chaine,
        clause("1.4.5", "Wherever digital zoom, internal cropping or "
               "computational processing has intervened, the file as produced "
               "by the camera is kept, and so is the file prior to processing "
               "where the camera can supply it."),
        clause("1.4.6", "Enlarging information already recorded is acceptable. "
               "Reconstructing information that was never recorded &#8212; "
               "detail synthesis, subject enhancement, fusion inventing a "
               "structure absent from the individual frames &#8212; is "
               "excluded from measurement. The areas concerned are not "
               "measured, and the operator states which modes were active."),
        sous("1.5 Effective resolution"),
        clause("1.5.1", "The ground scale at the target's distance shall not "
               "exceed one metre per native sensor pixel, for a sensor of at "
               "least %s pixels on the long side. Table&#160;1 gives the "
               "corresponding equivalent focal lengths." % nb(PIXELS, fr)),
        t_focales,
        clause("1.5.2", "Table&#160;1 bears on the optical chain alone. "
               "Digital zoom and internal cropping do not count towards it: "
               "they add no information. Nor do they disqualify the frame; "
               "neither do they qualify it."),
        clause("1.5.3", "The smallest structure actually resolved is measured "
               "on a sharp edge of known dimension present in the field. The "
               "feature to be measured shall be at least %d times larger than "
               "that structure." % FACTEUR_RESOLU),
        clause("1.5.4", "The decisive check is the one in 1.5.3, carried out "
               "on the image itself. Table&#160;1 serves to plan the capture. "
               "A frame that falls short of table&#160;1 but whose intended "
               "feature is resolved remains usable; a frame that meets it but "
               "whose feature is not resolved does not."),
        clause("1.5.5", "An edge is measurable only if it is a resolved "
               "discontinuity. If the transition between the object and its "
               "background spans more than three times the resolved structure "
               "of 1.5.3, it is not an edge but a gradient: its position is "
               "not measured."),
        clause("1.5.6", "A frame whose intended feature is not resolved, or "
               "whose edge is not measurable, is not rejected. It is "
               "classified inconclusive for that feature, and remains usable "
               "for a larger one."),
        sous("1.6 Admissibility rules for the capture"),
        clause("1.6.1", "The raw EXIF metadata are kept intact. No field is "
               "erased, overwritten or rewritten, including by a transfer "
               "utility, an automatic backup or a messaging application."),
        clause("1.6.2", "The camera clock is set to universal time before the "
               "capture. The satellite position is recorded with the image."),
        clause("1.6.3", "The target is unmistakably identifiable. The field "
               "contains at least two reference elements whose real dimensions "
               "are established by an outside source: a listed structure, a "
               "dimensioned works, a geodetic point."),
        clause("1.6.4", "A wide-angle frame of the viewpoint is taken from the "
               "same position, showing the near landmarks. It is submitted "
               "with the series."),
        clause("1.6.5", "The SHA-256 digest of each original file is computed "
               "at transfer, before any other operation, and recorded with the "
               "date of computation."),
        clause("1.6.6", "The digest is lodged the same day with a third party "
               "that dates it: electronic timestamping, dated publication, "
               "public register. Failing that, the date of computation is "
               "merely the operator's declaration, and the report says so."),
        clause("1.6.7", "The satellite position of the viewpoint is read and "
               "recorded separately, together with the uncertainty stated by "
               "the receiver."),
        encadre("After the capture, never do this",
                "<p>Do not sort the frames, do not &#8220;improve&#8221; the "
                "image, do not crop it to show the target better, do not "
                "re-export it, do not send it through a service that "
                "recompresses. What the camera did before recording is "
                "documented (1.4); what the operator does afterwards destroys "
                "the file as evidence.</p>"),
    ])


# ─────────────────────────────────────────────────────────────────────────────
# Partie 2 — recevabilité du dossier
# ─────────────────────────────────────────────────────────────────────────────
PIECES = [
    ("Fichier d'origine",
     "Original file",
     "le fichier tel qu'il sort de l'appareil &#8212; brut lorsque l'appareil "
     "en produit un &#8212; avec ses m&#233;tadonn&#233;es EXIF intactes, son "
     "empreinte SHA-256 et la preuve de datation de celle-ci",
     "the file exactly as it comes out of the camera &#8212; raw where the "
     "camera produces one &#8212; with its EXIF metadata intact, its SHA-256 "
     "digest and the proof of that digest's date"),
    ("Cha&#238;ne optique et num&#233;rique",
     "Optical and digital chain",
     "les informations du tableau&#160;2, chacune renseign&#233;e ou "
     "d&#233;clar&#233;e indisponible, et la liste des traitements "
     "computationnels actifs &#224; la prise de vue",
     "the items of table&#160;2, each filled in or declared unavailable, and "
     "the list of computational processes active at capture"),
    ("Position de l'observateur",
     "Observer position",
     "coordonn&#233;es satellitaires du point de vue, avec l'incertitude "
     "annonc&#233;e par le r&#233;cepteur, et la vue grand-angle montrant les "
     "rep&#232;res proches",
     "satellite coordinates of the viewpoint, with the uncertainty stated by "
     "the receiver, and the wide-angle frame showing the near landmarks"),
    ("Identification et dimensions de la cible",
     "Target identification and dimensions",
     "d&#233;signation exacte de la cible et sources ind&#233;pendantes "
     "certifiant ses dimensions r&#233;elles&#160;: fiche officielle de "
     "l'ouvrage, plan cot&#233;, sp&#233;cification du constructeur, "
     "relev&#233; g&#233;od&#233;sique, registre horodat&#233;",
     "the target's exact designation and independent sources certifying its "
     "real dimensions: the structure's official record, a dimensioned drawing, "
     "a manufacturer's specification, a geodetic survey, a timestamped "
     "register"),
    ("Profil interm&#233;diaire",
     "Intervening profile",
     "profil topographique ou bathym&#233;trique entre le point de vue et la "
     "cible, issu de donn&#233;es publiques dat&#233;es, avec le niveau d'eau "
     "&#224; l'heure du clich&#233; le cas &#233;ch&#233;ant",
     "topographic or bathymetric profile between viewpoint and target, from "
     "dated public data, with the water level at the time of the frame where "
     "relevant"),
]

# Ce qui ne se falsifie pas : des faits extérieurs au fichier, qui devaient
# être vrais au lieu et à l'heure déclarés. Une empreinte et un champ EXIF se
# fabriquent ; la position du Soleil ce jour-là, non.
CONCORDANCES = [
    ("Position du Soleil", "Position of the Sun",
     "azimut et hauteur d&#233;duits des ombres port&#233;es et des "
     "&#233;clairements, compar&#233;s &#224; l'&#233;ph&#233;m&#233;ride du "
     "lieu et de l'heure d&#233;clar&#233;s",
     "azimuth and altitude inferred from cast shadows and illumination, "
     "compared with the ephemeris for the declared place and time"),
    ("&#201;tat de la mer et niveau d'eau", "Sea state and water level",
     "hauteur de mar&#233;e et &#233;tat de la surface &#224; l'heure "
     "d&#233;clar&#233;e, compar&#233;s aux pr&#233;dictions et aux "
     "observations mar&#233;graphiques",
     "tidal height and surface state at the declared time, compared with "
     "predictions and tide-gauge records"),
    ("Objets mobiles dat&#233;s", "Dated moving objects",
     "navire, a&#233;ronef ou &#233;olienne en rotation pr&#233;sent dans le "
     "champ, recoup&#233; avec un registre horodat&#233;",
     "a ship, aircraft or turning wind turbine present in the field, "
     "cross-checked against a timestamped register"),
    ("Conditions m&#233;t&#233;orologiques observ&#233;es",
     "Observed weather conditions",
     "couverture nuageuse, visibilit&#233; et pr&#233;cipitations "
     "relev&#233;es par la station la plus proche &#224; l'heure la plus "
     "proche",
     "cloud cover, visibility and precipitation recorded by the nearest "
     "station at the nearest hour"),
    ("Rep&#232;res attendus dans le champ", "Expected landmarks in the field",
     "pr&#233;sence, position relative et ordre des rep&#232;res que la "
     "direction de vis&#233;e d&#233;clar&#233;e impose",
     "presence, relative position and order of the landmarks that the declared "
     "sighting direction requires"),
]

CONTROLES = [
    ("Le fichier remis est celui qui a &#233;t&#233; d&#233;clar&#233;&#160;: "
     "l'empreinte SHA-256 recalcul&#233;e concorde, et sa datation est "
     "attest&#233;e par un tiers.",
     "The submitted file is the one declared: the recomputed SHA-256 digest "
     "matches, and its date is attested by a third party."),
    ("Deux concordances au moins du tableau&#160;4 sont &#233;tablies, et "
     "aucune discordance ne l'est.",
     "At least two of the concordances in table&#160;4 are established, and no "
     "discordance is."),
    ("La cha&#238;ne du tableau&#160;2 est reconstituable de la sc&#232;ne au "
     "fichier&#160;: chaque poste est renseign&#233; ou d&#233;clar&#233; "
     "indisponible, et la part optique du grossissement est s&#233;par&#233;e "
     "de sa part num&#233;rique.",
     "The chain of table&#160;2 can be reconstructed from scene to file: every "
     "stage is filled in or declared unavailable, and the optical share of the "
     "magnification is separated from its digital share."),
    ("La cible est identifi&#233;e au sens de 2.5.1, et ses dimensions "
     "proviennent d'une source ind&#233;pendante, dat&#233;e et citable.",
     "The target is identified within the meaning of 2.5.1, and its dimensions "
     "come from an independent, dated and citable source."),
    ("La position de l'observateur est certifi&#233;e au sens de 2.5.2.",
     "The observer's position is certified within the meaning of 2.5.2."),
    ("La caract&#233;ristique &#224; mesurer a &#233;t&#233; "
     "d&#233;sign&#233;e et consign&#233;e avant tout contr&#244;le de "
     "r&#233;solution, et elle est effectivement r&#233;solue selon 1.5.3.",
     "The feature to be measured was designated and recorded before any "
     "resolution check, and it is actually resolved per 1.5.3."),
    ("Le bord mesur&#233; est une discontinuit&#233; r&#233;solue au sens de "
     "1.5.5, et non un d&#233;grad&#233;.",
     "The measured edge is a resolved discontinuity within the meaning of "
     "1.5.5, not a gradient."),
    ("La zone mesur&#233;e ne provient pas d'un traitement reconstruisant de "
     "l'information non enregistr&#233;e.",
     "The measured area does not come from a process reconstructing "
     "information that was never recorded."),
    ("Toute occultation visible est identifi&#233;e et attribu&#233;e, au "
     "sens de 3.5.",
     "Every visible occultation is identified and attributed, within the "
     "meaning of 3.5."),
    ("Chaque donn&#233;e du dossier porte sa source, sa date, son incertitude "
     "et, le cas &#233;ch&#233;ant, la mention <em>d&#233;claratif</em>.",
     "Every datum in the file carries its source, its date, its uncertainty "
     "and, where applicable, the label <em>declarative</em>."),
]


def bloc_2(fr):
    t_pieces = tab(
        ("Tableau&#160;3 &#8212; pi&#232;ces &#224; fournir. La liste est "
         "exhaustive et aucune pi&#232;ce n'est facultative."
         if fr else
         "Table&#160;3 &#8212; evidence to be supplied. The list is exhaustive "
         "and no item is optional."),
        (["N&#176;", "Pi&#232;ce", "Forme admise"] if fr
         else ["No.", "Item", "Admissible form"]),
        [rang(["%02d" % (i + 1), p[0 if fr else 1], p[2 if fr else 3]],
              num=(0,)) for i, p in enumerate(PIECES)], num=(0,))

    t_conc = tab(
        ("Tableau&#160;4 &#8212; concordances externes. Chacune porte sur un "
         "fait qui devait &#234;tre vrai au lieu et &#224; l'heure "
         "d&#233;clar&#233;s, et qui ne se fabrique pas depuis le fichier."
         if fr else
         "Table&#160;4 &#8212; external concordances. Each bears on a fact "
         "that had to be true at the declared place and time, and that cannot "
         "be fabricated from the file."),
        (["N&#176;", "Concordance", "Ce qui est compar&#233;"] if fr
         else ["No.", "Concordance", "What is compared"]),
        [rang(["%02d" % (i + 1), c[0 if fr else 1], c[2 if fr else 3]],
              num=(0,)) for i, c in enumerate(CONCORDANCES)], num=(0,))

    ctrl = "\n".join("  <li>%s</li>" % c[0 if fr else 1] for c in CONTROLES)

    if fr:
        return "\n".join([
            partie("2", "Recevabilit&#233; du dossier", saut=True),
            clause("2.1", "La pr&#233;sente partie &#233;nonce ce que le "
                   "demandeur fournit et ce qui est v&#233;rifi&#233; avant "
                   "toute analyse. Elle s'applique &#224; tout clich&#233; "
                   "soumis, y compris pris sans intention de mesure."),
            clause("2.2", "Le crit&#232;re d'acceptation n'est pas "
                   "&#171;&#160;grossissement autoris&#233; ou "
                   "interdit&#160;&#187;. Il est&#160;: l'information "
                   "photographique est-elle assez document&#233;e et assez "
                   "exploitable pour permettre une mesure fiable&#160;?"),
            sous("2.3 Pi&#232;ces exig&#233;es"),
            clause("2.3.1", "Le demandeur fournit les cinq pi&#232;ces du "
                   "tableau&#160;3. Une pi&#232;ce absente n'est jamais "
                   "suppl&#233;&#233;e par une estimation, une reconstitution "
                   "ou une valeur de r&#233;f&#233;rence."),
            t_pieces,
            clause("2.3.2", "Chaque source produite est dat&#233;e et citable. "
                   "Une source sans date n'est pas admise."),
            clause("2.3.3", "Aucune dimension, aucune distance et aucune "
                   "position n'est &#233;tablie &#224; partir de la "
                   "photographie soumise."),
            clause("2.3.4", "Ce que l'op&#233;rateur rapporte sans pi&#232;ce "
                   "&#8212; facteur de grossissement, modes actifs, "
                   "circonstances &#8212; est marqu&#233; "
                   "<em>d&#233;claratif</em>. Un &#233;l&#233;ment "
                   "d&#233;claratif ne porte &#224; lui seul aucune "
                   "conclusion."),
            sous("2.4 Authenticit&#233; du fichier"),
            clause("2.4.1", "L'empreinte SHA-256 &#233;tablit que le fichier "
                   "n'a pas chang&#233; depuis sa d&#233;claration. Elle "
                   "n'&#233;tablit ni qu'il sort d'un appareil, ni la date de "
                   "la prise de vue."),
            clause("2.4.2", "Les m&#233;tadonn&#233;es EXIF s'&#233;crivent. "
                   "Elles renseignent la cha&#238;ne&#160;; elles ne prouvent "
                   "pas l'origine."),
            clause("2.4.3", "L'authenticit&#233; s'&#233;tablit par la "
                   "concordance entre le fichier et des faits v&#233;rifiables "
                   "ind&#233;pendamment de lui. Deux concordances au moins du "
                   "tableau&#160;4 sont exig&#233;es, issues de deux "
                   "cat&#233;gories diff&#233;rentes."),
            t_conc,
            clause("2.4.4", "Une concordance qu'on ne parvient pas &#224; "
                   "&#233;tablir rend le dossier non concluant. Une "
                   "discordance le fait rejeter."),
            sous("2.5 D&#233;finitions op&#233;ratoires"),
            clause("2.5.1", "<strong>Cible identifi&#233;e.</strong> Deux "
                   "sources ind&#233;pendantes et dat&#233;es concordent sur "
                   "la d&#233;signation de la cible et sur sa position. La "
                   "ressemblance visuelle n'identifie rien."),
            clause("2.5.2", "<strong>Position certifi&#233;e.</strong> "
                   "Relev&#233; satellitaire assorti de son incertitude, ou "
                   "rel&#232;vement sur deux rep&#232;res de position "
                   "connue&#160;; dans les deux cas confirm&#233;e par la vue "
                   "grand-angle."),
            clause("2.5.3", "<strong>Caract&#233;ristique d&#233;sign&#233;e."
                   "</strong> La grandeur que l'analyse pr&#233;tend mesurer "
                   "est nomm&#233;e et consign&#233;e avant tout contr&#244;le "
                   "de r&#233;solution. La changer rouvre le dossier et le "
                   "rapport le mentionne."),
            clause("2.5.4", "<strong>Dossier complet.</strong> Les cinq "
                   "pi&#232;ces sont fournies, les dix contr&#244;les de 2.6 "
                   "sont pass&#233;s, et chaque donn&#233;e porte sa source, "
                   "sa date et son incertitude."),
            sous("2.6 Contr&#244;les"),
            clause("2.6.1", "Les contr&#244;les suivants sont conduits dans "
                   "l'ordre, avant toute analyse. Le premier qui &#233;choue "
                   "arr&#234;te la proc&#233;dure et fixe le verdict."),
            "<ul>\n%s\n</ul>" % ctrl,
            clause("2.6.2", "Un dossier qui passe les dix contr&#244;les est "
                   "recevable. La recevabilit&#233; n'est pas une conclusion, "
                   "et le rapport ne la pr&#233;sente jamais comme telle."),
        ])

    return "\n".join([
        partie("2", "Admissibility of the file", saut=True),
        clause("2.1", "This part states what the submitter supplies and what "
               "is checked before any analysis. It applies to any frame "
               "submitted, including one taken with no measurement in mind."),
        clause("2.2", "The acceptance criterion is not &#8220;magnification "
               "permitted or forbidden&#8221;. It is: is the photographic "
               "information documented enough and usable enough to support a "
               "reliable measurement?"),
        sous("2.3 Required evidence"),
        clause("2.3.1", "The submitter supplies the five items of "
               "table&#160;3. A missing item is never made good by an "
               "estimate, a reconstruction or a reference value."),
        t_pieces,
        clause("2.3.2", "Every source produced is dated and citable. An "
               "undated source is not admissible."),
        clause("2.3.3", "No dimension, no distance and no position is "
               "established from the submitted photograph."),
        clause("2.3.4", "Whatever the operator reports without supporting "
               "evidence &#8212; magnification factor, active modes, "
               "circumstances &#8212; is labelled <em>declarative</em>. A "
               "declarative item carries no conclusion on its own."),
        sous("2.4 Authenticity of the file"),
        clause("2.4.1", "The SHA-256 digest establishes that the file has not "
               "changed since it was declared. It establishes neither that it "
               "came out of a camera, nor the date of the capture."),
        clause("2.4.2", "EXIF metadata can be written. They document the "
               "chain; they do not prove origin."),
        clause("2.4.3", "Authenticity is established by the concordance "
               "between the file and facts verifiable independently of it. At "
               "least two concordances from table&#160;4 are required, drawn "
               "from two different categories."),
        t_conc,
        clause("2.4.4", "A concordance that cannot be established makes the "
               "file inconclusive. A discordance has it rejected."),
        sous("2.5 Operative definitions"),
        clause("2.5.1", "<strong>Identified target.</strong> Two independent, "
               "dated sources agree on the target's designation and on its "
               "position. Visual resemblance identifies nothing."),
        clause("2.5.2", "<strong>Certified position.</strong> A satellite "
               "reading with its stated uncertainty, or a resection on two "
               "landmarks of known position; in both cases confirmed by the "
               "wide-angle frame."),
        clause("2.5.3", "<strong>Designated feature.</strong> The quantity the "
               "analysis claims to measure is named and recorded before any "
               "resolution check. Changing it reopens the file and the report "
               "says so."),
        clause("2.5.4", "<strong>Complete file.</strong> The five items are "
               "supplied, the ten checks of 2.6 are passed, and every datum "
               "carries its source, its date and its uncertainty."),
        sous("2.6 Checks"),
        clause("2.6.1", "The following checks are carried out in order, before "
               "any analysis. The first that fails stops the procedure and "
               "fixes the verdict."),
        "<ul>\n%s\n</ul>" % ctrl,
        clause("2.6.2", "A file that passes the ten checks is admissible. "
               "Admissibility is not a conclusion, and the report never "
               "presents it as one."),
    ])


# ─────────────────────────────────────────────────────────────────────────────
# Partie 3 — analyse et certification
# ─────────────────────────────────────────────────────────────────────────────
PARAMETRES = [
    ("Altitude de l'observateur", "Observer altitude",
     "mod&#232;le num&#233;rique de terrain au point relev&#233;, plus la "
     "hauteur de l'axe optique&#160;; en mer, le niveau d'eau &#224; l'heure "
     "exacte",
     "digital terrain model at the recorded point, plus the height of the "
     "optical axis; at sea, the water level at the exact time"),
    ("Distance", "Distance",
     "calcul g&#233;od&#233;sique &#224; partir des deux positions "
     "certifi&#233;es",
     "geodesic computation from the two certified positions"),
    ("Altitude de la base de la cible", "Altitude of the target's base",
     "mod&#232;le num&#233;rique de terrain, ou niveau de la mer "
     "corrig&#233; de la mar&#233;e",
     "digital terrain model, or sea level corrected for tide"),
    ("Hauteur de la cible", "Target height",
     "plan cot&#233;, fiche officielle, sp&#233;cification du constructeur",
     "dimensioned drawing, official record, manufacturer's specification"),
    ("R&#233;fraction", "Refraction",
     "profil vertical mesur&#233; s'il existe&#160;; &#224; d&#233;faut la "
     "plage plausible enti&#232;re pour le site, la saison et l'heure",
     "measured vertical profile where one exists; failing that, the whole "
     "plausible range for the site, season and hour"),
]

REGIMES = [
    ("Mirage inf&#233;rieur", "Inferior mirage",
     "image invers&#233;e sous l'objet, s&#233;par&#233;e par une ligne "
     "nette&#160;; s'att&#233;nue quand le point de vue s'&#233;l&#232;ve",
     "an inverted image below the object, separated by a sharp line; weakens "
     "as the viewpoint rises"),
    ("Mirage sup&#233;rieur", "Superior mirage",
     "image invers&#233;e au-dessus de l'objet&#160;; appara&#238;t et "
     "dispara&#238;t au fil des heures, souvent au-dessus d'une surface plus "
     "froide que l'air",
     "an inverted image above the object; appears and disappears over the "
     "hours, often above a surface colder than the air"),
    ("Looming", "Looming",
     "l'objet entier remonte sans se d&#233;former&#160;: les rapports de "
     "hauteur internes sont conserv&#233;s",
     "the whole object rises without distortion: internal height ratios are "
     "preserved"),
    ("Conduit", "Ducting",
     "objet visible bien au-del&#224; de sa port&#233;e habituelle, contraste "
     "soutenu, bandes horizontales, transitions abruptes d'une vue &#224; "
     "l'autre de la s&#233;rie",
     "object visible well beyond its usual range, sustained contrast, "
     "horizontal banding, abrupt transitions from one frame of the series to "
     "the next"),
    ("D&#233;formation verticale", "Vertical distortion",
     "les rapports de hauteur entre &#233;l&#233;ments de cote connue ne sont "
     "pas conserv&#233;s&#160;; &#233;tirement ou compression selon la couche",
     "height ratios between elements of known elevation are not preserved; "
     "stretching or compression depending on the layer"),
]


def bloc_3(fr):
    t_param = tab(
        ("Tableau&#160;5 &#8212; param&#232;tres vari&#233;s. L'intervalle "
         "retenu est celui que permettent les meilleures sources et les "
         "meilleurs instruments dont l'observateur disposait."
         if fr else
         "Table&#160;5 &#8212; parameters varied. The interval adopted is the "
         "one afforded by the best sources and instruments available to the "
         "observer."),
        (["N&#176;", "Param&#232;tre", "D'o&#249; vient son intervalle"] if fr
         else ["No.", "Parameter", "Where its interval comes from"]),
        [rang(["%02d" % (i + 1), p[0 if fr else 1], p[2 if fr else 3]],
              num=(0,)) for i, p in enumerate(PARAMETRES)], num=(0,))

    t_reg = tab(
        ("Tableau&#160;6 &#8212; r&#233;gimes atmosph&#233;riques et leurs "
         "signatures. Chacune se cherche sur la s&#233;rie enti&#232;re, "
         "jamais sur une image isol&#233;e."
         if fr else
         "Table&#160;6 &#8212; atmospheric regimes and their signatures. Each "
         "is looked for across the whole series, never in a single frame."),
        (["N&#176;", "R&#233;gime", "Signature observable"] if fr
         else ["No.", "Regime", "Observable signature"]),
        [rang(["%02d" % (i + 1), r[0 if fr else 1], r[2 if fr else 3]],
              num=(0,)) for i, r in enumerate(REGIMES)], num=(0,))

    if fr:
        return "\n".join([
            partie("3", "Analyse et certification", saut=True),
            clause("3.1", "La pr&#233;sente partie s'adresse aux analystes. "
                   "Elle fixe ce qui est arr&#234;t&#233; avant l'observation, "
                   "ce qui est calcul&#233;, comment les r&#233;gimes "
                   "atmosph&#233;riques sont trait&#233;s, et qui certifie."),
            sous("3.2 Seuil de r&#233;futation, arr&#234;t&#233; d'avance"),
            clause("3.2.1", "Le seuil de r&#233;futation est arr&#234;t&#233;, "
                   "dat&#233; et publi&#233; <strong>avant</strong> l'examen "
                   "des images. Il &#233;nonce la divergence, entre la portion "
                   "visible observ&#233;e et la portion visible pr&#233;dite, "
                   "&#224; partir de laquelle le r&#233;sultat est "
                   "d&#233;clar&#233; anomal."),
            clause("3.2.2", "Le seuil s'exprime en fraction de la hauteur de "
                   "la cible et en multiples de l'incertitude "
                   "compos&#233;e. Il n'est ni relev&#233; ni abaiss&#233; "
                   "apr&#232;s consultation des images."),
            clause("3.2.3", "&#192; d&#233;faut de seuil sp&#233;cifique "
                   "d&#233;pos&#233;, le seuil par d&#233;faut est celui-ci, "
                   "et les deux conditions sont exig&#233;es "
                   "ensemble&#160;: la divergence atteint trois fois "
                   "l'incertitude compos&#233;e de la mesure, "
                   "<strong>et</strong> elle tombe hors de l'enveloppe de "
                   "sensibilit&#233; de 3.4."),
            clause("3.2.4", "Un dossier analys&#233; sans seuil "
                   "pr&#233;alablement d&#233;pos&#233; ne peut pas conclure "
                   "&#224; une anomalie. Il peut conclure &#224; une "
                   "compatibilit&#233;."),
            sous("3.3 Courbe pr&#233;dictive"),
            clause("3.3.1", "Avant toute comparaison, l'analyste "
                   "&#233;tablit la courbe pr&#233;dictive&#160;: pour "
                   "l'altitude de l'observateur, la hauteur de la cible et la "
                   "distance, la <strong>fraction de la cible "
                   "pr&#233;dite visible</strong>."),
            clause("3.3.2", "La courbe est &#233;tablie sur toute la plage de "
                   "distances et d'altitudes pertinente, et non au seul point "
                   "du clich&#233;. Elle est publi&#233;e avec le rapport sous "
                   "forme de valeurs num&#233;riques reproductibles, avec la "
                   "m&#233;thode et les param&#232;tres qui l'ont "
                   "produite."),
            clause("3.3.3", "La comparaison porte sur une grandeur continue "
                   "&#8212; la fraction visible &#8212; et non sur une "
                   "alternative visible ou invisible. Le rapport &#233;nonce "
                   "la fraction observ&#233;e, la fraction pr&#233;dite et "
                   "leur &#233;cart, chacune avec son incertitude."),
            clause("3.3.4", "Lorsque plusieurs clich&#233;s d'une m&#234;me "
                   "cible existent &#224; des distances ou &#224; des "
                   "altitudes diff&#233;rentes, ils sont port&#233;s sur la "
                   "m&#234;me courbe. La coh&#233;rence de la s&#233;rie "
                   "p&#232;se davantage qu'un point isol&#233;, et une "
                   "s&#233;rie qui suit la courbe pr&#233;dite sur plusieurs "
                   "distances vaut davantage qu'un &#233;cart unique."),
            sous("3.4 Analyse de sensibilit&#233;"),
            clause("3.4.1", "Chaque param&#232;tre du tableau&#160;5 est "
                   "vari&#233; syst&#233;matiquement dans son intervalle "
                   "d'incertitude, et l'enveloppe des pr&#233;dictions qui en "
                   "r&#233;sulte est rapport&#233;e."),
            t_param,
            clause("3.4.2", "L'intervalle retenu est celui que permettent les "
                   "meilleures sources et les meilleurs instruments dont "
                   "l'observateur disposait au moment de la prise de vue. Il "
                   "n'est ni &#233;largi par pr&#233;caution, ni "
                   "resserr&#233; par commodit&#233;, et son origine est "
                   "cit&#233;e."),
            clause("3.4.3", "La conclusion ne porte que si elle tient sur "
                   "l'enveloppe enti&#232;re. Si une combinaison admissible "
                   "des param&#232;tres rend l'observation conforme &#224; la "
                   "pr&#233;diction, le r&#233;sultat n'est pas anomal."),
            clause("3.4.4", "L'analyste rapporte explicitement la combinaison "
                   "la plus d&#233;favorable &#224; sa propre conclusion, et "
                   "ce qu'elle donne."),
            sous("3.5 Occultation"),
            clause("3.5.1", "Ne sont analys&#233;s que les clich&#233;s dont "
                   "<strong>toute</strong> occultation visible est "
                   "identifi&#233;e et attribu&#233;e &#224; une cause "
                   "&#233;tablie."),
            clause("3.5.2", "Un clich&#233; o&#249; une partie de la cible est "
                   "masqu&#233;e par autre chose que la surface elle-m&#234;me "
                   "&#8212; relief interm&#233;diaire, v&#233;g&#233;tation, "
                   "construction, navire, vague, banc de brume, nuage bas "
                   "&#8212; est &#233;cart&#233;&#160;: la fraction visible "
                   "n'y est pas mesurable."),
            clause("3.5.3", "Un clich&#233; o&#249; une partie de la cible est "
                   "masqu&#233;e pour une raison qui ne peut pas &#234;tre "
                   "&#233;tablie est &#233;cart&#233;. L'ind&#233;cision sur "
                   "la cause n'est jamais tranch&#233;e en faveur de "
                   "l'hypoth&#232;se qu'on examine."),
            clause("3.5.4", "Le profil interm&#233;diaire est v&#233;rifi&#233; "
                   "sur les donn&#233;es de la pi&#232;ce&#160;05 avant toute "
                   "mesure, et non apr&#232;s constatation d'un &#233;cart."),
            sous("3.6 R&#233;gimes atmosph&#233;riques"),
            clause("3.6.1", "Les cinq r&#233;gimes du tableau&#160;6 sont "
                   "recherch&#233;s sur la s&#233;rie enti&#232;re, avant la "
                   "comparaison de 3.3, et le r&#233;sultat de cette recherche "
                   "est consign&#233; qu'il soit positif ou n&#233;gatif."),
            t_reg,
            clause("3.6.2", "Le test op&#233;ratoire de la d&#233;formation "
                   "verticale&#160;: les rapports de hauteur entre au moins "
                   "trois &#233;l&#233;ments de cote connue de la cible sont "
                   "mesur&#233;s dans l'image et compar&#233;s &#224; leurs "
                   "valeurs r&#233;elles. Un &#233;cart sup&#233;rieur &#224; "
                   "trois fois l'incertitude de ces rapports signale une "
                   "d&#233;formation."),
            clause("3.6.3", "Un r&#233;gime ne peut &#234;tre invoqu&#233; que "
                   "s'il a &#233;t&#233; recherch&#233; avant la comparaison "
                   "et s'il est &#233;tabli par des signatures relev&#233;es "
                   "dans les images et par les donn&#233;es "
                   "m&#233;t&#233;orologiques du lieu et de l'heure. Il n'est "
                   "<strong>jamais</strong> introduit apr&#232;s coup pour "
                   "rendre compte d'un &#233;cart constat&#233;."),
            clause("3.6.4", "Un r&#233;gime &#233;tabli rend le clich&#233; "
                   "non concluant. Il ne le rend ni favorable ni "
                   "d&#233;favorable, et cela vaut quel que soit le sens de "
                   "l'&#233;cart observ&#233;."),
            sous("3.7 Certification coll&#233;giale"),
            clause("3.7.1", "Aucun verdict n'est certifi&#233; par un seul "
                   "analyste. Trois analyses ind&#233;pendantes au moins sont "
                   "conduites sur le m&#234;me dossier et sous le m&#234;me "
                   "seuil d&#233;pos&#233;."),
            clause("3.7.2", "Les trois analystes travaillent "
                   "s&#233;par&#233;ment et ne connaissent pas leurs "
                   "conclusions respectives avant de rendre la leur."),
            clause("3.7.3", "Chacun d&#233;clare tout int&#233;r&#234;t dans "
                   "l'issue et toute participation &#224; la prise de vue. "
                   "L'op&#233;rateur du clich&#233; ne peut &#234;tre aucun "
                   "des trois."),
            clause("3.7.4", "Le r&#233;sultat est certifi&#233; lorsque les "
                   "trois analyses convergent. Toute divergence rend le "
                   "r&#233;sultat non concluant&#160;: les trois analyses sont "
                   "publi&#233;es, le point de d&#233;saccord est nomm&#233;, "
                   "et le dossier reste ouvert."),
            clause("3.7.5", "Les trois rapports sont publi&#233;s ensemble, "
                   "sign&#233;s, avec les d&#233;clarations "
                   "d'int&#233;r&#234;t."),
            sous("3.8 Bar&#232;me de d&#233;cision"),
            clause("3.8.1", "<strong>Rejet.</strong> Le dossier &#233;choue "
                   "&#224; l'un des contr&#244;les de 2.6, ou une discordance "
                   "du tableau&#160;4 est &#233;tablie. Il est &#233;cart&#233; "
                   "sans analyse."),
            clause("3.8.2", "<strong>Non concluant.</strong> Le dossier est "
                   "recevable mais la caract&#233;ristique n'est pas "
                   "r&#233;solue, ou une occultation n'est pas "
                   "attribu&#233;e, ou un r&#233;gime atmosph&#233;rique est "
                   "&#233;tabli, ou l'enveloppe de sensibilit&#233; recouvre "
                   "la pr&#233;diction, ou les trois analyses divergent."),
            clause("3.8.3", "<strong>Compatible.</strong> La fraction visible "
                   "observ&#233;e tombe dans l'enveloppe pr&#233;dite, "
                   "l'&#233;cart reste sous le seuil d&#233;pos&#233;, et les "
                   "trois analyses convergent."),
            clause("3.8.4", "<strong>Anomal.</strong> L'&#233;cart franchit le "
                   "seuil d&#233;pos&#233; de 3.2, il tient sur l'enveloppe "
                   "enti&#232;re de 3.4, aucun r&#233;gime atmosph&#233;rique "
                   "n'est &#233;tabli, aucune occultation n'est "
                   "inexpliqu&#233;e, et les trois analyses convergent."),
            clause("3.8.5", "Le verdict porte sur une caract&#233;ristique "
                   "d&#233;sign&#233;e, non sur le clich&#233; en bloc. Un "
                   "m&#234;me clich&#233; peut trancher une mesure large et "
                   "pas une mesure fine."),
            clause("3.8.6", "Aucune valeur n'est ajust&#233;e apr&#232;s "
                   "examen pour faire correspondre le r&#233;sultat &#224; "
                   "l'image. Une correction n'est admise que si elle provient "
                   "d'une source ind&#233;pendante nouvelle, et le rapport "
                   "indique la valeur ant&#233;rieure, la valeur retenue et la "
                   "source qui a tranch&#233;."),
            clause("3.8.7", "Un dossier compl&#233;t&#233; plus tard est "
                   "r&#233;examin&#233; sans que la photographie soit "
                   "reprise&#160;: la prise de vue n'est jamais &#224; "
                   "refaire."),
            sous("3.9 Rapport"),
            clause("3.9.1", "Le rapport &#233;nonce&#160;: le verdict et la "
                   "caract&#233;ristique sur laquelle il porte&#160;; le seuil "
                   "d&#233;pos&#233; et sa date&#160;; la fraction "
                   "observ&#233;e, la fraction pr&#233;dite et leur "
                   "&#233;cart, chacune avec son incertitude&#160;; "
                   "l'enveloppe de sensibilit&#233; et la combinaison la plus "
                   "d&#233;favorable&#160;; le r&#233;sultat de la recherche "
                   "de r&#233;gimes&#160;; les pi&#232;ces re&#231;ues avec "
                   "leur source et leur date&#160;; la cha&#238;ne du "
                   "tableau&#160;2&#160;; l'empreinte du fichier "
                   "d'origine&#160;; et le contr&#244;le de 2.6 qui a "
                   "&#233;chou&#233; le cas &#233;ch&#233;ant."),
            clause("3.9.2", "Le rapport est publi&#233; avec le fichier "
                   "d'origine ou, si celui-ci ne peut &#234;tre "
                   "diffus&#233;, avec son empreinte et l'indication de qui le "
                   "d&#233;tient."),
            clause("3.9.3", "Le verdict <em>non concluant</em> n'est ni "
                   "favorable ni d&#233;favorable. Il n'est jamais "
                   "pr&#233;sent&#233; comme un r&#233;sultat."),
            encadre("R&#232;gle sans exception",
                    "<p>Une pi&#232;ce manquante ne se remplace pas, un seuil "
                    "ne se d&#233;place pas apr&#232;s coup, et un "
                    "r&#233;gime atmosph&#233;rique ne s'invoque pas pour "
                    "expliquer un &#233;cart qu'on vient de constater. Un "
                    "dossier incomplet ne devient pas concluant parce que "
                    "l'image est frappante, parce que le demandeur est de "
                    "bonne foi, ou parce que le r&#233;sultat attendu "
                    "arrangerait.</p>"),
        ])

    return "\n".join([
        partie("3", "Analysis and certification", saut=True),
        clause("3.1", "This part addresses the analysts. It fixes what is "
               "settled before the observation, what is computed, how "
               "atmospheric regimes are handled, and who certifies."),
        sous("3.2 Refutation threshold, settled in advance"),
        clause("3.2.1", "The refutation threshold is settled, dated and "
               "published <strong>before</strong> the images are examined. It "
               "states the divergence, between the observed visible fraction "
               "and the predicted visible fraction, from which the result is "
               "declared anomalous."),
        clause("3.2.2", "The threshold is expressed as a fraction of the "
               "target's height and in multiples of the combined uncertainty. "
               "It is neither raised nor lowered after the images have been "
               "seen."),
        clause("3.2.3", "Failing a specific deposited threshold, the default "
               "threshold is this one, and both conditions are required "
               "together: the divergence reaches three times the combined "
               "uncertainty of the measurement, <strong>and</strong> it falls "
               "outside the sensitivity envelope of 3.4."),
        clause("3.2.4", "A file analysed without a previously deposited "
               "threshold cannot conclude to an anomaly. It may conclude to "
               "compatibility."),
        sous("3.3 Predictive curve"),
        clause("3.3.1", "Before any comparison, the analyst establishes the "
               "predictive curve: for the observer's altitude, the target's "
               "height and the distance, the <strong>fraction of the target "
               "predicted visible</strong>."),
        clause("3.3.2", "The curve is established across the whole relevant "
               "range of distances and altitudes, not at the single point of "
               "the frame. It is published with the report as reproducible "
               "numerical values, together with the method and parameters that "
               "produced it."),
        clause("3.3.3", "The comparison bears on a continuous quantity &#8212; "
               "the visible fraction &#8212; and not on a visible-or-invisible "
               "alternative. The report states the observed fraction, the "
               "predicted fraction and their difference, each with its "
               "uncertainty."),
        clause("3.3.4", "Where several frames of the same target exist at "
               "different distances or altitudes, they are plotted on the same "
               "curve. The consistency of the series weighs more than an "
               "isolated point, and a series that follows the predicted curve "
               "across several distances weighs more than a single "
               "discrepancy."),
        sous("3.4 Sensitivity analysis"),
        clause("3.4.1", "Each parameter in table&#160;5 is varied "
               "systematically across its uncertainty interval, and the "
               "resulting envelope of predictions is reported."),
        t_param,
        clause("3.4.2", "The interval adopted is the one afforded by the best "
               "sources and instruments available to the observer at the time "
               "of capture. It is neither widened out of caution nor narrowed "
               "for convenience, and its origin is cited."),
        clause("3.4.3", "The conclusion holds only if it holds across the "
               "whole envelope. If any admissible combination of the "
               "parameters makes the observation agree with the prediction, "
               "the result is not anomalous."),
        clause("3.4.4", "The analyst explicitly reports the combination least "
               "favourable to their own conclusion, and what it yields."),
        sous("3.5 Occultation"),
        clause("3.5.1", "Only frames in which <strong>every</strong> visible "
               "occultation is identified and attributed to an established "
               "cause are analysed."),
        clause("3.5.2", "A frame in which part of the target is hidden by "
               "anything other than the surface itself &#8212; intervening "
               "ground, vegetation, a structure, a ship, a wave, a fog bank, a "
               "low cloud &#8212; is set aside: the visible fraction is not "
               "measurable in it."),
        clause("3.5.3", "A frame in which part of the target is hidden for a "
               "reason that cannot be established is set aside. Indecision "
               "about the cause is never resolved in favour of the hypothesis "
               "under examination."),
        clause("3.5.4", "The intervening profile is checked against the data "
               "of item&#160;05 before any measurement, and not after a "
               "discrepancy has been noticed."),
        sous("3.6 Atmospheric regimes"),
        clause("3.6.1", "The five regimes of table&#160;6 are looked for "
               "across the whole series, before the comparison of 3.3, and the "
               "outcome of that search is recorded whether it is positive or "
               "negative."),
        t_reg,
        clause("3.6.2", "The operative test for vertical distortion: the "
               "height ratios between at least three elements of known "
               "elevation on the target are measured in the image and compared "
               "with their real values. A departure greater than three times "
               "the uncertainty of those ratios signals distortion."),
        clause("3.6.3", "A regime may be invoked only if it was looked for "
               "before the comparison and is established by signatures found "
               "in the images and by the meteorological data for the place and "
               "hour. It is <strong>never</strong> introduced afterwards to "
               "account for an observed discrepancy."),
        clause("3.6.4", "An established regime makes the frame inconclusive. "
               "It makes it neither favourable nor unfavourable, and this "
               "holds whichever way the observed discrepancy runs."),
        sous("3.7 Collegial certification"),
        clause("3.7.1", "No verdict is certified by a single analyst. At least "
               "three independent analyses are carried out on the same file "
               "and under the same deposited threshold."),
        clause("3.7.2", "The three analysts work separately and do not know "
               "one another's conclusions before rendering their own."),
        clause("3.7.3", "Each declares any interest in the outcome and any "
               "part taken in the capture. The operator of the frame may be "
               "none of the three."),
        clause("3.7.4", "The result is certified when the three analyses "
               "agree. Any divergence makes the result inconclusive: the three "
               "analyses are published, the point of disagreement is named, "
               "and the file stays open."),
        clause("3.7.5", "The three reports are published together, signed, "
               "with the declarations of interest."),
        sous("3.8 Decision scale"),
        clause("3.8.1", "<strong>Rejected.</strong> The file fails one of the "
               "checks of 2.6, or a discordance from table&#160;4 is "
               "established. It is set aside without analysis."),
        clause("3.8.2", "<strong>Inconclusive.</strong> The file is admissible "
               "but the feature is not resolved, or an occultation is not "
               "attributed, or an atmospheric regime is established, or the "
               "sensitivity envelope covers the prediction, or the three "
               "analyses diverge."),
        clause("3.8.3", "<strong>Compatible.</strong> The observed visible "
               "fraction falls within the predicted envelope, the difference "
               "stays below the deposited threshold, and the three analyses "
               "agree."),
        clause("3.8.4", "<strong>Anomalous.</strong> The difference crosses "
               "the deposited threshold of 3.2, it holds across the whole "
               "envelope of 3.4, no atmospheric regime is established, no "
               "occultation is unexplained, and the three analyses agree."),
        clause("3.8.5", "The verdict bears on a designated feature, not on the "
               "frame as a whole. One and the same frame may settle a coarse "
               "measurement and not a fine one."),
        clause("3.8.6", "No value is adjusted after examination to make the "
               "result match the image. A correction is admissible only if it "
               "comes from a new independent source, and the report states the "
               "previous value, the adopted value and the source that settled "
               "it."),
        clause("3.8.7", "A file completed later is re-examined without the "
               "photograph being retaken: the capture is never to be done "
               "again."),
        sous("3.9 Report"),
        clause("3.9.1", "The report states: the verdict and the feature it "
               "bears on; the deposited threshold and its date; the observed "
               "fraction, the predicted fraction and their difference, each "
               "with its uncertainty; the sensitivity envelope and the least "
               "favourable combination; the outcome of the regime search; the "
               "items received with their source and date; the chain of "
               "table&#160;2; the digest of the original file; and which check "
               "of 2.6 failed, where one did."),
        clause("3.9.2", "The report is published with the original file or, if "
               "that file cannot be circulated, with its digest and a "
               "statement of who holds it."),
        clause("3.9.3", "The <em>inconclusive</em> verdict is neither "
               "favourable nor unfavourable. It is never presented as a "
               "result."),
        encadre("Rule without exception",
                "<p>A missing item is not replaced, a threshold is not moved "
                "after the fact, and an atmospheric regime is not invoked to "
                "explain a discrepancy one has just noticed. An incomplete "
                "file does not become conclusive because the image is "
                "striking, because the submitter is in good faith, or because "
                "the expected result would suit.</p>"),
    ])


def corps(fr):
    resume = (
        '<div class="abstract"><span class="lab">%s</span>%s</div>' % (
            "Objet" if fr else "Purpose",
            ("<p>Trois parties. La premi&#232;re dit comment prendre une "
             "photographie qui ne sera pas &#233;cart&#233;e d'entr&#233;e. La "
             "deuxi&#232;me dit ce qu'il faut fournir avec elle et ce qui est "
             "v&#233;rifi&#233; avant toute analyse. La troisi&#232;me dit ce "
             "qui est arr&#234;t&#233; avant l'observation, ce qui est "
             "calcul&#233;, et &#224; quelle condition un r&#233;sultat est "
             "certifi&#233;.</p>"
             "<p>Un fort grossissement est autoris&#233;, y compris "
             "num&#233;rique. Ce qui est exig&#233; n'est pas de s'en priver, "
             "mais de documenter la cha&#238;ne de traitement et de conserver "
             "le fichier d'origine.</p>"
             "<p>Trois choses ne se n&#233;gocient pas&#160;: le seuil de "
             "r&#233;futation est d&#233;pos&#233; avant que les images soient "
             "vues, la conclusion doit tenir sur toute l'enveloppe "
             "d'incertitude, et aucun verdict n'est certifi&#233; par un seul "
             "analyste.</p>")
            if fr else
            ("<p>Three parts. The first states how to take a photograph that "
             "will not be set aside at the outset. The second states what must "
             "be supplied with it and what is checked before any analysis. The "
             "third states what is settled before the observation, what is "
             "computed, and under what condition a result is certified.</p>"
             "<p>Strong magnification is permitted, digital magnification "
             "included. What is required is not to do without it, but to "
             "document the processing chain and to preserve the original "
             "file.</p>"
             "<p>Three things are not negotiable: the refutation threshold is "
             "deposited before the images are seen, the conclusion must hold "
             "across the whole uncertainty envelope, and no verdict is "
             "certified by a single analyst.</p>")))
    return "\n\n".join([masthead(fr), resume,
                        bloc_1(fr), bloc_2(fr), bloc_3(fr)])


def main():
    controle()
    ecrire(corps(True), corps(False))
    print("Écrit : %s (%d ko)"
          % (os.path.relpath(CIBLE, RACINE), os.path.getsize(CIBLE) // 1024))
    print("  focales minimales : %s"
          % ", ".join("%d km → %d mm" % (d, focale_mini(d)) for d in DISTANCES))
    return 0


if __name__ == "__main__":
    sys.exit(main())
