/**
 * fiche-terrain.ts — Port TypeScript de `visee_optique.fiche_terrain` (outil A).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est
 * `outils/outil-A-visee-optique/visee_optique/fiche_terrain.py`. Ce port est
 * épinglé au Python par `vecteurs-or-fiche.json`, que
 * `scripts/verifier-port-fiche.mjs` rejoue ici — texte compris, caractère par
 * caractère. Toute correction se fait dans le Python d'abord.
 *
 * LES APOSTROPHES SONT DROITES, ET IL FAUT LES LAISSER DROITES
 * ───────────────────────────────────────────────────────────
 * Le reste du site écrit l'apostrophe typographique dans sa prose. Pas ici :
 * le paquet Python emploie l'apostrophe DROITE, et la fiche doit sortir
 * identique des deux côtés. Une « correction » typographique dans ce fichier
 * ferait donc échouer le vérificateur de port — ce n'est pas un défaut du
 * vérificateur, c'est son travail. La divergence d'apostrophe entre Python et
 * TypeScript s'est déjà produite quatre fois dans ce dépôt : elle est
 * invisible à l'œil et change le texte rendu.
 *
 * D'où les gabarits entre accents graves partout : ils portent l'apostrophe
 * droite sans échappement, donc sans occasion de se tromper.
 *
 * CE QUE LA FICHE EST
 * ───────────────────
 * Une page dérivée d'une simulation déjà faite, écrite pour un volontaire qui
 * n'a lu aucun protocole. Chaque champ demandé dit POURQUOI il est demandé, et
 * la prédiction est rassemblée dans un dernier bloc qu'on ne lit qu'après la
 * prise de vue — sinon l'œil trouve la valeur qu'on lui a annoncée.
 */

import {
  K_ENVELOPPE_MAX,
  K_ENVELOPPE_MIN,
  K_STANDARD,
  type Verdict,
  formatDecimal,
  formatK,
  formatMetres,
  formatPourcent,
} from './simulation';

export class FicheError extends Error {
  constructor(message: string) {
    super(message);
    this.name = 'FicheError';
  }
}

export interface DescriptionMilieu {
  nom: string;
  /** Le niveau de référence, SANS article — voir PREFIXE_REFERENCE_ATTENDU. */
  reference: string;
  reserve: string;
}

/**
 * Les trois milieux, avec ce que chacun change RÉELLEMENT.
 *
 * La réserve n'est pas décorative : elle dit ce que le milieu retire ou ajoute
 * à ce que l'observation pourra établir.
 */
export const MILIEUX: Record<string, DescriptionMilieu> = {
  lac: {
    nom: 'Lac',
    reference: `niveau de l'eau du lac`,
    reserve: `Un lac est le meilleur cas : sa surface est un plan d'eau au `
      + `repos, donc une surface de référence sans relief, et son étendue `
      + `limitée réduit les écarts de température le long du trajet. Ce `
      + `qui reste à surveiller est l'air juste au-dessus de l'eau, où la `
      + `réfraction s'écarte le plus de la moyenne employée par le `
      + `calcul — d'où les deux températures demandées.`,
  },
  mer: {
    nom: 'Mer',
    reference: `niveau de la mer à l'heure de la prise de vue`,
    reserve: `La mer est une surface de référence sans relief, mais son niveau `
      + `BOUGE : la marée le déplace de plusieurs mètres en quelques `
      + `heures. Une hauteur d'objectif relevée sans l'heure ne veut donc `
      + `rien dire, et c'est la raison pour laquelle l'heure et la marée `
      + `sont demandées ensemble.`,
  },
  terre: {
    nom: 'Terre',
    reference: `niveau du sol au poste d'observation`,
    reserve: `Une visée terrestre est structurellement plus faible, et il faut `
      + `le savoir avant de partir. Le sol entre les deux points n'est pas `
      + `une surface de référence : il monte et il descend, et ce `
      + `simulateur ne modélise AUCUN relief. Une base masquée peut l'être `
      + `par un pli de terrain plutôt que par la courbure, et l'image `
      + `seule ne les distingue pas. Une conclusion demande donc, en plus, `
      + `de montrer que la ligne de visée passe au-dessus de tout le `
      + `terrain intermédiaire — un profil altimétrique que cet outil ne `
      + `fournit pas.`,
  },
};

