'use client';

import { useRef, useState, useMemo, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line } from '@react-three/drei';
import * as THREE from 'three';

// ─── Configuration ──────────────────────────────────
type ModelType = 'helio' | 'geo' | 'flat';

const SUN_COLOR = '#FFD040';
const MOON_COLOR = '#C8C8D0';

interface PlanetDef {
  name: string;
  color: string;
  radius: number;    // distance orbitale
  period: number;    // période en années terrestres
  size: number;      // taille visuelle
}

const PLANETS: PlanetDef[] = [
  { name: 'Mercure', color: '#A0A0A0', radius: 2.0, period: 0.24, size: 0.10 },
  { name: 'Vénus',   color: '#E8C060', radius: 3.0, period: 0.62, size: 0.13 },
  { name: 'Terre',   color: '#4488CC', radius: 4.2, period: 1.00, size: 0.14 },
  { name: 'Mars',    color: '#CC6644', radius: 5.5, period: 1.88, size: 0.11 },
  { name: 'Jupiter', color: '#C8A060', radius: 7.5, period: 11.86, size: 0.28 },
];

// ─── Orbite ring ────────────────────────────────────
function OrbitRing({ radius, color = '#00C8FF', opacity = 0.15, segments = 128 }: { 
  radius: number; color?: string; opacity?: number; segments?: number;
}) {
  const points = useMemo(() => {
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= segments; i++) {
      const a = (i / segments) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(a) * radius, 0, Math.sin(a) * radius));
    }
    return pts;
  }, [radius, segments]);
  return <Line points={points} color={color} opacity={opacity} transparent lineWidth={0.5} />;
}

// ─── Planet mesh animé (ref-based) ──────────────────
function AnimatedPlanet({ color, size, emissive = false, glowSize = 0 }: {
  color: string; size: number; emissive?: boolean; glowSize?: number;
}) {
  return (
    <group>
      <mesh>
        <sphereGeometry args={[size, 24, 24]} />
        <meshStandardMaterial
          color={color}
          emissive={emissive ? color : '#000000'}
          emissiveIntensity={emissive ? 1.5 : 0}
          roughness={emissive ? 0.2 : 0.6}
        />
      </mesh>
      {glowSize > 0 && (
        <mesh>
          <sphereGeometry args={[glowSize, 16, 16]} />
          <meshBasicMaterial color={color} transparent opacity={0.06} />
        </mesh>
      )}
    </group>
  );
}

// ─── HUD Grid de fond ───────────────────────────────
function HudGrid() {
  const lines = useMemo(() => {
    const arr: THREE.Vector3[][] = [];
    for (let i = -12; i <= 12; i += 2) {
      arr.push([new THREE.Vector3(i, -0.01, -12), new THREE.Vector3(i, -0.01, 12)]);
      arr.push([new THREE.Vector3(-12, -0.01, i), new THREE.Vector3(12, -0.01, i)]);
    }
    return arr;
  }, []);
  return <>
    {lines.map((pts, i) => (
      <Line key={i} points={pts} color="#00C8FF" opacity={0.04} transparent lineWidth={0.5} />
    ))}
  </>;
}

// ─── Disque Terre Plane ─────────────────────────────
function FlatEarthDisc() {
  return (
    <group>
      {/* Disque principal */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
        <circleGeometry args={[6, 64]} />
        <meshStandardMaterial color="#1a3a5c" roughness={0.8} />
      </mesh>
      {/* Anneau glacé extérieur (Antarctique) */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]}>
        <ringGeometry args={[5.5, 6.2, 64]} />
        <meshStandardMaterial color="#d0e4f0" roughness={0.3} />
      </mesh>
      {/* Contours continentaux simplifiés (cercles pour les masses continentales) */}
      {/* Pôle Nord au centre */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.03, 0]}>
        <circleGeometry args={[0.3, 16]} />
        <meshStandardMaterial color="#e8e8f0" roughness={0.3} />
      </mesh>
      {/* Masses continentales approximatives en projection azimutale */}
      {[
        { pos: [-1.5, 0, -1.8], scale: [1.4, 0.01, 1.8], color: '#4a7a3a' },  // Amérique du Nord
        { pos: [-1.0, 0, 1.0], scale: [0.6, 0.01, 1.6], color: '#5a8a3a' },   // Amérique du Sud
        { pos: [1.5, 0, -0.5], scale: [1.2, 0.01, 1.4], color: '#6a8a3a' },    // Eurasie
        { pos: [1.8, 0, 1.5], scale: [0.9, 0.01, 1.0], color: '#5a7a2a' },     // Afrique
        { pos: [3.5, 0, 1.8], scale: [0.6, 0.01, 0.5], color: '#8a9a4a' },     // Australie
      ].map((c, i) => (
        <mesh key={i} position={c.pos as [number, number, number]} scale={c.scale as [number, number, number]}>
          <sphereGeometry args={[0.5, 8, 8]} />
          <meshStandardMaterial color={c.color} roughness={0.7} flatShading />
        </mesh>
      ))}
    </group>
  );
}

