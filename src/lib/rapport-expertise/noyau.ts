/**
 * noyau.ts — Port TypeScript du paquet Python `rapport_expertise` (outil C).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-C-rapport-expertise/`, qui porte 42 tests. Ce
 * port est épinglé au Python par `vecteurs-or.json` et le contrôle
 * `scripts/verifier-port-rapport.mjs`.
 *
 * Ce qui est porté ici n'est pas du calcul mais une STRUCTURE — les neuf blocs
 * du §33 et l'arborescence du §34 — et c'est justement ce qui se désynchronise
 * sans bruit : un champ ajouté côté Python et oublié ici donnerait une fiche
 * qui a l'air complète et qui ne l'est pas. Les vecteurs figent donc le nom et
 * l'ordre exacts de chacun des cinquante-six champs.
 *
 * Ce que le navigateur ne peut pas faire, et que ce port ne prétend pas faire :
 * `verrouiller_originaux` retire le droit d'écriture sur 10-originaux/ par un
 * chmod Unix. Un navigateur n'a pas de système de fichiers à verrouiller. La
 * commande exacte est fournie à l'utilisateur (voir COMMANDE_VERROUILLAGE)
 * plutôt que simulée.
 */

export class RapportError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'RapportError';
  }
}

/** §33 : le même mot que dans les trois paquets Python et les trois ports. */
export const INDISPONIBLE = 'indisponible';

/**
 * Force un choix explicite : une vraie valeur, ou le sentinel — jamais une
 * chaîne vide, jamais une omission (§33).
 */
export function declarer(valeur: string | null | undefined, nomChamp: string): string {
  if (valeur === null || valeur === undefined || valeur === '') {
    throw new RapportError(
      `« ${nomChamp} » doit être renseigné ou explicitement « ${INDISPONIBLE} », ` +
        'jamais omis (§33).',
    );
  }
  return valeur;
}

// --- §33 : les neuf blocs de la fiche standard d'observation ---

export interface DefinitionChamp {
  /** Nom exact du champ côté Python. Épinglé par les vecteurs. */
  nom: string;
  /** Intitulé lisible, pour l'interface seulement. */
  libelle: string;
  /** Ce que le champ attend, en une phrase. */
  aide: string;
}

export interface DefinitionBloc {
  nom: string;
  titre: string;
  champs: DefinitionChamp[];
}

