'use client';

import { useCallback, useMemo, useRef, useState } from 'react';
import type { ReseauData, Noyau } from '@/lib/reseau';

type Projection = 'equirect' | 'azimutale';

const W = 2000;
const H = 1040;
const ZMIN = 0.6;
const ZMAX = 40;

/* ---------- projections ---------- */

function projEquirect(lat: number, lon: number): [number, number] {
  return [((lon + 180) / 360) * W, ((90 - lat) / 180) * H];
}

// Azimutale équidistante polaire nord : r ∝ colatitude, angle = longitude.
// C'est le modèle plan de référence du projet, dessiné tel qu'il est.
function projAzimutale(lat: number, lon: number): [number, number] {
  const cx = W / 2;
  const cy = H / 2;
  const rMax = H / 2 - 16;
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

function courtNom(titre: string): string {
  return titre.replace(/^Noyau (de la |de l'|des |du |de |d')?/i, '').split(' —')[0];
}

export default function CarteClient({ data }: { data: ReseauData }) {
  const [proj, setProj] = useState<Projection>('equirect');
  const [voirCordes, setVoirCordes] = useState(false);
  const [voirPoints, setVoirPoints] = useState(true);
  const [voirCibles, setVoirCibles] = useState(true);
  const [selection, setSelection] = useState<Noyau | null>(null);
  const [panneau, setPanneau] = useState(true);

  const [zoom, setZoom] = useState(1);
  const [pan, setPan] = useState<[number, number]>([0, 0]);
  const drag = useRef<{ x: number; y: number; px: number; py: number } | null>(null);
  const svgRef = useRef<SVGSVGElement | null>(null);

  const P = proj === 'equirect' ? projEquirect : projAzimutale;

  const centres = useMemo(
    () => new Map(data.noyaux.map((n) => [n.centre.nom, n])),
    [data.noyaux]
  );

  /* ---------- zoom / pan ---------- */

  const clampPan = useCallback((x: number, y: number, z: number): [number, number] => {
    const mx = (W * (z - 1)) / 2 + W * 0.15;
    const my = (H * (z - 1)) / 2 + H * 0.15;
    return [Math.max(-mx, Math.min(mx, x)), Math.max(-my, Math.min(my, y))];
  }, []);

  const zoomVers = useCallback(
    (facteur: number, cx?: number, cy?: number) => {
      setZoom((z0) => {
        const z = Math.max(ZMIN, Math.min(ZMAX, z0 * facteur));
        const k = z / z0;
        setPan(([px, py]) => {
          const ax = cx ?? W / 2;
          const ay = cy ?? H / 2;
          return clampPan(ax - (ax - px) * k, ay - (ay - py) * k, z);
        });
        return z;
      });
    },
    [clampPan]
  );

  const surMolette = useCallback(
    (e: React.WheelEvent<SVGSVGElement>) => {
      e.preventDefault();
      const svg = svgRef.current;
      if (!svg) return;
      const r = svg.getBoundingClientRect();
      const ax = ((e.clientX - r.left) / r.width) * W;
      const ay = ((e.clientY - r.top) / r.height) * H;
      zoomVers(e.deltaY < 0 ? 1.18 : 1 / 1.18, ax, ay);
    },
    [zoomVers]
  );

  const debutDrag = (e: React.PointerEvent<SVGSVGElement>) => {
    (e.target as Element).setPointerCapture?.(e.pointerId);
    drag.current = { x: e.clientX, y: e.clientY, px: pan[0], py: pan[1] };
  };
  const pendantDrag = (e: React.PointerEvent<SVGSVGElement>) => {
    if (!drag.current || !svgRef.current) return;
    const r = svgRef.current.getBoundingClientRect();
    const dx = ((e.clientX - drag.current.x) / r.width) * W;
    const dy = ((e.clientY - drag.current.y) / r.height) * H;
    setPan(clampPan(drag.current.px + dx, drag.current.py + dy, zoom));
  };
  const finDrag = () => {
    drag.current = null;
  };

  const reset = () => {
    setZoom(1);
    setPan([0, 0]);
  };

  const allerA = (lat: number, lon: number, z = 8) => {
    const [x, y] = P(lat, lon);
    setZoom(z);
    setPan(clampPan(W / 2 - x * z, H / 2 - y * z, z));
  };

  /* ---------- échelles adaptatives ---------- */

  const s = 1 / zoom; // épaisseurs et rayons constants à l'écran
  const labelSeuil = zoom;

  const grille = useMemo(() => {
    const lignes: { d: string; fort: boolean }[] = [];
    if (proj === 'equirect') {
      for (let lon = -180; lon <= 180; lon += 15) {
        const [x1, y1] = P(90, lon);
        const [x2, y2] = P(-90, lon);
        lignes.push({ d: `M${x1},${y1}L${x2},${y2}`, fort: lon === 0 });
      }
      for (let lat = -75; lat <= 75; lat += 15) {
        const [x1, y1] = P(lat, -180);
        const [x2, y2] = P(lat, 180);
        lignes.push({ d: `M${x1},${y1}L${x2},${y2}`, fort: lat === 0 });
      }
    } else {
      for (let lon = -180; lon < 180; lon += 15) {
        const [x1, y1] = P(90, lon);
        const [x2, y2] = P(-90, lon);
        lignes.push({ d: `M${x1},${y1}L${x2},${y2}`, fort: lon === 0 });
      }
      for (let lat = 75; lat >= -75; lat -= 15) {
        const pts: string[] = [];
        for (let lon = -180; lon <= 180; lon += 4) {
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
    <div style={{ background: 'var(--bg)' }}>
      {/* ---------- bandeau ---------- */}
      <div
        style={{
          padding: '112px 24px 18px',
          maxWidth: 1600,
          margin: '0 auto',
        }}
      >
        <h1
          style={{
            fontSize: 'clamp(1.7rem, 3.4vw, 2.6rem)',
            lineHeight: 1.1,
            margin: 0,
            color: 'var(--ink)',
          }}
        >
          La carte du réseau
        </h1>
        <p
          style={{
            marginTop: 10,
            marginBottom: 0,
            maxWidth: '80ch',
            fontSize: '0.96rem',
            lineHeight: 1.6,
            color: 'var(--ink-soft)',
          }}
        >
          {data.stats.noyaux} noyaux géodésiques clos, {data.stats.points} points,{' '}
          {data.stats.distances} distances calculées, <strong>zéro mesure de terrain</strong>.
          Basculez entre les deux modèles : les points nordiques bougent à peine, les austraux
          s&apos;écartent massivement. C&apos;est tout le sujet.
        </p>
      </div>

      {/* ---------- barre d'outils ---------- */}
      <div
        style={{
          position: 'sticky',
          top: 0,
          zIndex: 20,
          background: 'var(--bg)',
          borderBottom: '1px solid var(--border)',
          padding: '10px 24px',
        }}
      >
        <div
          style={{
            maxWidth: 1600,
            margin: '0 auto',
            display: 'flex',
            flexWrap: 'wrap',
            gap: 8,
            alignItems: 'center',
          }}
        >
          {(
            [
              ['equirect', 'Équirectangulaire (WGS84)'],
              ['azimutale', 'Azimutale polaire nord (modèle plan)'],
            ] as [Projection, string][]
          ).map(([k, label]) => (
            <button
              key={k}
              onClick={() => {
                setProj(k);
                reset();
              }}
              style={{
                padding: '8px 14px',
                borderRadius: 8,
                border: `1px solid ${proj === k ? 'var(--opal)' : 'var(--border)'}`,
                background: proj === k ? 'var(--opal)' : 'transparent',
                color: proj === k ? '#fff' : 'var(--ink-soft)',
                fontSize: '0.8rem',
                cursor: 'pointer',
                fontFamily: 'inherit',
              }}
            >
              {label}
            </button>
          ))}

          <span style={{ width: 14 }} />

          <button onClick={() => zoomVers(1.4)} style={btn} aria-label="Zoom avant">
            +
          </button>
          <button onClick={() => zoomVers(1 / 1.4)} style={btn} aria-label="Zoom arrière">
            −
          </button>
          <button onClick={reset} style={{ ...btn, width: 'auto', padding: '0 12px' }}>
            Réinitialiser
          </button>
          <span
            style={{
              fontFamily: 'monospace',
              fontSize: '0.74rem',
              color: 'var(--ink-muted)',
              minWidth: 52,
            }}
          >
            ×{zoom.toFixed(1)}
          </span>

          <span style={{ flex: 1 }} />

          <label style={chk}>
            <input
              type="checkbox"
              checked={voirPoints}
              onChange={(e) => setVoirPoints(e.target.checked)}
            />
            Les {data.stats.points} points
          </label>
          <label style={chk}>
            <input
              type="checkbox"
              checked={voirCibles}
              onChange={(e) => setVoirCibles(e.target.checked)}
            />
            Cibles
          </label>
          <label style={chk}>
            <input
              type="checkbox"
              checked={voirCordes}
              onChange={(e) => setVoirCordes(e.target.checked)}
            />
            {data.stats.cordes} cordes
          </label>
          <button onClick={() => setPanneau((v) => !v)} style={{ ...btn, width: 'auto', padding: '0 12px' }}>
            {panneau ? 'Masquer le panneau' : 'Afficher le panneau'}
          </button>
        </div>
      </div>

      {/* ---------- carte plein format ---------- */}
      <div style={{ position: 'relative', width: '100%', height: '82vh', background: '#0d1117' }}>
        <svg
          ref={svgRef}
          viewBox={`0 0 ${W} ${H}`}
          preserveAspectRatio="xMidYMid meet"
          onWheel={surMolette}
          onPointerDown={debutDrag}
          onPointerMove={pendantDrag}
          onPointerUp={finDrag}
          onPointerLeave={finDrag}
          style={{
            display: 'block',
            width: '100%',
            height: '100%',
            cursor: drag.current ? 'grabbing' : 'grab',
            touchAction: 'none',
          }}
        >
          <rect width={W} height={H} fill="#0d1117" />

          <g transform={`translate(${pan[0]},${pan[1]}) scale(${zoom})`}>
            {grille.map((g, i) => (
              <path
                key={i}
                d={g.d}
                fill="none"
                stroke={g.fort ? '#33424f' : '#1b2530'}
                strokeWidth={(g.fort ? 1.4 : 0.8) * s}
              />
            ))}

            {voirCordes &&
              data.cordes.map((c, i) => {
                const pa = posDe(data, centres, c.a, P);
                const pb = posDe(data, centres, c.b, P);
                if (!pa || !pb) return null;
                return (
                  <line
                    key={i}
                    x1={pa[0]}
                    y1={pa[1]}
                    x2={pb[0]}
                    y2={pb[1]}
                    stroke="#3D9E7C"
                    strokeOpacity={0.18}
                    strokeWidth={0.9 * s}
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
                      r={2.2 * s}
                      fill="#8B7EC8"
                      opacity={0.9}
                    />
                  );
                })
              )}

            {voirCibles &&
              data.cibles.map((c, i) => {
                const [x1, y1] = P(c.aLat, c.aLon);
                const [x2, y2] = P(c.bLat, c.bLon);
                return (
                  <g key={`cible-${i}`}>
                    <line
                      x1={x1}
                      y1={y1}
                      x2={x2}
                      y2={y2}
                      stroke="#D4943A"
                      strokeWidth={2.4 * s}
                      strokeLinecap="round"
                    />
                    <circle
                      cx={(x1 + x2) / 2}
                      cy={(y1 + y2) / 2}
                      r={7 * s}
                      fill="#D4943A"
                      fillOpacity={0.16}
                      stroke="#D4943A"
                      strokeWidth={1.1 * s}
                    />
                    <text
                      x={(x1 + x2) / 2}
                      y={(y1 + y2) / 2 + 3 * s}
                      fill="#D4943A"
                      fontSize={9 * s}
                      fontFamily="monospace"
                      textAnchor="middle"
                    >
                      {c.rang}
                    </text>
                  </g>
                );
              })}

            {data.reperes.map((r, i) => {
              const [x, y] = P(r.latitude, r.longitude);
              return (
                <g key={`rep-${i}`}>
                  <circle
                    cx={x}
                    cy={y}
                    r={5 * s}
                    fill="none"
                    stroke="#6b7684"
                    strokeWidth={1.4 * s}
                  />
                  <text
                    x={x + 9 * s}
                    y={y + 3.5 * s}
                    fill="#8792a2"
                    fontSize={11 * s}
                    fontFamily="monospace"
                  >
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
                  onClick={(e) => {
                    e.stopPropagation();
                    setSelection(actif ? null : n);
                  }}
                  style={{ cursor: 'pointer' }}
                >
                  <circle cx={x} cy={y} r={(actif ? 11 : 7) * s} fill={col} fillOpacity={0.24} />
                  <circle cx={x} cy={y} r={(n.discriminant ? 4.4 : 3.4) * s} fill={col} />
                  {(labelSeuil > 0.9 || n.discriminant) && (
                    <text
                      x={x + 9 * s}
                      y={y + 4 * s}
                      fill={actif ? '#fff' : '#cbd4de'}
                      fontSize={12 * s}
                      fontFamily="monospace"
                      style={{ paintOrder: 'stroke', stroke: '#0d1117', strokeWidth: 3 * s }}
                    >
                      {courtNom(n.titre)}
                    </text>
                  )}
                </g>
              );
            })}
          </g>
        </svg>

        {/* légende flottante */}
        <div
          style={{
            position: 'absolute',
            left: 16,
            bottom: 16,
            padding: '10px 14px',
            borderRadius: 10,
            background: 'rgba(13,17,23,0.86)',
            border: '1px solid #22303c',
            fontSize: '0.74rem',
            lineHeight: 1.7,
            color: '#9aa7b5',
            pointerEvents: 'none',
          }}
        >
          <div>
            <span style={{ color: '#D4943A' }}>●</span> noyau discriminant ({data.stats.discriminants}
            )
          </div>
          <div>
            <span style={{ color: '#3B8FD4' }}>●</span> non discriminant (
            {data.stats.noyaux - data.stats.discriminants})
          </div>
          <div>
            <span style={{ color: '#D4943A' }}>▬</span> cible pré-enregistrée
          </div>
          <div style={{ marginTop: 4, color: '#6b7684' }}>
            molette : zoom · glisser : déplacer
          </div>
        </div>

        {/* fiche noyau flottante */}
        {selection && (
          <div
            style={{
              position: 'absolute',
              right: panneau ? 372 : 16,
              top: 16,
              width: 300,
              maxHeight: 'calc(100% - 32px)',
              overflowY: 'auto',
              padding: '16px 18px',
              borderRadius: 12,
              background: 'rgba(13,17,23,0.94)',
              border: `1px solid ${selection.discriminant ? '#D4943A' : '#22303c'}`,
            }}
          >
            <button
              onClick={() => setSelection(null)}
              style={{
                float: 'right',
                background: 'none',
                border: 'none',
                color: '#6b7684',
                cursor: 'pointer',
                fontSize: '1rem',
                lineHeight: 1,
              }}
              aria-label="Fermer"
            >
              ×
            </button>
            <h3 style={{ margin: '0 0 12px', fontSize: '0.98rem', color: '#e6edf3' }}>
              {courtNom(selection.titre)}
            </h3>
            <dl style={dlSombre}>
              <L k="Points" v={`${selection.points.length}`} />
              <L k="Liaisons" v={`${selection.liaisons} (K${selection.points.length})`} />
              <L k="Étendue" v={fmt(selection.etendueM)} />
              <L k="Flèche sphérique" v={fmt(selection.flecheM)} />
              <L k="Incertitude" v={`± ${selection.incertitudeM} m`} />
              <L k="Latitude" v={`${selection.centre.latitude.toFixed(2)}°`} />
              <L k="Étirement du plan" v={`× ${selection.etirement.toFixed(3)}`} />
              <L k="Écart entre modèles" v={`+${selection.ecartMaxPct} %`} fort />
            </dl>
            <p
              style={{
                margin: '12px 0 0',
                fontSize: '0.78rem',
                lineHeight: 1.55,
                color: selection.discriminant ? '#D4943A' : '#7d8794',
              }}
            >
              {selection.discriminant
                ? `Discriminant : sur sa meilleure paire, le modèle plan s'écarte de ${selection.ecartMaxPct} % du modèle sphérique. Une mesure de classe A faite ici trancherait.`
                : `Non discriminant : ${selection.ecartMaxPct} % d'écart maximal entre les deux modèles. Trop peu pour trancher, quelle que soit la précision de la mesure. C'est la latitude qui l'impose, pas la qualité du relevé.`}
            </p>
            <button
              onClick={() => allerA(selection.centre.latitude, selection.centre.longitude, 12)}
              style={{ ...btn, width: '100%', marginTop: 12, height: 32 }}
            >
              Centrer et zoomer
            </button>
          </div>
        )}

        {/* panneau latéral rétractable */}
        {panneau && (
          <aside
            style={{
              position: 'absolute',
              right: 0,
              top: 0,
              bottom: 0,
              width: 356,
              overflowY: 'auto',
              padding: '18px 20px 28px',
              background: 'rgba(13,17,23,0.94)',
              borderLeft: '1px solid #22303c',
              display: 'grid',
              gap: 16,
              alignContent: 'start',
            }}
          >
            <div style={blocSombre}>
              <h2 style={h2}>État du projet</h2>
              <dl style={dlSombre}>
                <L k="Noyaux clos" v={`${data.stats.noyaux}`} />
                <L k="dont discriminants" v={`${data.stats.discriminants}`} />
                <L k="Points relevés" v={`${data.stats.points}`} />
                <L k="Distances calculées" v={`${data.stats.distances}`} />
                <L k="Cordes 3D ECEF" v={`${data.stats.cordes}`} />
                <L k="Mesures de terrain" v={`${data.stats.mesures}`} fort />
              </dl>
              <p style={note}>
                Toutes ces distances sont <strong>calculées</strong> depuis des coordonnées WGS84.
                Elles restituent le modèle qui les a produites et ne peuvent pas le tester.
              </p>
            </div>

            <div style={{ ...blocSombre, borderColor: '#D4943A' }}>
              <h2 style={{ ...h2, color: '#D4943A' }}>Cible n°1 — {cible1.lieu}</h2>
              <p style={{ margin: '0 0 10px', fontSize: '0.86rem', color: '#e6edf3' }}>
                {cible1.a}
                <br />→ {cible1.b}
              </p>
              <dl style={dlSombre}>
                <L k="Azimut" v={`${cible1.azimut}°`} />
                <L k="Modèle sphérique" v={fmt(cible1.spherique)} />
                <L k="Modèle plan" v={fmt(cible1.plan)} />
                <L k="Écart" v={`+${cible1.ecartPct} %`} fort />
                <L k="Classe exigée" v={cible1.classeExigee} />
              </dl>
              <button
                onClick={() => allerA((cible1.aLat + cible1.bLat) / 2, (cible1.aLon + cible1.bLon) / 2, 16)}
                style={{ ...btn, width: '100%', marginTop: 12, height: 32 }}
              >
                Voir sur la carte
              </button>
              <p style={note}>{cible1.accessibilite}</p>
            </div>

            <div style={blocSombre}>
              <h2 style={h2}>Les {data.cibles.length} cibles</h2>
              <ol style={{ margin: 0, paddingLeft: 20, display: 'grid', gap: 11 }}>
                {data.cibles.map((c) => (
                  <li key={c.rang} style={{ fontSize: '0.78rem', color: '#9aa7b5' }}>
                    <button
                      onClick={() => allerA((c.aLat + c.bLat) / 2, (c.aLon + c.bLon) / 2, 16)}
                      style={lien}
                    >
                      {c.a.replace(/ \(.*\)$/, '')} – {c.b.replace(/ \(.*\)$/, '')}
                    </button>
                    <br />
                    <span style={{ fontFamily: 'monospace', color: '#6b7684' }}>
                      {fmt(c.spherique)} → {fmt(c.plan)} · +{c.ecartPct} % · az {c.azimut}°
                    </span>
                  </li>
                ))}
              </ol>
              <p style={note}>
                Prédictions consignées le 28 juillet 2026, avant toute mesure. Elles ne doivent plus
                être recalculées ensuite.
              </p>
            </div>

            <div style={blocSombre}>
              <h2 style={h2}>Étirement par latitude</h2>
              <p style={{ ...note, marginTop: 0 }}>
                Sur l&apos;azimutale polaire nord, une paire est-ouest est multipliée par θ/sin θ
                (θ = colatitude). Ce facteur vaut 1 au pôle Nord et croît sans borne vers le sud.
              </p>
              <dl style={dlSombre}>
                {data.etirement.slice(0, 6).map((e) => (
                  <L key={e.lieu} k={`${e.lieu} (${e.latitude.toFixed(1)}°)`} v={`× ${e.facteur.toFixed(3)}`} />
                ))}
                <L k="…" v="" />
                {data.etirement.slice(-3).map((e) => (
                  <L key={e.lieu} k={`${e.lieu} (${e.latitude.toFixed(1)}°)`} v={`× ${e.facteur.toFixed(3)}`} />
                ))}
              </dl>
              <p style={note}>
                Une base est-ouest de 1 km à Buenos Aires discrimine plus qu&apos;une base de 44 km à
                Reykjavík. La longueur ne décide de rien ; la latitude et l&apos;azimut décident de
                tout.
              </p>
            </div>
          </aside>
        )}
      </div>

      <div style={{ maxWidth: 1600, margin: '0 auto', padding: '20px 24px 80px' }}>
        <p style={{ fontSize: '0.82rem', lineHeight: 1.7, color: 'var(--ink-muted)', margin: 0 }}>
          Aucune tuile distante, aucune dépendance cartographique : les deux projections sont
          dessinées à égalité sur une grille nue. Un fond de carte Web Mercator aurait tranché
          visuellement la question avant qu&apos;on la pose, puisqu&apos;il dérive lui-même de
          l&apos;ellipsoïde WGS84. Données lues directement depuis{' '}
          <code>content/reseau/</code>.
        </p>
      </div>
    </div>
  );
}

function posDe(
  data: ReseauData,
  centres: Map<string, Noyau>,
  nom: string,
  P: (lat: number, lon: number) => [number, number]
): [number, number] | null {
  const n = centres.get(nom);
  if (n) return P(n.centre.latitude, n.centre.longitude);
  const r = data.reperes.find((x) => x.nom === nom);
  return r ? P(r.latitude, r.longitude) : null;
}

function L({ k, v, fort }: { k: string; v: string; fort?: boolean }) {
  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', gap: 12 }}>
      <dt style={{ fontSize: '0.76rem', color: '#7d8794' }}>{k}</dt>
      <dd
        style={{
          margin: 0,
          fontSize: '0.76rem',
          fontFamily: 'monospace',
          color: fort ? '#D4943A' : '#dbe3ea',
          textAlign: 'right',
        }}
      >
        {v}
      </dd>
    </div>
  );
}

const blocSombre: React.CSSProperties = {
  border: '1px solid #22303c',
  borderRadius: 12,
  padding: '16px 18px',
  background: 'rgba(22,27,34,0.7)',
};

const h2: React.CSSProperties = {
  margin: '0 0 12px',
  fontSize: '0.72rem',
  letterSpacing: '0.14em',
  textTransform: 'uppercase',
  color: '#7d8794',
};

const dlSombre: React.CSSProperties = { margin: 0, display: 'grid', gap: 7 };

const note: React.CSSProperties = {
  marginTop: 12,
  marginBottom: 0,
  fontSize: '0.75rem',
  lineHeight: 1.6,
  color: '#7d8794',
};

const chk: React.CSSProperties = {
  display: 'inline-flex',
  alignItems: 'center',
  gap: 6,
  fontSize: '0.76rem',
  color: 'var(--ink-soft)',
  cursor: 'pointer',
};

const btn: React.CSSProperties = {
  height: 34,
  minWidth: 34,
  borderRadius: 8,
  border: '1px solid var(--border)',
  background: 'transparent',
  color: 'var(--ink-soft)',
  fontSize: '0.82rem',
  cursor: 'pointer',
  fontFamily: 'inherit',
};

const lien: React.CSSProperties = {
  background: 'none',
  border: 'none',
  padding: 0,
  color: '#dbe3ea',
  fontSize: '0.78rem',
  fontFamily: 'inherit',
  textAlign: 'left',
  cursor: 'pointer',
  textDecoration: 'underline',
  textDecorationColor: '#3a4854',
};
