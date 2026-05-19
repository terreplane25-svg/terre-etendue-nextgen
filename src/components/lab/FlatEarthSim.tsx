'use client';
import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame, useLoader } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
import * as THREE from 'three';
import { getAllPositions, latLngToFlatDisc } from './celestialCalc';

const SUN_C = '#FFD040';
const MOON_C = '#C8C8D0';
const DISC_R = 6;

function Label({ text, color = '#C8D8E8', show = true }: { text: string; color?: string; show?: boolean }) {
  if (!show) return null;
  return (
    <Html center distanceFactor={10} style={{ pointerEvents: 'none' }}>
      <div style={{ color, fontSize: '10px', fontFamily: 'monospace', textShadow: '0 0 6px rgba(0,0,0,0.9)', whiteSpace: 'nowrap', fontWeight: 'bold' }}>
        {text}
      </div>
    </Html>
  );
}

function FlatScene({ speed, showLabels, isPlaying }: {
  speed: number; showLabels: boolean; isPlaying: boolean;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group | null)[]>([]);
  const dayZoneRef = useRef<THREE.Mesh>(null);
  const timeOffset = useRef(0);

  const mapTexture = useMemo(() => new THREE.TextureLoader().load('/textures/ae-map.jpg'), []);

  const SUN_H = 0.3;  // Juste au-dessus du disque (vue du dessus)
  const MOON_H = 0.25;
  const PLANET_H = 0.2;

  useFrame(() => {
    if (!isPlaying) return;
    const dt = 0.016 * speed; // ~60fps
    timeOffset.current += dt;
    // 1 seconde réelle à speed 1 ≈ 30 minutes simulées
    const offsetMs = timeOffset.current * 30 * 60 * 1000;
    const simDate = new Date(Date.now() + offsetMs);
    const pos = getAllPositions(simDate);

    // Soleil
    const [sx, sz] = latLngToFlatDisc(pos.sun.lat, pos.sun.lng, DISC_R);
    if (sunRef.current) sunRef.current.position.set(sx, SUN_H, sz);

    // Zone éclairée — disque semi-transparent qui suit le soleil
    if (dayZoneRef.current) {
      dayZoneRef.current.position.set(sx * 0.85, 0.01, sz * 0.85);
    }

    // Lune
    const [mx, mz] = latLngToFlatDisc(pos.moon.lat, pos.moon.lng, DISC_R);
    if (moonRef.current) moonRef.current.position.set(mx, MOON_H, mz);

    // Planètes
    pos.planets.forEach((p, i) => {
      const ref = planetRefs.current[i];
      if (!ref) return;
      const [px, pz] = latLngToFlatDisc(p.lat, p.lng, DISC_R);
      ref.position.set(px, PLANET_H, pz);
    });
  });

  const initPos = useMemo(() => getAllPositions(new Date()), []);

  return (
    <group>
      {/* Lumière ambiante douce */}
      <ambientLight intensity={0.35} />

      {/* Disque terrestre — texture satellite AE */}
      <mesh rotation={[-Math.PI / 2, 0, 0]} position={[0, 0, 0]}>
        <circleGeometry args={[DISC_R, 128]} />
        <meshBasicMaterial map={mapTexture} />
      </mesh>

      {/* Zone éclairée — disque doré semi-transparent */}
      <mesh ref={dayZoneRef} rotation={[-Math.PI / 2, 0, 0]} position={[0, 0.01, 0]}>
        <circleGeometry args={[DISC_R * 0.55, 64]} />
        <meshBasicMaterial color="#FFE880" transparent opacity={0.12} />
      </mesh>

      {/* Soleil */}
      <group ref={sunRef} position={[0, SUN_H, 0]}>
        <mesh>
          <circleGeometry args={[0.25, 32]} />
          <meshBasicMaterial color={SUN_C} side={THREE.DoubleSide} />
        </mesh>
        {/* Halo */}
        <mesh>
          <circleGeometry args={[0.5, 32]} />
          <meshBasicMaterial color={SUN_C} transparent opacity={0.15} side={THREE.DoubleSide} />
        </mesh>
        <Label text="Soleil ☉" color={SUN_C} show={showLabels} />
      </group>

      {/* Lune */}
      <group ref={moonRef} position={[0, MOON_H, 0]}>
        <mesh>
          <circleGeometry args={[0.12, 24]} />
          <meshBasicMaterial color={MOON_C} side={THREE.DoubleSide} />
        </mesh>
        <Label text="Lune ☾" color={MOON_C} show={showLabels} />
      </group>

      {/* Planètes */}
      {initPos.planets.map((p, i) => (
        <group key={p.name} ref={el => { planetRefs.current[i] = el; }}>
          <mesh rotation={[-Math.PI / 2, 0, 0]}>
            <circleGeometry args={[p.size * 0.7, 16]} />
            <meshBasicMaterial color={p.color} side={THREE.DoubleSide} />
          </mesh>
          <Label text={p.name} color={p.color} show={showLabels} />
        </group>
      ))}
    </group>
  );
}

