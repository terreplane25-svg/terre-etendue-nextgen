"""
run_case.py — second cas réel bout-en-bout, à travers visee_optique (Outil A),
preuve_image (Outil B) et rapport_expertise (Outil C).

Même cible que le premier cas (CAS-DEMO-CORDOUAN-001, dossier cas-cordouan/) :
le phare de Cordouan. Poste de référence différent : le phare de Chassiron
(pointe nord-ouest de l'île d'Oléron), à 54,4 km plutôt que 13,1 km — choisi
précisément parce que le calcul montre que la condition de discrimination du
§28.2 y est satisfaite, contrairement au premier site.

CE QUE CE CAS EST : un second point du même exercice — même géométrie réelle
sourcée, même discipline de déclaration (INDISPONIBLE plutôt que deviné),
menée jusqu'à une seconde archive §34 publiable.

CE QUE CE CAS N'EST PAS : une expertise, ni la preuve que la Terre est ronde
ou plate. Aucune photographie réelle n'a été prise ni mesurée depuis
Chassiron. Le résultat marquant n'est pas une fraction visible mesurée, mais
un second constat géométrique, inverse du premier : à cette distance, le
modèle sphérique prédit que le sommet du phare de Cordouan (67,5 m) est
entièrement sous l'horizon géométrique et réfracté, quelle que soit la
combinaison plausible de hauteur d'observateur et de coefficient de
réfraction retenue — alors que le modèle plat prédit toujours une visibilité
totale.

CORRECTION (2026-09-03) : ce module a d'abord conclu, sur cette seule base
géométrique, que le site était « un candidat sérieux pour une VRAIE campagne
de mesure ». Une vérification demandée ensuite, menée avec l'altimétrie
officielle IGN (RGE ALTI — voir case_data.PROFIL_CONCLUSION_DEFINITIVE et
30-donnees-externes/profil_intermediaire.md dans l'archive produite), a
montré que c'est FAUX : la ligne droite Chassiron→Cordouan traverse la terre
ferme sur environ 20,5 km (l'île d'Oléron elle-même, puis la presqu'île
d'Arvert). Chassiron ne peut pas voir Cordouan en ligne droite, indépendamment
de tout modèle de courbure. Le site est donc INVALIDE pour une vraie
campagne — la condition de discrimination du §28.2 reste correcte comme
calcul, mais sans objet ici.
"""

import dataclasses
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

# Les trois paquets sont rendus importables par le module commun, qui les
# cherche d'abord parmi les paquets installés puis, à défaut, à côté de ce
# fichier. Les chemins codés en dur d'origine — /home/claude/... — n'existaient
# que sur la machine où ces cas ont été écrits.
sys.path.insert(0, str(Path(__file__).resolve().parent.parent / "commun"))
from bootstrap import preparer_chemins  # noqa: E402
preparer_chemins()

from visee_optique.geodesy import rayon_euler, GrandeurGeodesique
from visee_optique.geometry import Cible as CibleGeom
from visee_optique.refraction import RegimeRefraction
from visee_optique.atmosphere import intervalle_k_faute_de_donnee_resolue, ClasseDonnee
from visee_optique.models import ModeleSpherique, ModeleSurfacePlane, condition_discrimination
from visee_optique.uncertainty import PlageParametre

from preuve_image.integrity import empreinte_fichier, DeclarationIntegrite
from preuve_image.metadata import lire_exif_depuis_jpeg, PositionGPS, FicheGrossissement
from preuve_image.metadata import INDISPONIBLE as INDISPONIBLE_B
from preuve_image.chain_of_custody import (
    ElementPreuve, EtatAppareil, ChaineDeCustody, Transfert,
    RegistreConformite, RapportAcquisition, MethodeAcquisition, DossierPreuve,
)
from preuve_image.chain_of_custody import INDISPONIBLE as INDISPONIBLE_CDC

from rapport_expertise.report_builder import (
    INDISPONIBLE, Identification, PosteObservation, Cible, Geometrie,
    SystemePhotographique, Atmosphere, Images, Mesures, Resultat, FicheObservation,
    champs_indisponibles,
)
from rapport_expertise.archive import (
    creer_arborescence, verrouiller_originaux, calculer_manifeste,
    declarer_empreinte_archive, verifier_licence_reprise, ArchiveError,
)

import case_data
from build_demo_image import construire_image_demo

assert INDISPONIBLE == INDISPONIBLE_B == INDISPONIBLE_CDC, "le sentinel doit être identique dans les trois outils"

IDENTIFIANT_DOSSIER = "CAS-DEMO-CHASSIRON-001"
MAINTENANT = datetime.now(timezone.utc)


def calculer_geometrie():
    geo = case_data.vincenty_inverse(
        case_data.CHASSIRON_LAT_DEG, case_data.CHASSIRON_LON_DEG,
        case_data.CORDOUAN_LAT_DEG, case_data.CORDOUAN_LON_DEG,
        a=6_378_137.0, f=1.0 / 298.257222101,
    )
    # az_arrivee est l'azimut AU POINT D'ARRIVÉE (α₂), pas le gisement de
    # retour : il n'est pas employé ici, mais son nom ne doit pas mentir.
    D, az_aller = geo.distance_m, geo.azimut_depart_deg
    lat_moyenne = (case_data.CHASSIRON_LAT_DEG + case_data.CORDOUAN_LAT_DEG) / 2.0
    R_euler = rayon_euler(lat_moyenne, az_aller)
    return D, az_aller, lat_moyenne, R_euler


