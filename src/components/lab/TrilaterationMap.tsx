'use client';
import { useState, useMemo, useCallback } from 'react';

/* ═══════════════════════════════════════════════════════════════
   CARTE PAR TRILATÉRATION
   Toile vierge. Aucune carte de fond, aucun centre, aucune
   coordonnée. Les villes sont placées uniquement à partir des
   distances saisies : la première sert d'ancrage, la deuxième se
   place à la distance donnée (orientation libre), les suivantes
   par trilatération sur les villes déjà placées.
   Si le réseau ne peut pas s'aplanir sans déformation, on applique
   le meilleur compromis (tension globale minimale) et on affiche
   l'écart entre distance saisie et distance tracée.
   ═══════════════════════════════════════════════════════════════ */

const OPAL = '#3D9E7C';
const GOLD = '#D4943A';
const ROSE = '#C45E6A';
const MONO = "'JetBrains Mono', monospace";
const NM = 1.852;

interface Leg { a: string; b: string; km: number; src: string; }

/** Lot de données fourni — repris tel quel, sans modification. */
const SEED: Leg[] = [
  { a: 'Paris', b: 'Londres', km: 343, src: 'Géodésique / Directe — triangulation IGN / Ordnance Survey' },
  { a: 'Paris', b: 'Berlin', km: 878, src: 'Terrestre (Odomètre / Rail) — via Francfort' },
  { a: 'Paris', b: 'Moscou', km: 3217, src: 'Terrestre (Odomètre / Rail) — via Allemagne et Biélorussie' },
  { a: 'New York', b: 'Londres', km: 5869, src: 'Maritime (NGA Pub. 151) — Bishop Rock' },
  { a: 'New York', b: 'Rio de Janeiro', km: 8834, src: 'Maritime (NGA Pub. 151) — Atlantique' },
  { a: 'New York', b: 'Los Angeles', km: 4491, src: 'Terrestre (Odomètre / Route) — I-80 / I-15' },
  { a: 'Los Angeles', b: 'Tokyo', km: 8816, src: 'Maritime (NGA Pub. 151) — transpacifique' },
  { a: 'Tokyo', b: 'Sydney', km: 8225, src: 'Maritime (NGA Pub. 151) — Pacifique Ouest' },
  { a: 'Londres', b: 'Le Caire', km: 3510, src: 'Aérienne (Orthodromie) — trajet direct' },
  { a: 'Sydney', b: 'Auckland', km: 2156, src: 'Maritime (NGA Pub. 151) — mer de Tasman' },
];

// ── Géométrie ───────────────────────────────────────────────────
type Pt = { x: number; y: number };

/** Intersection de deux cercles. Renvoie 0, 1 ou 2 points.
 *  Si les cercles ne se coupent pas, renvoie le point de compromis
 *  situé sur la droite qui les joint. */
function circleIntersect(p1: Pt, r1: number, p2: Pt, r2: number): Pt[] {
  const dx = p2.x - p1.x, dy = p2.y - p1.y;
  const d = Math.hypot(dx, dy);
  if (d < 1e-9) return [];
  const ux = dx / d, uy = dy / d;
  if (d > r1 + r2 || d < Math.abs(r1 - r2)) {
    // pas d'intersection : compromis sur l'axe (respecte au mieux les deux rayons)
    const t = d > r1 + r2 ? r1 + (d - r1 - r2) / 2 : (r1 + (d + r2)) / 2;
    return [{ x: p1.x + ux * t, y: p1.y + uy * t }];
  }
  const a = (r1 * r1 - r2 * r2 + d * d) / (2 * d);
  const h2 = r1 * r1 - a * a;
  const h = Math.sqrt(Math.max(0, h2));
  const bx = p1.x + ux * a, by = p1.y + uy * a;
  if (h < 1e-9) return [{ x: bx, y: by }];
  return [{ x: bx - uy * h, y: by + ux * h }, { x: bx + uy * h, y: by - ux * h }];
}

/** Ordre d'insertion : ordre d'apparition des villes dans la liste des liaisons. */
function insertionOrder(legs: Leg[]): string[] {
  const seen: string[] = [];
  legs.forEach(l => { [l.a, l.b].forEach(c => { if (!seen.includes(c)) seen.push(c); }); });
  return seen;
}

