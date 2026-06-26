'use client';
import { useState, useMemo } from 'react';
import { Line, Html } from '@react-three/drei';
import * as THREE from 'three';
import { LengthField, PlainField } from './ui/Field';
import { Canvas3D, Marker } from './ui/scene3d';

const R_EARTH = 6371;

function curvatureBulge(dist: number): number {
  return (dist ** 2) / (2 * R_EARTH);
}

/** Coefficient de réfraction k depuis les conditions atmosphériques.
 *  Formule géodésique standard : k ≈ 503·P/T² · (0.0342 + dT/dh)
 *  avec P en hPa, T en Kelvin, dT/dh en °C/m (gradient thermique vertical).
 *  Gradient standard −6.5 °C/km → k ≈ 0.13–0.17 selon la température. */
function refractionK(tempC: number, gradCPerKm: number, pressureHpa = 1013): number {
  const T = tempC + 273.15;
  const dTdh = gradCPerKm / 1000; // °C/m
  const k = 503 * pressureHpa / (T * T) * (0.0342 + dTdh);
  return Math.max(-0.5, Math.min(1.2, k));
}

/** Déviation verticale du rayon laser due à la réfraction à la distance d (km) :
 *  le rayon suit un arc de rayon R_ray = R_earth/k → flèche δ = d²·k/(2·R_earth).
 *  k > 0 : le rayon se courbe VERS la surface (réduit l'écart apparent). */
function laserRefractionDrop(dist: number, k: number): number {
  return (dist ** 2) * k / (2 * R_EARTH);
}

const PRESETS = [
  {
    label: 'Bedford Level (10 km)',
    d: 10, laserH: 1.5, targets: [2, 4, 6, 8, 10],
    desc: 'Expérience classique d\'Alfred Russel Wallace (1870) sur le canal Old Bedford, Norfolk.',
  },
  {
    label: 'Lac Pontchartrain (30 km)',
    d: 30, laserH: 0.5, targets: [5, 10, 15, 20, 25, 30],
    desc: 'Pylônes de transmission traversant le lac en Louisiane. Souvent filmé avec zoom.',
  },
  {
    label: 'Test laser 5 km',
    d: 5, laserH: 1.0, targets: [1, 2, 3, 4, 5],
    desc: 'Expérience laser courte distance. Chute attendue : 1.96 m sur 5 km.',
  },
  {
    label: 'Grand lac salé (20 km)',
    d: 20, laserH: 0.3, targets: [4, 8, 12, 16, 20],
    desc: 'Test sur surface saline parfaitement plate. Utah, USA.',
  },
];

