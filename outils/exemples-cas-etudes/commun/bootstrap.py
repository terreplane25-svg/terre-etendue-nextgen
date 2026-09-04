"""
bootstrap.py — Rend les trois paquets importables, quel que soit l'endroit d'où
l'on lance un cas d'étude.

Les quatre `run_case.py` livrés commençaient par trois lignes de chemins codés
en dur :

    sys.path.insert(0, "/home/claude/visee-optique")
    sys.path.insert(0, "/home/claude/preuve-image")
    sys.path.insert(0, "/home/claude/rapport-expertise")

Ces chemins n'existent que sur la machine où les cas ont été écrits. Ailleurs,
les trois insertions ne servaient à rien et l'import échouait — sauf si les
paquets étaient déjà installés, auquel cas les insertions étaient inutiles.
Autrement dit : elles ne pouvaient jamais aider.

Ce module les remplace par une résolution relative au fichier lui-même. Il
essaie d'abord l'import direct — le cas normal quand les paquets sont installés
en editable, et le seul qui garantisse que le code exécuté est bien celui du
dépôt — et ne touche à `sys.path` que si l'import échoue.
"""

import sys
from pathlib import Path

# outils/exemples-cas-etudes/commun/bootstrap.py → outils/
RACINE_OUTILS = Path(__file__).resolve().parent.parent.parent

PAQUETS = (
    ("visee_optique", "outil-A-visee-optique"),
    ("preuve_image", "outil-B-preuve-image"),
    ("rapport_expertise", "outil-C-rapport-expertise"),
)


def preparer_chemins() -> list[str]:
    """Garantit que les trois paquets sont importables. Renvoie ce qui a été ajouté.

    Lève ImportError avec la marche à suivre si un paquet reste introuvable,
    plutôt que de laisser remonter une trace d'import nue.
    """
    ajoutes = []
    for module, dossier in PAQUETS:
        try:
            __import__(module)
            continue
        except ImportError:
            pass
        chemin = RACINE_OUTILS / dossier
        if not (chemin / module).is_dir():
            raise ImportError(
                f"Paquet « {module} » introuvable, ni installé ni sous {chemin}.\n"
                "Depuis la racine du dépôt :\n"
                "    python3 -m venv outils/.venv\n"
                "    outils/.venv/bin/pip install -e outils/outil-A-visee-optique \\\n"
                "        -e outils/outil-B-preuve-image -e outils/outil-C-rapport-expertise"
            )
        sys.path.insert(0, str(chemin))
        ajoutes.append(str(chemin))
        __import__(module)

    # Le dossier commun lui-même, pour build_demo_image.
    commun = str(Path(__file__).resolve().parent)
    if commun not in sys.path:
        sys.path.insert(0, commun)
        ajoutes.append(commun)
    return ajoutes
