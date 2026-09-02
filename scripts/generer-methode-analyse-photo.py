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

La grille des focales
─────────────────────
Elle repose sur un seul critère, énoncé en 1.4.1 : l'échelle au sol à la
distance de la cible ne dépasse pas un mètre par pixel, pour un capteur d'au
moins 6 000 pixels sur le grand côté. Sur une image 24×36 de largeur 36 mm, cela
donne une focale équivalente minimale de six millimètres par kilomètre de
distance — 120 mm à 20 km, 4 200 mm à 700 km. Les valeurs du tableau sont
recalculées par focale_mini() et vérifiées par controle() ; elles ne sont pas
écrites en dur dans le texte.

Aucune marque et aucun modèle n'est cité, nulle part.
"""
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
CIBLE = os.path.join(PROTOCOLES, "analyse-photo-bilingue.html")
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

LARGEUR_IMAGE = 36.0        # mm — grand côté du format 24×36
PIXELS = 6000               # pixels sur le grand côté
ECHELLE_MAX = 1.0           # m par pixel à la distance de la cible
DISTANCES = [20, 50, 100, 300, 700]   # km


def focale_mini(d_km):
    """Focale équivalente minimale, en mm, pour tenir l'échelle de 1.4.1."""
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
    # kilomètre. Si le critère de 1.4.1 change, elle reste proportionnelle.
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
                    % (c, "2.0" if c == "Version" else "&nbsp;") for c in champs)
    return ('<div class="masthead">\n  <div class="kicker">%s</div>\n'
            '  <h1>%s</h1>\n  <p class="dek">%s</p>\n'
            '  <div class="byline">\n    %s\n  </div>\n</div>'
            % (kicker, titre, sous_titre, cases))