export default function FlatEarthSim() {
  const [speed, setSpeed] = useState(1);
  const [showLabels, setShowLabels] = useState(true);
  const [isPlaying, setIsPlaying] = useState(true);

  return (
    <div className="w-full">
      <div className="flex flex-wrap items-center gap-2 mb-3">
        <button onClick={() => setIsPlaying(!isPlaying)}
          className="px-4 py-2 text-[9px] font-tech-mono tracking-widest border transition-all"
          style={{
            borderColor: isPlaying ? '#00E87B99' : '#D4A84399',
            backgroundColor: isPlaying ? '#00E87B1a' : '#D4A8431a',
            color: isPlaying ? '#00E87B' : '#D4A843',
          }}
        >{isPlaying ? '⏸ PAUSE' : '▶ LECTURE'}</button>

        <div className="flex items-center gap-2 ml-auto">
          <span className="text-[8px] font-tech-mono text-slate-500">VIT.</span>
          <input type="range" min={0.1} max={5} step={0.1} value={speed}
            onChange={e => setSpeed(+e.target.value)} className="w-16 md:w-20 accent-[#00C8FF]" />
          <span className="text-[8px] font-tech-mono text-[#00C8FF]">&times;{speed.toFixed(1)}</span>
        </div>

        <button onClick={() => setShowLabels(!showLabels)}
          className={`px-3 py-1 text-[8px] font-tech-mono border ${showLabels ? 'border-slate-600 text-slate-400' : 'border-slate-800 text-slate-600'}`}
        >NOMS: {showLabels ? 'ON' : 'OFF'}</button>
      </div>

      <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        <div className="absolute top-3 left-3 z-10">
          <div className="text-[9px] font-tech-mono text-[#00E87B]/80 tracking-widest">◉ TERRE PLANE — VUE DU DESSUS</div>
          <div className="text-[8px] font-tech-mono text-slate-600 mt-1">Positions : Astronomy Engine (éphémérides précises)</div>
        </div>

        <Canvas camera={{ position: [0, 12, 0.1], fov: 50 }} >
          <FlatScene speed={speed} showLabels={showLabels} isPlaying={isPlaying} />
          <OrbitControls
            enablePan={false}
            minDistance={6}
            maxDistance={20}
            minPolarAngle={0}
            maxPolarAngle={Math.PI * 0.3}
          />
        </Canvas>
      </div>

      <div className="mt-3 border border-slate-800/50 bg-[#0A1020] p-4">
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          Modèle Terre plane (MGPP) : la carte en projection azimutale équidistante, pôle Nord au centre, anneau glacé antarctique en bordure. Le Soleil et la Lune circulent au-dessus du disque. La zone éclairée suit le Soleil. Toutes les positions sont calculées avec Astronomy Engine.
        </p>
        <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
          <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF]">Le MGPP →</a>
          <a href="/article/le-theodolite-celeste" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF]">Le théodolite céleste →</a>
        </div>
      </div>
    </div>
  );
}
