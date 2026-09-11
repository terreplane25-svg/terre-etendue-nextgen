'use client';

/**
 * ResultatVisee.tsx — Le résultat du Simulateur de Visée.
 *
 * CE QUE CE PANNEAU MONTRE, ET CE QU'IL SE REFUSE À MONTRER
 * ────────────────────────────────────────────────────────
 * Il montre : un verdict sur la capacité de la visée à départager les deux
 * modèles, ce que chacun prédit à la BASE de la cible, et la coupe de la ligne
 * de visée théorique.
 *
 * Il montre aussi, quand le relevé a été demandé, les reliefs qui coupent la
 * visée : combien, où, et de combien chacun la dépasse.
 *
 * Il se refuse à : conclure sur la forme de la Terre, et à faire entrer le
 * relief dans le verdict. Ce qui est affiché en haut, c'est ce que chaque
 * modèle IMPLIQUE sur une surface de référence lisse ; le relief est une
 * information à côté, pas une condition. Un simulateur qui afficherait « le
 * modèle X est réfuté » ferait passer une prédiction pour une observation ; un
 * simulateur qui présenterait un relief NON RELEVÉ comme une absence
 * d'obstacle ferait passer son ignorance pour une mesure.
 *
 * L'EXAGÉRATION VERTICALE EST ÉCRITE, TOUJOURS
 * ────────────────────────────────────────────
 * Sur 35 km de trajet, une occultation de 40 m fait 0,1 % de la largeur : à
 * l'échelle, la coupe serait un trait. Elle est donc exagérée verticalement,
 * et c'est précisément ce qui permet à un même écart de paraître spectaculaire
 * ou anodin selon le facteur choisi. Le facteur est calculé, affiché en clair
 * sur le dessin, et rappelé sous lui.
 */

import { dash } from '@/lib/design-tokens';
import FicheTerrainPanneau from './FicheTerrainPanneau';
import {
  type Cible,
  altitudeDepuisArc,
  arcTangence,
} from '@/lib/visee-optique/noyau';
import { RESERVE_GEOCODAGE, type Position } from '@/lib/visee-optique/geocodage-ign';
import {
  type AnalyseRelief,
  type Occlusion,
  largeurOcclusionM,
} from '@/lib/visee-optique/relief';
import {
  K_ENVELOPPE_MAX,
  K_ENVELOPPE_MIN,
  K_STANDARD,
  MOTIF_REFRACTION_STANDARD,
  motifRefraction,
  MOTIF_RELIEF_RELEVE,
  MOTIF_SANS_RELIEF,
  MOTIF_SEUIL,
  SEUIL_DISCRIMINATION_FRACTION,
  type Verdict,
  formatDecimal,
} from '@/lib/visee-optique/simulation';

const ACCENT = dash.opal;

export interface Simulation {
  D: number;
  azimutDeg: number;
  positionObs: Position;
  positionCible: Position;
  /** L'occultation à la base au gradient moyen : c'est elle qui est jugée. */
  masqueeStandardM: number;
  /**
   * Ce que l'ignorance du profil de température laisse comme écart. Les deux
   * bornes valent la même chose quand l'analyste déclare son coefficient :
   * afficher une enveloppe contredirait ce qu'il affirme connaître.
   */
  masqueeEnveloppeMinM: number;
  masqueeEnveloppeMaxM: number;
  /** Le coefficient de réfraction RÉELLEMENT employé, standard ou déclaré. */
  kEmploye: number;
  kPersonnalise: boolean;
  verdict: Verdict;
  cible: Cible;
  h: number;
  /** Le rayon employé pour le TRACÉ, au gradient moyen. */
  rTrace: number;
}

/**
 * Le relevé du terrain, quand il a été demandé.
 *
 * Il est SÉPARÉ de `Simulation` à dessein : la géométrie ne dépend pas de lui,
 * ne l'attend pas, et se passe très bien de son absence. Le fondre dans la
 * simulation laisserait croire que le verdict en tient compte — il n'en tient
 * pas compte, et c'est une décision, pas un oubli.
 */
export interface ReleveRelief {
  analyse: AnalyseRelief;
  /** Les points qui dépassent, regroupés en RELIEFS contigus. */
  occlusions: Occlusion[];
  /** Le pas réellement employé pour interroger le service. */
  pasM: number | null;
  source: string;
  /** Les points sans donnée, en distance depuis le poste. Jamais comblés. */
  lacunesM: number[];
  reserve: string;
}

