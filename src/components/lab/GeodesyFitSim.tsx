'use client';
import { useState, useMemo, useCallback } from 'react';

/* ═══════════════════════════════════════════════════════════════
   CARTOGRAPHIE PAR MULTILATÉRATION
   Reconstruit la position des villes à partir des SEULES durées de
   trajet mesurées (vols sans escale, traversées maritimes).
   Aucune carte, aucune coordonnée géographique n'est utilisée en entrée.
   ═══════════════════════════════════════════════════════════════ */

const OPAL = '#3D9E7C';
const CYAN = '#3B8FD4';
const ROSE = '#C45E6A';
const GOLD = '#D4943A';
const MONO = "'JetBrains Mono', monospace";

interface Leg { a: string; b: string; h: number; mode: 'air' | 'mer'; src: string; }

/** Jeu de données par défaut — durées sans escale, moyenne aller/retour.
 *  Chaque valeur est modifiable par l'utilisateur. */
const DEFAULT_LEGS: Leg[] = [
  { a: 'SYD', b: 'AKL', h: 3.3, mode: 'air', src: 'Horaires Qantas / Air NZ' },
  { a: 'SYD', b: 'LAX', h: 14.1, mode: 'air', src: 'Horaires Qantas / United' },
  { a: 'SYD', b: 'JNB', h: 12.8, mode: 'air', src: 'Horaires Qantas QF63/64' },
  { a: 'SYD', b: 'SCL', h: 12.9, mode: 'air', src: 'Horaires LATAM' },
  { a: 'SYD', b: 'SIN', h: 8.0, mode: 'air', src: 'Horaires Singapore Airlines' },
  { a: 'SYD', b: 'HKG', h: 9.0, mode: 'air', src: 'Horaires Cathay Pacific' },
  { a: 'SYD', b: 'DXB', h: 14.5, mode: 'air', src: 'Horaires Emirates' },
  { a: 'SYD', b: 'PER', h: 5.0, mode: 'air', src: 'Horaires Qantas' },
  { a: 'AKL', b: 'LAX', h: 12.3, mode: 'air', src: 'Horaires Air NZ' },
  { a: 'AKL', b: 'EZE', h: 11.9, mode: 'air', src: 'Horaires Air NZ' },
  { a: 'AKL', b: 'SIN', h: 10.3, mode: 'air', src: 'Horaires Singapore Airlines' },
  { a: 'SCL', b: 'EZE', h: 2.2, mode: 'air', src: 'Horaires LATAM' },
  { a: 'SCL', b: 'LAX', h: 10.5, mode: 'air', src: 'Horaires LATAM' },
  { a: 'SCL', b: 'JFK', h: 10.7, mode: 'air', src: 'Horaires LATAM / Delta' },
  { a: 'JNB', b: 'PER', h: 9.3, mode: 'air', src: 'Horaires Qantas' },
  { a: 'JNB', b: 'LHR', h: 11.0, mode: 'air', src: 'Horaires BA / Virgin' },
  { a: 'JNB', b: 'DXB', h: 8.2, mode: 'air', src: 'Horaires Emirates' },
  { a: 'JNB', b: 'JFK', h: 15.5, mode: 'air', src: 'Horaires South African / United' },
  { a: 'JNB', b: 'EZE', h: 8.5, mode: 'air', src: 'Horaires South African' },
  { a: 'PER', b: 'LHR', h: 17.3, mode: 'air', src: 'Horaires Qantas QF9/10' },
  { a: 'PER', b: 'SIN', h: 5.2, mode: 'air', src: 'Horaires Singapore Airlines' },
  { a: 'LAX', b: 'JFK', h: 5.3, mode: 'air', src: 'Horaires American / Delta' },
  { a: 'LAX', b: 'LHR', h: 10.5, mode: 'air', src: 'Horaires BA / United' },
  { a: 'LAX', b: 'HKG', h: 13.9, mode: 'air', src: 'Horaires Cathay Pacific' },
  { a: 'LAX', b: 'NRT', h: 11.6, mode: 'air', src: 'Horaires JAL / ANA' },
  { a: 'JFK', b: 'LHR', h: 7.0, mode: 'air', src: 'Horaires BA / American' },
  { a: 'JFK', b: 'NRT', h: 13.5, mode: 'air', src: 'Horaires JAL / ANA' },
  { a: 'JFK', b: 'DXB', h: 13.3, mode: 'air', src: 'Horaires Emirates' },
  { a: 'LHR', b: 'DXB', h: 7.0, mode: 'air', src: 'Horaires Emirates / BA' },
  { a: 'LHR', b: 'SIN', h: 13.3, mode: 'air', src: 'Horaires Singapore Airlines' },
  { a: 'LHR', b: 'NRT', h: 12.5, mode: 'air', src: 'Horaires BA / JAL' },
  { a: 'DXB', b: 'SIN', h: 7.4, mode: 'air', src: 'Horaires Emirates' },
  { a: 'DXB', b: 'HKG', h: 7.8, mode: 'air', src: 'Horaires Emirates' },
  { a: 'SIN', b: 'HKG', h: 3.9, mode: 'air', src: 'Horaires Cathay Pacific' },
  { a: 'HKG', b: 'NRT', h: 4.0, mode: 'air', src: 'Horaires Cathay / ANA' },
];

