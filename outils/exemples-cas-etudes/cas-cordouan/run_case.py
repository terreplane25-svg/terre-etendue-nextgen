"""
run_case.py — premier cas réel bout-en-bout, à travers visee_optique (Outil A),
preuve_image (Outil B) et rapport_expertise (Outil C).

CE QUE CE CAS EST : une géométrie réelle (deux phares publics, coordonnées et
hauteurs sourcées, cf. case_data.py) traversant tout le pipeline jusqu'à une
archive §34 publiable — la « prochaine étape » proposée au pilier 3 du
Carnet de l'observateur.

CE QUE CE CAS N'EST PAS : une expertise. Aucune photographie réelle n'a été
prise ni mesurée. Le fichier image utilisé pour exercer Outil B est un
diagramme généré par ordinateur, explicitement étiqueté comme tel à chaque
étape (voir build_demo_image.py). Le résultat marquant de ce cas n'est
d'ailleurs pas une fraction visible mesurée, mais un constat géométrique :
la condition de discrimination du §28.2 n'est PAS satisfaite pour cette
configuration (voir plus bas) — la géométrie elle-même dit qu'une mesure sur
site ne permettrait pas ici de trancher entre les deux modèles, avant même
d'envisager une prise de vue.
"""

import dataclasses
import json
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, "/home/claude/visee-optique")
sys.path.insert(0, "/home/claude/preuve-image")
sys.path.insert(0, "/home/claude/rapport-expertise")

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

IDENTIFIANT_DOSSIER = "CAS-DEMO-CORDOUAN-001"
MAINTENANT = datetime.now(timezone.utc)


def calculer_geometrie():
    D, az_aller, _az_retour = case_data.vincenty_inverse(
        case_data.COUBRE_LAT_DEG, case_data.COUBRE_LON_DEG,
        case_data.CORDOUAN_LAT_DEG, case_data.CORDOUAN_LON_DEG,
        a=6_378_137.0, f=1.0 / 298.257222101,
    )
    lat_moyenne = (case_data.COUBRE_LAT_DEG + case_data.CORDOUAN_LAT_DEG) / 2.0
    R_euler = rayon_euler(lat_moyenne, az_aller)
    return D, az_aller, lat_moyenne, R_euler


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
        source="hauteur d'observateur posée pour la démonstration (dune/plage au pied du phare de la Coubre, non mesurée)",
    )

    enveloppe_S = modele_S.enveloppe_prediction(D, plages_supplementaires=[plage_h], pas_par_parametre=9)
    enveloppe_P = modele_P.enveloppe_prediction(D, plages_supplementaires=[plage_h], pas_par_parametre=9)

    u_f_preenregistre = 0.02  # hypothèse de pré-enregistrement, cf. AVERTISSEMENT ci-dessous
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

    # sensor_forensics.py (PRNU/ELA) est délibérément NON exécuté : ces analyses
    # supposent un capteur réel dont le bruit spatial fixe (PRNU) ou une chaîne
    # de compression JPEG réaliste (ELA) sont significatifs. Un diagramme généré
    # par ordinateur n'a ni l'un ni l'autre — les exécuter produirait un résultat
    # techniquement calculable mais dépourvu de sens, et le présenter serait
    # trompeur. Cette omission est documentée ici plutôt que masquée.

    return chemin_image, declaration, exif, grossissement, dossier_preuve


