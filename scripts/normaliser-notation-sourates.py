#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Unifie la notation des références coraniques dans les attributions.

La charte impose une notation unique — nom translittéré, puis S<sourate> V<verset>.
Soixante-six attributions la respectent. Vingt ne la respectaient pas, dans trois
formes différentes : « Sourate Al-A'raf, 7:54 », « Sourate Al-Māʾida — 5:48 », et
les plages « 88:17-20 ».

Ce n'est pas de la cosmétique. Un lecteur qui veut vérifier une citation la
cherche par sourate et verset ; deux notations concurrentes dans le même corpus
l'obligent à deviner laquelle il a sous les yeux, et une recherche plein texte
sur « S88 V20 » rate la moitié des occurrences. Sur un site dont l'argument
principal est textuel, la référence est l'équivalent du chiffre : elle se donne
sous une forme et une seule.

Les translittérations sont alignées sur celles déjà employées dans le corpus :
diacritiques savants, article assimilé devant les lettres solaires — An-Naḥl et
non Al-Naḥl —, finale -ah. « Al-Ghashiyah » devient « Al-Ghāshiyah », qui est
déjà la forme dans quatre autres articles.

Les cinq attributions qui écrivaient « — An-Naḥl — S16 V15 » sans le mot
« Sourate » reçoivent ce mot : la forme majoritaire du corpus le porte, et deux
formes justes valent moins qu'une seule.

