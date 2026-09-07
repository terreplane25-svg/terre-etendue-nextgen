'use client';

/**
 * SimulationRelief.tsx — La coupe du terrain, et les deux modèles côte à côte.
 *
 * CE QUE CE PANNEAU MONTRE, ET CE QU'IL SE REFUSE À MONTRER
 * ────────────────────────────────────────────────────────
 * Il montre : le profil du relief entre le poste et la cible, la ligne de
 * visée que chaque modèle implique, l'obstacle terrestre le plus gênant s'il
 * y en a un, et la comparaison directe des deux prédictions.
 *
 * Il se refuse à : conclure. Un simulateur qui afficherait « le modèle X est
 * réfuté » ferait passer une prédiction pour une observation. Ce qui est
 * affiché, c'est ce que chaque modèle IMPLIQUE ; les confronter à la réalité
 * demande une photographie mesurée selon le protocole.
 *
 * L'EXAGÉRATION VERTICALE EST ÉCRITE, TOUJOURS
 * ────────────────────────────────────────────
 * Sur 35 km de trajet, un relief de 200 m fait 0,6 % de la largeur : à
 * l'échelle, la coupe serait un trait. Toutes les coupes de ce genre sont donc
 * exagérées verticalement, et c'est précisément ce qui permet à un profil de
 * paraître spectaculaire ou anodin selon le facteur choisi. Le facteur est
 * calculé, affiché en clair, et rappelé sous le graphique : sans lui, l'image
 * n'est pas lisible comme une preuve.
 */

import { useCallback, useState } from 'react';
import { dash } from '@/lib/design-tokens';
import {
  type Cible,
  cible as faireCible,
  rayonEffectif,
  vincentyInverse,
} from '@/lib/visee-optique/noyau';
import {
  type AnalyseRelief,
  type ProfilTerrain,
  altitudeLigneDeVisee,
  altitudeLigneDeViseePlane,
  analyserRelief,
  masqueParLeRelief,
} from '@/lib/visee-optique/relief';
import {
  AltimetrieError,
  RESERVE_IGN,
  profilDepuisIgn,
  profilDepuisTexte,
} from '@/lib/visee-optique/altimetrie-ign';

const ACCENT = dash.opal;

export interface EntreesSimulation {
  obsLat: number;
  obsLon: number;
  obsAlt: number;
  cibLat: number;
  cibLon: number;
  cibH: number;
  cibZb: number;
  kMin: number;
  kMax: number;
  rayonEuler: number;
}

interface Simulation {
  D: number;
  azimutDeg: number;
  profil: ProfilTerrain | null;
  reserve: string | null;
  lacunesM: number[];
  /** Le globe aux deux bornes de k, plus la médiane pour le tracé. */
  globeMin: AnalyseRelief;
  globeMed: AnalyseRelief;
  globeMax: AnalyseRelief;
  plan: AnalyseRelief;
  cible: Cible;
  h: number;
  rMed: number;
  kMin: number;
  kMax: number;
}

const fmt = (x: number | null | undefined, n = 1): string =>
  x === null || x === undefined || !Number.isFinite(x)
    ? 'indisponible'
    : x.toLocaleString('fr-FR', { minimumFractionDigits: n, maximumFractionDigits: n });

const fmtKm = (m: number) => `${fmt(m / 1000, 3)} km`;

/**
 * Le verdict d'un modèle, en toutes lettres.
 *
 * Les deux causes ne sont jamais fondues en un seul mot : « masqué » sans dire
 * PAR QUOI est exactement l'ambiguïté que ce simulateur existe pour lever.
 */