/** Relaxation par ressorts : minimise la tension globale
 *  Σ (distance tracée − distance saisie)². */
function relax(pos: Map<string, Pt>, legs: Leg[], iterations = 4000) {
  const names = Array.from(pos.keys());
  const active = legs.filter(l => pos.has(l.a) && pos.has(l.b));
  if (active.length === 0) return;
  for (let it = 0; it < iterations; it++) {
    const g = new Map<string, Pt>(names.map(n => [n, { x: 0, y: 0 }]));
    for (const l of active) {
      const A = pos.get(l.a)!, B = pos.get(l.b)!;
      const dx = A.x - B.x, dy = A.y - B.y;
      const L = Math.hypot(dx, dy) + 1e-9;
      const c = 2 * (L - l.km) / L;
      const ga = g.get(l.a)!, gb = g.get(l.b)!;
      ga.x += c * dx; ga.y += c * dy;
      gb.x -= c * dx; gb.y -= c * dy;
    }
    const lr = 0.12 / active.length;
    for (const n of names) {
      const p = pos.get(n)!, gr = g.get(n)!;
      p.x -= lr * gr.x; p.y -= lr * gr.y;
    }
  }
}

/** Construit la carte de façon incrémentale, ville par ville. */
function buildMap(legs: Leg[], upTo: number) {
  const order = insertionOrder(legs).slice(0, upTo);
  const pos = new Map<string, Pt>();
  const unconstrained: string[] = [];

  order.forEach((city, i) => {
    const links = legs.filter(l =>
      (l.a === city && pos.has(l.b)) || (l.b === city && pos.has(l.a)));

    if (i === 0) { pos.set(city, { x: 0, y: 0 }); return; }

    if (links.length === 0) {
      // aucune distance connue vers les villes déjà placées
      const ang = (i / Math.max(1, order.length)) * Math.PI * 2;
      const spread = 4000;
      pos.set(city, { x: Math.cos(ang) * spread, y: Math.sin(ang) * spread });
      unconstrained.push(city);
      return;
    }

    const ref = (l: Leg) => (l.a === city ? pos.get(l.b)! : pos.get(l.a)!);

    if (links.length === 1) {
      // une seule contrainte : distance respectée, orientation libre
      const p = ref(links[0]); const d = links[0].km;
      const ang = pos.size === 1 ? 0 : (i * 2.399963);   // angle d'or, pour étaler
      pos.set(city, { x: p.x + Math.cos(ang) * d, y: p.y + Math.sin(ang) * d });
      return;
    }

    // deux contraintes ou plus : trilatération
    const [l1, l2] = links;
    const cands = circleIntersect(ref(l1), l1.km, ref(l2), l2.km);
    if (cands.length === 0) { pos.set(city, { x: 0, y: 0 }); return; }
    // on retient la solution qui respecte le mieux les autres distances connues
    let bestPt = cands[0], bestErr = Infinity;
    for (const c of cands) {
      let err = 0;
      for (const l of links.slice(2)) {
        const p = ref(l);
        err += (Math.hypot(c.x - p.x, c.y - p.y) - l.km) ** 2;
      }
      if (err < bestErr) { bestErr = err; bestPt = c; }
    }
    pos.set(city, bestPt);
  });

  // meilleur compromis global sur l'ensemble des villes placées
  relax(pos, legs);
  return { pos, order, unconstrained };
}