function Scene({ dist, laserH, targets, k }: { dist: number; laserH: number; targets: number[]; k: number }) {
  const scale = 12 / Math.max(dist, 5);
  const hScale = scale * 800;
  const halfD = (dist / 2) * scale;

  // Trajectoire du laser réfracté (modèle globe) : arc qui plonge de d²k/2R
  const refractedPts = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= 100; i++) {
      const dKm = (i / 100) * dist;
      const x = -halfD + (i / 100) * (halfD * 2);
      const y = laserH * hScale - laserRefractionDrop(dKm, k) * hScale;
      pts.push(new THREE.Vector3(x, y, 0));
    }
    return pts;
  }, [dist, halfD, laserH, hScale, k]);

  const waterPts = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= 200; i++) {
      const x = -halfD + (i / 200) * (halfD * 2);
      pts.push(new THREE.Vector3(x, 0, 0));
    }
    return pts;
  }, [halfD]);

  const curvedWaterPts = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= 200; i++) {
      const x = -halfD + (i / 200) * (halfD * 2);
      const dFromCenter = Math.abs(x / scale);
      const bulge = curvatureBulge(dFromCenter) * hScale;
      pts.push(new THREE.Vector3(x, -bulge, 0));
    }
    return pts;
  }, [halfD, scale, hScale]);

  return <>
    {/* ── MODÈLE PLAN (haut) ── */}
    <group position={[0, 3, 0]}>
      <Html position={[0, 2, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#00E87B', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.12em', fontWeight: 'bold' }}>
          EAU PLATE — Laser droit
        </div>
      </Html>
      {/* Surface d'eau */}
      <Line points={waterPts} color="#4488CC" lineWidth={2} />
      {/* Fond d'eau */}
      <mesh position={[0, -0.15, 0]}>
        <planeGeometry args={[halfD * 2 + 1, 0.3]} />
        <meshBasicMaterial color="#4488CC" transparent opacity={0.08} />
      </mesh>
      {/* Laser */}
      <Line points={[
        new THREE.Vector3(-halfD, laserH * hScale, 0),
        new THREE.Vector3(halfD, laserH * hScale, 0),
      ]} color="#FF0000" lineWidth={2} />
      {/* Glow du laser */}
      <Line points={[
        new THREE.Vector3(-halfD, laserH * hScale, 0),
        new THREE.Vector3(halfD, laserH * hScale, 0),
      ]} color="#FF4444" lineWidth={6} opacity={0.15} transparent />
      {/* Source */}
      <Marker position={[-halfD, laserH * hScale, 0]} r={0.08} color="#FF0000" />
      {/* Cibles */}
      {targets.map(t => {
        const x = -halfD + (t / dist) * halfD * 2;
        return (
          <group key={t}>
            <Line points={[new THREE.Vector3(x, 0, 0), new THREE.Vector3(x, laserH * hScale + 0.3, 0)]}
              color="#D4A843" lineWidth={1.5} />
            <mesh position={[x, laserH * hScale, 0]}>
              <circleGeometry args={[0.06, 16]} />
              <meshBasicMaterial color="#00E87B" />
            </mesh>
            <Html position={[x, -0.4, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
              <div style={{ color: '#607890', fontSize: '8px', fontFamily: 'monospace' }}>{t} km</div>
            </Html>
          </group>
        );
      })}
      <Html position={[halfD + 0.5, laserH * hScale, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#00E87B', fontSize: '9px', fontFamily: 'monospace' }}>
          touche à {(laserH * 1000).toFixed(0)} mm
        </div>
      </Html>
    </group>

    {/* ── MODÈLE GLOBE (bas) ── */}
    <group position={[0, -3, 0]}>
      <Html position={[0, 2, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#00C8FF', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.12em', fontWeight: 'bold' }}>
          EAU COURBÉE — Laser monte
        </div>
      </Html>
      {/* Surface courbée */}
      <Line points={curvedWaterPts} color="#4488CC" lineWidth={2} />
      {/* Laser géométrique droit (théorique, sans réfraction) */}
      <Line points={[
        new THREE.Vector3(-halfD, laserH * hScale, 0),
        new THREE.Vector3(halfD, laserH * hScale, 0),
      ]} color="#FF8888" lineWidth={1} opacity={0.35} transparent dashed dashSize={0.08} gapSize={0.05} />
      {/* Laser réfracté (trajectoire réelle, courbée vers la surface) */}
      <Line points={refractedPts} color="#FF0000" lineWidth={2} />
      <Line points={refractedPts} color="#FF4444" lineWidth={6} opacity={0.15} transparent />
      <Html position={[halfD * 0.6, laserH * hScale + 0.4, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#FF8888', fontSize: '7px', fontFamily: 'monospace' }}>
          pointillé = droit · plein = réfracté (k={k.toFixed(2)})
        </div>
      </Html>
      {/* Source */}
      <Marker position={[-halfD, laserH * hScale, 0]} r={0.08} color="#FF0000" />
      {/* Cibles + écart */}
      {targets.map(t => {
        const x = -halfD + (t / dist) * halfD * 2;
        const bulge = curvatureBulge(t) * hScale;
        const laserAtTarget = laserH * hScale;
        const surfaceAtTarget = -bulge;
        return (
          <group key={t}>
            <Line points={[new THREE.Vector3(x, surfaceAtTarget, 0), new THREE.Vector3(x, laserAtTarget + 0.3, 0)]}
              color="#D4A843" lineWidth={1.5} />
            {/* Point de visée laser */}
            <mesh position={[x, laserAtTarget, 0]}>
              <circleGeometry args={[0.06, 16]} />
              <meshBasicMaterial color="#FF4444" />
            </mesh>
            {/* Écart laser-surface */}
            {bulge > 0.001 && (
              <Html position={[x, (laserAtTarget + surfaceAtTarget) / 2, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
                <div style={{ color: '#FF4444', fontSize: '7px', fontFamily: 'monospace' }}>
                  +{(curvatureBulge(t) * 1000).toFixed(1)} m
                </div>
              </Html>
            )}
          </group>
        );
      })}
    </group>
  </>;
}

export default function LaserLakeSim() {
  const [dist, setDist] = useState(10);
  const [laserH, setLaserH] = useState(1.5);
  const [numTargets, setNumTargets] = useState(5);
  const [tempC, setTempC] = useState(15);
  const [gradC, setGradC] = useState(-6.5);

  const k = refractionK(tempC, gradC);

  const targets = useMemo(() => {
    const t: number[] = [];
    for (let i = 1; i <= numTargets; i++) {
      t.push(Math.round((i / numTargets) * dist * 10) / 10);
    }
    return t;
  }, [dist, numTargets]);

  const maxBulge = curvatureBulge(dist);
  const maxBulgeRefracted = Math.max(0, maxBulge - laserRefractionDrop(dist, k));

  return <div className="w-full">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <LengthField label="Distance totale" value={dist} onChange={setDist} canonical="km" units={['km','m']} min={1} max={50} accent="#00C8FF" hint="Longueur du plan d'eau visé par le laser." />
      <LengthField label="Hauteur du laser" value={laserH} onChange={setLaserH} canonical="m" units={['m','cm']} min={0.1} max={5} accent="#FF4444" hint="Hauteur du laser au-dessus de l'eau." />
      <PlainField label="Nombre de cibles" value={numTargets} onChange={v=>setNumTargets(Math.round(v))} min={2} max={10} unit="cibles" accent="#D4A843" hint="Nombre de jalons répartis sur la distance." />
    </div>

    {/* Conditions atmosphériques */}
    <div className="border border-[#D4A843]/30 bg-[#0A1020] p-4 mb-4">
      <div className="text-[11px] font-tech-mono text-[#D4A843] tracking-widest mb-3">
        CONDITIONS ATMOSPHÉRIQUES → k = {k.toFixed(3)} (R_rayon = {k > 0.001 ? `${Math.round(R_EARTH / k).toLocaleString('fr-FR')} km` : '∞'})
      </div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
        <PlainField label="Température (T₀)" value={tempC} onChange={setTempC} min={5} max={40} unit="°C" accent="#D4A843" compact hint="Température de l'air au niveau de l'eau." />
        <PlainField label="Gradient ΔT/Δh" value={gradC} onChange={setGradC} min={-10} max={10} unit="°C/km" accent="#D4A843" compact hint="Variation de température avec l'altitude." />
      </div>
      <div className="flex flex-wrap gap-2 mt-3">
        <button onClick={() => { setTempC(15); setGradC(-6.5); }} className="px-3 py-2 md:py-1 text-[11px] md:text-[9px] font-tech-mono border border-slate-600 text-slate-400 hover:text-white">Standard (k≈0.13)</button>
        <button onClick={() => { setTempC(10); setGradC(0); }} className="px-3 py-2 md:py-1 text-[11px] md:text-[9px] font-tech-mono border border-[#D4A843]/40 text-[#D4A843] hover:bg-[#D4A843]/10">Eau froide / inversion légère</button>
        <button onClick={() => { setTempC(8); setGradC(8); }} className="px-3 py-2 md:py-1 text-[11px] md:text-[9px] font-tech-mono border border-red-700/40 text-red-400 hover:bg-red-400/10">Forte inversion (super-réfraction)</button>
      </div>
    </div>

    {/* Presets */}
    <div className="mb-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-2">
      {PRESETS.map(p => (
        <button key={p.label} onClick={() => { setDist(p.d); setLaserH(p.laserH); setNumTargets(p.targets.length); }}
          className="border border-slate-700 bg-[#0A1020] p-3 text-left hover:border-[#FF4444]/50 transition-all group">
          <div className="text-[11px] font-tech-mono text-slate-200 group-hover:text-[#FF4444] font-bold">{p.label}</div>
          <div className="text-[9px] font-tech-mono text-slate-500 mt-1">{p.desc}</div>
        </button>
      ))}
    </div>

    {/* Canvas 3D */}
    <Canvas3D accent="#FF4444" controlsProps={{ enablePan: true, enableZoom: true, maxDistance: 20, minDistance: 3 }}>
      <Scene dist={dist} laserH={laserH} targets={targets} k={k} />
    </Canvas3D>

    {/* Tableau des écarts */}
    <div className="mt-4 overflow-x-auto">
      <table className="w-full border-collapse">
        <thead>
          <tr className="border-b border-slate-800">
            <th className="text-[10px] font-tech-mono text-slate-500 px-3 py-2 text-left">DISTANCE</th>
            <th className="text-[10px] font-tech-mono text-slate-500 px-3 py-2 text-right">CHUTE COURBURE</th>
            <th className="text-[10px] font-tech-mono text-slate-500 px-3 py-2 text-right">ÉCART GÉOMÉTRIQUE</th>
            <th className="text-[10px] font-tech-mono text-slate-500 px-3 py-2 text-right">ÉCART AVEC RÉFRACTION</th>
            <th className="text-[10px] font-tech-mono text-slate-500 px-3 py-2 text-right">VERDICT GLOBE</th>
          </tr>
        </thead>
        <tbody>
          {targets.map(t => {
            const bulge = curvatureBulge(t);
            const bulgeM = bulge * 1000;
            const refractedGapM = Math.max(0, (bulge - laserRefractionDrop(t, k)) * 1000);
            const laserAbove = bulgeM > 0;
            return (
              <tr key={t} className="border-b border-slate-800/30">
                <td className="text-[11px] font-tech-mono text-[#00C8FF] px-3 py-2">{t} km</td>
                <td className="text-[11px] font-tech-mono text-amber-400 px-3 py-2 text-right">
                  {bulgeM >= 1 ? `${bulgeM.toFixed(1)} m` : `${(bulgeM * 100).toFixed(1)} cm`}
                </td>
                <td className="text-[11px] font-tech-mono px-3 py-2 text-right" style={{ color: laserAbove ? '#FF4444' : '#00E87B' }}>
                  {laserAbove ? `+${bulgeM.toFixed(1)} m` : 'sur la cible'}
                </td>
                <td className="text-[11px] font-tech-mono px-3 py-2 text-right" style={{ color: refractedGapM > 0.5 ? '#FF8888' : '#00E87B' }}>
                  {refractedGapM >= 1 ? `+${refractedGapM.toFixed(1)} m` : refractedGapM > 0.01 ? `+${(refractedGapM * 100).toFixed(0)} cm` : '≈ 0'}
                </td>
                <td className="text-[11px] font-tech-mono px-3 py-2 text-right" style={{ color: bulgeM > laserH * 1000 ? '#FF4444' : '#D4A843' }}>
                  {bulgeM > laserH * 1000 ? 'laser sous l\'eau' : 'laser visible'}
                </td>
              </tr>
            );
          })}
        </tbody>
      </table>
    </div>

    {/* Résultats */}
    <div className="mt-4 grid grid-cols-1 sm:grid-cols-2 md:grid-cols-4 gap-3">
      <div className="border border-cyan-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">COURBURE MAX</div>
        <div className="text-[20px] font-tech-mono text-cyan-400 font-bold">
          {(maxBulge * 1000) >= 1 ? `${(maxBulge * 1000).toFixed(1)} m` : `${(maxBulge * 100000).toFixed(1)} cm`}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">à {dist} km</div>
      </div>
      <div className="border border-red-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-red-400/70 tracking-widest mb-2">HAUTEUR LASER</div>
        <div className="text-[20px] font-tech-mono text-red-400 font-bold">{(laserH * 100).toFixed(0)} cm</div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">au-dessus de l&apos;eau</div>
      </div>
      <div className={`border p-4 ${maxBulge * 1000 > laserH ? 'border-red-900/30 bg-red-950/20' : 'border-amber-900/30 bg-amber-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">SI GLOBE</div>
        <div className={`text-[16px] font-tech-mono font-bold ${maxBulge * 1000 > laserH ? 'text-red-400' : 'text-amber-400'}`}>
          {maxBulge * 1000 > laserH ? 'LASER BLOQUÉ' : `ÉCART +${(maxBulge * 1000).toFixed(1)} m`}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          le laser devrait monter au-dessus des cibles
        </div>
      </div>
      <div className="border border-green-900/30 bg-green-950/20 p-4">
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">SI PLAN</div>
        <div className="text-[16px] font-tech-mono font-bold text-green-400">LASER DROIT</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          touche chaque cible à la même hauteur
        </div>
      </div>
    </div>

    <div className="mt-4 border border-[#FF4444]/20 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-[#FF4444]/60 mb-2">L&apos;EXPÉRIENCE LASER SUR LAC</div>
      <p className="text-[12px] text-[#C8D8E8]/80 font-rajdhani leading-relaxed">
        Un laser placé à basse altitude au-dessus d&apos;une surface d&apos;eau calme devrait, sur un globe de 6 371 km de rayon,
        s&apos;éloigner progressivement de la surface. Sur {dist} km, l&apos;écart géométrique attendu est de {(maxBulge * 1000).toFixed(1)} m.
        La réfraction atmosphérique courbe le rayon vers la surface et réduit cet écart à {(maxBulgeRefracted * 1000).toFixed(1)} m
        dans les conditions choisies (k = {k.toFixed(2)}). Même en super-réfraction réaliste (k ≈ 0.4), l&apos;écart résiduel reste
        important au-delà de 5 km — la réfraction seule ne peut pas expliquer un laser qui touche toutes les cibles à la même hauteur.
        Si le laser reste droit, l&apos;eau est plate sur cette distance. C&apos;est le test le plus simple et le plus direct de la courbure.
      </p>
    </div>

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex flex-wrap items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-400">ARTICLES :</span>
      <a href="/article/leau-ne-ment-pas" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;eau ne ment pas →</a>
      <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;hypothèse nulle →</a>
    </div>
  </div>;
}
