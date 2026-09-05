import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Le paquet visee_optique est la référence géométrique de cet outil : il n'est
# pas recopié ici. S'il n'est pas installé, on le résout à côté, comme le fait
# `outils/exemples-cas-etudes/commun/bootstrap.py`.
try:
    import visee_optique  # noqa: F401
except ImportError:  # pragma: no cover - dépend de l'environnement
    sys.path.insert(
        0,
        os.path.join(
            os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
            "outil-A-visee-optique",
        ),
    )