def construire_fiche(D, azimut, R_euler, cible_geom, hyp_k, enveloppe_S, enveloppe_P,
                      discrimination, u_f, exif, declaration_integrite, grossissement) -> FicheObservation:
    identification = Identification(
        identifiant_dossier=IDENTIFIANT_DOSSIER,
        date_heure_utc_serie=MAINTENANT,
        ecart_horloge_mesure=INDISPONIBLE,
        operateur="Claude (assistant), pour le compte de l'utilisateur — cas de démonstration",
        campagne_et_reference_preenregistrement=(
            "démonstration du pipeline A→B→C (pilier 3 du Carnet de l'observateur) ; "
            "aucun pré-enregistrement formel au sens du §26 — u_f et le facteur du §28.2 sont "
            "déclarés ci-dessous à titre d'hypothèse de démonstration, pas déposés avant une campagne réelle"
        ),
    )

    position_coubre = PositionGPS(
        latitude_deg=case_data.COUBRE_LAT_DEG, longitude_deg=case_data.COUBRE_LON_DEG,
        altitude_m=None, incertitude_m=None,
        source=(
            "position déclarée du repère phare de la Coubre (" + case_data.COUBRE_COORDS_SOURCE + ") — "
            "point de référence posé pour la démonstration, pas une mesure GNSS sur site : "
            "aucune observation réelle n'a eu lieu"
        ),
    )
    poste_observation = PosteObservation(
        observateur=INDISPONIBLE,
        coordonnees_et_systeme_reference=position_coubre,
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
        nom="distance géodésique (La Coubre → Cordouan)", valeur=D, unite="m", referentiel="GRS80 (ellipsoïde)",
        source="algorithme de Vincenty (1975), formule inverse — case_data.vincenty_inverse, à partir des coordonnées sourcées",
        incertitude=10.0,
    )
    grandeur_azimut = GrandeurGeodesique(
        nom="azimut géodésique direct (La Coubre → Cordouan)", valeur=azimut, unite="°", referentiel="GRS80",
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
        profil_intermediaire_source_et_pas=INDISPONIBLE,
        altitude_maximale_profil_et_marge=INDISPONIBLE,
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
        f"condition de discrimination du §28.2 NON satisfaite pour cette géométrie : "
        f"écart le plus défavorable entre les modèles S et P = {discrimination.delta:.2e} "
        f"(seuil = {discrimination.facteur:g}×u_f = {discrimination.seuil:.3f}, avec u_f={u_f:g} "
        f"pris comme hypothèse de pré-enregistrement pour cette démonstration). "
        f"À {D / 1000:.1f} km, les deux modèles prédisent une fraction visible quasi identique sur toute "
        f"la plage plausible de h∈[2;8] m et k∈[{hyp_k.k_min:g};{hyp_k.k_max:g}] : une mesure serait classée "
        "indéterminée quel que soit son résultat, avant même d'être réalisée (§28.3, premier critère). "
        "Aucune image réelle n'a par ailleurs été mesurée pour ce cas de démonstration."
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
    racine_projet = Path("/home/claude/cas-cordouan")
    racine_sortie = racine_projet / "sortie"
    if racine_sortie.exists():
        shutil.rmtree(racine_sortie)
    racine_sortie.mkdir(parents=True)

    print("1. Géométrie (Outil A — geodesy, geometry, refraction, atmosphere)")
    D, azimut, lat_moyenne, R_euler = calculer_geometrie()
    print(f"   distance = {D:.1f} m, azimut = {azimut:.3f}°, latitude moyenne = {lat_moyenne:.5f}°, R_euler = {R_euler:.1f} m")

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
        "# Plan de démonstration — CAS-DEMO-CORDOUAN-001\n\n"
        f"Rédigé le {MAINTENANT.isoformat()}.\n\n"
        "Ce n'est PAS un pré-enregistrement au sens du §26 : aucune campagne de mesure "
        "réelle n'est prévue. Les hypothèses ci-dessous sont déclarées ici pour que le "
        "calcul du §28.2 (condition de discrimination) puisse s'exécuter avec des valeurs "
        "explicites plutôt qu'ad hoc, exactement comme le §26 l'exigerait avant une vraie "
        "campagne.\n\n"
        f"- Cible : phare de Cordouan (voir 30-donnees-externes/).\n"
        f"- Point de référence : phare de la Coubre (voir 30-donnees-externes/).\n"
        f"- Hauteur d'observateur h : plage [2 ; 8] m, balayée (§23.1), non mesurée.\n"
        f"- Intervalle de réfraction k : [{hyp_k.k_min:g} ; {hyp_k.k_max:g}] "
        "(régimes standard + fort, §21.3, faute de donnée atmosphérique résolue).\n"
        f"- Incertitude de mesure anticipée u_f : {u_f:g} (hypothèse de démonstration).\n"
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
        f"## Cible — phare de Cordouan\n"
        f"- Coordonnées : {case_data.CORDOUAN_LAT_DEG:.6f}°N, {case_data.CORDOUAN_LON_DEG:.6f}°E\n"
        f"  Source : {case_data.CORDOUAN_COORDS_SOURCE}\n"
        f"- Hauteur totale : {case_data.CORDOUAN_HAUTEUR_TOTALE_M} m\n"
        f"  Source : {case_data.CORDOUAN_HAUTEUR_SOURCE}\n\n"
        f"## Point de référence — phare de la Coubre\n"
        f"- Coordonnées : {case_data.COUBRE_LAT_DEG:.6f}°N, {case_data.COUBRE_LON_DEG:.6f}°E\n"
        f"  Source : {case_data.COUBRE_COORDS_SOURCE}\n"
        f"- Hauteur de tour (non utilisée dans le calcul, pour information) : {case_data.COUBRE_HAUTEUR_TOUR_M} m\n"
        f"  Divergence de source non résolue : {case_data.COUBRE_HAUTEUR_SOURCE_DIVERGENTE}\n\n"
        "## Algorithme géodésique\n"
        "Vincenty (1975), formule inverse, ellipsoïde GRS80 — voir case_data.vincenty_inverse "
        "dans 60-calcul/case_data.py.\n",
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

    for nom_fichier in ("case_data.py", "build_demo_image.py", "run_case.py"):
        shutil.copy2(racine_projet / nom_fichier, racine_archive / "60-calcul" / nom_fichier)
    resultats_json = {
        "distance_m": D, "azimut_deg": azimut, "latitude_moyenne_deg": lat_moyenne, "rayon_euler_m": R_euler,
        "k_min": hyp_k.k_min, "k_max": hyp_k.k_max,
        "enveloppe_S": {"min": enveloppe_S.minimum, "max": enveloppe_S.maximum, "n_evaluations": enveloppe_S.n_evaluations},
        "enveloppe_P": {"min": enveloppe_P.minimum, "max": enveloppe_P.maximum, "n_evaluations": enveloppe_P.n_evaluations},
        "discrimination_delta": discrimination.delta, "discrimination_seuil": discrimination.seuil,
        "discrimination_satisfaite": discrimination.satisfaite, "u_f_preenregistre": u_f,
    }
    (racine_archive / "60-calcul" / "resultats.json").write_text(
        json.dumps(resultats_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (racine_archive / "70-rapport" / "synthese.md").write_text(
        "# Synthèse — CAS-DEMO-CORDOUAN-001\n\n"
        "Premier cas bout-en-bout à travers Outil A, Outil B et Outil C, construit à partir "
        "de données publiques sourcées (voir 30-donnees-externes/). Aucune photographie "
        "réelle n'a été mesurée : voir 10-originaux/AVERTISSEMENT.md.\n\n"
        f"**Constat principal :** la condition de discrimination du §28.2 n'est pas satisfaite "
        f"à {D / 1000:.1f} km pour la plage h∈[2;8] m et k∈[{hyp_k.k_min:g};{hyp_k.k_max:g}] "
        f"(écart le plus défavorable {discrimination.delta:.2e}, sous le seuil {discrimination.seuil:.3f}). "
        "Ce site, à cette distance, ne permettrait pas de distinguer les modèles S et P même avec "
        "une mesure de qualité parfaite — un résultat du calcul géométrique seul, avant toute image. "
        "Voir 20-fiche/fiche_observation.txt pour le détail des neuf blocs et 60-calcul/resultats.json "
        "pour les valeurs numériques.\n\n"
        "Déclaration d'intérêts : sans objet (démonstration solitaire, pas un examen commandé).\n",
        encoding="utf-8",
    )

    (racine_archive / "90-journal" / "journal.md").write_text(
        "# Journal des opérations — CAS-DEMO-CORDOUAN-001\n\n"
        f"- {MAINTENANT.isoformat()} — calcul géodésique (Vincenty, GRS80) entre les coordonnées sourcées\n"
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