/**
 * Le nom du niveau de référence est stocké SANS article, et les phrases le
 * reprennent en « le / du / au ». Toutes les valeurs commencent par
 * « niveau », un masculin à consonne, ce qui rend ces trois contractions
 * correctes sans qu'aucune règle de grammaire soit devinée.
 */
export const PREFIXE_REFERENCE_ATTENDU = 'niveau ';

/**
 * Combien de pixels l'écart entre les deux modèles doit occuper sur l'image
 * pour être MESURÉ et non estimé à l'œil. Convention, comme le seuil de
 * discrimination : nommée pour qu'on puisse la contester.
 */
export const PIXELS_MIN_ECART = 20;

/** La largeur du rendu texte : 72 colonnes tiennent partout sans réglage. */
export const LARGEUR_TXT = 72;

export const MOTIF_MILIEU_SANS_EFFET =
  `Le milieu ne change AUCUN chiffre de la simulation : la géométrie est la `
  + `même sur un lac, en mer et sur terre. Il change le niveau auquel les `
  + `hauteurs sont comptées, les grandeurs qui font bouger ce niveau, et ce `
  + `que l'observation pourra établir.`;

export const MOTIF_AVEUGLE =
  `À ne pas lire avant la prise de vue. Une mesure faite en connaissant la `
  + `valeur attendue la retrouve, sans mauvaise foi de personne : l'œil place `
  + `le bord là où on lui a dit de le chercher. Mesurez d'abord, comparez `
  + `ensuite.`;

export const MOTIF_HORODATAGE =
  `Cet horodatage est celui de la machine qui a produit la fiche. Il `
  + `n'atteste aucune antériorité devant un tiers, et le présenter comme une `
  + `preuve de dépôt serait exactement le défaut que le préenregistrement `
  + `existe pour empêcher. Pour une antériorité opposable, il faut déposer `
  + `l'empreinte du fichier auprès d'un service d'horodatage — c'est la `
  + `procédure du protocole complet, pas celle de cette fiche.`;

/**
 * Ce que la fiche NE demande PAS, et pourquoi.
 *
 * Rendu au même titre que le reste : une omission qu'on ne peut pas lire ne
 * peut pas être contestée.
 */
export const CHAMPS_ECARTES: [string, string][] = [
  [
    'Pression atmosphérique',
    `Elle entre dans le coefficient de réfraction, mais très loin derrière `
    + `le gradient vertical de température : à pression réaliste, sa `
    + `contribution est du second ordre. Notez-la si vous avez un baromètre, `
    + `ne faites pas un détour pour elle.`,
  ],
  [
    `Focale, ouverture, heure exacte du déclenchement`,
    `Le fichier de l'appareil les porte déjà. Les recopier à la main `
    + `ajoute une occasion de se tromper sans ajouter d'information — il `
    + `suffit de conserver le fichier d'origine.`,
  ],
  [
    'Humidité, visibilité annoncée, force du vent',
    `Elles expliquent qu'une image soit belle ou ratée, pas où se trouve `
    + `le bord de la cible. Ce qui décide de la recevabilité d'une image se `
    + `constate sur l'image.`,
  ],
  [
    'Un jugement sur ce que vous voyez',
    `« On voit la base » ou « on ne la voit pas » est précisément la `
    + `question que le protocole remplace par une mesure. La fiche ne `
    + `demande donc aucune appréciation, seulement des grandeurs.`,
  ],
];

