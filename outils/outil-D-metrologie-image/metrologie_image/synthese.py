"""
synthese.py — Le tableau de bord, et l'export destiné au dossier d'audit (§33).

Assemble ce que `optique`, `annotation` et `inversion` ont établi, dans une
structure sérialisable en JSON, reprise telle quelle par la fiche d'observation
de l'outil C.

DEUX RÈGLES QUI TIENNENT TOUT LE MODULE
───────────────────────────────────────
1. Aucun champ n'est comblé. Une grandeur non établie porte la chaîne
   `indisponible`, jamais une valeur plausible, jamais zéro, jamais une
   moyenne.

   La source, elle, n'est plus une condition de calcul mais un relevé : une
   chaîne saisie dans un champ n'est pas une source vérifiée, et l'analyste qui
   reprend le dossier refait le travail. Le verrou ne garantissait donc rien et
   empêchait de calculer. `sources_manquantes` en fait la liste, et cette liste
   voyage jusque dans l'export — visible plutôt que bloquante.

2. Aucune ligne du tableau de bord ne conclut sur la forme de la surface. Le
   modèle sphérique est une ENTRÉE de cette chaîne : il est posé pour inverser
   l'angle en k. Un résultat obtenu en supposant le modèle ne peut pas servir
   à l'établir, et `CE_QUE_CA_N_ETABLIT_PAS` accompagne chaque synthèse pour
   que ce soit écrit là où le chiffre est lu.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional, Sequence, Tuple

from visee_optique.geometry import Cible, fraction_visible
from visee_optique.refraction import rayon_effectif

from .annotation import (
    AngleReleve,
    ControleHorizon,
    Pointes,
    angle_portion_emergente,
    controler_horizon,
)
from .inversion import (
    EnveloppeK,
    Plage,
    ResultatK,
    StatutK,
    altitude_visible_la_plus_basse,
    coefficient_refraction_effectif,
    elevation,
    enveloppe_coefficient,
)
from .optique import (
    Cadrage,
    Capteur,
    INDISPONIBLE,
    MetrologieError,
    Objectif,
    echelle_m_par_px,
    pas_angulaire_rad,
    resolution_angulaire_limite_rad,
)

CE_QUE_CA_N_ETABLIT_PAS = (
    "Le modèle sphérique est une entrée de ce calcul, pas sa conclusion : k est "
    "le coefficient qui réconcilierait l'angle relevé avec ce modèle, si D, "
    "h_obs et H sont exacts. Rien ici ne mesure la réfraction — aucune donnée "
    "atmosphérique n'entre dans la chaîne — et rien ici ne tranche sur la forme "
    "de la surface. Toute erreur sur les paramètres d'entrée se déverse dans k, "
    "qui est la variable d'ajustement.",
    "L'angle relevé n'établit la portion émergente que si la cible pointée est "
    "bien celle dont H est déclarée, et si le sommet pointé est bien son sommet.",
    "Une valeur de k compatible avec un régime du Tableau 8 ne démontre pas que "
    "ce régime régnait : le §11.7 interdit d'invoquer un régime après coup pour "
    "justifier la valeur obtenue.",
)


def altitude_pour_elevation(
    e_cible_rad: float, D: float, h: float, R: float,
    z_min: float = 0.0, z_max: float = 100_000.0,
) -> float:
    """z tel que elevation(z, D, h, R) == e_cible_rad — inverse de `elevation`.

    L'élévation croît strictement avec z à D et h fixés ; la bissection est
    donc bien posée. Elle refuse plutôt que d'extrapoler si l'élévation visée
    tombe hors du domaine balayé.
    """
    e_bas, e_haut = elevation(z_min, D, h, R), elevation(z_max, D, h, R)
    if not (e_bas <= e_cible_rad <= e_haut):
        raise MetrologieError(
            "Élévation %.9f rad hors du domaine balayé [%.9f ; %.9f] pour "
            "z ∈ [%g ; %g] m." % (e_cible_rad, e_bas, e_haut, z_min, z_max)
        )
    lo, hi = z_min, z_max
    for _ in range(200):
        mid = (lo + hi) / 2.0
        if elevation(mid, D, h, R) < e_cible_rad:
            lo = mid
        else:
            hi = mid
    return (lo + hi) / 2.0


def hauteur_emergente_mesuree(
    angle_rad: float, D: float, h: float, cible: Cible, R: float
) -> float:
    """Hauteur, en mètres, de la portion vue sous `angle_rad` depuis le bas visible.

    Calcul exact dans le modèle : on part de l'élévation du point le plus bas
    visible, on y ajoute l'angle relevé, et on cherche l'altitude qui rend
    cette élévation. Ce n'est pas D·tan(θ) — cette forme-là suppose la scène
    plane et perpendiculaire à la visée, ce qu'une cible lointaine n'est pas
    tout à fait. L'écart entre les deux est rendu par `Synthese`, parce qu'il
    est petit et qu'un écart petit non montré est un écart qu'on croit nul.
    """
    z_v = altitude_visible_la_plus_basse(D, h, cible, R)
    e_base = elevation(z_v, D, h, R)
    z_sommet = altitude_pour_elevation(e_base + angle_rad, D, h, R)
    return z_sommet - z_v


def hauteur_emergente_petit_angle(angle_rad: float, D: float) -> float:
    """D · tan(θ) — la forme du cahier des charges, pour comparaison seulement."""
    return D * math.tan(angle_rad)


def sources_manquantes(plages: Sequence[Plage]) -> Tuple[str, ...]:
    """Les grandeurs entrées sans source déclarée. Un relevé, pas un refus.

    Le calcul n'est plus bloqué par une source absente — voir `Plage` pour le
    raisonnement. Mais l'absence est relevée ici, portée dans la synthèse, et
    écrite dans l'export : un analyste qui reprend le dossier doit trouver la
    liste de ce qui reste à établir, pas la deviner.
    """
    return tuple(p.nom for p in plages if not p.source_declaree)


AVERTISSEMENT_SOURCES = (
    "Une source saisie ici est une DÉCLARATION de l'opérateur, jamais une "
    "vérification : rien dans cette chaîne ne contrôle qu'une fiche d'ouvrage "
    "dit bien ce qu'on lui fait dire. Les grandeurs sans source ne sont pas "
    "écartées du calcul, elles sont listées — c'est à l'analyste de les établir."
)


def _valeur_ou_indisponible(x: Optional[float], chiffres: int = 6) -> Any:
    return INDISPONIBLE if x is None else round(x, chiffres)


@dataclass(frozen=True)
class Synthese:
    """Le tableau de bord complet. Sérialisable tel quel."""

    # Étalonnage
    pas_angulaire_rad: float
    pas_angulaire_arcsec: float
    echelle_m_par_px: float
    limite_diffraction_arcsec: Optional[float]
    pas_sous_la_limite_de_diffraction: Optional[bool]
    point_principal_connu: bool
    image_recadree: bool
    facteur_reechantillonnage: float
    # Mesure
    angle_emergent: AngleReleve
    controle_horizon: ControleHorizon
    # Inversion
    resultat_k: ResultatK
    enveloppe_k: EnveloppeK
    # Restitution
    hauteur_emergente_m: Optional[float]
    hauteur_emergente_petit_angle_m: float
    fraction_visible_mesuree: Optional[float]
    fraction_visible_modele: Optional[float]
    # Traçabilité
    empreinte_sha256: str
    nom_fichier: str
    sources: Dict[str, str]
    sources_manquantes: Tuple[str, ...]

    def en_dict(self) -> Dict[str, Any]:
        """Représentation JSON, destinée au dossier d'audit et à l'outil C."""
        r = self.resultat_k
        return {
            "outil": "metrologie-image (outil D)",
            "protocole": "Portion visible d'une cible éloignée au-dessus de la mer v1.0",
            "traçabilité": {
                "fichier": self.nom_fichier or INDISPONIBLE,
                "sha256": self.empreinte_sha256 or INDISPONIBLE,
                "sources": dict(self.sources),
                # Ce qui reste à établir. Une liste vide n'atteste de rien : une
                # source déclarée est une déclaration, pas une vérification.
                "sources_manquantes": list(self.sources_manquantes),
                "avertissement_sources": AVERTISSEMENT_SOURCES,
            },
            "étalonnage": {
                "pas_angulaire_arcsec": round(self.pas_angulaire_arcsec, 6),
                "echelle_m_par_px": round(self.echelle_m_par_px, 6),
                "limite_diffraction_arcsec": _valeur_ou_indisponible(
                    self.limite_diffraction_arcsec
                ),
                "pas_sous_la_limite_de_diffraction": (
                    INDISPONIBLE
                    if self.pas_sous_la_limite_de_diffraction is None
                    else self.pas_sous_la_limite_de_diffraction
                ),
                "point_principal_connu": self.point_principal_connu,
                "image_recadree": self.image_recadree,
                "facteur_reechantillonnage": round(self.facteur_reechantillonnage, 9),
            },
            "mesure": {
                "angle_emergent_rad": _valeur_ou_indisponible(self.angle_emergent.exact, 12),
                "angle_emergent_paraxial_rad": round(self.angle_emergent.paraxial, 12),
                "angle_emergent_borne_basse_rad": round(self.angle_emergent.borne_basse, 12),
                "angle_emergent_borne_haute_rad": round(self.angle_emergent.borne_haute, 12),
                "incertitude_elargie_rad": round(self.angle_emergent.incertitude, 12),
                "ecart_paraxial_rad": _valeur_ou_indisponible(
                    self.angle_emergent.ecart_paraxial, 12
                ),
                "hauteur_emergente_m": _valeur_ou_indisponible(self.hauteur_emergente_m, 3),
                "hauteur_emergente_petit_angle_m": round(
                    self.hauteur_emergente_petit_angle_m, 3
                ),
                "fraction_visible_mesuree": _valeur_ou_indisponible(
                    self.fraction_visible_mesuree, 6
                ),
            },
            "controle_horizon_base": {
                "ecart_releve_px": round(self.controle_horizon.ecart_px, 3),
                "ecart_predit_px": round(self.controle_horizon.ecart_predit_px, 3),
                "tolerance_px": round(self.controle_horizon.tolerance_px, 3),
                "coherent": self.controle_horizon.coherent,
                "causes_possibles": list(self.controle_horizon.causes_possibles),
            },
            "refraction": {
                "statut": r.statut.value,
                "k": _valeur_ou_indisponible(r.k),
                "k_min": _valeur_ou_indisponible(r.k_min),
                "k_max": _valeur_ou_indisponible(r.k_max),
                "k_saturation": _valeur_ou_indisponible(r.k_saturation),
                "dans_zone_saturee": r.dans_zone_saturee,
                "regime": r.regime.value if r.regime else INDISPONIBLE,
                "regime_determine": r.regime_determine,
                "enveloppe_entrees": {
                    "k_min": _valeur_ou_indisponible(self.enveloppe_k.k_min),
                    "k_max": _valeur_ou_indisponible(self.enveloppe_k.k_max),
                    "combinaisons": self.enveloppe_k.combinaisons,
                    "combinaisons_non_bornees": self.enveloppe_k.combinaisons_non_bornees,
                },
                "interpretation": interpreter(r),
            },
            "ce_que_ca_n_etablit_pas": list(CE_QUE_CA_N_ETABLIT_PAS),
        }


def interpreter(r: ResultatK) -> str:
    """Phrase de restitution. Décrit ce qui est établi, jamais davantage.

    Le cahier des charges proposait trois seuils (k ≈ 0,13 ; k > 0,25 ;
    k < 0,00). Les deux premiers ne sont pas ceux du protocole : le Tableau 8
    (§11.3) donne 0,13–0,17 pour le régime standard et 0,20–0,40 pour la
    réfraction forte. Le classement employé ici est celui du Tableau 8, par
    `visee_optique.classer_regime` — une seule table de régimes dans tout le
    dépôt, pas deux qui divergeront.

    Le libellé du cahier des charges « cible surélevée » est écarté : c'est
    une conclusion sur la scène, alors que la seule chose établie est une
    valeur de k compatible avec un régime.
    """
    if r.statut is StatutK.MINORE:
        return (
            "La portion relevée excède ce que le modèle prédit pour tout k exploré : "
            "k n'est pas déterminé, il est seulement minoré. Cela se produit quand la "
            "cible paraît plus haute que la géométrie ne l'autorise — régime de conduit, "
            "erreur sur D, h_obs ou H, ou cible mal identifiée."
        )
    if r.statut is StatutK.MAJORE:
        if r.dans_zone_eteinte:
            seuil = (
                " Sous k = %.3f la cible est occultée jusqu'au sommet, et l'angle "
                "prédit y vaut exactement zéro quelle que soit la valeur de k : "
                "un relevé nul majore k, il ne le mesure pas." % r.k_extinction
                if r.k_extinction is not None
                else " L'angle prédit vaut zéro sur tout l'intervalle exploré."
            )
            return (
                "Aucune portion émergente n'a été relevée." + seuil + " Ce résultat est "
                "compatible avec une cible réellement invisible comme avec un sommet "
                "manqué au pointé : il ne les distingue pas."
            )
        return (
            "La portion relevée est inférieure à ce que le modèle prédit pour tout k "
            "exploré : k n'est pas déterminé, il est seulement majoré. Une occultation "
            "autre que la courbure — relief, brume, ouvrage — suffit à produire cela."
        )
    if r.k is None:
        return "k n'est pas établi par ce relevé."

    if r.dans_zone_saturee:
        socle = (
            "Au-delà de k = %.3f la cible est entièrement émergée et l'angle cesse de "
            "dépendre de k. La valeur trouvée (%.3f) est dans cette zone : elle est "
            "compatible avec le relevé, mais le relevé ne la distingue pas des valeurs "
            "supérieures. À traiter comme un minorant, pas comme une mesure."
            % (r.k_saturation, r.k)
        )
    else:
        socle = "k = %.3f rend compte de l'angle relevé." % r.k

    if r.k_min is None or r.k_max is None:
        borne = " L'enveloppe de pointé est ouverte d'un côté : k n'y est pas encadré."
    else:
        borne = " Enveloppe due au seul pointé : k ∈ [%.3f ; %.3f]." % (r.k_min, r.k_max)

    if r.regime_determine:
        regime = " Les deux bornes tombent dans le régime « %s » (Tableau 8, §11.3)." % (
            r.regime_min.value
        )
    elif r.regime_min is not None and r.regime_max is not None:
        regime = (
            " L'enveloppe traverse plusieurs régimes du Tableau 8, de « %s » à « %s » : "
            "aucun n'est établi." % (r.regime_min.value, r.regime_max.value)
        )
    else:
        regime = " Le régime n'est pas déterminé."

    return socle + borne + regime


def assembler(
    pointes: Pointes,
    capteur: Capteur,
    cadrage: Cadrage,
    objectif: Objectif,
    distance: Plage,
    altitude_observateur: Plage,
    hauteur_cible: Plage,
    altitude_base: Plage,
    R0: float,
    empreinte_sha256: str = "",
    nom_fichier: str = "",
    diametre_pupille_m: Optional[float] = None,
    longueur_onde_m: float = 550e-9,
) -> Synthese:
    """Chaîne complète : trois clics, quatre grandeurs sourcées, une synthèse.

    R0 est le rayon de courbure géométrique adopté — le rayon d'Euler à
    l'azimut de la visée (§12.2), fourni par l'outil A. Cet outil ne le calcule
    pas : le recalculer ici en ferait une seconde implémentation, et c'est
    exactement le défaut que le dépôt combat.
    """
    plages = [distance, altitude_observateur, hauteur_cible, altitude_base]

    cible = Cible(H=hauteur_cible.valeur, z_b=altitude_base.valeur)
    D, h = distance.valeur, altitude_observateur.valeur

    angle = angle_portion_emergente(pointes, capteur, cadrage, objectif)
    resultat = coefficient_refraction_effectif(
        angle.valeur, angle.incertitude, D, h, cible, R0
    )
    enveloppe = enveloppe_coefficient(
        angle.valeur, angle.incertitude,
        distance, altitude_observateur, hauteur_cible, altitude_base, R0,
    )

    if resultat.k is not None:
        R = rayon_effectif(R0, resultat.k)
        hauteur = hauteur_emergente_mesuree(angle.valeur, D, h, cible, R)
        fraction_mesuree = hauteur / cible.H
        fraction_modele = fraction_visible(D, h, cible, R)
    else:
        R = rayon_effectif(R0, 0.13)  # seul le contrôle d'horizon s'en sert
        hauteur = None
        fraction_mesuree = None
        fraction_modele = None

    controle = controler_horizon(pointes, capteur, cadrage, objectif, D, h, cible, R)

    pas = pas_angulaire_rad(capteur, cadrage, objectif)
    if diametre_pupille_m is not None:
        limite = resolution_angulaire_limite_rad(longueur_onde_m, diametre_pupille_m)
        limite_arcsec = math.degrees(limite) * 3600.0
        sous_limite = pas < limite
    else:
        limite_arcsec = None
        sous_limite = None

    return Synthese(
        pas_angulaire_rad=pas,
        pas_angulaire_arcsec=math.degrees(pas) * 3600.0,
        echelle_m_par_px=echelle_m_par_px(D, capteur, cadrage, objectif),
        limite_diffraction_arcsec=limite_arcsec,
        pas_sous_la_limite_de_diffraction=sous_limite,
        point_principal_connu=cadrage.point_principal_connu,
        image_recadree=cadrage.recadree,
        facteur_reechantillonnage=cadrage.facteur_reechantillonnage,
        angle_emergent=angle,
        controle_horizon=controle,
        resultat_k=resultat,
        enveloppe_k=enveloppe,
        hauteur_emergente_m=hauteur,
        hauteur_emergente_petit_angle_m=hauteur_emergente_petit_angle(angle.valeur, D),
        fraction_visible_mesuree=fraction_mesuree,
        fraction_visible_modele=fraction_modele,
        empreinte_sha256=empreinte_sha256,
        nom_fichier=nom_fichier,
        sources={p.nom: p.source for p in plages if p.source_declaree},
        sources_manquantes=sources_manquantes(plages),
    )