// ── Composant ───────────────────────────────────────────────────
export default function TrilaterationMap() {
  const [legs, setLegs] = useState<Leg[]>(SEED);
  const [unit, setUnit] = useState<'km' | 'nm'>('km');
  const order = useMemo(() => insertionOrder(legs), [legs]);
  const [shown, setShown] = useState(2);
  const [form, setForm] = useState({ a: '', b: '', km: '', src: '' });

  const nShown = Math.min(Math.max(2, shown), order.length);
  const built = useMemo(() => buildMap(legs, nShown), [legs, nShown]);

  const conv = (km: number) => (unit === 'km' ? km : km / NM);
  const uLabel = unit === 'km' ? 'km' : 'NM';
  const fmt = (km: number) =>
    conv(km).toLocaleString('fr-FR', { maximumFractionDigits: 0 });

  // liaisons visibles + écart entre saisi et tracé
  const visible = useMemo(() => {
    const { pos } = built;
    return legs
      .filter(l => pos.has(l.a) && pos.has(l.b))
      .map(l => {
        const A = pos.get(l.a)!, B = pos.get(l.b)!;
        const drawn = Math.hypot(A.x - B.x, A.y - B.y);
        return { ...l, drawn, gap: drawn - l.km };
      });
  }, [built, legs]);

  // mise à l'échelle pour l'affichage
  const view = useMemo(() => {
    const pts = Array.from(built.pos.values());
    if (pts.length === 0) return null;
    const xs = pts.map(p => p.x), ys = pts.map(p => p.y);
    const minX = Math.min(...xs), maxX = Math.max(...xs);
    const minY = Math.min(...ys), maxY = Math.max(...ys);
    const w = Math.max(1, maxX - minX), h = Math.max(1, maxY - minY);
    const pad = 60;
    const S = Math.min((680 - 2 * pad) / w, (520 - 2 * pad) / h);
    const cx = (minX + maxX) / 2, cy = (minY + maxY) / 2;
    const map = (p: Pt) => ({ x: 340 + (p.x - cx) * S, y: 260 + (p.y - cy) * S });
    return { map, S };
  }, [built]);

  const addLeg = useCallback(() => {
    const km = Number(form.km);
    if (!form.a.trim() || !form.b.trim() || !km || km <= 0) return;
    const kmStored = unit === 'km' ? km : km * NM;
    setLegs(ls => [...ls, {
      a: form.a.trim(), b: form.b.trim(), km: kmStored,
      src: form.src.trim() || 'source non renseignée',
    }]);
    setForm({ a: '', b: '', km: '', src: '' });
  }, [form, unit]);

  const card: React.CSSProperties = {
    background: 'var(--card)', border: '1px solid var(--border)',
    borderRadius: 10, padding: '16px 18px',
  };
  const input: React.CSSProperties = {
    background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--ink)',
    padding: '7px 9px', borderRadius: 6, fontFamily: MONO, fontSize: 13, width: '100%',
  };

  // barre d'échelle
  const scaleBar = useMemo(() => {
    if (!view) return null;
    const targets = [500, 1000, 2000, 5000, 10000];
    const t = targets.find(v => v * view.S > 70 && v * view.S < 220) ?? 5000;
    return { km: t, px: t * view.S };
  }, [view]);

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 16 }}>

      {/* Contrôles */}
      <div style={{ ...card, display: 'flex', gap: 18, flexWrap: 'wrap', alignItems: 'center' }}>
        <div>
          <div style={{ fontSize: 10.5, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 5 }}>
            VILLES PLACÉES
          </div>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
            <button onClick={() => setShown(s => Math.max(2, s - 1))}
              style={{ background: 'var(--bg)', border: '1px solid var(--border)', color: 'var(--ink)', width: 30, height: 30, borderRadius: 6, cursor: 'pointer', fontSize: 15 }}>−</button>
            <span style={{ fontFamily: MONO, fontSize: 17, fontWeight: 800, color: OPAL, minWidth: 54, textAlign: 'center' }}>
              {nShown} / {order.length}
            </span>
            <button onClick={() => setShown(s => Math.min(order.length, s + 1))}
              style={{ background: OPAL, border: 'none', color: '#08130f', width: 30, height: 30, borderRadius: 6, cursor: 'pointer', fontSize: 15, fontWeight: 800 }}>+</button>
          </div>
        </div>
        <div>
          <div style={{ fontSize: 10.5, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 5 }}>UNITÉ</div>
          <div style={{ display: 'flex', gap: 4 }}>
            {(['km', 'nm'] as const).map(u => (
              <button key={u} onClick={() => setUnit(u)}
                style={{
                  background: unit === u ? OPAL : 'var(--bg)', color: unit === u ? '#08130f' : 'var(--ink-soft)',
                  border: `1px solid ${unit === u ? OPAL : 'var(--border)'}`, padding: '6px 13px',
                  borderRadius: 6, cursor: 'pointer', fontFamily: MONO, fontSize: 12, fontWeight: 700,
                }}>{u === 'km' ? 'KM' : 'MILLES NAUT.'}</button>
            ))}
          </div>
        </div>
        <div style={{ marginLeft: 'auto', fontSize: 11.5, color: 'var(--ink-muted)', fontFamily: MONO }}>
          {visible.length} liaison{visible.length > 1 ? 's' : ''} tracée{visible.length > 1 ? 's' : ''}
        </div>
      </div>

      {/* Toile */}
      <div style={{ ...card, padding: 0, overflow: 'hidden' }}>
        <svg viewBox="0 0 680 520" style={{ width: '100%', display: 'block', background: '#0d1117' }}>
          <rect width="680" height="520" fill="#0d1117" />
          {view && visible.map((l, i) => {
            const A = view.map(built.pos.get(l.a)!), B = view.map(built.pos.get(l.b)!);
            const mx = (A.x + B.x) / 2, my = (A.y + B.y) / 2;
            const tense = Math.abs(l.gap) / l.km > 0.02;
            return (
              <g key={i}>
                <line x1={A.x} y1={A.y} x2={B.x} y2={B.y}
                  stroke={tense ? ROSE : OPAL} strokeWidth={tense ? 1.4 : 1}
                  strokeDasharray={tense ? '5,3' : undefined} opacity="0.75" />
                <text x={mx} y={my - 4} fill={tense ? ROSE : '#8fa0b8'} fontSize="8.5"
                  fontFamily="monospace" textAnchor="middle">
                  {fmt(l.km)} {uLabel}
                </text>
                {tense && (
                  <text x={mx} y={my + 7} fill={ROSE} fontSize="7.5" fontFamily="monospace" textAnchor="middle">
                    tracé {fmt(l.drawn)} ({l.gap > 0 ? '+' : ''}{fmt(l.gap)})
                  </text>
                )}
              </g>
            );
          })}
          {view && (() => {
            // placement des libellés : côté choisi selon la position, décalage
            // vertical si deux villes sont trop proches à l'écran
            const placed: { x: number; y: number }[] = [];
            return built.order.map(c => {
              const p = view.map(built.pos.get(c)!);
              const free = built.unconstrained.includes(c);
              const right = p.x < 520;
              let ly = p.y + 4;
              while (placed.some(q => Math.abs(q.x - p.x) < 90 && Math.abs(q.y - ly) < 12)) ly += 13;
              placed.push({ x: p.x, y: ly });
              return (
                <g key={c}>
                  <circle cx={p.x} cy={p.y} r="4.5" fill={free ? '#6b7a8f' : GOLD}
                    stroke="#0d1117" strokeWidth="1.5" />
                  {Math.abs(ly - (p.y + 4)) > 6 && (
                    <line x1={p.x} y1={p.y} x2={right ? p.x + 6 : p.x - 6} y2={ly - 3}
                      stroke="#4a5b70" strokeWidth="0.6" />
                  )}
                  <text x={right ? p.x + 8 : p.x - 8} y={ly} fill="#c8d8e8" fontSize="11"
                    fontFamily="monospace" fontWeight="bold" textAnchor={right ? 'start' : 'end'}>
                    {c}
                  </text>
                </g>
              );
            });
          })()}
          {scaleBar && (
            <g transform="translate(24,494)">
              <line x1="0" y1="0" x2={scaleBar.px} y2="0" stroke="#8fa0b8" strokeWidth="1.5" />
              <line x1="0" y1="-4" x2="0" y2="4" stroke="#8fa0b8" strokeWidth="1.5" />
              <line x1={scaleBar.px} y1="-4" x2={scaleBar.px} y2="4" stroke="#8fa0b8" strokeWidth="1.5" />
              <text x={scaleBar.px / 2} y="-8" fill="#8fa0b8" fontSize="9" fontFamily="monospace" textAnchor="middle">
                {fmt(scaleBar.km)} {uLabel}
              </text>
            </g>
          )}
        </svg>
      </div>

      <p style={{ fontSize: 12, color: 'var(--ink-muted)', fontStyle: 'italic', lineHeight: 1.6, margin: 0 }}>
        La première ville sert d&apos;ancrage, la deuxième se place à la distance donnée (orientation libre), les
        suivantes par trilatération sur les villes déjà placées. Les liaisons en <span style={{ color: ROSE }}>rose
        pointillé</span> ne peuvent pas être respectées exactement : le tracé applique le meilleur compromis et
        l&apos;écart est indiqué. Un point <span style={{ color: '#6b7a8f' }}>gris</span> signale une ville sans
        distance connue vers le réseau déjà placé.
      </p>

      {/* Saisie */}
      <div style={card}>
        <div style={{ fontSize: 10.5, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 10 }}>
          AJOUTER UNE LIAISON
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 110px 1.6fr auto', gap: 8, alignItems: 'end' }}>
          <input style={input} placeholder="Ville A" value={form.a} onChange={e => setForm({ ...form, a: e.target.value })} />
          <input style={input} placeholder="Ville B" value={form.b} onChange={e => setForm({ ...form, b: e.target.value })} />
          <input style={input} type="number" placeholder={uLabel} value={form.km} onChange={e => setForm({ ...form, km: e.target.value })} />
          <input style={input} placeholder="Provenance (source)" value={form.src} onChange={e => setForm({ ...form, src: e.target.value })} />
          <button onClick={addLeg}
            style={{ background: OPAL, color: '#08130f', border: 'none', padding: '8px 16px', borderRadius: 6, fontFamily: MONO, fontSize: 12, fontWeight: 800, cursor: 'pointer' }}>
            AJOUTER
          </button>
        </div>
      </div>

      {/* Données */}
      <div style={card}>
        <div style={{ fontSize: 10.5, fontFamily: MONO, color: 'var(--ink-muted)', marginBottom: 10 }}>
          DONNÉES — {legs.length} LIAISON{legs.length > 1 ? 'S' : ''}
        </div>
        <div style={{ maxHeight: 300, overflowY: 'auto' }}>
          <table style={{ width: '100%', borderCollapse: 'collapse', fontSize: 12 }}>
            <thead>
              <tr style={{ color: 'var(--ink-muted)', fontFamily: MONO, fontSize: 10, textAlign: 'left' }}>
                <th style={{ padding: '4px 6px' }}>LIAISON</th>
                <th style={{ padding: '4px 6px', width: 100 }}>SAISI ({uLabel})</th>
                <th style={{ padding: '4px 6px', width: 100 }}>TRACÉ</th>
                <th style={{ padding: '4px 6px' }}>PROVENANCE</th>
                <th style={{ padding: '4px 6px', width: 30 }} />
              </tr>
            </thead>
            <tbody>
              {legs.map((l, i) => {
                const v = visible.find(x => x.a === l.a && x.b === l.b && x.km === l.km);
                return (
                  <tr key={i} style={{ borderTop: '1px solid var(--border-soft)' }}>
                    <td style={{ padding: '4px 6px', fontFamily: MONO, color: 'var(--ink)' }}>{l.a} – {l.b}</td>
                    <td style={{ padding: '4px 6px' }}>
                      <input type="number" value={Math.round(conv(l.km))}
                        onChange={e => {
                          const val = Number(e.target.value) || 0;
                          setLegs(ls => ls.map((x, k) => k === i ? { ...x, km: unit === 'km' ? val : val * NM } : x));
                        }}
                        style={{ ...input, width: 84, padding: '3px 6px', fontSize: 12 }} />
                    </td>
                    <td style={{ padding: '4px 6px', fontFamily: MONO, fontSize: 11.5, color: v && Math.abs(v.gap) / l.km > 0.02 ? ROSE : 'var(--ink-muted)' }}>
                      {v ? `${fmt(v.drawn)}${Math.abs(v.gap) / l.km > 0.02 ? ` (${v.gap > 0 ? '+' : ''}${fmt(v.gap)})` : ''}` : '—'}
                    </td>
                    <td style={{ padding: '4px 6px', color: 'var(--ink-muted)', fontSize: 10.5 }}>{l.src}</td>
                    <td style={{ padding: '4px 6px' }}>
                      <button onClick={() => setLegs(ls => ls.filter((_, k) => k !== i))}
                        style={{ background: 'none', border: 'none', color: ROSE, cursor: 'pointer', fontSize: 14 }}>×</button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