// ── Optimisation ────────────────────────────────────────────────
/** Effort de calcul IDENTIQUE pour les deux modèles (équité de traitement). */
const RESTARTS = 24;
const STEPS = 12000;

function buildIndex(legs: Leg[]) {
  const set = new Set<string>();
  legs.forEach(l => { set.add(l.a); set.add(l.b); });
  const cities = Array.from(set).sort();
  const idx = new Map(cities.map((c, i) => [c, i]));
  return { cities, idx };
}

function mulberry(seed: number) {
  let t = seed >>> 0;
  return () => {
    t += 0x6D2B79F5;
    let r = Math.imul(t ^ (t >>> 15), 1 | t);
    r ^= r + Math.imul(r ^ (r >>> 7), 61 | r);
    return ((r ^ (r >>> 14)) >>> 0) / 4294967296;
  };
}

/** Ajustement sur un PLAN : positions 2D libres, aucune contrainte de forme. */
function fitFlat(legs: Leg[], n: number, I: number[], J: number[], T: number[]) {
  let best: { rms: number; P: number[][] } | null = null;
  for (let trial = 0; trial < RESTARTS; trial++) {
    const rnd = mulberry(1000 + trial * 77);
    const P: number[][] = Array.from({ length: n }, () => [(rnd() - 0.5) * 20, (rnd() - 0.5) * 20]);
    for (let s = 0; s < STEPS; s++) {
      const g: number[][] = Array.from({ length: n }, () => [0, 0]);
      for (let k = 0; k < T.length; k++) {
        const i = I[k], j = J[k];
        const dx = P[i][0] - P[j][0], dy = P[i][1] - P[j][1];
        const L = Math.hypot(dx, dy) + 1e-9;
        const c = 2 * (L - T[k]) / L;
        g[i][0] += c * dx; g[i][1] += c * dy;
        g[j][0] -= c * dx; g[j][1] -= c * dy;
      }
      const lr = 0.05 / T.length;
      for (let i = 0; i < n; i++) { P[i][0] -= lr * g[i][0]; P[i][1] -= lr * g[i][1]; }
    }
    let se = 0;
    for (let k = 0; k < T.length; k++) {
      const L = Math.hypot(P[I[k]][0] - P[J[k]][0], P[I[k]][1] - P[J[k]][1]);
      se += (L - T[k]) ** 2;
    }
    const rms = Math.sqrt(se / T.length);
    if (!best || rms < best.rms) best = { rms, P };
  }
  return best!;
}

