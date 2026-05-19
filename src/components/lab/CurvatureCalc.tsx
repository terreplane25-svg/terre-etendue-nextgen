'use client';
import { useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

const R = 6371; // km

// ─── Formules exactes (Pythagore) ───────────────
function horizonDist(h: number): number { return Math.sqrt((R+h)**2 - R**2); }
function hiddenH(d: number, h: number): number {
  const a = horizonDist(h); if (d<=a) return 0;
  return Math.sqrt(R**2 + (d-a)**2) - R;
}
function curvDrop(d: number): number { return d**2 / (2*R); }
function fmt(km: number): string {
  if(km>=1) return km.toFixed(2)+' km';
  if(km>=0.001) return (km*1000).toFixed(1)+' m';
  return (km*100000).toFixed(1)+' cm';
}

// Données vérifiées
const PRESETS = [
  { label:'Bedford Level',    d:10,  oh:0.2,   th:0.9,   note:'Télescope 20cm, drapeau 90cm, 10km' },
  { label:'Chicago 90 km',    d:90,  oh:1.7,   th:443,   note:'Obs 1.7m, Willis Tower 443m' },
  { label:'Canigou 263 km',   d:263, oh:50,    th:2784,  note:'Obs 50m (Marseille), sommet 2784m' },
  { label:'Finestrelles 443 km', d:443, oh:2820, th:3144, note:'Pic Finestrelles 2820m → Pic Gaspard 3144m' },
  { label:'Douvres→Calais',   d:33,  oh:100,   th:10,    note:'Falaises 100m, côte française ~10m' },
  { label:'Everest 340 km',   d:340, oh:1.6,   th:8849,  note:'Obs 1.6m, sommet 8849m' },
  { label:'Shkhara 493 km',   d:493, oh:3107,  th:5642,  note:'Obs 3107m → Mont Elbrouz 5642m' },
];

// ─── Input avec slider + saisie directe ─────────
function NumInput({ label, value, onChange, min, max, unit, step=1 }:{
  label:string; value:number; onChange:(v:number)=>void; min:number; max:number; unit:string; step?:number;
}){
  const display = unit==='m' 
    ? (value>=1000 ? `${(value/1000).toFixed(1)} km` : `${value.toFixed(0)} m`)
    : `${value} km`;
  return (
    <div className="border border-slate-800/50 bg-[#0A1020] p-3">
      <label className="text-[8px] font-tech-mono text-slate-500 tracking-widest block mb-1">{label}</label>
      <div className="flex items-center gap-2">
        <input type="range" min={min} max={max} step={step} value={value}
          onChange={e=>onChange(+e.target.value)} className="flex-1 accent-[#00C8FF]" />
        <input type="number" min={min} max={max} step={step} value={value}
          onChange={e=>{const v=+e.target.value; if(!isNaN(v)&&v>=min&&v<=max) onChange(v);}}
          className="w-20 bg-[#050A12] border border-slate-700 text-[12px] font-tech-mono text-[#00C8FF] px-2 py-1 text-right"
        />
        <span className="text-[9px] font-tech-mono text-slate-600 w-6">{unit}</span>
      </div>
    </div>
  );
}

// ─── Scène 3D ───────────────────────────────────
function Scene({d,oh,th}:{d:number;oh:number;th:number}){
  const hidden=hiddenH(d,oh);
  const maxDim=Math.max(d,80); const s=7/maxDim; const halfD=(d/2)*s;
  const arc=d/R;
  const curve=useMemo(()=>{
    const p:THREE.Vector3[]=[];
    for(let i=0;i<=120;i++){const a=-arc/2+(i/120)*arc;p.push(new THREE.Vector3(Math.sin(a)*R*s,(Math.cos(a)-1)*R*s,0));}
    return p;
  },[d,s,arc]);
  const maxH=Math.max(oh,th,0.01); const hs=Math.min(s*200,4/maxH);
  const oA=-arc/2,tA=arc/2;
  const oGx=Math.sin(oA)*R*s,oGy=(Math.cos(oA)-1)*R*s;
  const tGx=Math.sin(tA)*R*s,tGy=(Math.cos(tA)-1)*R*s;
  const oNx=Math.sin(oA),oNy=Math.cos(oA),tNx=Math.sin(tA),tNy=Math.cos(tA);
  const obsP:[number,number,number]=[oGx+oNx*oh*hs,oGy+oNy*oh*hs,0];
  const tgtP:[number,number,number]=[tGx+tNx*th*hs,tGy+tNy*th*hs,0];
  const hidP:[number,number,number]=[tGx+tNx*Math.min(hidden,th)*hs,tGy+tNy*Math.min(hidden,th)*hs,0];
  const vis=hidden<th;

  // Point d'horizon sur la courbe
  const hDist=horizonDist(oh);
  const hAngle=-arc/2 + (hDist/d)*arc;
  const hx=Math.sin(hAngle)*R*s, hy=(Math.cos(hAngle)-1)*R*s;

  return <>
    <ambientLight intensity={0.5}/>
    {/* GLOBE */}
    <group position={[0,2.5,0]}>
      <Line points={curve} color="#00C8FF" lineWidth={2}/>
      {/* Observateur */}
      <Line points={[new THREE.Vector3(oGx,oGy,0),new THREE.Vector3(...obsP)]} color="#00C8FF" lineWidth={2}/>
      <mesh position={obsP}><sphereGeometry args={[0.06,12,12]}/><meshBasicMaterial color="#00C8FF"/></mesh>
      {/* Cible — partie visible (vert) */}
      {vis && <Line points={[
        new THREE.Vector3(tGx+tNx*hidden*hs,tGy+tNy*hidden*hs,0),
        new THREE.Vector3(...tgtP)
      ]} color="#00E87B" lineWidth={2.5}/>}
      {/* Cible — partie cachée (rouge) */}
      {hidden>0 && <Line points={[new THREE.Vector3(tGx,tGy,0),new THREE.Vector3(...hidP)]} color="#FF4444" lineWidth={3}/>}
      {/* Ligne de visée */}
      <Line points={[new THREE.Vector3(...obsP),new THREE.Vector3(...tgtP)]}
        color={vis?'#00E87B':'#FF4444'} lineWidth={1} opacity={0.4} transparent dashed dashSize={0.08} gapSize={0.04}/>
      {/* Ligne d'horizon */}
      {hDist<d && <Line points={[new THREE.Vector3(...obsP),new THREE.Vector3(hx,hy,0)]}
        color="#FFFFFF" lineWidth={0.5} opacity={0.2} transparent dashed dashSize={0.05} gapSize={0.03}/>}
      <Html position={[0,4.2,0]} center distanceFactor={12} style={{pointerEvents:'none'}}>
        <div style={{color:'#00C8FF',fontSize:'10px',fontFamily:'monospace',letterSpacing:'0.1em'}}>MODÈLE GLOBE (R = 6 371 km)</div>
      </Html>
    </group>
    {/* PLAN */}
    <group position={[0,-2.5,0]}>
      <Line points={[new THREE.Vector3(-halfD-0.5,0,0),new THREE.Vector3(halfD+0.5,0,0)]} color="#D4A843" lineWidth={2}/>
      <Line points={[new THREE.Vector3(-halfD,0,0),new THREE.Vector3(-halfD,oh*hs,0)]} color="#D4A843" lineWidth={2}/>
      <mesh position={[-halfD,oh*hs,0]}><sphereGeometry args={[0.06,12,12]}/><meshBasicMaterial color="#D4A843"/></mesh>
      <Line points={[new THREE.Vector3(halfD,0,0),new THREE.Vector3(halfD,th*hs,0)]} color="#00E87B" lineWidth={2}/>
      <Line points={[new THREE.Vector3(-halfD,oh*hs,0),new THREE.Vector3(halfD,th*hs,0)]}
        color="#00E87B" lineWidth={1} opacity={0.4} transparent dashed dashSize={0.08} gapSize={0.04}/>
      <Html position={[0,2,0]} center distanceFactor={12} style={{pointerEvents:'none'}}>
        <div style={{color:'#D4A843',fontSize:'10px',fontFamily:'monospace',letterSpacing:'0.1em'}}>MODÈLE PLAN — toujours visible</div>
      </Html>
    </group>
    <OrbitControls enablePan enableZoom maxDistance={20} minDistance={3}/>
  </>;
}

export default function CurvatureCalc(){
  const [dist,setDist]=useState(90);
  const [obsM,setObsM]=useState(1.7);
  const [tgtM,setTgtM]=useState(443);
  const oh=obsM/1000,th=tgtM/1000;
  const hidden=hiddenH(dist,oh);
  const hDist=horizonDist(oh);
  const drop=curvDrop(dist);
  const vis=hidden<th;

  return <div className="w-full">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <NumInput label="DISTANCE" value={dist} onChange={setDist} min={1} max={2000} unit="km"/>
      <NumInput label="HAUTEUR OBSERVATEUR" value={obsM} onChange={setObsM} min={1} max={500000} unit="m"/>
      <NumInput label="HAUTEUR CIBLE" value={tgtM} onChange={setTgtM} min={1} max={10000} unit="m"/>
    </div>
    <div className="flex flex-wrap gap-2 mb-4">
      <span className="text-[8px] font-tech-mono text-slate-600 self-center">CAS RÉELS :</span>
      {PRESETS.map(p=>(
        <button key={p.label} onClick={()=>{setDist(p.d);setObsM(p.oh);setTgtM(p.th);}}
          title={p.note}
          className="px-3 py-1 text-[8px] font-tech-mono border border-slate-700 text-slate-400 hover:border-[#00C8FF]/40 hover:text-[#00C8FF] transition-all"
        >{p.label}</button>
      ))}
    </div>
    <div className="w-full h-[50vh] md:h-[60vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10"/>
      <Canvas camera={{position:[0,0,12],fov:45}}>
        <Scene d={dist} oh={oh} th={th}/>
      </Canvas>
    </div>
    <div className="mt-4 grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="border border-cyan-900/30 bg-[#0A1020] p-3">
        <div className="text-[8px] font-tech-mono text-cyan-400/60 tracking-widest mb-1">HORIZON</div>
        <div className="text-[16px] font-tech-mono text-cyan-400">{hDist.toFixed(1)} km</div>
        <div className="text-[8px] font-tech-mono text-slate-500 mt-1">a = √[(R+h)² - R²]</div>
      </div>
      <div className="border border-red-900/30 bg-[#0A1020] p-3">
        <div className="text-[8px] font-tech-mono text-red-400/60 tracking-widest mb-1">CHUTE COURBURE</div>
        <div className="text-[16px] font-tech-mono text-red-400">{fmt(drop)}</div>
        <div className="text-[8px] font-tech-mono text-slate-500 mt-1">h = d²/(2R)</div>
      </div>
      <div className="border border-amber-900/30 bg-[#0A1020] p-3">
        <div className="text-[8px] font-tech-mono text-amber-400/60 tracking-widest mb-1">HAUTEUR CACHÉE</div>
        <div className="text-[16px] font-tech-mono text-amber-400">{fmt(hidden)}</div>
        <div className="text-[8px] font-tech-mono text-slate-500 mt-1">x = √[R²+(d-a)²]-R</div>
      </div>
      <div className={`border p-3 ${vis?'border-green-900/30 bg-green-950/20':'border-red-900/30 bg-red-950/20'}`}>
        <div className="text-[8px] font-tech-mono text-slate-400/60 tracking-widest mb-1">VERDICT GLOBE</div>
        <div className={`text-[14px] font-tech-mono ${vis?'text-green-400':'text-red-400'}`}>{vis?'✓ CIBLE VISIBLE':'✗ CIBLE MASQUÉE'}</div>
        <div className="text-[8px] font-tech-mono text-slate-500 mt-1">
          {vis?`Visible : ${fmt(th-hidden)} sur ${fmt(th)}`:`Caché : ${fmt(hidden)} &gt; cible : ${fmt(th)}`}
        </div>
      </div>
    </div>
    <div className="mt-3 text-[9px] font-tech-mono text-slate-600 px-1">⚠ Ne tient pas compte de la réfraction atmosphérique.</div>
    <div className="mt-3 border-t border-slate-800/30 pt-3 flex items-center gap-4">
      <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
      <a href="/article/leau-ne-ment-pas" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF]">L&apos;eau ne ment pas →</a>
      <a href="/article/ce-quon-voit-quand-on-ne-devrait-plus-voir" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF]">Ce qu&apos;on voit →</a>
    </div>
  </div>;
}