/** Une grandeur à consigner sur place. */
export interface Champ {
  libelle: string;
  /** L'unité attendue, ou null quand la réponse n'est pas un nombre. */
  unite: string | null;
  /** Pourquoi ce champ est demandé. UNE phrase — la fiche est lue debout. */
  pourquoi: string;
  obligatoire: boolean;
}

/** Un bloc de la fiche. */
export interface Section {
  numero: string;
  titre: string;
  releves: [string, string][];
  champs: Champ[];
  consignes: string[];
  reserves: string[];
  /** Vrai pour le bloc de dépôt, qui ne se lit qu'après la prise de vue. */
  sousScelle: boolean;
}

export interface FicheTerrain {
  milieu: string;
  milieuNom: string;
  referenceVerticale: string;
  titre: string;
  sousTitre: string;
  horodatage: string;
  discriminante: boolean;
  sections: Section[];
  champsEcartes: [string, string][];
}

export interface EntreeFiche {
  milieu: string;
  /** ISO 8601, FOURNI par l'appelant : ce module ne lit jamais l'heure. */
  horodatage: string;
  obsLatitude: number;
  obsLongitude: number;
  obsLibelle: string | null;
  cibleLatitude: number;
  cibleLongitude: number;
  cibleLibelle: string | null;
  distanceM: number;
  azimutDeg: number;
  hauteurObservateurM: number;
  hauteurCibleM: number;
  masqueeEnveloppeMinM: number;
  masqueeEnveloppeMaxM: number;
  kEmploye: number;
  kPersonnalise: boolean;
  verdict: Verdict;
}

// ── Les formateurs propres à la fiche ───────────────────────────────────────
//
// Les grandeurs partagées avec l'écran passent par les formateurs exportés de
// `simulation` : deux implémentations d'un même chiffre finiraient par en
// rendre deux valeurs différentes.

// Tous passent par `formatDecimal`, qui arrondit comme le « %.*f » du
// Python — demi vers le pair. `toFixed` arrondirait les égalités à l'écart de
// zéro, et rendrait 1,3 là où le paquet de référence rend 1,2.
const km = (m: number) => formatDecimal(m / 1000, 2).replace('.', ',');
const deg = (x: number) => formatDecimal(x, 1).replace('.', ',');
const coord = (lat: number, lon: number) =>
  `${formatDecimal(lat, 5)}, ${formatDecimal(lon, 5)}`.replaceAll('.', ',');

/**
 * Un point, avec son libellé quand il y en a un.
 *
 * Les coordonnées sont TOUJOURS écrites, même quand un libellé existe : sur le
 * terrain, c'est le chiffre qu'on entre dans le GPS, et un nom de lieu ne se
 * saisit pas dans un appareil.
 */
function point(lat: number, lon: number, libelle: string | null): string {
  const brut = coord(lat, lon);
  return libelle ? `${libelle} (${brut})` : brut;
}

/**
 * La taille angulaire de l'écart, en minutes d'arc.
 *
 * C'est la grandeur qui dit si l'écart est photographiable : deux modèles qui
 * diffèrent de 40 m à 35 km diffèrent de près de 4 minutes d'arc, ce qu'un
 * téléobjectif montre sans peine ; les mêmes 40 m à 3 000 km ne feraient plus
 * rien de mesurable.
 */
function arcmin(ecartM: number, distanceM: number): string {
  if (distanceM <= 0) throw new FicheError('La distance doit être strictement positive.');
  // L'ordre des opérations suit celui du Python : (écart / distance) × 10800
  // puis ÷ π. Regrouper autrement changerait le dernier chiffre.
  return formatDecimal((ecartM / distanceM) * 10800 / Math.PI, 2).replace('.', ',');
}

