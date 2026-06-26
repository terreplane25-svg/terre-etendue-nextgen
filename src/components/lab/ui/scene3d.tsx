'use client';
import { useRef, ReactNode } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls } from '@react-three/drei';

// Éclairage partagé : ambiant doux + 2 directionnelles pour donner du relief
// aux sphères/surfaces (matériaux standard). Sans effet sur les lignes.
export function SceneLights() {
  return <>
    <ambientLight intensity={0.5} />
    <directionalLight position={[6, 9, 7]} intensity={0.85} />
    <directionalLight position={[-5, 2, -4]} intensity={0.28} color="#88aaff" />
  </>;
}

// Marqueur sphérique éclairé : lit par les directionnelles → petite bille en
// relief plutôt qu'un rond plat, tout en gardant sa couleur (émissif).
export function Marker({ position, color, r = 0.06 }: {
  position: [number, number, number]; color: string; r?: number;
}) {
  return (
    <mesh position={position}>
      <sphereGeometry args={[r, 18, 18]} />
      <meshStandardMaterial color={color} emissive={color} emissiveIntensity={0.5} roughness={0.3} metalness={0.15} />
    </mesh>
  );
}

// Coin décoratif (repris du style des canvases du Lab).
function Corner({ pos, accent }: { pos: string; accent: string }) {
  const base = 'absolute w-4 h-4 z-10';
  const map: Record<string, string> = {
    tl: 'top-0 left-0 border-t border-l',
    tr: 'top-0 right-0 border-t border-r',
    bl: 'bottom-0 left-0 border-b border-l',
    br: 'bottom-0 right-0 border-b border-r',
  };
  return <div className={`${base} ${map[pos]}`} style={{ borderColor: accent + '4d' }} />;
}

// Conteneur de canvas 3D unifié : cadre + coins + bouton « recentrer » +
// indice de manipulation + OrbitControls amorti. Les enfants sont la scène.
export function Canvas3D({
  accent = '#00C8FF',
  heightClass = 'h-[40vh] sm:h-[55vh] md:h-[70vh]',
  cameraPos = [0, 0, 12],
  fov = 45,
  controlsProps,
  children,
}: {
  accent?: string;
  heightClass?: string;
  cameraPos?: [number, number, number];
  fov?: number;
  controlsProps?: Record<string, unknown>;
  children: ReactNode;
}) {
  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const ref = useRef<any>(null);
  return (
    <div className={`w-full ${heightClass} border border-slate-800/50 bg-[#030810] relative overflow-hidden`}>
      <Corner pos="tl" accent={accent} /><Corner pos="tr" accent={accent} />
      <Corner pos="bl" accent={accent} /><Corner pos="br" accent={accent} />

      <button
        onClick={() => ref.current?.reset()}
        className="absolute top-2 right-2 z-20 px-2.5 py-1 text-[10px] font-tech-mono tracking-widest transition-all"
        style={{ border: `1px solid ${accent}55`, background: '#030810cc', color: accent }}
        title="Recentrer la vue"
      >⟳ RECENTRER</button>

      <div className="absolute bottom-2 left-2 z-20 text-[9px] font-tech-mono pointer-events-none"
        style={{ color: accent, opacity: 0.55 }}>
        glisser pour pivoter · molette pour zoomer · clic droit pour déplacer
      </div>

      <Canvas camera={{ position: cameraPos, fov }}>
        <SceneLights />
        {children}
        <OrbitControls ref={ref} enableDamping dampingFactor={0.08} makeDefault {...controlsProps} />
      </Canvas>
    </div>
  );
}