/** L'état du relevé, vu par l'interface. */
export type EtatRelief =
  | { etat: 'inactif' }
  | { etat: 'en-cours' }
  | { etat: 'fait'; releve: ReleveRelief }
  | { etat: 'echec'; motif: string };

/**
 * Un nombre à l'écran : arrondi comme le paquet Python, groupé comme le
 * français.
 *
 * L'ARRONDI PASSE D'ABORD PAR `formatDecimal`, et ce n'est pas un détour.
 * `toLocaleString` arrondit les égalités à l'écart de zéro, le « %.*f » du
 * paquet de référence les arrondit vers le pair : le seuil d'une cible de
 * 12,5 m valait 1,3 m à l'écran et 1,2 m sur la fiche terrain imprimée, pour
 * la même visée. Arrondir avant de grouper rend l'opération de groupement
 * insensible à la convention, et les deux affichages redeviennent le même
 * chiffre.
 */
const fmt = (x: number | null | undefined, n = 1): string =>
  x === null || x === undefined || !Number.isFinite(x)
    ? 'indisponible'
    : Number(formatDecimal(x, n))
      .toLocaleString('fr-FR', { minimumFractionDigits: n, maximumFractionDigits: n });

const fmtKm = (m: number) => `${fmt(m / 1000, 2)} km`;

// ── Les deux schémas ────────────────────────────────────────────────────────
//
// POURQUOI DEUX, ET POURQUOI LA TERRE SE BOMBE
// ────────────────────────────────────────────
// Un tracé unique en « altitude au-dessus de la surface » faisait plonger la
// ligne de visée sous le niveau zéro. Le calcul était exact — une corde droite
// entre deux points bas traverse bel et bien la Terre — mais l'image était
// absurde : une visée ne passe pas sous le sol.
//
// C'est le repère qu'il fallait changer, pas le calcul. Les altitudes sont
// donc décalées du BOMBEMENT de la surface au-dessus de la corde A–B :
//
//     b(d) = R · [ cos(d/R − D/2R) − cos(D/2R) ]
//
// nul aux deux extrémités, égal à la flèche au milieu. La surface devient un
// arc qui monte, et c'est LUI qui vient couper la visée — ce qui est la
// description physique juste. Le décalage étant le même pour la surface et
// pour la visée, tous les ÉCARTS VERTICAUX sont préservés exactement : la
// bande rouge sur la cible mesure toujours la hauteur masquée réelle.
//
// La visée tracée est le RAYON RASANT, celui qui frôle la surface à
// l'horizon. C'est le rayon le plus bas que l'observateur puisse envoyer, donc
// la limite de ce qu'il voit — et il ne descend jamais sous la surface. Sa
// hauteur au-dessus de la base de la cible vaut exactement l'occultation
// calculée ; les deux ont été confrontées, l'écart est nul à l'epsilon machine.

const L = 860;
const Ht = 300;
const MG = 62;
// La marge droite loge le repère de la cible ET l'étiquette de la dernière
// graduation, qui déborderait sinon hors du cadre.
const MD = 52;
const MH = 26;
const MB = 42;

const VERT = '#3D9E7C';
const ROUGE = '#C45E6A';

/** Le bombement de la surface au-dessus de la corde A–B, à l'abscisse d. */
function bombement(d: number, D: number, R: number): number {
  const a = D / (2 * R);
  return R * (Math.cos(d / R - a) - Math.cos(a));
}

/**
 * L'altitude du rayon rasant au-dessus de la surface, à l'abscisse d.
 *
 * En deçà de l'horizon le rayon descend vers son point de tangence, au-delà il
 * remonte : c'est la même courbe des deux côtés, prise en valeur absolue de
 * l'écart à l'horizon. Elle vaut la hauteur de l'œil en d = 0 et zéro à
 * l'horizon.
 */
function altitudeRayonRasant(d: number, sH: number, R: number): number {
  const arc = Math.abs(d - sH);
  // Au-delà de π/2 la construction de tangence sort de son domaine. Cela
  // n'arrive que sur des visées de plusieurs milliers de kilomètres, où la
  // cible est de toute façon enfouie ; on borne le TRACÉ plutôt que de lever.
  if (arc / R >= Math.PI / 2 - 1e-9) return Number.NaN;
  return altitudeDepuisArc(arc, R);
}

interface Echelle {
  x: (d: number) => number;
  y: (z: number) => number;
  zMin: number;
  zMax: number;
  exageration: number;
}