/**
 * Combien de pixels de haut la cible doit occuper sur l'image.
 *
 * LE CALCUL PART DU SEUIL, PAS DU RÉSULTAT — et c'est tout le point. Diviser
 * PIXELS_MIN_ECART par la fraction réellement masquée donnerait un nombre
 * juste qui annonce au volontaire la grandeur même qu'il doit mesurer : à
 * 20 pixels d'écart pour 55 pixels de cible, la fraction se retrouve en une
 * division, et le bloc sous scellé ne scellerait plus rien.
 *
 * Le seuil, lui, ne dépend pas du résultat. Et il suffit : une visée
 * discriminante masque au moins `seuil` de la hauteur, donc exige MOINS de
 * pixels que ce que le seuil demande.
 */
function hauteurApparenteMinPx(seuil: number): number | null {
  if (seuil <= 0) return null;
  return Math.ceil(PIXELS_MIN_ECART / seuil);
}

/**
 * Construit la fiche à partir d'une simulation déjà faite.
 *
 * `horodatage` est FOURNI, jamais lu sur l'horloge : sans cela le module ne
 * serait pas reproductible et ses vecteurs d'or n'épingleraient rien.
 */
export function construireFiche(e: EntreeFiche): FicheTerrain {
  const m = MILIEUX[e.milieu];
  if (!m) {
    throw new FicheError(
      `Milieu inconnu : '${e.milieu}'. Les milieux couverts sont `
      + `${Object.keys(MILIEUX).sort().join(', ')}.`,
    );
  }
  if (e.distanceM <= 0) throw new FicheError('La distance doit être strictement positive.');
  if (e.hauteurCibleM <= 0) {
    throw new FicheError('La hauteur de la cible doit être strictement positive.');
  }
  if (e.hauteurObservateurM < 0) {
    throw new FicheError(`La hauteur de l'observateur ne peut pas être négative.`);
  }
  if (e.horodatage.trim() === '') {
    throw new FicheError(
      `L'horodatage manque : sans lui, le bloc de dépôt ne dit pas à quel `
      + `moment la prédiction a été fixée, et il n'a plus d'objet.`,
    );
  }

  const reference = m.reference;
  const aquatique = e.milieu === 'lac' || e.milieu === 'mer';
  const v = e.verdict;

  // ── 01 · Ce sur quoi la simulation a tourné ─────────────────────────────
  const sectionVisee: Section = {
    numero: '01',
    titre: 'La visée simulée',
    releves: [
      ['Milieu', m.nom],
      ['Niveau de référence', `le ${reference}`],
      ['Observateur', point(e.obsLatitude, e.obsLongitude, e.obsLibelle)],
      [`Hauteur d'objectif employée`,
        `${formatMetres(e.hauteurObservateurM)} m au-dessus du ${reference}`],
      ['Cible', point(e.cibleLatitude, e.cibleLongitude, e.cibleLibelle)],
      ['Hauteur de cible employée',
        `${formatMetres(e.hauteurCibleM)} m, base prise au ${reference}`],
      ['Distance géodésique', `${km(e.distanceM)} km`],
      ['Azimut de départ', `${deg(e.azimutDeg)}°`],
      ['Coefficient de réfraction', `k = ${formatK(e.kEmploye)} (${
        e.kPersonnalise ? 'déclaré par vous' : 'moyenne standard, non mesurée'
      })`],
    ],
    champs: [],
    consignes: [],
    reserves: [MOTIF_MILIEU_SANS_EFFET, m.reserve],
    sousScelle: false,
  };

  // ── 02 · Ce qu'il faut rapporter ────────────────────────────────────────
  const champs: Champ[] = [
    {
      libelle: `Hauteur de l'objectif au-dessus du ${reference}, mesurée`,
      unite: 'm',
      pourquoi: `C'est le paramètre le plus sensible de toute la visée : près `
        + `de la surface, quelques dizaines de centimètres changent `
        + `l'occultation de façon visible. La simulation a tourné sur `
        + `${formatMetres(e.hauteurObservateurM)} m — si votre mesure diffère, `
        + `c'est elle qui compte.`,
      obligatoire: true,
    },
    {
      libelle: 'La même hauteur, remesurée en fin de série',
      unite: 'm',
      pourquoi: `Une embarcation s'enfonce, une marée monte, un trépied `
        + `s'enfonce dans le sable. Deux valeurs qui diffèrent ne `
        + `gâchent rien : elles disent que la série porte un intervalle `
        + `et non un point.`,
      obligatoire: true,
    },
    {
      libelle: 'Position GPS relevée sur place',
      unite: null,
      pourquoi: `Si elle diffère du point simulé, la distance change, donc la `
        + `prédiction. Relever le point réel permet de refaire le calcul `
        + `au lieu de jeter la série.`,
      obligatoire: true,
    },
    {
      libelle: 'Date, heure et fuseau du début de série',
      unite: null,
      pourquoi: `Sans l'heure, ni la marée ni les températures ne peuvent être `
        + `retrouvées après coup, et l'objection « c'était la `
        + `réfraction » devient invérifiable dans les deux sens.`,
      obligatoire: true,
    },
  ];

  if (e.milieu === 'mer') {
    champs.push({
      libelle: 'Hauteur de marée à cette heure, et port de référence',
      unite: 'm',
      pourquoi: `Le niveau de la mer EST le niveau de référence de ce calcul. `
        + `Une marée de plusieurs mètres déplace d'autant votre hauteur `
        + `d'objectif et la base de la cible.`,
      obligatoire: true,
    });
  } else if (e.milieu === 'lac') {
    champs.push({
      libelle: 'Cote du lac, si une échelle limnimétrique est visible',
      unite: 'm',
      pourquoi: `Le niveau d'un lac bouge peu mais il bouge, et une cote `
        + `relevée vaut mieux qu'une cote supposée. Notez « non `
        + `relevée » plutôt que de deviner.`,
      obligatoire: false,
    });
  }

  champs.push({
    libelle: `Température de l'air à hauteur d'objectif`,
    unite: '°C',
    pourquoi: `Elle n'entre PAS dans le calcul, qui tourne sur k = `
      + `${formatK(K_STANDARD)}. Elle sert à ce qu'un tiers puisse borner k `
      + `après coup et contester ce choix.`,
    obligatoire: true,
  });
  champs.push({
    libelle: aquatique
      ? `Température de l'eau en surface`
      : `Température de l'air à deux mètres du sol`,
    unite: '°C',
    pourquoi: `C'est l'ÉCART entre cette valeur et la précédente qui compte, et `
      + `son signe : il dit dans quel sens la réfraction s'écarte de la `
      + `moyenne employée. Deux températures sans leur écart ne servent à `
      + `rien, et l'écart sans son signe non plus.`,
    obligatoire: true,
  });
  champs.push({
    libelle: 'Appareil, objectif, et zoom optique ou numérique',
    unite: null,
    pourquoi: `La focale est dans le fichier, le matériel ne l'est pas toujours. `
      + `Un zoom numérique n'ajoute aucun détail : le savoir évite de `
      + `mesurer un bord qui n'a été qu'agrandi.`,
    obligatoire: true,
  });

  const px = hauteurApparenteMinPx(v.seuilApplique);
  champs.push({
    libelle: `Hauteur de la cible sur l'image, en pixels`,
    unite: 'px',
    pourquoi: px !== null
      ? `Au seuil de ${formatPourcent(v.seuilApplique)} %, un écart de `
        + `${PIXELS_MIN_ECART} pixels demande une cible de ${px} pixels de `
        + `haut : zoomez jusque-là. Ce nombre est tiré du SEUIL et non de `
        + `votre résultat — le donner à partir du résultat reviendrait à vous `
        + `annoncer la grandeur que vous devez mesurer.`
      : `Aucun seuil n'étant appliqué, aucune exigence de cadrage ne peut `
        + `être formulée : notez la hauteur en pixels, elle servira à dire `
        + `après coup si la mesure était possible.`,
    obligatoire: true,
  });

  const sectionMesures: Section = {
    numero: '02',
    titre: 'À consigner sur place',
    releves: [], champs, consignes: [], reserves: [], sousScelle: false,
  };

  // ── 03 · Le cadrage ────────────────────────────────────────────────────
  const consignes: string[] = [
    `Trépied, ou appui ferme sur un point fixe. À longue focale, le flou `
    + `de bougé se confond avec le bord de la cible — et le bord est `
    + `exactement ce qu'on mesure.`,
    `Deux photographies par série au minimum : une LARGE qui montre le `
    + `contexte et le niveau de référence, une au ZOOM MAXIMAL sur la `
    + `cible. La large prouve de quoi on parle, la serrée sert à mesurer.`,
    `Vérifier l'horizontalité au niveau à bulle ou au niveau de `
    + `l'appareil, et la noter. Une bascule fait paraître masquée une base `
    + `qui ne l'est pas.`,
    `Photographier le mètre ou la mire au moment où vous mesurez la `
    + `hauteur d'objectif. Une hauteur écrite sans image est une `
    + `déclaration, pas une mesure.`,
    `Ne rien recadrer, rien redresser, pas de HDR ni de correction `
    + `automatique. Conserver le fichier d'origine tel que sorti de `
    + `l'appareil, en plus de toute version retouchée.`,
    `Refaire la série au moins deux fois, à quelques minutes `
    + `d'intervalle. La réfraction change vite ; deux séries qui donnent la `
    + `même chose valent mieux qu'une série isolée.`,
  ];
  consignes.push(aquatique
    ? `Photographier la ligne d'eau au pied de la cible si elle est `
      + `visible : c'est le repère de la base, et c'est ce repère que la `
      + `mesure cherche.`
    : `Photographier le terrain intermédiaire depuis le poste, aussi `
      + `loin que possible. Sur terre, c'est la seule pièce qui permettra `
      + `de discuter un pli de terrain — et sans elle la série ne pourra `
      + `pas conclure.`);

  const sectionCadrage: Section = {
    numero: '03',
    titre: 'Consignes de prise de vue',
    releves: [], champs: [], consignes, reserves: [], sousScelle: false,
  };

  // ── 04 · Ce que la sortie ne pourra pas établir ────────────────────────
  const reservesFinales: string[] = [
    `Cette observation ne conclura rien sur la forme de la Terre à elle `
    + `seule. Elle confronte une mesure à ce que deux modèles géométriques `
    + `prédisent, sur les données que vous aurez rapportées.`,
    `Aucun modèle de terrain n'est employé. Une haie, un cargo, un `
    + `bâtiment récent ne figurent dans aucun calcul : c'est sur l'image `
    + `qu'il faut montrer qu'aucun obstacle ne masque la base.`,
    `Un verdict « indéterminé » est un résultat. Il arrive dès que les `
    + `données atmosphériques manquent, et le déclarer vaut mieux que de `
    + `trancher sans elles.`,
  ];
  if (!v.discriminante) {
    reservesFinales.unshift(
      `Cette visée n'est PAS discriminante : les deux modèles y `
      + `prédisent des choses trop proches pour qu'une photographie les `
      + `sépare. La sortie peut se faire, elle ne départagera rien. Viser `
      + `plus loin, ou plus bas, ou une cible plus courte.`,
    );
  }
  const sectionLimites: Section = {
    numero: '04',
    titre: 'Ce que cette sortie ne pourra pas établir',
    releves: [], champs: [], consignes: [],
    reserves: reservesFinales, sousScelle: false,
  };

  // ── 05 · Le dépôt, sous scellé ─────────────────────────────────────────
  const depot: [string, string][] = [
    ['Fiche générée le', e.horodatage],
    ['Modèle sphérique — masqué à la base', `${formatMetres(v.hauteurMasqueeBaseM)} m`],
    ['Soit, en fraction de la cible', `${formatPourcent(v.fractionMasqueeBase)} %`],
    ['Modèle plat — masqué à la base', `${formatMetres(v.hauteurMasqueePlatM)} m`],
    ['Écart entre les deux prédictions', `${formatMetres(v.ecartEntreModelesM)} m`],
    ['Taille angulaire de cet écart',
      `${arcmin(v.ecartEntreModelesM, e.distanceM)} minutes d'arc`],
    ['Seuil retenu',
      `${formatPourcent(v.seuilApplique)} % de la hauteur de la cible, soit `
      + `${formatMetres(e.hauteurCibleM * v.seuilApplique)} m ici`],
    ['Verdict géométrique',
      v.discriminante ? 'visée discriminante' : 'visée NON discriminante'],
  ];
  if (!e.kPersonnalise) {
    depot.push([
      'Enveloppe de réfraction',
      `de ${formatMetres(e.masqueeEnveloppeMinM)} à `
      + `${formatMetres(e.masqueeEnveloppeMaxM)} m masqués, pour k entre `
      + `${formatK(K_ENVELOPPE_MIN)} et ${formatK(K_ENVELOPPE_MAX)}`,
    ]);
  }

  const reservesDepot: string[] = [v.motif, MOTIF_HORODATAGE];
  if (!e.kPersonnalise) {
    reservesDepot.push(
      `La conclusion doit tenir sur TOUTE l'enveloppe ci-dessus. Si une `
      + `seule valeur admissible de k réconcilie ce que vous avez mesuré `
      + `avec la prédiction, le modèle n'est pas départagé — et c'est un `
      + `résultat, pas un échec.`,
    );
  }
  if (v.fractionMasqueeBase >= 1) {
    reservesDepot.push(
      `La fraction masquée dépasse 100 % : sur le modèle sphérique, la `
      + `cible est entièrement sous l'horizon géométrique, et de `
      + `${formatMetres(v.hauteurMasqueeBaseM - e.hauteurCibleM)} m `
      + `au-delà de son propre sommet. L'observation devient alors `
      + `binaire — on voit quelque chose, ou rien — et c'est le cas où la `
      + `réfraction explique le plus facilement une visibilité `
      + `inattendue. Les deux températures deviennent la pièce `
      + `principale.`,
    );
  }
  const sectionDepot: Section = {
    numero: '05',
    titre: `Prédiction déposée — à ne lire qu'après la prise de vue`,
    releves: depot, champs: [], consignes: [],
    reserves: reservesDepot, sousScelle: true,
  };

  return {
    milieu: e.milieu,
    milieuNom: m.nom,
    referenceVerticale: reference,
    titre: 'Fiche protocole terrain',
    sousTitre: `${m.nom} — visée de ${km(e.distanceM)} km, cible de `
      + `${formatMetres(e.hauteurCibleM)} m`,
    horodatage: e.horodatage,
    discriminante: v.discriminante,
    sections: [
      sectionVisee, sectionMesures, sectionCadrage, sectionLimites,
      // Le dépôt EN DERNIER, pour qu'il soit la partie qu'on replie ou qu'on
      // découpe avant de partir. Au milieu de la page, une consigne « ne pas
      // lire » ne tient pas une seconde.
      sectionDepot,
    ],
    champsEcartes: CHAMPS_ECARTES,
  };
}

