#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Tri des faits établis par nature de la revendication.

Deux cent quarante encadrés ne s'examinent pas en bloc : ils ne se vérifient pas
tous de la même façon. Un chiffre de courbure se tranche au calcul, une citation
coranique en ouvrant le texte, une affirmation sur ce qu'a écrit Foucault en
1851 en consultant sa communication, et « la gravité n'a jamais été prouvée »
par l'examen de ce qu'on entend par prouver. Confondre ces quatre régimes, c'est
se condamner à ne rien conclure.

Ce script range chaque encadré dans l'un d'eux, d'après ce qu'il contient. Le
tri est grossier — il repose sur des marqueurs de surface — et il n'a pas
vocation à décider : il sert à constituer des piles de travail homogènes et à
dire, chiffres en main, quelle part du dossier relève de quel type de contrôle.

Les quatre régimes
──────────────────
  MÉTROLOGIQUE  une grandeur physique chiffrée, avec son unité. Se tranche au
                calcul, sans rien consulter. C'est la pile déjà entamée par
                verifier-encadres-empiriques.py.
  TEXTUEL       une citation, une référence de sourate, un nom de savant. Se
                tranche en ouvrant la source.
  HISTORIQUE    une date, un événement, une attribution. Se tranche en
                consultant une source primaire ou une édition critique.
  ARGUMENTATIF  une thèse sur la valeur d'une preuve, sur une méthode, sur ce
                qui a été supposé plutôt que montré. Ne se tranche pas par une
                consultation : elle s'examine.
  NARRATIF      une thèse sur des institutions, des motifs, un paradigme, un
                contexte culturel. Cette pile est apparue au deuxième passage :
                le premier tri la manquait entièrement et rangeait ses cent
                énoncés en « non classé ». Elle mérite d'être nommée, car elle
                pose une question que les autres ne posent pas — un énoncé de ce
                type peut être entièrement vrai sans rien établir de la figure
                de la Terre.

Un encadré peut porter plusieurs marqueurs ; il est alors rangé selon la
priorité MÉTROLOGIQUE > TEXTUEL > HISTORIQUE > ARGUMENTATIF > NARRATIF, parce
que c'est l'ordre de la difficulté croissante à conclure.

    python3 scripts/trier-faits-etablis.py           # synthèse
    python3 scripts/trier-faits-etablis.py --detail  # liste complète
"""

import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INVENTAIRE = os.path.join(RACINE, "content", "corrections", "faits-etablis.md")

# Unités physiques précédées d'un nombre. Le point délicat est « % » et « ° »,
# qui apparaissent aussi dans des tournures non métrologiques ; on exige donc
# un nombre collé devant.
UNITES = (r"\d[\d\s.,]*\s*(?:km|m|cm|mm|kg|g|s|h|min|°|′|″|%|hPa|Pa|W|K|"
          r"mètres?|kilomètres?|degrés?|minutes? d'arc|secondes? d'arc|"
          r"années?-lumière|UA|Hz|nm|µm)\b")

TEXTUEL = (r"\bS\d+\s*V\d+\b|sourate|hadith|Coran|coranique|Bukh[āa]r[īi]|"
           r"Muslim|[ṬT]abar[īi]|tafs[īi]r|Ibn Taymiyya|Ibn Kath[īi]r|"
           r"al-Qur[ṭt]ub[īi]|verset|ex[ée]g[èe]se|commentateur|traduction|"
           r"manuscrit|folio|Majm[ūu]|Ris[āa]la|ijm[āa]|oul[ée]mas?|Compagnons|"
           r"[ée]crit que|selon .{0,24}, la [Tt]erre")

HISTORIQUE = (r"\b1[0-9]\d\d\b|\b20[0-2]\d\b|\bX{1,3}[IVX]*[eè]\s*si[èe]cle|"
              r"Foucault|Airy|Michelson|Sagnac|[ÉE]ratosth[èe]ne|Halley|Maskelyne|"
              r"Copernic|Galil[ée]e|Newton|Einstein|Bradley|Arago|Hubble|Lorentz|"
              r"Rowbotham|Bourdaloue|Ptol[ée]m[ée]e|Philolaos|Nansen|Cook|"
              r"exp[ée]rience de|publi[ée]|rapport officiel|archives|"
              r"Babylone|[ÉE]gypte|Mayas|Azt[èe]ques|Incas|SRTM|LIGO|NASA|"
              r"fabriqu[ée]|premi[èe]re campagne|Institute")

ARGUMENTATIF = (r"n'a jamais [ée]t[ée]|aucune preuve|ne prouve|ne d[ée]montre|"
                r"n'est pas prouv|hypoth[èe]se|postulat|pr[ée]suppose|circulaire|"
                r"p[ée]tition de principe|interpr[ée]t|admis sans|par convention|"
                r"il n'existe aucun|jamais observ|jamais mesur|inv[ée]rifiable|"
                r"falsifiable|raisonnement|argument|ne distingue pas|"
                r"[ée]galement coh[ée]rent|coh[ée]rent avec|r[ée]futerait|"
                r"ind[ée]tectable|repose sur|ne permet pas de|"
                r"n'est pas une preuve|ne tranche pas|pr[ée]diction|"
                r"cha[îi]ne de maillons|d[ée]pendant|sans jamais poser|"
                r"invalide|n[ée]cessite plus de|correction consiste")

NARRATIF = (r"paradigme|instrument de|conviction|domination|culturel|religieux|"
            r"institution|financement|carri[èe]re|consensus|autorit[ée]|"
            r"a [ée]t[ée] charg[ée]|propagande|croyance|m[ée]taphysique|"
            r"doctorat|architectes|contexte|accept[ée] comme|"
            r"civilisations|sacr[ée]|prestige|pouvoir|[ÉE]glise|id[ée]ologi")

# ── Reclassements décidés à la lecture ──────────────────────────────────────
# Le tri de surface range dans MÉTROLOGIQUE tout énoncé portant un nombre suivi
# d'une unité. Une date en est une : « 1849 », « 1775 », « 60 Hz » suffisent à
# faire basculer un énoncé qui ne fait aucune affirmation physique. Ces huit-là
# ont été lus un par un et rangés à la main dans la pile qui les concerne.
# Un tri automatique qu'on ne corrige jamais finit par décider à notre place.
RECLASSEMENTS = {
    ("le-mouvement-zetetique-150-ans-de-resistance", 1): "HISTORIQUE",
    ("ligo-londe-qui-nexistait-pas", 2): "HISTORIQUE",
    ("ligo-londe-qui-nexistait-pas", 3): "ARGUMENTATIF",
    ("lire-le-ciel-avant-le-globe", 1): "HISTORIQUE",
    ("par-rapport-a-quoi-mesure-t-on-une-altitude", 2): "HISTORIQUE",
    ("par-rapport-a-quoi-mesure-t-on-une-altitude", 5): "HISTORIQUE",
    ("debut-de-la-creation-le-soleil-mobile-la-terre-immobile", 3): "TEXTUEL",
    ("monter-l-experience-des-trois-mires", 2): "ARGUMENTATIF",
}


def classer(txt, cle=None):
    if cle in RECLASSEMENTS:
        return RECLASSEMENTS[cle]
    for motif, nom, drapeaux in (
            (UNITES, "MÉTROLOGIQUE", 0),
            (TEXTUEL, "TEXTUEL", re.I),
            (HISTORIQUE, "HISTORIQUE", 0),
            (ARGUMENTATIF, "ARGUMENTATIF", re.I),
            (NARRATIF, "NARRATIF", re.I)):
        if re.search(motif, txt, drapeaux):
            return nom
    return "NON CLASSÉ"


ORDRE = ["MÉTROLOGIQUE", "TEXTUEL", "HISTORIQUE",
         "ARGUMENTATIF", "NARRATIF", "NON CLASSÉ"]


def relever():
    """Rend [(pilier, slug, n, énoncé, verdict)] dans l'ordre du fichier."""
    pilier = slug = None
    out = []
    for l in open(INVENTAIRE, encoding="utf-8"):
        m = re.match(r"## (.+?) — \d+ faits", l)
        if m:
            pilier = m.group(1)
            continue
        m = re.match(r"`([a-z0-9-]+)` — \d+ encadré", l)
        if m:
            slug = m.group(1)
            continue
        m = re.match(r"\|\s*(\d+)\s*\|(.*)\|(.*)\|\s*$", l)
        if m and slug:
            out.append((pilier, slug, int(m.group(1)),
                        m.group(2).strip(), m.group(3).strip()))
    return out


