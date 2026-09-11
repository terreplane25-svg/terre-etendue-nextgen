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
export interface AnalyseParLigne {
  /** La ligne qui rejoint le PIED : un obstacle ici rend la mesure impossible. */
  base: AnalyseRelief;
  /** La ligne qui rejoint le SOMMET : un obstacle ici cache la cible entière. */
  sommet: AnalyseRelief;
  occlusionsBase: Occlusion[];
  occlusionsSommet: Occlusion[];
}

export interface ReleveRelief {
  /**
   * Les deux modèles sont analysés SÉPARÉMENT, et c'est le point.
   *
   * Le profil du terrain est le même, la ligne de visée non : sur le globe la
   * surface se bombe entre les deux points, sur le plan elle ne se bombe pas.
   * Un même relief peut donc couper l'une et pas l'autre — et quand c'est le
   * cas, les deux modèles ne prédisent pas la même VISIBILITÉ, ce qui est une
   * information et non une contradiction à masquer.
   */
  spherique: AnalyseParLigne;
  plat: AnalyseParLigne;
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

export default function ResultatVisee({ sim, relief }: {
  sim: Simulation;
  /**
   * L'état du relevé de terrain. Optionnel, et c'est la règle qui ne se
   * négocie pas : la géométrie n'attend pas le relief, ne dépend pas de lui,
   * et s'affiche entière même quand le service ne répond pas.
   */
  relief?: EtatRelief;
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
      {/* ── Ce que le relief interdit, AVANT le verdict géométrique ──
          Il ne le remplace pas : une visée peut être discriminante en
          géométrie ET impossible à faire parce qu'une colline est au milieu.
          Les deux énoncés sont vrais en même temps, et les fondre en perdrait
          un. Rien ne s'affiche quand le terrain ne coupe rien. */}
      <BandeauRelief relief={relief} />

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
              <AnnotationRelief relief={relief} modele="spherique" />
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
              <AnnotationRelief relief={relief} modele="plat" />
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
      <details className="tei-depliant" style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '14px 18px',
      }}>
        <summary style={{ fontSize: 13.5, fontWeight: 600 }}>
          <svg className="tei-depliant-fleche" width="11" height="11" viewBox="0 0 11 11"
            aria-hidden focusable="false">
            <path d="M3.5 1.5 L7.5 5.5 L3.5 9.5" fill="none" stroke="currentColor"
              strokeWidth="1.9" strokeLinecap="round" strokeLinejoin="round" />
          </svg>
          <span className="tei-depliant-titre">Comment ce résultat est calculé, et ce qu’il n’établit pas</span>
          <span className="tei-depliant-invite" aria-hidden>
            <span className="tei-depliant-invite-ouvrir">Afficher</span>
            <span className="tei-depliant-invite-fermer">Masquer</span>
          </span>
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