export const BLOCS: DefinitionBloc[] = [
  {
    nom: 'identification',
    titre: 'Identification',
    champs: [
      { nom: 'identifiant_dossier', libelle: 'Identifiant du dossier', aide: 'Référence unique et stable, reprise partout ailleurs.' },
      { nom: 'date_heure_utc_serie', libelle: 'Date et heure UTC de la série', aide: 'Temps universel, pas l’heure locale.' },
      { nom: 'ecart_horloge_mesure', libelle: 'Écart d’horloge mesuré', aide: 'Écart relevé entre l’horloge de l’appareil et le temps universel, avant la série.' },
      { nom: 'operateur', libelle: 'Opérateur', aide: 'Qui a pris les vues. Ne peut être aucun des trois analystes (§25).' },
      { nom: 'campagne_et_reference_preenregistrement', libelle: 'Campagne et référence du pré-enregistrement', aide: 'Où le seuil et le plan ont été déposés, et à quelle date.' },
    ],
  },
  {
    nom: 'poste_observation',
    titre: 'Poste d’observation',
    champs: [
      { nom: 'observateur', libelle: 'Observateur', aide: 'Lieu et description du poste.' },
      { nom: 'coordonnees_et_systeme_reference', libelle: 'Coordonnées et système de référence', aide: 'Avec l’époque du système, pas seulement son nom.' },
      { nom: 'incertitude_recepteur', libelle: 'Incertitude annoncée par le récepteur', aide: 'Celle que le récepteur affiche, pas une valeur de catalogue.' },
      { nom: 'hauteur_ellipsoidale_et_geoide', libelle: 'Hauteur ellipsoïdale et modèle de géoïde', aide: 'Une hauteur GNSS brute est ellipsoïdale : le modèle employé pour la convertir doit être nommé (§12.1).' },
      { nom: 'altitude_sol_ou_niveau_eau', libelle: 'Altitude du sol ou niveau d’eau', aide: 'À l’heure exacte, marée corrigée le cas échéant.' },
      { nom: 'hauteur_axe_optique', libelle: 'Hauteur de l’axe optique', aide: 'Au-dessus du sol ou du plan d’eau, mesurée et photographiée.' },
      { nom: 'altitude_h_retenue_et_incertitude', libelle: 'Altitude h retenue et son incertitude', aide: 'La valeur employée au calcul, et ce qu’elle vaut.' },
    ],
  },
  {
    nom: 'cible',
    titre: 'Cible',
    champs: [
      { nom: 'designation_et_sources', libelle: 'Désignation et sources d’identification', aide: 'Recoupement avec une source extérieure, jamais la ressemblance (§2.5.1).' },
      { nom: 'coordonnees_et_systeme_reference', libelle: 'Coordonnées et système de référence', aide: 'Fiche officielle, relevé géodésique, ou registre horodaté pour un mobile.' },
      { nom: 'altitude_base_zb_et_source', libelle: 'Altitude de base z_b et sa source', aide: 'Modèle de terrain, ou niveau de la mer corrigé de la marée.' },
      { nom: 'hauteur_totale_H_et_source', libelle: 'Hauteur totale H et sa source', aide: 'Établie indépendamment de la photographie analysée (§12.4).' },
      { nom: 'parties_pertinentes_cote_connue', libelle: 'Parties pertinentes de cote connue', aide: 'Les repères qui serviront d’échelle métrique dans l’image.' },
      { nom: 'extension_longitudinale', libelle: 'Extension longitudinale de la cible', aide: 'Une cible étendue le long de la visée n’a pas une distance unique.' },
    ],
  },
  {
    nom: 'geometrie',
    titre: 'Géométrie',
    champs: [
      { nom: 'distance_D_algorithme_et_incertitude', libelle: 'Distance D, algorithme et incertitude', aide: 'Géodésique sur l’ellipsoïde par un algorithme publié, jamais une règle sur une carte.' },
      { nom: 'azimut_geodesique', libelle: 'Azimut géodésique', aide: 'Issu du même calcul que la distance.' },
      { nom: 'rayon_courbure_euler', libelle: 'Rayon de courbure d’Euler', aide: 'À l’azimut de la visée et à la latitude du trajet — jamais le rayon moyen (§12.2).' },
      { nom: 'profil_intermediaire_source_et_pas', libelle: 'Profil intermédiaire : source et pas', aide: 'Échantillonné au pas de 500 m au plus le long de la géodésique.' },
      { nom: 'altitude_maximale_profil_et_marge', libelle: 'Altitude maximale du profil et marge sous la visée', aide: 'Un relief qui dépasse la ligne de visée rend le masquage topographique, pas géométrique (§9.1.3).' },
    ],
  },
  {
    nom: 'systeme_photographique',
    titre: 'Système photographique',
    champs: [
      { nom: 'boitier_objectif_numeros_serie', libelle: 'Boîtier, objectif, numéros de série', aide: 'Identifie le matériel employé, pas seulement son modèle.' },
      { nom: 'focale_reelle_et_equivalente', libelle: 'Focale réelle et focale équivalente', aide: 'La focale optique réelle, pas un grossissement affiché.' },
      { nom: 'ouverture_temps_pose_sensibilite', libelle: 'Ouverture, temps de pose, sensibilité', aide: 'Tels qu’écrits dans les métadonnées.' },
      { nom: 'resolution_native_et_pas_photosite', libelle: 'Résolution native du capteur et pas de photosite', aide: 'D’après la documentation du constructeur.' },
      { nom: 'resolution_fichier_final', libelle: 'Résolution du fichier final', aide: 'À comparer à la précédente : l’écart révèle un recadrage ou un rééchantillonnage.' },
      { nom: 'grossissement', libelle: 'Grossissement, part optique et part numérique', aide: 'Les deux séparément (§15.2). Un fort zoom est autorisé, pas dispensé de documentation.' },
      { nom: 'recadrage_interne_avant_enregistrement', libelle: 'Recadrage interne avant enregistrement', aide: 'Mode ou réglage employé, et rapport à la surface du capteur entier.' },
      { nom: 'traitements_computationnels_actifs', libelle: 'Traitements computationnels actifs', aide: 'Rehaussement, fusion multi-vues, réduction de bruit, reconnaissance de sujet : actifs ou non.' },
      { nom: 'profil_distorsion_et_residuel', libelle: 'Profil de distorsion appliqué et résiduel', aide: 'Après étalonnage du couple boîtier-objectif.' },
    ],
  },
  {
    nom: 'atmosphere',
    titre: 'Atmosphère',
    champs: [
      { nom: 'temperature_air_par_hauteur', libelle: 'Température de l’air à chaque hauteur mesurée', aide: 'Le gradient près de la surface pèse bien plus que sa part en hauteur (§11.5).' },
      { nom: 'temperature_surface_mer', libelle: 'Température de surface de la mer', aide: 'L’écart air-eau est le meilleur indicateur disponible d’une inversion de surface.' },
      { nom: 'pression_humidite', libelle: 'Pression et humidité', aide: 'Relevées au poste, ou déclarées d’une autre origine avec leur classe.' },
      { nom: 'profil_vertical_disponible', libelle: 'Profil vertical disponible', aide: 'Source, résolution, distance et écart horaire — tous les quatre.' },
      { nom: 'classe_de_chaque_donnee', libelle: 'Classe de chaque donnée (A à E)', aide: 'La classe dit comment la valeur a été obtenue, pas si elle est juste (§21.2).' },
      { nom: 'intervalle_k_retenu_et_justification', libelle: 'Intervalle de k retenu et sa justification', aide: 'Déposé avant l’analyse. Ne se resserre jamais après avoir vu un résultat (§11.7).' },
    ],
  },
  {
    nom: 'images',
    titre: 'Images',
    champs: [
      { nom: 'nombre_vues_noms_fichiers_empreintes', libelle: 'Nombre de vues, noms de fichiers, empreintes', aide: 'Toutes les vues de la série, y compris celles qui seront écartées.' },
      { nom: 'preuve_datation_empreintes', libelle: 'Preuve de datation des empreintes', aide: 'Par un tiers. Sans elle, la date n’est que votre déclaration (§17.1).' },
      { nom: 'classement_chaque_vue', libelle: 'Classement de chaque vue', aide: 'Selon la grille du §18, par quelqu’un qui ignore la prédiction.' },
      { nom: 'vues_exclues_et_motif', libelle: 'Vues exclues et motif', aide: 'Le taux d’exclusion fait partie du résultat, pas des coulisses.' },
      { nom: 'resolution_effective_mesuree', libelle: 'Résolution effective mesurée', aide: 'Sur un bord franc de dimension connue, jamais calculée (§20.2).' },
      { nom: 'transformations_appliquees_copie', libelle: 'Transformations appliquées à la copie', aide: 'La liste complète. Le fichier d’origine, lui, n’est jamais ouvert en écriture.' },
    ],
  },
  {
    nom: 'mesures',
    titre: 'Mesures',
    champs: [
      { nom: 'caracteristique_designee_et_date', libelle: 'Caractéristique désignée et date de sa désignation', aide: 'Nommée avant tout contrôle de résolution (§2.5.3).' },
      { nom: 'positions_pixels_par_analyste', libelle: 'Positions en pixels rendues par chaque analyste', aide: 'Trois analystes en aveugle, sans connaître distance, hauteur ni prédiction.' },
      { nom: 'echelle_par_focale_et_par_reperes', libelle: 'Échelle par la focale, et par les repères', aide: 'Deux déterminations indépendantes ; un écart de plus de 2 % invalide la focale déclarée.' },
      { nom: 'hauteur_visible_et_occultee', libelle: 'Hauteur visible et hauteur occultée', aide: 'En mètres, après conversion par l’échelle retenue.' },
      { nom: 'fraction_visible_observee_et_incertitude', libelle: 'Fraction visible observée et son incertitude', aide: 'La grandeur comparée. L’incertitude n’est jamais inférieure à la résolution effective.' },
      { nom: 'rapports_hauteur_mesures_et_attendus', libelle: 'Rapports de hauteur mesurés et attendus', aide: 'Le test opératoire de la déformation verticale (§19.4).' },
    ],
  },
  {
    nom: 'resultat',
    titre: 'Résultat',
    champs: [
      { nom: 'fraction_predite_par_modele_avec_enveloppe', libelle: 'Fraction prédite par modèle, avec enveloppe', aide: 'Jamais une valeur ponctuelle.' },
      { nom: 'ecart_observe_predit_et_incertitude', libelle: 'Écart observé-prédit et incertitude composée', aide: 'À confronter au seuil déposé, pas à un seuil choisi maintenant.' },
      { nom: 'combinaison_plus_defavorable', libelle: 'Combinaison la plus défavorable à la conclusion', aide: 'Le §23.2 l’exige explicitement, et dans les deux sens.' },
      { nom: 'resultat_recherche_regimes', libelle: 'Résultat de la recherche de régimes', aide: 'Consigné qu’il soit positif ou négatif (§19.4).' },
      { nom: 'verdict_par_modele', libelle: 'Verdict par modèle', aide: 'Compatible, incompatible ou indéterminé — pour chaque modèle déposé.' },
      { nom: 'motif_indetermination', libelle: 'Motif d’indétermination le cas échéant', aide: 'Ce qui manque, et ce qu’il faudrait pour le lever.' },
    ],
  },
];

