#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Squelette commun des méthodes d'essai du site.

Toutes nos méthodes suivent désormais l'ordre de sections qu'imposent les normes
d'essai — celui de la *standard test method* de l'ASTM, repris par la plupart
des agences :

    1  Domaine d'application       Scope
    2  Documents de référence      Referenced documents
    3  Terminologie                Terminology
    4  Résumé de la méthode        Summary of method
    5  Intérêt et emploi           Significance and use
    6  Appareillage                Apparatus
    7  Conditions d'essai          Test conditions
    8  Mode opératoire             Procedure
    9  Calcul                      Calculation
    10 Rapport d'essai             Report
    11 Fidélité et biais           Precision and bias
    X1 Annexe non normative        Non-mandatory appendix

La règle structurante, et la raison d'être de ce module : **le corps ne contient
que des exigences.** Le raisonnement, la justification, l'histoire d'une valeur
et la réponse aux objections vont en annexe X1, qui s'ouvre sur la mention
« les informations de la présente annexe ne constituent pas des exigences ».

Un corps rédigé au conditionnel, une justification glissée entre deux
prescriptions, un paragraphe qui raconte pourquoi on a changé d'avis : tout cela
appartient à l'annexe. C'est ce que nos protocoles mélangeaient.
"""
import os
import re

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROTOCOLES = os.path.join(RACINE, "content", "protocoles")
# Le gabarit typographique — feuille de style, polices, mise en page A4 — est
# repris d'un document existant plutôt que dupliqué. Il n'a pas à être réécrit
# pour chaque méthode.
GABARIT = os.path.join(PROTOCOLES, "visee-terrestre-bilingue.html")

TITRES = {
    1: ("Domaine d'application", "Scope"),
    2: ("Documents de r&#233;f&#233;rence", "Referenced documents"),
    3: ("Terminologie", "Terminology"),
    4: ("R&#233;sum&#233; de la m&#233;thode", "Summary of method"),
    5: ("Int&#233;r&#234;t et emploi", "Significance and use"),
    6: ("Appareillage", "Apparatus"),
    7: ("Conditions d'essai", "Test conditions"),
    8: ("Mode op&#233;ratoire", "Procedure"),
    9: ("Calcul", "Calculation"),
    10: ("Rapport d'essai", "Report"),
    11: ("Fid&#233;lit&#233; et biais", "Precision and bias"),
}
ANNEXE = ("Annexe non normative &#8212; d'o&#249; viennent ces exigences",
          "Non-mandatory appendix &#8212; where these requirements come from")
AVIS_ANNEXE = ("Les informations de la pr&#233;sente annexe ne constituent pas des "
               "exigences.",
               "The information in this appendix does not constitute requirements.")


def nb(x, n, fr):
    """Un nombre, avec la virgule décimale française si fr."""
    return ("%.*f" % (n, x)).replace(".", "," if fr else ".")


def mil(x, fr):
    """Un entier avec séparateur de milliers fin, dans les deux langues."""
    return "{:,.0f}".format(x).replace(",", "&#8239;")


def h2(numero, fr, saut=False):
    """Un titre de section, numéroté selon la table normalisée."""
    titre = TITRES[numero][0 if fr else 1]
    cls = ' class="brk"' if saut else ""
    return '<h2%s><span class="n">%d</span>%s</h2>' % (cls, numero, titre)


def h2_annexe(fr, saut=True):
    cls = ' class="brk"' if saut else ""
    return ('<h2%s><span class="n">X1</span>%s</h2>\n<p class="lead">%s</p>'
            % (cls, ANNEXE[0 if fr else 1], AVIS_ANNEXE[0 if fr else 1]))


def clause(numero, texte):
    """Une clause numérotée du corps. Une exigence, à l'impératif ou au présent."""
    return "<p>%s &#8212; %s</p>" % (numero, texte)