/** Ajustement sur une SPHÈRE : positions libres, rayon libre. */
function fitSphere(legs: Leg[], n: number, I: number[], J: number[], T: number[]) {
  let best: { rms: number; V: number[][]; R: number } | null = null;
  for (let trial = 0; trial < RESTARTS; trial++) {
    const rnd = mulberry(2000 + trial * 131);
    const V: number[][] = Array.from({ length: n }, () => {
      const v = [rnd() - 0.5, rnd() - 0.5, rnd() - 0.5];
      const m = Math.hypot(v[0], v[1], v[2]);
      return [v[0] / m, v[1] / m, v[2] / m];
    });
    let R = 6;
    for (let s = 0; s < STEPS; s++) {
      const g: number[][] = Array.from({ length: n }, () => [0, 0, 0]);
      let gR = 0;
      for (let k = 0; k < T.length; k++) {
        const i = I[k], j = J[k];
        let dot = V[i][0] * V[j][0] + V[i][1] * V[j][1] + V[i][2] * V[j][2];
        dot = Math.max(-0.999999, Math.min(0.999999, dot));
        const ang = Math.acos(dot);
        const res = R * ang - T[k];
        const c = -2 * res * R / Math.sqrt(1 - dot * dot);
        for (let d = 0; d < 3; d++) { g[i][d] += c * V[j][d]; g[j][d] += c * V[i][d]; }
        gR += 2 * res * ang;
      }
      const lr = 0.05 / T.length;
      for (let i = 0; i < n; i++) {
        for (let d = 0; d < 3; d++) V[i][d] -= lr * g[i][d];
        const m = Math.hypot(V[i][0], V[i][1], V[i][2]) || 1;
        for (let d = 0; d < 3; d++) V[i][d] /= m;
      }
      R -= lr * gR * 0.5;
      if (R < 0.5) R = 0.5;
    }
    let se = 0;
    for (let k = 0; k < T.length; k++) {
      let dot = V[I[k]][0] * V[J[k]][0] + V[I[k]][1] * V[J[k]][1] + V[I[k]][2] * V[J[k]][2];
      dot = Math.max(-1, Math.min(1, dot));
      se += (R * Math.acos(dot) - T[k]) ** 2;
    }
    const rms = Math.sqrt(se / T.length);
    if (!best || rms < best.rms) best = { rms, V, R };
  }
  return best!;
}