def main():
    detail = "--detail" in sys.argv
    lignes = relever()
    faits = [x for x in lignes if not x[4]]
    tranches = [x for x in lignes if x[4]]

    print("═" * 74)
    print("TRI DES FAITS ÉTABLIS PAR NATURE DE LA REVENDICATION")
    print("═" * 74)
    print("  %d encadrés relevés · %d déjà tranchés · %d à examiner"
          % (len(lignes), len(tranches), len(faits)))
    print()

    piliers = []
    for p, _, _, _, _ in lignes:
        if p not in piliers:
            piliers.append(p)

    grille = {p: {r: [] for r in ORDRE} for p in piliers}
    for p, slug, n, txt, _ in faits:
        grille[p][classer(txt, (slug, n))].append((slug, n, txt))

    entete = "  %-22s" + "%14s" * len(ORDRE)
    rang = "  %-22s" + "%14d" * len(ORDRE)
    print(entete % ("pilier", *ORDRE))
    print("  " + "─" * (22 + 14 * len(ORDRE)))
    for p in piliers:
        print(rang % (p, *[len(grille[p][r]) for r in ORDRE]))
    print("  " + "─" * (22 + 14 * len(ORDRE)))
    print(rang % ("TOTAL",
                  *[sum(len(grille[p][r]) for p in piliers) for r in ORDRE]))
    print()

    print("  Ce que chaque pile demande :")
    print("    MÉTROLOGIQUE   le calcul seul. Aucune consultation.")
    print("    TEXTUEL        ouvrir la source citée et lire ce qu'elle dit.")
    print("    HISTORIQUE     remonter à une source primaire ou une édition critique.")
    print("    ARGUMENTATIF   examiner le raisonnement ; rien à consulter, tout à peser.")
    print("    NARRATIF       porte sur des institutions ou des motifs, non sur la Terre.")
    print("    NON CLASSÉ     à lire à la main : le tri de surface n'a rien reconnu.")
    print()

    if detail:
        for p in piliers:
            for r in ORDRE:
                items = grille[p][r]
                if not items:
                    continue
                print()
                print("── %s · %s — %d" % (p, r, len(items)))
                for slug, n, txt in items:
                    print("   %s n°%d" % (slug, n))
                    print("      %s" % (txt[:150] + ("…" if len(txt) > 150 else "")))
    else:
        print("  (--detail pour la liste complète)")
    print("═" * 74)
    return 0


if __name__ == "__main__":
    sys.exit(main())