# Le corps ne contient que des exigences. Ces tournures y signalent une
# digression, et le document est refusé plutôt qu'écrit.
DIGRESSION = [
    r"coefficient de r[ée]fraction", r"refraction coefficient",
    r"courbure", r"curvature", r"hauteur masqu", r"hidden height",
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
            raise SystemExit("digression th&#233;orique : %r"
                             % doc[max(0, m.start() - 70):m.end() + 40])
    open(CIBLE, "w", encoding="utf-8").write(doc)
    return doc


# ─────────────────────────────────────────────────────────────────────────────
# Partie 1 — prise de vue et matériel
# ─────────────────────────────────────────────────────────────────────────────
def bloc_1(fr):
    t_focales = tab(
        ("Tableau&#160;1 &#8212; focale &#233;quivalente minimale. En "
         "de&#231;&#224; de ces valeurs, le clich&#233; est &#233;cart&#233; "
         "sans examen."
         if fr else
         "Table&#160;1 &#8212; minimum equivalent focal length. Below these "
         "values the frame is rejected without examination."),
        (["Distance de vis&#233;e", "Focale &#233;quivalente minimale"] if fr
         else ["Sighting distance", "Minimum equivalent focal length"]),
        [rang(["%s&#8239;km" % nb(d, fr),
               "%s&#8239;mm" % nb(focale_mini(d), fr)], num=(0, 1))
         for d in DISTANCES], num=(0, 1))

    if fr:
        return "\n".join([
            partie("1", "Prise de vue et mat&#233;riel"),
            clause("1.1", "La pr&#233;sente partie &#233;nonce les conditions "
                   "dans lesquelles une photographie d'objet &#233;loign&#233; "
                   "est prise pour &#234;tre recevable. Elle s'adresse &#224; "
                   "l'op&#233;rateur. Le non-respect d'une seule de ces "
                   "conditions entra&#238;ne le rejet pr&#233;vu en 2.4."),
            sous("1.2 Enregistrement"),
            clause("1.2.1", "L'enregistrement se fait en format brut. Le "
                   "fichier brut d'origine est conserv&#233; tel qu'il sort de "
                   "l'appareil."),
            clause("1.2.2", "Aucune retouche, aucun recadrage, aucun "
                   "r&#233;&#233;chantillonnage, aucune conversion, aucune "
                   "correction de perspective ni de distorsion n'est "
                   "appliqu&#233;e au fichier d'origine."),
            clause("1.2.3", "Si l'appareil produit &#233;galement un fichier "
                   "compress&#233;, les deux sont conserv&#233;s et remis "
                   "ensemble."),
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
                   "&#224; la mise au point ni au cadrage entre les vues. "
                   "Toutes sont remises&#160;; aucune n'est &#233;cart&#233;e "
                   "par l'op&#233;rateur."),
            sous("1.4 Focale"),
            clause("1.4.1", "La focale &#233;quivalente employ&#233;e est telle "
                   "que l'&#233;chelle au sol &#224; la distance de la cible "
                   "n'exc&#232;de pas un m&#232;tre par pixel, pour un capteur "
                   "d'au moins %s pixels sur le grand c&#244;t&#233;. Le "
                   "tableau&#160;1 donne les valeurs correspondantes."
                   % nb(PIXELS, fr)),
            t_focales,
            clause("1.4.2", "La focale est une focale optique r&#233;elle. Un "
                   "agrandissement num&#233;rique, quel que soit son nom "
                   "commercial, ne compte pas et rend le clich&#233; "
                   "irrecevable."),
            clause("1.4.3", "La focale r&#233;elle, l'ouverture, le temps de "
                   "pose et la sensibilit&#233; doivent figurer dans les "
                   "m&#233;tadonn&#233;es. Une focale non v&#233;rifiable "
                   "entra&#238;ne le rejet pr&#233;vu en 2.4."),
            sous("1.5 R&#232;gles d'admissibilit&#233; de la prise de vue"),
            clause("1.5.1", "Les m&#233;tadonn&#233;es EXIF brutes sont "
                   "conserv&#233;es intactes. Aucun champ n'est effac&#233;, "
                   "&#233;cras&#233; ni r&#233;&#233;crit, y compris par un "
                   "outil de transfert, une sauvegarde automatique ou un "
                   "envoi par messagerie."),
            clause("1.5.2", "L'horloge de l'appareil est r&#233;gl&#233;e sur "
                   "le temps universel avant la prise de vue. La position "
                   "satellitaire est enregistr&#233;e avec l'image."),
            clause("1.5.3", "La cible est parfaitement identifiable. Le champ "
                   "contient au moins deux &#233;l&#233;ments de "
                   "r&#233;f&#233;rence dont les dimensions r&#233;elles sont "
                   "&#233;tablies par une source ext&#233;rieure&#160;: "
                   "ouvrage r&#233;pertori&#233;, structure cot&#233;e, point "
                   "g&#233;od&#233;sique."),
            clause("1.5.4", "Une vue grand-angle du point de vue est "
                   "prise depuis la m&#234;me position, montrant les "
                   "rep&#232;res proches. Elle est remise avec la "
                   "s&#233;rie."),
            clause("1.5.5", "L'empreinte SHA-256 de chaque fichier d'origine "
                   "est calcul&#233;e d&#232;s le transfert, avant toute autre "
                   "op&#233;ration, et consign&#233;e avec la date du calcul."),
            clause("1.5.6", "La position satellitaire du point de vue est "
                   "relev&#233;e et consign&#233;e s&#233;par&#233;ment, avec "
                   "l'incertitude annonc&#233;e par le r&#233;cepteur."),
            encadre("&#192; ne jamais faire",
                    "<p>Ne pas trier les vues, ne pas &#171;&#160;am&#233;"
                    "liorer&#160;&#187; l'image, ne pas la recadrer pour "
                    "mieux montrer la cible, ne pas la r&#233;exporter, ne pas "
                    "l'envoyer par un service qui recompresse. Chacune de ces "
                    "op&#233;rations d&#233;truit le fichier comme "
                    "pi&#232;ce.</p>"),
        ])

    return "\n".join([
        partie("1", "Image capture and equipment"),
        clause("1.1", "This part states the conditions under which a "
               "photograph of a distant object is taken in order to be "
               "admissible. It addresses the operator. Failure to meet any one "
               "of these conditions results in the rejection set out in 2.4."),
        sous("1.2 Recording"),
        clause("1.2.1", "Recording is in raw format. The original raw file is "
               "kept exactly as it comes out of the camera."),
        clause("1.2.2", "No retouching, no cropping, no resampling, no "
               "conversion, no perspective or distortion correction is applied "
               "to the original file."),
        clause("1.2.3", "If the camera also produces a compressed file, both "
               "are kept and submitted together."),
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
               "sighting are recorded, without touching focus or framing "
               "between frames. All are submitted; none is discarded by the "
               "operator."),
        sous("1.4 Focal length"),
        clause("1.4.1", "The equivalent focal length used shall be such that "
               "the ground scale at the target's distance does not exceed one "
               "metre per pixel, for a sensor of at least %s pixels on the long "
               "side. Table&#160;1 gives the corresponding values."
               % nb(PIXELS, fr)),
        t_focales,
        clause("1.4.2", "The focal length is a real optical focal length. "
               "Digital magnification, whatever its trade name, does not count "
               "and renders the frame inadmissible."),
        clause("1.4.3", "The actual focal length, aperture, shutter speed and "
               "sensitivity shall appear in the metadata. An unverifiable focal "
               "length results in the rejection set out in 2.4."),
        sous("1.5 Admissibility rules for the capture"),
        clause("1.5.1", "The raw EXIF metadata are kept intact. No field is "
               "erased, overwritten or rewritten, including by a transfer "
               "utility, an automatic backup or a messaging application."),
        clause("1.5.2", "The camera clock is set to universal time before the "
               "capture. The satellite position is recorded with the image."),
        clause("1.5.3", "The target is unmistakably identifiable. The field "
               "contains at least two reference elements whose real dimensions "
               "are established by an outside source: a listed structure, a "
               "dimensioned works, a geodetic point."),
        clause("1.5.4", "A wide-angle frame of the viewpoint is taken from the "
               "same position, showing the near landmarks. It is submitted "
               "with the series."),
        clause("1.5.5", "The SHA-256 digest of each original file is computed "
               "at transfer, before any other operation, and recorded with the "
               "date of computation."),
        clause("1.5.6", "The satellite position of the viewpoint is read and "
               "recorded separately, together with the uncertainty stated by "
               "the receiver."),
        encadre("Never do this",
                "<p>Do not sort the frames, do not &#8220;improve&#8221; the "
                "image, do not crop it to show the target better, do not "
                "re-export it, do not send it through a service that "
                "recompresses. Each of these operations destroys the file as "
                "evidence.</p>"),
    ])