def calculer_verification_profil():
    """Vérification du profil intermédiaire (Tableau 10, §12.3) à partir de
    points côtiers réels sourcés — voir case_data.calculer_verification_profil
    et la discussion qui l'accompagne dans case_data.py. Retourne la liste de
    résultats (un par point de contrôle)."""
    return case_data.calculer_verification_profil(
        case_data.CHASSIRON_LAT_DEG, case_data.CHASSIRON_LON_DEG,
        case_data.CORDOUAN_LAT_DEG, case_data.CORDOUAN_LON_DEG,
        a=6_378_137.0, f=1.0 / 298.257222101,
    )


def calculer_predictions(D, R_euler):
    cible_geom = CibleGeom(H=case_data.CORDOUAN_HAUTEUR_TOTALE_M, z_b=0.0)
    hyp_k = intervalle_k_faute_de_donnee_resolue(
        [RegimeRefraction.STANDARD, RegimeRefraction.FORTE],
        justification=(
            "Aucune donnée atmosphérique de classe A/B/C disponible pour ce cas de démonstration "
            "(aucune date d'observation réelle, aucune station consultée) ; régimes standard et fort "
            "retenus comme plausibles par défaut en l'absence de tout indice de surface (§21.3) ; "
            "inversion et conduit exclus faute de signature établie (§11.4, §19.4)."
        ),
    )
    modele_S = ModeleSpherique(R=R_euler, cible=cible_geom, hypothese_k=hyp_k)
    modele_P = ModeleSurfacePlane()
    plage_h = PlageParametre(
        "h", 2.0, 8.0,
        source="hauteur d'observateur posée pour la démonstration (dune/plage au pied du phare de Chassiron, non mesurée)",
    )

    enveloppe_S = modele_S.enveloppe_prediction(D, plages_supplementaires=[plage_h], pas_par_parametre=9)
    enveloppe_P = modele_P.enveloppe_prediction(D, plages_supplementaires=[plage_h], pas_par_parametre=9)

    u_f_preenregistre = 0.02  # même hypothèse de pré-enregistrement que le premier cas, pour comparaison directe
    discrimination = condition_discrimination(
        modele_S, modele_P, D, u_f=u_f_preenregistre,
        plages_supplementaires=[plage_h], facteur=5.0, pas_par_parametre=9,
    )
    return cible_geom, hyp_k, enveloppe_S, enveloppe_P, discrimination, u_f_preenregistre, plage_h


def construire_dossier_outil_b(racine_travail: Path):
    chemin_image = racine_travail / "DEMO_diagramme_horizon.jpg"
    construire_image_demo(chemin_image, MAINTENANT)

    empreinte = empreinte_fichier(chemin_image)
    declaration = DeclarationIntegrite(
        fichier=chemin_image.name, empreinte=empreinte, date_calcul=MAINTENANT,
        operateur="Claude (assistant), génération du cas de démonstration",
    )
    exif = lire_exif_depuis_jpeg(chemin_image)

    grossissement = FicheGrossissement(
        focale_optique_reelle=exif.focale_mm,
        focale_equivalente=exif.focale_equivalente_35mm,
        facteur_grossissement=1.0,
        part_optique_vs_numerique=INDISPONIBLE,
        resolution_native=(exif.largeur_px, exif.hauteur_px),
        resolution_fichier=(exif.largeur_px, exif.hauteur_px),
        recadrage_avant_enregistrement=False,
        traitements_computationnels_actifs=INDISPONIBLE,
        autre_etape_scene_vers_fichier="image générée par ordinateur (diagramme), aucune scène réelle capturée",
    )

    element = ElementPreuve(
        identifiant=IDENTIFIANT_DOSSIER,
        description="Diagramme généré par ordinateur (horizon + silhouette schématique), pas une photographie",
        type_support="fichier JPEG généré localement",
        lieu_decouverte="environnement de construction du cas de démonstration (aucune scène réelle)",
        date_heure=MAINTENANT,
        identifie_par="Claude (assistant), pour le compte de l'utilisateur",
        etat_appareil=EtatAppareil.ETEINT,
        justification_etat=(
            "Aucun appareil physique impliqué : fichier généré par script. « Éteint » est choisi par "
            "convention, faute de catégorie « sans objet » dans EtatAppareil."
        ),
        reference_photographie=INDISPONIBLE,
    )
    chaine = ChaineDeCustody(element_id=IDENTIFIANT_DOSSIER, detenteur_initial="script build_demo_image.py")
    chaine.transferer(Transfert(
        horodatage=MAINTENANT, cedant="script build_demo_image.py", receveur="dossier d'archive (§34)",
        raison="dépôt du fichier généré dans l'archive du cas de démonstration",
        lieu="environnement de session cloud",
    ))
    conformite = RegistreConformite(
        auditabilite="script de génération et de calcul déposés dans 60-calcul/, horodatage UTC sur chaque déclaration",
        repetabilite="entrées publiques sourcées + balayage en grille complète (aucun tirage aléatoire) → mêmes résultats",
        reproductibilite="ré-exécutable par un tiers disposant du code des trois outils et de ce script",
        justifiabilite="chaque hypothèse (hauteur d'observateur, intervalle de k, u_f pré-enregistré) est sourcée dans case_data.py/run_case.py",
    )
    acquisition = RapportAcquisition(
        element_id=IDENTIFIANT_DOSSIER,
        methode=MethodeAcquisition.COPIE_LOGIQUE,
        outil="build_demo_image.py (script Python + Pillow)",
        version_outil="1.0",
        empreinte_source=empreinte,
        empreinte_copie=empreinte,
        debut=MAINTENANT,
        fin=datetime.fromtimestamp(MAINTENANT.timestamp() + 1, tz=timezone.utc),
        operateur="Claude (assistant)",
        justification_modification_source=INDISPONIBLE,
    )
    dossier_preuve = DossierPreuve(element=element, chaine=chaine, conformite=conformite, acquisition=acquisition)

    # sensor_forensics.py (PRNU/ELA) est délibérément NON exécuté — voir le
    # premier cas d'étude pour la justification complète : un diagramme généré
    # par ordinateur n'a ni bruit de capteur ni chaîne JPEG réaliste à analyser.

    return chemin_image, declaration, exif, grossissement, dossier_preuve


