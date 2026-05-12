'use client';

import { useRef, useMemo, useState } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Text, Float } from '@react-three/drei';
import * as THREE from 'three';

// ─── Données : Quelques-uns des 99 Noms ──────────
const DIVINE_NAMES = [
  'الرحمن', 'الرحيم', 'الملك', 'القدوس', 'السلام',
  'المؤمن', 'المهيمن', 'العزيز', 'الجبار', 'المتكبر',
  'الخالق', 'البارئ', 'المصور', 'الغفار', 'القهار',
  'الوهاب', 'الرزاق', 'الفتاح', 'العليم', 'القابض',
  'الباسط', 'الخافض', 'الرافع', 'المعز', 'المذل',
  'السميع', 'البصير', 'الحكم', 'العدل', 'اللطيف',
  'الحليم', 'العظيم', 'الغفور', 'الشكور',
];

// ─── Noyau Central : Point de l'Unité ─────────────
function DivineCoreNode() {
  const meshRef = useRef<THREE.Mesh>(null);
  const glowRef = useRef<THREE.Mesh>(null);

  useFrame(({ clock }) => {
    const t = clock.getElapsedTime();
    if (meshRef.current) {
      meshRef.current.scale.setScalar(1 + Math.sin(t * 2) * 0.08);
    }
    if (glowRef.current) {
      (glowRef.current.material as THREE.MeshBasicMaterial).opacity = 0.15 + Math.sin(t * 1.5) * 0.05;
      glowRef.current.scale.setScalar(2.5 + Math.sin(t) * 0.3);
    }
  });

  return (
    <group>
      {/* Glow */}
      <mesh ref={glowRef}>
        <sphereGeometry args={[1, 32, 32]} />
        <meshBasicMaterial color="#D4AF37" transparent opacity={0.15} />
      </mesh>
      {/* Core */}
      <mesh ref={meshRef}>
        <sphereGeometry args={[0.5, 64, 64]} />
        <meshStandardMaterial
          color="#D4AF37"
          emissive="#D4AF37"
          emissiveIntensity={1.2}
          roughness={0.2}
          metalness={0.8}
        />
      </mesh>
    </group>
  );
}

// ─── Orbite Concentrique ──────────────────────────
function ConcentricOrbit({ radius, speed, color, count }: {
  radius: number;
  speed: number;
  color: string;
  count: number;
}) {
  const groupRef = useRef<THREE.Group>(null);

  // Cercle de l'orbite
  const ringGeometry = useMemo(() => {
    const points: THREE.Vector3[] = [];
    for (let i = 0; i <= 128; i++) {
      const angle = (i / 128) * Math.PI * 2;
      points.push(new THREE.Vector3(Math.cos(angle) * radius, 0, Math.sin(angle) * radius));
    }
    return new THREE.BufferGeometry().setFromPoints(points);
  }, [radius]);

  useFrame(({ clock }) => {
    if (groupRef.current) {
      groupRef.current.rotation.y = clock.getElapsedTime() * speed;
    }
  });

  // Particules réparties sur l'orbite
  const particles = useMemo(() => {
    return Array.from({ length: count }, (_, i) => {
      const angle = (i / count) * Math.PI * 2;
      return {
        x: Math.cos(angle) * radius,
        z: Math.sin(angle) * radius,
        name: DIVINE_NAMES[i % DIVINE_NAMES.length],
      };
    });
  }, [radius, count]);

  // Objet Three.js Line (pas l'élément SVG)
  const lineObj = useMemo(() => {
    const mat = new THREE.LineBasicMaterial({ color, transparent: true, opacity: 0.2 });
    return new THREE.Line(ringGeometry, mat);
  }, [ringGeometry, color]);

  return (
    <group>
      {/* Ligne de l'orbite */}
      <primitive object={lineObj} />

      {/* Particules orbitant */}
      <group ref={groupRef}>
        {particles.map((p, i) => (
          <Float key={i} speed={1} floatIntensity={0.3} rotationIntensity={0}>
            <mesh position={[p.x, 0, p.z]}>
              <sphereGeometry args={[0.12, 16, 16]} />
              <meshStandardMaterial
                color={color}
                emissive={color}
                emissiveIntensity={0.6}
              />
            </mesh>
            {/* Nom arabe */}
            <Text
              position={[p.x, 0.35, p.z]}
              fontSize={0.22}
              color={color}
              anchorX="center"
              anchorY="middle"
              fillOpacity={0.7}
            >
              {p.name}
            </Text>
          </Float>
        ))}
      </group>
    </group>
  );
}

