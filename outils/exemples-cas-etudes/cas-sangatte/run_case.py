"""
run_case.py — troisième cas réel bout-en-bout, à travers visee_optique (Outil A),
preuve_image (Outil B) et rapport_expertise (Outil C).

Poste de référence : Digue de Sangatte (Pas-de-Calais), un point d'altitude sourcée
quasi nulle (2 m, Cirkwi) sur le cordon dunaire bas entre Cap Blanc-Nez et Cap
Gris-Nez. Cible : phare de South Foreland / falaises de Douvres (White Cliffs of
Dover), 110 m au-dessus du niveau de la mer. Distance 35,6 km.

CE QUE CE CAS EST : un troisième point du même exercice, choisi cette fois selon une
discipline inversée par rapport aux deux premiers — le profil intermédiaire a été
vérifié par altimétrie officielle IGN (RGE ALTI) AVANT la construction de cette
archive, et non après coup. C'est la leçon tirée directement de la correction du
second cas (CAS-DEMO-CHASSIRON-001, dossier cas-chassiron/) : ce dossier-là avait
d'abord conclu à tort qu'un simple raisonnement géographique suffisait, avant qu'une
vérification altimétrique demandée après coup ne révèle deux traversées de terre
ferme totalisant 20,5 km. Ici, le pré-écran (outils-verification/profil_altimetrique.py)
a d'abord servi à ÉCARTER deux candidats plausibles en apparence (Cap Gris-Nez↔South
Foreland, Cordouan↔Cap Ferret — voir case_data.py et
outils-verification/rapport_selection_site3.md) avant de retenir Sangatte↔South
Foreland, puis à le CONFIRMER à deux résolutions (2 km sur le corps de la route,
500 m aux deux extrémités, sur demande explicite de resserrement de la maille
côtière) avant d'écrire la moindre ligne de cette archive.

CE QUE CE CAS N'EST PAS : une expertise, ni la preuve que la Terre est ronde ou
plate. Aucune photographie réelle n'a été prise ni mesurée depuis Sangatte. Le
résultat marquant est double : (1) la condition de discrimination du §28.2 est
satisfaite à cette distance — le modèle sphérique prédit une fraction visible
partielle et nettement différente du modèle plat, qui prédit toujours une
visibilité totale ; (2) et, à la différence du cas Chassiron, ce préalable
géométrique N'EST PAS sans objet ici : le profil intermédiaire est confirmé
100 % maritime, donc une vraie campagne de mesure y serait physiquement possible
(sous réserve des affinements listés plus bas).
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

IDENTIFIANT_DOSSIER = "CAS-DEMO-SANGATTE-001"
MAINTENANT = datetime.now(timezone.utc)


def calculer_geometrie():
    geo = case_data.vincenty_inverse(
        case_data.SANGATTE_LAT_DEG, case_data.SANGATTE_LON_DEG,
        case_data.SOUTHFORELAND_LAT_DEG, case_data.SOUTHFORELAND_LON_DEG,
        a=6_378_137.0, f=1.0 / 298.257222101,
    )
    # az_arrivee est l'azimut AU POINT D'ARRIVÉE (α₂), pas le gisement de
    # retour : il n'est pas employé ici, mais son nom ne doit pas mentir.
    D, az_aller = geo.distance_m, geo.azimut_depart_deg
    lat_moyenne = (case_data.SANGATTE_LAT_DEG + case_data.SOUTHFORELAND_LAT_DEG) / 2.0
    R_euler = rayon_euler(lat_moyenne, az_aller)
    return D, az_aller, lat_moyenne, R_euler


def calculer_predictions(D, R_euler):
    cible_geom = CibleGeom(H=case_data.SOUTHFORELAND_HAUTEUR_TOTALE_M, z_b=0.0)
    hyp_k = intervalle_k_faute_de_donnee_resolue(
        [RegimeRefraction.STANDARD, RegimeRefraction.FORTE],
        justification=(
            "Aucune donnée atmosphérique de classe A/B/C disponible pour ce cas de démonstration "
            "(aucune date d'observation réelle, aucune station consultée) ; régimes standard et fort "
            "retenus comme plausibles par défaut en l'absence de tout indice de surface (§21.3) ; "
            "inversion et conduit exclus faute de signature établie (§11.4, §19.4) — même hypothèse "
            "que pour les deux premiers cas d'étude, pour permettre une comparaison directe."
        ),
    )
    modele_S = ModeleSpherique(R=R_euler, cible=cible_geom, hypothese_k=hyp_k)
    modele_P = ModeleSurfacePlane()
    plage_h = PlageParametre(
        "h", 2.0, 8.0,
        source=(
            f"hauteur d'observateur au-dessus du sol posée pour la démonstration (2 à 8 m), ajoutée à "
            f"l'altitude sourcée du site ({case_data.SANGATTE_ALTITUDE_SITE_M:g} m, Digue de Sangatte — "
            "voir case_data.SANGATTE_ALTITUDE_SOURCE) mais non ajoutée numériquement ici : par "
            "convention avec les deux premiers cas (postes eux aussi proches du niveau de la mer), h "
            "reste balayé sur [2 ; 8] m au-dessus du niveau moyen de la mer directement, l'altitude du "
            "site (2 m) étant elle-même à l'intérieur de cette plage plutôt qu'ajoutée à elle"
        ),
    )

    enveloppe_S = modele_S.enveloppe_prediction(D, plages_supplementaires=[plage_h], pas_par_parametre=9)
    enveloppe_P = modele_P.enveloppe_prediction(D, plages_supplementaires=[plage_h], pas_par_parametre=9)

    u_f_preenregistre = 0.02  # même hypothèse de pré-enregistrement que les deux premiers cas
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

    # sensor_forensics.py (PRNU/ELA) est délibérément NON exécuté — voir le premier cas d'étude pour
    # la justification complète : un diagramme généré par ordinateur n'a ni bruit de capteur ni
    # chaîne JPEG réaliste à analyser.

    return chemin_image, declaration, exif, grossissement, dossier_preuve


def construire_fiche(D, azimut, R_euler, cible_geom, hyp_k, enveloppe_S, enveloppe_P,
                      discrimination, u_f, exif, declaration_integrite, grossissement) -> FicheObservation:
    identification = Identification(
        identifiant_dossier=IDENTIFIANT_DOSSIER,
        date_heure_utc_serie=MAINTENANT,
        ecart_horloge_mesure=INDISPONIBLE,
        operateur="Claude (assistant), pour le compte de l'utilisateur — cas de démonstration",
        campagne_et_reference_preenregistrement=(
            "démonstration du pipeline A→B→C, troisième site (pilier 3 du Carnet de l'observateur) ; "
            "aucun pré-enregistrement formel au sens du §26 — u_f et le facteur du §28.2 sont "
            "déclarés ci-dessous à titre d'hypothèse de démonstration, identiques aux deux premiers "
            "cas pour permettre une comparaison directe"
        ),
    )

    position_sangatte = PositionGPS(
        latitude_deg=case_data.SANGATTE_LAT_DEG, longitude_deg=case_data.SANGATTE_LON_DEG,
        altitude_m=None, incertitude_m=None,
        source=(
            "position déclarée de la Digue de Sangatte (" + case_data.SANGATTE_COORDS_SOURCE + ") — "
            "point de référence posé pour la démonstration, pas une mesure GNSS sur site : aucune "
            "observation réelle n'a eu lieu"
        ),
    )
    poste_observation = PosteObservation(
        observateur=INDISPONIBLE,
        coordonnees_et_systeme_reference=position_sangatte,
        incertitude_recepteur=INDISPONIBLE,
        hauteur_ellipsoidale_et_geoide=INDISPONIBLE,
        altitude_sol_ou_niveau_eau=(
            f"{case_data.SANGATTE_ALTITUDE_SITE_M:g} m au-dessus du niveau moyen de la mer — "
            f"contrairement aux deux premiers cas (hypothèse posée), cette valeur est ici sourcée "
            f"(voir case_data.SANGATTE_ALTITUDE_SOURCE), pas simplement assimilée à z=0"
        ),
        hauteur_axe_optique="2 à 8 m au-dessus du niveau de la mer, plage balayée (§23.1) — voir 60-calcul/resultats.json",
        altitude_h_retenue_et_incertitude=(
            "traitée comme une plage balayée [2 ; 8] m, pas une valeur ponctuelle ; aucune incertitude "
            "JCGM composée séparément pour ce cas de démonstration ; cohérente avec l'altitude sourcée "
            f"du site ({case_data.SANGATTE_ALTITUDE_SITE_M:g} m) plus une hauteur d'œil humaine plausible"
        ),
    )

    position_southforeland = PositionGPS(
        latitude_deg=case_data.SOUTHFORELAND_LAT_DEG, longitude_deg=case_data.SOUTHFORELAND_LON_DEG,
        altitude_m=None, incertitude_m=None, source=case_data.SOUTHFORELAND_COORDS_SOURCE,
    )
    hauteur_southforeland = GrandeurGeodesique(
        nom="hauteur totale H (falaises de Douvres / South Foreland)", valeur=case_data.SOUTHFORELAND_HAUTEUR_TOTALE_M,
        unite="m", referentiel="hauteur au-dessus du niveau de la mer",
        source=case_data.SOUTHFORELAND_HAUTEUR_SOURCE, incertitude=5.0,
    )
    cible = Cible(
        designation_et_sources=(
            "Falaises de Douvres (White Cliffs of Dover) au droit du phare de South Foreland, "
            "Angleterre — relief naturel, pas un monument construit"
        ),
        coordonnees_et_systeme_reference=position_southforeland,
        altitude_base_zb_et_source=(
            "0 m (niveau moyen de la mer) — contrairement aux deux premiers cas, ce n'est pas ici une "
            "simplification : Wikipédia EN « White Cliffs of Dover » décrit explicitement des falaises "
            "s'élevant directement depuis le niveau de la mer"
        ),
        hauteur_totale_H_et_source=hauteur_southforeland,
        parties_pertinentes_cote_connue=INDISPONIBLE,
        extension_longitudinale=INDISPONIBLE,
    )

    grandeur_distance = GrandeurGeodesique(
        nom="distance géodésique (Digue de Sangatte → South Foreland)", valeur=D, unite="m", referentiel="GRS80 (ellipsoïde)",
        source="algorithme de Vincenty (1975), formule inverse — visee_optique.geodesy.vincenty_inverse, à partir des coordonnées sourcées",
        incertitude=15.0,
    )
    grandeur_azimut = GrandeurGeodesique(
        nom="azimut géodésique direct (Sangatte → South Foreland)", valeur=azimut, unite="°", referentiel="GRS80",
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
            + " Détail chiffré (37 points, altimétrie IGN RGE ALTI, résolution 2 km puis 500 m aux "
            "extrémités) dans 30-donnees-externes/profil_intermediaire.md."
        ),
        altitude_maximale_profil_et_marge=(
            "Aucun point intermédiaire en mer ne dépasse le niveau de la mer (valeur sentinelle IGN "
            "sur toute la portion couverte, 500 m à 28 km) — profil plat, marge de dégagement maximale "
            "par construction sur cette portion. Seuls les deux points d'ancrage sont au-dessus du "
            "niveau de la mer, par nature : le départ (5,76 m, Digue de Sangatte) et l'arrivée (110 m, "
            "falaises de Douvres, hors couverture IGN — voir 30-donnees-externes/profil_intermediaire.md "
            "pour la limite documentée)."
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
        f"condition de discrimination du §28.2 SATISFAITE pour cette géométrie : écart le plus "
        f"défavorable entre les modèles S et P = {discrimination.delta:.3f} (seuil = "
        f"{discrimination.facteur:g}×u_f = {discrimination.seuil:.3f}, avec u_f={u_f:g} pris comme "
        f"hypothèse de pré-enregistrement, identique aux deux premiers cas). À {D / 1000:.1f} km, le "
        f"modèle sphérique prédit une fraction visible PARTIELLE sur la plage plausible de h∈[2;8] m "
        f"et k∈[{hyp_k.k_min:g};{hyp_k.k_max:g}] (enveloppe S = "
        f"[{enveloppe_S.minimum:.4f};{enveloppe_S.maximum:.4f}]), pendant que le modèle plat prédit "
        "toujours une visibilité totale. Le verdict reste néanmoins déclaré indisponible ci-dessous : "
        "la condition de discrimination n'est qu'un préalable géométrique (§28.2) — trancher réellement "
        "entre les modèles exige une vraie photographie, validée (§18) et mesurée par au moins trois "
        "analystes indépendants (§25), ce qui n'existe pas pour ce cas de démonstration. À LA "
        "DIFFÉRENCE DU CAS CHASSIRON↔CORDOUAN, ce préalable géométrique N'EST PAS sans objet ici : la "
        "vérification du profil intermédiaire par altimétrie officielle IGN, menée AVANT la "
        "construction de cette archive (voir Geometrie.profil_intermediaire_source_et_pas ci-dessus et "
        "30-donnees-externes/profil_intermediaire.md), confirme une traversée intégralement maritime "
        "(aucune terre ferme intermédiaire détectée entre 500 m et 28 km, à la résolution testée). Une "
        "vraie campagne de mesure y serait donc physiquement possible — sous réserve des affinements "
        "listés dans 70-rapport/synthese.md (résolution ponctuelle plus fine, données atmosphériques "
        "réelles, trois analystes indépendants, etc.)."
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

    print("1b. Profil intermédiaire (Tableau 10, §12.3) : voir case_data.PROFIL_CONCLUSION_DEFINITIVE")
    print(f"    croisements de terre détectés : {len(case_data.PROFIL_CROISEMENTS_TERRE)} (attendu : 0)")

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
        "# Plan de démonstration — CAS-DEMO-SANGATTE-001\n\n"
        f"Rédigé le {MAINTENANT.isoformat()}.\n\n"
        "Troisième cas d'étude du projet. Cible : falaises de Douvres / phare de South Foreland "
        "(Angleterre). Poste de référence : Digue de Sangatte (Pas-de-Calais), 35,6 km. "
        "Contrairement aux deux premiers cas, le profil intermédiaire a été vérifié par altimétrie "
        "officielle IGN AVANT la construction de cette archive, et deux autres candidats plausibles "
        "ont été écartés au même stade (voir 30-donnees-externes/sources.md).\n\n"
        "Ce n'est PAS un pré-enregistrement au sens du §26 : aucune campagne de mesure réelle n'est "
        "prévue. Les hypothèses ci-dessous sont déclarées pour que le calcul du §28.2 puisse "
        "s'exécuter avec des valeurs explicites, identiques aux deux premiers cas pour permettre une "
        "comparaison directe.\n\n"
        f"- Cible : falaises de Douvres au droit du phare de South Foreland, H = "
        f"{case_data.SOUTHFORELAND_HAUTEUR_TOTALE_M:g} m (voir 30-donnees-externes/).\n"
        f"- Point de référence : Digue de Sangatte, altitude sourcée "
        f"{case_data.SANGATTE_ALTITUDE_SITE_M:g} m (voir 30-donnees-externes/).\n"
        f"- Hauteur d'observateur h : plage [2 ; 8] m, balayée (§23.1), non mesurée mais cohérente "
        "avec l'altitude sourcée du site.\n"
        f"- Intervalle de réfraction k : [{hyp_k.k_min:g} ; {hyp_k.k_max:g}] (régimes standard + "
        "fort, §21.3, faute de donnée atmosphérique résolue).\n"
        f"- Incertitude de mesure anticipée u_f : 0,02 (hypothèse de démonstration, identique aux "
        "deux premiers cas).\n"
        "- Facteur de discrimination (§28.2) : 5 (valeur par défaut de condition_discrimination).\n"
        "- Profil intermédiaire (Tableau 10, §12.3) : vérifié EN AMONT, 100 % maritime — voir "
        "30-donnees-externes/profil_intermediaire.md.\n",
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
        f"## Cible — falaises de Douvres / phare de South Foreland\n"
        f"- Coordonnées : {case_data.SOUTHFORELAND_LAT_DEG:.6f}°N, {case_data.SOUTHFORELAND_LON_DEG:.6f}°E\n"
        f"  Source : {case_data.SOUTHFORELAND_COORDS_SOURCE}\n"
        f"- Hauteur totale (falaise) : {case_data.SOUTHFORELAND_HAUTEUR_TOTALE_M:g} m\n"
        f"  Source : {case_data.SOUTHFORELAND_HAUTEUR_SOURCE}\n\n"
        f"## Point de référence — Digue de Sangatte\n"
        f"- Coordonnées : {case_data.SANGATTE_LAT_DEG:.6f}°N, {case_data.SANGATTE_LON_DEG:.6f}°E\n"
        f"  Source : {case_data.SANGATTE_COORDS_SOURCE}\n"
        f"- Altitude du site : {case_data.SANGATTE_ALTITUDE_SITE_M:g} m\n"
        f"  Source : {case_data.SANGATTE_ALTITUDE_SOURCE}\n\n"
        "## Sites écartés et pourquoi (AVANT construction de cette archive)\n\n"
        "**Cap Gris-Nez ↔ South Foreland** (33,9 km, le point de traversée le plus étroit de la "
        "Manche) : Cap Gris-Nez est en réalité un cap élevé (falaise ~45 m, source geowiki.fr). Avec "
        "h reflétant honnêtement cette altitude réelle (h∈[45;53] m), la condition de discrimination "
        "du §28.2 n'est PAS satisfaite à cette distance (écart le plus défavorable ≈ 3,7×10⁻⁵, très "
        "en dessous du seuil) : un poste déjà élevé rend le modèle sphérique quasi indiscernable du "
        "modèle plat. Substituer artificiellement h∈[2;8] m (comme si l'observateur se tenait au ras "
        "de l'eau au pied de la falaise) aurait rétabli la discrimination sur le papier, mais de "
        "façon malhonnête : rien ne documente un poste réel au ras de l'eau à cet endroit précis. "
        "Écarté pour cette raison, avant toute construction d'archive.\n\n"
        "**Cordouan ↔ Cap Ferret** (104,7 km, Côte d'Argent) : le pré-écran altimétrique IGN a montré "
        "que la ligne droite reste en mer jusqu'à ~88-90 km, PUIS remonte la presqu'île du Cap Ferret "
        "elle-même (son isthme sableux) sur ses ~15 derniers km avant d'atteindre le phare — même "
        "type de piège que le cas Chassiron↔Cordouan (un phare en bout de presqu'île ne regarde pas "
        "forcément le large dans l'azimut testé). Écarté avant toute construction d'archive.\n\n"
        "Détail complet des deux écarts et du choix final dans "
        "le rapport de sélection de site (non joint à cette livraison).\n\n"
        "## Contrôle géométrique — absence de cap français intermédiaire\n"
        "Le Cap Blanc-Nez (azimut ~230,6° depuis la digue) et le Cap Gris-Nez (azimut ~234,3°) sont "
        "tous deux à l'opposé de la route vers l'Angleterre (azimut ~305,5°) : la ligne droite "
        "s'éloigne des deux caps dès le départ et ne les recroise jamais (vérifié par "
        "échantillonnage tous les 2 km — la latitude ne redescend jamais sous celle de la digue).\n\n"
        "## Profil intermédiaire — vérifié par altimétrie officielle IGN, EN AMONT de cette archive\n"
        "Vérification effectuée le 2026-09-03 à partir du RGE ALTI de l'IGN (API Géoplateforme, "
        "donnée souveraine officielle) : voir le relevé complet (37 points, deux résolutions) et la "
        "conclusion dans 30-donnees-externes/profil_intermediaire.md. RÉSULTAT : aucune traversée de "
        "terre ferme intermédiaire détectée — traversée intégralement maritime sur toute la portion "
        "couverte par le référentiel français. CE SITE SATISFAIT l'exigence d'une visée directe sur "
        "mer (Tableau 10, §12.3), à la résolution testée.\n\n"
        "## Algorithme géodésique\n"
        "Vincenty (1975), formule inverse, ellipsoïde GRS80 — voir visee_optique.geodesy.vincenty_inverse "
        "dans 60-calcul/case_data.py.\n",
        encoding="utf-8",
    )

    lignes_elevations = "\n".join(
        f"| {d/1000:.3f} | {('mer / hors couverture IGN' if elev is None else f'{elev:+.2f}')} |"
        for d, elev in case_data.PROFIL_ELEVATIONS_IGN
    )
    (racine_archive / "30-donnees-externes" / "profil_intermediaire.md").write_text(
        "# Vérification du profil intermédiaire (Tableau 10, §12.3)\n\n"
        "Contrairement aux deux premiers cas de ce projet, cette vérification a été menée EN AMONT "
        "de la construction de cette archive — discipline instaurée après la correction du cas "
        "Chassiron↔Cordouan (voir cas-chassiron/30-donnees-externes/profil_intermediaire.md pour le "
        "précédent qui a motivé ce changement de méthode).\n\n"
        "## Méthode\n\n"
        "API REST d'altimétrie de la Géoplateforme IGN "
        "(https://data.geopf.fr/altimetrie/1.0/calcul/alti/rest/elevation.json, ressource "
        "`ign_rge_alti_wld`) : donnée souveraine officielle française, renvoie -99999 (à l'arrondi "
        "près) pour tout point hors de sa couverture terrestre. Deux résolutions, conformément à la "
        "demande explicite de resserrement de la maille côtière (Tableau 10, §12.3) : 500 m sur les "
        "6 premiers et les 6 derniers kilomètres (zones de départ et d'arrivée), 2 km sur le corps "
        "de la route (8 à 28 km).\n\n"
        "## Limite assumée et documentée\n\n"
        "Le RGE ALTI est une donnée SOUVERAINE FRANÇAISE : il ne couvre pas le territoire "
        "britannique. Les points interrogés près de South Foreland (29,61 à 35,61 km) renvoient tous "
        "la valeur -99999, ce qui signifie ici « hors de la couverture du référentiel », pas "
        "nécessairement « mer confirmée » au sens où on l'entend côté français. La nature terrestre "
        "de l'arrivée (falaises de Douvres, 110 m) est établie par une source indépendante "
        "(Wikipédia EN, voir sources.md), pas par l'IGN.\n\n"
        "## Relevé complet (37 points)\n\n"
        "| distance depuis la Digue de Sangatte (km) | élévation |\n"
        "|---|---|\n"
        f"{lignes_elevations}\n\n"
        "## Traversées de terre ferme intermédiaires identifiées\n\n"
        "Aucune. Le tableau ci-dessus ne montre que deux points terrestres, les deux points "
        "d'ancrage eux-mêmes (0 km : Digue de Sangatte, 5,76 m ; et, hors couverture IGN, 35,61 km : "
        "falaises de Douvres, confirmées par ailleurs). Toute la portion intermédiaire couverte par "
        "l'IGN (500 m à 28 km) renvoie la valeur sentinelle (mer).\n\n"
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
        "verification_profil_ign_rge_alti": {
            "elevations_m_par_distance_m": {str(d): e for d, e in case_data.PROFIL_ELEVATIONS_IGN},
            "croisements_terre": list(case_data.PROFIL_CROISEMENTS_TERRE),
            "longueur_totale_sur_terre_m": 0,
            "site_valide_pour_visee_directe_sur_mer": True,
            "verifie_avant_construction_archive": True,
        },
        "sites_ecartes_avant_archive": [
            {"nom": "Cap Gris-Nez ↔ South Foreland", "distance_km": 33.9, "motif": "discrimination non satisfaite a h reel (~45 m)"},
            {"nom": "Cordouan ↔ Cap Ferret", "distance_km": 104.7, "motif": "ligne remonte la presqu'ile du Cap Ferret sur ~15 km"},
        ],
    }
    (racine_archive / "60-calcul" / "resultats.json").write_text(
        json.dumps(resultats_json, ensure_ascii=False, indent=2), encoding="utf-8"
    )

    (racine_archive / "70-rapport" / "synthese.md").write_text(
        "# Synthèse — CAS-DEMO-SANGATTE-001\n\n"
        "Troisième cas bout-en-bout à travers Outil A, Outil B et Outil C. Cible : falaises de "
        "Douvres au droit du phare de South Foreland (Angleterre), 110 m. Poste de référence : Digue "
        "de Sangatte (Pas-de-Calais), 35,6 km, altitude sourcée 2 m. Aucune photographie réelle n'a "
        "été mesurée : voir 10-originaux/AVERTISSEMENT.md.\n\n"
        "**Méthode inversée par rapport aux deux premiers cas :** le profil intermédiaire a été "
        "vérifié par altimétrie officielle IGN (RGE ALTI) AVANT la construction de cette archive, et "
        "deux candidats plausibles en apparence ont été écartés au même stade (Cap Gris-Nez↔South "
        "Foreland, pour discrimination insuffisante à altitude réaliste ; Cordouan↔Cap Ferret, pour "
        "traversée de la presqu'île elle-même) — voir 30-donnees-externes/sources.md. C'est la leçon "
        "tirée directement de la correction du second cas (CAS-DEMO-CHASSIRON-001), qui avait conclu "
        "à tort, sur la seule base d'un raisonnement géographique, qu'un site était valide.\n\n"
        f"**Constat géométrique :** la condition de discrimination du §28.2 EST satisfaite à "
        f"{D / 1000:.1f} km pour la plage h∈[2;8] m et k∈[{hyp_k.k_min:g};{hyp_k.k_max:g}] (écart le "
        f"plus défavorable {discrimination.delta:.3f}, au-dessus du seuil {discrimination.seuil:.3f}) "
        f"— le modèle sphérique prédit une fraction visible partielle "
        f"(enveloppe S = [{enveloppe_S.minimum:.4f};{enveloppe_S.maximum:.4f}]), le modèle plat une "
        "visibilité totale. Voir 20-fiche/fiche_observation.txt pour le détail et "
        "60-calcul/resultats.json pour les valeurs numériques.\n\n"
        "**Constat de profil :** vérification altimétrique IGN, 37 points, résolution 2 km sur le "
        "corps de la route et 500 m aux deux extrémités (sur demande explicite de resserrement de la "
        "maille côtière) : AUCUNE traversée de terre ferme intermédiaire. Traversée intégralement "
        "maritime sur toute la portion couverte par le référentiel français. **Ce site SATISFAIT "
        "l'exigence du Tableau 10 (§12.3) d'une visée directe sur mer.**\n\n"
        "**Ce que ce dossier n'établit PAS pour autant :** un verdict compatible/incompatible réel "
        "(§28.3) exige une vraie photographie, validée (§18) et mesurée par au moins trois analystes "
        "indépendants (§25) — inexistante ici. La résolution du pré-écran (500 m aux extrémités, "
        "2 km au centre) suffit à écarter tout cap ou île de taille significative, mais pas à "
        "garantir l'absence d'un écueil ponctuel de quelques dizaines de mètres non répertorié : un "
        "affinement local supplémentaire (pas 50-100 m sur l'intégralité du corps de la route, pas "
        "seulement les extrémités) resterait recommandé avant toute vraie campagne de mesure. Les "
        "données atmosphériques réelles (température par hauteur, pression, humidité) restent elles "
        "aussi non résolues (classe E), comme pour les deux premiers cas.\n\n"
        "Déclaration d'intérêts : sans objet (démonstration solitaire, pas un examen commandé).\n",
        encoding="utf-8",
    )

    (racine_archive / "90-journal" / "journal.md").write_text(
        "# Journal des opérations — CAS-DEMO-SANGATTE-001\n\n"
        f"- {MAINTENANT.isoformat()} — recherche d'un candidat Manche/Atlantique proche du niveau de "
        "la mer, sur demande explicite ; écart de Cap Gris-Nez↔South Foreland (discrimination non "
        "satisfaite à altitude réaliste)\n"
        f"- {MAINTENANT.isoformat()} — écart de Cordouan↔Cap Ferret (pré-écran altimétrique : ligne "
        "remontant la presqu'île elle-même)\n"
        f"- {MAINTENANT.isoformat()} — sélection de Sangatte↔South Foreland (35,6 km) ; contrôle "
        "géométrique de l'absence de cap français intermédiaire\n"
        f"- {MAINTENANT.isoformat()} — pré-écran altimétrique IGN à résolution 2 km (18 points) : "
        "aucune traversée détectée\n"
        f"- {MAINTENANT.isoformat()} — calcul géodésique définitif (Vincenty, GRS80) entre les "
        "coordonnées sourcées\n"
        f"- {MAINTENANT.isoformat()} — resserrement de la maille altimétrique à 500 m sur les zones "
        "de départ (0-6 km) et d'arrivée (29,61-35,61 km), sur demande explicite (Tableau 10, "
        "§12.3) ; confirmation, avec documentation de la limite de couverture IGN côté anglais\n"
        f"- {MAINTENANT.isoformat()} — balayage de sensibilité des modèles S et P (§23.1)\n"
        f"- {MAINTENANT.isoformat()} — calcul de la condition de discrimination (§28.2) : satisfaite\n"
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