          <BlocRelief sim={sim} relief={relief} />

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

// ── Le relief intermédiaire ─────────────────────────────────────────────────
//
// TROIS ÉTATS, ET ILS NE DISENT PAS LA MÊME CHOSE
// ───────────────────────────────────────────────
// « Pas relevé », « relevé et dégagé » et « relevé, N occlusions » sont trois
// réponses distinctes, et la première n'est surtout pas la deuxième. Un
// simulateur qui afficherait « aucun obstacle » faute d'avoir regardé donnerait
// une assurance qu'il n'a pas.
//
// DEUX LIGNES, DEUX CONSÉQUENCES
// ──────────────────────────────
// La ligne qui rejoint le SOMMET dit si la cible est entièrement cachée. Celle
// qui rejoint la BASE dit si son pied est visible — et c'est le pied que le
// protocole mesure. Un relief peut couper la seconde sans couper la première :
// la cible reste visible, et la mesure est pourtant impossible. Les deux sont
// donc rapportées à part.

/** Ce que le relief interdit, s'il interdit quelque chose. */
type Empechement = 'aucun' | 'base' | 'sommet';

function empechement(a: AnalyseParLigne): Empechement {
  if (a.occlusionsSommet.length > 0) return 'sommet';
  if (a.occlusionsBase.length > 0) return 'base';
  return 'aucun';
}

/** La plus haute occlusion d'une liste, ou null. */
function laPlusHaute(occ: Occlusion[]): Occlusion | null {
  if (occ.length === 0) return null;
  return occ.reduce((m, o) => (o.sommet.manqueM > m.sommet.manqueM ? o : m), occ[0]);
}

/**
 * La ligne d'annotation d'un schéma : combien d'occlusions, et la plus haute.
 *
 * Elle figure sous CHAQUE modèle, parce que les deux ne comptent pas les mêmes
 * obstacles : le profil du terrain est identique, la ligne de visée non. Sur le
 * globe la surface se bombe entre les deux points ; sur le plan elle ne se
 * bombe pas, et la visée passe donc plus haut au-dessus du terrain.
 */
export function AnnotationRelief({ relief, modele }: {
  relief?: EtatRelief; modele: 'spherique' | 'plat';
}) {
  const commun = {
    fontSize: 12, lineHeight: 1.55, margin: '6px 0 0',
  } as const;
  if (relief === undefined || relief.etat === 'inactif') {
    return <p style={{ ...commun, color: 'var(--ink-muted)' }}>Relief non relevé.</p>;
  }
  if (relief.etat === 'en-cours') {
    return <p style={{ ...commun, color: 'var(--ink-muted)' }}>Relevé du terrain en cours…</p>;
  }
  if (relief.etat === 'echec') {
    return (
      <p style={{ ...commun, color: 'var(--ink-muted)' }}>
        Relief non évalué — le relevé a échoué. Ce n’est pas « aucun obstacle ».
      </p>
    );
  }

  const a = relief.releve[modele];
  const emp = empechement(a);
  if (emp === 'aucun') {
    return (
      <p style={{ ...commun, color: ACCENT }}>
        Aucune occlusion : la visée passe au-dessus de tout le terrain relevé.
      </p>
    );
  }
  const occ = emp === 'sommet' ? a.occlusionsSommet : a.occlusionsBase;
  const pire = laPlusHaute(occ)!;
  return (
    <p style={{ ...commun, color: dash.rose, fontWeight: 600 }}>
      {occ.length} occlusion{occ.length > 1 ? 's' : ''}
      {emp === 'sommet'
        ? ` coup${occ.length > 1 ? 'ent' : 'e'} la visée jusqu’au sommet`
        : ` masqu${occ.length > 1 ? 'ent' : 'e'} le pied de la cible`}
      {' '}— la plus haute dépasse la ligne de {fmt(pire.sommet.manqueM)} m
      {' '}à {fmtKm(pire.sommet.distanceM)}.
    </p>
  );
}

/**
 * Le bandeau que le relief impose AVANT le verdict géométrique.
 *
 * Il ne remplace pas le verdict : il dit ce que le terrain interdit, ce qui est
 * une autre question. Une visée peut être parfaitement discriminante EN
 * GÉOMÉTRIE et impossible à faire parce qu'une colline est au milieu — les
 * deux énoncés sont vrais en même temps, et les fondre en perdrait un.
 */
export function BandeauRelief({ relief }: { relief?: EtatRelief }) {
  if (relief === undefined || relief.etat !== 'fait') return null;
  const s = empechement(relief.releve.spherique);
  const p = empechement(relief.releve.plat);
  if (s === 'aucun' && p === 'aucun') return null;

  const bloquant = s === 'sommet' || p === 'sommet';
  const couleur = bloquant ? dash.rose : dash.saffron;
  const occ = s === 'aucun' ? [] : (s === 'sommet'
    ? relief.releve.spherique.occlusionsSommet
    : relief.releve.spherique.occlusionsBase);
  const pire = laPlusHaute(occ);

  const lesDeuxDiffèrent = s !== p;

  return (
    <div style={{
      background: 'var(--card)', border: `1px solid ${couleur}`,
      borderLeft: `4px solid ${couleur}`, borderRadius: 10,
      padding: '16px 20px', marginBottom: 16,
    }}>
      <div style={{ fontSize: 17, fontWeight: 700, color: couleur, marginBottom: 7 }}>
        {bloquant
          ? 'Visée impossible — obstacle physique détecté'
          : 'Le pied de la cible est masqué par le relief'}
      </div>
      <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.65, color: 'var(--ink)' }}>
        {bloquant ? (
          <>
            Un relief coupe la ligne de visée jusqu’au sommet de la cible : elle
            n’est pas visible depuis ce poste, quelle que soit la courbure.
          </>
        ) : (
          <>
            Le sommet reste visible, mais un relief masque le <strong>pied</strong> de
            la cible. L’occultation par la courbure se mesure depuis la base :
            elle ne peut donc pas être mesurée depuis ce poste, même si la visée
            est discriminante en géométrie.
          </>
        )}
        {pire && (
          <>
            {' '}L’obstacle le plus critique culmine à {fmt(pire.sommet.altitudeTerrainM)} m
            et dépasse la ligne de <strong>{fmt(pire.sommet.manqueM)} m</strong>,
            à {fmtKm(pire.sommet.distanceM)} de l’observateur.
          </>
        )}
        {lesDeuxDiffèrent && (
          <>
            {' '}Les deux modèles ne disent pas la même chose ici — le détail
            figure sous chaque schéma. Ce désaccord n’est pas un défaut du
            calcul : la surface se bombe sur l’un et pas sur l’autre, donc la
            visée ne passe pas à la même hauteur au-dessus du terrain.
          </>
        )}
      </p>
      <p style={{ margin: '9px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-soft)' }}>
        Déplacer le poste d’observation, ou monter plus haut, change ce résultat.
        Le relief ne se contourne pas en changeant de modèle.
      </p>
    </div>
  );
}

