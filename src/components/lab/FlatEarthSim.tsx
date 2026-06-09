'use client';
import React, { useRef, useState, useMemo, useEffect } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html, Line } from '@react-three/drei';
import * as THREE from 'three';
import { getAllPositions, latLngToFlatDisc } from './celestialCalc';

const SUN_C = '#FFD040';
const MOON_C = '#C8C8D0';
const DISC_R = 6;

function Label({ text, color='#C8D8E8', show=true }:{ text:string; color?:string; show?:boolean }) {
  if(!show) return null;
  return <Html center distanceFactor={10} style={{pointerEvents:'none'}}>
    <div style={{color,fontSize:'10px',fontFamily:'monospace',textShadow:'0 0 6px rgba(0,0,0,0.9)',whiteSpace:'nowrap',fontWeight:'bold'}}>{text}</div>
  </Html>;
}

function EarthDisc({ sunPos }:{ sunPos:[number,number] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const mapTex = useMemo(()=>new THREE.TextureLoader().load('/textures/ae-map.jpg'),[]);

  const shader = useMemo(()=>({
    uniforms: {
      uMap: { value: mapTex },
      uSunPos: { value: new THREE.Vector2(sunPos[0], sunPos[1]) },
      uRadius: { value: DISC_R * 0.48 },
    },
    vertexShader: `
      varying vec2 vUv;
      varying vec3 vPos;
      void main(){
        vUv = uv;
        vPos = position;
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
      }
    `,
    fragmentShader: `
      uniform sampler2D uMap;
      uniform vec2 uSunPos;
      uniform float uRadius;
      varying vec2 vUv;
      varying vec3 vPos;
      void main(){
        vec4 texColor = texture2D(uMap, vUv);
        float dist = distance(vPos.xy, uSunPos);
        float light = 1.0 - smoothstep(uRadius * 0.6, uRadius * 1.1, dist);
        float brightness = mix(0.08, 1.0, light);
        gl_FragColor = vec4(texColor.rgb * brightness, texColor.a);
      }
    `,
  }),[mapTex, sunPos]);

  useEffect(()=>{
    if(meshRef.current){
      const mat = meshRef.current.material as THREE.ShaderMaterial;
      if(mat.uniforms) mat.uniforms.uSunPos.value.set(sunPos[0], sunPos[1]);
    }
  },[sunPos]);

  return (
    <mesh ref={meshRef} rotation={[-Math.PI/2, 0, 0]}>
      <circleGeometry args={[DISC_R, 128]} />
      <shaderMaterial
        uniforms={shader.uniforms}
        vertexShader={shader.vertexShader}
        fragmentShader={shader.fragmentShader}
        transparent
      />
    </mesh>
  );
}

function TropicCircles() {
  const tropicLat = 23.44;
  const arcticLat = 66.56;

  const makeCircle = (lat: number) => {
    const [cx, cz] = latLngToFlatDisc(lat, 0, DISC_R);
    const r = Math.sqrt(cx * cx + cz * cz);
    const pts: THREE.Vector3[] = [];
    for (let i = 0; i <= 96; i++) {
      const a = (i / 96) * Math.PI * 2;
      pts.push(new THREE.Vector3(Math.cos(a) * r, 0.01, Math.sin(a) * r));
    }
    return pts;
  };

  return <>
    <Line points={makeCircle(tropicLat)} color="#D4A843" opacity={0.25} transparent lineWidth={1} />
    <Line points={makeCircle(-tropicLat)} color="#D4A843" opacity={0.25} transparent lineWidth={1} />
    <Line points={makeCircle(arcticLat)} color="#00C8FF" opacity={0.15} transparent lineWidth={1} />
    <Line points={makeCircle(-arcticLat)} color="#00C8FF" opacity={0.15} transparent lineWidth={1} />
    <Line points={makeCircle(0)} color="#FF4444" opacity={0.2} transparent lineWidth={1} />
  </>;
}

function FlatScene({ speed, showLabels, isPlaying, showTropics, onDateUpdate }:{
  speed:number; showLabels:boolean; isPlaying:boolean; showTropics:boolean;
  onDateUpdate:(d:Date)=>void;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group|null)[]>([]);
  const timeOffset = useRef(0);
  const [sunXZ, setSunXZ] = useState<[number,number]>([0,0]);
  const frameCount = useRef(0);

  const SUN_H = 0.3;
  const MOON_H = 0.25;

  useFrame(()=>{
    if(!isPlaying) return;
    const dt = 0.016 * speed;
    timeOffset.current += dt;
    const offsetMs = timeOffset.current * 30 * 60 * 1000;
    const simDate = new Date(Date.now() + offsetMs);
    const pos = getAllPositions(simDate);

    const [sx,sz] = latLngToFlatDisc(pos.sun.lat, pos.sun.lng, DISC_R);
    if(sunRef.current) sunRef.current.position.set(sx, SUN_H, sz);
    setSunXZ([sx, -sz]);

    const [mx,mz] = latLngToFlatDisc(pos.moon.lat, pos.moon.lng, DISC_R);
    if(moonRef.current) moonRef.current.position.set(mx, MOON_H, mz);

    pos.planets.forEach((p,i)=>{
      const ref = planetRefs.current[i];
      if(!ref) return;
      const [px,pz] = latLngToFlatDisc(p.lat, p.lng, DISC_R);
      ref.position.set(px, 0.2, pz);
    });

    frameCount.current++;
    if (frameCount.current % 30 === 0) onDateUpdate(simDate);
  });

  const initPos = useMemo(()=>getAllPositions(new Date()),[]);

  return (
    <group>
      <ambientLight intensity={0.1} />
      <EarthDisc sunPos={sunXZ} />
      {showTropics && <TropicCircles />}

      <group ref={sunRef} position={[0,SUN_H,0]}>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.22,32]} />
          <meshBasicMaterial color={SUN_C} side={THREE.DoubleSide} />
        </mesh>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.45,32]} />
          <meshBasicMaterial color={SUN_C} transparent opacity={0.15} side={THREE.DoubleSide} />
        </mesh>
        <Label text="Soleil ☉" color={SUN_C} show={showLabels} />
      </group>

      <group ref={moonRef} position={[0,MOON_H,0]}>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.1,24]} />
          <meshBasicMaterial color={MOON_C} side={THREE.DoubleSide} />
        </mesh>
        <Label text="Lune ☾" color={MOON_C} show={showLabels} />
      </group>

      {initPos.planets.map((p,i)=>(
        <group key={p.name} ref={el=>{planetRefs.current[i]=el;}}>
          <mesh rotation={[-Math.PI/2,0,0]}>
            <circleGeometry args={[p.size*0.6,16]} />
            <meshBasicMaterial color={p.color} side={THREE.DoubleSide} />
          </mesh>
          <Label text={p.name} color={p.color} show={showLabels} />
        </group>
      ))}
    </group>
  );
}

