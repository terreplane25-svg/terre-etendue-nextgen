#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Schemas de la Bibliotheque. Palette saffron du pilier.

Reutilise la classe Vue de generer-schemas-cote.py, avec son controle
automatique de debordement et de chevauchement des textes.
"""
import sys, os, importlib.util, math

spec = importlib.util.spec_from_file_location("cote", "scripts/generer-schemas-cote.py")
cote = importlib.util.module_from_spec(spec)
sys.argv = [sys.argv[0]]           # empeche le __main__ du module importe d'ecrire
spec.loader.exec_module(cote)

Vue, INK, MUT, GRID, BG = cote.Vue, cote.INK, cote.MUT, cote.GRID, cote.BG
SAF, LV, CY, RO, OP = cote.GO, cote.LV, cote.CY, cote.RO, cote.OP
SAFFRON = "#D4943A"


def chaine_de_transmission():
    """Deux chaines paralleles qui ne se rejoignent jamais."""
    W, H = 1060, 880
    v = Vue(W, H,
            "D'OÙ VIENT LE « CONSENSUS » — DEUX CHAÎNES QUI NE SE CROISENT PAS",
            "À gauche, la transmission astronomique. À droite, les savants de la Loi. Aucun lien entre les deux.",
            "Chaine de transmission du consensus sur la sphericite", SAFFRON)

    XG, XD = 250, 790                 # colonnes gauche et droite
    v.txt(XG, 104, "AHL AL-HAY'A — les astronomes", CY, 12.5, "700", "middle")
    v.txt(XD, 104, "'ULAMA' AL-SHAR' — les savants de la Loi", SAFFRON, 12.5, "700", "middle")
    v.line(520, 118, 520, H - 96, GRID, 1, "6 5")

    GAUCHE = [
      ("Ptolémée — Almageste", "IIᵉ siècle, grec", None),
      ("traduction arabe", "IXᵉ siècle", None),
      ("al-Kindī", "185-256 H · « philosophe des Arabes »", None),
      ("al-Farghānī", "† ~247 H · astronome", "aucune formation religieuse · Kitāb fī Jawāmiʿ ʿIlm al-Nujūm"),
      ("Ibn Khurdādhbih", "† 280 H · géographe", None),
      ("Ibn Rustah", "† ~300 H · géographe d'Ispahan", "al-Aʿlāq al-Nafīsa, p. 9"),
      ("al-Masʿūdī", "† 346 H · historien", "Murūj al-Dhahab"),
      ("Ibn al-Munādī", "† 336 H · le texte dit « consensus »", None),
    ]
    DROITE = [
      ("al-Ṭabarī", "† 310 H · imam des mufassirūn", None),
      ("al-Qayrawānī", "† 437 H", None),
      ("al-Māwardī", "† 450 H", None),
      ("Ibn ʿAṭiyyah", "† 542 H", None),
      ("al-Qurṭubī", "† 671 H", None),
      ("al-Suyūṭī", "† 911 H", None),
      ("al-Shawkānī", "† 1255 H", None),
    ]

    def colonne(x, items, col, y0, pas):
        ys = []
        for i, (nom, sous, ouvrage) in enumerate(items):
            y = y0 + i * pas
            ys.append(y)
            v.rect(x - 200, y - 17, 400, 34 if not ouvrage else 46, BG, col, 1.4, 5)
            v.txt(x - 188, y - 1, nom, col, 12.5, "700")
            v.txt(x - 188 + len(nom) * 12.5 * cote.CHW + 12, y - 1, sous, MUT, 10.5)
            if ouvrage:
                v.txt(x - 188, y + 17, ouvrage, INK, 10.5)
            if i:
                v.line(x, ys[i - 1] + (17 if not items[i - 1][2] else 29), x, y - 17, col, 1.6)
                v.raw(f'<path d="M{x - 4},{y - 24} L{x},{y - 17} L{x + 4},{y - 24}" fill="none" '
                      f'stroke="{col}" stroke-width="1.6"/>')
        return ys

    yg = colonne(XG, GAUCHE, CY, 148, 72)
    colonne(XD, DROITE, SAFFRON, 148, 72)

    # Ibn Taymiyyah : il rapporte la chaine de gauche, il n'en est pas l'auteur
    yb = 736
    v.rect(XG - 200, yb - 20, 400, 40, BG, RO, 1.6, 5)
    v.txt(XG - 188, yb + 5, "Ibn Taymiyyah † 728 H — il RAPPORTE", RO, 12.5, "700")
    v.line(XG, yg[-1] + 17, XG, yb - 20, RO, 1.6, "5 4")
    v.txt(XG - 188, yb + 38, "Majmūʿ al-Fatāwā 6/586-587 — ou 25/195 selon l'édition", MUT, 10.5)

    v.txt(556, 690, "aucune flèche", MUT, 11.5)
    v.txt(556, 708, "ne traverse", MUT, 11.5)
    v.txt(556, 726, "ce trait", MUT, 11.5)

    v.txt(28, H - 62, "Le texte qu'Ibn Taymiyyah rapporte descend de la colonne de gauche. Aucun de ses maillons", MUT, 11.5)
    v.txt(28, H - 42, "n'est un mujtahid de la Loi — ce que la définition de l'ijmāʿ exige. La colonne de droite,", MUT, 11.5)
    v.txt(28, H - 22, "elle, est indépendante : elle ne cite jamais la gauche, et elle la précède.", MUT, 11.5)
    return v


if __name__ == "__main__":
    os.makedirs("public/schemas", exist_ok=True)
    pb = 0
    for nom, fn in [("chaine-transmission-consensus", chaine_de_transmission)]:
        v = fn()
        pb += v.controle(nom)
        s = v.rendu()
        open(f"public/schemas/{nom}.svg", "w", encoding="utf-8").write(s)
        print(f"  ecrit  public/schemas/{nom}.svg  ({len(s)} octets, {v.w}x{v.h}, {len(v.boxes)} textes)")
    print("controle :", "OK" if pb == 0 else f"{pb} PROBLEME(S)")
    sys.exit(1 if pb else 0)