/** Le détail du relief, dans le bloc explicatif. */
function BlocRelief({ sim, relief }: { sim: Simulation; relief?: EtatRelief }) {
  const encadre = (couleur: string, contenu: React.ReactNode) => (
    <div style={{
      margin: '0 0 12px', padding: '12px 14px', borderRadius: 8,
      background: 'var(--bg)', borderLeft: `3px solid ${couleur}`,
      fontSize: 13, lineHeight: 1.7, color: 'var(--ink)',
    }}>{contenu}</div>
  );

  if (relief === undefined || relief.etat === 'inactif') {
    return encadre(dash.saffron, (
      <><strong>Relief intermédiaire : non relevé.</strong> {MOTIF_SANS_RELIEF}</>
    ));
  }
  if (relief.etat === 'en-cours') {
    return encadre(dash.saffron, (
      <><strong>Relief intermédiaire.</strong> Relevé du terrain en cours…</>
    ));
  }
  if (relief.etat === 'echec') {
    return encadre(dash.rose, (
      <>
        <strong>Le relevé du terrain a échoué.</strong> {relief.motif}
        {' '}Le relief reste <em>non évalué</em>, ce qui n’est pas « aucun obstacle ».
      </>
    ));
  }

  const { spherique, plat, pasM, source, lacunesM, reserve } = relief.releve;
  const detail = (nom: string, a: AnalyseParLigne) => {
    const emp = empechement(a);
    if (emp === 'aucun') {
      return (
        <li key={nom} style={{ marginBottom: 7 }}>
          <strong>{nom}</strong> — aucune occlusion
          {a.sommet.margeMinimaleM !== null && (
            <>, marge minimale {fmt(a.sommet.margeMinimaleM)} m
            {a.sommet.distanceMargeMinimaleM !== null
              && <> à {fmtKm(a.sommet.distanceMargeMinimaleM)}</>}</>
          )}.
        </li>
      );
    }
    return (
      <li key={nom} style={{ marginBottom: 7 }}>
        <strong>{nom}</strong> — {a.occlusionsBase.length} occlusion
        {a.occlusionsBase.length > 1 ? 's' : ''} masqu
        {a.occlusionsBase.length > 1 ? 'ent' : 'e'} le pied
        {a.occlusionsSommet.length > 0
          ? <>, dont {a.occlusionsSommet.length} coup
            {a.occlusionsSommet.length > 1 ? 'ent' : 'e'} aussi la visée jusqu’au sommet</>
          : <> ; le sommet, lui, reste dégagé</>}.
        <ul style={{ margin: '4px 0 0', paddingLeft: 18 }}>
          {a.occlusionsBase.map((o, i) => (
            <li key={i} style={{ fontSize: 12.5, color: 'var(--ink-soft)' }}>
              à {fmtKm(o.sommet.distanceM)} — terrain à {fmt(o.sommet.altitudeTerrainM)} m,
              dépasse la ligne du pied de {fmt(o.sommet.manqueM)} m
              {largeurOcclusionM(o) > 0
                && <> sur {fmt(largeurOcclusionM(o) / 1000, 2)} km au moins</>}
              {' '}({o.nbPoints} point{o.nbPoints > 1 ? 's' : ''}).
            </li>
          ))}
        </ul>
      </li>
    );
  };

  return encadre(
    empechement(spherique) === 'aucun' && empechement(plat) === 'aucun' ? ACCENT : dash.rose,
    <>
      <strong>Relief intermédiaire, modèle par modèle.</strong>
      <ul style={{ margin: '8px 0 0', paddingLeft: 20 }}>
        {detail('Modèle sphérique', spherique)}
        {detail('Modèle plat', plat)}
      </ul>
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
    </>,
  );
}
