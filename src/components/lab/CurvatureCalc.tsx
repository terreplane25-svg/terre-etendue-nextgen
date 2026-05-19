'use client';
import { useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

const R = 6371;
function horizonDist(h:number):number{return Math.sqrt((R+h)**2-R**2);}
function hiddenH(d:number,h:number):number{const a=horizonDist(h);if(d<=a)return 0;return Math.sqrt(R**2+(d-a)**2)-R;}
function curvDrop(d:number):number{return d**2/(2*R);}
function fmt(km:number):string{if(km>=1)return km.toFixed(2)+' km';if(km>=0.001)return(km*1000).toFixed(1)+' m';return(km*100000).toFixed(1)+' cm';}

const PRESETS = [
  { label:'Finestrelles → Alpes (443 km)', d:443, oh:2820, th:4102,
    desc:'Pic de Finestrelles (2 820 m) → Barre des Écrins (4 102 m). Record photo 2016, Marc Bret.' },
  { label:'Navire — Île Maurice (321 km)', d:321, oh:0, th:30,
    desc:'Observation depuis le niveau de la mer. Navire visible à 321 km (Fata Morgana, 1895).' },
  { label:'Notre-Dame d\'Anvers (241 km)', d:241, oh:0, th:123,
    desc:'Flèche de la cathédrale (123 m) vue par des capitaines de navires à 241 km.' },
  { label:'Shkhara → Elbrouz (493 km)', d:493, oh:3107, th:5642,
    desc:'Mont Karagöl (3 107 m) → Mont Elbrouz (5 642 m). Photo Richard Ježík, à travers la mer Noire.' },
];

function NumInput({label,value,onChange,min,max,unit,step=1}:{label:string;value:number;onChange:(v:number)=>void;min:number;max:number;unit:string;step?:number}){
  return(
    <div className="border border-slate-800/50 bg-[#0A1020] p-4">
      <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">{label}</label>
      <div className="flex items-center gap-3">
        <input type="range" min={min} max={max} step={step} value={value}
          onChange={e=>onChange(+e.target.value)} className="flex-1 accent-[#00C8FF] h-2" />
        <input type="number" min={min} max={max} step={step} value={value}
          onChange={e=>{const v=+e.target.value;if(!isNaN(v)&&v>=min&&v<=max)onChange(v);}}
          className="w-24 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#00C8FF] px-3 py-2 text-right rounded-none"
        />
        <span className="text-[12px] font-tech-mono text-slate-500 w-8">{unit}</span>
      </div>
    </div>
  );
}

function Scene({d,oh,th}:{d:number;oh:number;th:number}){
  const hidden=hiddenH(d,oh);
  const maxDim=Math.max(d,60);const s=5/maxDim;
  const arc=d/R;
  const curve=useMemo(()=>{
    const p:THREE.Vector3[]=[];
    for(let i=0;i<=150;i++){const a=-arc/2+(i/150)*arc;p.push(new THREE.Vector3(Math.sin(a)*R*s,(Math.cos(a)-1)*R*s,0));}
    return p;
  },[d,s,arc]);
  const maxH=Math.max(oh,th,0.001);const hs=Math.min(s*150,3/maxH);
  const halfD=(d/2)*s;
  const oA=-arc/2,tA=arc/2;
  const oGx=Math.sin(oA)*R*s,oGy=(Math.cos(oA)-1)*R*s;
  const tGx=Math.sin(tA)*R*s,tGy=(Math.cos(tA)-1)*R*s;
  const oNx=Math.sin(oA),oNy=Math.cos(oA),tNx=Math.sin(tA),tNy=Math.cos(tA);
  const obsP:[number,number,number]=[oGx+oNx*oh*hs,oGy+oNy*oh*hs,0];
  const tgtP:[number,number,number]=[tGx+tNx*th*hs,tGy+tNy*th*hs,0];
  const hidP:[number,number,number]=[tGx+tNx*Math.min(hidden,th)*hs,tGy+tNy*Math.min(hidden,th)*hs,0];
  const vis=hidden<th;

  return<>
    <ambientLight intensity={0.5}/>
    {/* GLOBE — centré verticalement plus haut */}
    <group position={[0,3,0]}>
      <Line points={curve} color="#00C8FF" lineWidth={2.5}/>
      <Line points={[new THREE.Vector3(oGx,oGy,0),new THREE.Vector3(...obsP)]} color="#00C8FF" lineWidth={2}/>
      <mesh position={obsP}><sphereGeometry args={[0.08,12,12]}/><meshBasicMaterial color="#00C8FF"/></mesh>
      {vis&&<Line points={[new THREE.Vector3(tGx+tNx*hidden*hs,tGy+tNy*hidden*hs,0),new THREE.Vector3(...tgtP)]} color="#00E87B" lineWidth={3}/>}
      {hidden>0&&<Line points={[new THREE.Vector3(tGx,tGy,0),new THREE.Vector3(...hidP)]} color="#FF4444" lineWidth={4}/>}
      <Line points={[new THREE.Vector3(...obsP),new THREE.Vector3(...tgtP)]}
        color={vis?'#00E87B':'#FF4444'} lineWidth={1} opacity={0.4} transparent dashed dashSize={0.08} gapSize={0.04}/>
      <Html position={[0,2.5,0]} center distanceFactor={10} style={{pointerEvents:'none'}}>
        <div style={{color:'#00C8FF',fontSize:'13px',fontFamily:'monospace',letterSpacing:'0.12em',fontWeight:'bold'}}>MODÈLE GLOBE (R = 6 371 km)</div>
      </Html>
    </group>
    {/* PLAN — centré plus bas */}
    <group position={[0,-3.5,0]}>
      <Line points={[new THREE.Vector3(-halfD-0.5,0,0),new THREE.Vector3(halfD+0.5,0,0)]} color="#D4A843" lineWidth={2.5}/>
      <Line points={[new THREE.Vector3(-halfD,0,0),new THREE.Vector3(-halfD,oh*hs,0)]} color="#D4A843" lineWidth={2}/>
      <mesh position={[-halfD,oh*hs,0]}><sphereGeometry args={[0.08,12,12]}/><meshBasicMaterial color="#D4A843"/></mesh>
      <Line points={[new THREE.Vector3(halfD,0,0),new THREE.Vector3(halfD,th*hs,0)]} color="#00E87B" lineWidth={2}/>
      <Line points={[new THREE.Vector3(-halfD,oh*hs,0),new THREE.Vector3(halfD,th*hs,0)]}
        color="#00E87B" lineWidth={1} opacity={0.4} transparent dashed dashSize={0.08} gapSize={0.04}/>
      <Html position={[0,2,0]} center distanceFactor={10} style={{pointerEvents:'none'}}>
        <div style={{color:'#D4A843',fontSize:'13px',fontFamily:'monospace',letterSpacing:'0.12em',fontWeight:'bold'}}>MODÈLE PLAN — toujours visible</div>
      </Html>
    </group>
    <OrbitControls enablePan enableZoom maxDistance={20} minDistance={3}/>
  </>;
}

export default function CurvatureCalc(){
  const [dist,setDist]=useState(443);
  const [obsM,setObsM]=useState(2820);
  const [tgtM,setTgtM]=useState(4102);
  const oh=obsM/1000,th=tgtM/1000;
  const hidden=hiddenH(dist,oh);
  const hDist=horizonDist(oh);
  const drop=curvDrop(dist);
  const vis=hidden<th;

  return<div className="w-full">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-5">
      <NumInput label="DISTANCE" value={dist} onChange={setDist} min={0} max={2000} unit="km"/>
      <NumInput label="HAUTEUR OBSERVATEUR" value={obsM} onChange={setObsM} min={0} max={500000} unit="m"/>
      <NumInput label="HAUTEUR CIBLE" value={tgtM} onChange={setTgtM} min={0} max={10000} unit="m"/>
    </div>

    <div className="flex flex-wrap gap-2 mb-5">
      <span className="text-[11px] font-tech-mono text-slate-500 self-center">CAS RÉELS :</span>
      {PRESETS.map(p=>(
        <button key={p.label} onClick={()=>{setDist(p.d);setObsM(p.oh);setTgtM(p.th);}}
          title={p.desc}
          className="px-4 py-2 text-[11px] font-tech-mono border border-slate-600 text-slate-300 hover:border-[#00C8FF]/50 hover:text-[#00C8FF] transition-all"
        >{p.label}</button>
      ))}
    </div>

    <div className="w-full h-[55vh] md:h-[65vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10"/>
      <Canvas camera={{position:[0,0,12],fov:45}}>
        <Scene d={dist} oh={oh} th={th}/>
      </Canvas>
    </div>

    <div className="mt-5 grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="border border-cyan-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">HORIZON</div>
        <div className="text-[20px] font-tech-mono text-cyan-400 font-bold">{hDist.toFixed(1)} km</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">a = √[(R+h)² - R²]</div>
      </div>
      <div className="border border-red-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-red-400/70 tracking-widest mb-2">CHUTE COURBURE</div>
        <div className="text-[20px] font-tech-mono text-red-400 font-bold">{fmt(drop)}</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">h = d²/(2R)</div>
      </div>
      <div className="border border-amber-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-amber-400/70 tracking-widest mb-2">HAUTEUR CACHÉE</div>
        <div className="text-[20px] font-tech-mono text-amber-400 font-bold">{fmt(hidden)}</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">x = √[R²+(d-a)²]-R</div>
      </div>
      <div className={`border p-4 ${vis?'border-green-900/30 bg-green-950/20':'border-red-900/30 bg-red-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">VERDICT GLOBE</div>
        <div className={`text-[18px] font-tech-mono font-bold ${vis?'text-green-400':'text-red-400'}`}>{vis?'✓ VISIBLE':'✗ MASQUÉE'}</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          {vis?`Visible : ${fmt(th-hidden)} sur ${fmt(th)}`:`Caché : ${fmt(hidden)} > cible : ${fmt(th)}`}
        </div>
      </div>
    </div>

    <div className="mt-4 text-[11px] font-tech-mono text-slate-500 px-1">
      ⚠ Ne tient pas compte de la réfraction atmosphérique — qui peut rendre visible un objet théoriquement masqué.
    </div>

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-500">ARTICLES :</span>
      <a href="/article/leau-ne-ment-pas" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;eau ne ment pas →</a>
      <a href="/article/ce-quon-voit-quand-on-ne-devrait-plus-voir" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">Ce qu&apos;on voit →</a>
    </div>
  </div>;
}