export type Fiche = Record<string, Record<string, string>>;

/** Une fiche neuve : chaque champ vide, aucun préremplissage. */
export function ficheVide(): Fiche {
  const f: Fiche = {};
  for (const b of BLOCS) {
    f[b.nom] = {};
    for (const c of b.champs) f[b.nom][c.nom] = '';
  }
  return f;
}

/**
 * Les chemins pointés des champs portant le sentinel (§33).
 * « Un dossier incomplet est indéterminé, pas défavorable » suppose de pouvoir
 * dire précisément ce qui manque.
 */
export function champsIndisponibles(fiche: Fiche): string[] {
  const manquants: string[] = [];
  for (const b of BLOCS) {
    for (const c of b.champs) {
      if (fiche[b.nom]?.[c.nom] === INDISPONIBLE) manquants.push(`${b.nom}.${c.nom}`);
    }
  }
  return manquants;
}

/** Les chemins pointés des champs ni renseignés ni déclarés indisponibles. */
export function champsOmis(fiche: Fiche): string[] {
  const omis: string[] = [];
  for (const b of BLOCS) {
    for (const c of b.champs) {
      const v = fiche[b.nom]?.[c.nom];
      if (v === undefined || v === '') omis.push(`${b.nom}.${c.nom}`);
    }
  }
  return omis;
}

