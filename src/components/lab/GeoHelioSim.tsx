'use client';

import React, { useRef, useState, useMemo, useEffect, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';
import {
  getAllPositions, latLngToFlatDisc,
} from './celestialCalc';

// ─── Types & Config ─────────────────────────────────
type ModelType = 'helio' | 'geo' | 'flat';

const SUN_COLOR = '#FFD040';
const MOON_COLOR = '#C8C8D0';

interface PlanetDef {
  name: string;
  color: string;
  radius: number;
  period: number;
  size: number;
}

const PLANETS: PlanetDef[] = [
  { name: 'Mercure', color: '#A0A0A0', radius: 2.0, period: 0.24, size: 0.10 },
  { name: 'Vénus',   color: '#E8C060', radius: 3.0, period: 0.62, size: 0.13 },
  { name: 'Terre',   color: '#4488CC', radius: 4.2, period: 1.00, size: 0.14 },
  { name: 'Mars',    color: '#CC6644', radius: 5.5, period: 1.88, size: 0.11 },
  { name: 'Jupiter', color: '#C8A060', radius: 7.5, period: 11.86, size: 0.28 },
];

// ─── Orbit Ring ─────────────────────────────────────
function OrbitRing({ radius, color = '#00C8FF', opacity = 0.15 }: {
  radius: number; color?: string; opacity?: number;
}) {
  const pts = useMemo(() => {
    const arr: THREE.Vector3[] = [];
    for (let i = 0; i <= 128; i++) {
      const a = (i / 128) * Math.PI * 2;
      arr.push(new THREE.Vector3(Math.cos(a) * radius, 0, Math.sin(a) * radius));
    }
    return arr;
  }, [radius]);
  return <Line points={pts} color={color} opacity={opacity} transparent lineWidth={0.5} />;
}

// ─── Label HTML flottant ────────────────────────────
function Label({ text, color = '#C8D8E8', show = true }: { text: string; color?: string; show?: boolean }) {
  if (!show) return null;
  return (
    <Html center distanceFactor={15} style={{ pointerEvents: 'none' }}>
      <div style={{
        color, fontSize: '9px', fontFamily: 'monospace',
        textShadow: '0 0 4px rgba(0,0,0,0.8)', whiteSpace: 'nowrap',
        letterSpacing: '0.05em', transform: 'translateY(-16px)',
      }}>
        {text}
      </div>
    </Html>
  );
}

// ─── HUD Grid ───────────────────────────────────────
function HudGrid() {
  const lines = useMemo(() => {
    const arr: THREE.Vector3[][] = [];
    for (let i = -12; i <= 12; i += 2) {
      arr.push([new THREE.Vector3(i, -0.01, -12), new THREE.Vector3(i, -0.01, 12)]);
      arr.push([new THREE.Vector3(-12, -0.01, i), new THREE.Vector3(12, -0.01, i)]);
    }
    return arr;
  }, []);
  return <>{lines.map((p, i) => <Line key={i} points={p} color="#00C8FF" opacity={0.04} transparent lineWidth={0.5} />)}</>;
}

// ═══════════════════════════════════════════════════
// SCENE 1 : HÉLIOCENTRIQUE
// ═══════════════════════════════════════════════════
function HelioScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const planetRefs = useRef<(THREE.Group | null)[]>([]);
  const moonRef = useRef<THREE.Group>(null);
  const sunLightRef = useRef<THREE.PointLight>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.3;
    PLANETS.forEach((p, i) => {
      const ref = planetRefs.current[i];
      if (!ref) return;
      const a = (t / p.period) * Math.PI * 2;
      ref.position.set(Math.cos(a) * p.radius, 0, Math.sin(a) * p.radius);
    });
    if (moonRef.current && planetRefs.current[2]) {
      const e = planetRefs.current[2]!.position;
      const ma = t * 13.37;
      moonRef.current.position.set(e.x + Math.cos(ma) * 0.5, 0, e.z + Math.sin(ma) * 0.5);
    }
  });

  return (
    <group>
      {/* Soleil */}
      <group>
        <mesh><sphereGeometry args={[0.45, 32, 32]} /><meshStandardMaterial color={SUN_COLOR} emissive={SUN_COLOR} emissiveIntensity={1.5} /></mesh>
        <mesh><sphereGeometry args={[0.9, 16, 16]} /><meshBasicMaterial color={SUN_COLOR} transparent opacity={0.06} /></mesh>
        <pointLight ref={sunLightRef} intensity={2} color={SUN_COLOR} distance={20} />
        <Label text="Soleil" color={SUN_COLOR} show={showLabels} />
      </group>

      {PLANETS.map(p => <OrbitRing key={`o-${p.name}`} radius={p.radius} />)}

      {PLANETS.map((p, i) => (
        <group key={p.name} ref={el => { planetRefs.current[i] = el; }}>
          <mesh><sphereGeometry args={[p.size, 20, 20]} /><meshStandardMaterial color={p.color} roughness={0.6} /></mesh>
          <Label text={p.name} color={p.color} show={showLabels} />
        </group>
      ))}

      <group ref={moonRef}>
        <mesh><sphereGeometry args={[0.05, 16, 16]} /><meshStandardMaterial color={MOON_COLOR} roughness={0.4} /></mesh>
        <Label text="Lune" color={MOON_COLOR} show={showLabels} />
      </group>
    </group>
  );
}