# ─────────────────────────────────────────────────────────────────────────────
# Partie 2 — pièces exigées et barème
# ─────────────────────────────────────────────────────────────────────────────
PIECES = [
    ("Fichier brut d'origine",
     "Original raw file",
     "le fichier tel qu'il sort de l'appareil, avec ses "
     "m&#233;tadonn&#233;es EXIF intactes, accompagn&#233; de son empreinte "
     "SHA-256 et de la date de calcul de celle-ci",
     "the file exactly as it comes out of the camera, with its EXIF metadata "
     "intact, together with its SHA-256 digest and the date that digest was "
     "computed"),
    ("Position de l'observateur",
     "Observer position",
     "coordonn&#233;es satellitaires du point de vue, avec l'incertitude "
     "annonc&#233;e par le r&#233;cepteur, et la vue grand-angle "
     "montrant les rep&#232;res proches",
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
     "fichier brut manquant ou modifi&#233;&#160;; empreinte SHA-256 absente "
     "ou non concordante&#160;; m&#233;tadonn&#233;es EXIF alt&#233;r&#233;es "
     "ou r&#233;&#233;crites&#160;; focale non v&#233;rifiable ou "
     "inf&#233;rieure au tableau&#160;1&#160;; cible douteuse&#160;; position "
     "d'observation non certifi&#233;e",
     "raw file missing or modified; SHA-256 digest absent or not matching; "
     "EXIF metadata altered or rewritten; focal length unverifiable or below "
     "table&#160;1; target doubtful; observation position uncertified",
     "le dossier est &#233;cart&#233; sans examen et sans analyse",
     "the file is set aside without examination and without analysis"),
    ("Non concluant", "Inconclusive",
     "toutes les pi&#232;ces du tableau&#160;2 sont pr&#233;sentes et "
     "authentifi&#233;es, mais un &#233;l&#233;ment manque dans la "
     "cha&#238;ne de tra&#231;abilit&#233; des donn&#233;es fournies",
     "every item of table&#160;2 is present and authenticated, but one element "
     "is missing from the traceability chain of the data supplied",
     "l'analyse s'arr&#234;te&#160;; le rapport nomme l'&#233;l&#233;ment "
     "manquant et ce qu'il faudrait pour l'&#233;tablir",
     "the analysis stops; the report names the missing element and what would "
     "be needed to establish it"),
    ("Analyse valide", "Valid analysis",
     "100&#8239;% des pi&#232;ces et des sources ind&#233;pendantes "
     "requises sont fournies et authentifi&#233;es",
     "100&#8239;% of the required evidence and independent sources are "
     "supplied and authenticated",
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
    ("La focale r&#233;elle est lisible dans les m&#233;tadonn&#233;es et "
     "atteint la valeur du tableau&#160;1 pour la distance "
     "d&#233;clar&#233;e.",
     "The actual focal length is readable in the metadata and meets the "
     "table&#160;1 value for the declared distance."),
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
        ("Tableau&#160;2 &#8212; pi&#232;ces &#224; fournir. La liste est "
         "exhaustive et aucune pi&#232;ce n'est facultative."
         if fr else
         "Table&#160;2 &#8212; evidence to be supplied. The list is exhaustive "
         "and no item is optional."),
        (["N&#176;", "Pi&#232;ce", "Forme admise"] if fr
         else ["No.", "Item", "Admissible form"]),
        [rang(["%02d" % (i + 1), p[0 if fr else 1], p[2 if fr else 3]],
              num=(0,)) for i, p in enumerate(PIECES)], num=(0,))

    t_verdicts = tab(
        ("Tableau&#160;3 &#8212; bar&#232;me de d&#233;cision. Les trois "
         "verdicts sont exclusifs et il n'en existe pas d'autre."
         if fr else
         "Table&#160;3 &#8212; decision scale. The three verdicts are mutually "
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
                   "quelle condition une conclusion est rendue. Elle "
                   "s'adresse &#224; l'analyste. Elle s'applique &#224; tout "
                   "clich&#233; soumis, y compris pris sans intention de "
                   "mesure, d&#232;s lors que la partie&#160;1 est "
                   "satisfaite."),
            sous("2.2 Pi&#232;ces exig&#233;es"),
            clause("2.2.1", "Le demandeur fournit les trois pi&#232;ces du "
                   "tableau&#160;2. Une pi&#232;ce absente n'est jamais "
                   "suppl&#233;&#233;e par une estimation, une reconstitution "
                   "ou une valeur de r&#233;f&#233;rence."),
            t_pieces,
            clause("2.2.2", "Chaque source produite est dat&#233;e et "
                   "citable. Une source sans date n'est pas admise."),
            clause("2.2.3", "Aucune dimension, aucune distance et aucune "
                   "position n'est &#233;tablie &#224; partir de la "
                   "photographie soumise."),
            sous("2.3 Contr&#244;les"),
            clause("2.3.1", "Les contr&#244;les suivants sont conduits dans "
                   "l'ordre, avant toute analyse. Le premier qui &#233;choue "
                   "arr&#234;te la proc&#233;dure et fixe le verdict."),
            "<ul>\n%s\n</ul>" % ctrl,
            sous("2.4 Bar&#232;me de d&#233;cision"),
            t_verdicts,
            clause("2.4.1", "Aucune valeur n'est ajust&#233;e apr&#232;s "
                   "examen pour faire correspondre le r&#233;sultat &#224; "
                   "l'image. Une correction n'est admise que si elle provient "
                   "d'une source ind&#233;pendante nouvelle, et le rapport "
                   "indique la valeur ant&#233;rieure, la valeur retenue et la "
                   "source qui a tranch&#233;."),
            clause("2.4.2", "Un dossier compl&#233;t&#233; plus tard est "
                   "r&#233;examin&#233; sans que la photographie soit "
                   "reprise&#160;: la prise de vue n'est jamais &#224; "
                   "refaire."),
            clause("2.4.3", "Le verdict <em>non concluant</em> n'est ni "
                   "favorable ni d&#233;favorable. Il n'est jamais "
                   "pr&#233;sent&#233; comme un r&#233;sultat."),
            sous("2.5 Rapport"),
            clause("2.5.1", "Le rapport &#233;nonce le verdict, la liste des "
                   "pi&#232;ces re&#231;ues avec leur source et leur date, "
                   "l'empreinte SHA-256 du fichier d'origine, et le "
                   "contr&#244;le de 2.3 qui a &#233;chou&#233; le cas "
                   "&#233;ch&#233;ant."),
            clause("2.5.2", "Le rapport est publi&#233; avec le fichier "
                   "d'origine ou, si celui-ci ne peut &#234;tre "
                   "diffus&#233;, avec son empreinte et l'indication de qui le "
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
               "including one taken with no measurement in mind, provided "
               "part&#160;1 is satisfied."),
        sous("2.2 Required evidence"),
        clause("2.2.1", "The submitter supplies the three items of "
               "table&#160;2. A missing item is never made good by an "
               "estimate, a reconstruction or a reference value."),
        t_pieces,
        clause("2.2.2", "Every source produced is dated and citable. An "
               "undated source is not admissible."),
        clause("2.2.3", "No dimension, no distance and no position is "
               "established from the submitted photograph."),
        sous("2.3 Checks"),
        clause("2.3.1", "The following checks are carried out in order, before "
               "any analysis. The first that fails stops the procedure and "
               "fixes the verdict."),
        "<ul>\n%s\n</ul>" % ctrl,
        sous("2.4 Decision scale"),
        t_verdicts,
        clause("2.4.1", "No value is adjusted after examination to make the "
               "result match the image. A correction is admissible only if it "
               "comes from a new independent source, and the report states the "
               "previous value, the adopted value and the source that settled "
               "it."),
        clause("2.4.2", "A file completed later is re-examined without the "
               "photograph being retaken: the capture is never to be done "
               "again."),
        clause("2.4.3", "The <em>inconclusive</em> verdict is neither "
               "favourable nor unfavourable. It is never presented as a "
               "result."),
        sous("2.5 Report"),
        clause("2.5.1", "The report states the verdict, the list of items "
               "received with their source and date, the SHA-256 digest of the "
               "original file, and which check of 2.3 failed, where one did."),
        clause("2.5.2", "The report is published with the original file or, if "
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
             "photographie qui ne sera pas &#233;cart&#233;e d'entr&#233;e. "
             "La seconde dit ce qu'il faut fournir avec elle, ce qui est "
             "v&#233;rifi&#233;, et &#224; quelle condition une conclusion "
             "est rendue.</p>"
             "<p>Le document ne d&#233;crit aucun calcul. Il fixe les "
             "conditions dans lesquelles un calcul a le droit d'&#234;tre "
             "fait.</p>")
            if fr else
            ("<p>Two parts. The first states how to take a photograph that "
             "will not be set aside at the outset. The second states what must "
             "be supplied with it, what is checked, and under what condition a "
             "conclusion is issued.</p>"
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