// ─── Scène HÉLIOCENTRIQUE ───────────────────────────
function HelioScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const planetRefs = useRef<(THREE.Group | null)[]>([]);
  const moonRef = useRef<THREE.Group>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.3;
    PLANETS.forEach((p, i) => {
      const ref = planetRefs.current[i];
      if (!ref) return;
      const angle = (t / p.period) * Math.PI * 2;
      ref.position.x = Math.cos(angle) * p.radius;
      ref.position.z = Math.sin(angle) * p.radius;
    });
    // Lune autour de la Terre
    if (moonRef.current && planetRefs.current[2]) {
      const earth = planetRefs.current[2]!.position;
      const moonAngle = t * 13.37;
      moonRef.current.position.x = earth.x + Math.cos(moonAngle) * 0.5;
      moonRef.current.position.z = earth.z + Math.sin(moonAngle) * 0.5;
    }
  });

  return (
    <group>
      {/* Soleil au centre */}
      <group position={[0, 0, 0]}>
        <AnimatedPlanet color={SUN_COLOR} size={0.45} emissive glowSize={1.0} />
        <pointLight intensity={2} color={SUN_COLOR} distance={20} />
      </group>
      
      {/* Orbites */}
      {PLANETS.map(p => <OrbitRing key={p.name} radius={p.radius} />)}
      
      {/* Planètes */}
      {PLANETS.map((p, i) => (
        <group key={p.name} ref={el => { planetRefs.current[i] = el; }}>
          <AnimatedPlanet color={p.color} size={p.size} />
        </group>
      ))}
      
      {/* Lune */}
      <group ref={moonRef}>
        <AnimatedPlanet color={MOON_COLOR} size={0.05} />
      </group>
    </group>
  );
}

// ─── Scène GÉOCENTRIQUE (Ptolémée / Tycho) ─────────
function GeoScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group | null)[]>([]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.3;
    
    // Soleil orbite autour de la Terre
    const sunAngle = t * Math.PI * 2;
    const sunR = 4.2;
    const sunX = Math.cos(sunAngle) * sunR;
    const sunZ = Math.sin(sunAngle) * sunR;
    if (sunRef.current) {
      sunRef.current.position.set(sunX, 0, sunZ);
    }

    // Lune orbite autour de la Terre
    if (moonRef.current) {
      const moonAngle = t * 13.37;
      moonRef.current.position.x = Math.cos(moonAngle) * 1.2;
      moonRef.current.position.z = Math.sin(moonAngle) * 1.2;
    }

    // Planètes
    PLANETS.forEach((p, i) => {
      const ref = planetRefs.current[i];
      if (!ref || i === 2) return; // Terre = centre
      if (i < 2) {
        // Inférieures : épicycles autour du Soleil
        const relAngle = (t / p.period) * Math.PI * 2;
        ref.position.x = sunX + Math.cos(relAngle) * (p.radius * 0.5);
        ref.position.z = sunZ + Math.sin(relAngle) * (p.radius * 0.5);
      } else {
        // Supérieures : orbites autour de la Terre
        const angle = (t / p.period) * Math.PI * 2;
        ref.position.x = Math.cos(angle) * p.radius;
        ref.position.z = Math.sin(angle) * p.radius;
      }
    });
  });

  return (
    <group>
      {/* Terre au centre */}
      <group position={[0, 0, 0]}>
        <AnimatedPlanet color="#4488CC" size={0.18} />
      </group>

      {/* Soleil */}
      <OrbitRing radius={4.2} color="#FFD040" opacity={0.12} />
      <group ref={sunRef}>
        <AnimatedPlanet color={SUN_COLOR} size={0.35} emissive glowSize={0.8} />
        <pointLight intensity={2} color={SUN_COLOR} distance={20} />
      </group>

      {/* Lune */}
      <OrbitRing radius={1.2} color="#C8C8D0" opacity={0.1} />
      <group ref={moonRef}>
        <AnimatedPlanet color={MOON_COLOR} size={0.07} />
      </group>

      {/* Autres planètes */}
      {PLANETS.map((p, i) => {
        if (i === 2) return null;
        return (
          <group key={p.name}>
            {i > 2 && <OrbitRing radius={p.radius} />}
            <group ref={el => { planetRefs.current[i] = el; }}>
              <AnimatedPlanet color={p.color} size={p.size} />
            </group>
          </group>
        );
      })}
    </group>
  );
}

