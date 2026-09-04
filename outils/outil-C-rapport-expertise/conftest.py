import os
import sys

_ICI = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, _ICI)

# rapport_expertise assemble les sorties de l'Outil A (visee_optique) et de
# l'Outil B (preuve_image) — voir le README du paquet. Ce projet ne les
# vendorise pas : en développement, les trois projets vivent comme dossiers
# frères sous le même répertoire parent, et on les ajoute ici au chemin
# d'import pour les tests. En dehors de cet environnement, installez-les
# (`pip install -e ../visee-optique -e ../preuve-image`) plutôt que de
# dépendre de cette astuce de chemin.
_PARENT = os.path.dirname(_ICI)
for _projet in ("visee-optique", "preuve-image"):
    _chemin = os.path.join(_PARENT, _projet)
    if os.path.isdir(_chemin) and _chemin not in sys.path:
        sys.path.insert(0, _chemin)
