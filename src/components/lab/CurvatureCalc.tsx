'use client';
import { useState, useMemo } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

const R_EARTH = 6371; // km

// ─── Formules avec réfraction ───────────────────
// Rayon effectif : R' = R / (1 - k)
// k=0 → pas de réfraction, k=0.143 → standard, k≥1 → terre paraît plate/concave
function Reff(k:number):number{ return R_EARTH / (1 - k); }

function horizonDist(h:number, k:number):number{
  const r = Reff(k);
  return Math.sqrt((r+h)**2 - r**2);
}

function hiddenH(d:number, h:number, k:number):number{
  const r = Reff(k);
  const a = horizonDist(h, k);
  if(d<=a) return 0;
  return Math.sqrt(r**2 + (d-a)**2) - r;
}

function curvDrop(d:number, k:number):number{
  const r = Reff(k);
  return d**2 / (2*r);
}

function fmt(km:number):string{
  if(km>=1) return km.toFixed(2)+' km';
  if(km>=0.001) return(km*1000).toFixed(1)+' m';
  return(km*100000).toFixed(1)+' cm';
}

// ─── Cas réels avec k estimé ────────────────────
const PRESETS = [
  { label:'Finestrelles → Alpes (443 km)', d:443, oh:2820, th:4102, k:0.14,
    desc:'Pic de Finestrelles 2 820 m → Barre des Écrins 4 102 m. Record 2016, Marc Bret. Réfraction standard.' },
  { label:'Navire — Île Maurice (321 km)', d:321, oh:0, th:30, k:0.45,
    desc:'Obs. niveau de la mer → navire ~30 m. Fata Morgana 1895. Super-réfraction k≈0.45.' },
  { label:'Notre-Dame d\'Anvers (241 km)', d:241, oh:2, th:123, k:0.38,
    desc:'Navire en mer du Nord → flèche 123 m. Réfraction forte (air froid sur mer) k≈0.38.' },
  { label:'Shkhara → Elbrouz (493 km)', d:493, oh:3107, th:5642, k:0.18,
    desc:'Mont Karagöl 3 107 m → Mont Elbrouz 5 642 m. Photo R. Ježík. Super-réfraction k≈0.18.' },
];

// ─── Input slider + saisie ──────────────────────
function NumInput({label,value,onChange,min,max,unit,step=1}:{
  label:string;value:number;onChange:(v:number)=>void;min:number;max:number;unit:string;step?:number;
}){
  return(
    <div className="border border-slate-800/50 bg-[#0A1020] p-4">
      <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">{label}</label>
      <div className="flex items-center gap-3">
        <input type="range" min={min} max={max} step={step} value={value}
          onChange={e=>onChange(+e.target.value)} className="flex-1 accent-[#00C8FF] h-2"/>
        <input type="number" min={min} max={max} step={step} value={value}
          onChange={e=>{const v=+e.target.value;if(!isNaN(v))onChange(Math.max(min,Math.min(max,v)));}}
          className="w-24 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#00C8FF] px-3 py-2 text-right rounded-none"/>
        <span className="text-[12px] font-tech-mono text-slate-500 w-8">{unit}</span>
      </div>
    </div>
  );
}

