'use client';
import React, { useRef, useState, useMemo } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Line, Html, Stars } from '@react-three/drei';
import * as THREE from 'three';

type Mode = 'classic' | 'vortex';
const SUN_C = '#FFD040';

interface PDef { name:string; color:string; r:number; period:number; size:number; }
const PLANETS: PDef[] = [
  { name:'Mercure', color:'#A0A0A0', r:2.0, period:0.24, size:0.10 },
  { name:'Vénus',   color:'#E8C060', r:3.0, period:0.62, size:0.13 },
  { name:'Terre',   color:'#4488CC', r:4.2, period:1.00, size:0.14 },
  { name:'Mars',    color:'#CC6644', r:5.5, period:1.88, size:0.11 },
  { name:'Jupiter', color:'#C8A060', r:7.5, period:11.86, size:0.28 },
];

function OrbitRing({ radius, color='#00C8FF', opacity=0.15 }:{ radius:number; color?:string; opacity?:number }) {
  const pts = useMemo(()=>{
    const a:THREE.Vector3[]=[];
    for(let i=0;i<=128;i++){const t=(i/128)*Math.PI*2;a.push(new THREE.Vector3(Math.cos(t)*radius,0,Math.sin(t)*radius));}
    return a;
  },[radius]);
  return <Line points={pts} color={color} opacity={opacity} transparent lineWidth={0.5} />;
}

function Label({text,color='#C8D8E8',show=true}:{text:string;color?:string;show?:boolean}){
  if(!show)return null;
  return <Html center distanceFactor={15} style={{pointerEvents:'none'}}>
    <div style={{color,fontSize:'9px',fontFamily:'monospace',textShadow:'0 0 4px rgba(0,0,0,0.8)',whiteSpace:'nowrap',transform:'translateY(-16px)'}}>{text}</div>
  </Html>;
}

function HudGrid(){
  const l=useMemo(()=>{const a:THREE.Vector3[][]=[];for(let i=-12;i<=12;i+=2){
    a.push([new THREE.Vector3(i,-0.01,-12),new THREE.Vector3(i,-0.01,12)]);
    a.push([new THREE.Vector3(-12,-0.01,i),new THREE.Vector3(12,-0.01,i)]);
  }return a;},[]);
  return <>{l.map((p,i)=><Line key={i} points={p} color="#00C8FF" opacity={0.04} transparent lineWidth={0.5}/>)}</>;
}

// ═══ CLASSIQUE ═══
function ClassicScene({speed,showLabels}:{speed:number;showLabels:boolean}){
  const refs=useRef<(THREE.Group|null)[]>([]);
  const moonRef=useRef<THREE.Group>(null);
  useFrame(({clock})=>{
    const t=clock.getElapsedTime()*speed*0.3;
    PLANETS.forEach((p,i)=>{const g=refs.current[i];if(!g)return;const a=(t/p.period)*Math.PI*2;g.position.set(Math.cos(a)*p.r,0,Math.sin(a)*p.r);});
    if(moonRef.current&&refs.current[2]){const e=refs.current[2]!.position;const ma=t*13.37;moonRef.current.position.set(e.x+Math.cos(ma)*0.5,0,e.z+Math.sin(ma)*0.5);}
  });
  return <group>
    <group><mesh><sphereGeometry args={[0.45,32,32]}/><meshStandardMaterial color={SUN_C} emissive={SUN_C} emissiveIntensity={1.5}/></mesh>
    <mesh><sphereGeometry args={[0.9,16,16]}/><meshBasicMaterial color={SUN_C} transparent opacity={0.06}/></mesh>
    <pointLight intensity={2} color={SUN_C} distance={20}/><Label text="Soleil" color={SUN_C} show={showLabels}/></group>
    {PLANETS.map(p=><OrbitRing key={'o'+p.name} radius={p.r}/>)}
    {PLANETS.map((p,i)=><group key={p.name} ref={el=>{refs.current[i]=el;}}><mesh><sphereGeometry args={[p.size,20,20]}/><meshStandardMaterial color={p.color} roughness={0.6}/></mesh><Label text={p.name} color={p.color} show={showLabels}/></group>)}
    <group ref={moonRef}><mesh><sphereGeometry args={[0.05,16,16]}/><meshStandardMaterial color="#C8C8D0" roughness={0.4}/></mesh><Label text="Lune" color="#C8C8D0" show={showLabels}/></group>
  </group>;
}

