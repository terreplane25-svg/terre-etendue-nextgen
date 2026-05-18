'use client';

import { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Text, Line } from '@react-three/drei';
import * as THREE from 'three';

// ─── Données orbitales simplifiées ───────────────────
const PLANETS = [
  { name: 'Mercure', color: '#A0A0A0', radius: 2.0, period: 0.24, size: 0.12 },
  { name: 'Vénus',   color: '#E8C060', radius: 3.0, period: 0.62, size: 0.15 },
  { name: 'Terre',   color: '#4488CC', radius: 4.2, period: 1.00, size: 0.16 },
  { name: 'Mars',    color: '#CC6644', radius: 5.5, period: 1.88, size: 0.13 },
  { name: 'Jupiter', color: '#C8A060', radius: 7.5, period: 11.86, size: 0.35 },
];

const SUN_COLOR = '#FFD040';
const MOON_COLOR = '#C8C8D0';

// ─── Orbite (anneau) ────────────────────────────────
function OrbitRing({ radius, color = '#00C8FF' }: { radius: number; color?: string }) {
  const points = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= 128; i++) {
      const angle = (i / 128) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(angle) * radius, 0, Math.sin(angle) * radius));
    }
    return pts;
  }, [radius]);

  return <Line points={points} color={color} opacity={0.15} transparent lineWidth={0.5} />;
}

// ─── Corps céleste ──────────────────────────────────
function CelestialBody({ 
  position, color, size, emissive = false, label, showLabel = true 
}: { 
  position: [number, number, number]; 
  color: string; 
  size: number; 
  emissive?: boolean; 
  label?: string;
  showLabel?: boolean;
}) {
  return (
    <group position={position}>
      <mesh>
        <sphereGeometry args={[size, 32, 32]} />
        <meshStandardMaterial
          color={color}
          emissive={emissive ? color : '#000000'}
          emissiveIntensity={emissive ? 1.5 : 0}
          roughness={emissive ? 0.2 : 0.6}
          metalness={emissive ? 0.8 : 0.1}
        />
      </mesh>
      {emissive && (
        <mesh>
          <sphereGeometry args={[size * 2, 16, 16]} />
          <meshBasicMaterial color={color} transparent opacity={0.08} />
        </mesh>
      )}
      {label && showLabel && (
        <Text
          position={[0, size + 0.3, 0]}
          fontSize={0.2}
          color="#C8D8E8"
          anchorX="center"
          anchorY="bottom"
         
        >
          {label}
        </Text>
      )}
    </group>
  );
}

// ─── Scène Héliocentrique ───────────────────────────
function HeliocentricScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const groupRef = useRef<THREE.Group>(null);
  const positionsRef = useRef<[number, number, number][]>(PLANETS.map(() => [0, 0, 0]));
  const moonPosRef = useRef<[number, number, number]>([0, 0, 0]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.3;
    PLANETS.forEach((planet, i) => {
      const angle = (t / planet.period) * Math.PI * 2;
      positionsRef.current[i] = [
        Math.cos(angle) * planet.radius,
        0,
        Math.sin(angle) * planet.radius,
      ];
    });
    // Lune autour de la Terre
    const earthPos = positionsRef.current[2];
    const moonAngle = t * 13.37; // ~13 orbites/an
    moonPosRef.current = [
      earthPos[0] + Math.cos(moonAngle) * 0.5,
      0,
      earthPos[2] + Math.sin(moonAngle) * 0.5,
    ];
  });

  return (
    <group ref={groupRef}>
      {/* Soleil au centre */}
      <CelestialBody position={[0, 0, 0]} color={SUN_COLOR} size={0.5} emissive label="Soleil" showLabel={showLabels} />
      <pointLight position={[0, 0, 0]} intensity={2} color={SUN_COLOR} distance={20} />

      {/* Orbites */}
      {PLANETS.map((p) => (
        <OrbitRing key={p.name} radius={p.radius} />
      ))}

      {/* Planètes */}
      {PLANETS.map((planet, i) => (
        <CelestialBody
          key={planet.name}
          position={positionsRef.current[i]}
          color={planet.color}
          size={planet.size}
          label={planet.name}
          showLabel={showLabels}
        />
      ))}

      {/* Lune */}
      <CelestialBody position={moonPosRef.current} color={MOON_COLOR} size={0.06} />
    </group>
  );
}

