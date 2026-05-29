'use client';
import React, { useRef, useState, useMemo, useEffect, useCallback } from 'react';
import { Canvas, useFrame, useThree } from '@react-three/fiber';
import { OrbitControls, Html } from '@react-three/drei';
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

/**
 * Disque terrestre avec éclairage shader :
 * - La texture carte est visible normalement dans la zone éclairée
 * - Les zones hors du cercle lumineux sont assombries
 */
function EarthDisc({ sunPos }:{ sunPos:[number,number] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const mapTex = useMemo(()=>new THREE.TextureLoader().load('/textures/ae-map.jpg'),[]);

  // Shader custom : assombrit les pixels éloignés du soleil
  const shader = useMemo(()=>({
    uniforms: {
      uMap: { value: mapTex },
      uSunPos: { value: new THREE.Vector2(sunPos[0], sunPos[1]) },
      uRadius: { value: DISC_R * 0.48 }, // rayon de la zone éclairée
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
        // Smooth falloff : 1.0 au centre, 0.0 loin
        float light = 1.0 - smoothstep(uRadius * 0.6, uRadius * 1.1, dist);
        // Mélanger : zone éclairée = texture, zone sombre = quasi-noir
        float brightness = mix(0.08, 1.0, light);
        gl_FragColor = vec4(texColor.rgb * brightness, texColor.a);
      }
    `,
  }),[mapTex, sunPos]);

  // Mettre à jour la position du soleil dans le shader
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

function FlatScene({ speed, showLabels, isPlaying }:{
  speed:number; showLabels:boolean; isPlaying:boolean;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group|null)[]>([]);
  const discRef = useRef<THREE.Mesh>(null);
  const timeOffset = useRef(0);
  const [sunXZ, setSunXZ] = useState<[number,number]>([0,0]);

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

    // Mettre à jour le shader de la carte
    // En Three.js, le disque est en rotation -PI/2 autour de X,
    // donc les coords du shader sont (x, -z) dans le plan UV local
    setSunXZ([sx, -sz]);

    const [mx,mz] = latLngToFlatDisc(pos.moon.lat, pos.moon.lng, DISC_R);
    if(moonRef.current) moonRef.current.position.set(mx, MOON_H, mz);

    pos.planets.forEach((p,i)=>{
      const ref = planetRefs.current[i];
      if(!ref) return;
      const [px,pz] = latLngToFlatDisc(p.lat, p.lng, DISC_R);
      ref.position.set(px, 0.2, pz);
    });
  });

  const initPos = useMemo(()=>getAllPositions(new Date()),[]);

  return (
    <group>
      <ambientLight intensity={0.1} />

      {/* Disque terrestre avec shader jour/nuit */}
      <EarthDisc sunPos={sunXZ} />

      {/* Soleil */}
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

      {/* Lune */}
      <group ref={moonRef} position={[0,MOON_H,0]}>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.1,24]} />
          <meshBasicMaterial color={MOON_C} side={THREE.DoubleSide} />
        </mesh>
        <Label text="Lune ☾" color={MOON_C} show={showLabels} />
      </group>

      {/* Planètes */}
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

  return <div className="w-full">
    <div className="flex flex-wrap items-center gap-2 mb-3">
      <button onClick={()=>setIsPlaying(!isPlaying)}
        className="px-4 py-2 text-[9px] font-tech-mono tracking-widest border transition-all"
        style={{borderColor:isPlaying?'#00E87B99':'#D4A84399',backgroundColor:isPlaying?'#00E87B1a':'#D4A8431a',color:isPlaying?'#00E87B':'#D4A843'}}
      >{isPlaying?'⏸ PAUSE':'▶ LECTURE'}</button>
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
      <Canvas camera={{position:[0,12,0.1],fov:50}}>
        <FlatScene speed={speed} showLabels={showLabels} isPlaying={isPlaying}/>
        <OrbitControls enablePan={false} minDistance={6} maxDistance={20} minPolarAngle={0} maxPolarAngle={Math.PI*0.3}/>
      </Canvas>
    </div>
    <div className="mt-3 border border-slate-800/50 bg-[var(--hull)] p-4">
      <p className="text-[13px] text-[var(--text-60)] font-rajdhani leading-relaxed">
        Modèle Terre plane : carte azimutale équidistante satellite. Le Soleil circule au-dessus du disque — la zone éclairée suit sa position (shader temps réel). Le reste du disque est dans l&apos;obscurité.
      </p>
      <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
        <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">Le MGPP →</a>
      </div>
    </div>
  </div>;
}