function verdict(a: AnalyseRelief, H: number): { texte: string; couleur: string; detail: string } {
  const parLeRelief = masqueParLeRelief(a);
  const fractionCourbure = a.fractionVisibleCourbure;
  const morceaux: string[] = [];

  if (fractionCourbure >= 1) {
    morceaux.push('la courbure n’occulte rien');
  } else if (fractionCourbure <= 0) {
    morceaux.push('la courbure occulte la cible entière');
  } else {
    morceaux.push(
      `la courbure occulte ${fmt(a.hauteurOccultéeCourbureM)} m sur ${fmt(H)} m`,
    );
  }

  if (parLeRelief === null) {
    morceaux.push('le relief n’a pas été évalué');
    return {
      texte: fractionCourbure >= 1 ? 'Rien ne l’occulte — relief non évalué' : 'Partiellement occultée — relief non évalué',
      couleur: dash.saffron,
      detail: morceaux.join(' ; '),
    };
  }
  if (parLeRelief) {
    const o = a.obstacleLePlusGenant!;
    morceaux.push(
      `un obstacle terrestre à ${fmtKm(o.distanceM)} coupe la visée de ${fmt(o.manqueM)} m`,
    );
    return { texte: 'Masquée par le relief', couleur: dash.rose, detail: morceaux.join(' ; ') };
  }
  morceaux.push('aucun obstacle terrestre sur le trajet');
  if (fractionCourbure <= 0) {
    return { texte: 'Entièrement sous l’horizon', couleur: dash.rose, detail: morceaux.join(' ; ') };
  }
  if (fractionCourbure >= 1) {
    return { texte: 'Entièrement visible', couleur: ACCENT, detail: morceaux.join(' ; ') };
  }
  return { texte: 'Partiellement visible', couleur: dash.saffron, detail: morceaux.join(' ; ') };
}

// ── La coupe ────────────────────────────────────────────────────────────────

const L = 860;   // largeur du dessin
const Ht = 340;  // hauteur
const MG = 62;   // marges
// La marge droite loge le repère de la cible ET l'étiquette de la dernière
// graduation, qui déborderait sinon hors du cadre — un axe dont on ne lit pas
// la dernière valeur n'a pas d'échelle.
const MD = 46;
const MH = 22;
const MB = 46;

