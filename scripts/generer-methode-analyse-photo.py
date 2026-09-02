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

VERSION = "2.1"
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
    sous_titre = ("Partie&#160;1&#160;: prise de vue et mat&#233;riel. "
                  "Partie&#160;2&#160;: pi&#232;ces exig&#233;es et bar&#232;me "
                  "de d&#233;cision." if fr else
                  "Part&#160;1: image capture and equipment. Part&#160;2: "
                  "required evidence and decision scale.")
    champs = (("R&#233;dacteur", "Contact", "Version", "Date") if fr
              else ("Author", "Contact", "Version", "Date"))
    cases = "".join("<span>%s<b>%s</b></span>"
                    % (c, VERSION if c == "Version" else "&nbsp;")
                    for c in champs)
    return ('<div class="masthead">\n  <div class="kicker">%s</div>\n'
            '  <h1>%s</h1>\n  <p class="dek">%s</p>\n'
            '  <div class="byline">\n    %s\n  </div>\n</div>'
            % (kicker, titre, sous_titre, cases))


# Le corps ne contient que des exigences. Ces tournures y signalent une
# digression, et le document est refusé plutôt qu'écrit.
DIGRESSION = [
    r"coefficient de r[ée]fraction", r"refraction coefficient",
    r"hauteur masqu", r"hidden height",
    r"incertitude propag", r"propagated uncertainty",
    r"hauteur d'&#339;il", r"eye height",
    r"nous (?:avons|pensons|proposons)", r"version pr[ée]c[ée]dente",
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
         "cha&#238;ne optique. Un clich&#233; qui ne les atteint pas n'est pas "
         "rejet&#233;&#160;; il rel&#232;ve de 1.5.4."
         if fr else
         "Table&#160;1 &#8212; minimum equivalent focal length of the optical "
         "chain. A frame that falls short is not rejected; it falls under "
         "1.5.4."),
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
            clause("1.5.4", "Un clich&#233; qui n'atteint pas le "
                   "tableau&#160;1, ou dont la caract&#233;ristique vis&#233;e "
                   "n'est pas r&#233;solue au sens de 1.5.3, n'est pas "
                   "rejet&#233;. Il est class&#233; non concluant pour cette "
                   "caract&#233;ristique, et reste utilisable pour une "
                   "caract&#233;ristique plus grande."),
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
            clause("1.6.6", "La position satellitaire du point de vue est "
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
        clause("1.5.4", "A frame that falls short of table&#160;1, or whose "
               "intended feature is not resolved within the meaning of 1.5.3, "
               "is not rejected. It is classified inconclusive for that "
               "feature, and remains usable for a larger one."),
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
        clause("1.6.6", "The satellite position of the viewpoint is read and "
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
# Partie 2 — pièces exigées et barème
# ─────────────────────────────────────────────────────────────────────────────
PIECES = [
    ("Fichier d'origine",
     "Original file",
     "le fichier tel qu'il sort de l'appareil &#8212; brut lorsque l'appareil "
     "en produit un &#8212; avec ses m&#233;tadonn&#233;es EXIF intactes, son "
     "empreinte SHA-256 et la date de calcul de celle-ci",
     "the file exactly as it comes out of the camera &#8212; raw where the "
     "camera produces one &#8212; with its EXIF metadata intact, its SHA-256 "
     "digest and the date that digest was computed"),
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
     "d&#233;signation exacte de la cible et source ind&#233;pendante "
     "certifiant ses dimensions r&#233;elles&#160;: fiche officielle de "
     "l'ouvrage, plan cot&#233;, sp&#233;cification du constructeur, "
     "relev&#233; g&#233;od&#233;sique, registre horodat&#233;",
     "the target's exact designation and an independent source certifying its "
     "real dimensions: the structure's official record, a dimensioned drawing, "
     "a manufacturer's specification, a geodetic survey, a timestamped "
     "register"),
]

VERDICTS = [
    ("Rejet imm&#233;diat", "Immediate rejection",
     "fichier d'origine manquant ou modifi&#233;&#160;; empreinte SHA-256 "
     "absente ou non concordante&#160;; m&#233;tadonn&#233;es EXIF "
     "alt&#233;r&#233;es ou r&#233;&#233;crites&#160;; cha&#238;ne optique et "
     "num&#233;rique non documentable&#160;; cible douteuse&#160;; position "
     "d'observation non certifi&#233;e",
     "original file missing or modified; SHA-256 digest absent or not "
     "matching; EXIF metadata altered or rewritten; optical and digital chain "
     "not documentable; target doubtful; observation position uncertified",
     "le dossier est &#233;cart&#233; sans examen et sans analyse",
     "the file is set aside without examination and without analysis"),
    ("Non concluant", "Inconclusive",
     "un &#233;l&#233;ment manque dans la cha&#238;ne de "
     "tra&#231;abilit&#233;&#160;; ou la caract&#233;ristique &#224; mesurer "
     "n'est pas r&#233;solue au sens de 1.5.3&#160;; ou elle se trouve dans "
     "une zone reconstruite par l'appareil au sens de 1.4.6",
     "an element is missing from the traceability chain; or the feature to be "
     "measured is not resolved within the meaning of 1.5.3; or it lies in an "
     "area reconstructed by the camera within the meaning of 1.4.6",
     "l'analyse s'arr&#234;te pour cette caract&#233;ristique&#160;; le "
     "rapport nomme ce qui manque et ce qu'il faudrait pour l'&#233;tablir",
     "the analysis stops for that feature; the report names what is missing "
     "and what would be needed to establish it"),
    ("Analyse valide", "Valid analysis",
     "100&#8239;% des pi&#232;ces et des sources ind&#233;pendantes requises "
     "sont fournies et authentifi&#233;es, et la caract&#233;ristique &#224; "
     "mesurer est r&#233;solue",
     "100&#8239;% of the required evidence and independent sources are "
     "supplied and authenticated, and the feature to be measured is resolved",
     "l'analyse est conduite et conclut&#160;: compatible ou incompatible",
     "the analysis is carried out and concludes: compatible or incompatible"),
]

CONTROLES = [
    ("Le fichier remis est le fichier d'origine&#160;: l'empreinte SHA-256 "
     "recalcul&#233;e concorde avec celle qui est d&#233;clar&#233;e.",
     "The submitted file is the original: the recomputed SHA-256 digest "
     "matches the declared one."),
    ("Les m&#233;tadonn&#233;es EXIF sont celles de l'appareil et n'ont pas "
     "&#233;t&#233; r&#233;&#233;crites.",
     "The EXIF metadata are the camera's and have not been rewritten."),
    ("La cha&#238;ne du tableau&#160;2 est reconstituable de la sc&#232;ne au "
     "fichier&#160;: chaque poste est renseign&#233; ou d&#233;clar&#233; "
     "indisponible, et la part optique du grossissement est s&#233;par&#233;e "
     "de sa part num&#233;rique.",
     "The chain of table&#160;2 can be reconstructed from scene to file: every "
     "stage is filled in or declared unavailable, and the optical share of the "
     "magnification is separated from its digital share."),
    ("La caract&#233;ristique que l'on veut mesurer est effectivement "
     "r&#233;solue, v&#233;rifi&#233;e sur un bord franc de dimension connue "
     "selon 1.5.3.",
     "The feature to be measured is actually resolved, checked against a sharp "
     "edge of known dimension per 1.5.3."),
    ("La zone mesur&#233;e ne provient pas d'un traitement reconstruisant de "
     "l'information non enregistr&#233;e.",
     "The measured area does not come from a process reconstructing "
     "information that was never recorded."),
    ("La cible est identifi&#233;e par recoupement avec une source "
     "ext&#233;rieure, et non par ressemblance.",
     "The target is identified by cross-check against an outside source, not "
     "by resemblance."),
    ("Les dimensions de la cible proviennent d'une source ind&#233;pendante, "
     "dat&#233;e et citable.",
     "The target's dimensions come from an independent, dated and citable "
     "source."),
    ("La position de l'observateur est certifi&#233;e par le relev&#233; "
     "satellitaire et confirm&#233;e par la vue grand-angle.",
     "The observer's position is certified by the satellite reading and "
     "confirmed by the wide-angle frame."),
    ("Chaque donn&#233;e du dossier porte sa source, sa date et son "
     "incertitude.",
     "Every datum in the file carries its source, its date and its "
     "uncertainty."),
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

    t_verdicts = tab(
        ("Tableau&#160;4 &#8212; bar&#232;me de d&#233;cision. Les trois "
         "verdicts sont exclusifs et il n'en existe pas d'autre."
         if fr else
         "Table&#160;4 &#8212; decision scale. The three verdicts are mutually "
         "exclusive and there is no fourth."),
        (["Verdict", "Condition", "Cons&#233;quence"] if fr
         else ["Verdict", "Condition", "Consequence"]),
        [rang(["<strong>%s</strong>" % v[0 if fr else 1],
               v[2 if fr else 3], v[4 if fr else 5]],
              vedette=(i == 2)) for i, v in enumerate(VERDICTS)])

    ctrl = "\n".join("  <li>%s</li>" % c[0 if fr else 1] for c in CONTROLES)

    if fr:
        return "\n".join([
            partie("2", "Grille d'&#233;valuation", saut=True),
            clause("2.1", "La pr&#233;sente partie &#233;nonce ce que le "
                   "demandeur fournit, ce qui est v&#233;rifi&#233; et &#224; "
                   "quelle condition une conclusion est rendue. Elle s'adresse "
                   "&#224; l'analyste. Elle s'applique &#224; tout clich&#233; "
                   "soumis, y compris pris sans intention de mesure."),
            clause("2.2", "Le crit&#232;re d'acceptation n'est pas "
                   "&#171;&#160;grossissement autoris&#233; ou "
                   "interdit&#160;&#187;. Il est&#160;: l'information "
                   "photographique est-elle assez document&#233;e et assez "
                   "exploitable pour permettre une mesure fiable&#160;?"),
            sous("2.3 Pi&#232;ces exig&#233;es"),
            clause("2.3.1", "Le demandeur fournit les quatre pi&#232;ces du "
                   "tableau&#160;3. Une pi&#232;ce absente n'est jamais "
                   "suppl&#233;&#233;e par une estimation, une reconstitution "
                   "ou une valeur de r&#233;f&#233;rence."),
            t_pieces,
            clause("2.3.2", "Chaque source produite est dat&#233;e et citable. "
                   "Une source sans date n'est pas admise."),
            clause("2.3.3", "Aucune dimension, aucune distance et aucune "
                   "position n'est &#233;tablie &#224; partir de la "
                   "photographie soumise."),
            sous("2.4 Contr&#244;les"),
            clause("2.4.1", "Les contr&#244;les suivants sont conduits dans "
                   "l'ordre, avant toute analyse. Le premier qui &#233;choue "
                   "arr&#234;te la proc&#233;dure et fixe le verdict."),
            "<ul>\n%s\n</ul>" % ctrl,
            sous("2.5 Bar&#232;me de d&#233;cision"),
            t_verdicts,
            clause("2.5.1", "Une information manquante et une information "
                   "insuffisante ne conduisent pas au m&#234;me verdict. La "
                   "cha&#238;ne non documentable fait rejeter le "
                   "dossier&#160;; la cha&#238;ne document&#233;e mais trop "
                   "grossi&#232;re le rend non concluant pour la "
                   "caract&#233;ristique vis&#233;e."),
            clause("2.5.2", "Le verdict porte sur une caract&#233;ristique "
                   "d&#233;sign&#233;e, non sur le clich&#233; en bloc. Un "
                   "m&#234;me clich&#233; peut &#234;tre concluant pour une "
                   "caract&#233;ristique large et non concluant pour une "
                   "caract&#233;ristique fine."),
            clause("2.5.3", "Aucune valeur n'est ajust&#233;e apr&#232;s examen "
                   "pour faire correspondre le r&#233;sultat &#224; l'image. "
                   "Une correction n'est admise que si elle provient d'une "
                   "source ind&#233;pendante nouvelle, et le rapport indique la "
                   "valeur ant&#233;rieure, la valeur retenue et la source qui "
                   "a tranch&#233;."),
            clause("2.5.4", "Un dossier compl&#233;t&#233; plus tard est "
                   "r&#233;examin&#233; sans que la photographie soit "
                   "reprise&#160;: la prise de vue n'est jamais &#224; "
                   "refaire."),
            clause("2.5.5", "Le verdict <em>non concluant</em> n'est ni "
                   "favorable ni d&#233;favorable. Il n'est jamais "
                   "pr&#233;sent&#233; comme un r&#233;sultat."),
            sous("2.6 Rapport"),
            clause("2.6.1", "Le rapport &#233;nonce le verdict et la "
                   "caract&#233;ristique sur laquelle il porte, la liste des "
                   "pi&#232;ces re&#231;ues avec leur source et leur date, la "
                   "cha&#238;ne du tableau&#160;2 telle que reconstitu&#233;e, "
                   "l'empreinte SHA-256 du fichier d'origine, et le "
                   "contr&#244;le de 2.4 qui a &#233;chou&#233; le cas "
                   "&#233;ch&#233;ant."),
            clause("2.6.2", "Le rapport est publi&#233; avec le fichier "
                   "d'origine ou, si celui-ci ne peut &#234;tre diffus&#233;, "
                   "avec son empreinte et l'indication de qui le "
                   "d&#233;tient."),
            encadre("R&#232;gle sans exception",
                    "<p>Une pi&#232;ce manquante ne se remplace pas. Un "
                    "dossier incomplet ne devient pas concluant parce que "
                    "l'image est frappante, parce que le demandeur est de "
                    "bonne foi, ou parce que le r&#233;sultat attendu "
                    "arrangerait.</p>"),
        ])

    return "\n".join([
        partie("2", "Assessment grid", saut=True),
        clause("2.1", "This part states what the submitter supplies, what is "
               "checked, and under what condition a conclusion is issued. It "
               "addresses the analyst. It applies to any frame submitted, "
               "including one taken with no measurement in mind."),
        clause("2.2", "The acceptance criterion is not &#8220;magnification "
               "permitted or forbidden&#8221;. It is: is the photographic "
               "information documented enough and usable enough to support a "
               "reliable measurement?"),
        sous("2.3 Required evidence"),
        clause("2.3.1", "The submitter supplies the four items of "
               "table&#160;3. A missing item is never made good by an "
               "estimate, a reconstruction or a reference value."),
        t_pieces,
        clause("2.3.2", "Every source produced is dated and citable. An "
               "undated source is not admissible."),
        clause("2.3.3", "No dimension, no distance and no position is "
               "established from the submitted photograph."),
        sous("2.4 Checks"),
        clause("2.4.1", "The following checks are carried out in order, before "
               "any analysis. The first that fails stops the procedure and "
               "fixes the verdict."),
        "<ul>\n%s\n</ul>" % ctrl,
        sous("2.5 Decision scale"),
        t_verdicts,
        clause("2.5.1", "Missing information and insufficient information do "
               "not lead to the same verdict. An undocumentable chain has the "
               "file rejected; a documented but too coarse chain makes it "
               "inconclusive for the intended feature."),
        clause("2.5.2", "The verdict bears on a designated feature, not on the "
               "frame as a whole. One and the same frame may be conclusive for "
               "a coarse feature and inconclusive for a fine one."),
        clause("2.5.3", "No value is adjusted after examination to make the "
               "result match the image. A correction is admissible only if it "
               "comes from a new independent source, and the report states the "
               "previous value, the adopted value and the source that settled "
               "it."),
        clause("2.5.4", "A file completed later is re-examined without the "
               "photograph being retaken: the capture is never to be done "
               "again."),
        clause("2.5.5", "The <em>inconclusive</em> verdict is neither "
               "favourable nor unfavourable. It is never presented as a "
               "result."),
        sous("2.6 Report"),
        clause("2.6.1", "The report states the verdict and the feature it "
               "bears on, the list of items received with their source and "
               "date, the chain of table&#160;2 as reconstructed, the SHA-256 "
               "digest of the original file, and which check of 2.4 failed, "
               "where one did."),
        clause("2.6.2", "The report is published with the original file or, if "
               "that file cannot be circulated, with its digest and a "
               "statement of who holds it."),
        encadre("Rule without exception",
                "<p>A missing item is not replaced. An incomplete file does not "
                "become conclusive because the image is striking, because the "
                "submitter is in good faith, or because the expected result "
                "would suit.</p>"),
    ])


def corps(fr):
    resume = (
        '<div class="abstract"><span class="lab">%s</span>%s</div>' % (
            "Objet" if fr else "Purpose",
            ("<p>Deux parties. La premi&#232;re dit comment prendre une "
             "photographie qui ne sera pas &#233;cart&#233;e d'entr&#233;e. La "
             "seconde dit ce qu'il faut fournir avec elle, ce qui est "
             "v&#233;rifi&#233;, et &#224; quelle condition une conclusion est "
             "rendue.</p>"
             "<p>Un fort grossissement est autoris&#233;, y compris "
             "num&#233;rique. Ce qui est exig&#233; n'est pas de s'en priver, "
             "mais de documenter exactement ce que l'appareil a fait entre la "
             "sc&#232;ne et le fichier.</p>"
             "<p>Le document ne d&#233;crit aucun calcul. Il fixe les "
             "conditions dans lesquelles un calcul a le droit d'&#234;tre "
             "fait.</p>")
            if fr else
            ("<p>Two parts. The first states how to take a photograph that "
             "will not be set aside at the outset. The second states what must "
             "be supplied with it, what is checked, and under what condition a "
             "conclusion is issued.</p>"
             "<p>Strong magnification is permitted, digital magnification "
             "included. What is required is not to do without it, but to "
             "document exactly what the camera did between the scene and the "
             "file.</p>"
             "<p>The document describes no computation. It fixes the "
             "conditions under which a computation is entitled to be "
             "made.</p>")))
    return "\n\n".join([masthead(fr), resume, bloc_1(fr), bloc_2(fr)])


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