// ── Composant ───────────────────────────────────────────────────
export default function GeodesyFitSim() {
  const [legs, setLegs] = useState<Leg[]>(DEFAULT_LEGS);
  const [speed, setSpeed] = useState(850);
  const [anchor, setAnchor] = useState('LHR');
  const [ran, setRan] = useState(false);
  const [busy, setBusy] = useState(false);
  const [result, setResult] = useState<null | {
    cities: string[]; flatRms: number; sphRms: number; circHours: number;
    P: number[][]; resid: { a: string; b: string; t: number; flat: number; sph: number }[];
  }>(null);

  const run = useCallback(() => {
    setBusy(true);
    setTimeout(() => {
      const { cities, idx } = buildIndex(legs);
      const n = cities.length;
      const I = legs.map(l => idx.get(l.a)!);
      const J = legs.map(l => idx.get(l.b)!);
      const T = legs.map(l => l.h);
      const flat = fitFlat(legs, n, I, J, T);
      const sph = fitSphere(legs, n, I, J, T);
      const resid = legs.map((l, k) => {
        const fl = Math.hypot(flat.P[I[k]][0] - flat.P[J[k]][0], flat.P[I[k]][1] - flat.P[J[k]][1]);
        let dot = sph.V[I[k]][0] * sph.V[J[k]][0] + sph.V[I[k]][1] * sph.V[J[k]][1] + sph.V[I[k]][2] * sph.V[J[k]][2];
        dot = Math.max(-1, Math.min(1, dot));
        return { a: l.a, b: l.b, t: l.h, flat: fl - l.h, sph: sph.R * Math.acos(dot) - l.h };
      });
      setResult({ cities, flatRms: flat.rms, sphRms: sph.rms, circHours: 2 * Math.PI * sph.R, P: flat.P, resid });
      setRan(true); setBusy(false);
    }, 30);
  }, [legs]);

  const editLeg = (i: number, h: number) =>
    setLegs(ls => ls.map((l, k) => (k === i ? { ...l, h } : l)));

  // Rendu de la carte plate obtenue (orientée : ville d'ancrage en haut)
  const mapSvg = useMemo(() => {
    if (!result) return null;
    const { cities, P } = result;
    const ai = cities.indexOf(anchor) >= 0 ? cities.indexOf(anchor) : 0;
    const cx = P.reduce((s, p) => s + p[0], 0) / P.length;
    const cy = P.reduce((s, p) => s + p[1], 0) / P.length;
    const ax = P[ai][0] - cx, ay = P[ai][1] - cy;
    const rot = -Math.atan2(ax, -ay);
    const pts = P.map(p => {
      const x = p[0] - cx, y = p[1] - cy;
      return [x * Math.cos(rot) - y * Math.sin(rot), x * Math.sin(rot) + y * Math.cos(rot)];
    });
    const m = Math.max(...pts.map(p => Math.hypot(p[0], p[1]))) || 1;
    const S = 150 / m;
    return { pts: pts.map(p => [180 + p[0] * S, 180 + p[1] * S]), cities };
  }, [result, anchor]);

  const card: React.CSSProperties = {
    background: 'var(--card)', border: '1px solid var(--border)',
    borderRadius: 10, padding: '16px 18px',
  };

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      <div style={{ ...card, borderLeft: `3px solid ${OPAL}` }}>
        <div style={{ fontSize: 11, fontFamily: MONO, color: OPAL, letterSpacing: '0.1em', marginBottom: 8 }}>
          MÉTHODE
        </div>
        <p style={{ fontSize: 13.5, color: 'var(--ink-soft)', lineHeight: 1.65, margin: 0 }}>
          Aucune carte n&apos;est utilisée. On part uniquement de <strong>durées de trajet mesurées</strong>
          {' '}(horaires publiés, vérifiables), et on cherche par calcul <strong>où placer les villes</strong> pour
          reproduire ces durées — d&apos;abord sur un <strong>plan</strong> (forme totalement libre), puis sur une
          {' '}<strong>sphère</strong> (rayon libre). La géométrie qui laisse le moins d&apos;erreur est celle qui
          décrit le mieux les trajets réels. Modifiez les durées : les conclusions se recalculent.
        </p>
      </div>

      <div style={{ display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'flex-end' }}>
        <div>
          <div style={{ fontSize: 11, color: 'var(--ink-muted)', fontFamily: MONO, marginBottom: 4 }}>
            VITESSE DE CROISIÈRE (km/h)
          </div>
          <input type="number" value={speed} onChange={e => setSpeed(Number(e.target.value) || 0)}
            style={{
              width: 120, background: 'var(--bg)', border: '1px solid var(--border)',
              color: 'var(--ink)', padding: '8px 10px', borderRadius: 6, fontFamily: MONO, fontSize: 14,
            }} />
        </div>
        <div>
          <div style={{ fontSize: 11, color: 'var(--ink-muted)', fontFamily: MONO, marginBottom: 4 }}>
            VILLE EN HAUT DE CARTE
          </div>
          <select value={anchor} onChange={e => setAnchor(e.target.value)}
            style={{
              background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--ink)',
              padding: '8px 10px', borderRadius: 6, fontFamily: MONO, fontSize: 14,
            }}>
            {(result?.cities ?? ['LHR']).map(c => <option key={c} value={c}>{c}</option>)}
          </select>
        </div>
        <button onClick={run} disabled={busy}
          style={{
            background: OPAL, color: '#08130f', border: 'none', padding: '11px 22px',
            borderRadius: 8, fontWeight: 800, fontFamily: MONO, fontSize: 13,
            letterSpacing: '0.06em', cursor: busy ? 'wait' : 'pointer',
          }}>
          {busy ? 'CALCUL…' : ran ? 'RECALCULER' : 'CONSTRUIRE LA CARTE'}
        </button>
      </div>

      {result && (
        <>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(210px,1fr))', gap: 12 }}>
            <div style={{ ...card, borderTop: `3px solid ${ROSE}` }}>
              <div style={{ fontSize: 11, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 6 }}>
                MEILLEUR PLAN POSSIBLE
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: ROSE, fontFamily: MONO }}>
                {result.flatRms.toFixed(2)} h
              </div>
              <div style={{ fontSize: 12, color: 'var(--ink-muted)', marginTop: 4 }}>
                erreur résiduelle moyenne
              </div>
            </div>
            <div style={{ ...card, borderTop: `3px solid ${CYAN}` }}>
              <div style={{ fontSize: 11, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 6 }}>
                SPHÈRE (RAYON LIBRE)
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: CYAN, fontFamily: MONO }}>
                {result.sphRms.toFixed(2)} h
              </div>
              <div style={{ fontSize: 12, color: 'var(--ink-muted)', marginTop: 4 }}>
                erreur résiduelle moyenne
              </div>
            </div>
            <div style={{ ...card, borderTop: `3px solid ${GOLD}` }}>
              <div style={{ fontSize: 11, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 6 }}>
                TAILLE DÉDUITE DES TRAJETS
              </div>
              <div style={{ fontSize: 28, fontWeight: 800, color: GOLD, fontFamily: MONO }}>
                {(result.circHours * speed).toLocaleString('fr-FR', { maximumFractionDigits: 0 })} km
              </div>
              <div style={{ fontSize: 12, color: 'var(--ink-muted)', marginTop: 4 }}>
                circonférence ({result.circHours.toFixed(1)} h × {speed} km/h)
              </div>
            </div>
          </div>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit,minmax(330px,1fr))', gap: 16 }}>
            {/* Carte obtenue */}
            <div style={card}>
              <div style={{ fontSize: 11, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 10 }}>
                CARTE OBTENUE — PLACEMENT DÉDUIT DES SEULS TRAJETS
              </div>
              <svg viewBox="0 0 360 360" style={{ width: '100%', background: '#0d1117', borderRadius: 8 }}>
                <rect width="360" height="360" fill="#0d1117" />
                {[50, 100, 150].map(r => (
                  <circle key={r} cx="180" cy="180" r={r} fill="none" stroke="#1e2c48" strokeWidth="1" />
                ))}
                <line x1="180" y1="20" x2="180" y2="340" stroke="#1e2c48" strokeWidth="1" />
                <line x1="20" y1="180" x2="340" y2="180" stroke="#1e2c48" strokeWidth="1" />
                {legs.map((l, k) => {
                  const ia = result.cities.indexOf(l.a), ib = result.cities.indexOf(l.b);
                  if (!mapSvg || ia < 0 || ib < 0) return null;
                  return <line key={k} x1={mapSvg.pts[ia][0]} y1={mapSvg.pts[ia][1]}
                    x2={mapSvg.pts[ib][0]} y2={mapSvg.pts[ib][1]}
                    stroke={OPAL} strokeWidth="0.5" opacity="0.28" />;
                })}
                {mapSvg?.pts.map((p, i) => (
                  <g key={i}>
                    <circle cx={p[0]} cy={p[1]} r="3.5" fill={GOLD} />
                    <text x={p[0] + 6} y={p[1] + 3.5} fill="#c8d8e8" fontSize="9" fontFamily="monospace">
                      {mapSvg.cities[i]}
                    </text>
                  </g>
                ))}
              </svg>
              <p style={{ fontSize: 11.5, color: 'var(--ink-muted)', fontStyle: 'italic', marginTop: 8, lineHeight: 1.5 }}>
                Meilleur arrangement plan possible. L&apos;orientation est arbitraire (choisissez la ville placée
                en haut) : seules les distances relatives ont un sens.
              </p>
            </div>

            {/* Résidus */}
            <div style={card}>
              <div style={{ fontSize: 11, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 10 }}>
                ÉCART PAR LIAISON — <span style={{ color: ROSE }}>PLAN</span> vs <span style={{ color: CYAN }}>SPHÈRE</span>
              </div>
              <div style={{ maxHeight: 330, overflowY: 'auto' }}>
                {[...result.resid].sort((x, y) => Math.abs(y.flat) - Math.abs(x.flat)).map((r, i) => {
                  const w = (v: number) => Math.min(100, Math.abs(v) / 2.5 * 100);
                  return (
                    <div key={i} style={{ marginBottom: 7 }}>
                      <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 10.5, fontFamily: MONO, color: 'var(--ink-muted)' }}>
                        <span>{r.a}–{r.b}</span>
                        <span>{r.t.toFixed(1)} h</span>
                      </div>
                      <div style={{ display: 'flex', gap: 3, alignItems: 'center' }}>
                        <div style={{ flex: 1, height: 7, background: 'var(--bg)', borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{ width: `${w(r.flat)}%`, height: '100%', background: ROSE }} />
                        </div>
                        <span style={{ fontSize: 9.5, fontFamily: MONO, color: ROSE, width: 40, textAlign: 'right' }}>
                          {r.flat > 0 ? '+' : ''}{r.flat.toFixed(1)}
                        </span>
                      </div>
                      <div style={{ display: 'flex', gap: 3, alignItems: 'center', marginTop: 2 }}>
                        <div style={{ flex: 1, height: 7, background: 'var(--bg)', borderRadius: 2, overflow: 'hidden' }}>
                          <div style={{ width: `${w(r.sph)}%`, height: '100%', background: CYAN }} />
                        </div>
                        <span style={{ fontSize: 9.5, fontFamily: MONO, color: CYAN, width: 40, textAlign: 'right' }}>
                          {r.sph > 0 ? '+' : ''}{r.sph.toFixed(1)}
                        </span>
                      </div>
                    </div>
                  );
                })}
              </div>
            </div>
          </div>
        </>
      )}

      {/* Données */}
      <div style={card}>
        <div style={{ fontSize: 11, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 10 }}>
          DONNÉES SOURCES — {legs.length} LIAISONS SANS ESCALE (modifiables)
        </div>
        <div style={{ maxHeight: 300, overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ color: 'var(--ink-muted)', fontFamily: MONO, fontSize: 10.5, textAlign: 'left' }}>
                <th style={{ padding: '4px 6px' }}>LIAISON</th>
                <th style={{ padding: '4px 6px', width: 90 }}>DURÉE (h)</th>
                <th style={{ padding: '4px 6px' }}>SOURCE</th>
              </tr>
            </thead>
            <tbody>
              {legs.map((l, i) => (
                <tr key={i} style={{ borderTop: '1px solid var(--border-soft)' }}>
                  <td style={{ padding: '4px 6px', fontFamily: MONO, color: 'var(--ink)' }}>
                    {l.mode === 'mer' ? '⚓ ' : '✈ '}{l.a}–{l.b}
                  </td>
                  <td style={{ padding: '4px 6px' }}>
                    <input type="number" step="0.1" value={l.h}
                      onChange={e => editLeg(i, Number(e.target.value) || 0)}
                      style={{
                        width: 72, background: 'var(--bg)', border: '1px solid var(--border)',
                        color: 'var(--ink)', padding: '3px 6px', borderRadius: 4, fontFamily: MONO, fontSize: 12,
                      }} />
                  </td>
                  <td style={{ padding: '4px 6px', color: 'var(--ink-muted)', fontSize: 11 }}>{l.src}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
        <p style={{ fontSize: 11.5, color: 'var(--ink-muted)', fontStyle: 'italic', marginTop: 10, lineHeight: 1.55 }}>
          Durées moyennes aller/retour (les vents rendent l&apos;aller et le retour inégaux), arrondies à 0,1 h.
          Marge d&apos;incertitude estimée : ±0,5 h. C&apos;est cette incertitude qui fixe le plancher de
          l&apos;erreur résiduelle — aucun modèle ne peut faire mieux que la précision des données.
        </p>
      </div>
    </div>
  );
}
