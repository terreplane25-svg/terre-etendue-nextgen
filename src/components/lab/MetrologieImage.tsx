'use client';
/**
 * MetrologieImage — Analyse d'image par métrologie optique.
 *
 * Expose l'outil D du protocole « Portion visible d'une cible éloignée
 * au-dessus de la mer » v1.0, via le port TypeScript de
 * `src/lib/metrologie-image/` — port épinglé au paquet Python par 786
 * contrôles (voir scripts/verifier-port-metrologie.mjs). La géométrie du §9
 * vient du port de l'outil A, l'empreinte et l'EXIF du port de l'outil B :
 * rien n'est recalculé ici.
 *
 * L'image ne quitte jamais la machine. Tout — empreinte, EXIF, angles,
 * inversion, exports — se fait dans le navigateur.
 *
 * Cinq règles gouvernent cette interface, et elles ne sont pas cosmétiques :
 *
 *  1. Aucun champ n'est prérempli d'une valeur plausible. Les valeurs lues
 *     dans l'EXIF ne sont adoptées que sur un geste explicite, et arrivent
 *     alors avec « EXIF du fichier » pour source — parce que c'en est une,
 *     déclarative, et que l'opérateur doit la voir.
 *  2. Chaque grandeur exige sa source. Sans source, elle n'entre pas dans le
 *     calcul et l'interface le dit.
 *  3. Le résultat est une enveloppe. Quand l'angle relevé ne détermine pas k
 *     — cible entière, cible disparue, relevé hors modèle — l'outil affiche
 *     INDISPONIBLE et la raison, jamais une valeur de bout de domaine.
 *  4. Le clic sur l'horizon est un CONTRÔLE, pas une mesure : le rayon rasant
 *     qui définit l'horizon est le même qui définit le bas visible de la
 *     cible, donc les deux pointés coïncident. Le cahier des charges y voyait
 *     une « hauteur masquée par la courbure » ; elle n'existe pas.
 *  5. k n'est pas un verdict sur la forme de la Terre. Le modèle sphérique est
 *     une ENTRÉE de cette chaîne. C'est écrit à côté de chaque résultat.
 */
import { useCallback, useEffect, useMemo, useRef, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import { analyserFichier, type RapportFichier } from '@/lib/preuve-image/noyau';
import {
  CE_QUE_CA_N_ETABLIT_PAS,
  FACTEUR_ELARGISSEMENT,
  IUGG_R1,
  SIGMA_POINTE_PX_DEFAUT,
  anglePortionEmergente,
  cadrage as faireCadrage,
  cible as faireCible,
  capteur as faireCapteur,
  capteurEquivalent35mm,
  coefficientRefractionEffectif,
  controlerHorizon,
  echelleMParPx,
  enveloppeCoefficient,
  estRecadree,
  fractionVisible,
  hauteurEmergenteMesuree,
  hauteurEmergentePetitAngle,
  interpreter,
  objectif as faireObjectif,
  pasAngulaireRad,
  plage as fairePlage,
  pointes as fairePointes,
  pointPrincipalConnu,
  rayonEffectif,
  resolutionAngulaireLimiteRad,
  type Cadrage,
  type Capteur,
  type Objectif,
  type ResultatK,
} from '@/lib/metrologie-image/noyau';

const INDISPONIBLE = 'INDISPONIBLE';
const ACCENT = dash.cyan;
const COULEUR_HORIZON = '#3B8FD4';
const COULEUR_BASE = '#C45E6A';
const COULEUR_SOMMET = '#D4943A';

type Repere = 'horizon' | 'base' | 'sommet';

const REPERES: { cle: Repere; label: string; couleur: string; aide: string }[] = [
  {
    cle: 'horizon',
    label: '1 — Ligne d’horizon',
    couleur: COULEUR_HORIZON,
    aide: "La limite eau/ciel. Sert de CONTRÔLE : le modèle la prédit confondue avec le bas visible de la cible dès que celle-ci est partiellement occultée.",
  },
  {
    cle: 'base',
    label: '2 — Bas visible de la cible',
    couleur: COULEUR_BASE,
    aide: "Le point le plus bas encore visible, là où la cible sort de l’eau. Avec le clic 3, c’est la seule mesure de l’image.",
  },
  {
    cle: 'sommet',
    label: '3 — Sommet de la cible',
    couleur: COULEUR_SOMMET,
    aide: "Le sommet réel de l’ouvrage ou du relief, celui dont la hauteur H est déclarée plus haut.",
  },
];

interface Champ {
  valeur: string;
  incertitude: string;
  source: string;
}

const vide = (): Champ => ({ valeur: '', incertitude: '', source: '' });

interface Etat {
  // Appareil
  modeFocale: 'reelle' | 'equivalent35';
  largeurCapteurMm: Champ;
  largeurNativePx: Champ;
  hauteurNativePx: Champ;
  focaleMm: Champ;
  // Cadrage
  recadree: boolean;
  largeurRecadreePx: Champ;
  hauteurRecadreePx: Champ;
  origineXPx: Champ;
  origineYPx: Champ;
  origineConnue: boolean;
  // Scène
  distanceKm: Champ;
  altitudeObsM: Champ;
  hauteurCibleM: Champ;
  altitudeBaseM: Champ;
  // Relevé
  sigmaPx: string;
  diametrePupilleMm: Champ;
}

const ETAT_VIDE: Etat = {
  modeFocale: 'reelle',
  largeurCapteurMm: vide(),
  largeurNativePx: vide(),
  hauteurNativePx: vide(),
  focaleMm: vide(),
  recadree: false,
  largeurRecadreePx: vide(),
  hauteurRecadreePx: vide(),
  origineXPx: vide(),
  origineYPx: vide(),
  origineConnue: true,
  distanceKm: vide(),
  altitudeObsM: vide(),
  hauteurCibleM: vide(),
  altitudeBaseM: vide(),
  sigmaPx: String(SIGMA_POINTE_PX_DEFAUT),
  diametrePupilleMm: vide(),
};

function nombre(c: Champ): number | null {
  if (c.valeur.trim() === '') return null;
  const v = Number(c.valeur.replace(',', '.'));
  return Number.isFinite(v) ? v : null;
}

function incertitude(c: Champ): number {
  if (c.incertitude.trim() === '') return 0;
  const v = Number(c.incertitude.replace(',', '.'));
  return Number.isFinite(v) && v >= 0 ? v : 0;
}

function complet(c: Champ): boolean {
  return nombre(c) !== null && c.source.trim() !== '';
}

/**
 * Mise en forme française. Les valeurs plus petites que le dernier rang affiché
 * sont ramenées à zéro franc : sans cela, l'écart horizon/base — nul par
 * construction mais rendu à −10⁻¹⁵ par le calcul — s'affichait « −0,0 px », ce
 * qui se lit comme un défaut alors que c'est le résultat attendu.
 */
const fmt = (x: number, n = 3) => {
  const v = Math.abs(x) < 0.5 * 10 ** -n ? 0 : x;
  return v.toLocaleString('fr-FR', { minimumFractionDigits: n, maximumFractionDigits: n });
};

const arcsec = (rad: number) => (rad * 180.0 * 3600.0) / Math.PI;

/**
 * Grossissement de la loupe. C'est lui qui rend le pointé possible : sans elle,
 * la résolution de pointé est celle de l'affichage réduit — sur un téléphone,
 * plus de dix pixels d'image par pixel d'écran.
 */
const GROSSISSEMENT = 8;

/** Seuil de bascule en colonne unique. 768 px : la limite usuelle tablette / téléphone. */
const SEUIL_PETIT_ECRAN_PX = 768;

interface Ecran {
  petit: boolean;
  /** `pointer: coarse` — le doigt, ou un stylet imprécis. */
  grossier: boolean;
  /** Vrai tant que le navigateur n'a pas répondu : on ne suppose rien avant. */
  inconnu: boolean;
}

/**
 * Ce que l'écran est, mesuré et non supposé.
 *
 * Le composant est chargé sans rendu serveur (`ssr: false` dans LabClient), donc
 * `matchMedia` est disponible dès le premier rendu et il n'y a pas de
 * divergence d'hydratation à craindre. `inconnu` couvre le seul cas restant :
 * un environnement sans `matchMedia`, où l'on préfère ne rien affirmer.
 */
function useEcran(): Ecran {
  const [e, setE] = useState<Ecran>({ petit: false, grossier: false, inconnu: true });
  useEffect(() => {
    if (typeof window === 'undefined' || !window.matchMedia) return;
    const mqTaille = window.matchMedia(`(max-width: ${SEUIL_PETIT_ECRAN_PX - 1}px)`);
    const mqPointeur = window.matchMedia('(pointer: coarse)');
    const relire = () => setE({ petit: mqTaille.matches, grossier: mqPointeur.matches, inconnu: false });
    relire();
    mqTaille.addEventListener('change', relire);
    mqPointeur.addEventListener('change', relire);
    return () => {
      mqTaille.removeEventListener('change', relire);
      mqPointeur.removeEventListener('change', relire);
    };
  }, []);
  return e;
}

// ─────────────────────────────────────────────────────────────────────────────

function ChampNombre({
  cle, label, unite, champ, onChange, aide, avecIncertitude = true, pas,
}: {
  cle: string; label: string; unite: string; champ: Champ;
  onChange: (c: Champ) => void; aide: string; avecIncertitude?: boolean; pas?: string;
}) {
  const n = nombre(champ);
  const manqueSource = n !== null && champ.source.trim() === '';
  return (
    <div style={{ marginBottom: 13 }}>
      <label style={{
        display: 'block', fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.06em',
        color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 4,
      }}>
        {label} <span style={{ opacity: 0.6 }}>({unite})</span>
      </label>
      <div style={{ display: 'flex', gap: 6 }}>
        <input
          type="text" inputMode="decimal" value={champ.valeur} placeholder="—" step={pas}
          data-champ={`${cle}-valeur`} aria-label={`${label} — valeur`}
          onChange={(e) => onChange({ ...champ, valeur: e.target.value })}
          style={{
            flex: avecIncertitude ? 2 : 1, padding: '7px 9px', fontSize: 13,
            fontFamily: dash.fontMono, border: `1px solid ${dash.border}`,
            borderRadius: 4, background: 'var(--card)', color: 'var(--ink)',
          }}
        />
        {avecIncertitude && (
          <input
            type="text" inputMode="decimal" value={champ.incertitude} placeholder="± 0"
            data-champ={`${cle}-incertitude`} aria-label={`${label} — incertitude`}
            onChange={(e) => onChange({ ...champ, incertitude: e.target.value })}
            title="Demi-largeur de l’enveloppe. Laissée vide, elle vaut zéro — ce qui déclare la valeur exacte."
            style={{
              flex: 1, padding: '7px 9px', fontSize: 13, fontFamily: dash.fontMono,
              border: `1px solid ${dash.border}`, borderRadius: 4,
              background: 'var(--card)', color: 'var(--ink)',
            }}
          />
        )}
      </div>
      <input
        type="text" value={champ.source} placeholder="Source — obligatoire"
        data-champ={`${cle}-source`} aria-label={`${label} — source`}
        onChange={(e) => onChange({ ...champ, source: e.target.value })}
        style={{
          width: '100%', marginTop: 4, padding: '6px 9px', fontSize: 11,
          border: `1px solid ${manqueSource ? COULEUR_BASE : dash.border}`,
          borderRadius: 4, background: 'var(--card)', color: 'var(--ink-muted)',
        }}
      />
      <div style={{ fontSize: 10, color: manqueSource ? COULEUR_BASE : 'var(--ink-ghost)', marginTop: 3, lineHeight: 1.45 }}>
        {manqueSource ? 'Valeur saisie sans source : elle n’entre pas dans le calcul.' : aide}
      </div>
    </div>
  );
}

/**
 * Le contenu des outils du Lab vit dans des cartes claires : la fenêtre qui les
 * accueille a un fond sombre, et `var(--ink)` y serait illisible posé
 * directement. Un premier jet s'en dispensait — la capture d'écran de l'essai
 * de bout en bout a montré les valeurs en gris sombre sur bleu nuit.
 */
function Carte({ children, style }: { children: React.ReactNode; style?: React.CSSProperties }) {
  return (
    <div style={{
      background: 'var(--card)', border: '1px solid var(--border)',
      borderRadius: 10, padding: '18px 20px', marginBottom: 16, ...style,
    }}>
      {children}
    </div>
  );
}

function Ligne({ cle, label, valeur, note, accent }: {
  cle: string; label: string; valeur: string; note?: string; accent?: string;
}) {
  return (
    <div data-ligne={cle} style={{ padding: '7px 0', borderBottom: `1px solid ${dash.border}` }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12, alignItems: 'baseline' }}>
        <span style={{ fontSize: 11, color: 'var(--ink-muted)' }}>{label}</span>
        <span data-valeur={cle} style={{
          fontSize: 13, fontFamily: dash.fontMono, fontWeight: 600,
          color: valeur === INDISPONIBLE ? 'var(--ink-ghost)' : (accent || 'var(--ink)'),
          textAlign: 'right',
        }}>{valeur}</span>
      </div>
      {note && <div style={{ fontSize: 10, color: 'var(--ink-ghost)', marginTop: 2, lineHeight: 1.5 }}>{note}</div>}
    </div>
  );
}

