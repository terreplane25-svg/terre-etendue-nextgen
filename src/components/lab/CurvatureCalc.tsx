'use client';

import { useRef, useState, useMemo, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import * as THREE from 'three';

const R_EARTH = 6371; // km
const PRESETS = [
  { label: 'Bedford Level (10 km)', distance: 10, height: 0.5 },
  { label: 'Chicago depuis Michigan (90 km)', distance: 90, height: 1.7 },
  { label: 'Canigou depuis Marseille (263 km)', distance: 263, height: 50 },
  { label: 'Finestrelles→Gaspard (443 km)', distance: 443, height: 2820 },
];

// ─── Surface courbée (globe) ────────────────────────
function GlobeSurface({ distance, scale }: { distance: number; scale: number }) {
  const geometry = useMemo(() => {
    const arc = distance / R_EARTH; // angle en radians
    const segments = 64;
    const points: THREE.Vector3[] = [];
    for (let i = 0; i <= segments; i++) {
      const angle = -arc / 2 + (i / segments) * arc;
      const x = Math.sin(angle) * R_EARTH * scale;
      const y = (Math.cos(angle) - 1) * R_EARTH * scale; // 0 au centre, négatif aux bords
      points.push(new THREE.Vector3(x, y, 0));
    }
    return points;
  }, [distance, scale]);

  return <Line points={geometry} color="#00C8FF" lineWidth={2} />;
}

// ─── Surface plane ──────────────────────────────────
function FlatSurface({ distance, scale }: { distance: number; scale: number }) {
  const halfD = (distance / 2) * scale;
  return (
    <Line
      points={[
        new THREE.Vector3(-halfD, 0, 0),
        new THREE.Vector3(halfD, 0, 0),
      ]}
      color="#D4A843"
      lineWidth={2}
    />
  );
}

// ─── Ligne de visée ─────────────────────────────────
function LineOfSight({
  from, to, color, blocked = false
}: {
  from: [number, number, number];
  to: [number, number, number];
  color: string;
  blocked?: boolean;
}) {
  return (
    <Line
      points={[new THREE.Vector3(...from), new THREE.Vector3(...to)]}
      color={color}
      lineWidth={1.5}
      opacity={blocked ? 0.3 : 0.8}
      transparent
      dashed={blocked}
      dashSize={0.1}
      gapSize={0.05}
    />
  );
}

// ─── Observateur (triangle) ─────────────────────────
function Observer({ position, color, label }: {
  position: [number, number, number];
  color: string;
  label: string;
}) {
  return (
    <group position={position}>
      <mesh>
        <coneGeometry args={[0.05, 0.15, 4]} />
        <meshBasicMaterial color={color} />
      </mesh>
      <Text
        position={[0, 0.25, 0]}
        fontSize={0.08}
        color={color}
        anchorX="center"
        font="/fonts/Rajdhani-Medium.ttf"
      >
        {label}
      </Text>
    </group>
  );
}

// ─── Scène principale ───────────────────────────────
function VisibilityScene({ distance, height, targetHeight }: {
  distance: number;
  height: number;
  targetHeight: number;
}) {
  // Échelle pour que ça rentre dans la scène
  const maxDim = Math.max(distance, 100);
  const scale = 8 / maxDim;
  const halfD = (distance / 2) * scale;

  // Calcul de courbure
  const curvatureDrop = (distance * distance) / (2 * R_EARTH); // en km
  const curveDropScaled = curvatureDrop * scale;

  // Positions des observateurs
  const hScaled = height * scale / 1; // hauteur en km → échelle
  const tScaled = targetHeight * scale / 1;

  // Globe : observateur sur la courbe
  const obsAngle = -distance / (2 * R_EARTH);
  const targetAngle = distance / (2 * R_EARTH);
  
  const globeObsX = Math.sin(obsAngle) * R_EARTH * scale;
  const globeObsY = (Math.cos(obsAngle) - 1) * R_EARTH * scale + hScaled;
  
  const globeTargetX = Math.sin(targetAngle) * R_EARTH * scale;
  const globeTargetY = (Math.cos(targetAngle) - 1) * R_EARTH * scale + tScaled;

  // Plan : observateur sur le plan
  const flatObsY = hScaled;
  const flatTargetY = tScaled;

  return (
    <>
      <ambientLight intensity={0.5} />

      {/* Globe (en haut) */}
      <group position={[0, 2, 0]}>
        <GlobeSurface distance={distance} scale={scale} />
        <Observer position={[globeObsX, globeObsY, 0]} color="#00C8FF" label={`h=${height >= 1 ? height.toFixed(0) : height.toFixed(1)} km`} />
        <Observer position={[globeTargetX, globeTargetY, 0]} color="#00E87B" label="Cible" />
        <LineOfSight
          from={[globeObsX, globeObsY, 0]}
          to={[globeTargetX, globeTargetY, 0]}
          color="#FF4444"
          blocked={curvatureDrop > height + targetHeight}
        />
        {/* Drop de courbure */}
        <Line
          points={[
            new THREE.Vector3(0, 0, 0),
            new THREE.Vector3(0, -curveDropScaled, 0),
          ]}
          color="#FF4444"
          lineWidth={1}
          dashed
          dashSize={0.05}
          gapSize={0.03}
        />
        <Text position={[0.3, -curveDropScaled / 2, 0]} fontSize={0.07} color="#FF4444" anchorX="left">
          {curvatureDrop >= 1 ? `↓ ${curvatureDrop.toFixed(1)} km` : `↓ ${(curvatureDrop * 1000).toFixed(1)} m`}
        </Text>
        <Text position={[0, 3.5, 0]} fontSize={0.12} color="#00C8FF" anchorX="center" font="/fonts/Rajdhani-Medium.ttf">
          MODÈLE GLOBE (R = 6 371 km)
        </Text>
      </group>

      {/* Plan (en bas) */}
      <group position={[0, -2, 0]}>
        <FlatSurface distance={distance} scale={scale} />
        <Observer position={[-halfD, flatObsY, 0]} color="#D4A843" label={`h=${height >= 1 ? height.toFixed(0) : height.toFixed(1)} km`} />
        <Observer position={[halfD, flatTargetY, 0]} color="#00E87B" label="Cible" />
        <LineOfSight
          from={[-halfD, flatObsY, 0]}
          to={[halfD, flatTargetY, 0]}
          color="#00E87B"
        />
        <Text position={[0, 1.5, 0]} fontSize={0.12} color="#D4A843" anchorX="center" font="/fonts/Rajdhani-Medium.ttf">
          MODÈLE PLAN
        </Text>
      </group>

      <OrbitControls enablePan enableZoom maxDistance={20} minDistance={3} />
    </>
  );
}

// ─── Composant Principal ────────────────────────────
export default function CurvatureCalc() {
  const [distance, setDistance] = useState(90);
  const [height, setHeight] = useState(1.7);
  const [targetHeight, setTargetHeight] = useState(0.3);

  const curvatureDrop = (distance * distance) / (2 * R_EARTH);
  const horizonDist = Math.sqrt(2 * R_EARTH * (height / 1000)); // en km, h en mètres

  return (
    <div className="w-full">
      {/* Contrôles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <div className="border border-slate-800/50 bg-[#0A1020] p-3">
          <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">DISTANCE (km)</label>
          <input
            type="range" min={1} max={500} step={1} value={distance}
            onChange={(e) => setDistance(parseInt(e.target.value))}
            className="w-full accent-[#00C8FF]"
          />
          <div className="text-[14px] font-tech-mono text-[#00C8FF] mt-1">{distance} km</div>
        </div>
        <div className="border border-slate-800/50 bg-[#0A1020] p-3">
          <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">HAUTEUR OBSERVATEUR</label>
          <input
            type="range" min={0.001} max={5} step={0.001} value={height}
            onChange={(e) => setHeight(parseFloat(e.target.value))}
            className="w-full accent-[#00C8FF]"
          />
          <div className="text-[14px] font-tech-mono text-[#00C8FF] mt-1">
            {height >= 1 ? `${height.toFixed(1)} km` : `${(height * 1000).toFixed(0)} m`}
          </div>
        </div>
        <div className="border border-slate-800/50 bg-[#0A1020] p-3">
          <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">HAUTEUR CIBLE</label>
          <input
            type="range" min={0.001} max={1} step={0.001} value={targetHeight}
            onChange={(e) => setTargetHeight(parseFloat(e.target.value))}
            className="w-full accent-[#00C8FF]"
          />
          <div className="text-[14px] font-tech-mono text-[#00C8FF] mt-1">
            {targetHeight >= 1 ? `${targetHeight.toFixed(1)} km` : `${(targetHeight * 1000).toFixed(0)} m`}
          </div>
        </div>
      </div>

      {/* Presets */}
      <div className="flex flex-wrap gap-2 mb-4">
        <span className="text-[8px] font-tech-mono text-slate-600 self-center">CAS RÉELS :</span>
        {PRESETS.map((p) => (
          <button
            key={p.label}
            onClick={() => { setDistance(p.distance); setHeight(p.height / 1000); setTargetHeight(0.01); }}
            className="px-3 py-1 text-[8px] font-tech-mono border border-slate-700 text-slate-400 hover:border-[#00C8FF]/40 hover:text-[#00C8FF] transition-all"
          >
            {p.label}
          </button>
        ))}
      </div>

      {/* Canvas */}
      <div className="w-full h-[450px] md:h-[550px] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        <Canvas camera={{ position: [0, 0, 12], fov: 45 }}>
          <VisibilityScene distance={distance} height={height} targetHeight={targetHeight} />
        </Canvas>
      </div>

      {/* Résultats */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="border border-red-900/30 bg-[#0A1020] p-3">
          <div className="text-[8px] font-tech-mono text-red-400/60 tracking-widest mb-1">CHUTE DE COURBURE</div>
          <div className="text-[18px] font-tech-mono text-red-400">
            {curvatureDrop >= 1 ? `${curvatureDrop.toFixed(1)} km` : `${(curvatureDrop * 1000).toFixed(1)} m`}
          </div>
          <div className="text-[9px] font-tech-mono text-slate-500 mt-1">h = d² / (2R)</div>
        </div>
        <div className="border border-cyan-900/30 bg-[#0A1020] p-3">
          <div className="text-[8px] font-tech-mono text-cyan-400/60 tracking-widest mb-1">HORIZON THÉORIQUE</div>
          <div className="text-[18px] font-tech-mono text-cyan-400">
            {horizonDist.toFixed(1)} km
          </div>
          <div className="text-[9px] font-tech-mono text-slate-500 mt-1">d = √(2Rh)</div>
        </div>
        <div className={`border p-3 ${curvatureDrop > (height + targetHeight) ? 'border-red-900/30 bg-red-950/20' : 'border-green-900/30 bg-green-950/20'}`}>
          <div className="text-[8px] font-tech-mono text-slate-400/60 tracking-widest mb-1">VERDICT GLOBE</div>
          <div className={`text-[14px] font-tech-mono ${curvatureDrop > (height + targetHeight) ? 'text-red-400' : 'text-green-400'}`}>
            {curvatureDrop > (height + targetHeight) ? '✗ CIBLE MASQUÉE' : '✓ CIBLE VISIBLE'}
          </div>
          <div className="text-[9px] font-tech-mono text-slate-500 mt-1">
            Masquage : {curvatureDrop >= 1 ? `${curvatureDrop.toFixed(1)} km` : `${(curvatureDrop * 1000).toFixed(0)} m`} vs cible : {targetHeight >= 1 ? `${targetHeight.toFixed(1)} km` : `${(targetHeight * 1000).toFixed(0)} m`}
          </div>
        </div>
      </div>

      {/* Liens */}
      <div className="mt-3 border-t border-slate-800/30 pt-3 flex items-center gap-4">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES LIÉS :</span>
        <a href="/article/leau-ne-ment-pas" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">L&apos;eau ne ment pas →</a>
        <a href="/article/ce-quon-voit-quand-on-ne-devrait-plus-voir" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">Ce qu&apos;on voit →</a>
      </div>
    </div>
  );
}