// ── Le rendu texte ──────────────────────────────────────────────────────────

/**
 * Replie un paragraphe, avec une indentation PENDANTE.
 *
 * `premier` préfixe la première ligne, `suite` les autres. Sans cela, la
 * deuxième ligne d'une consigne revient à la marge et la numérotation cesse de
 * se lire : la liste devient un pavé.
 *
 * Écrit à la main de part et d'autre — le Python n'emploie pas `textwrap` non
 * plus — pour que les deux implémentations coupent aux MÊMES endroits. Un mot
 * plus long que la largeur déborde plutôt que d'être coupé : une coupure au
 * milieu d'un nombre serait pire que la ligne longue.
 */
export function replier(
  texte: string, largeur: number, premier = '', suite: string | null = null,
): string[] {
  const marge2 = suite === null ? ' '.repeat(premier.length) : suite;
  const mots = texte.split(' ').filter((x) => x !== '');
  const lignes: string[] = [];
  let courante = '';
  for (const mot of mots) {
    const essai = courante === '' ? mot : `${courante} ${mot}`;
    const marge = lignes.length === 0 ? premier : marge2;
    if (marge.length + essai.length <= largeur || courante === '') {
      courante = essai;
    } else {
      lignes.push(marge + courante);
      courante = mot;
    }
  }
  if (courante !== '') lignes.push((lignes.length === 0 ? premier : marge2) + courante);
  return lignes.length > 0 ? lignes : [premier.replace(/\s+$/, '')];
}

