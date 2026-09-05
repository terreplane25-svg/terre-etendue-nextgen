"""
metrologie_image — Outil D : métrologie optique sur image.

Convertit trois pointés sur une photographie de visée en un angle, puis cet
angle en coefficient de réfraction effectif, dans le modèle sphérique du
protocole « Portion visible d'une cible éloignée au-dessus de la mer » v1.0.

Ce paquet ne recopie aucune géométrie : il importe `visee_optique` (outil A),
qui reste la seule implémentation de la construction du §9. Il ne calcule
aucune empreinte ni métadonnée : c'est `preuve_image` (outil B) qui les
établit, et cet outil les transporte telles quelles.

Il ne conclut sur rien. Le modèle sphérique est une entrée de la chaîne, pas
sa conclusion ; k est une variable d'ajustement, pas une mesure de la
réfraction ; et quand l'angle relevé ne détermine pas k, le résultat est
`indisponible` et non une valeur plausible.
"""

from .optique import (
    INDISPONIBLE,
    LARGEUR_24x36_MM,
    Cadrage,
    Capteur,
    MetrologieError,
    Objectif,
    angle_entre_lignes,
    angle_entre_lignes_enveloppe,
    angle_entre_lignes_paraxial,
    cadrage_plein_capteur,
    capteur_equivalent_35mm,
    echelle_m_par_px,
    ordonnee_point_principal_px,
    pas_angulaire_rad,
    pas_pixel_livre_mm,
    resolution_angulaire_limite_rad,
)

from .inversion import (
    K_PLAFOND,
    K_PLANCHER,
    EnveloppeK,
    Plage,
    ResultatK,
    StatutK,
    altitude_visible_la_plus_basse,
    angle_horizon_base,
    angle_portion_visible,
    coefficient_refraction_effectif,
    elevation,
    elevation_horizon,
    enveloppe_coefficient,
    k_d_extinction,
    k_de_saturation,
)

from .annotation import (
    CAUSES_ECART_HORIZON,
    FACTEUR_ELARGISSEMENT,
    SIGMA_POINTE_PX_DEFAUT,
    AngleReleve,
    ControleHorizon,
    Pointes,
    angle_portion_emergente,
    controler_horizon,
    dispersion_pointes,
)

from .synthese import (
    CE_QUE_CA_N_ETABLIT_PAS,
    Synthese,
    altitude_pour_elevation,
    assembler,
    hauteur_emergente_mesuree,
    hauteur_emergente_petit_angle,
    interpreter,
    verifier_sources,
)

__all__ = [
    "INDISPONIBLE",
    "LARGEUR_24x36_MM",
    "Cadrage",
    "Capteur",
    "MetrologieError",
    "Objectif",
    "angle_entre_lignes",
    "angle_entre_lignes_enveloppe",
    "angle_entre_lignes_paraxial",
    "cadrage_plein_capteur",
    "capteur_equivalent_35mm",
    "echelle_m_par_px",
    "ordonnee_point_principal_px",
    "pas_angulaire_rad",
    "pas_pixel_livre_mm",
    "resolution_angulaire_limite_rad",
    "K_PLAFOND",
    "K_PLANCHER",
    "EnveloppeK",
    "Plage",
    "ResultatK",
    "StatutK",
    "altitude_visible_la_plus_basse",
    "angle_horizon_base",
    "angle_portion_visible",
    "coefficient_refraction_effectif",
    "elevation",
    "elevation_horizon",
    "enveloppe_coefficient",
    "k_d_extinction",
    "k_de_saturation",
    "CAUSES_ECART_HORIZON",
    "FACTEUR_ELARGISSEMENT",
    "SIGMA_POINTE_PX_DEFAUT",
    "AngleReleve",
    "ControleHorizon",
    "Pointes",
    "angle_portion_emergente",
    "controler_horizon",
    "dispersion_pointes",
    "CE_QUE_CA_N_ETABLIT_PAS",
    "Synthese",
    "altitude_pour_elevation",
    "assembler",
    "hauteur_emergente_mesuree",
    "hauteur_emergente_petit_angle",
    "interpreter",
    "verifier_sources",
]