// ─── Scène Géocentrique (Tychonique) ────────────────
function GeocentricScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const positionsRef = useRef<{ sun: [number, number, number]; planets: [number, number, number][]; moon: [number, number, number] }>({
    sun: [0, 0, 0],
    planets: PLANETS.map(() => [0, 0, 0]),
    moon: [0, 0, 0],
  });

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.3;
    const earthRadius = 4.2;
    
    // Soleil orbite autour de la Terre
    const sunAngle = t * Math.PI * 2;
    const sunX = Math.cos(sunAngle) * earthRadius;
    const sunZ = Math.sin(sunAngle) * earthRadius;
    positionsRef.current.sun = [sunX, 0, sunZ];

    // Mercure et Vénus orbitent autour du Soleil
    PLANETS.forEach((planet, i) => {
      if (i === 2) {
        // Terre au centre
        positionsRef.current.planets[i] = [0, 0, 0];
        return;
      }
      
      if (i < 2) {
        // Planètes inférieures : orbitent autour du Soleil
        const relAngle = (t / planet.period) * Math.PI * 2;
        const relRadius = planet.radius; // Distance au Soleil dans le modèle hélio → épicycle
        positionsRef.current.planets[i] = [
          sunX + Math.cos(relAngle) * (relRadius * 0.5),
          0,
          sunZ + Math.sin(relAngle) * (relRadius * 0.5),
        ];
      } else {
        // Planètes supérieures : orbitent autour de la Terre, portées par l'épicycle du Soleil
        const mainAngle = (t / planet.period) * Math.PI * 2;
        positionsRef.current.planets[i] = [
          Math.cos(mainAngle) * planet.radius,
          0,
          Math.sin(mainAngle) * planet.radius,
        ];
      }
    });

    // Lune orbite autour de la Terre
    const moonAngle = t * 13.37;
    positionsRef.current.moon = [
      Math.cos(moonAngle) * 1.2,
      0,
      Math.sin(moonAngle) * 1.2,
    ];
  });

  return (
    <group>
      {/* Terre au centre */}
      <CelestialBody position={[0, 0, 0]} color="#4488CC" size={0.2} label="Terre" showLabel={showLabels} />

      {/* Soleil orbite autour de la Terre */}
      <OrbitRing radius={4.2} color="#FFD040" />
      <CelestialBody position={positionsRef.current.sun} color={SUN_COLOR} size={0.4} emissive label="Soleil" showLabel={showLabels} />
      <pointLight position={positionsRef.current.sun} intensity={2} color={SUN_COLOR} distance={20} />

      {/* Lune */}
      <OrbitRing radius={1.2} color="#C8C8D0" />
      <CelestialBody position={positionsRef.current.moon} color={MOON_COLOR} size={0.08} label="Lune" showLabel={showLabels} />

      {/* Autres orbites et planètes */}
      {PLANETS.map((planet, i) => {
        if (i === 2) return null; // Terre déjà affichée
        return (
          <group key={planet.name}>
            {i > 2 && <OrbitRing radius={planet.radius} />}
            <CelestialBody
              position={positionsRef.current.planets[i]}
              color={planet.color}
              size={planet.size}
              label={planet.name}
              showLabel={showLabels}
            />
          </group>
        );
      })}
    </group>
  );
}

// ─── Grille HUD de fond ─────────────────────────────
function HudGrid() {
  const points = useMemo(() => {
    const lines: THREE.Vector3[][] = [];
    const size = 12;
    const step = 2;
    for (let i = -size; i <= size; i += step) {
      lines.push([new THREE.Vector3(i, -0.01, -size), new THREE.Vector3(i, -0.01, size)]);
      lines.push([new THREE.Vector3(-size, -0.01, i), new THREE.Vector3(size, -0.01, i)]);
    }
    return lines;
  }, []);

  return (
    <>
      {points.map((pts, i) => (
        <Line key={i} points={pts} color="#00C8FF" opacity={0.04} transparent lineWidth={0.5} />
      ))}
    </>
  );
}