// ─── Scène TERRE PLANE ──────────────────────────────
function FlatScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const sunLightRef = useRef<THREE.SpotLight>(null);

  // Zone éclairée : spotlight conique depuis le soleil vers le disque
  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.2;

    // Le Soleil circule au-dessus du disque
    // En été boréal : cercle plus serré (tropique du Cancer ~23°)
    // Oscillation saisonnière
    const yearPhase = t * 0.5; // 1 an = ~12s
    const dayAngle = t * Math.PI * 2; // 1 jour = ~2s

    // Rayon d'orbite du Soleil : oscille entre 1.5 (été) et 3.5 (hiver)
    const sunOrbitR = 2.5 + Math.sin(yearPhase) * 1.0;
    const sunHeight = 3.0;

    if (sunRef.current) {
      sunRef.current.position.x = Math.cos(dayAngle) * sunOrbitR;
      sunRef.current.position.y = sunHeight;
      sunRef.current.position.z = Math.sin(dayAngle) * sunOrbitR;
    }

    // Spotlight qui suit le Soleil
    if (sunLightRef.current && sunRef.current) {
      sunLightRef.current.position.copy(sunRef.current.position);
      sunLightRef.current.target.position.set(
        sunRef.current.position.x * 0.8,
        0,
        sunRef.current.position.z * 0.8
      );
      sunLightRef.current.target.updateMatrixWorld();
    }

    // Lune : orbite légèrement plus large, décalée
    const moonOrbitR = 2.8 + Math.sin(yearPhase + 1.5) * 0.8;
    const moonAngle = dayAngle + Math.PI; // opposition approximative
    const moonHeight = 2.5;
    if (moonRef.current) {
      moonRef.current.position.x = Math.cos(moonAngle) * moonOrbitR;
      moonRef.current.position.y = moonHeight;
      moonRef.current.position.z = Math.sin(moonAngle) * moonOrbitR;
    }
  });

  return (
    <group>
      {/* Ambient faible — l'éclairage vient du spotlight */}
      <ambientLight intensity={0.08} />

      {/* Disque terrestre */}
      <FlatEarthDisc />

      {/* Soleil */}
      <group ref={sunRef} position={[2.5, 3, 0]}>
        <AnimatedPlanet color={SUN_COLOR} size={0.25} emissive glowSize={0.6} />
        <pointLight intensity={1} color={SUN_COLOR} distance={10} />
      </group>

      {/* Spotlight pour zone jour/nuit */}
      <spotLight
        ref={sunLightRef}
        intensity={3}
        color="#FFF5D0"
        distance={12}
        angle={Math.PI / 3.5}
        penumbra={0.6}
        position={[2.5, 3, 0]}
        castShadow={false}
      />

      {/* Lune */}
      <group ref={moonRef} position={[-2.5, 2.5, 0]}>
        <AnimatedPlanet color={MOON_COLOR} size={0.12} />
      </group>

      {/* Orbites du Soleil et de la Lune (cercles en hauteur) */}
      {[2.0, 2.5, 3.0, 3.5].map((r, i) => (
        <group key={i} position={[0, 3, 0]}>
          <OrbitRing radius={r} color="#FFD040" opacity={0.05} />
        </group>
      ))}

      {/* Dôme / firmament (optionnel, semi-transparent) */}
      <mesh position={[0, 0, 0]}>
        <sphereGeometry args={[8, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshBasicMaterial color="#0a1030" transparent opacity={0.15} side={THREE.BackSide} />
      </mesh>

      {/* Étoiles sur le dôme */}
      {useMemo(() => {
        const stars: [number, number, number][] = [];
        for (let i = 0; i < 200; i++) {
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.random() * Math.PI * 0.45;
          const r = 7.8;
          stars.push([
            Math.sin(phi) * Math.cos(theta) * r,
            Math.cos(phi) * r,
            Math.sin(phi) * Math.sin(theta) * r,
          ]);
        }
        return stars.map((pos, i) => (
          <mesh key={i} position={pos}>
            <sphereGeometry args={[0.02, 4, 4]} />
            <meshBasicMaterial color="#ffffff" transparent opacity={0.4 + Math.random() * 0.4} />
          </mesh>
        ));
      }, [])}
    </group>
  );
}

// ─── Composant Principal ────────────────────────────
export default function GeoHelioSim() {
  const [mode, setMode] = useState<ModelType>('helio');
  const [speed, setSpeed] = useState(1);
  const [showLabels, setShowLabels] = useState(true);

  const modeConfig = {
    helio: { label: 'HÉLIOCENTRIQUE', color: '#00C8FF', cam: [0, 12, 8] as [number, number, number] },
    geo: { label: 'GÉOCENTRIQUE', color: '#D4A843', cam: [0, 12, 8] as [number, number, number] },
    flat: { label: 'TERRE PLANE', color: '#00E87B', cam: [6, 8, 6] as [number, number, number] },
  };

  const cfg = modeConfig[mode];

  return (
    <div className="w-full">
      {/* Contrôles */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        <div className="flex gap-1">
          {(Object.entries(modeConfig) as [ModelType, typeof cfg][]).map(([id, c]) => (
            <button
              key={id}
              onClick={() => setMode(id)}
              className={`px-3 md:px-4 py-2 text-[8px] md:text-[9px] font-orbitron tracking-widest border transition-all ${
                mode === id
                  ? `border-[${c.color}]/60 bg-[${c.color}]/10`
                  : 'border-slate-700 text-slate-500 hover:border-slate-500'
              }`}
              style={{
                clipPath: 'polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)',
                borderColor: mode === id ? `${c.color}99` : undefined,
                backgroundColor: mode === id ? `${c.color}1a` : undefined,
                color: mode === id ? c.color : undefined,
              }}
            >
              {c.label}
            </button>
          ))}
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-[8px] font-tech-mono text-slate-500">VIT.</span>
          <input
            type="range" min={0.1} max={5} step={0.1} value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-16 md:w-20 accent-[#00C8FF]"
          />
          <span className="text-[8px] font-tech-mono text-[#00C8FF]">×{speed.toFixed(1)}</span>
        </div>
      </div>

      {/* Canvas 3D */}
      <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
        {/* Corner marks */}
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        {/* Mode indicator */}
        <div className="absolute top-3 left-3 z-10">
          <div className="text-[9px] font-tech-mono tracking-widest" style={{ color: `${cfg.color}99` }}>
            ◉ {cfg.label}
          </div>
          <div className="text-[8px] font-tech-mono text-slate-600 mt-1">
            {mode === 'helio' && 'Centre : Soleil — Terre en orbite'}
            {mode === 'geo' && 'Centre : Terre — Soleil en orbite'}
            {mode === 'flat' && 'Terre plane — Soleil et Lune au-dessus du disque'}
          </div>
        </div>

        <Canvas camera={{ position: cfg.cam, fov: 50 }} key={mode}>
          <ambientLight intensity={mode === 'flat' ? 0.05 : 0.15} />
          {mode !== 'flat' && <HudGrid />}

          {mode === 'helio' && <HelioScene speed={speed} showLabels={showLabels} />}
          {mode === 'geo' && <GeoScene speed={speed} showLabels={showLabels} />}
          {mode === 'flat' && <FlatScene speed={speed} showLabels={showLabels} />}

          <OrbitControls
            enablePan={false}
            minDistance={4}
            maxDistance={25}
            maxPolarAngle={mode === 'flat' ? Math.PI * 0.45 : Math.PI * 0.85}
          />
        </Canvas>
      </div>

      {/* Panneau d'information */}
      <div className="mt-4 border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[9px] font-tech-mono tracking-widest mb-2" style={{ color: `${cfg.color}66` }}>
          ANALYSE // {cfg.label}
        </div>
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          {mode === 'helio' && "Modèle héliocentrique (Copernic, 1543) : la Terre orbite autour du Soleil. Les mêmes mouvements apparents — phases, rétrogradations, saisons — sont observés depuis la Terre. Ce modèle est cinématiquement équivalent au modèle géocentrique."}
          {mode === 'geo' && "Modèle géocentrique (Ptolémée / Tycho) : la Terre sphérique est au centre, le Soleil orbite autour d\u2019elle, et les planètes inférieures orbitent autour du Soleil (épicycles). Ce modèle produit exactement les mêmes observations que le modèle héliocentrique."}
          {mode === 'flat' && "Modèle MGPP (Terre plane) : le disque terrestre est stationnaire, le Soleil et la Lune circulent au-dessus à quelques milliers de km d\u2019altitude. Le jour et la nuit résultent du déplacement du cône lumineux solaire sur le disque. Le Soleil oscille entre les tropiques selon les saisons."}
        </p>
        <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES LIÉS :</span>
          <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">L&apos;hypothèse nulle →</a>
          <a href="/article/200-ans-de-resultats-nuls-darago-a-einstein" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">200 ans de résultats nuls →</a>
          {mode === 'flat' && <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[#00E87B]/50 hover:text-[#00E87B] transition-colors">Le MGPP →</a>}
        </div>
      </div>
    </div>
  );
}