// ─── Scène 3D ───────────────────────────────────
function Scene({d,oh,th,k}:{d:number;oh:number;th:number;k:number}){
  const hidden=hiddenH(d,oh,k);
  const hiddenNoRef=hiddenH(d,oh,0);
  const rEff=Reff(k);
  const maxDim=Math.max(d,60);const s=5/maxDim;
  const arc=d/rEff;
  const arcNoRef=d/R_EARTH;

  // Courbe AVEC réfraction (rayon effectif)
  const curveRef=useMemo(()=>{
    const p:THREE.Vector3[]=[];
    for(let i=0;i<=150;i++){const a=-arc/2+(i/150)*arc;p.push(new THREE.Vector3(Math.sin(a)*rEff*s,(Math.cos(a)-1)*rEff*s,0));}
    return p;
  },[d,s,arc,rEff]);

  // Courbe SANS réfraction (rayon réel) — en pointillé pour comparaison
  const curveNoRef=useMemo(()=>{
    const p:THREE.Vector3[]=[];
    for(let i=0;i<=150;i++){const a=-arcNoRef/2+(i/150)*arcNoRef;p.push(new THREE.Vector3(Math.sin(a)*R_EARTH*s,(Math.cos(a)-1)*R_EARTH*s,0));}
    return p;
  },[d,s,arcNoRef]);

  const maxH=Math.max(oh,th,0.001);const hs=Math.min(s*150,3/maxH);
  const halfD=(d/2)*s;

  // Positions sur la courbe avec réfraction
  const oA=-arc/2,tA=arc/2;
  const oGx=Math.sin(oA)*rEff*s,oGy=(Math.cos(oA)-1)*rEff*s;
  const tGx=Math.sin(tA)*rEff*s,tGy=(Math.cos(tA)-1)*rEff*s;
  const oNx=Math.sin(oA),oNy=Math.cos(oA),tNx=Math.sin(tA),tNy=Math.cos(tA);
  const obsP:[number,number,number]=[oGx+oNx*oh*hs,oGy+oNy*oh*hs,0];
  const tgtP:[number,number,number]=[tGx+tNx*th*hs,tGy+tNy*th*hs,0];
  const hidP:[number,number,number]=[tGx+tNx*Math.min(hidden,th)*hs,tGy+tNy*Math.min(hidden,th)*hs,0];
  const vis=hidden<th;

  return<>
    <ambientLight intensity={0.5}/>
    {/* GLOBE avec réfraction */}
    <group position={[0,3,0]}>
      {/* Courbe sans réfraction (gris pointillé) si k>0 */}
      {k>0.01 && <Line points={curveNoRef} color="#666666" lineWidth={1} opacity={0.3} transparent dashed dashSize={0.06} gapSize={0.04}/>}
      {/* Courbe avec réfraction */}
      <Line points={curveRef} color="#00C8FF" lineWidth={2.5}/>
      {/* Observateur */}
      <Line points={[new THREE.Vector3(oGx,oGy,0),new THREE.Vector3(...obsP)]} color="#00C8FF" lineWidth={2}/>
      <mesh position={obsP}><sphereGeometry args={[0.08,12,12]}/><meshBasicMaterial color="#00C8FF"/></mesh>
      {/* Cible visible (vert) */}
      {vis&&<Line points={[new THREE.Vector3(tGx+tNx*hidden*hs,tGy+tNy*hidden*hs,0),new THREE.Vector3(...tgtP)]} color="#00E87B" lineWidth={3}/>}
      {/* Cible cachée (rouge) */}
      {hidden>0&&<Line points={[new THREE.Vector3(tGx,tGy,0),new THREE.Vector3(...hidP)]} color="#FF4444" lineWidth={4}/>}
      {/* Ligne de visée */}
      <Line points={[new THREE.Vector3(...obsP),new THREE.Vector3(...tgtP)]}
        color={vis?'#00E87B':'#FF4444'} lineWidth={1} opacity={0.4} transparent dashed dashSize={0.08} gapSize={0.04}/>
      <Html position={[0,2.8,0]} center distanceFactor={10} style={{pointerEvents:'none'}}>
        <div style={{color:'#00C8FF',fontSize:'13px',fontFamily:'monospace',letterSpacing:'0.12em',fontWeight:'bold'}}>
          MODÈLE GLOBE {k>0.01 ? `(R\u2019 = ${Math.round(rEff)} km)` : '(R = 6 371 km)'}
        </div>
      </Html>
      {k>0.01 && <Html position={[0,2.2,0]} center distanceFactor={10} style={{pointerEvents:'none'}}>
        <div style={{color:'#666',fontSize:'10px',fontFamily:'monospace'}}>pointillé = sans réfraction</div>
      </Html>}
    </group>
    {/* PLAN */}
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

// ─── COMPOSANT PRINCIPAL ────────────────────────
export default function CurvatureCalc(){
  const [dist,setDist]=useState(443);
  const [obsM,setObsM]=useState(2820);
  const [tgtM,setTgtM]=useState(4102);
  const [k,setK]=useState(0.143); // Standard par défaut

  const oh=obsM/1000,th=tgtM/1000;
  const hidden=hiddenH(dist,oh,k);
  const hiddenNoRef=hiddenH(dist,oh,0);
  const hDist=horizonDist(oh,k);
  const hDistNoRef=horizonDist(oh,0);
  const drop=curvDrop(dist,k);
  const dropNoRef=curvDrop(dist,0);
  const vis=hidden<th;
  const visNoRef=hiddenNoRef<th;

  return<div className="w-full">
    {/* Sliders principaux */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <NumInput label="DISTANCE" value={dist} onChange={setDist} min={0} max={2000} unit="km"/>
      <NumInput label="HAUTEUR OBSERVATEUR" value={obsM} onChange={setObsM} min={0} max={500000} unit="m"/>
      <NumInput label="HAUTEUR CIBLE" value={tgtM} onChange={setTgtM} min={0} max={10000} unit="m"/>
    </div>

    {/* Slider réfraction */}
    <div className="border border-[#D4A843]/30 bg-[#0A1020] p-4 mb-4">
      <div className="flex items-center gap-4">
        <label className="text-[11px] font-tech-mono text-[#D4A843] tracking-widest whitespace-nowrap">RÉFRACTION (k)</label>
        <input type="range" min={0} max={0.8} step={0.001} value={k}
          onChange={e=>setK(+e.target.value)} className="flex-1 accent-[#D4A843] h-2"/>
        <input type="number" min={0} max={0.99} step={0.001} value={k}
          onChange={e=>{const v=+e.target.value;if(!isNaN(v))setK(Math.max(0,Math.min(0.99,v)));}}
          className="w-20 bg-[#050A12] border border-[#D4A843]/40 text-[14px] font-tech-mono text-[#D4A843] px-3 py-2 text-right rounded-none"/>
      </div>
      <div className="flex flex-wrap gap-3 mt-3">
        <button onClick={()=>setK(0)} className="px-3 py-1 text-[10px] font-tech-mono border border-slate-600 text-slate-400 hover:text-white">k=0 (aucune)</button>
        <button onClick={()=>setK(0.143)} className="px-3 py-1 text-[10px] font-tech-mono border border-[#D4A843]/40 text-[#D4A843] hover:bg-[#D4A843]/10">k=0.143 (standard)</button>
        <button onClick={()=>setK(0.17)} className="px-3 py-1 text-[10px] font-tech-mono border border-[#D4A843]/40 text-[#D4A843] hover:bg-[#D4A843]/10">k=0.17 (mer)</button>
        <button onClick={()=>setK(0.38)} className="px-3 py-1 text-[10px] font-tech-mono border border-amber-700/40 text-amber-400 hover:bg-amber-400/10">k=0.38 (forte)</button>
        <button onClick={()=>setK(0.5)} className="px-3 py-1 text-[10px] font-tech-mono border border-red-700/40 text-red-400 hover:bg-red-400/10">k=0.5 (super)</button>
        <span className="text-[10px] font-tech-mono text-slate-600 self-center ml-2">
          R&apos; = {Math.round(Reff(k))} km {k>0.01 ? `(×${(Reff(k)/R_EARTH).toFixed(2)})` : ''}
        </span>
      </div>
    </div>

    {/* Cas réels */}
    <div className="flex flex-wrap gap-2 mb-5">
      <span className="text-[11px] font-tech-mono text-slate-500 self-center">CAS RÉELS :</span>
      {PRESETS.map(p=>(
        <button key={p.label} onClick={()=>{setDist(p.d);setObsM(p.oh);setTgtM(p.th);setK(p.k);}}
          title={p.desc}
          className="px-4 py-2 text-[11px] font-tech-mono border border-slate-600 text-slate-300 hover:border-[#00C8FF]/50 hover:text-[#00C8FF] transition-all"
        >{p.label}</button>
      ))}
    </div>

    {/* Canvas 3D */}
    <div className="w-full h-[55vh] md:h-[65vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10"/>
      <Canvas camera={{position:[0,0,12],fov:45}}>
        <Scene d={dist} oh={oh} th={th} k={k}/>
      </Canvas>
    </div>

    {/* Résultats — avec et sans réfraction */}
    <div className="mt-5 grid grid-cols-2 md:grid-cols-5 gap-3">
      <div className="border border-cyan-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">HORIZON</div>
        <div className="text-[20px] font-tech-mono text-cyan-400 font-bold">{hDist.toFixed(1)} km</div>
        {k>0.01&&<div className="text-[10px] font-tech-mono text-slate-600 mt-1">sans réf: {hDistNoRef.toFixed(1)} km</div>}
      </div>
      <div className="border border-red-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-red-400/70 tracking-widest mb-2">CHUTE COURBURE</div>
        <div className="text-[20px] font-tech-mono text-red-400 font-bold">{fmt(drop)}</div>
        {k>0.01&&<div className="text-[10px] font-tech-mono text-slate-600 mt-1">sans réf: {fmt(dropNoRef)}</div>}
      </div>
      <div className="border border-amber-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-amber-400/70 tracking-widest mb-2">HAUTEUR CACHÉE</div>
        <div className="text-[20px] font-tech-mono text-amber-400 font-bold">{fmt(hidden)}</div>
        {k>0.01&&<div className="text-[10px] font-tech-mono text-slate-600 mt-1">sans réf: {fmt(hiddenNoRef)}</div>}
      </div>
      <div className={`border p-4 ${vis?'border-green-900/30 bg-green-950/20':'border-red-900/30 bg-red-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">AVEC RÉFRACTION</div>
        <div className={`text-[18px] font-tech-mono font-bold ${vis?'text-green-400':'text-red-400'}`}>{vis?'✓ VISIBLE':'✗ MASQUÉE'}</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          {vis?`${fmt(th-hidden)} visible sur ${fmt(th)}`:`${fmt(hidden)} caché > ${fmt(th)}`}
        </div>
      </div>
      <div className={`border p-4 ${visNoRef?'border-green-900/30 bg-green-950/20':'border-red-900/30 bg-red-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">SANS RÉFRACTION</div>
        <div className={`text-[18px] font-tech-mono font-bold ${visNoRef?'text-green-400':'text-red-400'}`}>{visNoRef?'✓ VISIBLE':'✗ MASQUÉE'}</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          {visNoRef?`${fmt(th-hiddenNoRef)} visible`:`${fmt(hiddenNoRef)} caché`}
        </div>
      </div>
    </div>

    <div className="mt-4 border border-[#D4A843]/20 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-[#D4A843]/60 mb-2">À PROPOS DE LA RÉFRACTION</div>
      <p className="text-[12px] text-[#C8D8E8]/50 font-rajdhani leading-relaxed">
        La réfraction atmosphérique courbe les rayons lumineux vers le sol (l&apos;air dense au sol a un indice plus élevé). 
        L&apos;effet est modélisé par un rayon terrestre effectif R&apos; = R/(1−k). 
        En conditions standard (k≈0.143), l&apos;horizon recule de ~8%. 
        Sur mer froide (k≈0.17-0.38), la réfraction est plus forte. 
        En super-réfraction (k&gt;0.4, Fata Morgana), des objets à des centaines de km deviennent visibles.
        Quand k≥1, la lumière suit la courbure terrestre : la Terre paraît plate.
      </p>
    </div>

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-500">ARTICLES :</span>
      <a href="/article/leau-ne-ment-pas" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;eau ne ment pas →</a>
      <a href="/article/ce-quon-voit-quand-on-ne-devrait-plus-voir" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">Ce qu&apos;on voit →</a>
      <a href="/article/lhorizon-la-perspective-et-la-refraction" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;horizon et la réfraction →</a>
    </div>
  </div>;
}