// ─── Grille de Fond ───────────────────────────────
function BackgroundGrid() {
  const gridRef = useRef<THREE.GridHelper>(null);

  useFrame(({ clock }) => {
    if (gridRef.current) {
      (gridRef.current.material as THREE.Material).opacity = 0.06 + Math.sin(clock.getElapsedTime() * 0.5) * 0.02;
    }
  });

  return (
    <gridHelper
      ref={gridRef}
      args={[30, 30, '#00D1FF', '#2A3138']}
      position={[0, -2, 0]}
      rotation={[0, 0, 0]}
    />
  );
}

// ─── Contrôles d'affichage ────────────────────────
interface SimulationControlsProps {
  orbits: number;
  setOrbits: (n: number) => void;
  speed: number;
  setSpeed: (n: number) => void;
}

function SimulationControls({ orbits, setOrbits, speed, setSpeed }: SimulationControlsProps) {
  return (
    <div className="absolute top-4 left-4 bg-surface/90 backdrop-blur border border-white/[0.06] rounded-lg p-4 space-y-4 z-10">
      <h4 className="font-display font-semibold text-xs uppercase tracking-widest text-[#E8E4DD]/40">
        Paramètres
      </h4>

      <div className="space-y-2">
        <label className="flex items-center justify-between text-xs text-[#E8E4DD]/40">
          <span>Orbites : {orbits}</span>
        </label>
        <input
          type="range"
          min={1}
          max={7}
          step={1}
          value={orbits}
          onChange={(e) => setOrbits(Number(e.target.value))}
          className="w-full h-1 bg-white/[0.06] rounded-lg appearance-none cursor-pointer accent-accent-gold"
        />
      </div>

      <div className="space-y-2">
        <label className="flex items-center justify-between text-xs text-[#E8E4DD]/40">
          <span>Vitesse : {speed.toFixed(1)}×</span>
        </label>
        <input
          type="range"
          min={0.1}
          max={3}
          step={0.1}
          value={speed}
          onChange={(e) => setSpeed(Number(e.target.value))}
          className="w-full h-1 bg-white/[0.06] rounded-lg appearance-none cursor-pointer accent-accent-cyan"
        />
      </div>
    </div>
  );
}

// ─── Composant Principal ──────────────────────────
export default function TawhidSimulation() {
  const [orbits, setOrbits] = useState(4);
  const [speed, setSpeed] = useState(1);

  const orbitConfigs = useMemo(() => {
    return Array.from({ length: orbits }, (_, i) => ({
      radius: 2 + i * 1.4,
      speed: (0.15 - i * 0.02) * speed,
      color: i % 2 === 0 ? '#D4AF37' : '#00D1FF',
      count: 3 + i * 2,
    }));
  }, [orbits, speed]);

  return (
    <div className="relative w-full h-[500px] rounded-xl overflow-hidden border border-white/[0.06] bg-[#070B10]">
      <SimulationControls orbits={orbits} setOrbits={setOrbits} speed={speed} setSpeed={setSpeed} />

      <Canvas camera={{ position: [0, 8, 12], fov: 45 }}>
        <color attach="background" args={['#0A0F14']} />

        {/* Éclairage */}
        <ambientLight intensity={0.3} />
        <pointLight position={[0, 10, 0]} intensity={1.5} color="#D4AF37" />
        <pointLight position={[10, 5, 10]} intensity={0.6} color="#00D1FF" />
        <pointLight position={[-10, 5, -10]} intensity={0.4} color="#D4AF37" />

        {/* Scène */}
        <DivineCoreNode />
        {orbitConfigs.map((config, i) => (
          <ConcentricOrbit key={i} {...config} />
        ))}
        <BackgroundGrid />

        {/* Contrôles Caméra */}
        <OrbitControls
          autoRotate
          autoRotateSpeed={0.5 * speed}
          enableZoom
          enablePan={false}
          minDistance={5}
          maxDistance={25}
          maxPolarAngle={Math.PI / 2.2}
        />
      </Canvas>

      {/* Overlay */}
      <div className="absolute bottom-4 right-4 text-xs text-[#E8E4DD]/40/60 pointer-events-none">
        Souris : Rotation · Molette : Zoom · Sliders : Paramètres
      </div>
    </div>
  );
}
