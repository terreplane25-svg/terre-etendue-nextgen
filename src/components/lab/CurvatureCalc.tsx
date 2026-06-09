'use client';
import { useState, useMemo, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';

const R_EARTH = 6371;

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

const PRESETS = [
  { label:'Finestrelles → Écrins (443 km)', d:443, oh:2820, th:4102, k:0.14,
    desc:'Pic de Finestrelles 2 820 m → Barre des Écrins 4 102 m. Record 2016.' },
  { label:'Canigou → Marseille (263 km)', d:263, oh:0, th:2784, k:0.17,
    desc:'Vieux-Port de Marseille → Pic du Canigou 2 784 m. Classique en Provence.' },
  { label:'Chicago skyline (90 km)', d:90, oh:0, th:0.527, k:0.143,
    desc:'Chicago skyline (527 m) vu depuis l\'autre rive du lac Michigan.' },
  { label:'Notre-Dame d\'Anvers (241 km)', d:241, oh:2, th:123, k:0.38,
    desc:'Navire en mer du Nord → flèche 123 m. Réfraction forte k≈0.38.' },
  { label:'Shkhara → Elbrouz (493 km)', d:493, oh:3107, th:5642, k:0.18,
    desc:'Mont Karagöl 3 107 m → Mont Elbrouz 5 642 m. Photo R. Ježík.' },
  { label:'Île Maurice — navire (321 km)', d:321, oh:0, th:30, k:0.45,
    desc:'Obs. niveau de la mer → navire ~30 m. Fata Morgana. Super-réfraction.' },
];

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

// ─── Graphique SVG : courbure cachée en fonction de la distance ───
function CurveGraph({ dist, oh, th, k }:{ dist:number; oh:number; th:number; k:number }) {
  const W = 500, H = 180, PAD = 44;
  const maxD = Math.max(dist * 1.3, 100);
  const steps = 100;

  const points = useMemo(() => {
    const pts: { x:number; y:number; d:number; h:number }[] = [];
    let maxH = 0.001;
    for (let i = 0; i <= steps; i++) {
      const d = (i / steps) * maxD;
      const h = hiddenH(d, oh / 1000, k);
      if (h > maxH) maxH = h;
      pts.push({ x: 0, y: 0, d, h });
    }
    maxH = Math.max(maxH, th / 1000 * 1.2, 0.01);
    for (const p of pts) {
      p.x = PAD + (p.d / maxD) * (W - PAD * 2);
      p.y = H - PAD - (p.h / maxH) * (H - PAD * 2);
    }
    return { pts, maxH };
  }, [dist, oh, th, k, maxD]);

  const pathD = points.pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
  const curHidden = hiddenH(dist, oh / 1000, k);
  const curX = PAD + (dist / maxD) * (W - PAD * 2);
  const curY = H - PAD - (curHidden / points.maxH) * (H - PAD * 2);
  const tgtY = H - PAD - ((th / 1000) / points.maxH) * (H - PAD * 2);

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 180 }}>
      <rect x={PAD} y={4} width={W - PAD * 2} height={H - PAD - 4} fill="#050A12" rx={4} />
      {/* Grid lines */}
      {[0.25, 0.5, 0.75].map(f => (
        <line key={f} x1={PAD} y1={H - PAD - f * (H - PAD * 2)} x2={W - PAD} y2={H - PAD - f * (H - PAD * 2)}
          stroke="#1a2540" strokeWidth={0.5} />
      ))}
      {/* Target height line */}
      <line x1={PAD} y1={tgtY} x2={W - PAD} y2={tgtY} stroke="#D4A843" strokeWidth={1} strokeDasharray="4,3" opacity={0.6} />
      <text x={W - PAD + 4} y={tgtY + 3} fill="#D4A843" fontSize={8} fontFamily="monospace">cible</text>
      {/* Curve */}
      <path d={pathD} fill="none" stroke="#00C8FF" strokeWidth={2} />
      {/* Current point */}
      <circle cx={curX} cy={curY} r={4} fill={curHidden < th / 1000 ? '#00E87B' : '#FF4444'} />
      <line x1={curX} y1={H - PAD} x2={curX} y2={curY} stroke={curHidden < th / 1000 ? '#00E87B' : '#FF4444'} strokeWidth={1} strokeDasharray="2,2" opacity={0.5} />
      {/* Axes */}
      <line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="#607890" strokeWidth={1} />
      <line x1={PAD} y1={4} x2={PAD} y2={H - PAD} stroke="#607890" strokeWidth={1} />
      <text x={W / 2} y={H - 4} fill="#607890" fontSize={9} fontFamily="monospace" textAnchor="middle">Distance (km)</text>
      <text x={8} y={H / 2} fill="#607890" fontSize={9} fontFamily="monospace" textAnchor="middle" transform={`rotate(-90,8,${H / 2})`}>Caché (km)</text>
      {/* Tick labels */}
      <text x={PAD} y={H - PAD + 12} fill="#607890" fontSize={8} fontFamily="monospace" textAnchor="middle">0</text>
      <text x={W - PAD} y={H - PAD + 12} fill="#607890" fontSize={8} fontFamily="monospace" textAnchor="middle">{Math.round(maxD)}</text>
      <text x={PAD - 4} y={H - PAD} fill="#607890" fontSize={8} fontFamily="monospace" textAnchor="end">0</text>
      <text x={PAD - 4} y={10} fill="#607890" fontSize={8} fontFamily="monospace" textAnchor="end">{points.maxH >= 1 ? points.maxH.toFixed(1) + ' km' : (points.maxH * 1000).toFixed(0) + ' m'}</text>
      {/* Legend */}
      <text x={curX + 8} y={curY - 6} fill="#C8D8E8" fontSize={8} fontFamily="monospace">{fmt(curHidden)} caché à {dist} km</text>
    </svg>
  );
}

