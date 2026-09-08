'use client';

/**
 * SimulationRelief.tsx — Le résultat du Simulateur de Visée.
 *
 * CE QUE CE PANNEAU MONTRE, ET CE QU'IL SE REFUSE À MONTRER
 * ────────────────────────────────────────────────────────
 * Il montre : un verdict sur la capacité de la visée à départager les deux
 * modèles, ce que chacun prédit, la coupe du terrain, et l'obstacle le plus
 * gênant s'il y en a un.
 *
 * Il se refuse à : conclure sur la forme de la Terre. Ce qui est affiché, c'est
 * ce que chaque modèle IMPLIQUE ; les confronter à la réalité demande une
 * photographie. Un simulateur qui afficherait « le modèle X est réfuté » ferait
 * passer une prédiction pour une observation.
 *
 * L'EXAGÉRATION VERTICALE EST ÉCRITE, TOUJOURS
 * ────────────────────────────────────────────
 * Sur 35 km de trajet, un relief de 200 m fait 0,6 % de la largeur : à
 * l'échelle, la coupe serait un trait. Toutes les coupes de ce genre sont donc
 * exagérées verticalement, et c'est précisément ce qui permet à un profil de
 * paraître spectaculaire ou anodin selon le facteur choisi. Le facteur est
 * calculé, affiché en clair sur le dessin, et rappelé sous lui.
 */

import { dash } from '@/lib/design-tokens';
import { type Cible } from '@/lib/visee-optique/noyau';
import {
  type AnalyseRelief,
  type ProfilTerrain,
  altitudeLigneDeVisee,
  altitudeLigneDeViseePlane,
  masqueParLeRelief,
} from '@/lib/visee-optique/relief';
import { RESERVE_GEOCODAGE, type Position } from '@/lib/visee-optique/geocodage-ign';
import {
  K_ENVELOPPE_MAX,
  K_ENVELOPPE_MIN,
  K_STANDARD,
  MOTIF_REFRACTION,
  MOTIF_RESERVE_RELIEF,
  MOTIF_SEUIL,
  SEUIL_DISCRIMINATION_FRACTION,
  type Verdict,
} from '@/lib/visee-optique/simulation';

const ACCENT = dash.opal;

export interface Simulation {
  D: number;
  azimutDeg: number;
  /** Le pas d'échantillonnage demandé, choisi d'après la distance. */
  pasDemandeM: number;
  positionObs: Position;
  positionCible: Position;
  profil: ProfilTerrain | null;
  /** Pourquoi le profil manque, le cas échéant. Jamais « aucun obstacle ». */
  motifProfil: string | null;
  reserveIgn: string | null;
  lacunesM: number[];
  /** Le modèle sphérique aux deux bornes de l'enveloppe de réfraction. */
  globeMin: AnalyseRelief;
  globeMax: AnalyseRelief;
  plan: AnalyseRelief;
  verdict: Verdict;
  cible: Cible;
  h: number;
  /** Le rayon employé pour le TRACÉ, au milieu de l'enveloppe. */
  rTrace: number;
}

const fmt = (x: number | null | undefined, n = 1): string =>
  x === null || x === undefined || !Number.isFinite(x)
    ? 'indisponible'
    : x.toLocaleString('fr-FR', { minimumFractionDigits: n, maximumFractionDigits: n });

const fmtKm = (m: number) => `${fmt(m / 1000, 2)} km`;

// ── La coupe ────────────────────────────────────────────────────────────────

const L = 860;
const Ht = 320;
const MG = 62;
// La marge droite loge le repère de la cible ET l'étiquette de la dernière
// graduation, qui déborderait sinon hors du cadre — un axe dont on ne lit pas
// la dernière valeur n'a pas d'échelle.
const MD = 46;
const MH = 22;
const MB = 42;

