'use client';
import { useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

const R_EARTH = 6371;

function hiddenByGlobe(d: number, hObs: number): number {
  const r = R_EARTH;
  const horizonD = Math.sqrt((r + hObs) ** 2 - r ** 2);
  if (d <= horizonD) return 0;
  return Math.sqrt(r ** 2 + (d - horizonD) ** 2) - r;
}

function angularSize(height: number, distance: number): number {
  if (distance <= 0) return 90;
  return Math.atan2(height, distance) * (180 / Math.PI) * 60;
}

const PRESETS = [
  { label: 'Bateau 10 m — 15 km', d: 15, oh: 1.7, tgt: 0.010, name: 'Bateau côtier' },
  { label: 'Cargo 40 m — 30 km', d: 30, oh: 1.7, tgt: 0.040, name: 'Cargo' },
  { label: 'Tour 300 m — 60 km', d: 60, oh: 0, tgt: 0.300, name: 'Tour Eiffel' },
  { label: 'Chicago skyline — 90 km', d: 90, oh: 0, tgt: 0.527, name: 'Chicago' },
];

function Scene({ dist, obsH, tgtH }: { dist: number; obsH: number; tgtH: number }) {
  const hidden = hiddenByGlobe(dist, obsH);
  const scale = 8 / Math.max(dist, 10);
  const hScale = Math.min(scale * 500, 4 / Math.max(tgtH, obsH, 0.001));

  const halfD = (dist / 2) * scale;
  const obsHsc = obsH * hScale;
  const tgtHsc = tgtH * hScale;
  const hidHsc = Math.min(hidden, tgtH) * hScale;
  const visHsc = Math.max(0, tgtH - hidden) * hScale;

  const vanishY = -0.003 * dist * scale;
  const perspTgtH = tgtHsc * Math.max(0.05, 1 - dist * 0.008);

  return <>
    <ambientLight intensity={0.6} />

    {/* Modèle PERSPECTIVE (haut) */}
    <group position={[0, 3.5, 0]}>
      <Html position={[0, 2.5, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#D4A843', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.12em', fontWeight: 'bold' }}>
          MODÈLE PERSPECTIVE (plan)
        </div>
      </Html>
      {/* Sol */}
      <Line points={[
        new THREE.Vector3(-halfD - 0.5, 0, 0),
        new THREE.Vector3(halfD + 0.5, 0, 0),
      ]} color="#D4A843" lineWidth={2} />
      {/* Lignes de fuite */}
      <Line points={[
        new THREE.Vector3(-halfD, obsHsc, 0),
        new THREE.Vector3(halfD + 1, vanishY, 0),
      ]} color="#D4A843" lineWidth={1} opacity={0.2} transparent dashed dashSize={0.06} gapSize={0.04} />
      <Line points={[
        new THREE.Vector3(-halfD, 0, 0),
        new THREE.Vector3(halfD + 1, vanishY, 0),
      ]} color="#D4A843" lineWidth={1} opacity={0.2} transparent dashed dashSize={0.06} gapSize={0.04} />
      {/* Observateur */}
      <Line points={[new THREE.Vector3(-halfD, 0, 0), new THREE.Vector3(-halfD, obsHsc, 0)]} color="#D4A843" lineWidth={2} />
      <mesh position={[-halfD, obsHsc, 0]}><sphereGeometry args={[0.06, 12, 12]} /><meshBasicMaterial color="#D4A843" /></mesh>
      {/* Cible (réduite par perspective) */}
      <Line points={[new THREE.Vector3(halfD, 0, 0), new THREE.Vector3(halfD, perspTgtH, 0)]} color="#00E87B" lineWidth={3} />
      <mesh position={[halfD, perspTgtH, 0]}><sphereGeometry args={[0.05, 12, 12]} /><meshBasicMaterial color="#00E87B" /></mesh>
      {/* Ligne de visée */}
      <Line points={[new THREE.Vector3(-halfD, obsHsc, 0), new THREE.Vector3(halfD, perspTgtH, 0)]}
        color="#00E87B" lineWidth={1} opacity={0.4} transparent dashed dashSize={0.06} gapSize={0.04} />
      <Html position={[halfD + 0.5, perspTgtH / 2, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#00E87B', fontSize: '9px', fontFamily: 'monospace' }}>
          toujours visible (entier)
        </div>
      </Html>
    </group>

    {/* Modèle COURBURE (bas) */}
    <group position={[0, -3, 0]}>
      <Html position={[0, 2.8, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
        <div style={{ color: '#00C8FF', fontSize: '13px', fontFamily: 'monospace', letterSpacing: '0.12em', fontWeight: 'bold' }}>
          MODÈLE COURBURE (globe)
        </div>
      </Html>
      {/* Arc de la Terre */}
      {(() => {
        const arc = dist / R_EARTH;
        const pts: THREE.Vector3[] = [];
        for (let i = 0; i <= 100; i++) {
          const a = -arc / 2 + (i / 100) * arc;
          pts.push(new THREE.Vector3(Math.sin(a) * R_EARTH * scale, (Math.cos(a) - 1) * R_EARTH * scale, 0));
        }
        const oA = -arc / 2, tA = arc / 2;
        const oGx = Math.sin(oA) * R_EARTH * scale, oGy = (Math.cos(oA) - 1) * R_EARTH * scale;
        const tGx = Math.sin(tA) * R_EARTH * scale, tGy = (Math.cos(tA) - 1) * R_EARTH * scale;
        const oNx = Math.sin(oA), oNy = Math.cos(oA), tNx = Math.sin(tA), tNy = Math.cos(tA);
        const obsP: [number, number, number] = [oGx + oNx * obsHsc, oGy + oNy * obsHsc, 0];
        const tgtTopP: [number, number, number] = [tGx + tNx * tgtHsc, tGy + tNy * tgtHsc, 0];
        const hidP: [number, number, number] = [tGx + tNx * hidHsc, tGy + tNy * hidHsc, 0];
        const vis = hidden < tgtH;

        return <>
          <Line points={pts} color="#00C8FF" lineWidth={2.5} />
          <Line points={[new THREE.Vector3(oGx, oGy, 0), new THREE.Vector3(...obsP)]} color="#00C8FF" lineWidth={2} />
          <mesh position={obsP}><sphereGeometry args={[0.06, 12, 12]} /><meshBasicMaterial color="#00C8FF" /></mesh>
          {/* Portion visible (verte) */}
          {vis && <Line points={[new THREE.Vector3(...hidP), new THREE.Vector3(...tgtTopP)]} color="#00E87B" lineWidth={3} />}
          {/* Portion cachée (rouge) */}
          {hidden > 0 && <Line points={[new THREE.Vector3(tGx, tGy, 0), new THREE.Vector3(...hidP)]} color="#FF4444" lineWidth={4} />}
          {/* Ligne de visée */}
          <Line points={[new THREE.Vector3(...obsP), new THREE.Vector3(...tgtTopP)]}
            color={vis ? '#00E87B' : '#FF4444'} lineWidth={1} opacity={0.4} transparent dashed dashSize={0.06} gapSize={0.04} />
          {hidden > 0 && (
            <Html position={[tGx + 0.5, tGy - 0.3, 0]} center distanceFactor={10} style={{ pointerEvents: 'none' }}>
              <div style={{ color: '#FF4444', fontSize: '9px', fontFamily: 'monospace' }}>
                {(hidden * 1000).toFixed(1)} m cachés
              </div>
            </Html>
          )}
        </>;
      })()}
    </group>

    <OrbitControls enablePan enableZoom maxDistance={20} minDistance={3} />
  </>;
}

export default function PerspectiveSim() {
  const [dist, setDist] = useState(30);
  const [obsM, setObsM] = useState(1.7);
  const [tgtM, setTgtM] = useState(40);

  const obsH = obsM / 1000;
  const tgtH = tgtM / 1000;
  const hidden = hiddenByGlobe(dist, obsH);
  const angSz = angularSize(tgtM, dist * 1000);
  const eyeLimit = 1.0;

  return <div className="w-full">
    {/* Contrôles */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">DISTANCE</label>
        <div className="flex items-center gap-3">
          <input type="range" min={1} max={200} step={0.5} value={dist}
            onChange={e => setDist(+e.target.value)} className="flex-1 accent-[#00C8FF] h-2" />
          <input type="number" min={1} max={200} step={0.5} value={dist}
            onChange={e => { const v = +e.target.value; if (!isNaN(v)) setDist(Math.max(1, Math.min(200, v))); }}
            className="w-20 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#00C8FF] px-3 py-2 text-right rounded-none" />
          <span className="text-[12px] font-tech-mono text-slate-500">km</span>
        </div>
      </div>
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">HAUTEUR OBSERVATEUR</label>
        <div className="flex items-center gap-3">
          <input type="range" min={0} max={100} step={0.1} value={obsM}
            onChange={e => setObsM(+e.target.value)} className="flex-1 accent-[#D4A843] h-2" />
          <input type="number" min={0} max={100} step={0.1} value={obsM}
            onChange={e => { const v = +e.target.value; if (!isNaN(v)) setObsM(Math.max(0, Math.min(100, v))); }}
            className="w-20 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#D4A843] px-3 py-2 text-right rounded-none" />
          <span className="text-[12px] font-tech-mono text-slate-500">m</span>
        </div>
      </div>
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">HAUTEUR CIBLE</label>
        <div className="flex items-center gap-3">
          <input type="range" min={1} max={600} step={1} value={tgtM}
            onChange={e => setTgtM(+e.target.value)} className="flex-1 accent-[#00E87B] h-2" />
          <input type="number" min={1} max={600} step={1} value={tgtM}
            onChange={e => { const v = +e.target.value; if (!isNaN(v)) setTgtM(Math.max(1, Math.min(600, v))); }}
            className="w-20 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#00E87B] px-3 py-2 text-right rounded-none" />
          <span className="text-[12px] font-tech-mono text-slate-500">m</span>
        </div>
      </div>
    </div>

    {/* Presets */}
    <div className="mb-4 grid grid-cols-2 md:grid-cols-4 gap-2">
      {PRESETS.map(p => (
        <button key={p.label} onClick={() => { setDist(p.d); setObsM(p.oh); setTgtM(p.tgt * 1000); }}
          className="border border-slate-700 bg-[#0A1020] p-3 text-left hover:border-[#D4A843]/50 transition-all group">
          <div className="text-[11px] font-tech-mono text-slate-200 group-hover:text-[#D4A843] font-bold">{p.name}</div>
          <div className="text-[9px] font-tech-mono text-slate-500">{p.label}</div>
        </button>
      ))}
    </div>

    {/* Canvas 3D */}
    <div className="w-full h-[50vh] md:h-[60vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#D4A843]/30 z-10" />
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#D4A843]/30 z-10" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#D4A843]/30 z-10" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#D4A843]/30 z-10" />
      <Canvas camera={{ position: [0, 0, 12], fov: 45 }}>
        <Scene dist={dist} obsH={obsH} tgtH={tgtH} />
      </Canvas>
    </div>

    {/* Résultats */}
    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="border border-cyan-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">CACHÉ (GLOBE)</div>
        <div className="text-[20px] font-tech-mono text-cyan-400 font-bold">
          {hidden > 0 ? `${(hidden * 1000).toFixed(1)} m` : '0 m'}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">
          {hidden > 0 ? `${((hidden / tgtH) * 100).toFixed(0)}% de la cible` : 'rien de caché'}
        </div>
      </div>
      <div className="border border-amber-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-amber-400/70 tracking-widest mb-2">TAILLE ANGULAIRE</div>
        <div className="text-[20px] font-tech-mono text-amber-400 font-bold">{angSz.toFixed(1)}&apos;</div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">
          {angSz < eyeLimit ? 'sous le seuil de l\'œil (1\')' : `visible (seuil: ${eyeLimit}')`}
        </div>
      </div>
      <div className={`border p-4 ${hidden < tgtH ? 'border-green-900/30 bg-green-950/20' : 'border-red-900/30 bg-red-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">GLOBE</div>
        <div className={`text-[18px] font-tech-mono font-bold ${hidden < tgtH ? 'text-green-400' : 'text-red-400'}`}>
          {hidden < tgtH ? (hidden > 0 ? 'PARTIEL' : '✓ VISIBLE') : '✗ MASQUÉE'}
        </div>
      </div>
      <div className="border border-green-900/30 bg-green-950/20 p-4">
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">PLAN</div>
        <div className="text-[18px] font-tech-mono font-bold text-green-400">
          {angSz >= eyeLimit ? '✓ VISIBLE' : '✗ TROP PETIT'}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          {angSz >= eyeLimit ? 'perspective réduit la taille' : 'résolution angulaire insuffisante'}
        </div>
      </div>
    </div>

    <div className="mt-4 border border-[#D4A843]/20 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-[#D4A843]/60 mb-2">PERSPECTIVE VS COURBURE</div>
      <p className="text-[12px] text-[#C8D8E8]/50 font-rajdhani leading-relaxed">
        Sur un plan, un objet ne disparaît jamais « par le bas » — il rétrécit vers le point de fuite jusqu&apos;à devenir trop petit pour l&apos;œil (limite ~1 arc-minute).
        Sur un globe, la courbure cache progressivement le bas de l&apos;objet, même s&apos;il est assez grand pour être résolu.
        Ce simulateur compare les deux mécanismes : la perspective (réduction angulaire) et la courbure (occultation physique).
      </p>
    </div>

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex flex-wrap items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-500">ARTICLES :</span>
      <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;hypothèse nulle →</a>
      <a href="/article/loeil-humain-la-machine-a-voir-qui-faconne-notre-realite" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;œil humain →</a>
    </div>
  </div>;
}