// ─── Scène 3D ───────────────────────────────────
function Scene({d,oh,th,k}:{d:number;oh:number;th:number;k:number}){
  const hidden=hiddenH(d,oh,k);
  const rEff=Reff(k);
  const maxDim=Math.max(d,60);const s=5/maxDim;
  const arc=d/rEff;
  const arcNoRef=d/R_EARTH;

  const curveRef=useMemo(()=>{
    const p:THREE.Vector3[]=[];
    for(let i=0;i<=150;i++){const a=-arc/2+(i/150)*arc;p.push(new THREE.Vector3(Math.sin(a)*rEff*s,(Math.cos(a)-1)*rEff*s,0));}
    return p;
  },[d,s,arc,rEff]);

  const curveNoRef=useMemo(()=>{
    const p:THREE.Vector3[]=[];
    for(let i=0;i<=150;i++){const a=-arcNoRef/2+(i/150)*arcNoRef;p.push(new THREE.Vector3(Math.sin(a)*R_EARTH*s,(Math.cos(a)-1)*R_EARTH*s,0));}
    return p;
  },[d,s,arcNoRef]);

  const maxH=Math.max(oh,th,0.001);const hs=Math.min(s*150,3/maxH);
  const halfD=(d/2)*s;

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
    <group position={[0,3,0]}>
      {k>0.01 && <Line points={curveNoRef} color="#666666" lineWidth={1} opacity={0.3} transparent dashed dashSize={0.06} gapSize={0.04}/>}
      <Line points={curveRef} color="#00C8FF" lineWidth={2.5}/>
      <Line points={[new THREE.Vector3(oGx,oGy,0),new THREE.Vector3(...obsP)]} color="#00C8FF" lineWidth={2}/>
      <mesh position={obsP}><sphereGeometry args={[0.08,12,12]}/><meshBasicMaterial color="#00C8FF"/></mesh>
      {vis&&<Line points={[new THREE.Vector3(tGx+tNx*hidden*hs,tGy+tNy*hidden*hs,0),new THREE.Vector3(...tgtP)]} color="#00E87B" lineWidth={3}/>}
      {hidden>0&&<Line points={[new THREE.Vector3(tGx,tGy,0),new THREE.Vector3(...hidP)]} color="#FF4444" lineWidth={4}/>}
      <Line points={[new THREE.Vector3(...obsP),new THREE.Vector3(...tgtP)]}
        color={vis?'#00E87B':'#FF4444'} lineWidth={1} opacity={0.4} transparent dashed dashSize={0.08} gapSize={0.04}/>
      <Html position={[0,2.8,0]} center distanceFactor={10} style={{pointerEvents:'none'}}>
        <div style={{color:'#00C8FF',fontSize:'13px',fontFamily:'monospace',letterSpacing:'0.12em',fontWeight:'bold'}}>
          MODÈLE GLOBE {k>0.01 ? `(R’ = ${Math.round(rEff)} km)` : '(R = 6 371 km)'}
        </div>
      </Html>
      {k>0.01 && <Html position={[0,2.2,0]} center distanceFactor={10} style={{pointerEvents:'none'}}>
        <div style={{color:'#666',fontSize:'10px',fontFamily:'monospace'}}>pointillé = sans réfraction</div>
      </Html>}
    </group>
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
  const [k,setK]=useState(0.143);
  const [copied,setCopied]=useState(false);

  const oh=obsM/1000,th=tgtM/1000;
  const hidden=hiddenH(dist,oh,k);
  const hiddenNoRef=hiddenH(dist,oh,0);
  const hDist=horizonDist(oh,k);
  const hDistNoRef=horizonDist(oh,0);
  const drop=curvDrop(dist,k);
  const dropNoRef=curvDrop(dist,0);
  const vis=hidden<th;
  const visNoRef=hiddenNoRef<th;

  const copyResults = useCallback(() => {
    const txt = [
      `═══ CALCULATEUR DE COURBURE ═══`,
      `Distance : ${dist} km`,
      `Observateur : ${obsM} m | Cible : ${tgtM} m`,
      `Réfraction k = ${k} (R' = ${Math.round(Reff(k))} km)`,
      `───`,
      `Horizon : ${hDist.toFixed(1)} km ${k > 0.01 ? `(sans réf: ${hDistNoRef.toFixed(1)} km)` : ''}`,
      `Chute de courbure : ${fmt(drop)} ${k > 0.01 ? `(sans réf: ${fmt(dropNoRef)})` : ''}`,
      `Hauteur cachée : ${fmt(hidden)} ${k > 0.01 ? `(sans réf: ${fmt(hiddenNoRef)})` : ''}`,
      `Visibilité : ${vis ? 'VISIBLE' : 'MASQUÉE'} (avec réf.) | ${visNoRef ? 'VISIBLE' : 'MASQUÉE'} (sans réf.)`,
      `───`,
      `Source : Terre Étendue — Calculateur de Courbure`,
    ].join('\n');
    navigator.clipboard.writeText(txt).then(() => {
      setCopied(true);
      setTimeout(() => setCopied(false), 2000);
    });
  }, [dist, obsM, tgtM, k, hDist, hDistNoRef, drop, dropNoRef, hidden, hiddenNoRef, vis, visNoRef]);

  return<div className="w-full">
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-4">
      <NumInput label="DISTANCE" value={dist} onChange={setDist} min={0} max={2000} unit="km"/>
      <NumInput label="HAUTEUR OBSERVATEUR" value={obsM} onChange={setObsM} min={0} max={500000} unit="m"/>
      <NumInput label="HAUTEUR CIBLE" value={tgtM} onChange={setTgtM} min={0} max={10000} unit="m"/>
    </div>

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

    <div className="mb-5">
      <div className="text-[11px] font-tech-mono text-slate-500 mb-3">CAS RÉELS DOCUMENTÉS :</div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
        {PRESETS.map(p=>{
          const fmtH = (m:number) => m>=1000 ? `${(m/1000).toFixed(1)} km` : `${m} m`;
          return (
            <button key={p.label} onClick={()=>{setDist(p.d);setObsM(p.oh);setTgtM(p.th);setK(p.k);}}
              className="border border-slate-700 bg-[#0A1020] p-3 text-left hover:border-[#00C8FF]/50 transition-all group"
            >
              <div className="text-[12px] font-tech-mono text-slate-200 group-hover:text-[#00C8FF] mb-2 font-bold">{p.label}</div>
              <div className="text-[10px] font-tech-mono text-slate-500 space-y-0.5">
                <div>Obs : <span className="text-[#00C8FF]/70">{fmtH(p.oh)}</span> — Cible : <span className="text-[#00C8FF]/70">{fmtH(p.th)}</span></div>
                <div>Réfraction : <span className="text-[#D4A843]/70">k = {p.k}</span></div>
              </div>
            </button>
          );
        })}
      </div>
    </div>

    {/* Graphique SVG : hauteur cachée vs distance */}
    <div className="mb-4 border border-slate-800/50 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-slate-400 tracking-widest mb-3">HAUTEUR CACHÉE EN FONCTION DE LA DISTANCE</div>
      <CurveGraph dist={dist} oh={obsM} th={tgtM} k={k} />
      <div className="flex items-center gap-4 mt-2">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-[#00C8FF]" />
          <span className="text-[9px] font-tech-mono text-slate-500">hauteur cachée (globe)</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-[#D4A843] opacity-60" style={{ borderTop: '1px dashed #D4A843' }} />
          <span className="text-[9px] font-tech-mono text-slate-500">hauteur de la cible</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#00E87B]" />
          <span className="text-[9px] font-tech-mono text-slate-500">visible</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-2 h-2 rounded-full bg-[#FF4444]" />
          <span className="text-[9px] font-tech-mono text-slate-500">masquée</span>
        </div>
      </div>
    </div>

    {/* Canvas 3D */}
    <div className="w-full h-[50vh] md:h-[60vh] border border-slate-800/50 bg-[#030810] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10"/>
      <Canvas camera={{position:[0,0,12],fov:45}}>
        <Scene d={dist} oh={oh} th={th} k={k}/>
      </Canvas>
    </div>

    {/* Résultats */}
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

    {/* Bouton copier */}
    <div className="mt-4 flex gap-3">
      <button onClick={copyResults}
        className="px-5 py-2.5 text-[11px] font-tech-mono tracking-widest border transition-all"
        style={{
          borderColor: copied ? '#00E87B99' : '#00C8FF40',
          backgroundColor: copied ? '#00E87B1a' : '#00C8FF0a',
          color: copied ? '#00E87B' : '#00C8FF',
        }}>
        {copied ? '✓ COPIÉ' : '⎘ COPIER LES RÉSULTATS'}
      </button>
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

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex flex-wrap items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-500">ARTICLES :</span>
      <a href="/article/leau-ne-ment-pas" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;eau ne ment pas →</a>
      <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;hypothèse nulle →</a>
      <a href="/article/loeil-humain-la-machine-a-voir-qui-faconne-notre-realite" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;œil humain →</a>
    </div>
  </div>;
}