/**
 * La fiche en texte pur, imprimable et lisible dans un courriel.
 *
 * Le texte pur est le format qui survit à tout : pas de police à charger, pas
 * de visionneuse, pas de mise en page qui casse. C'est aussi celui qui se
 * relit dix ans plus tard.
 */
export function rendreTxt(fiche: FicheTerrain, largeur = LARGEUR_TXT): string {
  const out: string[] = [];
  out.push(fiche.titre.toUpperCase());
  out.push(fiche.sousTitre);
  out.push('Simulateur de Visée — Terre Étendue Islam');
  out.push('='.repeat(largeur));

  for (const s of fiche.sections) {
    out.push('');
    out.push(`${s.numero} · ${s.titre.toUpperCase()}`);
    out.push('-'.repeat(largeur));
    if (s.sousScelle) {
      out.push(...replier(MOTIF_AVEUGLE, largeur, '  ! ', '    '));
      out.push('');
    }

    for (const [cle, valeur] of s.releves) {
      // La clé préfixe la première ligne ; les suivantes s'alignent sous la
      // VALEUR, pas sous la clé, pour que la colonne se lise.
      out.push(...replier(valeur, largeur, `  ${cle} : `));
    }

    for (const c of s.champs) {
      const unite = c.unite ? ` (${c.unite})` : '';
      const marque = c.obligatoire ? '[ ] ' : '[~] ';
      out.push(...replier(`${c.libelle}${unite}`, largeur, `  ${marque}`, '      '));
      out.push(`      ${'.'.repeat(largeur - 6)}`);
      out.push(...replier(c.pourquoi, largeur, '      → ', '        '));
      out.push('');
    }

    s.consignes.forEach((texte, i) => {
      const tete = `  ${i + 1}. `;
      out.push(...replier(texte, largeur, tete, ' '.repeat(tete.length)));
      out.push('');
    });

    for (const texte of s.reserves) {
      out.push(...replier(texte, largeur, '  · ', '    '));
      out.push('');
    }
  }

  out.push('='.repeat(largeur));
  out.push('CE QUE CETTE FICHE NE DEMANDE PAS, ET POURQUOI');
  out.push('-'.repeat(largeur));
  for (const [titre, motif] of fiche.champsEcartes) {
    out.push(...replier(titre, largeur, '  – ', '    '));
    out.push(...replier(motif, largeur, '      '));
    out.push('');
  }

  // Un fichier texte se termine par un saut de ligne : c'est la convention, et
  // certains outils avalent la dernière ligne sans lui.
  return `${out.join('\n').replace(/\n+$/, '')}\n`;
}

/**
 * Un nom de fichier sans accent, sans espace et sans surprise.
 *
 * Ni l'horodatage ni le libellé du lieu n'y entrent : le premier contient des
 * deux-points, refusés par certains systèmes de fichiers, et le second des
 * accents et des apostrophes.
 */
export function nomFichier(fiche: FicheTerrain, distanceM: number): string {
  return `fiche-terrain-${fiche.milieu}-${formatDecimal(distanceM / 1000, 0)}-km.txt`;
}