function Coupe({ s }: { s: Simulation }) {
  const { D, profil, cible, h, rMed } = s;
  const zSommet = cible.zB + cible.H;

  // Les courbes, échantillonnées finement pour que la visée sphérique soit
  // lisse même là où le profil est grossier.
  const N = 240;
  const echantillons = Array.from({ length: N + 1 }, (_, i) => (i * D) / N);
  const viseeGlobe = echantillons.map((d) => [d, altitudeLigneDeVisee(d, D, h, zSommet, rMed)] as const);
  const viseePlane = echantillons.map((d) => [d, altitudeLigneDeViseePlane(d, D, h, zSommet)] as const);

  // La borne basse du dessin descend sous la visée sphérique quand celle-ci
  // plonge sous le niveau zéro : c'est là que se lit l'occultation, et la
  // rogner reviendrait à cacher le phénomène observé.
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
  const echelleH = (L - MG - MD) / D;
  const echelleV = (Ht - MH - MB) / (zMax - zMin);
  const exageration = echelleV / echelleH;

  const chemin = (pts: readonly (readonly [number, number])[]) =>
    pts.map(([d, z], i) => `${i === 0 ? 'M' : 'L'}${x(d).toFixed(2)},${y(z).toFixed(2)}`).join(' ');

  const solPts = profil
    ? profil.points.map((p) => [p.distanceM, p.altitudeM] as const)
    : ([[0, 0], [D, 0]] as const);
  const sol = `${chemin(solPts)} L${x(D).toFixed(2)},${y(zMin).toFixed(2)} L${x(0).toFixed(2)},${y(zMin).toFixed(2)} Z`;

  const pire = s.globeMed.obstacleLePlusGenant;
  const graduations = [0, 0.25, 0.5, 0.75, 1].map((f) => f * D);
  const nivAlt = [zMin, (zMin + zMax) / 2, zMax];

  return (
    <div style={{ overflowX: 'auto' }}>
      <svg viewBox={`0 0 ${L} ${Ht}`} style={{ width: '100%', minWidth: 560, height: 'auto', display: 'block' }}
        role="img"
        aria-label={`Coupe du terrain sur ${fmtKm(D)}, exagération verticale ${Math.round(exageration)} fois`}>
        <rect x={0} y={0} width={L} height={Ht} fill="#0d1117" rx={8} />

        {/* Graduations */}
        {graduations.map((d) => (
          <g key={`g${d}`}>
            <line x1={x(d)} y1={MH} x2={x(d)} y2={Ht - MB} stroke="#1e2733" strokeWidth={1} />
            <text x={x(d)} y={Ht - MB + 16} fill="#6b7d8f" fontSize={10} fontFamily="ui-monospace, monospace" textAnchor="middle">
              {fmt(d / 1000, 1)} km
            </text>
          </g>
        ))}
        {nivAlt.map((z) => (
          <g key={`n${z}`}>
            <line x1={MG} y1={y(z)} x2={L - MD} y2={y(z)} stroke="#1e2733" strokeWidth={1} />
            <text x={MG - 6} y={y(z) + 3} fill="#6b7d8f" fontSize={10} fontFamily="ui-monospace, monospace" textAnchor="end">
              {fmt(z, 0)} m
            </text>
          </g>
        ))}
        {/* Le niveau de référence : la frontière entre « courbure » et « relief ». */}
        {zMin < 0 && zMax > 0 && (
          <line x1={MG} y1={y(0)} x2={L - MD} y2={y(0)} stroke="#3B8FD4" strokeWidth={1} strokeDasharray="2 4" opacity={0.7} />
        )}

        {/* Le terrain */}
        <path d={sol} fill="#243044" stroke="#3d5068" strokeWidth={1.2} />

        {/* Les deux visées */}
        <path d={chemin(viseePlane)} fill="none" stroke={dash.saffron} strokeWidth={1.8} strokeDasharray="7 5" />
        <path d={chemin(viseeGlobe)} fill="none" stroke={ACCENT} strokeWidth={2} />

        {/* La cible : sa base et son sommet */}
        <line x1={x(D)} y1={y(cible.zB)} x2={x(D)} y2={y(zSommet)} stroke="#C8D8E8" strokeWidth={3} />
        <circle cx={x(D)} cy={y(zSommet)} r={3.5} fill="#C8D8E8" />

        {/* Le poste */}
        <circle cx={x(0)} cy={y(h)} r={4} fill={ACCENT} />

        {/* L'obstacle le plus gênant */}
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
        <Legende couleur={ACCENT} texte="Visée — modèle sphérique" />
        <Legende couleur={dash.saffron} texte="Visée — modèle plan" tirets />
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
      <span style={{
        width: 20, height: 0, borderTop: `2px ${tirets ? 'dashed' : 'solid'} ${couleur}`,
      }} />
      {texte}
    </span>
  );
}

// ── Le panneau ──────────────────────────────────────────────────────────────

