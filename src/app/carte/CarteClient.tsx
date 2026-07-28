'use client';

import { useMemo, useState } from 'react';
import type { ReseauData, Noyau } from '@/lib/reseau';

type Projection = 'equirect' | 'azimutale';

const W = 1000;
const H = 520;
const R_TERRE = 6371008.8;

/* ---------- projections ---------- */

function projEquirect(lat: number, lon: number): [number, number] {
  return [((lon + 180) / 360) * W, ((90 - lat) / 180) * H];
}

// Azimutale équidistante polaire nord : r ∝ colatitude, angle = longitude.
// C'est le modèle plan de référence du projet, dessiné tel qu'il est.
function projAzimutale(lat: number, lon: number): [number, number] {
  const cx = W / 2;
  const cy = H / 2;
  const rMax = H / 2 - 12;
  const r = ((90 - lat) / 180) * rMax;
  const a = ((lon - 90) * Math.PI) / 180;
  return [cx + r * Math.cos(a), cy + r * Math.sin(a)];
}

/* ---------- utilitaires ---------- */

function fmt(m: number): string {
  if (Math.abs(m) >= 1000)
    return `${(m / 1000).toLocaleString('fr-FR', { maximumFractionDigits: 1 })} km`;
  return `${Math.round(m).toLocaleString('fr-FR')} m`;
}

function etirement(lat: number): number {
  const th = ((90 - lat) * Math.PI) / 180;
  return th / Math.sin(th);
}