Le numéro de sourate annoncé par le nom est vérifié contre le numéro écrit. Un
nom qui ne correspondrait pas à son numéro arrête le script.
"""
import json
import os
import re
import sys

RACINE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ARTICLES = os.path.join(RACINE, "content", "articles")

# Nom normalisé par numéro de sourate, pour celles qui apparaissent dans le
# corpus. La table sert deux fois : à corriger l'orthographe, et à vérifier que
# le nom cité correspond bien au numéro cité.
NOMS = {
    2: "Al-Baqarah", 3: "Āl ʿImrān", 4: "An-Nisāʾ", 5: "Al-Māʾidah",
    6: "Al-Anʿām", 7: "Al-Aʿrāf", 10: "Yūnus", 11: "Hūd", 13: "Ar-Raʿd",
    14: "Ibrāhīm", 15: "Al-Ḥijr", 16: "An-Naḥl", 18: "Al-Kahf", 20: "Ṭā Hā",
    21: "Al-Anbiyāʾ", 27: "An-Naml", 29: "Al-ʿAnkabūt", 31: "Luqmān",
    35: "Fāṭir", 36: "Yā Sīn", 37: "Aṣ-Ṣāffāt", 38: "Ṣād", 39: "Az-Zumar",
    41: "Fuṣṣilat", 51: "Adh-Dhāriyāt", 55: "Ar-Raḥmān", 67: "Al-Mulk",
    70: "Al-Maʿārij", 71: "Nūḥ", 78: "An-Nabaʾ", 79: "An-Nāziʿāt",
    88: "Al-Ghāshiyah", 91: "Ash-Shams", 112: "Al-Ikhlāṣ",
}

# Les graphies rencontrées, ramenées à leur numéro. Sert de garde-fou : un nom
# absent de cette table et absent de NOMS fait échouer le script plutôt que de
# passer inaperçu.
ALIAS = {
    "al-a'raf": 7, "al-a’raf": 7, "al-aʿrāf": 7,
    "al-mulk": 67, "al-ghashiyah": 88, "al-ghāshiyah": 88,
    "al-ʿankabūt": 29, "al-ankabut": 29,
    "yūnus": 10, "nūḥ": 71, "al-naḥl": 16, "an-naḥl": 16,
    "al-māʾida": 5, "al-māʾidah": 5, "al-anbiyāʾ": 21, "al-ikhlāṣ": 112,
    "az-zumar": 39, "al-imran": 3, "āl ʿimrān": 3, "sad": 38, "ṣād": 38,
    "fussilat": 41, "fuṣṣilat": 41, "al-nisāʾ": 4, "an-nisāʾ": 4,
    "al-baqarah": 2, "adh-dhāriyāt": 51, "al-kahf": 18, "hūd": 11,
    "an-naml": 27, "luqmān": 31, "ar-raʿd": 13, "al-ḥijr": 15,
    "an-nabaʾ": 78, "ash-shams": 91, "an-nāziʿāt": 79, "aṣ-ṣāffāt": 37,
    "al-ṣāffāt": 37, "yā sīn": 36, "ibrāhīm": 14, "ar-raḥmān": 55,
    "ṭā hā": 20, "ṭā-hā": 20, "al-anʿām": 6, "fāṭir": 35, "al-maʿārij": 70,
}

# « Sourate Nom, 7:54 » ou « Sourate Nom — 7:54 », dans une attribution.
ANCIENNE = re.compile(
    r"<footer>(\s*—\s*)?Sourate\s+([^,—<]+?)\s*[,—]\s*(\d+)\s*:\s*(\d+(?:-\d+)?)\s*</footer>")
# « — An-Naḥl — S16 V15 » : conforme, mais sans le mot « Sourate ».
SANS_MOT = re.compile(r"<footer>\s*—\s*([^—<]+?)\s+—\s+S(\d+)\s+V(\d+(?:-\d+)?)\s*</footer>")


def numero(nom):
    cle = nom.strip().lower().replace("’", "'")
    if cle in ALIAS:
        return ALIAS[cle]
    for n, propre in NOMS.items():
        if propre.lower() == cle:
            return n
    return None


def main():
    total, fichiers = 0, {}
    for fichier in sorted(os.listdir(ARTICLES)):
        if not fichier.endswith(".json"):
            continue
        chemin = os.path.join(ARTICLES, fichier)
        with open(chemin, encoding="utf-8") as f:
            art = json.load(f)
        html = art["htmlBody"]
        avant = html

        def refaire(m):
            _, nom, sourate, verset = m.groups()
            n = numero(nom)
            if n is None:
                sys.exit("Sourate inconnue dans %s : « %s ». "
                         "L'ajouter à ALIAS avant de relancer." % (fichier, nom))
            if n != int(sourate):
                sys.exit("%s : « %s » est la sourate %d, mais la référence dit %s. "
                         "Rien n'est écrit." % (fichier, nom.strip(), n, sourate))
            return "<footer>— Sourate %s — S%s V%s</footer>" % (NOMS[n], sourate, verset)

        html = ANCIENNE.sub(refaire, html)

        def ajouter_mot(m):
            nom, sourate, verset = m.groups()
            n = numero(nom)
            if n is None or n != int(sourate):
                return m.group(0)  # ce n'est pas une sourate : on n'y touche pas
            return "<footer>— Sourate %s — S%s V%s</footer>" % (NOMS[n], sourate, verset)

        html = SANS_MOT.sub(ajouter_mot, html)

        if html != avant:
            n = len(ANCIENNE.findall(avant))
            total += n
            art["htmlBody"] = html
            fichiers[chemin] = art

    for chemin, art in fichiers.items():
        with open(chemin, "w", encoding="utf-8") as f:
            json.dump(art, f, ensure_ascii=False, indent=2)
            f.write("\n")
    print("%d fichiers réécrits, %d références remises à la notation S/V."
          % (len(fichiers), total))

    # Contrôle final : plus aucune attribution coranique hors notation.
    restantes = []
    for fichier in sorted(os.listdir(ARTICLES)):
        if not fichier.endswith(".json"):
            continue
        with open(os.path.join(ARTICLES, fichier), encoding="utf-8") as f:
            html = json.load(f)["htmlBody"]
        for m in re.finditer(r"<footer>(.*?)</footer>", html, re.S):
            t = re.sub(r"<[^>]+>", "", m.group(1)).strip()
            if re.match(r"^—?\s*(Sourate|Coran|Sūrat)", t, re.I) and not re.search(
                    r"S\d+ V\d+", t):
                restantes.append((fichier[:-5], t))
    if restantes:
        for s, t in restantes:
            print("  RESTE : %-46s %s" % (s, t))
        sys.exit("Des attributions coraniques échappent encore à la notation.")
    print("Contrôle : aucune attribution coranique hors notation S/V.")


if __name__ == "__main__":
    main()