export default function SimulationRelief({ entrees }: { entrees: EntreesSimulation | null }) {
  const [sim, setSim] = useState<Simulation | null>(null);
  const [enCours, setEnCours] = useState(false);
  const [erreur, setErreur] = useState<string | null>(null);
  const [texteProfil, setTexteProfil] = useState('');
  const [sourceProfil, setSourceProfil] = useState('');
  const [pasM, setPasM] = useState('500');

  const construire = useCallback((
    e: EntreesSimulation,
    profil: ProfilTerrain | null,
    reserve: string | null,
    lacunesM: number[],
  ): Simulation => {
    const geo = vincentyInverse(e.obsLat, e.obsLon, e.cibLat, e.cibLon);
    if (geo.distanceM === 0) throw new Error('Les deux points sont confondus : il n’y a pas de visée.');
    const ci = faireCible(e.cibH, e.cibZb);
    const kMed = (e.kMin + e.kMax) / 2;
    const analyse = (k: number) => analyserRelief(
      geo.distanceM, e.obsAlt, ci, rayonEffectif(e.rayonEuler, k), profil, 'sphérique', 0,
    );
    return {
      D: geo.distanceM,
      azimutDeg: geo.azimutDepartDeg,
      profil, reserve, lacunesM,
      // Les bornes de k, pas une valeur unique : l'enveloppe est la réponse,
      // et un point au milieu serait une réponse plus précise que la donnée.
      globeMin: analyse(e.kMin),
      globeMed: analyse(kMed),
      globeMax: analyse(e.kMax),
      plan: analyserRelief(geo.distanceM, e.obsAlt, ci, null, profil, 'plan', 0),
      cible: ci,
      h: e.obsAlt,
      rMed: rayonEffectif(e.rayonEuler, kMed),
      kMin: e.kMin,
      kMax: e.kMax,
    };
  }, []);

  const simulerAvecIgn = useCallback(async () => {
    if (!entrees) return;
    setEnCours(true);
    setErreur(null);
    try {
      const pas = Number(pasM.replace(',', '.'));
      const r = await profilDepuisIgn(entrees.obsLat, entrees.obsLon, entrees.cibLat, entrees.cibLon, {
        pasM: Number.isFinite(pas) && pas > 0 ? pas : 500,
      });
      setSim(construire(entrees, r.profil, r.reserve, r.lacunesM));
    } catch (err) {
      setErreur(err instanceof AltimetrieError || err instanceof Error ? err.message : String(err));
      setSim(null);
    } finally {
      setEnCours(false);
    }
  }, [entrees, pasM, construire]);

  const simulerAvecTexte = useCallback(() => {
    if (!entrees) return;
    setErreur(null);
    try {
      const p = profilDepuisTexte(texteProfil, sourceProfil.trim());
      setSim(construire(entrees, p, null, []));
    } catch (err) {
      setErreur(err instanceof Error ? err.message : String(err));
      setSim(null);
    }
  }, [entrees, texteProfil, sourceProfil, construire]);

  const simulerSansRelief = useCallback(() => {
    if (!entrees) return;
    setErreur(null);
    try {
      setSim(construire(entrees, null, null, []));
    } catch (err) {
      setErreur(err instanceof Error ? err.message : String(err));
      setSim(null);
    }
  }, [entrees, construire]);

  if (!entrees) {
    return (
      <div style={{
        background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
        padding: '18px 20px',
      }}>
        <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
          La simulation demande les <strong>coordonnées complètes</strong> du poste et de la
          cible, ainsi que la hauteur de la cible et l’intervalle de réfraction. Complétez
          les champs ci-dessus — l’encadré indique ceux qui manquent.
        </p>
      </div>
    );
  }

  return (
    <div>
      <div style={{
        background: dash.opalSoft, border: `1px solid ${ACCENT}40`, borderRadius: 10,
        padding: '16px 20px', marginBottom: 16,
      }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: ACCENT, textTransform: 'uppercase', marginBottom: 8,
        }}>Ce que la simulation transmet</div>
        <p style={{ margin: '0 0 8px', fontSize: 13, lineHeight: 1.6, color: dash.ink }}>
          Les autres outils du Lab ne transmettent rien : votre fichier ne quitte pas votre
          machine. <strong>Celui-ci est différent.</strong> Demander un profil de terrain à
          l’IGN suppose de lui envoyer les coordonnées du poste et de la cible. L’appel n’est
          jamais automatique — il part quand vous cliquez, et pas avant.
        </p>
        <p style={{ margin: 0, fontSize: 13, lineHeight: 1.6, color: dash.ink }}>
          Vous pouvez vous en passer entièrement : saisissez votre propre profil, ou simulez
          sans relief. Un outil qui exigerait le réseau ferait dépendre une démonstration de
          la disponibilité d’un tiers.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', alignItems: 'center', marginBottom: 14 }}>
        <button
          onClick={() => void simulerAvecIgn()}
          disabled={enCours}
          style={{
            padding: '11px 20px', fontSize: 14, fontWeight: 700, minHeight: 44,
            cursor: enCours ? 'wait' : 'pointer', background: ACCENT, color: '#08131b',
            border: 'none', borderRadius: 6,
          }}
        >{enCours ? 'Interrogation de l’IGN…' : 'Simuler — profil IGN'}</button>
        <button
          onClick={simulerSansRelief}
          style={{
            padding: '11px 18px', fontSize: 13.5, minHeight: 44, cursor: 'pointer',
            background: 'var(--card)', color: 'var(--ink)',
            border: '1px solid var(--border)', borderRadius: 6,
          }}
        >Simuler sans relief</button>
        <label style={{ fontSize: 12.5, color: 'var(--ink-muted)', display: 'inline-flex', alignItems: 'center', gap: 6 }}>
          pas d’échantillonnage
          <input
            value={pasM}
            onChange={(ev) => setPasM(ev.target.value)}
            inputMode="decimal"
            style={{
              width: 74, minHeight: 36, padding: '6px 8px', fontSize: 13,
              fontFamily: dash.fontMono, background: 'var(--bg)', color: 'var(--ink)',
              border: '1px solid var(--border)', borderRadius: 4,
            }}
          />
          m
        </label>
      </div>

      <details style={{ marginBottom: 16 }}>
        <summary style={{ cursor: 'pointer', fontSize: 13, color: ACCENT, minHeight: 32, display: 'flex', alignItems: 'center' }}>
          Saisir un profil à la main (sans réseau)
        </summary>
        <div style={{
          marginTop: 10, padding: '14px 16px', background: 'var(--card)',
          border: '1px solid var(--border)', borderRadius: 8,
        }}>
          <p style={{ margin: '0 0 10px', fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
            Une paire <em>distance, altitude</em> par ligne, en mètres. Virgule, point-virgule,
            tabulation ou espace : collez une colonne de tableur telle quelle. Les lignes
            commençant par <code>#</code> sont ignorées.{' '}
            <strong>Un relevé dont vous connaissez la provenance vaut mieux qu’un modèle
            national dont vous ignorez la date</strong> — c’est pourquoi la source est
            demandée ici comme partout ailleurs.
          </p>
          <input
            value={sourceProfil}
            onChange={(ev) => setSourceProfil(ev.target.value)}
            placeholder="Source du profil — d’où viennent ces altitudes ?"
            style={{
              width: '100%', minHeight: 40, padding: '8px 10px', fontSize: 13,
              background: 'var(--bg)', color: 'var(--ink)', marginBottom: 8,
              border: '1px solid var(--border)', borderRadius: 4,
            }}
          />
          <textarea
            value={texteProfil}
            onChange={(ev) => setTexteProfil(ev.target.value)}
            rows={7}
            placeholder={'0 12\n500 8\n1000 15\n…'}
            style={{
              width: '100%', padding: '8px 10px', fontSize: 13, fontFamily: dash.fontMono,
              background: 'var(--bg)', color: 'var(--ink)', resize: 'vertical',
              border: '1px solid var(--border)', borderRadius: 4,
            }}
          />
          <button
            onClick={simulerAvecTexte}
            style={{
              marginTop: 8, padding: '10px 18px', fontSize: 13.5, fontWeight: 600, minHeight: 44,
              cursor: 'pointer', background: 'var(--card)', color: ACCENT,
              border: `1px solid ${ACCENT}`, borderRadius: 6,
            }}
          >Simuler avec ce profil</button>
        </div>
      </details>

      {erreur && (
        <div style={{
          background: 'var(--card)', border: `1px solid ${dash.rose}60`,
          borderLeft: `3px solid ${dash.rose}`, borderRadius: 8,
          padding: '14px 18px', marginBottom: 16,
        }}>
          <p style={{ margin: 0, fontSize: 13.5, lineHeight: 1.6, color: 'var(--ink)' }}>{erreur}</p>
        </div>
      )}

      {sim && <Resultat sim={sim} />}
    </div>
  );
}

function Resultat({ sim }: { sim: Simulation }) {
  const H = sim.cible.H;
  const vGlobeMin = verdict(sim.globeMin, H);
  const vGlobeMax = verdict(sim.globeMax, H);
  const vPlan = verdict(sim.plan, H);
  const parLeRelief = masqueParLeRelief(sim.globeMed);

  return (
    <div>
      <Coupe s={sim} />

      <div style={{ marginTop: 22 }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 10,
        }}>Ce que chaque modèle implique</div>

        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 12 }}>
          <Carte
            titre="Modèle sphérique"
            sousTitre={`réfraction k déclarée de ${fmt(sim.kMin, 2)} à ${fmt(sim.kMax, 2)}`}
            couleur={ACCENT}
            lignes={[
              ['Occultée par la courbure', `de ${fmt(sim.globeMax.hauteurOccultéeCourbureM)} à ${fmt(sim.globeMin.hauteurOccultéeCourbureM)} m`],
              ['Fraction visible', `de ${fmt(100 * sim.globeMin.fractionVisibleCourbure, 1)} % à ${fmt(100 * sim.globeMax.fractionVisibleCourbure, 1)} %`],
              ['Hauteur émergente', `de ${fmt(H * sim.globeMin.fractionVisibleCourbure)} à ${fmt(H * sim.globeMax.fractionVisibleCourbure)} m`],
            ]}
            verdict={vGlobeMin.texte === vGlobeMax.texte ? vGlobeMin : {
              texte: `Entre « ${vGlobeMin.texte.toLowerCase()} » et « ${vGlobeMax.texte.toLowerCase()} »`,
              couleur: dash.saffron,
              detail: 'Les deux bornes de l’intervalle de réfraction ne donnent pas le même verdict : sur cette visée, k décide.',
            }}
          />
          <Carte
            titre="Modèle plan"
            sousTitre="aucune courbure, par construction"
            couleur={dash.saffron}
            lignes={[
              ['Occultée par la courbure', '0,0 m — par construction'],
              ['Fraction visible', '100,0 %'],
              ['Hauteur émergente', `${fmt(H)} m`],
            ]}
            verdict={vPlan}
          />
        </div>
      </div>

      <div style={{
        marginTop: 16, background: 'var(--card)', border: '1px solid var(--border)',
        borderRadius: 10, padding: '16px 20px',
      }}>
        <div style={{
          fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700, letterSpacing: '0.12em',
          color: 'var(--ink-muted)', textTransform: 'uppercase', marginBottom: 10,
        }}>Le relief, séparément</div>
        <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 13 }}>
          <tbody>
            <Ligne cle="Distance géodésique" val={`${fmtKm(sim.D)} — Vincenty sur l’ellipsoïde WGS-84`} />
            <Ligne cle="Azimut de départ" val={`${fmt(sim.azimutDeg, 3)}°`} />
            <Ligne cle="Profil de terrain" val={sim.profil ? `${sim.profil.points.length} points — ${sim.profil.source}` : 'non évalué — aucun profil fourni'} />
            {sim.profil?.pasM != null && <Ligne cle="Pas d’échantillonnage" val={`${fmt(sim.profil.pasM)} m`} />}
            {sim.lacunesM.length > 0 && (
              <Ligne cle="Points sans donnée" val={`${sim.lacunesM.length} — non comblés, jamais remplacés par zéro`} />
            )}
            {parLeRelief === null ? (
              <Ligne cle="Obstacle le plus gênant" val="non évalué — ce n’est pas « aucun obstacle »" />
            ) : parLeRelief ? (
              <>
                <Ligne cle="Obstacle le plus gênant"
                  val={`à ${fmtKm(sim.globeMed.obstacleLePlusGenant!.distanceM)}, altitude ${fmt(sim.globeMed.obstacleLePlusGenant!.altitudeTerrainM)} m`} />
                <Ligne cle="Il coupe la visée de"
                  val={`${fmt(sim.globeMed.obstacleLePlusGenant!.manqueM)} m`} />
                <Ligne cle="Obstacles au total" val={`${sim.globeMed.obstacles.length}`} />
              </>
            ) : (
              <>
                <Ligne cle="Obstacle terrestre" val="aucun sur le trajet" />
                <Ligne cle="Marge minimale de la visée"
                  val={`${fmt(sim.globeMed.margeMinimaleM)} m, à ${fmtKm(sim.globeMed.distanceMargeMinimaleM ?? 0)}`} />
              </>
            )}
          </tbody>
        </table>
        <p style={{ margin: '12px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
          Le relief masque <strong>identiquement dans les deux modèles</strong> : c’est ce qui
          en fait un discriminant utilisable. Ce que les deux modèles prédisent différemment,
          c’est la courbure seule — et c’est la seule chose qu’une observation puisse
          départager.
        </p>
      </div>

      {sim.reserve && (
        <p style={{
          margin: '14px 0 0', fontSize: 12, lineHeight: 1.6, color: 'var(--ink-muted)',
          padding: '12px 14px', background: 'var(--bg)', border: '1px solid var(--border)',
          borderRadius: 8,
        }}>
          {sim.reserve}{' '}
          <strong>Réserve supplémentaire :</strong> cette liaison avec le service de l’IGN
          n’a jamais pu être exécutée contre le service réel depuis l’environnement où elle a
          été écrite. Le contrat publié est respecté et les réponses non conformes sont
          refusées plutôt que comblées, mais la confrontation au service reste à faire.
        </p>
      )}

      <p style={{ margin: '14px 0 0', fontSize: 12.5, lineHeight: 1.6, color: 'var(--ink-muted)' }}>
        <strong>Ce que cette simulation n’établit pas.</strong> Rien sur ce qui est réellement
        visible depuis ce poste. Elle dit ce que chaque modèle <em>implique</em>, sur les
        données que vous avez saisies. Les confronter demande une photographie mesurée selon
        le protocole, avec ses contrôles d’intégrité, ses trois analystes en aveugle et son
        seuil déposé d’avance. La réfraction est supposée homogène le long du trajet, ce
        qu’elle n’est pas au voisinage d’un sol chaud ou d’une mer froide.
      </p>
    </div>
  );
}