export default function CarteClient({ data }: { data: ReseauData }) {
  const [proj, setProj] = useState<Projection>('equirect');
  const [voirCordes, setVoirCordes] = useState(true);
  const [voirPoints, setVoirPoints] = useState(false);
  const [selection, setSelection] = useState<Noyau | null>(null);

  const P = proj === 'equirect' ? projEquirect : projAzimutale;

  const centres = useMemo(
    () => new Map(data.noyaux.map((n) => [n.centre.nom, n])),
    [data.noyaux]
  );

  const grille = useMemo(() => {
    const lignes: { d: string; fort: boolean }[] = [];
    if (proj === 'equirect') {
      for (let lon = -180; lon <= 180; lon += 30) {
        const [x1, y1] = P(90, lon);
        const [x2, y2] = P(-90, lon);
        lignes.push({ d: `M${x1},${y1}L${x2},${y2}`, fort: lon === 0 });
      }
      for (let lat = -60; lat <= 60; lat += 30) {
        const [x1, y1] = P(lat, -180);
        const [x2, y2] = P(lat, 180);
        lignes.push({ d: `M${x1},${y1}L${x2},${y2}`, fort: lat === 0 });
      }
    } else {
      for (let lon = -180; lon < 180; lon += 30) {
        const [x1, y1] = P(90, lon);
        const [x2, y2] = P(-90, lon);
        lignes.push({ d: `M${x1},${y1}L${x2},${y2}`, fort: lon === 0 });
      }
      for (let lat = 60; lat >= -60; lat -= 30) {
        const pts: string[] = [];
        for (let lon = -180; lon <= 180; lon += 5) {
          const [x, y] = P(lat, lon);
          pts.push(`${x},${y}`);
        }
        lignes.push({ d: `M${pts.join('L')}Z`, fort: lat === 0 });
      }
    }
    return lignes;
  }, [proj, P]);

  const cible1 = data.cibles[0];

  return (
    <div style={{ minHeight: '100vh', background: 'var(--bg)' }}>
      <header
        style={{
          padding: '128px 24px 40px',
          maxWidth: 1240,
          margin: '0 auto',
        }}
      >
        <div
          style={{
            display: 'inline-block',
            padding: '6px 14px',
            borderRadius: 999,
            background: 'var(--card)',
            border: '1px solid var(--border)',
            fontSize: '0.72rem',
            letterSpacing: '0.14em',
            textTransform: 'uppercase',
            color: 'var(--ink-muted)',
            marginBottom: 20,
          }}
        >
          Réseaux de distances
        </div>
        <h1
          style={{
            fontSize: 'clamp(2rem, 4.5vw, 3.2rem)',
            lineHeight: 1.08,
            margin: 0,
            color: 'var(--ink)',
          }}
        >
          La carte du réseau
        </h1>
        <p
          style={{
            marginTop: 18,
            maxWidth: '62ch',
            fontSize: '1.05rem',
            lineHeight: 1.65,
            color: 'var(--ink-soft)',
          }}
        >
          {data.stats.noyaux} noyaux géodésiques clos, {data.stats.points} points relevés,{' '}
          {data.stats.distances} distances calculées — et <strong>zéro mesure de terrain</strong>.
          Basculez entre les deux modèles pour voir où ils cessent d&apos;être d&apos;accord.
        </p>
      </header>

      <div
        style={{
          maxWidth: 1240,
          margin: '0 auto',
          padding: '0 24px 96px',
          display: 'grid',
          gridTemplateColumns: 'minmax(0, 1fr) minmax(280px, 340px)',
          gap: 28,
          alignItems: 'start',
        }}
        className="tei-carte-grid"
      >
        {/* ---------- carte ---------- */}
        <section>
          <div
            style={{
              display: 'flex',
              flexWrap: 'wrap',
              gap: 8,
              marginBottom: 14,
            }}
          >
            {(
              [
                ['equirect', 'Équirectangulaire (WGS84)'],
                ['azimutale', 'Azimutale équidistante polaire nord'],
              ] as [Projection, string][]
            ).map(([k, label]) => (
              <button
                key={k}
                onClick={() => setProj(k)}
                style={{
                  padding: '9px 15px',
                  borderRadius: 8,
                  border: `1px solid ${proj === k ? 'var(--opal)' : 'var(--border)'}`,
                  background: proj === k ? 'var(--opal)' : 'transparent',
                  color: proj === k ? '#fff' : 'var(--ink-soft)',
                  fontSize: '0.82rem',
                  cursor: 'pointer',
                  fontFamily: 'inherit',
                }}
              >
                {label}
              </button>
            ))}
            <span style={{ flex: 1 }} />
            <label style={chk}>
              <input
                type="checkbox"
                checked={voirCordes}
                onChange={(e) => setVoirCordes(e.target.checked)}
              />
              Cordes K{data.noyaux.length + data.reperes.length}
            </label>
            <label style={chk}>
              <input
                type="checkbox"
                checked={voirPoints}
                onChange={(e) => setVoirPoints(e.target.checked)}
              />
              Tous les points
            </label>
          </div>

          <div
            style={{
              border: '1px solid var(--border)',
              borderRadius: 12,
              overflow: 'hidden',
              background: '#0d1117',
            }}
          >
            <svg viewBox={`0 0 ${W} ${H}`} style={{ display: 'block', width: '100%' }}>
              <rect width={W} height={H} fill="#0d1117" />

              {grille.map((g, i) => (
                <path
                  key={i}
                  d={g.d}
                  fill="none"
                  stroke={g.fort ? '#2c3947' : '#1b2530'}
                  strokeWidth={g.fort ? 1.2 : 0.7}
                />
              ))}

              {voirCordes &&
                data.cordes.map((c, i) => {
                  const A = centres.get(c.a);
                  const B = centres.get(c.b);
                  const pa = A
                    ? P(A.centre.latitude, A.centre.longitude)
                    : reperePos(data, c.a, P);
                  const pb = B
                    ? P(B.centre.latitude, B.centre.longitude)
                    : reperePos(data, c.b, P);
                  if (!pa || !pb) return null;
                  return (
                    <line
                      key={i}
                      x1={pa[0]}
                      y1={pa[1]}
                      x2={pb[0]}
                      y2={pb[1]}
                      stroke="#3D9E7C"
                      strokeOpacity={0.28}
                      strokeWidth={0.8}
                    />
                  );
                })}

              {voirPoints &&
                data.noyaux.flatMap((n) =>
                  n.points.map((p, j) => {
                    const [x, y] = P(p.latitude, p.longitude);
                    return (
                      <circle
                        key={`${n.fichier}-${j}`}
                        cx={x}
                        cy={y}
                        r={1.6}
                        fill="#8B7EC8"
                        opacity={0.85}
                      />
                    );
                  })
                )}

              {data.reperes.map((r, i) => {
                const [x, y] = P(r.latitude, r.longitude);
                return (
                  <g key={`rep-${i}`}>
                    <circle cx={x} cy={y} r={4} fill="none" stroke="#6b7684" strokeWidth={1.2} />
                    <text x={x + 8} y={y + 3.5} fill="#8792a2" fontSize={9} fontFamily="monospace">
                      {r.nom}
                    </text>
                  </g>
                );
              })}

              {data.noyaux.map((n) => {
                const [x, y] = P(n.centre.latitude, n.centre.longitude);
                const actif = selection?.fichier === n.fichier;
                const col = n.discriminant ? '#D4943A' : '#3B8FD4';
                return (
                  <g
                    key={n.fichier}
                    onClick={() => setSelection(actif ? null : n)}
                    style={{ cursor: 'pointer' }}
                  >
                    <circle cx={x} cy={y} r={actif ? 9 : 6} fill={col} fillOpacity={0.22} />
                    <circle cx={x} cy={y} r={n.discriminant ? 4.2 : 3.2} fill={col} />
                    <text
                      x={x + 9}
                      y={y + 3.5}
                      fill={actif ? '#fff' : '#c3ccd7'}
                      fontSize={10}
                      fontFamily="monospace"
                    >
                      {n.titre.replace(/^Noyau (de |des |du |d')?/, '')}
                    </text>
                  </g>
                );
              })}
            </svg>
          </div>

          <p
            style={{
              marginTop: 12,
              fontSize: '0.82rem',
              lineHeight: 1.6,
              color: 'var(--ink-muted)',
            }}
          >
            <span style={{ color: '#D4943A' }}>●</span> noyau discriminant ·{' '}
            <span style={{ color: '#3B8FD4' }}>●</span> noyau non discriminant · cliquez un point
            pour le détail. La projection azimutale est le <em>modèle plan de référence</em> du
            projet, dessiné tel quel : elle n&apos;est pas une vue de la Terre mais l&apos;hypothèse
            à tester.
          </p>

          {selection && (
            <div style={{ ...bloc, marginTop: 16 }}>
              <h3 style={{ margin: '0 0 10px', fontSize: '1rem', color: 'var(--ink)' }}>
                {selection.titre}
              </h3>
              <dl style={dl}>
                <Ligne k="Points" v={`${selection.points.length}`} />
                <Ligne k="Liaisons" v={`${selection.liaisons} (graphe complet)`} />
                <Ligne k="Étendue" v={fmt(selection.etendueM)} />
                <Ligne k="Flèche sphérique" v={fmt(selection.flecheM)} />
                <Ligne k="Incertitude" v={`± ${selection.incertitudeM} m`} />
                <Ligne k="Signal / bruit" v={selection.signalSurBruit} />
                <Ligne
                  k="Étirement du modèle plan"
                  v={`× ${etirement(selection.centre.latitude).toFixed(3)} (lat ${selection.centre.latitude.toFixed(2)}°)`}
                />
              </dl>
              <p
                style={{
                  margin: '12px 0 0',
                  fontSize: '0.84rem',
                  color: selection.discriminant ? 'var(--saffron)' : 'var(--ink-muted)',
                }}
              >
                {selection.discriminant
                  ? "Étendue suffisante : une mesure de classe A faite ici aurait valeur de test."
                  : "Étendue trop faible : la flèche reste sous l'incertitude de position. Aucune mesure faite ici ne peut trancher."}
              </p>
            </div>
          )}
        </section>

        {/* ---------- panneau ---------- */}
        <aside style={{ display: 'grid', gap: 18 }}>
          <div style={bloc}>
            <h2 style={h2}>État du projet</h2>
            <dl style={dl}>
              <Ligne k="Noyaux clos" v={`${data.stats.noyaux}`} />
              <Ligne k="dont discriminants" v={`${data.stats.discriminants}`} />
              <Ligne k="Points relevés" v={`${data.stats.points}`} />
              <Ligne k="Distances calculées" v={`${data.stats.distances} (classe C)`} />
              <Ligne k="Cordes 3D ECEF" v={`${data.stats.cordes}`} />
              <Ligne k="Mesures de terrain" v={`${data.stats.mesures}`} fort />
            </dl>
            <p style={note}>
              Toutes les distances du dépôt sont <strong>calculées</strong> depuis des coordonnées
              WGS84. Elles restituent le modèle qui les a produites et ne peuvent pas le tester.
            </p>
          </div>

          <div style={{ ...bloc, borderColor: 'var(--saffron)' }}>
            <h2 style={{ ...h2, color: 'var(--saffron)' }}>Cible n°1</h2>
            <p style={{ margin: '0 0 10px', fontSize: '0.9rem', color: 'var(--ink)' }}>
              {cible1.a}
              <br />→ {cible1.b}
            </p>
            <dl style={dl}>
              <Ligne k="Azimut" v={`${cible1.azimut}°`} />
              <Ligne k="Modèle sphérique" v={fmt(cible1.spherique)} />
              <Ligne k="Modèle plan" v={fmt(cible1.plan)} />
              <Ligne k="Écart" v={`+${fmt(cible1.ecart)} (+${cible1.ecartPct} %)`} fort />
              <Ligne k="Classe exigée" v={cible1.classeExigee} />
            </dl>
            <p style={note}>{cible1.pourquoi}</p>
          </div>

          <div style={bloc}>
            <h2 style={h2}>Les cinq cibles</h2>
            <ol style={{ margin: 0, paddingLeft: 18, display: 'grid', gap: 10 }}>
              {data.cibles.map((c, i) => (
                <li key={i} style={{ fontSize: '0.82rem', color: 'var(--ink-soft)' }}>
                  <span style={{ color: 'var(--ink)' }}>
                    {c.a.replace(/ \(.*\)$/, '')} – {c.b.replace(/ \(.*\)$/, '')}
                  </span>
                  <br />
                  <span style={{ fontFamily: 'monospace', color: 'var(--ink-muted)' }}>
                    {fmt(c.spherique)} vs {fmt(c.plan)} · +{c.ecartPct} % · az {c.azimut}°
                  </span>
                </li>
              ))}
            </ol>
            <p style={note}>
              Prédictions consignées le 28 juillet 2026, avant toute mesure. Elles ne doivent plus
              être recalculées après réception d&apos;une mesure.
            </p>
          </div>

          <div style={bloc}>
            <h2 style={h2}>Pourquoi l&apos;azimut</h2>
            <p style={{ ...note, marginTop: 0 }}>
              Sur l&apos;azimutale équidistante polaire nord, les distances le long d&apos;un
              méridien sont exactes par construction. Celles le long d&apos;un parallèle sont
              multipliées par θ/sin θ, où θ est la colatitude — un facteur qui croît vers le sud.
            </p>
            <dl style={dl}>
              <Ligne k="Açores (38° N)" v="× 1,152" />
              <Ligne k="La Mecque (21° N)" v="× 1,286" />
              <Ligne k="Tahiti (17,5° S)" v="× 1,967" />
              <Ligne k="La Réunion (21,1° S)" v="× 2,078" />
              <Ligne k="Point Nemo (48,9° S)" v="× 3,686" />
            </dl>
            <p style={note}>
              Une base est-ouest de 6 km dans l&apos;hémisphère sud discrimine mieux qu&apos;une base
              de 66 km dans l&apos;hémisphère nord.
            </p>
          </div>
        </aside>
      </div>

      <style>{`
        @media (max-width: 900px) {
          .tei-carte-grid { grid-template-columns: 1fr !important; }
        }
      `}</style>
    </div>
  );
}

function reperePos(
  data: ReseauData,
  nom: string,
  P: (lat: number, lon: number) => [number, number]
): [number, number] | null {
  const r = data.reperes.find((x) => x.nom === nom);
  return r ? P(r.latitude, r.longitude) : null;
}

function Ligne({ k, v, fort }: { k: string; v: string; fort?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
      <dt style={{ fontSize: '0.8rem', color: 'var(--ink-muted)' }}>{k}</dt>
      <dd
        style={{
          margin: 0,
          fontSize: '0.8rem',
          fontFamily: 'monospace',
          color: fort ? 'var(--saffron)' : 'var(--ink)',
          textAlign: 'right',
        }}
      >
        {v}
      </dd>
    </div>
  );
}

const bloc: React.CSSProperties = {
  border: '1px solid var(--border)',
  borderRadius: 12,
  padding: '18px 20px',
  background: 'var(--card)',
};

const h2: React.CSSProperties = {
  margin: '0 0 12px',
  fontSize: '0.74rem',
  letterSpacing: '0.14em',
  textTransform: 'uppercase',
  color: 'var(--ink-muted)',
};

const dl: React.CSSProperties = { margin: 0, display: 'grid', gap: 7 };

const note: React.CSSProperties = {
  marginTop: 12,
  marginBottom: 0,
  fontSize: '0.78rem',
  lineHeight: 1.6,
  color: 'var(--ink-muted)',
};

const chk: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  fontSize: '0.78rem',
  color: 'var(--ink-soft)',
  cursor: 'pointer',
};
