'use client';

import { useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import * as THREE from 'three';

// ─── Calculs de triangulation ───────────────────────
function triangulate(stationDist: number, angle1: number, angle2: number) {
  // Deux stations séparées de stationDist (km)
  // Angles d'élévation en degrés
  const a1 = (angle1 * Math.PI) / 180;
  const a2 = (angle2 * Math.PI) / 180;
  
  // Triangulation plane : intersection des deux lignes de visée
  const tan1 = Math.tan(a1);
  const tan2 = Math.tan(a2);
  
  if (Math.abs(tan1 + tan2) < 0.0001) return { altitude: Infinity, horizontalPos: 0 };
  
  // Position horizontale du Soleil depuis la station 1
  const x = (stationDist * tan2) / (tan1 + tan2);
  // Altitude
  const altitude = x * tan1;
  
  return { altitude, horizontalPos: x };
}

// ─── Scène de triangulation ─────────────────────────
function TriangulationScene({ 
  stationDist, angle1, angle2 
}: { 
  stationDist: number; 
  angle1: number; 
  angle2: number;
}) {
  const result = useMemo(
    () => triangulate(stationDist, angle1, angle2),
    [stationDist, angle1, angle2]
  );

  // Échelle pour la visualisation
  const maxDim = Math.max(stationDist, result.altitude || 100, 50);
  const scale = 6 / maxDim;

  const halfDist = (stationDist / 2) * scale;
  const altScaled = Math.min((result.altitude || 0) * scale, 8);
  const sunX = (result.horizontalPos - stationDist / 2) * scale;

  const a1Rad = (angle1 * Math.PI) / 180;
  const a2Rad = (angle2 * Math.PI) / 180;

  // Lignes de visée
  const lineLen = 10;
  const sight1End: [number, number, number] = [
    -halfDist + Math.cos(a1Rad) * lineLen,
    Math.sin(a1Rad) * lineLen,
    0,
  ];
  const sight2End: [number, number, number] = [
    halfDist - Math.cos(a2Rad) * lineLen,
    Math.sin(a2Rad) * lineLen,
    0,
  ];

  return (
    <>
      <ambientLight intensity={0.4} />

      {/* Surface */}
      <Line
        points={[
          new THREE.Vector3(-halfDist - 1, 0, 0),
          new THREE.Vector3(halfDist + 1, 0, 0),
        ]}
        color="#00C8FF"
        lineWidth={2}
      />

      {/* Grille de fond */}
      {Array.from({ length: 20 }).map((_, i) => {
        const y = (i + 1) * 0.5;
        return (
          <Line
            key={`grid-h-${i}`}
            points={[new THREE.Vector3(-halfDist - 1, y, 0), new THREE.Vector3(halfDist + 1, y, 0)]}
            color="#00C8FF"
            opacity={0.03}
            transparent
            lineWidth={0.5}
          />
        );
      })}

      {/* Station 1 (gauche) */}
      <group position={[-halfDist, 0, 0]}>
        <mesh>
          <coneGeometry args={[0.08, 0.2, 4]} />
          <meshBasicMaterial color="#00C8FF" />
        </mesh>
        <Text position={[0, -0.3, 0]} fontSize={0.12} color="#00C8FF" anchorX="center" font="/fonts/Rajdhani-Medium.ttf">
          Station A
        </Text>
        <Text position={[0, -0.5, 0]} fontSize={0.08} color="#00C8FF" anchorX="center">
          α = {angle1.toFixed(1)}°
        </Text>
      </group>

      {/* Station 2 (droite) */}
      <group position={[halfDist, 0, 0]}>
        <mesh>
          <coneGeometry args={[0.08, 0.2, 4]} />
          <meshBasicMaterial color="#00E87B" />
        </mesh>
        <Text position={[0, -0.3, 0]} fontSize={0.12} color="#00E87B" anchorX="center" font="/fonts/Rajdhani-Medium.ttf">
          Station B
        </Text>
        <Text position={[0, -0.5, 0]} fontSize={0.08} color="#00E87B" anchorX="center">
          β = {angle2.toFixed(1)}°
        </Text>
      </group>

      {/* Distance entre stations */}
      <Line
        points={[new THREE.Vector3(-halfDist, -0.1, 0), new THREE.Vector3(halfDist, -0.1, 0)]}
        color="#C8D8E8"
        opacity={0.3}
        transparent
        lineWidth={1}
      />
      <Text position={[0, -0.2, 0]} fontSize={0.1} color="#C8D8E8" anchorX="center">
        d = {stationDist} km
      </Text>

      {/* Lignes de visée */}
      <Line
        points={[new THREE.Vector3(-halfDist, 0.1, 0), new THREE.Vector3(sunX, altScaled, 0)]}
        color="#FFD040"
        opacity={0.6}
        transparent
        lineWidth={1}
        dashed
        dashSize={0.1}
        gapSize={0.05}
      />
      <Line
        points={[new THREE.Vector3(halfDist, 0.1, 0), new THREE.Vector3(sunX, altScaled, 0)]}
        color="#FFD040"
        opacity={0.6}
        transparent
        lineWidth={1}
        dashed
        dashSize={0.1}
        gapSize={0.05}
      />

      {/* Soleil (point de convergence) */}
      {result.altitude > 0 && result.altitude < 200000 && (
        <group position={[sunX, altScaled, 0]}>
          <mesh>
            <sphereGeometry args={[0.2, 32, 32]} />
            <meshStandardMaterial color="#FFD040" emissive="#FFD040" emissiveIntensity={1.5} />
          </mesh>
          <mesh>
            <sphereGeometry args={[0.5, 16, 16]} />
            <meshBasicMaterial color="#FFD040" transparent opacity={0.1} />
          </mesh>
          <pointLight intensity={1} color="#FFD040" distance={8} />

          {/* Ligne verticale d'altitude */}
          <Line
            points={[new THREE.Vector3(0, 0, 0), new THREE.Vector3(0, -altScaled, 0)]}
            color="#FF8800"
            opacity={0.4}
            transparent
            lineWidth={1}
            dashed
            dashSize={0.08}
            gapSize={0.04}
          />
          <Text position={[0.3, -altScaled / 2, 0]} fontSize={0.1} color="#FF8800" anchorX="left">
            h = {result.altitude >= 1000 ? `${(result.altitude / 1000).toFixed(0)} M km` : `${result.altitude.toFixed(0)} km`}
          </Text>
        </group>
      )}

      <OrbitControls enablePan enableZoom maxDistance={20} minDistance={3} />
    </>
  );
}

// ─── Composant Principal ────────────────────────────
export default function TriangulationSim() {
  const [stationDist, setStationDist] = useState(500);
  const [angle1, setAngle1] = useState(65);
  const [angle2, setAngle2] = useState(63);

  const result = triangulate(stationDist, angle1, angle2);
  
  // Altitude du Soleil standard : 149 597 870 km
  const standardAlt = 149597870;
  const ratio = result.altitude / standardAlt;

  return (
    <div className="w-full">
      {/* Contrôles */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
        <div className="border border-slate-800/50 bg-[#0A1020] p-3">
          <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">
            DISTANCE ENTRE STATIONS (km)
          </label>
          <input
            type="range" min={10} max={2000} step={10} value={stationDist}
            onChange={(e) => setStationDist(parseInt(e.target.value))}
            className="w-full accent-[#00C8FF]"
          />
          <div className="text-[14px] font-tech-mono text-[#00C8FF] mt-1">{stationDist} km</div>
        </div>
        <div className="border border-slate-800/50 bg-[#0A1020] p-3">
          <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">
            ANGLE STATION A (°)
          </label>
          <input
            type="range" min={5} max={89} step={0.5} value={angle1}
            onChange={(e) => setAngle1(parseFloat(e.target.value))}
            className="w-full accent-[#00C8FF]"
          />
          <div className="text-[14px] font-tech-mono text-[#00C8FF] mt-1">{angle1.toFixed(1)}°</div>
        </div>
        <div className="border border-slate-800/50 bg-[#0A1020] p-3">
          <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">
            ANGLE STATION B (°)
          </label>
          <input
            type="range" min={5} max={89} step={0.5} value={angle2}
            onChange={(e) => setAngle2(parseFloat(e.target.value))}
            className="w-full accent-[#00C8FF]"
          />
          <div className="text-[14px] font-tech-mono text-[#00E87B] mt-1">{angle2.toFixed(1)}°</div>
        </div>
      </div>

      {/* Canvas */}
      <div className="w-full h-[450px] md:h-[550px] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        <div className="absolute top-3 left-3 z-10">
          <div className="text-[9px] font-tech-mono text-[#FFD040]/60 tracking-widest">
            ◉ TRIANGULATION SOLAIRE
          </div>
        </div>

        <Canvas camera={{ position: [0, 3, 10], fov: 45 }}>
          <TriangulationScene stationDist={stationDist} angle1={angle1} angle2={angle2} />
        </Canvas>
      </div>

      {/* Résultats */}
      <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
        <div className="border border-amber-900/30 bg-[#0A1020] p-3">
          <div className="text-[8px] font-tech-mono text-amber-400/60 tracking-widest mb-1">ALTITUDE CALCULÉE</div>
          <div className="text-[18px] font-tech-mono text-amber-400">
            {result.altitude >= 1000 ? `${(result.altitude / 1000).toFixed(0)} M km` : `${result.altitude.toFixed(0)} km`}
          </div>
        </div>
        <div className="border border-slate-700/30 bg-[#0A1020] p-3">
          <div className="text-[8px] font-tech-mono text-slate-400/60 tracking-widest mb-1">ALTITUDE STANDARD</div>
          <div className="text-[18px] font-tech-mono text-slate-400">149 597 870 km</div>
          <div className="text-[9px] font-tech-mono text-slate-600 mt-1">1 UA (modèle hélio)</div>
        </div>
        <div className={`border p-3 ${ratio < 0.01 ? 'border-amber-900/30 bg-amber-950/20' : 'border-slate-700/30 bg-[#0A1020]'}`}>
          <div className="text-[8px] font-tech-mono text-slate-400/60 tracking-widest mb-1">RATIO</div>
          <div className={`text-[18px] font-tech-mono ${ratio < 0.01 ? 'text-amber-400' : 'text-slate-400'}`}>
            {ratio < 0.001 ? `${(ratio * 100).toFixed(4)}%` : `${(ratio * 100).toFixed(1)}%`}
          </div>
          <div className="text-[9px] font-tech-mono text-slate-600 mt-1">
            {ratio < 0.01 ? 'Convergence vers un Soleil local' : 'Compatible avec un Soleil distant'}
          </div>
        </div>
      </div>

      {/* Explication */}
      <div className="mt-4 border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[9px] font-tech-mono text-[#FFD040]/40 tracking-widest mb-2">
          PROTOCOLE // THÉODOLITE CÉLESTE
        </div>
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          Deux stations au sol, séparées d&apos;une distance connue, mesurent simultanément l&apos;angle d&apos;élévation du Soleil. 
          La trigonométrie plane donne directement l&apos;altitude. Si le Soleil est à 150 millions de km, 
          les deux angles devraient être quasi-identiques (parallaxe &lt; 0,001°). Si les angles divergent 
          de plus de 1°, cela implique un Soleil beaucoup plus proche.
        </p>
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLE LIÉ :</span>
          <a href="/article/le-theodolite-celeste" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">Le théodolite céleste →</a>
        </div>
      </div>
    </div>
  );
}