// ═══════════════════════════════════════════════════
// SCENE 2 : GÉOCENTRIQUE (tout autour de la Terre)
// ═══════════════════════════════════════════════════
function GeoScene({ speed, showLabels }: { speed: number; showLabels: boolean }) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group | null)[]>([]);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime() * speed * 0.3;

    // Soleil : orbite autour de la Terre (1 tour = 1 an)
    const sunAngle = t * Math.PI * 2;
    if (sunRef.current) {
      sunRef.current.position.set(Math.cos(sunAngle) * 4.0, 0, Math.sin(sunAngle) * 4.0);
    }

    // Lune : orbite autour de la Terre (13 tours / an)
    if (moonRef.current) {
      const ma = t * 13.37;
      moonRef.current.position.set(Math.cos(ma) * 1.3, 0, Math.sin(ma) * 1.3);
    }

    // TOUTES les planètes orbitent autour de la Terre
    // Avec des épicycles pour reproduire les rétrogradations
    PLANETS.forEach((p, i) => {
      const ref = planetRefs.current[i];
      if (!ref || i === 2) return; // Terre = centre

      // Déférent : grand cercle autour de la Terre
      const deferentAngle = (t / p.period) * Math.PI * 2;
      const deferentR = p.radius;

      // Épicycle : petit cercle pour simuler la rétrogradation
      // Rayon de l'épicycle proportionnel à la distance
      const epicycleR = i < 2 ? deferentR * 0.6 : 1.2;
      const epicycleAngle = sunAngle; // lié au mouvement du Soleil

      const x = Math.cos(deferentAngle) * deferentR + Math.cos(epicycleAngle) * epicycleR * (i < 2 ? 1 : 0.3);
      const z = Math.sin(deferentAngle) * deferentR + Math.sin(epicycleAngle) * epicycleR * (i < 2 ? 1 : 0.3);
      ref.position.set(x, 0, z);
    });
  });

  return (
    <group>
      {/* Terre au centre */}
      <group>
        <mesh><sphereGeometry args={[0.2, 24, 24]} /><meshStandardMaterial color="#4488CC" roughness={0.5} /></mesh>
        <Label text="Terre" color="#4488CC" show={showLabels} />
      </group>

      {/* Soleil */}
      <OrbitRing radius={4.0} color="#FFD040" opacity={0.12} />
      <group ref={sunRef}>
        <mesh><sphereGeometry args={[0.35, 32, 32]} /><meshStandardMaterial color={SUN_COLOR} emissive={SUN_COLOR} emissiveIntensity={1.5} /></mesh>
        <mesh><sphereGeometry args={[0.7, 16, 16]} /><meshBasicMaterial color={SUN_COLOR} transparent opacity={0.06} /></mesh>
        <pointLight intensity={2} color={SUN_COLOR} distance={20} />
        <Label text="Soleil" color={SUN_COLOR} show={showLabels} />
      </group>

      {/* Lune */}
      <OrbitRing radius={1.3} color="#C8C8D0" opacity={0.1} />
      <group ref={moonRef}>
        <mesh><sphereGeometry args={[0.07, 16, 16]} /><meshStandardMaterial color={MOON_COLOR} roughness={0.4} /></mesh>
        <Label text="Lune" color={MOON_COLOR} show={showLabels} />
      </group>

      {/* Planètes — toutes autour de la Terre */}
      {PLANETS.map((p, i) => {
        if (i === 2) return null;
        return (
          <group key={p.name}>
            <OrbitRing radius={p.radius} opacity={0.08} />
            <group ref={el => { planetRefs.current[i] = el; }}>
              <mesh><sphereGeometry args={[p.size, 20, 20]} /><meshStandardMaterial color={p.color} roughness={0.6} /></mesh>
              <Label text={p.name} color={p.color} show={showLabels} />
            </group>
          </group>
        );
      })}
    </group>
  );
}