def tableau(legende, entetes, lignes):
    return ("<table>\n  <caption>%s</caption>\n  <thead><tr>%s</tr></thead>\n"
            "  <tbody>\n%s\n  </tbody>\n</table>"
            % (legende,
               "".join('<th class="n">%s</th>' % e for e in entetes),
               "\n".join(lignes)))


def ligne(cellules, vedette=False):
    g = (lambda s: "<strong>%s</strong>" % s) if vedette else (lambda s: s)
    return ('    <tr%s>%s</tr>'
            % (' class="hi"' if vedette else "",
               "".join('<td class="n">%s</td>' % g(c) for c in cellules)))


def encadre(etiquette, contenu, genre="warn"):
    return ('<div class="box %s">\n  <span class="lab">%s</span>\n%s\n</div>'
            % (genre, etiquette, contenu))


def masthead(fr, titre, sous_titre, version):
    kicker = ("M&#233;thode d'essai &#183; Structure normalis&#233;e &#183; "
              "Annexe non normative" if fr else
              "Test method &#183; Standard section order &#183; "
              "Non-mandatory appendix")
    champs = (("R&#233;dacteur", "Affiliation", "Contact", "Version", "Date") if fr
              else ("Author", "Affiliation", "Contact", "Version", "Date"))
    cases = "".join(
        "<span>%s<b>%s</b></span>" % (c, version if c == "Version" else "&nbsp;")
        for c in champs)
    return ('<div class="masthead">\n  <div class="kicker">%s</div>\n'
            '  <h1>%s</h1>\n  <p class="sub">%s</p>\n'
            '  <div class="byline">\n    %s\n  </div>\n</div>'
            % (kicker, titre, sous_titre, cases))


def ecrire(cible, titre_onglet, corps_fr, corps_en):
    """Assemble le document bilingue et l'écrit."""
    modele = open(GABARIT, encoding="utf-8").read()
    i = modele.find('<div class="page">')
    if i < 0:
        raise SystemExit("gabarit sans <div class=\"page\"> : %s" % GABARIT)
    entete = re.sub(r"<title>[^<]*</title>", "<title>%s</title>" % titre_onglet,
                    modele[:i], count=1)
    doc = (entete + '<div class="page">\n'
           '<div class="langbar"><span class="on">FRAN&#199;AIS</span>'
           '<span>ENGLISH &#8212; seconde moiti&#233;</span></div>\n\n'
           + corps_fr +
           '\n\n<div class="langbar"><span>FRAN&#199;AIS &#8212; first half</span>'
           '<span class="on">ENGLISH</span></div>\n\n'
           + corps_en + '\n</div>\n')
    verifier(doc)
    open(cible, "w", encoding="utf-8").write(doc)
    return doc


# Les tournures qui trahissent du récit dans le corps d'une méthode d'essai.
# Elles sont légitimes en annexe, jamais avant.
RECIT = [
    r"nous (?:avons|pensons|croyons|proposons|reprochons)",
    r"ajout[ée]? en 1\.", r"added in 1\.",
    r"[Cc]orrection apport", r"version pr[ée]c[ée]dente", r"previous version",
    r"c'est pourquoi nous",
    # Les guillemets ne sont pas un indice : la section 2 cite légitimement des
    # titres de documents. Un premier jet les traquait et refusait « Dépression
    # de l'horizon marin » en référence normative.
]


def verifier(doc):
    """Refuse un document dont le corps contient du récit.

    Le contrôle s'arrête au titre de l'annexe : au-delà, tout est permis.
    """
    for langue, debut in (("FR", doc.find('<div class="masthead">')),
                          ("EN", doc.rfind('<div class="masthead">'))):
        fin = doc.find('<span class="n">X1</span>', debut)
        if fin < 0:
            raise SystemExit("moitié %s sans annexe X1" % langue)
        corps = doc[debut:fin]
        for motif in RECIT:
            m = re.search(motif, corps)
            if m:
                raise SystemExit(
                    "récit dans le corps %s : %r\n  → cela va en annexe X1"
                    % (langue, corps[max(0, m.start() - 60):m.end() + 40]))