/** Valide toute la fiche : lève au premier champ omis (§33). */
export function validerFiche(fiche: Fiche): void {
  for (const b of BLOCS) {
    for (const c of b.champs) declarer(fiche[b.nom]?.[c.nom], `${b.nom}.${c.nom}`);
  }
}

// --- §34 : l'arborescence d'archive ---

export const ARBORESCENCE_IMPOSEE: { nom: string; description: string }[] = [
  { nom: '00-preenregistrement', description: 'plan daté, seuil, modèles déposés, preuve de dépôt' },
  { nom: '10-originaux', description: 'fichiers tels que sortis de l’appareil, jamais modifiés' },
  { nom: '11-empreintes', description: 'SHA256SUMS, date de calcul, preuve de datation par un tiers' },
  { nom: '20-fiche', description: 'fiche du §33, en texte structuré et en PDF' },
  { nom: '30-donnees-externes', description: 'extraits géodésiques, topographiques, marégraphiques, météorologiques, avec leur date d’édition' },
  { nom: '40-controles', description: 'mire, distorsion, stabilité, orientation, cohérence entre focales' },
  { nom: '50-mesures', description: 'relevés en pixels de chaque analyste, journal de classement horodaté' },
  { nom: '60-calcul', description: 'code, paramètres, germe aléatoire, sorties intermédiaires' },
  { nom: '70-rapport', description: 'rapport de chaque analyste, déclarations d’intérêt, rapport de synthèse' },
  { nom: '90-journal', description: 'journal horodaté de toutes les opérations, y compris les écarts au plan' },
];

export function nomDossierArchive(identifiant: string): string {
  if (identifiant.trim() === '') {
    throw new RapportError("Un identifiant de dossier est requis pour nommer l'archive.");
  }
  return `dossier-${identifiant}`;
}

/**
 * Ce qu'un navigateur ne peut pas faire. `verrouiller_originaux` retire le
 * droit d'écriture sur 10-originaux/ ; il n'y a pas de système de fichiers à
 * verrouiller ici. La commande est donnée à l'utilisateur, pas simulée.
 */
export const COMMANDE_VERROUILLAGE = 'chmod -R a-w 10-originaux/';