def construire_fiche(D, azimut, R_euler, cible_geom, hyp_k, enveloppe_S, enveloppe_P,
                      discrimination, u_f, exif, declaration_integrite, grossissement) -> FicheObservation:
    identification = Identification(
        identifiant_dossier=IDENTIFIANT_DOSSIER,
        date_heure_utc_serie=MAINTENANT,
        ecart_horloge_mesure=INDISPONIBLE,
        operateur="Claude (assistant), pour le compte de l'utilisateur — cas de démonstration",
        campagne_et_reference_preenregistrement=(
            "démonstration du pipeline A→B→C, second site (pilier 3 du Carnet de l'observateur) ; "
            "aucun pré-enregistrement formel au sens du §26 — u_f et le facteur du §28.2 sont "
            "déclarés ci-dessous à titre d'hypothèse de démonstration, identiques au premier cas "
            "pour permettre une comparaison directe"
        ),
    )

    position_chassiron = PositionGPS(
        latitude_deg=case_data.CHASSIRON_LAT_DEG, longitude_deg=case_data.CHASSIRON_LON_DEG,
        altitude_m=None, incertitude_m=None,
        source=(
            "position déclarée du repère phare de Chassiron (" + case_data.CHASSIRON_COORDS_SOURCE + ") — "
            "point de référence posé pour la démonstration, pas une mesure GNSS sur site : "
            "aucune observation réelle n'a eu lieu"
        ),
    )
    poste_observation = PosteObservation(
        observateur=INDISPONIBLE,
        coordonnees_et_systeme_reference=position_chassiron,
        incertitude_recepteur=INDISPONIBLE,
        hauteur_ellipsoidale_et_geoide=INDISPONIBLE,
        altitude_sol_ou_niveau_eau="assimilée au niveau moyen de la mer (z=0), hypothèse posée pour la démonstration",
        hauteur_axe_optique="2 à 8 m au-dessus du niveau de la mer, plage balayée (§23.1) — voir 60-calcul/resultats.json",
        altitude_h_retenue_et_incertitude=(
            "traitée comme une plage balayée [2 ; 8] m, pas une valeur ponctuelle ; "
            "aucune incertitude JCGM composée séparément pour ce cas de démonstration"
        ),
    )

    position_cordouan = PositionGPS(
        latitude_deg=case_data.CORDOUAN_LAT_DEG, longitude_deg=case_data.CORDOUAN_LON_DEG,
        altitude_m=None, incertitude_m=None, source=case_data.CORDOUAN_COORDS_SOURCE,
    )
    hauteur_cordouan = GrandeurGeodesique(
        nom="hauteur totale H (phare de Cordouan)", valeur=case_data.CORDOUAN_HAUTEUR_TOTALE_M,
        unite="m", referentiel="hauteur au-dessus du niveau de la mer",
        source=case_data.CORDOUAN_HAUTEUR_SOURCE, incertitude=1.0,
    )
    cible = Cible(
        designation_et_sources="Phare de Cordouan, estuaire de la Gironde — monument historique classé, inscrit UNESCO",
        coordonnees_et_systeme_reference=position_cordouan,
        altitude_base_zb_et_source=(
            "0 m (niveau moyen de la mer), hypothèse simplificatrice posée pour la démonstration — "
            "la base réelle repose sur un plateau rocheux partiellement immergé, non modélisé ici"
        ),
        hauteur_totale_H_et_source=hauteur_cordouan,
        parties_pertinentes_cote_connue=INDISPONIBLE,
        extension_longitudinale=INDISPONIBLE,
    )

    grandeur_distance = GrandeurGeodesique(
        nom="distance géodésique (Chassiron → Cordouan)", valeur=D, unite="m", referentiel="GRS80 (ellipsoïde)",
        source="algorithme de Vincenty (1975), formule inverse — visee_optique.geodesy.vincenty_inverse, à partir des coordonnées sourcées",
        incertitude=15.0,
    )
    grandeur_azimut = GrandeurGeodesique(
        nom="azimut géodésique direct (Chassiron → Cordouan)", valeur=azimut, unite="°", referentiel="GRS80",
        source="même calcul de Vincenty (1975)", incertitude=0.01,
    )
    grandeur_rayon = GrandeurGeodesique(
        nom="rayon de courbure d'Euler", valeur=R_euler, unite="m",
        referentiel="GRS80, latitude moyenne du trajet, azimut ci-dessus",
        source="visee_optique.geodesy.rayon_euler(latitude_moyenne, azimut)", incertitude=0.1,
    )
    geometrie = Geometrie(
        distance_D_algorithme_et_incertitude=grandeur_distance,
        azimut_geodesique=grandeur_azimut,
        rayon_courbure_euler=grandeur_rayon,
        profil_intermediaire_source_et_pas=(
            case_data.PROFIL_CONCLUSION_DEFINITIVE
            + " Détail chiffré (77 points, altimétrie IGN RGE ALTI) dans "
            "30-donnees-externes/profil_intermediaire.md."
        ),
        altitude_maximale_profil_et_marge=(
            "13,76 m au-dessus du niveau de la mer, à 39,8 km de Chassiron (traversée de la "
            "presqu'île d'Arvert) — source : IGN RGE ALTI, voir "
            "30-donnees-externes/profil_intermediaire.md. Bien au-dessus de toute hauteur "
            "d'observateur plausible (h∈[2;8] m) : la ligne de visée y est interceptée par le "
            "relief, pas seulement rasante — marge négative, pas une marge de dégagement."
        ),
    )

    systeme_photo = SystemePhotographique(
        boitier_objectif_numeros_serie=exif,
        focale_reelle_et_equivalente=f"{exif.focale_mm:g} mm réelle / {exif.focale_equivalente_35mm} mm éq. 35 mm (métadonnées EXIF fictives)",
        ouverture_temps_pose_sensibilite=f"f/{exif.ouverture:g}, {exif.temps_pose_s * 1000:.1f} ms, ISO {exif.sensibilite_iso} (fictif)",
        resolution_native_et_pas_photosite=INDISPONIBLE,
        resolution_fichier_final=f"{exif.largeur_px}×{exif.hauteur_px} px",
        grossissement=grossissement,
        recadrage_interne_avant_enregistrement=False,
        traitements_computationnels_actifs=INDISPONIBLE,
        profil_distorsion_et_residuel=INDISPONIBLE,
    )

    atmosphere = Atmosphere(
        temperature_air_par_hauteur=INDISPONIBLE,
        temperature_surface_mer=INDISPONIBLE,
        pression_humidite=INDISPONIBLE,
        profil_vertical_disponible=False,
        classe_de_chaque_donnee={"k": ClasseDonnee.E},
        intervalle_k_retenu_et_justification=hyp_k,
    )

    images = Images(
        nombre_vues_noms_fichiers_empreintes=declaration_integrite,
        preuve_datation_empreintes=INDISPONIBLE,
        classement_chaque_vue=INDISPONIBLE,
        vues_exclues_et_motif=INDISPONIBLE,
        resolution_effective_mesuree=INDISPONIBLE,
        transformations_appliquees_copie="aucune : fichier généré directement, jamais recompressé ni retouché après génération",
    )

    mesures = Mesures(
        caracteristique_designee_et_date=INDISPONIBLE,
        positions_pixels_par_analyste=INDISPONIBLE,
        echelle_par_focale_et_par_reperes=INDISPONIBLE,
        hauteur_visible_et_occultee=INDISPONIBLE,
        fraction_visible_observee_et_incertitude=INDISPONIBLE,
        rapports_hauteur_mesures_et_attendus=INDISPONIBLE,
    )

    motif = (
        f"condition de discrimination du §28.2 SATISFAITE pour cette géométrie — à l'inverse du premier "
        f"cas (La Coubre, 13,1 km) : écart le plus défavorable entre les modèles S et P = "
        f"{discrimination.delta:.3f} (seuil = {discrimination.facteur:g}×u_f = {discrimination.seuil:.3f}, "
        f"avec u_f={u_f:g} pris comme hypothèse de pré-enregistrement, identique au premier cas). "
        f"À {D / 1000:.1f} km, le modèle sphérique prédit une fraction visible nulle sur toute la plage "
        f"plausible de h∈[2;8] m et k∈[{hyp_k.k_min:g};{hyp_k.k_max:g}] (enveloppe S = "
        f"[{enveloppe_S.minimum:.4f};{enveloppe_S.maximum:.4f}]), pendant que le modèle plat prédit "
        "toujours une visibilité totale. Le verdict reste néanmoins déclaré indisponible ci-dessous : "
        "la condition de discrimination n'est qu'un préalable géométrique (§28.2) — trancher réellement "
        "entre les modèles exige une vraie photographie, validée (§18) et mesurée par au moins trois "
        "analystes indépendants (§25), ce qui n'existe pas pour ce cas de démonstration. MAIS CE "
        "PRÉALABLE GÉOMÉTRIQUE EST SANS OBJET ICI : la vérification du profil intermédiaire par "
        "altimétrie officielle IGN (voir Geometrie.profil_intermediaire_source_et_pas ci-dessus et "
        "30-donnees-externes/profil_intermediaire.md) établit que la ligne droite Chassiron→Cordouan "
        "traverse la terre ferme sur environ 20,5 km (l'île d'Oléron elle-même, puis la presqu'île "
        "d'Arvert) — Chassiron ne peut pas voir Cordouan en ligne droite, quel que soit le modèle "
        "retenu. Ce site est donc déclaré INVALIDE pour une vraie campagne de mesure, contrairement à "
        "ce qu'affirmait une première évaluation de ce dossier (fondée sur une comparaison de points "
        "côtiers trop clairsemée pour détecter ce problème)."
    )

    resultat = Resultat(
        fraction_predite_par_modele_avec_enveloppe={"S": enveloppe_S, "P": enveloppe_P},
        ecart_observe_predit_et_incertitude=INDISPONIBLE,
        combinaison_plus_defavorable=discrimination,
        resultat_recherche_regimes=INDISPONIBLE,
        verdict_par_modele=INDISPONIBLE,
        motif_indetermination=motif,
    )

    return FicheObservation(
        identification=identification, poste_observation=poste_observation, cible=cible,
        geometrie=geometrie, systeme_photographique=systeme_photo, atmosphere=atmosphere,
        images=images, mesures=mesures, resultat=resultat,
    )


