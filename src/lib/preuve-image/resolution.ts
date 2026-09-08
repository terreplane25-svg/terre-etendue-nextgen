/**
 * resolution.ts — Port TypeScript de `preuve_image.resolution` (outil B).
 *
 * CE FICHIER N'EST PAS LA RÉFÉRENCE.
 * La référence est `outils/outil-B-preuve-image/preuve_image/resolution.py`.
 * Ce port est épinglé au Python par `vecteurs-or-resolution.json`, que
 * `scripts/verifier-port-resolution.mjs` rejoue ici.
 *
 * CE QUE CE MODULE ÉTABLIT, ET CE QU'IL SE REFUSE À ÉTABLIR
 * ────────────────────────────────────────────────────────
 * La directive demandait un « référentiel global des définitions d'écrans »
 * pour rapprocher une résolution d'un appareil du marché. Ce référentiel
 * n'existe pas dans ce dépôt : `ECRANS_CONNUS` reste VIDE.
 *
 * Mais le signal serait faible même vérifié, et c'est le point important :
 * 1179 × 2556 identifie une capture d'écran d'iPhone 15 Pro autant que
 * n'importe quelle image recadrée à ces dimensions.
 *
 * CE QUI EST VÉRIFIABLE, ET QUI VAUT MIEUX
 * ───────────────────────────────────────
 * Le rapport d'aspect EXACT, en fraction réduite — de l'arithmétique, sans
 * référentiel. Et surtout la COHÉRENCE entre les dimensions LUES DANS LES
 * OCTETS (marqueur SOF d'un JPEG, IHDR d'un PNG) et celles DÉCLARÉES dans
 * l'EXIF. Un écart ÉTABLIT que le fichier a été redimensionné ou recadré sans
 * que la métadonnée suive : les deux grandeurs sont écrites à des moments
 * différents, par des outils différents.
 */

/**
 * Le référentiel des écrans d'appareils. VIDE, et c'est délibéré.
 *
 * Y écrire « 1179 × 2556 = iPhone 15 Pro » de mémoire produirait une
 * identification fausse présentée comme un fait.
 */
export const ECRANS_CONNUS: Record<string, string> = {};

/**
 * Les dénominations d'USAGE. Ce ne sont PAS des identifications d'appareil :
 * ce sont les noms sous lesquels ces dimensions circulent, et ils
 * n'attribuent rien. Leur valeur probatoire est nulle.
 */
export const DEFINITIONS_NOMMEES: Record<string, string> = {
  '640x480': 'VGA',
  '800x600': 'SVGA',
  '1024x768': 'XGA',
  '1280x720': '720p',
  '1280x1024': 'SXGA',
  '1366x768': 'WXGA',
  '1600x900': 'HD+',
  '1920x1080': '1080p',
  '2048x1080': '2K DCI',
  '2560x1440': '1440p',
  '3840x2160': '2160p (UHD)',
  '4096x2160': '4K DCI',
  '7680x4320': '4320p (UHD-2)',
};

export const MOTIF_AUCUN_ECRAN =
  "Aucun rapprochement avec un appareil : il n'existe pas de référentiel "
  + "vérifié des définitions d'écrans dans ce dépôt, et en écrire un de mémoire "
  + 'produirait des correspondances fausses présentées comme des faits. Le '
  + "signal serait d'ailleurs faible même vérifié — une résolution de "
  + "1179 × 2556 identifie une capture d'écran d'iPhone 15 Pro autant que "
  + "n'importe quelle image recadrée à ces dimensions. Ce qui est rendu à la "
  + "place se vérifie : le rapport d'aspect exact, et la cohérence entre les "
  + "dimensions mesurées et celles que l'EXIF déclare.";

export const MOTIF_DENOMINATION =
  "Une dénomination d'usage, sans valeur probatoire. Elle dit sous quel nom "
  + "ces dimensions circulent, jamais d'où vient l'image : un cliché recadré "
  + "à 1920 × 1080 porte le même nom qu'une capture d'écran.";

export const MOTIF_ALIGNEMENT =
  'Un JPEG code par blocs de 8 × 8 pixels, groupés en unités de 8 ou 16 '
  + 'selon le sous-échantillonnage. Des dimensions non alignées sur cette '
  + "unité signifient que le bord de l'image est un bloc partiel, ce qui "
  + 'arrive à tout recadrage. Le signal est faible dans les deux sens : la '
  + 'plupart des appareils produisent des dimensions alignées, et un '
  + "alignement n'établit pas l'absence de recadrage.";

function pgcd(a: number, b: number): number {
  let x = Math.abs(a);
  let y = Math.abs(b);
  while (y !== 0) {
    const t = y;
    y = x % y;
    x = t;
  }
  return x;
}

/**
 * Le rapport d'aspect en fraction réduite. Arithmétique, sans référentiel.
 *
 * 3024 × 4032 rend [3, 4] et non [4, 3] : l'ordre suit les dimensions reçues,
 * parce qu'une image portrait n'est pas une image paysage.
 */