export default function FlatEarthSim(){
  const [speed,setSpeed]=useState(1);
  const [showLabels,setShowLabels]=useState(true);
  const [isPlaying,setIsPlaying]=useState(true);
  const [showTropics,setShowTropics]=useState(false);
  const [simDate,setSimDate]=useState(new Date());

  const seasonName = useMemo(() => {
    const m = simDate.getMonth();
    if (m >= 2 && m <= 4) return 'Printemps';
    if (m >= 5 && m <= 7) return 'Été';
    if (m >= 8 && m <= 10) return 'Automne';
    return 'Hiver';
  }, [simDate]);

  return <div className="w-full">
    <div className="flex flex-wrap items-center gap-2 mb-3">
      <button onClick={()=>setIsPlaying(!isPlaying)}
        className="px-4 py-2 text-[9px] font-tech-mono tracking-widest border transition-all"
        style={{borderColor:isPlaying?'#00E87B99':'#D4A84399',backgroundColor:isPlaying?'#00E87B1a':'#D4A8431a',color:isPlaying?'#00E87B':'#D4A843'}}
      >{isPlaying?'⏸ PAUSE':'▶ LECTURE'}</button>
      <button onClick={()=>setShowTropics(!showTropics)}
        className={`px-3 py-1 text-[8px] font-tech-mono border ${showTropics?'border-[#D4A843]/50 text-[#D4A843]':'border-slate-800 text-slate-600'}`}
      >TROPIQUES: {showTropics?'ON':'OFF'}</button>
      <div className="flex items-center gap-2 ml-auto">
        <span className="text-[8px] font-tech-mono text-slate-500">VIT.</span>
        <input type="range" min={0.1} max={5} step={0.1} value={speed} onChange={e=>setSpeed(+e.target.value)} className="w-16 md:w-20 accent-[var(--cyan)]"/>
        <span className="text-[8px] font-tech-mono text-[var(--cyan)]">&times;{speed.toFixed(1)}</span>
      </div>
      <button onClick={()=>setShowLabels(!showLabels)}
        className={`px-3 py-1 text-[8px] font-tech-mono border ${showLabels?'border-slate-600 text-slate-400':'border-slate-800 text-slate-600'}`}
      >NOMS: {showLabels?'ON':'OFF'}</button>
    </div>
    <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#020408] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-3 left-3 z-10">
        <div className="text-[9px] font-tech-mono text-[var(--green)] tracking-widest">◉ TERRE PLANE — VUE DU DESSUS</div>
        <div className="text-[8px] font-tech-mono text-slate-600 mt-1">Éphémérides : Astronomy Engine</div>
      </div>
      {/* Date & saison */}
      <div className="absolute top-3 right-3 z-10 text-right">
        <div className="text-[10px] font-tech-mono text-[var(--cyan)]">
          {simDate.toLocaleDateString('fr-FR', { day:'2-digit', month:'short', year:'numeric' })}
        </div>
        <div className="text-[9px] font-tech-mono text-[#D4A843]">
          {simDate.toLocaleTimeString('fr-FR', { hour:'2-digit', minute:'2-digit' })} — {seasonName}
        </div>
      </div>
      {/* Légende tropiques */}
      {showTropics && (
        <div className="absolute bottom-3 left-3 z-10 flex flex-col gap-1">
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-[#FF4444] opacity-40" />
            <span className="text-[7px] font-tech-mono text-slate-500">Équateur</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-[#D4A843] opacity-50" />
            <span className="text-[7px] font-tech-mono text-slate-500">Tropiques (±23.44°)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-[#00C8FF] opacity-30" />
            <span className="text-[7px] font-tech-mono text-slate-500">Cercles polaires (±66.56°)</span>
          </div>
        </div>
      )}
      <Canvas camera={{position:[0,12,0.1],fov:50}}>
        <FlatScene speed={speed} showLabels={showLabels} isPlaying={isPlaying} showTropics={showTropics} onDateUpdate={setSimDate}/>
        <OrbitControls enablePan={false} minDistance={6} maxDistance={20} minPolarAngle={0} maxPolarAngle={Math.PI*0.3}/>
      </Canvas>
    </div>
    <div className="mt-3 border border-slate-800/50 bg-[var(--hull)] p-4">
      <p className="text-[13px] text-[var(--text-60)] font-rajdhani leading-relaxed">
        Modèle Terre plane : carte azimutale équidistante satellite. Le Soleil circule au-dessus du disque — la zone éclairée suit sa position (shader temps réel). Activez les tropiques pour voir les cercles de latitude clés et le parcours saisonnier du Soleil.
      </p>
      <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
        <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">Le MGPP →</a>
        <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">L&apos;hypothèse nulle →</a>
      </div>
    </div>
  </div>;
}