// ─── Composant Principal ────────────────────────────
export default function GeoHelioSim() {
  const [mode, setMode] = useState<'helio' | 'geo'>('helio');
  const [speed, setSpeed] = useState(1);
  const [showLabels, setShowLabels] = useState(true);

  return (
    <div className="w-full">
      {/* Contrôles HUD */}
      <div className="flex flex-wrap items-center gap-3 mb-4">
        <div className="flex gap-1">
          <button
            onClick={() => setMode('helio')}
            className={`px-4 py-2 text-[9px] font-orbitron tracking-widest border transition-all ${
              mode === 'helio'
                ? 'border-[#00C8FF]/60 bg-[#00C8FF]/10 text-[#00C8FF]'
                : 'border-slate-700 text-slate-500 hover:border-slate-500'
            }`}
            style={{ clipPath: 'polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)' }}
          >
            HÉLIOCENTRIQUE
          </button>
          <button
            onClick={() => setMode('geo')}
            className={`px-4 py-2 text-[9px] font-orbitron tracking-widest border transition-all ${
              mode === 'geo'
                ? 'border-[#D4A843]/60 bg-[#D4A843]/10 text-[#D4A843]'
                : 'border-slate-700 text-slate-500 hover:border-slate-500'
            }`}
            style={{ clipPath: 'polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)' }}
          >
            GÉOCENTRIQUE
          </button>
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-[9px] font-tech-mono text-slate-500">VITESSE</span>
          <input
            type="range"
            min={0.1}
            max={5}
            step={0.1}
            value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-20 accent-[#00C8FF]"
          />
          <span className="text-[9px] font-tech-mono text-[#00C8FF]">×{speed.toFixed(1)}</span>
        </div>

        <button
          onClick={() => setShowLabels(!showLabels)}
          className={`px-3 py-1 text-[8px] font-tech-mono border transition-all ${
            showLabels ? 'border-slate-600 text-slate-400' : 'border-slate-800 text-slate-600'
          }`}
        >
          {showLabels ? 'NOMS: ON' : 'NOMS: OFF'}
        </button>
      </div>

      {/* Canvas 3D */}
      <div className="w-full h-[500px] md:h-[600px] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
        {/* Corner marks */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        {/* Mode indicator */}
        <div className="absolute top-3 left-3 z-10">
          <div className={`text-[9px] font-tech-mono tracking-widest ${mode === 'helio' ? 'text-[#00C8FF]/60' : 'text-[#D4A843]/60'}`}>
            {mode === 'helio' ? '◉ MODÈLE HÉLIOCENTRIQUE' : '◉ MODÈLE GÉOCENTRIQUE'}
          </div>
          <div className="text-[8px] font-tech-mono text-slate-600 mt-1">
            {mode === 'helio' ? 'Centre : Soleil — Terre en orbite' : 'Centre : Terre — Soleil en orbite'}
          </div>
        </div>

        <Canvas camera={{ position: [0, 12, 8], fov: 50 }}>
          <ambientLight intensity={0.15} />
          <HudGrid />
          
          {mode === 'helio' ? (
            <HeliocentricScene speed={speed} showLabels={showLabels} />
          ) : (
            <GeocentricScene speed={speed} showLabels={showLabels} />
          )}

          <OrbitControls
            enablePan={false}
            minDistance={5}
            maxDistance={25}
            maxPolarAngle={Math.PI * 0.85}
          />
        </Canvas>
      </div>

      {/* Panneau d'information */}
      <div className="mt-4 border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[9px] font-tech-mono text-[#00C8FF]/40 tracking-widest mb-2">
          ANALYSE // ÉQUIVALENCE CINÉMATIQUE
        </div>
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          {mode === 'helio'
            ? "Modèle héliocentrique (Copernic, 1543) : la Terre orbite autour du Soleil. Les mêmes mouvements apparents (phases, rétrogradations, saisons) sont observés depuis la Terre. Ce modèle est cinématiquement équivalent au modèle géocentrique — aucune expérience optique n'a discriminé entre les deux."
            : "Modèle géocentrique tychonique : la Terre est au centre, le Soleil orbite autour d'elle, et les planètes autour du Soleil. Ce modèle produit exactement les mêmes observations que le modèle héliocentrique. La distinction est dynamique (forces postulées), pas cinématique (mouvements observés)."
          }
        </p>
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES LIÉS :</span>
          <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">L&apos;hypothèse nulle →</a>
          <a href="/article/200-ans-de-resultats-nuls-darago-a-einstein" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">200 ans de résultats nuls →</a>
        </div>
      </div>
    </div>
  );
}
