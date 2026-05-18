'use client';

import React, { useRef, useState, useMemo, useEffect, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';
import {
  getSunDeclination, getSunLongitude,
  getMoonDeclination, getMoonLongitude, getMoonPhase,
  getPlanetPositions, latLngToFlatDisc,
  getCurrentTimeInfo,
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
// ═══════════════════════════════════════════════════

// (FlatEarthDisc intégré directement dans FlatScene)

// Ellipse geometry intégrée inline dans FlatScene

function FlatScene({ speed, showLabels, simTime }: {
  speed: number; showLabels: boolean; simTime: { dayOfYear: number; hoursUTC: number };
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const spotRef = useRef<THREE.SpotLight>(null);
  const planetRefsFlat = useRef<(THREE.Group | null)[]>([]);
  const timeOffset = useRef(0);

  const DISC_R = 5.5;
  const SUN_H = 3.5;
  const MOON_H = 3.0;

  useFrame(({ clock }) => {
    const dt = clock.getDelta() * speed;
    timeOffset.current += dt;
    const offsetHours = timeOffset.current * 0.5; // 1s réel ≈ 0.5h sim

    const day = simTime.dayOfYear;
    const h = (simTime.hoursUTC + offsetHours) % 24;

    // Soleil
    const sunLat = getSunDeclination(day);
    const sunLng = getSunLongitude(h);
    const [sx, sz] = latLngToFlatDisc(sunLat, sunLng, DISC_R);
    if (sunRef.current) {
      sunRef.current.position.set(sx, SUN_H, sz);
    }
    if (spotRef.current) {
      spotRef.current.position.set(sx, SUN_H, sz);
      spotRef.current.target.position.set(sx * 0.7, 0, sz * 0.7);
      spotRef.current.target.updateMatrixWorld();
    }

    // Lune
    const moonLat = getMoonDeclination(day);
    const moonLng = getMoonLongitude(h, day);
    const [mx, mz] = latLngToFlatDisc(moonLat, moonLng, DISC_R);
    if (moonRef.current) {
      moonRef.current.position.set(mx, MOON_H, mz);
    }

    // Planètes
    const planets = getPlanetPositions(day, h);
    planets.forEach((p, i) => {
      const ref = planetRefsFlat.current[i];
      if (!ref) return;
      const [px, pz] = latLngToFlatDisc(p.lat, p.lng, DISC_R);
      const ph = 3.2 + i * 0.15;
      ref.position.set(px, ph, pz);
    });
  });

  const planets = getPlanetPositions(simTime.dayOfYear, simTime.hoursUTC);

  return (
    <group>
      <ambientLight intensity={0.06} />

      {/* Disque terrestre */}
      <group>
        {/* Océan */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.05, 0]}>
          <circleGeometry args={[6.2, 64]} />
          <meshStandardMaterial color="#0a2a4a" roughness={0.6} />
        </mesh>
        {/* Anneau glacé */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.04, 0]}>
          <ringGeometry args={[5.6, 6.3, 64]} />
          <meshStandardMaterial color="#c8dce8" roughness={0.3} />
        </mesh>
        {/* Pôle Nord */}
        <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, -0.02, 0]}>
          <circleGeometry args={[0.2, 16]} />
          <meshStandardMaterial color="#e0e8f0" roughness={0.3} />
        </mesh>
        {/* Continents simplifiés */}
        {[
          [-1.8, -1.5, 0.65, 0.75, '#3a6a30'],
          [-1.2, 1.2, 0.3, 0.72, '#4a7a3a'],
          [1.2, -0.8, 0.85, 0.65, '#4a7030'],
          [1.5, 1.5, 0.42, 0.5, '#5a7a2a'],
          [3.2, 1.5, 0.3, 0.22, '#7a8a40'],
        ].map(([x, z, rx, rz, c], i) => {
          const shape = new THREE.Shape();
          for (let j = 0; j <= 24; j++) {
            const a = (j / 24) * Math.PI * 2;
            const px = Math.cos(a) * (rx as number);
            const py = Math.sin(a) * (rz as number);
            j === 0 ? shape.moveTo(px, py) : shape.lineTo(px, py);
          }
          return (
            <mesh key={i} rotation={[-Math.PI / 2, 0, 0]} position={[x as number, -0.01, z as number]}>
              <shapeGeometry args={[shape]} />
              <meshStandardMaterial color={c as string} roughness={0.7} />
            </mesh>
          );
        })}
      </group>

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
        <pointLight intensity={1.5} color={SUN_COLOR} distance={8} />
        <Label text="Soleil ☉" color={SUN_COLOR} show={showLabels} />
      </group>

      {/* Spotlight jour/nuit */}
      <spotLight
        ref={spotRef}
        intensity={4}
        color="#FFF5D0"
        distance={10}
        angle={Math.PI / 3}
        penumbra={0.7}
        position={[0, SUN_H, 0]}
      />

      {/* Lune */}
      <group ref={moonRef} position={[0, MOON_H, 0]}>
        <mesh>
          <sphereGeometry args={[0.12, 24, 24]} />
          <meshStandardMaterial color={MOON_COLOR} roughness={0.3} />
        </mesh>
        <Label text="Lune ☾" color={MOON_COLOR} show={showLabels} />
      </group>

      {/* Planètes */}
      {planets.map((p, i) => (
        <group key={p.name} ref={el => { planetRefsFlat.current[i] = el; }}>
          <mesh>
            <sphereGeometry args={[p.size * 0.4, 16, 16]} />
            <meshStandardMaterial color={p.color} emissive={p.color} emissiveIntensity={0.3} roughness={0.5} />
          </mesh>
          <Label text={p.name} color={p.color} show={showLabels} />
        </group>
      ))}

      {/* Orbites en hauteur (tropiques) */}
      {[1.5, 2.2, 2.8, 3.5].map((r, i) => (
        <group key={`or-${i}`} position={[0, SUN_H, 0]}>
          <OrbitRing radius={r} color="#FFD040" opacity={0.04} />
        </group>
      ))}

      {/* Dôme céleste */}
      <mesh>
        <sphereGeometry args={[8.5, 32, 16, 0, Math.PI * 2, 0, Math.PI / 2]} />
        <meshBasicMaterial color="#060818" transparent opacity={0.2} side={THREE.BackSide} />
      </mesh>

      {/* Étoiles */}
      {useMemo(() => {
        const stars: React.ReactNode[] = [];
        for (let i = 0; i < 300; i++) {
          const theta = Math.random() * Math.PI * 2;
          const phi = Math.random() * Math.PI * 0.48;
          const r = 8.2;
          const pos: [number, number, number] = [
            Math.sin(phi) * Math.cos(theta) * r,
            Math.cos(phi) * r,
            Math.sin(phi) * Math.sin(theta) * r,
          ];
          stars.push(
            <mesh key={i} position={pos}>
              <sphereGeometry args={[0.015 + Math.random() * 0.01, 4, 4]} />
              <meshBasicMaterial color="#ffffff" transparent opacity={0.3 + Math.random() * 0.5} />
            </mesh>
          );
        }
        return stars;
      }, [])}
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

  const [simTime, setSimTime] = useState(() => getCurrentTimeInfo());

  // Pour Terre Plane : afficher la date/heure simulée
  const moonPhase = getMoonPhase(simTime.dayOfYear);
  const phasePercent = (moonPhase * 100).toFixed(1);

  const modeConfig = {
    helio: { label: 'HÉLIOCENTRIQUE', color: '#00C8FF', cam: [0, 12, 8] as [number, number, number], desc: 'Centre : Soleil — Terre en orbite' },
    geo:   { label: 'GÉOCENTRIQUE',   color: '#D4A843', cam: [0, 12, 8] as [number, number, number], desc: 'Centre : Terre — tous les astres en orbite' },
    flat:  { label: 'TERRE PLANE',    color: '#00E87B', cam: [6, 7, 6] as [number, number, number],  desc: 'Disque terrestre — astres au-dessus (positions réelles)' },
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
          <span className="text-[8px] font-tech-mono text-[#00C8FF]">×{speed.toFixed(1)}</span>
        </div>

        <button onClick={() => setShowLabels(!showLabels)}
          className={`px-3 py-1 text-[8px] font-tech-mono border ${showLabels ? 'border-slate-600 text-slate-400' : 'border-slate-800 text-slate-600'}`}
        >NOMS: {showLabels ? 'ON' : 'OFF'}</button>
      </div>

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

        {mode === 'flat' && (
          <div className="absolute top-3 right-3 z-10 text-right">
            <div className="text-[8px] font-tech-mono text-[#D4A843]/60">PHASE LUNAIRE : {phasePercent}%</div>
            <div className="text-[8px] font-tech-mono text-slate-600">
              Jour {simTime.dayOfYear} — {simTime.hoursUTC.toFixed(1)}h UTC
            </div>
          </div>
        )}

        <Canvas camera={{ position: cfg.cam, fov: 50 }} key={mode}>
          <ambientLight intensity={mode === 'flat' ? 0.04 : 0.15} />
          {mode !== 'flat' && <HudGrid />}

          {mode === 'helio' && <HelioScene speed={speed} showLabels={showLabels} />}
          {mode === 'geo' && <GeoScene speed={speed} showLabels={showLabels} />}
          {mode === 'flat' && <FlatScene speed={speed} showLabels={showLabels} simTime={simTime} />}

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
          {mode === 'helio' && "Modèle héliocentrique (Copernic, 1543) : la Terre orbite autour du Soleil. Les mêmes mouvements apparents — phases, rétrogradations, saisons — sont observés depuis la Terre. Ce modèle est cinématiquement équivalent au modèle géocentrique."}
          {mode === 'geo' && "Modèle géocentrique pur (Ptolémée) : la Terre est au centre de l\u2019univers. Tous les astres — Soleil, Lune, planètes — orbitent autour d\u2019elle. Les épicycles (cercles sur cercles) reproduisent les mouvements rétrogrades observés. Ce modèle a servi la navigation et l\u2019astronomie pendant 1\u2009400 ans."}
          {mode === 'flat' && "Modèle Terre plane (MGPP) : le disque terrestre est stationnaire sous un dôme céleste. Le Soleil et la Lune circulent au-dessus à quelques milliers de km, créant le cycle jour/nuit par déplacement de leur cône lumineux. Les positions affichées sont calculées à partir des éphémérides astronomiques réelles (déclinaison, longitude), projetées sur la carte azimutale équidistante."}
        </p>
        <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
          <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">L&apos;hypothèse nulle →</a>
          <a href="/article/200-ans-de-resultats-nuls-darago-a-einstein" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">200 ans de résultats nuls →</a>
          {mode === 'flat' && <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[#00E87B]/50 hover:text-[#00E87B] transition-colors">Le MGPP →</a>}
        </div>
      </div>
    </div>
  );
}