def _rendre_texte(obj, indent=0) -> str:
    prefixe = "  " * indent
    if dataclasses.is_dataclass(obj) and not isinstance(obj, type):
        lignes = [f"{prefixe}{type(obj).__name__}:"]
        for champ in dataclasses.fields(obj):
            valeur = getattr(obj, champ.name)
            if dataclasses.is_dataclass(valeur) and not isinstance(valeur, type):
                lignes.append(f"{prefixe}  {champ.name}:")
                lignes.append(_rendre_texte(valeur, indent + 2))
            else:
                lignes.append(f"{prefixe}  {champ.name}: {valeur!r}")
        return "\n".join(lignes)
    return f"{prefixe}{obj!r}"


def rendre_fiche_texte(fiche: FicheObservation) -> str:
    blocs = []
    for section in dataclasses.fields(fiche):
        blocs.append(f"=== {section.name} ===")
        blocs.append(_rendre_texte(getattr(fiche, section.name)))
        blocs.append("")
    manquants = champs_indisponibles(fiche)
    blocs.append("=== champs déclarés indisponibles ===")
    if manquants:
        for m in manquants:
            blocs.append(f"  - {m}")
    else:
        blocs.append("  (aucun)")
    return "\n".join(blocs)


def main():
    # Le cas produit sa sortie à côté de lui-même, où qu'il soit cloné.
    racine_projet = Path(__file__).resolve().parent
    racine_sortie = racine_projet / "sortie"
    if racine_sortie.exists():
        shutil.rmtree(racine_sortie)
    racine_sortie.mkdir(parents=True)

    print("1. Géométrie (Outil A — geodesy, geometry, refraction, atmosphere)")
    D, azimut, lat_moyenne, R_euler = calculer_geometrie()
    print(f"   distance = {D:.1f} m, azimut = {azimut:.3f}°, latitude moyenne = {lat_moyenne:.5f}°, R_euler = {R_euler:.1f} m")

    print("1b. Vérification du profil intermédiaire par points côtiers réels (Tableau 10, §12.3)")
    profil_resultats = calculer_verification_profil()
    for r in profil_resultats:
        print(f"    {r['nom']}: écart = {r['ecart_m']:+.0f} m (à {r['distance_le_long_route_m']/1000:.1f} km de Chassiron)")

    print("2. Prédictions et condition de discrimination (Outil A — models, uncertainty)")
    cible_geom, hyp_k, enveloppe_S, enveloppe_P, discrimination, u_f, plage_h = calculer_predictions(D, R_euler)
    print(f"   S: [{enveloppe_S.minimum:.4f} ; {enveloppe_S.maximum:.4f}]  P: [{enveloppe_P.minimum:.4f} ; {enveloppe_P.maximum:.4f}]")
    print(f"   discrimination §28.2 : delta={discrimination.delta:.3e}, seuil={discrimination.seuil:.3f}, satisfaite={discrimination.satisfaite}")

    print("3. Fichier de démonstration et bookkeeping forensique (Outil B — integrity, metadata, chain_of_custody)")
    chemin_image_travail = racine_sortie / "_travail_image"
    chemin_image_travail.mkdir()
    chemin_image, declaration_integrite, exif, grossissement, dossier_preuve = construire_dossier_outil_b(chemin_image_travail)
    print(f"   ISO/CEI 27037 (DossierPreuve) : prêt pour acquisition numérique = {dossier_preuve.pret_pour_acquisition_numerique()}")
    print(f"   image: {chemin_image.name}, SHA-256={declaration_integrite.empreinte}")
    print(f"   EXIF (fictif): fabricant={exif.fabricant!r}, modele={exif.modele!r}, gps={exif.gps}")

    print("4. Fiche standard d'observation (Outil C — report_builder, §33)")
    fiche = construire_fiche(
        D, azimut, R_euler, cible_geom, hyp_k, enveloppe_S, enveloppe_P,
        discrimination, u_f, exif, declaration_integrite, grossissement,
    )
    manquants = champs_indisponibles(fiche)
    print(f"   {len(manquants)} champs déclarés indisponibles (liste dans la fiche)")

    print("5. Archive (Outil C — archive, §34)")
    racine_archive = creer_arborescence(racine_sortie, IDENTIFIANT_DOSSIER)

    (racine_archive / "00-preenregistrement" / "plan.md").write_text(
        "# Plan de démonstration — CAS-DEMO-CHASSIRON-001\n\n"
        f"Rédigé le {MAINTENANT.isoformat()}.\n\n"
        "Second cas d'étude, même cible que CAS-DEMO-CORDOUAN-001 (phare de Cordouan), poste de "
        "référence différent (phare de Chassiron, 54,4 km au lieu de 13,1 km). Site choisi "
        "spécifiquement parce que le calcul préalable montre que la condition de discrimination du "
        "§28.2 y est satisfaite, contrairement au premier cas.\n\n"
        "Ce n'est PAS un pré-enregistrement au sens du §26 : aucune campagne de mesure réelle n'est "
        "prévue. Les hypothèses ci-dessous sont déclarées pour que le calcul du §28.2 puisse "
        "s'exécuter avec des valeurs explicites, identiques au premier cas pour permettre une "
        "comparaison directe.\n\n"
        f"- Cible : phare de Cordouan, H = {case_data.CORDOUAN_HAUTEUR_TOTALE_M:g} m (voir 30-donnees-externes/).\n"
        f"- Point de référence : phare de Chassiron, île d'Oléron (voir 30-donnees-externes/).\n"
        f"- Hauteur d'observateur h : plage [2 ; 8] m, balayée (§23.1), non mesurée.\n"
        f"- Intervalle de réfraction k : [{hyp_k.k_min:g} ; {hyp_k.k_max:g}] "
        "(régimes standard + fort, §21.3, faute de donnée atmosphérique résolue).\n"
        f"- Incertitude de mesure anticipée u_f : {u_f:g} (hypothèse de démonstration, identique au premier cas).\n"
        "- Facteur de discrimination (§28.2) : 5 (valeur par défaut de condition_discrimination).\n",
        encoding="utf-8",
    )

    dossier_10 = racine_archive / "10-originaux"
    shutil.copy2(chemin_image, dossier_10 / chemin_image.name)
    (dossier_10 / "AVERTISSEMENT.md").write_text(
        "# Avertissement\n\n"
        "Le fichier de ce répertoire N'EST PAS une photographie. C'est un diagramme "
        "généré par ordinateur, utilisé uniquement pour exercer mécaniquement les outils "
        "d'Outil B (intégrité, lecture EXIF, chaîne de détention) sur un fichier réel. "
        "Ses métadonnées EXIF sont fictives par construction (fabricant « DEMO-NON-REEL ») "
        "et ne portent aucune position GPS. Voir build_demo_image.py dans 60-calcul/.\n",
        encoding="utf-8",
    )

    (racine_archive / "11-empreintes" / "declaration_image.json").write_text(
        json.dumps(dataclasses.asdict(declaration_integrite), default=str, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    (racine_archive / "11-empreintes" / "dossier_preuve_iso27037.json").write_text(
        json.dumps(
            {
                "element": dataclasses.asdict(dossier_preuve.element),
                "chaine_detenteur_actuel": dossier_preuve.chaine.detenteur_actuel,
                "chaine_historique": [dataclasses.asdict(t) for t in dossier_preuve.chaine.historique],
                "conformite": dataclasses.asdict(dossier_preuve.conformite),
                "acquisition": dataclasses.asdict(dossier_preuve.acquisition) if dossier_preuve.acquisition else None,
                "pret_pour_acquisition_numerique": dossier_preuve.pret_pour_acquisition_numerique(),
            },
            default=str, ensure_ascii=False, indent=2,
        ),
        encoding="utf-8",
    )

    (racine_archive / "20-fiche" / "fiche_observation.txt").write_text(rendre_fiche_texte(fiche), encoding="utf-8")

    (racine_archive / "30-donnees-externes" / "sources.md").write_text(
        "# Données publiques sourcées\n\n"
        f"## Cible — phare de Cordouan (identique au premier cas d'étude)\n"
        f"- Coordonnées : {case_data.CORDOUAN_LAT_DEG:.6f}°N, {case_data.CORDOUAN_LON_DEG:.6f}°E\n"
        f"  Source : {case_data.CORDOUAN_COORDS_SOURCE}\n"
        f"- Hauteur totale : {case_data.CORDOUAN_HAUTEUR_TOTALE_M} m\n"
        f"  Source : {case_data.CORDOUAN_HAUTEUR_SOURCE}\n\n"
        f"## Point de référence — phare de Chassiron\n"
        f"- Coordonnées : {case_data.CHASSIRON_LAT_DEG:.6f}°N, {case_data.CHASSIRON_LON_DEG:.6f}°E\n"
        f"  Source : {case_data.CHASSIRON_COORDS_SOURCE}\n\n"
        "## Site écarté et pourquoi\n"
        "Phare de l'Île d'Aix (46,0099°N, 1,1778°E, même base) est à 47,1 km de Cordouan et "
        "satisferait lui aussi le §28.2, mais son azimut depuis Cordouan est quasi plein nord "
        "(359,6°) : la ligne de visée croiserait très probablement l'île d'Oléron elle-même. Voir "
        "case_data.py pour le raisonnement complet.\n\n"
        "## Profil intermédiaire — vérifié par altimétrie officielle IGN\n"
        "Vérification DÉFINITIVE effectuée le 2026-09-03 à partir du RGE ALTI de l'IGN (API "
        "Géoplateforme, donnée souveraine officielle) : voir le relevé complet (77 points) et la "
        "conclusion dans 30-donnees-externes/profil_intermediaire.md. RÉSULTAT : la ligne traverse "
        "la terre ferme à deux reprises (l'île d'Oléron elle-même sur ses 15 premiers km, puis la "
        "presqu'île d'Arvert sur environ 5,5 km vers le 40e km), pour un total d'environ 20,5 km sur "
        "54,4 km. CE SITE NE SATISFAIT PAS l'exigence d'une visée directe sur mer (Tableau 10, "
        "§12.3) : Chassiron ne peut pas voir Cordouan en ligne droite, quel que soit le modèle de "
        "courbure retenu.\n\n"
        "## Algorithme géodésique\n"
        "Vincenty (1975), formule inverse, ellipsoïde GRS80 — voir visee_optique.geodesy.vincenty_inverse "
        "dans 60-calcul/case_data.py.\n",
        encoding="utf-8",
    )

    lignes_tableau_profil = "\n".join(
        f"| {r['nom']} | {r['distance_le_long_route_m']/1000:.2f} | {r['lat_ref']:.5f} | {r['lon_ref']:.5f} | "
        f"{r['lon_route_meme_latitude']:.5f} | {r['ecart_m']:+.0f} | {r['source']} |"
        for r in profil_resultats
    )
    lignes_elevations = "\n".join(
        f"| {d/1000:.2f} | {('mer (hors couverture terrestre)' if elev is None else f'{elev:+.2f}')} |"
        for d, elev in case_data.PROFIL_ELEVATIONS_IGN
    )
    lignes_croisements = "\n".join(
        f"| {nom} | {d0/1000:.2f} – {d1/1000:.2f} | {(d1 - d0)/1000:.2f} | {detail} |"
        for nom, d0, d1, detail in case_data.PROFIL_CROISEMENTS_TERRE
    )
    (racine_archive / "30-donnees-externes" / "profil_intermediaire.md").write_text(
        "# Vérification du profil intermédiaire (Tableau 10, §12.3)\n\n"
        "## Première passe (dépassée) — comparaison à des points côtiers nommés\n\n"
        "Un premier contrôle, le 2026-09-03, comparait la route à quatre points côtiers réels "
        "individuellement sourcés (Mapcarta/OpenStreetMap), un par latitude testée. Il concluait à "
        "un dégagement confortable de l'île d'Oléron et à un écart non tranché d'environ 150 m près "
        "de la Pointe de la Coubre. Cette méthode s'est révélée INSUFFISANTE : elle ne peut pas "
        "détecter un empiètement sur la terre ferme à une longitude différente de celle des points "
        "testés — en particulier près du point de départ lui-même, qui n'avait pas été testé. Détail "
        "conservé ci-dessous pour traçabilité (§31 esprit : montrer la correction, pas l'effacer).\n\n"
        "| Point de contrôle | distance le long de la route (km) | latitude réf. | longitude réf. | "
        "longitude de la route à cette latitude | écart (m) | source |\n"
        "|---|---|---|---|---|---|---|\n"
        f"{lignes_tableau_profil}\n\n"
        f"{case_data.PROFIL_BANC_COUBRE_NOTE}\n\n"
        f"{case_data.PROFIL_CONCLUSION_PREMIERE_PASSE}\n\n"
        "## Vérification définitive — altimétrie officielle IGN (RGE ALTI)\n\n"
        "Contrôle réalisé le 2026-09-03 en réponse à une demande explicite de vérification sur une "
        "vraie carte marine SHOM. Le visualiseur cartographique du SHOM n'est pas atteignable depuis "
        "cette session (application interactive en JavaScript, non restituable par les outils de "
        "récupération web disponibles ici). L'API REST d'altimétrie de la Géoplateforme IGN "
        "(https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json, ressource "
        "`ign_rge_alti_wld`), elle, l'est : c'est une donnée souveraine officielle française — une "
        "autorité équivalente à un modèle numérique de terrain officiel, même si ce n'est pas la vue "
        "SHOM elle-même. Le service renvoie -99999 (à l'arrondi près) pour tout point hors de sa "
        "couverture terrestre, c'est-à-dire en mer. Élévation interrogée tous les 1 km le long de la "
        "géodésique (Vincenty direct, GRS80), affinée à 50–200 m près des transitions terre/mer.\n\n"
        "### Relevé complet (77 points)\n\n"
        "| distance depuis Chassiron (km) | élévation |\n"
        "|---|---|\n"
        f"{lignes_elevations}\n\n"
        "### Traversées de terre ferme identifiées\n\n"
        "| zone traversée | intervalle (km) | longueur (km) | détail de la transition |\n"
        "|---|---|---|---|\n"
        f"{lignes_croisements}\n\n"
        "## Conclusion\n\n"
        f"{case_data.PROFIL_CONCLUSION_DEFINITIVE}\n",
        encoding="utf-8",
    )

    (racine_archive / "40-controles" / "AVERTISSEMENT.md").write_text(
        "# Avertissement\n\nAucun contrôle de mire, de distorsion, de stabilité ou de "
        "cohérence entre focales n'a été réalisé : il n'existe pas d'appareil réel pour "
        "ce cas de démonstration (Tableau 17, §24).\n", encoding="utf-8",
    )
    (racine_archive / "50-mesures" / "AVERTISSEMENT.md").write_text(
        "# Avertissement\n\nAucune mesure d'analyste n'a été réalisée : aucune photographie "
        "réelle n'existe pour ce cas de démonstration (§19).\n", encoding="utf-8",
    )

    # Le §34 veut le code dans 60-calcul/. build_demo_image.py est passé dans
    # exemples-cas-etudes/commun/ quand les quatre cas ont cessé d'en porter
    # chacun une copie : on le prend là où il est, pas là où il était.
    commun = racine_projet.parent / "commun"
    for source in (racine_projet / "case_data.py",
                   racine_projet / "run_case.py",
                   commun / "build_demo_image.py",
                   commun / "bootstrap.py"):
        shutil.copy2(source, racine_archive / "60-calcul" / source.name)
    resultats_json = {
        "distance_m": D, "azimut_deg": azimut, "latitude_moyenne_deg": lat_moyenne, "rayon_euler_m": R_euler,
        "k_min": hyp_k.k_min, "k_max": hyp_k.k_max,
        "enveloppe_S": {"min": enveloppe_S.minimum, "max": enveloppe_S.maximum, "n_evaluations": enveloppe_S.n_evaluations},
        "enveloppe_P": {"min": enveloppe_P.minimum, "max": enveloppe_P.maximum, "n_evaluations": enveloppe_P.n_evaluations},
        "discrimination_delta": discrimination.delta, "discrimination_seuil": discrimination.seuil,
        "discrimination_satisfaite": discrimination.satisfaite, "u_f_preenregistre": u_f,
        "discrimination_combinaison_defavorable": dict(discrimination.combinaison_defavorable),
        "verification_profil_premiere_passe_points_cotiers": [
            {k: v for k, v in r.items()} for r in profil_resultats
        ],
        "verification_profil_definitive_ign_rge_alti": {
            "elevations_m_par_distance_m": dict(case_data.PROFIL_ELEVATIONS_IGN),
            "croisements_terre": [
                {"zone": nom, "debut_m": d0, "fin_m": d1, "detail": detail}
                for nom, d0, d1, detail in case_data.PROFIL_CROISEMENTS_TERRE
            ],
            "longueur_totale_sur_terre_m": sum(
                d1 - d0 for _, d0, d1, _ in case_data.PROFIL_CROISEMENTS_TERRE
            ),
            "site_valide_pour_visee_directe_sur_mer": False,
        },
    }
    (racine_archive / "60-calcul" / "resultats.json").write_text(
        json.dumps(resultats_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (racine_archive / "70-rapport" / "synthese.md").write_text(
        "# Synthèse — CAS-DEMO-CHASSIRON-001\n\n"
        "Second cas bout-en-bout à travers Outil A, Outil B et Outil C, même cible que "
        "CAS-DEMO-CORDOUAN-001 (phare de Cordouan), poste de référence différent (phare de "
        "Chassiron, 54,4 km). Aucune photographie réelle n'a été mesurée : voir "
        "10-originaux/AVERTISSEMENT.md.\n\n"
        "**CORRECTION IMPORTANTE (2026-09-03) :** ce dossier a d'abord conclu que ce site était "
        "« un candidat sérieux pour une vraie campagne de mesure ». Une vérification plus poussée du "
        "profil intermédiaire, demandée explicitement et menée avec l'altimétrie officielle IGN "
        "(RGE ALTI), a montré que c'est FAUX : la ligne droite Chassiron→Cordouan traverse la terre "
        "ferme sur environ 20,5 km au total (l'île d'Oléron elle-même sur ses 15 premiers kilomètres, "
        "puis la presqu'île d'Arvert vers le 40e kilomètre, sur environ 5,5 km). Le phare de Chassiron "
        "ne peut donc pas voir le phare de Cordouan en ligne droite, quel que soit le modèle de "
        "courbure retenu — bien avant toute question de courbure ou de réfraction. **Ce site est "
        "déclaré INVALIDE pour une vraie campagne de mesure.** Voir "
        "30-donnees-externes/profil_intermediaire.md pour le détail complet et la correction "
        "assumée.\n\n"
        f"**Constat géométrique (reste vrai, mais sans objet pour ce site) :** la condition de "
        f"discrimination du §28.2 EST satisfaite à {D / 1000:.1f} km pour la plage h∈[2;8] m et "
        f"k∈[{hyp_k.k_min:g};{hyp_k.k_max:g}] (écart le plus défavorable {discrimination.delta:.3f}, "
        f"au-dessus du seuil {discrimination.seuil:.3f}) — le calcul lui-même reste correct comme "
        "exercice géométrique abstrait sur cette distance, mais il ne s'applique à aucune mesure "
        "réalisable depuis Chassiron. Voir 20-fiche/fiche_observation.txt pour le détail et "
        "60-calcul/resultats.json pour les valeurs numériques.\n\n"
        "Déclaration d'intérêts : sans objet (démonstration solitaire, pas un examen commandé).\n",
        encoding="utf-8",
    )

    (racine_archive / "90-journal" / "journal.md").write_text(
        "# Journal des opérations — CAS-DEMO-CHASSIRON-001\n\n"
        f"- {MAINTENANT.isoformat()} — sélection du site (Chassiron retenu, Île d'Aix écartée — voir case_data.py)\n"
        f"- {MAINTENANT.isoformat()} — calcul géodésique (Vincenty, GRS80) entre les coordonnées sourcées\n"
        f"- {MAINTENANT.isoformat()} — première passe de vérification du profil intermédiaire par "
        "points côtiers réels sourcés (Tableau 10, §12.3) ; Pointe de la Coubre non tranchée (écart "
        "~150 m) — méthode ensuite jugée insuffisante\n"
        f"- {MAINTENANT.isoformat()} — vérification DÉFINITIVE du profil intermédiaire par "
        "altimétrie officielle IGN (RGE ALTI, API Géoplateforme), sur demande explicite d'une "
        "vérification par carte marine SHOM (non atteignable depuis cette session) ; RÉSULTAT : deux "
        "traversées de terre ferme totalisant ~20,5 km — site déclaré INVALIDE pour une visée directe "
        "sur mer, corrigeant la conclusion de la première passe\n"
        f"- {MAINTENANT.isoformat()} — balayage de sensibilité des modèles S et P (§23.1)\n"
        f"- {MAINTENANT.isoformat()} — calcul de la condition de discrimination (§28.2)\n"
        f"- {MAINTENANT.isoformat()} — génération du fichier de démonstration (diagramme, EXIF fictif)\n"
        f"- {MAINTENANT.isoformat()} — calcul de l'empreinte SHA-256 du fichier de démonstration\n"
        f"- {MAINTENANT.isoformat()} — construction de la fiche standard d'observation (§33)\n"
        f"- {MAINTENANT.isoformat()} — création de l'arborescence d'archive (§34)\n"
        f"- {MAINTENANT.isoformat()} — verrouillage (chmod) de 10-originaux/\n"
        f"- {MAINTENANT.isoformat()} — calcul du manifeste SHA256SUMS et de son empreinte\n",
        encoding="utf-8",
    )

    (racine_archive / "licence.txt").write_text(
        verifier_licence_reprise("CC-BY-4.0") + "\n"
        "Licence déclarée pour ce cas de démonstration (§34 : « publiée sous une licence "
        "permettant la reprise et la redémarche »). Le protocole ne nomme aucune licence "
        "précise ; CC-BY-4.0 est un choix de l'opérateur, pas une exigence du protocole.\n",
        encoding="utf-8",
    )

    print("   verrouillage de 10-originaux/ (limite de permissions Unix assumée, cf. docstring d'archive.py)")
    verrouiller_originaux(dossier_10)

    manifeste = calculer_manifeste(racine_archive)
    declaration_archive = declarer_empreinte_archive(
        manifeste, operateur="Claude (assistant)", date_calcul=MAINTENANT,
    )
    (racine_archive / "SHA256SUMS").write_text(
        "\n".join(f"{empreinte}  {chemin}" for chemin, empreinte in sorted(manifeste.items())) + "\n",
        encoding="utf-8",
    )
    (racine_archive / "SHA256SUMS.empreinte.txt").write_text(
        f"{declaration_archive.empreinte}  (empreinte du manifeste SHA256SUMS entier, §34)\n"
        f"calculée le {declaration_archive.date_calcul.isoformat()} par {declaration_archive.operateur}\n"
        "déclaration de l'opérateur seule — non datée par un tiers (voir preuve_image.integrity.statut_horodatage)\n",
        encoding="utf-8",
    )
    print(f"   manifeste : {len(manifeste)} fichiers, empreinte de l'archive = {declaration_archive.empreinte}")

    shutil.rmtree(chemin_image_travail)

    chemin_zip = shutil.make_archive(str(racine_projet / IDENTIFIANT_DOSSIER), "zip", root_dir=racine_sortie, base_dir=racine_archive.name)
    print(f"6. Archive zippée : {chemin_zip}")
    return chemin_zip


if __name__ == "__main__":
    main()