// ═══ VORTEX — fond qui suit, orbites elliptiques, traînée lumineuse ═══
function VortexScene({speed,showLabels}:{speed:number;showLabels:boolean}){
  const groupRef=useRef<THREE.Group>(null);
  const bgRef=useRef<THREE.Mesh>(null);
  const refs=useRef<(THREE.Group|null)[]>([]);
  const moonRef=useRef<THREE.Group>(null);
  const sunRef=useRef<THREE.Group>(null);
  const [sunTrail, setSunTrail]=useState<[number,number,number][]>([]);
  const [pTrails, setPTrails]=useState<[number,number,number][][]>(PLANETS.map(()=>[]));
  const frameCount=useRef(0);

  // Excentricités réelles simplifiées
  const ecc = [0.206, 0.007, 0.017, 0.093, 0.049]; // Mercure, Vénus, Terre, Mars, Jupiter

  useFrame(({clock})=>{
    const t=clock.getElapsedTime()*speed*0.15;
    const galV = 2.0;
    const z = t * galV;

    if(sunRef.current) sunRef.current.position.set(0, 0, z);
    
    // Fond d'espace suit le déplacement
    if(bgRef.current) bgRef.current.position.set(0, 0, z);

    PLANETS.forEach((p,i)=>{
      const g=refs.current[i];if(!g)return;
      const a=(t*2/p.period)*Math.PI*2;
      const e = ecc[i];
      // Orbite elliptique: r = a(1-e²)/(1+e·cos(θ))
      const rEllip = p.r * (1 - e*e) / (1 + e * Math.cos(a));
      const x = Math.cos(a) * rEllip;
      const y = Math.sin(a) * rEllip;
      g.position.set(x, y, z);
    });

    if(moonRef.current&&refs.current[2]){
      const e=refs.current[2]!.position;
      const ma=t*2*13.37;
      moonRef.current.position.set(e.x+Math.cos(ma)*0.4, e.y+Math.sin(ma)*0.4, e.z);
    }

    if(groupRef.current) groupRef.current.position.z = -z;

    frameCount.current++;
    if(frameCount.current%3===0){
      // Traînée soleil — plus longue (300 points)
      setSunTrail(prev=>{const n=[...prev,[0,0,z] as [number,number,number]];return n.length>300?n.slice(-300):n;});
      setPTrails(prev=>prev.map((trail,i)=>{
        const g=refs.current[i];if(!g)return trail;
        const p=g.position;
        const n=[...trail,[p.x,p.y,p.z] as [number,number,number]];
        return n.length>300?n.slice(-300):n;
      }));
    }
  });

  const spaceTex = useMemo(()=>new THREE.TextureLoader().load('/textures/space-bg.jpg'),[]);

  return <group ref={groupRef}>
    {/* Fond d'espace — suit le système */}
    <mesh ref={bgRef}><sphereGeometry args={[60,32,32]}/><meshBasicMaterial map={spaceTex} side={THREE.BackSide}/></mesh>

    {/* Traînée Soleil — luminescente */}
    {sunTrail.length>1 && <>
      <Line points={sunTrail.map(p=>new THREE.Vector3(...p))} color={SUN_C} opacity={0.6} transparent lineWidth={2}/>
      <Line points={sunTrail.map(p=>new THREE.Vector3(p[0],p[1],p[2]))} color="#FFFFFF" opacity={0.15} transparent lineWidth={4}/>
    </>}

    {/* Soleil */}
    <group ref={sunRef}>
      <mesh><sphereGeometry args={[0.4,32,32]}/><meshStandardMaterial color={SUN_C} emissive={SUN_C} emissiveIntensity={1.5}/></mesh>
      <mesh><sphereGeometry args={[1.0,16,16]}/><meshBasicMaterial color={SUN_C} transparent opacity={0.05}/></mesh>
      <pointLight intensity={3} color={SUN_C} distance={25}/>
      <Label text="Soleil" color={SUN_C} show={showLabels}/>
    </group>

    {/* Planètes + traînées */}
    {PLANETS.map((p,i)=>(
      <React.Fragment key={p.name}>
        {pTrails[i].length>1 && <Line points={pTrails[i].map(pt=>new THREE.Vector3(...pt))} color={p.color} opacity={0.35} transparent lineWidth={1}/>}
        <group ref={el=>{refs.current[i]=el;}}>
          <mesh><sphereGeometry args={[p.size,20,20]}/><meshStandardMaterial color={p.color} emissive={p.color} emissiveIntensity={0.3} roughness={0.6}/></mesh>
          <Label text={p.name} color={p.color} show={showLabels}/>
        </group>
      </React.Fragment>
    ))}

    {/* Lune */}
    <group ref={moonRef}>
      <mesh><sphereGeometry args={[0.04,16,16]}/><meshStandardMaterial color="#C8C8D0" roughness={0.4}/></mesh>
    </group>
  </group>;
}

