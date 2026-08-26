#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Inscription du DOI réservé dans le protocole de l'horizon, et préparation du
dépôt.

    python3 scripts/inscrire-doi.py 10.5281/zenodo.1234567

Ce que fait le script, dans l'ordre :

  1. remplace le marqueur DOI-EN-ATTENTE / DOI-PENDING par le DOI réel, aux
     deux emplacements de chacune des deux sources — première page et
     section 13 ;
  2. regénère les deux PDF ;
  3. les copie dans content/protocoles/depot/ ;
  4. calcule les empreintes SHA-256 et écrit SHA256SUMS.txt ;
  5. affiche ce qu'il reste à faire à la main.

Pourquoi un script plutôt qu'une retouche à la main
───────────────────────────────────────────────────
Parce qu'un DOI mal recopié à un seul des quatre emplacements passerait
inaperçu, et ne se verrait qu'après publication — c'est-à-dire trop tard, le
fichier étant alors figé et haché. Le script traite les quatre en une fois, et
refuse de s'exécuter s'il n'en trouve pas exactement quatre.

Pourquoi il ne peut être lancé qu'une fois
──────────────────────────────────────────
Une fois le marqueur remplacé, il n'y a plus rien à remplacer. Le script le
détecte et s'arrête en le disant, plutôt que de laisser croire qu'il a
travaillé. Pour changer un DOI déjà inscrit — cas qui ne devrait pas se
produire — il faut revenir aux sources par git.

L'EMPREINTE NE PEUT PAS ENTRER DANS LE FICHIER
──────────────────────────────────────────────
Elle se calcule sur le fichier fini. L'y inscrire le modifierait, donc la
fausserait. C'est pourquoi le script l'affiche et l'écrit à côté, dans
SHA256SUMS.txt : elle est destinée au champ « notes » de l'enregistrement, et
à toute annonce du protocole. Le DOI, lui, est attribué avant publication et
peut donc figurer dans le document — c'est tout l'objet de ce script.

Le rendu PDF n'est pas reproductible octet à octet : Chromium y inscrit un
horodatage de création. Les fichiers écrits dans depot/ sont donc les seuls
exemplaires auxquels les empreintes se rapportent. Ne pas les regénérer.
"""

import hashlib
import pathlib
import re
import subprocess
import sys

RACINE = pathlib.Path(__file__).resolve().parent.parent
SOURCES = RACINE / "content" / "protocoles"
PDF = SOURCES / "pdf"
DEPOT = SOURCES / "depot"

# source, marqueur, nom du PDF rendu, clé pour rendre-protocoles.py
DOCUMENTS = [
    ("horizon-fr.html", "DOI-EN-ATTENTE", "Protocole-depression-horizon.pdf", "horizon-fr"),
    ("horizon-en.html", "DOI-PENDING", "Horizon-Dip-Protocol.pdf", "horizon-en"),
]

ATTENDU = 2  # emplacements par fichier : première page et section 13


def valider(doi):
    """Un DOI commence par 10., un préfixe d'éditeur, une barre, un suffixe."""
    doi = doi.strip()
    for prefixe in ("https://doi.org/", "http://doi.org/", "doi:"):
        if doi.lower().startswith(prefixe):
            doi = doi[len(prefixe):]
    if not re.fullmatch(r"10\.\d{4,9}/\S+", doi):
        sys.exit("  ✗ « %s » ne ressemble pas à un DOI.\n"
                 "    Attendu : 10.5281/zenodo.1234567 (Zenodo)\n"
                 "              10.17605/OSF.IO/ABCDE  (OSF)" % doi)
    return doi


def empreinte(chemin):
    h = hashlib.sha256()
    with open(chemin, "rb") as f:
        for bloc in iter(lambda: f.read(1 << 20), b""):
            h.update(bloc)
    return h.hexdigest()


def main():
    if len(sys.argv) != 2:
        print(__doc__.strip())
        return 1
    doi = valider(sys.argv[1])

    # 1 — vérifier AVANT d'écrire quoi que ce soit
    for source, marqueur, _, _ in DOCUMENTS:
        chemin = SOURCES / source
        n = chemin.read_text(encoding="utf-8").count(marqueur)
        if n == 0:
            sys.exit("  ✗ %s ne contient plus le marqueur « %s ».\n"
                     "    Un DOI y a probablement déjà été inscrit. Pour recommencer,\n"
                     "    restaurer les sources : git checkout content/protocoles/"
                     % (source, marqueur))
        if n != ATTENDU:
            sys.exit("  ✗ %s contient %d marqueurs « %s », %d attendus.\n"
                     "    Le document a changé ; vérifier avant d'inscrire un DOI."
                     % (source, n, marqueur, ATTENDU))

    print("Inscription du DOI %s" % doi)
    for source, marqueur, _, _ in DOCUMENTS:
        chemin = SOURCES / source
        t = chemin.read_text(encoding="utf-8")
        chemin.write_text(t.replace(marqueur, doi), encoding="utf-8")
        print("  ✓ %-18s %d emplacements" % (source, ATTENDU))

    # 2 — rendu
    print("\nRendu des PDF")
    cles = [c for _, _, _, c in DOCUMENTS]
    r = subprocess.run([sys.executable, str(RACINE / "scripts" / "rendre-protocoles.py")] + cles,
                       cwd=str(RACINE))
    if r.returncode != 0:
        sys.exit("  ✗ le rendu a échoué. Les sources portent le DOI ; corriger et relancer\n"
                 "    seulement le rendu, sans repasser par ce script.")

    # 3 et 4 — dépôt et empreintes
    DEPOT.mkdir(parents=True, exist_ok=True)
    lignes = []
    print("\nDossier de dépôt")
    for _, _, pdf, _ in DOCUMENTS:
        src, dst = PDF / pdf, DEPOT / pdf
        dst.write_bytes(src.read_bytes())
        e = empreinte(dst)
        lignes.append("%s  %s" % (e, pdf))
        print("  ✓ %-34s %d ko" % (pdf, dst.stat().st_size // 1024))
        print("    %s" % e)
    (DEPOT / "SHA256SUMS.txt").write_text("\n".join(sorted(lignes)) + "\n", encoding="utf-8")

    print("""
Reste à faire, à la main :

  1. Téléverser les DEUX fichiers de content/protocoles/depot/ dans le MÊME
     enregistrement Zenodo — celui dont le DOI vient d'être réservé.
  2. Coller le contenu de SHA256SUMS.txt dans le champ « notes » de
     l'enregistrement. L'empreinte ne peut pas être dans les fichiers.
  3. Publier l'enregistrement. Le DOI devient permanent.
  4. Ne commencer à collecter qu'ensuite.

Ne pas regénérer les PDF de depot/ : le rendu n'étant pas reproductible octet
à octet, une nouvelle exécution donnerait d'autres empreintes que celles qui
viennent d'être publiées.""")
    return 0


if __name__ == "__main__":
    sys.exit(main())