function faireEchelle(D: number, zMin: number, zMax: number): Echelle {
  const marge = Math.max(5, (zMax - zMin) * 0.1);
  const bas = zMin - marge;
  const haut = zMax + marge;
  return {
    x: (d) => MG + (d / D) * (L - MG - MD),
    y: (z) => MH + (1 - (z - bas) / (haut - bas)) * (Ht - MH - MB),
    zMin: bas,
    zMax: haut,
    exageration: ((Ht - MH - MB) / (haut - bas)) / ((L - MG - MD) / D),
  };
}

function Cadre({ D, e, titre, children }: {
  D: number; e: Echelle; titre: string; children: React.ReactNode;
}) {
  const graduations = [0, 0.25, 0.5, 0.75, 1].map((f) => f * D);
  return (
    <div style={{ overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${L} ${Ht}`} style={{ width: '100%', minWidth: 460, height: 'auto', display: 'block' }}
        role="img" aria-label={titre}>
        <rect x={0} y={0} width={L} height={Ht} fill="#0d1117" rx={8} />
        {graduations.map((d) => (
          <g key={`g${d}`}>
            <line x1={e.x(d)} y1={MH} x2={e.x(d)} y2={Ht - MB} stroke="#1e2733" strokeWidth={1} />
            <text x={e.x(d)} y={Ht - MB + 16} fill="#6b7d8f" fontSize={10}
              fontFamily="ui-monospace, monospace" textAnchor="middle">
              {fmt(d / 1000, 1)} km
            </text>
          </g>
        ))}
        {[e.zMin, (e.zMin + e.zMax) / 2, e.zMax].map((z) => (
          <g key={`n${z}`}>
            <line x1={MG} y1={e.y(z)} x2={L - MD} y2={e.y(z)} stroke="#1e2733" strokeWidth={1} />
            <text x={MG - 6} y={e.y(z) + 3} fill="#6b7d8f" fontSize={10}
              fontFamily="ui-monospace, monospace" textAnchor="end">
              {fmt(z, 0)} m
            </text>
          </g>
        ))}
        {children}
        <text x={L - MD} y={MH - 10} fill="#8a9bad" fontSize={10.5}
          fontFamily="ui-monospace, monospace" textAnchor="end">
          exagération verticale × {Math.round(e.exageration).toLocaleString('fr-FR')}
        </text>
      </svg>
    </div>
  );
}

/** La cible dessinée, découpée en masqué et émergent. */
function CibleDessinee({ e, D, base, masquee, H }: {
  e: Echelle; D: number; base: number; masquee: number; H: number;
}) {
  const hautMasque = base + Math.min(masquee, H);
  const sommet = base + H;
  return (
    <g>
      {masquee > 0 && (
        <line x1={e.x(D)} y1={e.y(base)} x2={e.x(D)} y2={e.y(hautMasque)}
          stroke={ROUGE} strokeWidth={6} strokeLinecap="butt" />
      )}
      {hautMasque < sommet && (
        <line x1={e.x(D)} y1={e.y(hautMasque)} x2={e.x(D)} y2={e.y(sommet)}
          stroke={VERT} strokeWidth={6} strokeLinecap="butt" />
      )}
      <circle cx={e.x(D)} cy={e.y(sommet)} r={3} fill={hautMasque < sommet ? VERT : ROUGE} />
    </g>
  );
}

function chemin(pts: readonly (readonly [number, number])[], e: Echelle): string {
  return pts
    .filter(([, z]) => Number.isFinite(z))
    .map(([d, z], i) => `${i === 0 ? 'M' : 'L'}${e.x(d).toFixed(2)},${e.y(z).toFixed(2)}`)
    .join(' ');
}

const N = 240;

function Legende({ couleur, texte, tirets }: { couleur: string; texte: string; tirets?: boolean }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--ink-muted)' }}>
      <span style={{ width: 20, height: 0, borderTop: `2px ${tirets ? 'dashed' : 'solid'} ${couleur}` }} />
      {texte}
    </span>
  );
}

function SchemaSpherique({ s, e }: { s: Simulation; e: Echelle }) {
  const { D, cible, h, rTrace } = s;
  const sH = arcTangence(h, rTrace);
  const ech = Array.from({ length: N + 1 }, (_, i) => (i * D) / N);

  // La surface : l'arc qui monte. C'est lui qui coupe la visée.
  const surface = ech.map((d) => [d, bombement(d, D, rTrace)] as const);
  // Le rayon rasant, dans le même repère décalé.
  const rasant = ech.map((d) =>
    [d, altitudeRayonRasant(d, sH, rTrace) + bombement(d, D, rTrace)] as const);

  const bas = e.y(e.zMin);
  const sol = `${chemin(surface, e)} L${e.x(D).toFixed(2)},${bas.toFixed(2)} L${e.x(0).toFixed(2)},${bas.toFixed(2)} Z`;
  const horizonVisible = sH < D;

  return (
    <>
      <Cadre D={D} e={e} titre={`Modèle sphérique : coupe sur ${fmtKm(D)}`}>
        <path d={sol} fill="#243044" stroke="#3d5068" strokeWidth={1.4} />
        <path d={chemin(rasant, e)} fill="none" stroke={ACCENT} strokeWidth={2} />
        {horizonVisible && (
          <g>
            <line x1={e.x(sH)} y1={e.y(bombement(sH, D, rTrace))} x2={e.x(sH)} y2={MH + 6}
              stroke="#5a6b7d" strokeWidth={1} strokeDasharray="3 3" />
            <text x={e.x(sH)} y={MH + 2} fill="#8a9bad" fontSize={10}
              fontFamily="ui-monospace, monospace" textAnchor="middle">
              horizon {fmt(sH / 1000, 1)} km
            </text>
          </g>
        )}
        <circle cx={e.x(0)} cy={e.y(h)} r={4} fill={ACCENT} />
        <CibleDessinee e={e} D={D} base={cible.zB} masquee={s.masqueeStandardM} H={cible.H} />
      </Cadre>
      <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
        La <strong>surface se bombe</strong> entre les deux points : c’est elle qui vient couper
        la visée, et non la visée qui s’enfoncerait sous le sol. Le trait vert est le{' '}
        <strong>rayon rasant</strong>, le plus bas que l’observateur puisse envoyer — il frôle la
        surface à l’horizon{horizonVisible ? ` (${fmt(sH / 1000, 1)} km)` : ''} puis remonte, et
        arrive sur la cible à <strong>{fmt(s.masqueeStandardM)} m</strong> au-dessus de sa base.
        Tout ce qui est sous ce trait est masqué : c’est la bande rouge.
      </p>
    </>
  );
}

function SchemaPlat({ s, e }: { s: Simulation; e: Echelle }) {
  const { D, cible, h } = s;
  const sommet = cible.zB + cible.H;
  const bas = e.y(e.zMin);
  const sol = `${chemin([[0, 0], [D, 0]], e)} L${e.x(D).toFixed(2)},${bas.toFixed(2)} L${e.x(0).toFixed(2)},${bas.toFixed(2)} Z`;

  return (
    <>
      <Cadre D={D} e={e} titre={`Modèle plat : coupe sur ${fmtKm(D)}`}>
        <path d={sol} fill="#243044" stroke="#3d5068" strokeWidth={1.4} />
        <path d={chemin([[0, h], [D, sommet]], e)} fill="none"
          stroke={dash.saffron} strokeWidth={2} strokeDasharray="7 5" />
        <circle cx={e.x(0)} cy={e.y(h)} r={4} fill={dash.saffron} />
        <CibleDessinee e={e} D={D} base={cible.zB} masquee={0} H={cible.H} />
      </Cadre>
      <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
        Aucune courbure : la surface est plate et la visée va droit de l’œil au sommet. Rien ne
        s’interpose, donc <strong>la cible entière est visible</strong> — du pied au sommet, 0 m
        masqué. Ce modèle n’a aucun paramètre libre : il prédit la même chose à toute distance.
      </p>
    </>
  );
}

// ── Le panneau ──────────────────────────────────────────────────────────────

export default function ResultatVisee({ sim, relief, onRelever }: {
  sim: Simulation;
  /** L'état du relevé de terrain. Optionnel : la géométrie n'en dépend pas. */
  relief?: EtatRelief;
  /** Déclenche le relevé. Absent = le relevé n'est pas proposé. */
  onRelever?: () => void;
}) {
  const H = sim.cible.H;
  const v = sim.verdict;
  const masquee = v.hauteurMasqueeBaseM;
  // Au-delà de la distance limite, la cible est enfouie sous l'horizon : la
  // hauteur masquée dépasse alors sa hauteur totale, et le dire vaut mieux que
  // d'afficher « 100 % masqué » qui perdrait de combien.
  const enfouie = masquee > H;

  return (
    <div>
      {/* ── Le bandeau de décision ── */}
      <div style={{
        background: v.discriminante ? dash.opalSoft : dash.saffronSoft,
        border: `1px solid ${(v.discriminante ? ACCENT : dash.saffron)}55`,
        borderLeft: `4px solid ${v.discriminante ? ACCENT : dash.saffron}`,
        borderRadius: 10, padding: '18px 22px', marginBottom: 18,
      }}>
        <div style={{
          fontSize: 19, fontWeight: 700, marginBottom: 7,
          color: v.discriminante ? ACCENT : dash.saffron,
        }}>
          {v.discriminante ? 'Visée discriminante' : 'Visée non discriminante'}
        </div>
        <p style={{ margin: 0, fontSize: 14, lineHeight: 1.65, color: dash.ink }}>{v.motif}</p>
      </div>

      {/* ── Les deux prédictions, face à face ── */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 14, marginBottom: 18,
      }}>
        <Carte
          titre="Modèle sphérique"
          couleur={ACCENT}
          principal={`${fmt(masquee)} m de la base masqués`}
          soustitre={enfouie
            ? `sur une cible de ${fmt(H)} m — elle est entièrement sous l’horizon`
            : `sur ${fmt(H)} m de hauteur totale`}
          lignes={[
            [enfouie ? 'Sommet sous l’horizon' : 'Part masquée depuis la base',
              enfouie
                ? `${fmtKm(masquee - H)} en dessous`
                : `${fmt(100 * v.fractionMasqueeBase)} %`],
            ['Ce qui reste visible',
              enfouie ? 'rien — le sommet est passé sous l’horizon'
                : `${fmt(H - masquee)} m, en partant du sommet`],
            [sim.kPersonnalise ? 'Réfraction déclarée' : 'Selon la réfraction',
              sim.kPersonnalise
                ? `k = ${fmt(sim.kEmploye, 2)}, valeur unique — aucune enveloppe`
                : `de ${fmt(sim.masqueeEnveloppeMinM)} à ${fmt(sim.masqueeEnveloppeMaxM)} m masqués`],
          ]}
        />
        <Carte
          titre="Modèle plat"
          couleur={dash.saffron}
          principal={`${fmt(v.hauteurMasqueePlatM)} m de la base masqués`}
          soustitre="aucune courbure, par construction"
          lignes={[
            ['Part masquée depuis la base', '0,0 %'],
            ['Ce qui reste visible', `${fmt(H)} m — la cible entière`],
            ['Selon la réfraction', '0,0 m à toute distance, quel que soit k'],
          ]}
        />
      </div>

      {/* ── L'écart, qui est ce qu'une photographie doit montrer ── */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderLeft: `3px solid ${v.discriminante ? ACCENT : dash.saffron}`,
        borderRadius: 8, padding: '14px 18px', marginBottom: 18,
      }}>
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.65, color: 'var(--ink)' }}>
          <strong>Écart entre les deux prédictions : {fmt(v.ecartEntreModelesM)} m</strong> à la
          base de la cible, soit {fmt(100 * v.fractionMasqueeBase)} % de sa hauteur. C’est
          exactement ce qu’une photographie doit pouvoir montrer pour départager les deux
          modèles — le seuil retenu ici est de {fmt(100 * SEUIL_DISCRIMINATION_FRACTION, 0)} %,
          soit {fmt(H * SEUIL_DISCRIMINATION_FRACTION, 1)} m sur cette cible.
        </p>
      </div>

      {/* ── Les deux schémas ──
          Une SEULE échelle verticale pour les deux : sans cela, la bande rouge
          d'un schéma ne serait pas comparable à la cible entière de l'autre, et
          la comparaison — qui est tout l'objet de l'outil — serait fausse. */}
      {(() => {
        // L'échelle doit contenir le plus haut de tout ce qui est tracé dans
        // les DEUX schémas : le sommet de la cible, l'œil, la flèche du
        // bombement, et le rayon rasant à son arrivée.
        const fleche = bombement(sim.D / 2, sim.D, sim.rTrace);
        const sommet = sim.cible.zB + sim.cible.H;
        const zMax = Math.max(sim.h, sommet, fleche + sim.masqueeStandardM, fleche);
        const e = faireEchelle(sim.D, 0, zMax);
        return (
          // Les deux schémas sont EMPILÉS, pas côte à côte : un dessin de
          // 860 px de large réduit à une demi-colonne sortait la cible du
          // cadre — or la cible découpée en rouge et vert est tout ce que le
          // schéma existe pour montrer. L'échelle verticale restant commune,
          // la comparaison se fait aussi bien de haut en bas.
          <div style={{ display: 'grid', gap: 14, marginBottom: 18 }}>
            <div style={{
              background: 'var(--card)', border: '1px solid var(--border)',
              borderTop: `3px solid ${ACCENT}`, borderRadius: 10, padding: '16px 18px',
            }}>
              <div style={{
                fontSize: 11, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
                color: ACCENT, textTransform: 'uppercase', marginBottom: 12,
              }}>Modèle sphérique — {fmtKm(sim.D)}</div>
              <SchemaSpherique s={sim} e={e} />
            </div>
            <div style={{
              background: 'var(--card)', border: '1px solid var(--border)',
              borderTop: `3px solid ${dash.saffron}`, borderRadius: 10, padding: '16px 18px',
            }}>
              <div style={{
                fontSize: 11, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
                color: dash.saffron, textTransform: 'uppercase', marginBottom: 12,
              }}>Modèle plat — {fmtKm(sim.D)}</div>
              <SchemaPlat s={sim} e={e} />
            </div>
          </div>
        );
      })()}

      <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', marginBottom: 18, fontSize: 12 }}>
        <Legende couleur={ROUGE} texte="Masqué à la base" />
        <Legende couleur={VERT} texte="Émergent, visible" />
        <Legende couleur={ACCENT} texte="Rayon rasant — modèle sphérique" />
        <Legende couleur={dash.saffron} texte="Visée droite — modèle plat" tirets />
        <Legende couleur="#3d5068" texte="Surface de référence" />
      </div>

      {/* ── Le bloc explicatif, unique et rétractable ── */}
      <details style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '14px 18px',
      }}>
        <summary style={{
          cursor: 'pointer', fontSize: 13.5, fontWeight: 600, color: ACCENT,
          minHeight: 32, display: 'flex', alignItems: 'center',
        }}>
          Comment ce résultat est calculé, et ce qu’il n’établit pas
        </summary>

        <div style={{ marginTop: 14, fontSize: 13, lineHeight: 1.7, color: 'var(--ink)' }}>
          <p style={{ margin: '0 0 12px' }}>
            <strong>La distance.</strong> Elle est calculée sur l’ellipsoïde terrestre
            réel, pas sur une sphère : {fmtKm(sim.D)} entre vos deux points, azimut{' '}
            {fmt(sim.azimutDeg, 1)}°. La Terre étant aplatie aux pôles, son rayon de
            courbure change avec la latitude et la direction visée — jusqu’à 1 % d’écart,
            ce qui se voit sur une visée longue. Aucune longueur n’est refusée.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>Ce qui est mesuré : le pied de la cible.</strong> C’est lui qui
            disparaît en premier sous l’horizon, et c’est là que les deux modèles divergent
            en premier — le sommet, lui, reste visible longtemps après. La hauteur masquée
            n’est pas bornée à celle de la cible : au-delà d’une certaine distance elle
            continue de croître et dit de combien la cible est passée sous l’horizon.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>La réfraction.</strong> {motifRefraction(sim.kEmploye)}
            {!sim.kPersonnalise && (
              <> La fourchette affichée dans la carte va donc de {fmt(K_ENVELOPPE_MIN, 2)} à{' '}
              {fmt(K_ENVELOPPE_MAX, 2)}.</>
            )}
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>Le seuil du verdict.</strong> {MOTIF_SEUIL} Sur votre cible de{' '}
            {fmt(H)} m, ce seuil de {fmt(100 * SEUIL_DISCRIMINATION_FRACTION, 0)} % vaut{' '}
            {fmt(H * SEUIL_DISCRIMINATION_FRACTION, 2)} m.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>Les hauteurs employées.</strong> Observateur : {fmt(sim.h)} m au-dessus
            de la surface de référence. Cible : {fmt(sim.cible.H)} m de hauteur, sa base
            étant prise à cette même surface. Le formulaire ne demande qu’une hauteur par
            point, et la base de la cible n’est donc pas surélevée : si votre cible se
            dresse sur une falaise, comptez la hauteur totale depuis le niveau de la mer.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>D’où viennent vos deux points.</strong> Observateur :{' '}
            {sim.positionObs.libelle ?? `${fmt(sim.positionObs.latitude, 5)}, ${fmt(sim.positionObs.longitude, 5)}`}{' '}
            ({sim.positionObs.origine}). Cible :{' '}
            {sim.positionCible.libelle ?? `${fmt(sim.positionCible.latitude, 5)}, ${fmt(sim.positionCible.longitude, 5)}`}{' '}
            ({sim.positionCible.origine}).
          </p>

          <BlocRelief sim={sim} relief={relief} onRelever={onRelever} />

          <p style={{
            margin: '0 0 12px', padding: '12px 14px', borderRadius: 8,
            background: 'var(--bg)', borderLeft: `3px solid ${dash.rose}`,
          }}>
            <strong>Ce que cette simulation n’établit pas.</strong> Rien sur ce qui est
            réellement visible depuis ce point. Elle dit ce que chaque modèle{' '}
            <em>implique</em> sur une surface lisse, avec les données que vous avez saisies
            — et vos hauteurs valent ce que vaut leur source. La réfraction est supposée
            homogène le long du trajet, ce qu’elle n’est pas au voisinage d’un sol chaud ou
            d’une mer froide. Confronter ces prédictions au réel demande une photographie
            mesurée.
          </p>

          {(sim.positionObs.origine.includes('IGN')
            || sim.positionCible.origine.includes('IGN')) && (
            <p style={{ margin: 0, fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
              <strong>Réserve sur le géocodage.</strong> {RESERVE_GEOCODAGE}
            </p>
          )}
        </div>
      </details>

      {/* La fiche vient APRÈS le bloc explicatif : on emporte une visée une
          fois qu'on a compris ce qu'elle dit, pas avant. */}
      <FicheTerrainPanneau sim={sim} />
    </div>
  );
}

function Carte({ titre, couleur, principal, soustitre, lignes }: {
  titre: string; couleur: string; principal: string; soustitre: string;
  lignes: [string, string][];
}) {
  return (
    <div style={{
      background: 'var(--card)', border: '1px solid var(--border)',
      borderTop: `3px solid ${couleur}`, borderRadius: 10, padding: '16px 18px',
    }}>
      <div style={{ fontSize: 13, fontWeight: 700, color: 'var(--ink-muted)', marginBottom: 8 }}>
        {titre}
      </div>
      <div style={{ fontSize: 21, fontWeight: 700, color: couleur, lineHeight: 1.25 }}>
        {principal}
      </div>
      <div style={{ fontSize: 12, color: 'var(--ink-muted)', marginBottom: 12 }}>{soustitre}</div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
        <tbody>
          {lignes.map(([k, val]) => (
            <tr key={k}>
              <td style={{
                padding: '6px 10px 6px 0', color: 'var(--ink-muted)', verticalAlign: 'top',
                borderBottom: '1px solid var(--border)', width: '46%',
              }}>{k}</td>
              <td style={{
                padding: '6px 0', color: 'var(--ink)', verticalAlign: 'top',
                borderBottom: '1px solid var(--border)',
              }}>{val}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

/**
 * Le relief intermédiaire : ce qui coupe la visée entre les deux points.
 *
 * TROIS ÉTATS, ET ILS NE DISENT PAS LA MÊME CHOSE
 * ───────────────────────────────────────────────
 * « Pas relevé », « relevé et dégagé » et « relevé, N occlusions » sont trois
 * réponses distinctes, et la première n'est surtout pas la deuxième. Un
 * simulateur qui afficherait « aucun obstacle » faute d'avoir regardé
 * donnerait une assurance qu'il n'a pas — c'est le défaut pour lequel le
 * modèle de terrain avait été retiré, et il est écarté ici en nommant l'état
 * plutôt qu'en le déduisant.
 *
 * LE VERDICT N'EN TIENT PAS COMPTE
 * ────────────────────────────────
 * Le relief est rendu à titre d'INFORMATION. Il ne change ni la hauteur
 * masquée, ni la fraction, ni le caractère discriminant de la visée : ces
 * grandeurs répondent à « que prédit chaque modèle », pas à « que voit-on
 * depuis ce poste ». Les mêler sous un seul « invisible » perdrait ce qui
 * distingue les deux causes — une cible peut être entièrement au-dessus de
 * l'horizon géométrique ET entièrement cachée par une colline.
 */
function BlocRelief({ sim, relief, onRelever }: {
  sim: Simulation; relief?: EtatRelief; onRelever?: () => void;
}) {
  const etat = relief?.etat ?? 'inactif';
  const encadre = (couleur: string, contenu: React.ReactNode) => (
    <div style={{
      margin: '0 0 12px', padding: '12px 14px', borderRadius: 8,
      background: 'var(--bg)', borderLeft: `3px solid ${couleur}`,
      fontSize: 13, lineHeight: 1.7, color: 'var(--ink)',
    }}>{contenu}</div>
  );

  if (etat === 'en-cours') {
    return encadre(dash.saffron, (
      <><strong>Relief intermédiaire.</strong> Relevé du terrain en cours…</>
    ));
  }

  if (etat === 'echec') {
    const motif = relief && relief.etat === 'echec' ? relief.motif : '';
    return encadre(dash.rose, (
      <>
        <strong>Le relevé du terrain a échoué.</strong> {motif}
        {' '}La simulation ci-dessus, elle, n’en dépend pas : elle a tourné sur
        vos coordonnées et reste valide. Le relief reste <em>non évalué</em>,
        ce qui n’est pas « aucun obstacle ».
      </>
    ));
  }

  if (etat === 'inactif' || relief === undefined || relief.etat !== 'fait') {
    return encadre(dash.saffron, (
      <>
        <strong>Relief intermédiaire : non relevé.</strong> {MOTIF_SANS_RELIEF}
        {onRelever && (
          <div style={{ marginTop: 11 }}>
            <button
              onClick={onRelever}
              style={{
                padding: '9px 16px', fontSize: 13, fontWeight: 600, minHeight: 40,
                cursor: 'pointer', background: 'transparent', color: ACCENT,
                border: `1px solid ${ACCENT}80`, borderRadius: 6,
              }}
            >Relever le terrain auprès de l’IGN</button>
          </div>
        )}
      </>
    ));
  }

  const { analyse, occlusions, pasM, source, lacunesM, reserve } = relief.releve;
  const degage = occlusions.length === 0;

  return encadre(degage ? ACCENT : dash.rose, (
    <>
      <strong>
        {degage
          ? 'Relief intermédiaire : aucune occlusion.'
          : `Relief intermédiaire : ${occlusions.length} occlusion${occlusions.length > 1 ? 's' : ''} `
            + `entre l’observateur et la cible.`}
      </strong>
      {degage ? (
        <>
          {' '}Sur le terrain relevé, la visée passe au-dessus de tout le trajet
          {analyse.margeMinimaleM !== null && (
            <>, avec une marge minimale de <strong>{fmt(analyse.margeMinimaleM)} m</strong>
            {analyse.distanceMargeMinimaleM !== null && <> à {fmtKm(analyse.distanceMargeMinimaleM)}</>}</>
          )}.
        </>
      ) : (
        <ul style={{ margin: '9px 0 0', paddingLeft: 20 }}>
          {occlusions.map((o, i) => {
            const large = largeurOcclusionM(o);
            return (
              <li key={i} style={{ marginBottom: 6 }}>
                à <strong>{fmtKm(o.sommet.distanceM)}</strong> — le terrain
                culmine à {fmt(o.sommet.altitudeTerrainM)} m et dépasse la ligne
                de visée de <strong>{fmt(o.sommet.manqueM)} m</strong>
                {large > 0 && <> ; le relief coupe la visée sur {fmt(large / 1000, 2)} km au moins</>}
                {' '}({o.nbPoints} point{o.nbPoints > 1 ? 's' : ''} de mesure).
              </li>
            );
          })}
        </ul>
      )}

      <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
        Terrain relevé tous les {pasM === null ? 'pas inconnu' : `${fmt(pasM, 0)} m`} sur
        {' '}{fmtKm(sim.D)}, source {source}.
        {pasM !== null && (
          <> Un relief plus étroit que ce pas peut passer entre deux mesures — et un
          relief manqué ne se rattrape pas.</>
        )}
        {lacunesM.length > 0 && (
          <> {lacunesM.length} point{lacunesM.length > 1 ? 's' : ''} sans donnée
          {' '}dans le modèle, jamais comblé{lacunesM.length > 1 ? 's' : ''} par une
          valeur inventée : le trajet n’est donc pas relevé en entier.</>
        )}
      </p>

      <p style={{ margin: '8px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
        <strong>Ce que ce relevé n’établit pas.</strong> {MOTIF_RELIEF_RELEVE}
      </p>
      <p style={{ margin: '8px 0 0', fontSize: 11.5, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
        {reserve}
      </p>
      <p style={{ margin: '8px 0 0', fontSize: 11.5, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
        Le verdict affiché plus haut <strong>ne tient pas compte</strong> de ce
        relief : il dit ce que chaque modèle prédit sur une surface lisse, pas
        ce qui est visible depuis ce poste.
      </p>
    </>
  ));
}