// ═══ PRINCIPAL ═══
export default function GeoHelioSim(){
  const [mode, setMode] = useState<Mode>('classic');
  const [speed, setSpeed] = useState(1);
  const [showLabels, setShowLabels] = useState(true);

  return <div className="w-full">
    <div className="flex flex-wrap items-center gap-2 mb-3">
      <div className="flex gap-1">
        {([['classic','CLASSIQUE','#00C8FF'],['vortex','VORTEX GALACTIQUE','#D4A843']] as const).map(([id,lbl,col])=>(
          <button key={id} onClick={()=>setMode(id as Mode)}
            className="px-3 md:px-4 py-2 text-[8px] md:text-[9px] font-orbitron tracking-widest border transition-all"
            style={{clipPath:'polygon(6px 0,100% 0,calc(100% - 6px) 100%,0 100%)',
              borderColor:mode===id?col+'99':'#334155',backgroundColor:mode===id?col+'1a':'transparent',color:mode===id?col:'#64748b'}}
          >{lbl}</button>
        ))}
      </div>
      <div className="flex items-center gap-2 ml-auto">
        <span className="text-[8px] font-tech-mono text-slate-500">VIT.</span>
        <input type="range" min={0.1} max={5} step={0.1} value={speed} onChange={e=>setSpeed(+e.target.value)} className="w-16 md:w-20 accent-[var(--cyan)]"/>
        <span className="text-[8px] font-tech-mono text-[var(--cyan)]">&times;{speed.toFixed(1)}</span>
      </div>
      <button onClick={()=>setShowLabels(!showLabels)}
        className={`px-3 py-1 text-[8px] font-tech-mono border ${showLabels?'border-slate-600 text-slate-400':'border-slate-800 text-slate-600'}`}
      >NOMS: {showLabels?'ON':'OFF'}</button>
    </div>
    <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-3 left-3 z-10">
        <div className="text-[9px] font-tech-mono tracking-widest" style={{color:mode==='classic'?'var(--cyan)':'var(--gold)',opacity:0.6}}>
          ◉ {mode==='classic'?'HÉLIOCENTRIQUE CLASSIQUE':'VORTEX GALACTIQUE'}
        </div>
        <div className="text-[8px] font-tech-mono text-slate-600 mt-1">
          {mode==='classic'?'Soleil fixe — planètes en orbite':'Le système solaire fonce à ~828 000 km/h dans la galaxie'}
        </div>
      </div>
      <Canvas camera={{position:mode==='classic'?[0,12,8]:[8,6,4],fov:50}} key={mode}>
        <ambientLight intensity={0.15}/>
        {mode==='classic'&&<HudGrid/>}
        {mode==='classic'?<ClassicScene speed={speed} showLabels={showLabels}/>:<VortexScene speed={speed} showLabels={showLabels}/>}
        <OrbitControls enablePan={mode==='vortex'} minDistance={4} maxDistance={25}/>
      </Canvas>
    </div>
    <div className="mt-3 border border-slate-800/50 bg-[var(--hull)] p-4">
      <p className="text-[13px] text-[var(--text-60)] font-rajdhani leading-relaxed">
        {mode==='classic'
          ?"Modèle héliocentrique classique. Le Soleil est au centre, les planètes orbitent. Chaque planète a sa propre période."
          :"Le Soleil n\u2019est pas fixe \u2014 il voyage à ~828 000 km/h dans la Voie Lactée. Les planètes tracent des spirales hélicoïdales (vortex). Les traînées colorées montrent la trajectoire réelle de chaque planète dans l\u2019espace galactique."}
      </p>
      <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
        <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">L&apos;hypothèse nulle →</a>
      </div>
    </div>
  </div>;
}