export function rapportExact(largeur: number, hauteur: number): [number, number] {
  if (largeur <= 0 || hauteur <= 0) {
    throw new Error('Les dimensions doivent être strictement positives.');
  }
  const d = pgcd(largeur, hauteur);
  return [largeur / d, hauteur / d];
}

/** Ce que les dimensions d'une image permettent de dire. */
export interface Resolution {
  /** Les dimensions LUES DANS LES OCTETS. C'est la mesure. */
  largeurMesuree: number | null;
  hauteurMesuree: number | null;
  /** Les dimensions DÉCLARÉES dans l'EXIF. C'est une déclaration. */
  largeurDeclaree: number | null;
  hauteurDeclaree: number | null;
  /**
   * Vrai quand les deux coïncident, faux quand elles diffèrent, null quand
   * l'une des deux manque — jamais faux par défaut.
   */
  dimensionsCoherentes: boolean | null;
  motifEcart: string | null;
  rapport: [number, number] | null;
  rapportDecimal: number | null;
  orientation: string | null;
  megapixels: number | null;
  /** La dénomination d'usage. Sans valeur probatoire. */
  denomination: string | null;
  /** L'unité d'alignement JPEG respectée, ou null. 16 implique 8. */
  alignementJpeg: number | null;
  /** L'appareil rapproché. Toujours null : le référentiel est vide. */
  ecranRapproche: string | null;
  motifAucunEcran: string;
}

/**
 * Confronte les dimensions mesurées aux dimensions déclarées.
 *
 * Les deux jeux sont rendus SÉPARÉMENT, jamais l'un à la place de l'autre :
 * c'est leur écart qui porte l'information.
 */
export function analyserResolution(
  largeurMesuree: number | null,
  hauteurMesuree: number | null,
  largeurDeclaree: number | null = null,
  hauteurDeclaree: number | null = null,
): Resolution {
  const positif = (x: number | null): x is number => x !== null && x > 0;
  const aMesure = positif(largeurMesuree) && positif(hauteurMesuree);
  const aDeclare = positif(largeurDeclaree) && positif(hauteurDeclaree);

  let coherentes: boolean | null = null;
  let motifEcart: string | null = null;
  if (aMesure && aDeclare) {
    coherentes = largeurMesuree === largeurDeclaree && hauteurMesuree === hauteurDeclaree;
    if (!coherentes) {
      motifEcart =
        `Les octets portent ${largeurMesuree} × ${hauteurMesuree}, l'EXIF déclare `
        + `${largeurDeclaree} × ${hauteurDeclaree}. L'écart `
        + 'ÉTABLIT que le fichier a été redimensionné ou recadré sans '
        + 'que la métadonnée suive : les deux grandeurs sont écrites à '
        + "des moments différents, par des outils différents. Ce qu'il "
        + "n'établit pas, c'est lequel des deux est le bon, ni qui a "
        + 'fait la modification.';
    }
  }

  let rapport: [number, number] | null = null;
  let rapportDecimal: number | null = null;
  let orientation: string | null = null;
  let megapixels: number | null = null;
  let denomination: string | null = null;
  let alignement: number | null = null;
  if (aMesure) {
    rapport = rapportExact(largeurMesuree, hauteurMesuree);
    rapportDecimal = largeurMesuree / hauteurMesuree;
    if (largeurMesuree > hauteurMesuree) orientation = 'paysage';
    else if (largeurMesuree < hauteurMesuree) orientation = 'portrait';
    else orientation = 'carré';
    megapixels = (largeurMesuree * hauteurMesuree) / 1e6;
    // La dénomination se cherche dans les deux sens : une capture portrait
    // porte le même nom que son pendant paysage.
    denomination = DEFINITIONS_NOMMEES[`${largeurMesuree}x${hauteurMesuree}`]
      ?? DEFINITIONS_NOMMEES[`${hauteurMesuree}x${largeurMesuree}`]
      ?? null;
    if (largeurMesuree % 16 === 0 && hauteurMesuree % 16 === 0) alignement = 16;
    else if (largeurMesuree % 8 === 0 && hauteurMesuree % 8 === 0) alignement = 8;
  }

  return {
    largeurMesuree: aMesure ? largeurMesuree : null,
    hauteurMesuree: aMesure ? hauteurMesuree : null,
    largeurDeclaree: aDeclare ? largeurDeclaree : null,
    hauteurDeclaree: aDeclare ? hauteurDeclaree : null,
    dimensionsCoherentes: coherentes,
    motifEcart,
    rapport,
    rapportDecimal,
    orientation,
    megapixels,
    denomination,
    alignementJpeg: alignement,
    // Le référentiel est vide : le rapprochement ne peut rien rendre.
    ecranRapproche: ECRANS_CONNUS[`${largeurMesuree ?? 0}x${hauteurMesuree ?? 0}`] ?? null,
    motifAucunEcran: MOTIF_AUCUN_ECRAN,
  };
}