function Carte({ titre, sousTitre, couleur, lignes, verdict: v }: {
  titre: string; sousTitre: string; couleur: string;
  lignes: [string, string][];
  verdict: { texte: string; couleur: string; detail: string };
}) {
  return (
    <div style={{
      background: 'var(--card)', border: '1px solid var(--border)',
      borderTop: `3px solid ${couleur}`, borderRadius: 10, padding: '14px 16px',
    }}>
      <div style={{ fontSize: 14.5, fontWeight: 700, color: 'var(--ink)' }}>{titre}</div>
      <div style={{ fontSize: 11.5, color: 'var(--ink-muted)', marginBottom: 10 }}>{sousTitre}</div>
      <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12.5 }}>
        <tbody>
          {lignes.map(([k, val]) => <Ligne key={k} cle={k} val={val} />)}
        </tbody>
      </table>
      <div style={{
        marginTop: 10, padding: '8px 10px', borderRadius: 6,
        background: 'var(--bg)', borderLeft: `3px solid ${v.couleur}`,
      }}>
        <div style={{ fontSize: 13, fontWeight: 700, color: v.couleur }}>{v.texte}</div>
        <div style={{ fontSize: 11.5, lineHeight: 1.55, color: 'var(--ink-muted)', marginTop: 3 }}>{v.detail}</div>
      </div>
    </div>
  );
}

function Ligne({ cle, val }: { cle: string; val: string }) {
  return (
    <tr>
      <td style={{
        padding: '5px 10px 5px 0', color: 'var(--ink-muted)', verticalAlign: 'top',
        borderBottom: '1px solid var(--border)', width: '48%',
      }}>{cle}</td>
      <td style={{
        padding: '5px 0', color: 'var(--ink)', fontFamily: dash.fontMono, fontSize: 12.5,
        borderBottom: '1px solid var(--border)',
      }}>{val}</td>
    </tr>
  );
}