// ─────────────────────────────────────────────────────────────────────────────

export default function MetrologieImage() {
  const [etat, setEtat] = useState<Etat>(ETAT_VIDE);
  const [image, setImage] = useState<HTMLImageElement | null>(null);
  const [nomFichier, setNomFichier] = useState('');
  const [rapport, setRapport] = useState<RapportFichier | null>(null);
  const [erreurFichier, setErreurFichier] = useState<string | null>(null);
  const [clics, setClics] = useState<Partial<Record<Repere, number>>>({});
  const [repereActif, setRepereActif] = useState<Repere>('horizon');
  const [loupe, setLoupe] = useState<{ x: number; y: number } | null>(null);
  /**
   * Pointé en cours, pas encore validé. Sur souris il est validé au relâchement
   * — le geste habituel. Sur tactile il ne l'est jamais tout seul : le doigt
   * masque ce qu'il désigne, et lever le doigt déplace souvent le contact de
   * quelques pixels. Il faut donc un geste séparé pour valider, et des boutons
   * de retouche au pixel.
   */
  const [provisoire, setProvisoire] = useState<number | null>(null);
  /** Largeur CSS du canevas au dernier tracé — sert à recalculer la résolution atteignable. */
  const [largeurRendue, setLargeurRendue] = useState(0);
  const ecran = useEcran();

  const canvasRef = useRef<HTMLCanvasElement | null>(null);
  const loupeRef = useRef<HTMLCanvasElement | null>(null);
  const conteneurRef = useRef<HTMLDivElement | null>(null);

  const maj = (k: keyof Etat, v: unknown) => setEtat((e) => ({ ...e, [k]: v }));

  // --- Chargement du fichier : empreinte et EXIF par l'outil B ---

  const charger = useCallback(async (fichier: File) => {
    setErreurFichier(null);
    setClics({});
    setRepereActif('horizon');
    try {
      const octets = new Uint8Array(await fichier.arrayBuffer());
      const r = await analyserFichier(fichier.name, fichier.type, octets);
      setRapport(r);
      setNomFichier(fichier.name);
      const url = URL.createObjectURL(fichier);
      const img = new Image();
      img.onload = () => { setImage(img); URL.revokeObjectURL(url); };
      img.onerror = () => {
        setErreurFichier("Le navigateur n’a pas su décoder cette image. Formats acceptés : JPEG, PNG, WebP.");
        URL.revokeObjectURL(url);
      };
      img.src = url;
    } catch (err) {
      setErreurFichier(err instanceof Error ? err.message : String(err));
    }
  }, []);

  /**
   * Adoption explicite des valeurs EXIF. Ce n'est pas un préremplissage : rien
   * ne bouge sans ce geste, et chaque valeur arrive avec sa source, qui dit
   * qu'elle est déclarative — l'appareil affirme, il ne prouve pas.
   */
  const adopterExif = () => {
    const e = rapport?.exif;
    if (!e) return;
    const src = `EXIF du fichier « ${nomFichier} » — déclaratif appareil, non vérifié`;
    setEtat((s) => {
      const n = { ...s };
      if (e.focaleEquivalente35mm !== null && s.modeFocale === 'equivalent35') {
        n.focaleMm = { ...n.focaleMm, valeur: String(e.focaleEquivalente35mm), source: src };
      } else if (e.focaleMm !== null) {
        n.focaleMm = { ...n.focaleMm, valeur: String(e.focaleMm), source: src };
      }
      if (e.largeurPx !== null) n.largeurNativePx = { ...n.largeurNativePx, valeur: String(e.largeurPx), source: src };
      if (e.hauteurPx !== null) n.hauteurNativePx = { ...n.hauteurNativePx, valeur: String(e.hauteurPx), source: src };
      return n;
    });
  };

  // --- Assemblage des objets du noyau ---

  const appareil = useMemo(() => {
    const fNum = nombre(etat.focaleMm);
    const wNat = nombre(etat.largeurNativePx);
    const hNat = nombre(etat.hauteurNativePx);
    const largeurMm = nombre(etat.largeurCapteurMm);
    if (fNum === null || wNat === null || hNat === null || !image) return null;
    if (etat.modeFocale === 'reelle' && largeurMm === null) return null;
    if (!complet(etat.focaleMm) || !complet(etat.largeurNativePx) || !complet(etat.hauteurNativePx)) return null;
    if (etat.modeFocale === 'reelle' && !complet(etat.largeurCapteurMm)) return null;
    try {
      const cap: Capteur = etat.modeFocale === 'equivalent35'
        ? capteurEquivalent35mm(wNat, hNat)
        : faireCapteur(largeurMm as number, wNat, hNat);
      const obj: Objectif = faireObjectif(fNum);
      const wRec = etat.recadree ? nombre(etat.largeurRecadreePx) : image.naturalWidth;
      const hRec = etat.recadree ? nombre(etat.hauteurRecadreePx) : image.naturalHeight;
      if (wRec === null || hRec === null) return null;
      const ox = etat.recadree && etat.origineConnue ? nombre(etat.origineXPx) : (etat.recadree ? null : 0);
      const oy = etat.recadree && etat.origineConnue ? nombre(etat.origineYPx) : (etat.recadree ? null : 0);
      const cad: Cadrage = faireCadrage(
        image.naturalWidth, image.naturalHeight, wRec, hRec,
        etat.recadree && etat.origineConnue ? (ox ?? null) : ox,
        etat.recadree && etat.origineConnue ? (oy ?? null) : oy,
      );
      return { cap, obj, cad };
    } catch {
      return null;
    }
  }, [etat, image]);

  const scene = useMemo(() => {
    const champs = [etat.distanceKm, etat.altitudeObsM, etat.hauteurCibleM, etat.altitudeBaseM];
    if (!champs.every(complet)) return null;
    try {
      const dKm = nombre(etat.distanceKm) as number;
      const dU = incertitude(etat.distanceKm);
      const D = fairePlage('distance', dKm * 1000, (dKm - dU) * 1000, (dKm + dU) * 1000, etat.distanceKm.source);
      const hV = nombre(etat.altitudeObsM) as number;
      const hU = incertitude(etat.altitudeObsM);
      const h = fairePlage('altitude_observateur', hV, Math.max(0, hV - hU), hV + hU, etat.altitudeObsM.source);
      const HV = nombre(etat.hauteurCibleM) as number;
      const HU = incertitude(etat.hauteurCibleM);
      const H = fairePlage('hauteur_cible', HV, Math.max(0.001, HV - HU), HV + HU, etat.hauteurCibleM.source);
      const zV = nombre(etat.altitudeBaseM) as number;
      const zU = incertitude(etat.altitudeBaseM);
      const zb = fairePlage('altitude_base', zV, Math.max(0, zV - zU), zV + zU, etat.altitudeBaseM.source);
      return { D, h, H, zb };
    } catch {
      return null;
    }
  }, [etat]);

  const troisClics = clics.horizon !== undefined && clics.base !== undefined && clics.sommet !== undefined;

  /**
   * Ce que l'écran permet vraiment, en pixels d'image.
   *
   * Le canevas affiche l'image réduite : un pixel d'écran vaut `f` pixels
   * d'image. La loupe divise cela par son grossissement. En dessous de cette
   * résolution, déclarer un σ plus fin revient à annoncer une précision que le
   * geste ne peut pas produire — exactement ce que le reste de la chaîne
   * s'interdit. La valeur est mesurée sur le canevas rendu, pas déduite d'une
   * hypothèse d'appareil.
   */
  const resolution = useMemo(() => {
    const cv = canvasRef.current;
    if (!cv || !image) return null;
    const largeurCss = cv.getBoundingClientRect().width;
    if (largeurCss <= 0) return null;
    const pxImageParPxEcran = image.naturalWidth / largeurCss;
    return {
      pxImageParPxEcran,
      sansLoupe: pxImageParPxEcran,
      avecLoupe: pxImageParPxEcran / GROSSISSEMENT,
    };
  }, [image, largeurRendue]);

  const sigmaDeclare = Number(etat.sigmaPx.replace(',', '.'));
  const sigmaSousLaResolution = resolution !== null
    && Number.isFinite(sigmaDeclare)
    && sigmaDeclare < resolution.avecLoupe;

  const analyse = useMemo(() => {
    if (!appareil || !scene || !troisClics || !image) return null;
    const sigma = Number(etat.sigmaPx.replace(',', '.'));
    if (!Number.isFinite(sigma) || sigma <= 0) return null;
    try {
      const pts = fairePointes(clics.horizon as number, clics.base as number, clics.sommet as number, sigma);
      const angle = anglePortionEmergente(pts, appareil.cap, appareil.cad, appareil.obj);
      const cbl = faireCible(scene.H.valeur, scene.zb.valeur);
      const R0 = IUGG_R1;
      const resultat: ResultatK = coefficientRefractionEffectif(
        angle.valeur, angle.incertitude, scene.D.valeur, scene.h.valeur, cbl, R0,
      );
      const env = enveloppeCoefficient(
        angle.valeur, angle.incertitude, scene.D, scene.h, scene.H, scene.zb, R0,
      );
      // Le rayon employé pour le CONTRÔLE d'horizon quand k n'est pas établi :
      // celui du régime standard. Il ne sert qu'à prédire un écart qui vaut
      // zéro dans tout le régime occulté, et n'entre dans aucun résultat.
      const R = rayonEffectif(R0, resultat.k ?? 0.13);
      const ctl = controlerHorizon(pts, appareil.cap, appareil.cad, appareil.obj, scene.D.valeur, scene.h.valeur, cbl, R);
      const hauteur = resultat.k !== null
        ? hauteurEmergenteMesuree(angle.valeur, scene.D.valeur, scene.h.valeur, cbl, R)
        : null;
      const pupille = nombre(etat.diametrePupilleMm);
      const limite = pupille !== null && pupille > 0
        ? resolutionAngulaireLimiteRad(550e-9, pupille / 1000)
        : null;
      return {
        angle, resultat, env, ctl, hauteur, R, cbl, limite,
        pas: pasAngulaireRad(appareil.cap, appareil.cad, appareil.obj),
        echelle: echelleMParPx(scene.D.valeur, appareil.cap, appareil.cad, appareil.obj),
        petitAngle: hauteurEmergentePetitAngle(angle.valeur, scene.D.valeur),
        fractionModele: resultat.k !== null ? fractionVisible(scene.D.valeur, scene.h.valeur, cbl, R) : null,
      };
    } catch (err) {
      return { erreur: err instanceof Error ? err.message : String(err) } as const;
    }
  }, [appareil, scene, troisClics, clics, etat.sigmaPx, etat.diametrePupilleMm, image]);

  // --- Rendu du canevas ---

  const dessiner = useCallback(() => {
    const cv = canvasRef.current;
    const conteneur = conteneurRef.current;
    if (!cv || !image || !conteneur) return;
    const largeur = Math.max(280, conteneur.clientWidth);
    const echelle = largeur / image.naturalWidth;
    cv.width = largeur;
    cv.height = Math.round(image.naturalHeight * echelle);
    const ctx = cv.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(image, 0, 0, cv.width, cv.height);
    // Les étiquettes sont décalées horizontalement, une colonne par repère :
    // l'horizon et le bas visible tombent au même endroit quand la cible est
    // occultée — c'est justement ce que le modèle prédit — et deux libellés
    // superposés y devenaient illisibles.
    // Le pointé provisoire, tracé en pointillé serré : il n'est pas encore un
    // relevé, et rien dans le tableau de bord ne l'utilise.
    if (provisoire !== null) {
      const rA = REPERES.find((x) => x.cle === repereActif);
      const yc = provisoire * echelle;
      ctx.strokeStyle = rA ? rA.couleur : '#fff';
      ctx.lineWidth = 1.2;
      ctx.setLineDash([3, 3]);
      ctx.beginPath();
      ctx.moveTo(0, yc);
      ctx.lineTo(cv.width, yc);
      ctx.stroke();
      ctx.setLineDash([]);
    }

    REPERES.forEach((r, i) => {
      const y = clics[r.cle];
      if (y === undefined) return;
      const yc = y * echelle;
      ctx.strokeStyle = r.couleur;
      ctx.lineWidth = r.cle === repereActif ? 2 : 1.4;
      ctx.setLineDash(r.cle === 'horizon' ? [7, 5] : []);
      ctx.beginPath();
      ctx.moveTo(0, yc);
      ctx.lineTo(cv.width, yc);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.font = '600 11px ui-monospace, monospace';
      const texte = r.label;
      const x = 8 + i * Math.min(200, (cv.width - 24) / REPERES.length);
      const yTexte = Math.max(13, Math.min(cv.height - 4, yc - 5));
      const l = ctx.measureText(texte).width;
      ctx.fillStyle = 'rgba(13,17,23,0.66)';
      ctx.fillRect(x - 3, yTexte - 11, l + 6, 14);
      ctx.fillStyle = r.couleur;
      ctx.fillText(texte, x, yTexte);
    });
  }, [image, clics, repereActif, provisoire]);

  useEffect(() => { dessiner(); }, [dessiner]);

  /**
   * La largeur rendue est observée, pas relevée pendant le tracé.
   *
   * Un premier jet la lisait dans `dessiner` et la rangeait dans un état : la
   * barre de validation qui apparaît sous le canevas décale la mise en page,
   * ce qui change la largeur, ce qui relance le tracé, qui réécrit l'état —
   * React coupait la boucle avec l'erreur 185. L'observateur ne réagit qu'à un
   * changement réel, et l'arrondi au pixel entier empêche une oscillation sur
   * une fraction de pixel.
   */
  useEffect(() => {
    const conteneur = conteneurRef.current;
    if (!conteneur || typeof ResizeObserver === 'undefined') return;
    const obs = new ResizeObserver(() => {
      const l = Math.round(conteneur.clientWidth);
      setLargeurRendue((precedente) => (precedente === l ? precedente : l));
      dessiner();
    });
    obs.observe(conteneur);
    return () => obs.disconnect();
  }, [dessiner]);

  useEffect(() => {
    const lc = loupeRef.current;
    if (!lc || !image || !loupe || !canvasRef.current) return;
    const ctx = lc.getContext('2d');
    if (!ctx) return;
    const echelle = canvasRef.current.width / image.naturalWidth;
    const xi = loupe.x / echelle;
    const yi = loupe.y / echelle;
    const demi = lc.width / (2 * GROSSISSEMENT);
    ctx.imageSmoothingEnabled = false;
    ctx.fillStyle = '#0d1117';
    ctx.fillRect(0, 0, lc.width, lc.height);
    ctx.drawImage(
      image, xi - demi, yi - demi, demi * 2, demi * 2,
      0, 0, lc.width, lc.height,
    );
    const r = REPERES.find((x) => x.cle === repereActif);
    ctx.strokeStyle = r ? r.couleur : '#fff';
    ctx.lineWidth = 1;
    ctx.beginPath();
    ctx.moveTo(0, lc.height / 2);
    ctx.lineTo(lc.width, lc.height / 2);
    ctx.stroke();
  }, [loupe, image, repereActif]);

  /** Ordonnée d'image correspondant à un point de l'écran. */
  const yImageDepuisEcran = (clientY: number): number | null => {
    const cv = canvasRef.current;
    if (!cv || !image) return null;
    const rect = cv.getBoundingClientRect();
    if (rect.height === 0) return null;
    const yCanevas = ((clientY - rect.top) * cv.height) / rect.height;
    return yCanevas / (cv.width / image.naturalWidth);
  };

  const majLoupe = (clientX: number, clientY: number) => {
    const cv = canvasRef.current;
    if (!cv) return;
    const rect = cv.getBoundingClientRect();
    if (rect.width === 0 || rect.height === 0) return;
    setLoupe({
      x: ((clientX - rect.left) * cv.width) / rect.width,
      y: ((clientY - rect.top) * cv.height) / rect.height,
    });
  };

  const valider = (y: number) => {
    setClics((c) => ({ ...c, [repereActif]: y }));
    setProvisoire(null);
    setLoupe(null);
    const i = REPERES.findIndex((r) => r.cle === repereActif);
    if (i >= 0 && i < REPERES.length - 1) setRepereActif(REPERES[i + 1].cle);
  };

  // Événements POINTEUR et non souris : `onMouseMove` n'existe pas sous un
  // doigt, et la loupe — qui est ce qui rend le pointé précis — n'apparaissait
  // donc jamais sur téléphone.
  const surPointeurBas = (e: React.PointerEvent<HTMLCanvasElement>) => {
    (e.target as HTMLCanvasElement).setPointerCapture?.(e.pointerId);
    const y = yImageDepuisEcran(e.clientY);
    if (y === null) return;
    setProvisoire(y);
    majLoupe(e.clientX, e.clientY);
  };

  const surPointeurDeplace = (e: React.PointerEvent<HTMLCanvasElement>) => {
    // Au survol souris, la loupe suit sans rien poser. Doigt appuyé, elle suit
    // ET déplace le pointé provisoire.
    majLoupe(e.clientX, e.clientY);
    if (provisoire === null) return;
    const y = yImageDepuisEcran(e.clientY);
    if (y !== null) setProvisoire(y);
  };

  const surPointeurHaut = (e: React.PointerEvent<HTMLCanvasElement>) => {
    const y = yImageDepuisEcran(e.clientY);
    if (y === null) return;
    // À la souris, relâcher vaut validation : c'est le geste attendu, et le
    // curseur ne bouge pas au relâchement. Au doigt, non : lever le doigt
    // déplace le contact, et le doigt masquait le repère. On garde le pointé
    // provisoire, que l'opérateur ajuste puis valide.
    if (e.pointerType === 'mouse') valider(y);
    else setProvisoire(y);
  };

  /** Retouche au pixel d'image — le seul moyen d'atteindre le pixel au doigt. */
  const decaler = (dy: number) => {
    // Les deux états sont calculés puis posés côte à côte. Poser `setLoupe`
    // DANS l'updater de `setProvisoire` marchait à l'essai mais reste un appel
    // d'effet depuis une fonction que React peut rejouer : la boucle de rendu
    // corrigée juste au-dessus a suffi à rappeler pourquoi on ne le fait pas.
    if (provisoire === null || !image) return;
    const v = Math.min(Math.max(provisoire + dy, 0), image.naturalHeight);
    setProvisoire(v);
    const cv = canvasRef.current;
    if (cv) setLoupe({ x: cv.width * 0.5, y: v * (cv.width / image.naturalWidth) });
  };

  // --- Exports ---

  const exporterPng = () => {
    if (!image) return;
    const cv = document.createElement('canvas');
    cv.width = image.naturalWidth;
    cv.height = image.naturalHeight;
    const ctx = cv.getContext('2d');
    if (!ctx) return;
    ctx.drawImage(image, 0, 0);
    const taille = Math.max(12, Math.round(image.naturalWidth / 90));
    for (const r of REPERES) {
      const y = clics[r.cle];
      if (y === undefined) continue;
      ctx.strokeStyle = r.couleur;
      ctx.lineWidth = Math.max(1.5, image.naturalWidth / 1400);
      ctx.setLineDash(r.cle === 'horizon' ? [taille, taille * 0.7] : []);
      ctx.beginPath();
      ctx.moveTo(0, y);
      ctx.lineTo(cv.width, y);
      ctx.stroke();
      ctx.setLineDash([]);
      ctx.fillStyle = r.couleur;
      ctx.font = `600 ${taille}px ui-monospace, monospace`;
      ctx.fillText(`${r.label} — y = ${y.toFixed(1)} px`, taille, Math.max(taille * 1.3, y - taille * 0.5));
    }
    // La mention est brûlée dans l'image : une image annotée qui circule sans
    // sa nature est une image qui sera prise pour une mesure.
    ctx.fillStyle = 'rgba(13,17,23,0.72)';
    ctx.fillRect(0, cv.height - taille * 2.6, cv.width, taille * 2.6);
    ctx.fillStyle = '#C8D8E8';
    ctx.font = `${taille * 0.85}px ui-monospace, monospace`;
    ctx.fillText(
      'Annotation manuelle — les traits sont des pointés d’opérateur, pas une détection automatique.',
      taille, cv.height - taille * 1.3,
    );
    ctx.fillText(
      `Protocole « Portion visible d’une cible éloignée » v1.0 — outil D — ${nomFichier}`,
      taille, cv.height - taille * 0.4,
    );
    cv.toBlob((blob) => {
      if (!blob) return;
      const a = document.createElement('a');
      a.href = URL.createObjectURL(blob);
      a.download = `${nomFichier.replace(/\.[^.]+$/, '')}-annotee.png`;
      a.click();
      URL.revokeObjectURL(a.href);
    }, 'image/png');
  };

  /**
   * La synthèse JSON. Chaque nombre vient d'une fonction épinglée du noyau ;
   * seule la mise en forme est faite ici. Un champ non établi porte
   * « indisponible », jamais une valeur de remplacement.
   */
  const syntheseJson = () => {
    if (!analyse || 'erreur' in analyse || !scene || !appareil) return null;
    const { angle, resultat: r, env, ctl } = analyse;
    const ind = (x: number | null | undefined, n = 6) =>
      x === null || x === undefined ? 'indisponible' : Number(x.toFixed(n));
    return {
      outil: 'metrologie-image (outil D) — port navigateur',
      protocole: "Portion visible d'une cible éloignée au-dessus de la mer v1.0",
      genere_le: new Date().toISOString(),
      traçabilité: {
        fichier: nomFichier || 'indisponible',
        sha256: rapport?.empreinte ?? 'indisponible',
        taille_octets: rapport?.tailleOctets ?? 'indisponible',
        exif_lu: rapport?.exif ? true : false,
        motif_exif_absent: rapport?.motifExifAbsent ?? null,
        sources: {
          distance: scene.D.source,
          altitude_observateur: scene.h.source,
          hauteur_cible: scene.H.source,
          altitude_base: scene.zb.source,
          focale: etat.focaleMm.source,
          capteur: etat.modeFocale === 'equivalent35'
            ? 'focale équivalent 35 mm — capteur fictif de 36 mm'
            : etat.largeurCapteurMm.source,
        },
      },
      étalonnage: {
        mode_focale: etat.modeFocale,
        pas_angulaire_arcsec: Number(arcsec(analyse.pas).toFixed(4)),
        echelle_m_par_px: Number(analyse.echelle.toFixed(4)),
        limite_diffraction_arcsec: analyse.limite === null ? 'indisponible' : Number(arcsec(analyse.limite).toFixed(4)),
        pas_sous_la_limite_de_diffraction: analyse.limite === null ? 'indisponible' : analyse.pas < analyse.limite,
        point_principal_connu: pointPrincipalConnu(appareil.cad),
        image_recadree: estRecadree(appareil.cad),
        facteur_reechantillonnage: appareil.cad.largeurPx / appareil.cad.largeurRecadreePx,
      },
      relevé: {
        // Ordonnées NON arrondies, délibérément. Un arrondi au centième de
        // pixel suffit à déplacer k de 8·10⁻⁵ sur cette visée : l'essai de
        // bout en bout l'a mesuré en confrontant l'export au paquet Python.
        // Un fichier d'audit dont on ne peut pas refaire le calcul ne remplit
        // pas son office.
        y_horizon_px: clics.horizon as number,
        y_base_px: clics.base as number,
        y_sommet_px: clics.sommet as number,
        sigma_pointe_px: Number(etat.sigmaPx.replace(',', '.')),
        facteur_elargissement: FACTEUR_ELARGISSEMENT,
      },
      mesure: {
        angle_emergent_rad: ind(angle.exact, 12),
        angle_emergent_paraxial_rad: Number(angle.paraxial.toFixed(12)),
        angle_emergent_borne_basse_rad: Number(angle.borneBasse.toFixed(12)),
        angle_emergent_borne_haute_rad: Number(angle.borneHaute.toFixed(12)),
        incertitude_elargie_rad: Number(angle.incertitude.toFixed(12)),
        ecart_paraxial_rad: ind(angle.ecartParaxial, 12),
        hauteur_emergente_m: ind(analyse.hauteur, 3),
        hauteur_emergente_petit_angle_m: Number(analyse.petitAngle.toFixed(3)),
        fraction_visible_mesuree: analyse.hauteur === null ? 'indisponible' : Number((analyse.hauteur / scene.H.valeur).toFixed(6)),
        fraction_visible_modele: ind(analyse.fractionModele, 6),
      },
      controle_horizon_base: {
        ecart_releve_px: Number(ctl.ecartPx.toFixed(2)),
        ecart_predit_px: Number(ctl.ecartPreditPx.toFixed(2)),
        tolerance_px: Number(ctl.tolerancePx.toFixed(2)),
        coherent: ctl.coherent,
        causes_possibles: [...ctl.causesPossibles],
      },
      refraction: {
        statut: r.statut,
        k: ind(r.k),
        k_min: ind(r.kMin),
        k_max: ind(r.kMax),
        k_saturation: ind(r.kSaturation),
        k_extinction: ind(r.kExtinction),
        dans_zone_saturee: r.dansZoneSaturee,
        dans_zone_eteinte: r.dansZoneEteinte,
        regime: r.regime ?? 'indisponible',
        regime_determine: r.regimeDetermine,
        enveloppe_entrees: {
          k_min: ind(env.kMin),
          k_max: ind(env.kMax),
          combinaisons: env.combinaisons,
          combinaisons_non_bornees: env.combinaisonsNonBornees,
        },
        interpretation: interpreter(r),
      },
      ce_que_ca_n_etablit_pas: [...CE_QUE_CA_N_ETABLIT_PAS],
    };
  };

  const exporterJson = () => {
    const doc = syntheseJson();
    if (!doc) return;
    const blob = new Blob([JSON.stringify(doc, null, 2)], { type: 'application/json' });
    const a = document.createElement('a');
    a.href = URL.createObjectURL(blob);
    a.download = `${(nomFichier || 'analyse').replace(/\.[^.]+$/, '')}-metrologie.json`;
    a.click();
    URL.revokeObjectURL(a.href);
  };

  // --- Ce qui manque encore, dit explicitement ---

  const manques: string[] = [];
  if (!image) manques.push('une image chargée');
  if (!appareil) manques.push('l’étalonnage de l’appareil (capteur, focale, cadrage), sources comprises');
  if (!scene) manques.push('les quatre grandeurs de scène (D, h_obs, H, z_b), sources comprises');
  if (!troisClics) manques.push('les trois pointés sur l’image');

  const r = analyse && !('erreur' in analyse) ? analyse.resultat : null;

  return (
    <div style={{ maxWidth: 1180, margin: '0 auto', padding: '4px 2px 24px' }}>

      {/*
        Deux corrections que seul un média query peut porter, les styles étant
        écrits en ligne ailleurs dans ce fichier.

        1. `font-size: 16px` sur les champs. En dessous de 16 px, Safari iOS
           zoome la page à chaque prise de focus : le cadrage saute, et sur un
           outil où l'on saisit une quinzaine de champs c'est intenable.
        2. `min-height: 44px` : la cible tactile recommandée. Les champs faisaient
           31 px de haut, dimensionnés pour une souris.
      */}
      <style>{`
        @media (max-width: ${SEUIL_PETIT_ECRAN_PX - 1}px) {
          [data-champ] { font-size: 16px !important; min-height: 44px; }
        }
      `}</style>

      <div style={{
        background: dash.cyanSoft, border: `1px solid ${ACCENT}40`,
        borderRadius: 10, padding: '16px 20px', marginBottom: 18,
      }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 8,
        }}>Ce que cet outil produit</div>
        <p style={{ margin: '0 0 8px', fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          Trois pointés sur une photographie de visée, quatre grandeurs sourcées, et l’angle
          relevé est inversé en <strong>coefficient de réfraction effectif</strong> — avec son
          enveloppe, jamais une valeur seule. Quand le relevé ne détermine pas k, l’outil
          l’écrit et dit pourquoi.
        </p>
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: dash.ink }}>
          Il ne rend <strong>aucun verdict sur la forme de la Terre</strong> : le modèle
          sphérique est une entrée de ce calcul, pas sa conclusion.{' '}
          <strong>L’image ne quitte pas votre machine</strong> — empreinte, EXIF et calculs se
          font dans le navigateur.
        </p>
      </div>

      <div style={{
        display: 'grid',
        // En dessous du seuil, une seule colonne. Deux colonnes à 390 px
        // écrasaient celle de l'image à ZÉRO pixel de large : le canevas
        // existait, mais sa boîte était vide et aucun pointé n'était possible.
        gridTemplateColumns: ecran.petit ? 'minmax(0, 1fr)' : 'minmax(0, 1fr) minmax(0, 350px)',
        gap: 18,
        alignItems: 'start',
      }}>
        {/* ── Colonne gauche : image et annotation ── */}
        <div>
          <Carte>
            <label style={{ fontSize: 11, fontFamily: dash.fontMono, letterSpacing: '0.06em', color: 'var(--ink-muted)', textTransform: 'uppercase' }}>
              Photographie de visée — JPEG, PNG ou WebP
            </label>
            <input
              type="file" accept="image/jpeg,image/png,image/webp"
              onChange={(e) => { const f = e.target.files?.[0]; if (f) charger(f); }}
              style={{ display: 'block', marginTop: 8, fontSize: 12, color: 'var(--ink-muted)' }}
            />
            {erreurFichier && (
              <div style={{ fontSize: 11, color: COULEUR_BASE, marginTop: 8 }}>{erreurFichier}</div>
            )}
            {rapport && (
              <div style={{ marginTop: 12, fontSize: 11, fontFamily: dash.fontMono, lineHeight: 1.7 }}>
                <div style={{ color: 'var(--ink-muted)' }}>
                  SHA-256 <span style={{ color: 'var(--ink)', wordBreak: 'break-all' }}>{rapport.empreinte}</span>
                </div>
                <div style={{ color: 'var(--ink-muted)' }}>
                  {rapport.tailleOctets.toLocaleString('fr-FR')} octets
                  {image && ` — ${image.naturalWidth} × ${image.naturalHeight} px livrés`}
                </div>
                {rapport.exif ? (
                  <div style={{ marginTop: 6 }}>
                    <div style={{ color: 'var(--ink-muted)' }}>
                      EXIF : {rapport.exif.fabricant ?? '—'} {rapport.exif.modele ?? ''}
                      {rapport.exif.focaleMm !== null && ` — ${rapport.exif.focaleMm} mm`}
                      {rapport.exif.focaleEquivalente35mm !== null && ` (éq. 35 mm : ${rapport.exif.focaleEquivalente35mm} mm)`}
                    </div>
                    <button
                      onClick={adopterExif}
                      style={{
                        marginTop: 6, padding: '5px 10px', fontSize: 11, cursor: 'pointer',
                        border: `1px solid ${ACCENT}`, borderRadius: 4, background: 'transparent', color: ACCENT,
                      }}
                    >
                      Adopter ces valeurs comme entrées (source : EXIF, déclaratif)
                    </button>
                  </div>
                ) : (
                  <div style={{ color: 'var(--ink-ghost)', marginTop: 6 }}>
                    Pas d’EXIF exploitable : {rapport.motifExifAbsent ?? 'motif inconnu'}. Les champs
                    restent à saisir à la main — aucun n’est deviné.
                  </div>
                )}
              </div>
            )}
          </Carte>

          {image && (
            <Carte>
              <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 10 }}>
                {REPERES.map((rep) => (
                  <button
                    key={rep.cle}
                    onClick={() => setRepereActif(rep.cle)}
                    style={{
                      padding: '6px 10px', fontSize: 11, fontWeight: 600, cursor: 'pointer',
                      borderRadius: 4, background: repereActif === rep.cle ? rep.couleur + '18' : 'transparent',
                      border: `1px solid ${repereActif === rep.cle ? rep.couleur : dash.border}`,
                      color: repereActif === rep.cle ? rep.couleur : 'var(--ink-muted)',
                    }}
                  >
                    {rep.label}
                    {clics[rep.cle] !== undefined && ` · ${(clics[rep.cle] as number).toFixed(1)} px`}
                  </button>
                ))}
                {Object.keys(clics).length > 0 && (
                  <button
                    onClick={() => { setClics({}); setRepereActif('horizon'); }}
                    style={{
                      padding: '6px 10px', fontSize: 11, cursor: 'pointer', borderRadius: 4,
                      background: 'transparent', border: `1px solid ${dash.border}`, color: 'var(--ink-ghost)',
                    }}
                  >
                    Effacer les pointés
                  </button>
                )}
              </div>
              <div style={{ fontSize: 11, color: 'var(--ink-ghost)', marginBottom: 8, lineHeight: 1.6 }}>
                {REPERES.find((x) => x.cle === repereActif)?.aide}
              </div>

              <div ref={conteneurRef} style={{ position: 'relative', border: `1px solid ${dash.border}`, borderRadius: 6, overflow: 'hidden' }}>
                <canvas
                  ref={canvasRef}
                  onPointerDown={surPointeurBas}
                  onPointerMove={surPointeurDeplace}
                  onPointerUp={surPointeurHaut}
                  onPointerLeave={() => { if (provisoire === null) setLoupe(null); }}
                  style={{
                    display: 'block', width: '100%', cursor: 'crosshair',
                    // Sans cela, faire glisser le doigt sur le canevas fait
                    // défiler la page au lieu de déplacer le pointé.
                    touchAction: 'none',
                  }}
                />
                {loupe && (
                  <canvas
                    ref={loupeRef}
                    width={168}
                    height={168}
                    style={{
                      position: 'absolute', pointerEvents: 'none',
                      left: Math.min(Math.max(loupe.x - 84, 4), (canvasRef.current?.width ?? 400) - 172),
                      top: loupe.y > 190 ? loupe.y - 184 : loupe.y + 16,
                      border: `2px solid ${REPERES.find((x) => x.cle === repereActif)?.couleur}`,
                      borderRadius: 4, boxShadow: '0 4px 18px rgba(0,0,0,0.4)',
                    }}
                  />
                )}
              </div>
              {/* Barre de validation. Sur souris elle sert de retouche ; sur
                  tactile elle est la seule voie vers le pixel, le doigt
                  masquant ce qu'il désigne. */}
              {provisoire !== null && (
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 6, flexWrap: 'wrap',
                  marginTop: 8, padding: '8px 10px', borderRadius: 5,
                  border: `1px solid ${REPERES.find((x) => x.cle === repereActif)?.couleur}55`,
                  background: `${REPERES.find((x) => x.cle === repereActif)?.couleur}10`,
                }}>
                  <span style={{ fontSize: 11, fontFamily: dash.fontMono, color: 'var(--ink)' }}>
                    y = {provisoire.toFixed(1)} px
                  </span>
                  {[[-10, '−10'], [-1, '−1'], [1, '+1'], [10, '+10']].map(([d, lab]) => (
                    <button
                      key={String(d)} onClick={() => decaler(d as number)}
                      aria-label={`Décaler le pointé de ${d} pixel${Math.abs(d as number) > 1 ? 's' : ''}`}
                      style={{
                        minWidth: 44, minHeight: 34, fontSize: 12, cursor: 'pointer',
                        fontFamily: dash.fontMono, borderRadius: 4,
                        border: `1px solid ${dash.border}`, background: 'var(--card)', color: 'var(--ink)',
                      }}
                    >{lab}</button>
                  ))}
                  <button
                    onClick={() => valider(provisoire)}
                    style={{
                      minHeight: 34, padding: '0 14px', fontSize: 12, fontWeight: 700, cursor: 'pointer',
                      borderRadius: 4, border: `1px solid ${ACCENT}`, background: ACCENT + '1A', color: ACCENT,
                    }}
                  >Valider ce pointé</button>
                  <button
                    onClick={() => { setProvisoire(null); setLoupe(null); }}
                    style={{
                      minHeight: 34, padding: '0 10px', fontSize: 12, cursor: 'pointer',
                      borderRadius: 4, border: `1px solid ${dash.border}`, background: 'transparent', color: 'var(--ink-ghost)',
                    }}
                  >Annuler</button>
                </div>
              )}

              <div style={{ fontSize: 10, color: 'var(--ink-ghost)', marginTop: 6, lineHeight: 1.6 }}>
                Loupe ×{GROSSISSEMENT} : le pointé se fait au pixel de l’image, pas au pixel de
                l’affichage réduit. Les ordonnées sont enregistrées dans le repère du fichier
                livré.{' '}
                {ecran.grossier
                  ? 'Au doigt : posez, faites glisser pour ajuster sous la loupe, retouchez au pixel, puis validez.'
                  : 'À la souris, relâcher valide le pointé.'}
              </div>

              {/* Ce que l'écran permet, mesuré sur le canevas rendu. */}
              {resolution && (
                <div style={{
                  marginTop: 8, padding: '10px 12px', borderRadius: 5,
                  border: `1px solid ${sigmaSousLaResolution ? COULEUR_BASE : dash.border}`,
                  background: sigmaSousLaResolution ? COULEUR_BASE + '10' : 'transparent',
                  fontSize: 11, lineHeight: 1.65, color: 'var(--ink-muted)',
                }}>
                  <strong style={{ color: 'var(--ink)' }}>Résolution de pointé sur cet écran.</strong>{' '}
                  Le canevas affiche l’image réduite : un pixel d’écran vaut{' '}
                  <strong style={{ color: 'var(--ink)' }}>{fmt(resolution.pxImageParPxEcran, 1)} px d’image</strong>,
                  soit {fmt(resolution.avecLoupe, 2)} px sous la loupe ×{GROSSISSEMENT}.
                  {sigmaSousLaResolution && (
                    <>
                      {' '}
                      <span style={{ color: COULEUR_BASE }}>
                        Le σ déclaré ({fmt(sigmaDeclare, 1)} px) est plus fin que ce que ce geste peut
                        produire. L’enveloppe rendue sera plus étroite que la mesure ne le permet —
                        relevez σ à {fmt(resolution.avecLoupe, 1)} px au moins, ou reprenez le pointé
                        sur un écran plus grand.
                      </span>
                    </>
                  )}
                  {ecran.petit && !sigmaSousLaResolution && (
                    <> Sur un écran de cette taille, un pointé fin passe par la loupe et les
                    boutons de retouche : le doigt seul ne vaut pas mieux qu’une dizaine de pixels
                    d’image.</>
                  )}
                </div>
              )}
            </Carte>
          )}
        </div>

        {/* ── Colonne droite : saisie ── */}
        <Carte>
          <h3 style={{ fontSize: 12, fontFamily: dash.fontMono, letterSpacing: '0.08em', textTransform: 'uppercase', color: ACCENT, marginBottom: 10 }}>
            Étalonnage de l’appareil
          </h3>

          <div style={{ display: 'flex', gap: 6, marginBottom: 12 }}>
            {([['reelle', 'Focale réelle + capteur'], ['equivalent35', 'Équivalent 35 mm']] as const).map(([m, lab]) => (
              <button
                key={m}
                onClick={() => maj('modeFocale', m)}
                style={{
                  flex: 1, padding: '6px 8px', fontSize: 10, cursor: 'pointer', borderRadius: 4,
                  background: etat.modeFocale === m ? ACCENT + '18' : 'transparent',
                  border: `1px solid ${etat.modeFocale === m ? ACCENT : dash.border}`,
                  color: etat.modeFocale === m ? ACCENT : 'var(--ink-muted)',
                }}
              >{lab}</button>
            ))}
          </div>

          {etat.modeFocale === 'reelle' && (
            <ChampNombre
              cle="largeurCapteurMm" label="Largeur du capteur" unite="mm" champ={etat.largeurCapteurMm}
              onChange={(c) => maj('largeurCapteurMm', c)} avecIncertitude={false}
              aide="Largeur physique de la surface sensible. 36 mm en plein format, ~23,5 mm en APS-C."
            />
          )}
          <ChampNombre
            cle="focaleMm" label={etat.modeFocale === 'equivalent35' ? 'Focale équivalent 35 mm' : 'Focale réelle'}
            unite="mm" champ={etat.focaleMm} onChange={(c) => maj('focaleMm', c)} avecIncertitude={false}
            aide="Focale au moment de la prise de vue, zoom optique compris."
          />
          <ChampNombre
            cle="largeurNativePx" label="Définition native — largeur" unite="px" champ={etat.largeurNativePx}
            onChange={(c) => maj('largeurNativePx', c)} avecIncertitude={false}
            aide="Définition du capteur AVANT recadrage. C’est elle qui fixe le pas pixel, jamais la largeur du fichier livré."
          />
          <ChampNombre
            cle="hauteurNativePx" label="Définition native — hauteur" unite="px" champ={etat.hauteurNativePx}
            onChange={(c) => maj('hauteurNativePx', c)} avecIncertitude={false}
            aide="Même remarque. Un recadrage ne change pas le pas pixel : il enlève des pixels, il ne les agrandit pas."
          />

          <label style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 11, color: 'var(--ink-muted)', margin: '10px 0' }}>
            <input type="checkbox" checked={etat.recadree} onChange={(e) => maj('recadree', e.target.checked)} />
            L’image livrée a été recadrée ou rééchantillonnée
          </label>

          {etat.recadree && (
            <div style={{ paddingLeft: 10, borderLeft: `2px solid ${dash.border}` }}>
              <ChampNombre
                cle="largeurRecadreePx" label="Recadrage — largeur" unite="px natifs" champ={etat.largeurRecadreePx}
                onChange={(c) => maj('largeurRecadreePx', c)} avecIncertitude={false}
                aide="Dimensions du recadrage AVANT tout agrandissement, en pixels du capteur."
              />
              <ChampNombre
                cle="hauteurRecadreePx" label="Recadrage — hauteur" unite="px natifs" champ={etat.hauteurRecadreePx}
                onChange={(c) => maj('hauteurRecadreePx', c)} avecIncertitude={false}
                aide="Le rapport avec la définition du fichier livré donne le facteur de rééchantillonnage."
              />
              <label style={{ display: 'flex', alignItems: 'center', gap: 7, fontSize: 11, color: 'var(--ink-muted)', margin: '8px 0' }}>
                <input type="checkbox" checked={etat.origineConnue} onChange={(e) => maj('origineConnue', e.target.checked)} />
                L’origine du recadrage est documentée
              </label>
              {etat.origineConnue ? (
                <>
                  <ChampNombre
                    cle="origineXPx" label="Origine du recadrage — x" unite="px natifs" champ={etat.origineXPx}
                    onChange={(c) => maj('origineXPx', c)} avecIncertitude={false}
                    aide="Coin haut-gauche du recadrage dans le repère du capteur."
                  />
                  <ChampNombre
                    cle="origineYPx" label="Origine du recadrage — y" unite="px natifs" champ={etat.origineYPx}
                    onChange={(c) => maj('origineYPx', c)} avecIncertitude={false}
                    aide="C’est elle qui situe le point principal. Un recadrage le déplace ; l’ignorer fausse l’angle."
                  />
                </>
              ) : (
                <div style={{ fontSize: 10, color: 'var(--ink-ghost)', lineHeight: 1.6, marginBottom: 12 }}>
                  Sans origine, l’ordonnée du point principal est <strong>indisponible</strong>. L’angle
                  n’est pas refusé pour autant : il est rendu sous forme d’enveloppe sur toutes les
                  positions que le recadrage autorise, ce qui est plus honnête qu’un centre supposé.
                </div>
              )}
            </div>
          )}

          <h3 style={{ fontSize: 12, fontFamily: dash.fontMono, letterSpacing: '0.08em', textTransform: 'uppercase', color: ACCENT, margin: '18px 0 10px' }}>
            Scène
          </h3>
          <ChampNombre
            cle="distanceKm" label="Distance de la cible D" unite="km" champ={etat.distanceKm}
            onChange={(c) => maj('distanceKm', c)}
            aide="Distance géodésique, établie hors photographie (§12.4). Le second champ est la demi-largeur de l’enveloppe."
          />
          <ChampNombre
            cle="altitudeObsM" label="Altitude de l’œil h_obs" unite="m" champ={etat.altitudeObsM}
            onChange={(c) => maj('altitudeObsM', c)}
            aide="Hauteur de l’objectif au-dessus de la surface de référence, pas l’altitude du sol."
          />
          <ChampNombre
            cle="hauteurCibleM" label="Hauteur totale de la cible H" unite="m" champ={etat.hauteurCibleM}
            onChange={(c) => maj('hauteurCibleM', c)}
            aide="Établie par fiche d’ouvrage ou donnée altimétrique, jamais déduite de la photographie."
          />
          <ChampNombre
            cle="altitudeBaseM" label="Altitude de la base z_b" unite="m" champ={etat.altitudeBaseM}
            onChange={(c) => maj('altitudeBaseM', c)}
            aide="0 pour une base au niveau moyen de la mer. Une base surélevée change la géométrie."
          />

          <h3 style={{ fontSize: 12, fontFamily: dash.fontMono, letterSpacing: '0.08em', textTransform: 'uppercase', color: ACCENT, margin: '18px 0 10px' }}>
            Relevé
          </h3>
          <div style={{ marginBottom: 13 }}>
            <label style={{ display: 'block', fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.06em', color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 4 }}>
              Incertitude de pointé σ <span style={{ opacity: 0.6 }}>(px, 1 écart-type)</span>
            </label>
            <input
              type="text" inputMode="decimal" value={etat.sigmaPx}
              onChange={(e) => maj('sigmaPx', e.target.value)}
              style={{
                width: '100%', padding: '7px 9px', fontSize: 13, fontFamily: dash.fontMono,
                border: `1px solid ${dash.border}`, borderRadius: 4, background: 'var(--card)', color: 'var(--ink)',
              }}
            />
            <div style={{ fontSize: 10, color: 'var(--ink-ghost)', marginTop: 3, lineHeight: 1.45 }}>
              Valeur par défaut {SIGMA_POINTE_PX_DEFAUT} px. À remplacer par la dispersion de vos
              propres pointés répétés (§19.3) — c’est une valeur mesurable, pas une convention.
            </div>
          </div>
          <ChampNombre
            cle="diametrePupilleMm" label="Diamètre de pupille" unite="mm — facultatif" champ={etat.diametrePupilleMm}
            onChange={(c) => maj('diametrePupilleMm', c)} avecIncertitude={false}
            aide="Focale ÷ nombre d’ouverture. Sert à comparer le pas pixel à la limite de diffraction. Sans lui, cette limite reste indisponible."
          />
        </Carte>
      </div>

      {/* ── Résultats ── */}
      <Carte style={{ borderTop: `3px solid ${ACCENT}` }}>
        <h3 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ink)', marginBottom: 12 }}>
          Tableau de bord
        </h3>

        {manques.length > 0 && (
          <div style={{
            padding: '12px 14px', border: `1px solid ${dash.border}`, borderRadius: 6,
            background: 'var(--card)', fontSize: 12, color: 'var(--ink-muted)', lineHeight: 1.7,
          }}>
            Le calcul attend encore : {manques.join(' ; ')}. Rien n’est calculé sur des valeurs
            supposées.
          </div>
        )}

        {analyse && 'erreur' in analyse && (
          <div style={{ padding: '12px 14px', border: `1px solid ${COULEUR_BASE}`, borderRadius: 6, fontSize: 12, color: COULEUR_BASE, lineHeight: 1.7 }}>
            {analyse.erreur}
          </div>
        )}

        {analyse && !('erreur' in analyse) && r && (
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
            <div>
              <h4 style={{ fontSize: 11, fontFamily: dash.fontMono, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--ink-muted)', marginBottom: 6 }}>
                Étalonnage et mesure
              </h4>
              <Ligne cle="pasAngulaire" label="Pas angulaire par pixel" valeur={`${fmt(arcsec(analyse.pas), 3)} ″`} />
              <Ligne
                cle="echelle" label={`Échelle à ${fmt((scene as NonNullable<typeof scene>).D.valeur / 1000, 1)} km`}
                valeur={`${fmt(analyse.echelle, 3)} m/px`}
                note="Sur l’axe optique seulement. Grandeur de lecture : l’inversion travaille en angles et ne passe jamais par cette conversion."
              />
              <Ligne
                cle="limiteDiffraction" label="Limite de diffraction"
                valeur={analyse.limite === null ? INDISPONIBLE : `${fmt(arcsec(analyse.limite), 3)} ″`}
                note={analyse.limite === null
                  ? 'Diamètre de pupille non déclaré.'
                  : analyse.pas < analyse.limite
                    ? 'Le pas pixel est plus fin que la tache de diffraction : un écart de quelques pixels n’est plus forcément un détail enregistré.'
                    : 'Le pas pixel est plus grossier que la tache de diffraction : la mesure est limitée par le capteur, pas par l’optique.'}
              />
              <Ligne
                cle="angleEmergent" label="Angle de la portion émergente"
                valeur={analyse.angle.exact === null
                  ? `${fmt(arcsec(analyse.angle.borneBasse), 2)} – ${fmt(arcsec(analyse.angle.borneHaute), 2)} ″`
                  : `${fmt(arcsec(analyse.angle.exact), 2)} ± ${fmt(arcsec(analyse.angle.incertitude), 2)} ″`}
                accent={ACCENT}
                note={analyse.angle.exact === null
                  ? 'Enveloppe : le point principal est indisponible faute d’origine de recadrage déclarée.'
                  : `Forme paraxiale du cahier des charges : ${fmt(arcsec(analyse.angle.paraxial), 2)} ″, soit ${fmt(arcsec(analyse.angle.ecartParaxial ?? 0), 4)} ″ d’écart.`}
              />
              <Ligne
                cle="hauteurEmergente" label="Hauteur émergente mesurée"
                valeur={analyse.hauteur === null ? INDISPONIBLE : `${fmt(analyse.hauteur, 2)} m`}
                note={analyse.hauteur === null
                  ? 'Non calculable tant que k n’est pas établi : la conversion angle → mètres dépend du rayon effectif.'
                  : `Forme D·tan θ : ${fmt(analyse.petitAngle, 2)} m.`}
              />
              <Ligne
                cle="fractionVisible" label="Fraction de la cible visible"
                valeur={analyse.hauteur === null ? INDISPONIBLE : `${fmt((analyse.hauteur / (scene as NonNullable<typeof scene>).H.valeur) * 100, 1)} %`}
                note={analyse.fractionModele === null ? undefined
                  : `Le modèle prédit ${fmt(analyse.fractionModele * 100, 1)} % au k retenu — l’égalité des deux est l’identité qui ferme la chaîne.`}
              />
            </div>

            <div>
              <h4 style={{ fontSize: 11, fontFamily: dash.fontMono, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--ink-muted)', marginBottom: 6 }}>
                Contrôle horizon / bas visible
              </h4>
              <Ligne cle="ecartReleve" label="Écart relevé" valeur={`${fmt(analyse.ctl.ecartPx, 1)} px`} />
              <Ligne
                cle="ecartPredit" label="Écart prédit par le modèle"
                valeur={`${fmt(analyse.ctl.ecartPreditPx, 1)} px`}
                note="Nul dès que la cible est partiellement occultée : le rayon rasant qui définit l’horizon est le même qui définit son bas visible."
              />
              <Ligne cle="tolerance" label="Tolérance" valeur={`± ${fmt(analyse.ctl.tolerancePx, 1)} px`} />
              <Ligne
                cle="controle" label="Contrôle"
                valeur={analyse.ctl.coherent ? 'satisfait' : 'ÉCHOUÉ'}
                accent={analyse.ctl.coherent ? dash.opal : COULEUR_BASE}
              />
              {!analyse.ctl.coherent && (
                <div style={{ fontSize: 11, color: COULEUR_BASE, lineHeight: 1.7, marginTop: 8 }}>
                  Causes possibles, qu’aucun calcul ne peut départager :
                  <ul style={{ margin: '5px 0 0 16px', padding: 0 }}>
                    {analyse.ctl.causesPossibles.map((c) => <li key={c} style={{ marginBottom: 2 }}>{c}</li>)}
                  </ul>
                </div>
              )}
            </div>

            <div>
              <h4 style={{ fontSize: 11, fontFamily: dash.fontMono, letterSpacing: '0.06em', textTransform: 'uppercase', color: 'var(--ink-muted)', marginBottom: 6 }}>
                Coefficient de réfraction effectif
              </h4>
              <Ligne cle="statut" label="Statut" valeur={r.statut} accent={r.k === null ? 'var(--ink-ghost)' : ACCENT} />
              <Ligne
                cle="k" label="k"
                valeur={r.k === null ? INDISPONIBLE : fmt(r.k, 4)}
                accent={ACCENT}
              />
              <Ligne
                cle="enveloppePointe" label="Enveloppe — pointé seul"
                valeur={r.kMin === null || r.kMax === null ? INDISPONIBLE : `[${fmt(r.kMin, 4)} ; ${fmt(r.kMax, 4)}]`}
              />
              <Ligne
                cle="enveloppeEntrees" label="Enveloppe — pointé et entrées"
                valeur={analyse.env.kMin === null || analyse.env.kMax === null ? INDISPONIBLE : `[${fmt(analyse.env.kMin, 4)} ; ${fmt(analyse.env.kMax, 4)}]`}
                note={`${analyse.env.combinaisons} combinaisons des bornes d’entrée balayées${analyse.env.combinaisonsNonBornees > 0 ? `, dont ${analyse.env.combinaisonsNonBornees} sans borne` : ''}.`}
              />
              <Ligne
                cle="regime" label="Régime (Tableau 8, §11.3)"
                valeur={r.regimeDetermine && r.regime ? r.regime : INDISPONIBLE}
                note={r.regimeDetermine ? undefined : 'L’enveloppe ne tient pas dans un seul régime : en nommer un serait choisir.'}
              />
              <div style={{
                marginTop: 12, padding: '10px 12px', borderRadius: 5,
                background: ACCENT + '0E', border: `1px solid ${ACCENT}33`,
                fontSize: 11.5, lineHeight: 1.75, color: 'var(--ink-muted)',
              }}>
                {interpreter(r)}
              </div>
            </div>
          </div>
        )}

        {analyse && !('erreur' in analyse) && (
          <>
            <div style={{ display: 'flex', gap: 8, marginTop: 18, flexWrap: 'wrap' }}>
              <button
                onClick={exporterPng}
                style={{
                  padding: '8px 14px', fontSize: 12, fontWeight: 600, cursor: 'pointer', borderRadius: 4,
                  border: `1px solid ${ACCENT}`, background: ACCENT + '14', color: ACCENT,
                }}
              >
                Télécharger l’image annotée (PNG)
              </button>
              <button
                onClick={exporterJson}
                style={{
                  padding: '8px 14px', fontSize: 12, fontWeight: 600, cursor: 'pointer', borderRadius: 4,
                  border: `1px solid ${dash.lavender}`, background: dash.lavender + '14', color: dash.lavender,
                }}
              >
                Télécharger la synthèse (JSON)
              </button>
            </div>

            <div style={{
              marginTop: 18, padding: '13px 15px', borderRadius: 5,
              border: `1px solid ${dash.border}`, background: 'var(--card)',
            }}>
              <div style={{ fontSize: 10, fontFamily: dash.fontMono, letterSpacing: '0.08em', textTransform: 'uppercase', color: 'var(--ink-muted)', marginBottom: 8 }}>
                Ce que ce résultat n’établit pas
              </div>
              <ul style={{ margin: 0, paddingLeft: 17, fontSize: 11.5, lineHeight: 1.75, color: 'var(--ink-muted)' }}>
                {CE_QUE_CA_N_ETABLIT_PAS.map((t) => <li key={t} style={{ marginBottom: 6 }}>{t}</li>)}
              </ul>
            </div>
          </>
        )}
      </Carte>
    </div>
  );
}