function Coupe({ s }: { s: Simulation }) {
  const { D, profil, cible, h, rTrace } = s;
  const zSommet = cible.zB + cible.H;

  // Échantillonnage fin : la visée sphérique doit rester lisse même là où le
  // profil du terrain est grossier.
  const N = 240;
  const echantillons = Array.from({ length: N + 1 }, (_, i) => (i * D) / N);
  const viseeGlobe = echantillons.map((d) => [d, altitudeLigneDeVisee(d, D, h, zSommet, rTrace)] as const);
  const viseePlane = echantillons.map((d) => [d, altitudeLigneDeViseePlane(d, D, h, zSommet)] as const);

  // La borne basse descend sous la visée sphérique quand celle-ci plonge sous
  // le niveau zéro : c'est là que se lit l'occultation, et la rogner
  // reviendrait à cacher le phénomène observé.
  const altitudes = [
    ...(profil ? profil.points.map((p) => p.altitudeM) : [0]),
    ...viseeGlobe.map(([, z]) => z),
    ...viseePlane.map(([, z]) => z),
    0, h, cible.zB, zSommet,
  ];
  let zMin = Math.min(...altitudes);
  let zMax = Math.max(...altitudes);
  const marge = Math.max(5, (zMax - zMin) * 0.08);
  zMin -= marge;
  zMax += marge;

  const x = (d: number) => MG + (d / D) * (L - MG - MD);
  const y = (z: number) => MH + (1 - (z - zMin) / (zMax - zMin)) * (Ht - MH - MB);

  // L'exagération verticale : combien de fois l'échelle des altitudes dépasse
  // celle des distances. C'est LE chiffre sans lequel une coupe ne se lit pas.
  const exageration = ((Ht - MH - MB) / (zMax - zMin)) / ((L - MG - MD) / D);

  const chemin = (pts: readonly (readonly [number, number])[]) =>
    pts.map(([d, z], i) => `${i === 0 ? 'M' : 'L'}${x(d).toFixed(2)},${y(z).toFixed(2)}`).join(' ');

  const solPts = profil
    ? profil.points.map((p) => [p.distanceM, p.altitudeM] as const)
    : ([[0, 0], [D, 0]] as const);
  const sol = `${chemin(solPts)} L${x(D).toFixed(2)},${y(zMin).toFixed(2)} L${x(0).toFixed(2)},${y(zMin).toFixed(2)} Z`;

  const pire = s.globeMin.obstacleLePlusGenant;
  const graduations = [0, 0.25, 0.5, 0.75, 1].map((f) => f * D);

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${L} ${Ht}`} style={{ width: '100%', minWidth: 540, height: 'auto', display: 'block' }}
        role="img"
        aria-label={`Coupe du terrain sur ${fmtKm(D)}, exagération verticale ${Math.round(exageration)} fois`}>
        <rect x={0} y={0} width={L} height={Ht} fill="#0d1117" rx={8} />

        {graduations.map((d) => (
          <g key={`g${d}`}>
            <line x1={x(d)} y1={MH} x2={x(d)} y2={Ht - MB} stroke="#1e2733" strokeWidth={1} />
            <text x={x(d)} y={Ht - MB + 16} fill="#6b7d8f" fontSize={10} fontFamily="ui-monospace, monospace" textAnchor="middle">
              {fmt(d / 1000, 1)} km
            </text>
          </g>
        ))}
        {[zMin, (zMin + zMax) / 2, zMax].map((z) => (
          <g key={`n${z}`}>
            <line x1={MG} y1={y(z)} x2={L - MD} y2={y(z)} stroke="#1e2733" strokeWidth={1} />
            <text x={MG - 6} y={y(z) + 3} fill="#6b7d8f" fontSize={10} fontFamily="ui-monospace, monospace" textAnchor="end">
              {fmt(z, 0)} m
            </text>
          </g>
        ))}
        {/* Le niveau de la mer : la frontière entre « courbure » et « relief ». */}
        {zMin < 0 && zMax > 0 && (
          <line x1={MG} y1={y(0)} x2={L - MD} y2={y(0)} stroke="#3B8FD4" strokeWidth={1} strokeDasharray="2 4" opacity={0.7} />
        )}

        <path d={sol} fill="#243044" stroke="#3d5068" strokeWidth={1.2} />
        <path d={chemin(viseePlane)} fill="none" stroke={dash.saffron} strokeWidth={1.8} strokeDasharray="7 5" />
        <path d={chemin(viseeGlobe)} fill="none" stroke={ACCENT} strokeWidth={2} />

        {/* La cible : sa base et son sommet */}
        <line x1={x(D)} y1={y(cible.zB)} x2={x(D)} y2={y(zSommet)} stroke="#C8D8E8" strokeWidth={3} />
        <circle cx={x(D)} cy={y(zSommet)} r={3.5} fill="#C8D8E8" />
        <circle cx={x(0)} cy={y(h)} r={4} fill={ACCENT} />

        {pire && (
          <g>
            <line x1={x(pire.distanceM)} y1={y(pire.altitudeTerrainM)} x2={x(pire.distanceM)} y2={y(pire.altitudeViseeM)}
              stroke={dash.rose} strokeWidth={2.5} />
            <circle cx={x(pire.distanceM)} cy={y(pire.altitudeTerrainM)} r={4} fill={dash.rose} />
            <text x={x(pire.distanceM)} y={Math.max(MH + 10, y(pire.altitudeTerrainM) - 10)}
              fill={dash.rose} fontSize={11} fontFamily="ui-monospace, monospace" textAnchor="middle">
              +{fmt(pire.manqueM)} m
            </text>
          </g>
        )}

        {/* L'exagération, dans le dessin lui-même : découpée du graphique, elle
            se perdrait, et la coupe deviendrait trompeuse. */}
        <text x={L - MD} y={MH - 8} fill="#8a9bad" fontSize={10.5} fontFamily="ui-monospace, monospace" textAnchor="end">
          exagération verticale × {Math.round(exageration).toLocaleString('fr-FR')}
        </text>
      </svg>

      <div style={{ display: 'flex', gap: 18, flexWrap: 'wrap', marginTop: 10, fontSize: 12 }}>
        <Legende couleur={ACCENT} texte="Ce que voit le modèle sphérique" />
        <Legende couleur={dash.saffron} texte="Ce que voit le modèle plat" tirets />
        <Legende couleur="#3d5068" texte="Terrain" />
        {pire && <Legende couleur={dash.rose} texte="Obstacle le plus gênant" />}
      </div>
      <p style={{ margin: '10px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
        Les altitudes sont <strong>exagérées {Math.round(exageration).toLocaleString('fr-FR')} fois</strong> par
        rapport aux distances. Sans cela la coupe serait un trait : sur {fmtKm(D)}, un relief
        de 200 m fait moins de 1 % de la largeur. Ce facteur est ce qui rend un même profil
        spectaculaire ou anodin — il est donc écrit, ici et sur le dessin.
      </p>
    </div>
  );
}

function Legende({ couleur, texte, tirets }: { couleur: string; texte: string; tirets?: boolean }) {
  return (
    <span style={{ display: 'inline-flex', alignItems: 'center', gap: 6, color: 'var(--ink-muted)' }}>
      <span style={{ width: 20, height: 0, borderTop: `2px ${tirets ? 'dashed' : 'solid'} ${couleur}` }} />
      {texte}
    </span>
  );
}

// ── Le panneau ──────────────────────────────────────────────────────────────

export default function ResultatSimulation({ sim }: { sim: Simulation }) {
  const H = sim.cible.H;
  const v = sim.verdict;
  const parLeRelief = masqueParLeRelief(sim.globeMin);

  // Ce qui est mis en avant, c'est la hauteur masquée EN PARTANT DE LA BASE :
  // c'est le pied de la cible qui disparaît en premier, et c'est là que les
  // deux modèles divergent en premier. La part visible du sommet reste à
  // 100 % longtemps après que la divergence est devenue mesurable.
  const basMin = v.hauteurMasqueeBaseMinM;
  const basMax = v.hauteurMasqueeBaseMaxM;
  const memeValeur = Math.abs(basMax - basMin) < 0.05;
  // Au-delà de la distance limite, la cible est enfouie sous l'horizon : la
  // hauteur masquée dépasse alors sa hauteur totale, et le dire vaut mieux que
  // d'afficher « 100 % masqué » qui perdrait de combien.
  const enfouie = basMin > H;

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
        {v.reserveRelief && (
          <p style={{ margin: '10px 0 0', fontSize: 12.5, lineHeight: 1.6, color: dash.inkSoft }}>
            {MOTIF_RESERVE_RELIEF}
          </p>
        )}
      </div>

      {/* ── Les deux prédictions ── */}
      <div style={{
        display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
        gap: 14, marginBottom: 18,
      }}>
        <Carte
          titre="Modèle sphérique"
          couleur={ACCENT}
          principal={memeValeur
            ? `${fmt(basMin)} m de la base occultés`
            : `${fmt(basMin)} à ${fmt(basMax)} m de la base occultés`}
          soustitre={enfouie
            ? `sur une cible de ${fmt(H)} m — elle est entièrement sous l’horizon`
            : `sur ${fmt(H)} m de hauteur totale`}
          lignes={[
            // Quand la cible est enfouie, un pourcentage de plusieurs milliers
            // est exact et illisible. Ce qui parle alors, c'est de combien le
            // SOMMET est passé sous l'horizon — une longueur, pas un ratio.
            [enfouie ? 'Sommet sous l’horizon' : 'Part de la cible masquée',
              enfouie
                ? `de ${fmtKm(basMin - H)} à ${fmtKm(basMax - H)} en dessous`
                : memeValeur
                  ? `${fmt(100 * v.fractionMasqueeBaseMin)} %`
                  : `${fmt(100 * v.fractionMasqueeBaseMin)} % à ${fmt(100 * v.fractionMasqueeBaseMax)} %`],
            ['Ce qui reste visible',
              enfouie ? 'rien — le sommet est passé sous l’horizon'
                : `${fmt(Math.max(0, H - basMax))} à ${fmt(Math.max(0, H - basMin))} m, en partant du sommet`],
            ['Relief intermédiaire',
              parLeRelief === null
                ? 'non évalué — ce n’est pas « aucun obstacle »'
                : parLeRelief
                  ? `bloque à ${fmtKm(sim.globeMin.obstacleLePlusGenant!.distanceM)}`
                  : 'dégagé, aucun obstacle sur le trajet'],
          ]}
        />
        <Carte
          titre="Modèle plat"
          couleur={dash.saffron}
          principal="0,0 m de la base occultés"
          soustitre="aucune courbure, par construction"
          lignes={[
            ['Part de la cible masquée', '0,0 %'],
            ['Ce qui reste visible', `${fmt(H)} m — la cible entière`],
            ['Relief intermédiaire',
              parLeRelief === null
                ? 'non évalué — ce n’est pas « aucun obstacle »'
                : parLeRelief
                  ? `bloque à ${fmtKm(sim.plan.obstacleLePlusGenant?.distanceM ?? 0)}`
                  : 'dégagé, aucun obstacle sur le trajet'],
          ]}
        />
      </div>

      {/* ── La coupe ── */}
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '16px 18px', marginBottom: 18,
      }}>
        <div style={{
          fontSize: 11, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.1em',
          color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 12,
        }}>Coupe du terrain — {fmtKm(sim.D)}</div>
        <Coupe s={sim} />
      </div>

      {/* ── Le profil de terrain, quand il manque ── */}
      {sim.motifProfil && (
        <div style={{
          background: 'var(--card)', border: '1px solid var(--border)',
          borderLeft: `3px solid ${dash.saffron}`, borderRadius: 8,
          padding: '14px 18px', marginBottom: 18,
        }}>
          <p style={{ margin: '0 0 6px', fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>
            <strong>Le relief n’a pas pu être évalué.</strong> La simulation a tourné sur
            les coordonnées et hauteurs que vous avez saisies, en prenant le niveau de la
            mer comme surface. Ce n’est pas « aucun obstacle » : c’est « on ne sait pas ».
          </p>
          <p style={{ margin: 0, fontSize: 12, lineHeight: 1.55, color: 'var(--ink-muted)' }}>
            {sim.motifProfil}
          </p>
        </div>
      )}

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
            ce qui se voit sur une visée longue.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>La réfraction.</strong> {MOTIF_REFRACTION} Ici : de{' '}
            {fmt(K_ENVELOPPE_MIN, 2)} à {fmt(K_ENVELOPPE_MAX, 2)}, valeur moyenne{' '}
            {fmt(K_STANDARD, 2)} — c’est pourquoi les résultats ci-dessus sont donnés
            comme des fourchettes.
          </p>

          <p style={{ margin: '0 0 12px' }}>
            <strong>Le relief.</strong>{' '}
            {sim.profil
              ? <>Le profil du terrain entre les deux points vient du modèle altimétrique
                de l’IGN : {sim.profil.points.length} points relevés tous les{' '}
                {fmt(sim.profil.pasM ?? sim.pasDemandeM, 0)} m environ. Ce pas est choisi
                d’après la distance — 250 m sous 100 km, 500 m jusqu’à 500 km, 2 km au-delà —
                pour qu’une visée de n’importe quelle longueur reste interrogeable.
                Contrepartie : à ce pas, une colline plus étroite que{' '}
                {fmt(sim.pasDemandeM, 0)} m peut passer entre deux points de mesure.
                {sim.lacunesM.length > 0 && (
                  <> {sim.lacunesM.length} point{sim.lacunesM.length > 1 ? 's sont' : ' est'}{' '}
                  hors couverture : {sim.lacunesM.length > 1 ? 'ils sont laissés' : 'il est laissé'}{' '}
                  en lacune, jamais remplacé{sim.lacunesM.length > 1 ? 's' : ''} par zéro.</>
                )}</>
              : <>Le profil du terrain n’a pas pu être obtenu : le calcul a pris le niveau
                de la mer comme surface. Un profil manquant ne vaut pas « aucun
                obstacle ».</>}
            {' '}Point important : <strong>le relief masque identiquement dans les deux
            modèles</strong>. Ce que les deux prédisent différemment, c’est la courbure
            seule — et c’est la seule chose qu’une photographie puisse départager.
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
            background: 'var(--bg)', borderLeft: `3px solid ${dash.rose}`,
          }}>
            <strong>Ce que cette simulation n’établit pas.</strong> Rien sur ce qui est
            réellement visible depuis ce point. Elle dit ce que chaque modèle{' '}
            <em>implique</em>, sur les données que vous avez saisies — et vos hauteurs
            valent ce que vaut leur source. La réfraction est supposée homogène le long du
            trajet, ce qu’elle n’est pas au voisinage d’un sol chaud ou d’une mer froide.
            Confronter ces prédictions au réel demande une photographie mesurée.
          </p>

          {(sim.reserveIgn || sim.positionObs.origine.includes('IGN')
            || sim.positionCible.origine.includes('IGN')) && (
            <p style={{ margin: 0, fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
              <strong>Réserve sur les services interrogés.</strong>{' '}
              {sim.reserveIgn ? `${sim.reserveIgn} ` : ''}
              Ces liaisons avec les services de l’IGN n’ont jamais pu être exécutées contre
              les services réels depuis l’environnement où elles ont été écrites. Le contrat
              publié est respecté et les réponses non conformes sont refusées plutôt que
              comblées, mais la confrontation reste à faire. {RESERVE_GEOCODAGE}
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
