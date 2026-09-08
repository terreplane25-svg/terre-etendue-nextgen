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
 * Il se refuse à : conclure sur la forme de la Terre, et à dire ce qui bouche
 * réellement la vue. Ce qui est affiché, c'est ce que chaque modèle IMPLIQUE
 * sur une surface de référence lisse. Un simulateur qui afficherait « le
 * modèle X est réfuté » ferait passer une prédiction pour une observation ; un
 * simulateur qui prétendrait connaître les obstacles ferait passer un modèle
 * de terrain pour la réalité d'un poste.
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
import {
  type Cible,
  altitudeDepuisArc,
  arcTangence,
} from '@/lib/visee-optique/noyau';
import { RESERVE_GEOCODAGE, type Position } from '@/lib/visee-optique/geocodage-ign';
import {
  K_ENVELOPPE_MAX,
  K_ENVELOPPE_MIN,
  K_STANDARD,
  MOTIF_REFRACTION,
  MOTIF_SANS_RELIEF,
  MOTIF_SEUIL,
  SEUIL_DISCRIMINATION_FRACTION,
  type Verdict,
} from '@/lib/visee-optique/simulation';

const ACCENT = dash.opal;

export interface Simulation {
  D: number;
  azimutDeg: number;
  positionObs: Position;
  positionCible: Position;
  /** L'occultation à la base au gradient moyen : c'est elle qui est jugée. */
  masqueeStandardM: number;
  /** Ce que l'ignorance du profil de température laisse comme écart. */
  masqueeEnveloppeMinM: number;
  masqueeEnveloppeMaxM: number;
  verdict: Verdict;
  cible: Cible;
  h: number;
  /** Le rayon employé pour le TRACÉ, au gradient moyen. */
  rTrace: number;
}

const fmt = (x: number | null | undefined, n = 1): string =>
  x === null || x === undefined || !Number.isFinite(x)
    ? 'indisponible'
    : x.toLocaleString('fr-FR', { minimumFractionDigits: n, maximumFractionDigits: n });

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

export default function ResultatVisee({ sim }: { sim: Simulation }) {
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
            [enfouie ? 'Sommet sous l’horizon' : 'Part de la cible masquée',
              enfouie
                ? `${fmtKm(masquee - H)} en dessous`
                : `${fmt(100 * v.fractionMasqueeBase)} %`],
            ['Ce qui reste visible',
              enfouie ? 'rien — le sommet est passé sous l’horizon'
                : `${fmt(H - masquee)} m, en partant du sommet`],
            ['Selon la réfraction',
              `de ${fmt(sim.masqueeEnveloppeMinM)} à ${fmt(sim.masqueeEnveloppeMaxM)} m masqués`],
          ]}
        />
        <Carte
          titre="Modèle plat"
          couleur={dash.saffron}
          principal={`${fmt(v.hauteurMasqueePlatM)} m de la base masqués`}
          soustitre="aucune courbure, par construction"
          lignes={[
            ['Part de la cible masquée', '0,0 %'],
            ['Ce qui reste visible', `${fmt(H)} m — la cible entière`],
            ['Selon la réfraction', '0,0 m à toute distance'],
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
            <strong>La réfraction.</strong> {MOTIF_REFRACTION} Ici : {fmt(K_STANDARD, 2)} pour
            le calcul et le verdict, et de {fmt(K_ENVELOPPE_MIN, 2)} à{' '}
            {fmt(K_ENVELOPPE_MAX, 2)} pour la fourchette affichée dans la carte.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>Le seuil du verdict.</strong> {MOTIF_SEUIL} Sur votre cible de{' '}
            {fmt(H)} m, ce seuil de {fmt(100 * SEUIL_DISCRIMINATION_FRACTION, 0)} % vaut{' '}
            {fmt(H * SEUIL_DISCRIMINATION_FRACTION, 2)} m.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>D’où viennent vos deux points.</strong> Observateur :{' '}
            {sim.positionObs.libelle ?? `${fmt(sim.positionObs.latitude, 5)}, ${fmt(sim.positionObs.longitude, 5)}`}{' '}
            ({sim.positionObs.origine}). Cible :{' '}
            {sim.positionCible.libelle ?? `${fmt(sim.positionCible.latitude, 5)}, ${fmt(sim.positionCible.longitude, 5)}`}{' '}
            ({sim.positionCible.origine}).
          </p>

          <p style={{
            margin: '0 0 12px', padding: '12px 14px', borderRadius: 8,
            background: 'var(--bg)', borderLeft: `3px solid ${dash.saffron}`,
          }}>
            <strong>Aucun modèle de terrain.</strong> {MOTIF_SANS_RELIEF}
          </p>

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