// ═══════════════════════════════════════════════════
// SCENE 3 : TERRE PLANE (inspiré Flat Earth App)
// Texture carte AE + astronomy-engine + slider temporel
// ═══════════════════════════════════════════════════

function FlatScene({ speed, showLabels, simDate }: {
  speed: number; showLabels: boolean; simDate: Date;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const spotRef = useRef<THREE.SpotLight>(null);
  const planetRefsFlat = useRef<(THREE.Group | null)[]>([]);
  const timeOffset = useRef(0);
  const mapTexture = useMemo(() => new THREE.TextureLoader().load('/textures/flat-earth-ae-map.png'), []);

  const DISC_R = 5.8;
  const SUN_H = 3.5;
  const MOON_H = 3.0;

  useFrame(({ clock }) => {
    const dt = clock.getDelta() * speed;
    timeOffset.current += dt;
    // 1 seconde réelle ≈ 30 minutes simulées à vitesse ×1
    const offsetMs = timeOffset.current * 30 * 60 * 1000;
    const currentDate = new Date(simDate.getTime() + offsetMs);

    const positions = getAllPositions(currentDate);

    // Soleil
    const [sx, sz] = latLngToFlatDisc(positions.sun.lat, positions.sun.lng, DISC_R);
    if (sunRef.current) sunRef.current.position.set(sx, SUN_H, sz);
    if (spotRef.current) {
      spotRef.current.position.set(sx, SUN_H, sz);
      spotRef.current.target.position.set(sx * 0.7, 0, sz * 0.7);
      spotRef.current.target.updateMatrixWorld();
    }

    // Lune
    const [mx, mz] = latLngToFlatDisc(positions.moon.lat, positions.moon.lng, DISC_R);
    if (moonRef.current) moonRef.current.position.set(mx, MOON_H, mz);

    // Planètes
    positions.planets.forEach((p, i) => {
      const ref = planetRefsFlat.current[i];
      if (!ref) return;
      const [px, pz] = latLngToFlatDisc(p.lat, p.lng, DISC_R);
      ref.position.set(px, 3.2 + i * 0.15, pz);
    });
  });

  // Positions initiales pour créer les refs planètes
  const initialPositions = useMemo(() => getAllPositions(simDate), [simDate]);

  return (
    <group>
      <ambientLight intensity={0.02} />

      {/* Disque terrestre avec texture carte AE */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
        <circleGeometry args={[DISC_R, 128]} />
        <meshStandardMaterial
          map={mapTexture}
          roughness={0.7}
          transparent
        />
      </mesh>

      {/* Soleil */}
      <group ref={sunRef} position={[0, SUN_H, 0]}>
        <mesh>
          <sphereGeometry args={[0.22, 32, 32]} />
          <meshStandardMaterial color={SUN_COLOR} emissive={SUN_COLOR} emissiveIntensity={2} />
        </mesh>
        <mesh>
          <sphereGeometry args={[0.5, 16, 16]} />
          <meshBasicMaterial color={SUN_COLOR} transparent opacity={0.08} />
        </mesh>
        <pointLight intensity={3} color={SUN_COLOR} distance={10} />
        <Label text="Soleil ☉" color={SUN_COLOR} show={showLabels} />
      </group>

      {/* Spotlight jour/nuit — cône lumineux principal */}
      <spotLight
        ref={spotRef}
        intensity={8}
        color="#FFF8E0"
        distance={12}
        angle={Math.PI / 2.8}
        penumbra={0.5}
        position={[0, SUN_H, 0]}
      />

      {/* Lune */}
      <group ref={moonRef} position={[0, MOON_H, 0]}>
        <mesh>
          <sphereGeometry args={[0.12, 24, 24]} />
          <meshStandardMaterial color={MOON_COLOR} roughness={0.3} emissive={MOON_COLOR} emissiveIntensity={0.15} />
        </mesh>
        <Label text="Lune ☾" color={MOON_COLOR} show={showLabels} />
      </group>

      {/* Planètes */}
      {initialPositions.planets.map((p, i) => (
        <group key={p.name} ref={el => { planetRefsFlat.current[i] = el; }}>
          <mesh>
            <sphereGeometry args={[p.size, 16, 16]} />
            <meshStandardMaterial color={p.color} emissive={p.color} emissiveIntensity={0.4} roughness={0.5} />
          </mesh>
          <Label text={p.name} color={p.color} show={showLabels} />
        </group>
      ))}

      {/* Tropiques (cercles en hauteur) */}
      {[1.5, 2.2, 2.8, 3.5].map((r, i) => (
        <group key={`or-${i}`} position={[0, SUN_H, 0]}>
          <OrbitRing radius={r} color="#FFD040" opacity={0.04} />
        </group>
      ))}

      {/* Dôme céleste (sans étoiles) */}
      <mesh>
        <sphereGeometry args={[9, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshBasicMaterial color="#050A12" transparent opacity={0.3} side={THREE.BackSide} />
      </mesh>
    </group>
  );
}

// ═══════════════════════════════════════════════════
// COMPOSANT PRINCIPAL
// ═══════════════════════════════════════════════════
export default function GeoHelioSim() {
  const [mode, setMode] = useState<ModelType>('helio');
  const [speed, setSpeed] = useState(1);
  const [showLabels, setShowLabels] = useState(true);

  // Play/Pause pour l'animation Terre Plane
  const [isPlaying, setIsPlaying] = useState(true);
  const simDate = useMemo(() => new Date(), []);

  const flatPositions = useMemo(() => {
    if (mode !== 'flat') return null;
    return getAllPositions(simDate);
  }, [mode, simDate]);

  const modeConfig = {
    helio: { label: 'HÉLIOCENTRIQUE', color: '#00C8FF', cam: [0, 12, 8] as [number, number, number], desc: 'Centre : Soleil — Terre en orbite' },
    geo:   { label: 'GÉOCENTRIQUE',   color: '#D4A843', cam: [0, 12, 8] as [number, number, number], desc: 'Centre : Terre — tous les astres en orbite' },
    flat:  { label: 'TERRE PLANE',    color: '#00E87B', cam: [6, 7, 6] as [number, number, number],  desc: 'Disque terrestre — astres au-dessus (éphémérides réelles)' },
  };
  const cfg = modeConfig[mode];

  return (
    <div className="w-full">
      {/* Contrôles */}
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <div className="flex gap-1">
          {(Object.entries(modeConfig) as [ModelType, typeof cfg][]).map(([id, c]) => (
            <button key={id} onClick={() => setMode(id)}
              className="px-3 md:px-4 py-2 text-[8px] md:text-[9px] font-orbitron tracking-widest border transition-all"
              style={{
                clipPath: 'polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)',
                borderColor: mode === id ? `${c.color}99` : '#334155',
                backgroundColor: mode === id ? `${c.color}1a` : 'transparent',
                color: mode === id ? c.color : '#64748b',
              }}
            >{c.label}</button>
          ))}
        </div>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-[8px] font-tech-mono text-slate-500">VIT.</span>
          <input type="range" min={0.1} max={5} step={0.1} value={speed}
            onChange={(e) => setSpeed(parseFloat(e.target.value))}
            className="w-16 md:w-20 accent-[#00C8FF]" />
          <span className="text-[8px] font-tech-mono text-[#00C8FF]">&times;{speed.toFixed(1)}</span>
        </div>

        <button onClick={() => setShowLabels(!showLabels)}
          className={`px-3 py-1 text-[8px] font-tech-mono border ${showLabels ? 'border-slate-600 text-slate-400' : 'border-slate-800 text-slate-600'}`}
        >NOMS: {showLabels ? 'ON' : 'OFF'}</button>
      </div>

      {/* Play/Pause — mode Terre Plane */}
      {mode === 'flat' && (
        <div className="flex items-center gap-3 mb-3">
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="px-4 py-2 text-[9px] font-tech-mono tracking-widest border transition-all"
            style={{
              borderColor: isPlaying ? '#00E87B99' : '#D4A84399',
              backgroundColor: isPlaying ? '#00E87B1a' : '#D4A8431a',
              color: isPlaying ? '#00E87B' : '#D4A843',
            }}
          >
            {isPlaying ? '⏸ PAUSE' : '▶ LECTURE'}
          </button>
          <span className="text-[8px] font-tech-mono text-slate-500">
            {isPlaying ? 'Animation en cours — 1s ≈ 30 min' : 'Animation en pause'}
          </span>
        </div>
      )}

      {/* Canvas 3D */}
      <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        {/* Overlay info */}
        <div className="absolute top-3 left-3 z-10">
          <div className="text-[9px] font-tech-mono tracking-widest" style={{ color: `${cfg.color}99` }}>
            ◉ {cfg.label}
          </div>
          <div className="text-[8px] font-tech-mono text-slate-600 mt-1">{cfg.desc}</div>
        </div>

        {mode === 'flat' && flatPositions && (
          <div className="absolute top-3 right-3 z-10 text-right">
            <div className="text-[8px] font-tech-mono text-[#D4A843]/60">
              ☾ PHASE : {flatPositions.moonIllumination.toFixed(1)}%
            </div>
            <div className="text-[8px] font-tech-mono text-slate-600">
              ☉ Déc: {flatPositions.sun.lat.toFixed(1)}° | ☾ Déc: {flatPositions.moon.lat.toFixed(1)}°
            </div>
          </div>
        )}

        <Canvas camera={{ position: cfg.cam, fov: 50 }} key={mode}>
          <ambientLight intensity={mode === 'flat' ? 0.04 : 0.15} />
          {mode !== 'flat' && <HudGrid />}

          {mode === 'helio' && <HelioScene speed={speed} showLabels={showLabels} />}
          {mode === 'geo' && <GeoScene speed={speed} showLabels={showLabels} />}
          {mode === 'flat' && <FlatScene speed={isPlaying ? speed : 0} showLabels={showLabels} simDate={simDate} />}

          <OrbitControls enablePan={false} minDistance={4} maxDistance={25}
            maxPolarAngle={mode === 'flat' ? Math.PI * 0.48 : Math.PI * 0.85} />
        </Canvas>
      </div>

      {/* Panneau */}
      <div className="mt-3 border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[9px] font-tech-mono tracking-widest mb-2" style={{ color: `${cfg.color}66` }}>
          ANALYSE // {cfg.label}
        </div>
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          {mode === 'helio' && "Mod\u00e8le h\u00e9liocentrique (Copernic, 1543) : la Terre orbite autour du Soleil. Les m\u00eames mouvements apparents \u2014 phases, r\u00e9trogradations, saisons \u2014 sont observ\u00e9s depuis la Terre. Ce mod\u00e8le est cin\u00e9matiquement \u00e9quivalent au mod\u00e8le g\u00e9ocentrique."}
          {mode === 'geo' && "Mod\u00e8le g\u00e9ocentrique pur (Ptol\u00e9m\u00e9e) : la Terre est au centre de l\u2019univers. Tous les astres \u2014 Soleil, Lune, plan\u00e8tes \u2014 orbitent autour d\u2019elle. Les \u00e9picycles (cercles sur cercles) reproduisent les mouvements r\u00e9trogrades observ\u00e9s. Ce mod\u00e8le a servi la navigation et l\u2019astronomie pendant 1\u2009400 ans."}
          {mode === 'flat' && "Mod\u00e8le Terre plane (MGPP) : le disque terrestre est stationnaire sous un d\u00f4me c\u00e9leste. Le Soleil et la Lune circulent au-dessus \u00e0 quelques milliers de km. Les positions sont calcul\u00e9es avec la biblioth\u00e8que Astronomy Engine (\u00e9ph\u00e9m\u00e9rides pr\u00e9cises), puis projet\u00e9es sur la carte azimutale \u00e9quidistante. Le slider temporel permet de voyager \u00b1 7 jours."}
        </p>
        <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
          <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">L&apos;hypothèse nulle &rarr;</a>
          <a href="/article/200-ans-de-resultats-nuls-darago-a-einstein" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">200 ans de r&eacute;sultats nuls &rarr;</a>
          {mode === 'flat' && <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[#00E87B]/50 hover:text-[#00E87B] transition-colors">Le MGPP &rarr;</a>}
        </div>
      </div>
    </div>
  );
}
