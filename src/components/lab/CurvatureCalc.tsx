'use client';
import { useState, useMemo, useCallback } from 'react';
import { Canvas } from '@react-three/fiber';
import { OrbitControls, Line, Html } from '@react-three/drei';
import * as THREE from 'three';
import { LengthField, PlainField } from './ui/Field';
import { niceTicks, fmtKmAxis } from './ui/chart';

const R_EARTH = 6371;

function Reff(k:number):number{ return R_EARTH / (1 - k); }

/** Pression de vapeur saturante (formule de Magnus), en hPa. */
function satVaporPressure(tempC: number): number {
  return 6.112 * Math.exp(17.67 * tempC / (tempC + 243.5));
}

/** Coefficient de réfraction k depuis les conditions atmosphériques.
 *  Formule géodésique : k ≈ 503·P_eff/T² · (0.0342 + dT/dh)
 *  avec T en Kelvin, dT/dh en °C/m. L'humidité réduit légèrement la
 *  réfractivité optique : P_eff = P − 0.13·e (e = pression de vapeur). */
function refractionK(tempC: number, gradCPerKm: number, rhPercent: number, pressureHpa = 1013): number {
  const T = tempC + 273.15;
  const e = (rhPercent / 100) * satVaporPressure(tempC);
  const pEff = pressureHpa - 0.13 * e;
  const k = 503 * pEff / (T * T) * (0.0342 + gradCPerKm / 1000);
  return Math.max(0, Math.min(0.99, k));
}

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

// ─── Graphique SVG : courbure cachée en fonction de la distance ───
function CurveGraph({ dist, oh, th, k }:{ dist:number; oh:number; th:number; k:number }) {
  const W = 720, H = 300, PADL = 64, PADR = 46, PADT = 14, PADB = 42;
  const plotW = W - PADL - PADR, plotH = H - PADT - PADB;
  const maxD = Math.max(dist * 1.3, 100);
  const steps = 120;
  const [hoverD, setHoverD] = useState<number | null>(null);

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
      p.x = PADL + (p.d / maxD) * plotW;
      p.y = PADT + plotH - (p.h / maxH) * plotH;
    }
    return { pts, maxH };
  }, [dist, oh, th, k, maxD, plotW, plotH]);

  const xOf = (d:number) => PADL + (d / maxD) * plotW;
  const yOf = (hkm:number) => PADT + plotH - (hkm / points.maxH) * plotH;

  const pathD = points.pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x.toFixed(1)},${p.y.toFixed(1)}`).join(' ');
  const curHidden = hiddenH(dist, oh / 1000, k);
  const curX = xOf(dist);
  const curY = yOf(curHidden);
  const tgtY = yOf(th / 1000);

  const xTicks = niceTicks(maxD, 6);
  const yTicks = niceTicks(points.maxH, 4);

  // Survol : distance pointée + hauteur cachée correspondante
  const onMove = (e: React.MouseEvent<SVGRectElement>) => {
    const rect = e.currentTarget.getBoundingClientRect();
    const px = (e.clientX - rect.left) / rect.width * W;
    const d = Math.max(0, Math.min(maxD, (px - PADL) / plotW * maxD));
    setHoverD(d);
  };
  const hD = hoverD;
  const hH = hD != null ? hiddenH(hD, oh / 1000, k) : 0;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 340 }}
      role="img" aria-label="Graphique de la hauteur cachée par la courbure en fonction de la distance">
      <rect x={PADL} y={PADT} width={plotW} height={plotH} fill="#050A12" rx={4} />
      {/* Grille + graduations Y */}
      {yTicks.map(t => {
        const y = yOf(t);
        return <g key={`y${t}`}>
          <line x1={PADL} y1={y} x2={PADL + plotW} y2={y} stroke="#16203a" strokeWidth={0.7} />
          <text x={PADL - 8} y={y + 3.5} fill="#7c8ca5" fontSize={11} fontFamily="monospace" textAnchor="end">{fmtKmAxis(t)}</text>
        </g>;
      })}
      {/* Graduations X */}
      {xTicks.map(t => {
        const x = xOf(t);
        return <g key={`x${t}`}>
          <line x1={x} y1={PADT} x2={x} y2={PADT + plotH} stroke="#101a30" strokeWidth={0.6} />
          <text x={x} y={PADT + plotH + 16} fill="#7c8ca5" fontSize={11} fontFamily="monospace" textAnchor="middle">{Math.round(t)}</text>
        </g>;
      })}
      {/* Ligne hauteur cible */}
      <line x1={PADL} y1={tgtY} x2={PADL + plotW} y2={tgtY} stroke="#D4A843" strokeWidth={1} strokeDasharray="5,3" opacity={0.7} />
      <text x={PADL + plotW + 4} y={tgtY + 3.5} fill="#D4A843" fontSize={10} fontFamily="monospace">cible</text>
      {/* Courbe */}
      <path d={pathD} fill="none" stroke="#00C8FF" strokeWidth={2.2} />
      {/* Point courant */}
      <line x1={curX} y1={PADT} x2={curX} y2={PADT + plotH} stroke={curHidden < th / 1000 ? '#00E87B' : '#FF4444'} strokeWidth={1} strokeDasharray="2,2" opacity={0.45} />
      <circle cx={curX} cy={curY} r={4.5} fill={curHidden < th / 1000 ? '#00E87B' : '#FF4444'} />
      {/* Survol interactif */}
      {hD != null && (
        <g pointerEvents="none">
          <line x1={xOf(hD)} y1={PADT} x2={xOf(hD)} y2={PADT + plotH} stroke="#C8D8E8" strokeWidth={0.8} opacity={0.5} />
          <circle cx={xOf(hD)} cy={yOf(hH)} r={3.5} fill="#C8D8E8" />
          <g transform={`translate(${Math.min(xOf(hD) + 8, W - 150)},${PADT + 6})`}>
            <rect width={142} height={34} rx={4} fill="#0D1528" stroke="#283750" strokeWidth={0.8} />
            <text x={8} y={14} fill="#8499b3" fontSize={10} fontFamily="monospace">{Math.round(hD)} km</text>
            <text x={8} y={28} fill="#00C8FF" fontSize={11} fontFamily="monospace" fontWeight="bold">caché : {fmt(hH)}</text>
          </g>
        </g>
      )}
      {/* Axes */}
      <line x1={PADL} y1={PADT + plotH} x2={PADL + plotW} y2={PADT + plotH} stroke="#607890" strokeWidth={1.2} />
      <line x1={PADL} y1={PADT} x2={PADL} y2={PADT + plotH} stroke="#607890" strokeWidth={1.2} />
      <text x={PADL + plotW / 2} y={H - 6} fill="#8499b3" fontSize={11} fontFamily="monospace" textAnchor="middle">Distance (km)</text>
      <text x={16} y={PADT + plotH / 2} fill="#8499b3" fontSize={11} fontFamily="monospace" textAnchor="middle" transform={`rotate(-90,16,${PADT + plotH / 2})`}>Hauteur cachée</text>
      {/* Zone de capture du survol */}
      <rect x={PADL} y={PADT} width={plotW} height={plotH} fill="transparent"
        onMouseMove={onMove} onMouseLeave={() => setHoverD(null)} style={{ cursor: 'crosshair' }} />
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
  const [tempC,setTempC]=useState(15);
  const [gradC,setGradC]=useState(-6.5);
  const [rh,setRh]=useState(50);
  const [showAtmo,setShowAtmo]=useState(false);

  const kAtm = refractionK(tempC, gradC, rh);

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

  const kPresetBtn = (label:string, val:number, tone:'neutral'|'gold'|'amber'|'red'='gold')=>{
    const active = Math.abs(k-val)<0.0005;
    const c = tone==='neutral' ? '#8499b3' : tone==='amber' ? '#D9A441' : tone==='red' ? '#E06464' : '#D4A843';
    return(
      <button key={label} onClick={()=>setK(val)}
        style={{
          padding:'6px 11px',fontSize:11,fontFamily:'monospace',borderRadius:6,
          border:`1px solid ${active?c:c+'40'}`,
          background:active?c+'1f':'transparent',color:c,
          cursor:'pointer',transition:'all 0.15s ease',whiteSpace:'nowrap',
        }}>{label}</button>
    );
  };

  return<div className="w-full">

    {/* ── ENTRÉES PRINCIPALES — champs propres ── */}
    <div className="grid grid-cols-1 md:grid-cols-3 gap-3 mb-3">
      <LengthField label="Distance" value={dist} onChange={setDist}
        canonical="km" units={['km','m','mi']} min={0} max={2000} accent="#00C8FF"
        hint="Distance horizontale entre l'observateur et la cible." />
      <LengthField label="Hauteur observateur" value={obsM} onChange={setObsM}
        canonical="m" units={['m','km','ft']} min={0} max={500000} accent="#00C8FF"
        hint="Altitude de l'œil de l'observateur au-dessus du niveau de référence." />
      <LengthField label="Hauteur cible" value={tgtM} onChange={setTgtM}
        canonical="m" units={['m','km','ft']} min={0} max={10000} accent="#00E87B"
        hint="Hauteur de l'objet visé (sommet, immeuble, navire…)." />
    </div>

    {/* ── RÉFRACTION ── */}
    <div className="bg-[#0A1020] mb-3" style={{border:'1px solid #2a2410',borderRadius:12,padding:16}}>
      <div className="grid grid-cols-1 md:grid-cols-[180px_1fr] gap-3 items-start">
        <PlainField label="Réfraction k" value={k} onChange={setK} min={0} max={0.99}
          unit="" accent="#D4A843"
          hint="Coefficient de réfraction atmosphérique. 0 = aucune ; 0.143 = standard." />
        <div className="flex flex-wrap gap-2 md:pt-1">
          {kPresetBtn('aucune (0)',0,'neutral')}
          {kPresetBtn('standard (0.143)',0.143,'gold')}
          {kPresetBtn('mer (0.17)',0.17,'gold')}
          {kPresetBtn('forte (0.38)',0.38,'amber')}
          {kPresetBtn('super (0.5)',0.5,'red')}
          <span style={{fontSize:10,fontFamily:'monospace',color:'#5a6a82',alignSelf:'center',marginLeft:4}}>
            R&apos; = {Math.round(Reff(k))} km{k>0.01?` (×${(Reff(k)/R_EARTH).toFixed(2)})`:''}
          </span>
        </div>
      </div>

      {/* Mode atmosphérique repliable */}
      <button onClick={()=>setShowAtmo(s=>!s)}
        style={{
          marginTop:14,display:'flex',alignItems:'center',gap:8,background:'transparent',
          border:'none',cursor:'pointer',color:'#D4A843',fontSize:11,fontFamily:'monospace',
          letterSpacing:'0.08em',padding:0,
        }}>
        <span style={{transform:showAtmo?'rotate(90deg)':'none',transition:'transform 0.15s',display:'inline-block'}}>▸</span>
        CALCULER k DEPUIS L&apos;ATMOSPHÈRE
      </button>

      {showAtmo && (
        <div style={{marginTop:12,paddingTop:14,borderTop:'1px solid #2a2410'}}>
          <div style={{fontSize:10,fontFamily:'monospace',color:'#9a8240',letterSpacing:'0.06em',marginBottom:12}}>
            k = 503·P_eff/T² · (0.0342 + ΔT/Δh)
          </div>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
            <PlainField label="Température" value={tempC} onChange={setTempC} min={-40} max={60} unit="°C" accent="#D4A843" compact
              hint="Température de l'air au niveau de l'observateur." />
            <PlainField label="Gradient ΔT/Δh" value={gradC} onChange={setGradC} min={-15} max={20} unit="°C/km" accent="#D4A843" compact
              hint="Variation de température avec l'altitude. Négatif = l'air se refroidit en montant (normal)." />
            <PlainField label="Humidité" value={rh} onChange={setRh} min={0} max={100} unit="%" accent="#00C8FF" compact
              hint="Humidité relative. Effet optique faible (−0.13·e sur la pression effective)." />
          </div>
          <div className="flex flex-wrap items-center gap-3 mt-3">
            <span style={{fontSize:11,fontFamily:'monospace',color:'#C8D8E8'}}>
              k atmosphérique = <span style={{color:'#D4A843',fontWeight:700}}>{kAtm.toFixed(3)}</span>
            </span>
            <button onClick={()=>setK(Math.round(kAtm*1000)/1000)}
              style={{padding:'7px 14px',fontSize:10,fontFamily:'monospace',borderRadius:6,border:'1px solid #D4A84399',background:'#D4A8431a',color:'#D4A843',cursor:'pointer'}}>
              → APPLIQUER CE k
            </button>
            <button onClick={()=>{setTempC(15);setGradC(-6.5);setRh(50);}}
              style={{padding:'7px 12px',fontSize:10,fontFamily:'monospace',borderRadius:6,border:'1px solid #46566e',background:'transparent',color:'#8499b3',cursor:'pointer'}}>
              Standard
            </button>
            <button onClick={()=>{setTempC(8);setGradC(5);setRh(85);}}
              style={{padding:'7px 12px',fontSize:10,fontFamily:'monospace',borderRadius:6,border:'1px solid #9a824055',background:'transparent',color:'#D9A441',cursor:'pointer'}}>
              Inversion sur mer froide
            </button>
          </div>
        </div>
      )}
    </div>

    {/* ── CAS RÉELS ── */}
    <div className="mb-5">
      <div className="text-[11px] font-tech-mono text-slate-500 mb-3" style={{letterSpacing:'0.08em'}}>CAS RÉELS DOCUMENTÉS</div>
      <div className="grid grid-cols-1 sm:grid-cols-2 md:grid-cols-3 gap-2">
        {PRESETS.map(p=>{
          const fmtH = (m:number) => m>=1000 ? `${(m/1000).toFixed(1)} km` : `${m} m`;
          return (
            <button key={p.label} onClick={()=>{setDist(p.d);setObsM(p.oh);setTgtM(p.th);setK(p.k);}}
              className="text-left group" style={{border:'1px solid #283750',background:'#0A1020',borderRadius:8,padding:12,transition:'border-color 0.15s'}}
              onMouseEnter={e=>e.currentTarget.style.borderColor='#00C8FF80'}
              onMouseLeave={e=>e.currentTarget.style.borderColor='#283750'}
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
    <div className="mb-4 bg-[#0A1020] p-4" style={{border:'1px solid #1c2942',borderRadius:12}}>
      <div className="text-[11px] font-tech-mono text-slate-400 tracking-widest mb-3">HAUTEUR CACHÉE EN FONCTION DE LA DISTANCE</div>
      <CurveGraph dist={dist} oh={obsM} th={tgtM} k={k} />
      <div className="flex items-center flex-wrap gap-4 mt-2">
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
    <div className="w-full h-[40vh] sm:h-[55vh] md:h-[70vh] bg-[#030810] relative overflow-hidden" style={{border:'1px solid #1c2942',borderRadius:12}}>
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
      <div className="bg-[#0A1020] p-4" style={{border:'1px solid #14333f',borderRadius:10}}>
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">HORIZON</div>
        <div className="text-[20px] font-tech-mono text-cyan-400 font-bold">{hDist.toFixed(1)} km</div>
        {k>0.01&&<div className="text-[10px] font-tech-mono text-slate-600 mt-1">sans réf: {hDistNoRef.toFixed(1)} km</div>}
      </div>
      <div className="bg-[#0A1020] p-4" style={{border:'1px solid #3a1414',borderRadius:10}}>
        <div className="text-[11px] font-tech-mono text-red-400/70 tracking-widest mb-2">CHUTE COURBURE</div>
        <div className="text-[20px] font-tech-mono text-red-400 font-bold">{fmt(drop)}</div>
        {k>0.01&&<div className="text-[10px] font-tech-mono text-slate-600 mt-1">sans réf: {fmt(dropNoRef)}</div>}
      </div>
      <div className="bg-[#0A1020] p-4" style={{border:'1px solid #3a2e14',borderRadius:10}}>
        <div className="text-[11px] font-tech-mono text-amber-400/70 tracking-widest mb-2">HAUTEUR CACHÉE</div>
        <div className="text-[20px] font-tech-mono text-amber-400 font-bold">{fmt(hidden)}</div>
        {k>0.01&&<div className="text-[10px] font-tech-mono text-slate-600 mt-1">sans réf: {fmt(hiddenNoRef)}</div>}
      </div>
      <div className="p-4" style={{borderRadius:10,border:`1px solid ${vis?'#14401f':'#401414'}`,background:vis?'#0a1f12':'#1f0a0a'}}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">AVEC RÉFRACTION</div>
        <div className={`text-[18px] font-tech-mono font-bold ${vis?'text-green-400':'text-red-400'}`}>{vis?'✓ VISIBLE':'✗ MASQUÉE'}</div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          {vis?`${fmt(th-hidden)} visible sur ${fmt(th)}`:`${fmt(hidden)} caché > ${fmt(th)}`}
        </div>
      </div>
      <div className="p-4" style={{borderRadius:10,border:`1px solid ${visNoRef?'#14401f':'#401414'}`,background:visNoRef?'#0a1f12':'#1f0a0a'}}>
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
        className="px-5 py-2.5 text-[11px] font-tech-mono tracking-widest transition-all"
        style={{
          borderRadius:8,
          border: `1px solid ${copied ? '#00E87B99' : '#00C8FF40'}`,
          backgroundColor: copied ? '#00E87B1a' : '#00C8FF0a',
          color: copied ? '#00E87B' : '#00C8FF',
        }}>
        {copied ? '✓ COPIÉ' : '⎘ COPIER LES RÉSULTATS'}
      </button>
    </div>

    <div className="mt-4 bg-[#0A1020] p-4" style={{border:'1px solid #2a2410',borderRadius:10}}>
      <div className="text-[11px] font-tech-mono text-[#D4A843]/60 mb-2">À PROPOS DE LA RÉFRACTION</div>
      <p className="text-[12px] text-[#C8D8E8]/80 font-rajdhani leading-relaxed">
        La réfraction atmosphérique courbe les rayons lumineux vers le sol (l&apos;air dense au sol a un indice plus élevé).
        L&apos;effet est modélisé par un rayon terrestre effectif R&apos; = R/(1−k).
        En conditions standard (k≈0.143), l&apos;horizon recule de ~8%.
        Sur mer froide (k≈0.17-0.38), la réfraction est plus forte.
        En super-réfraction (k&gt;0.4, Fata Morgana), des objets à des centaines de km deviennent visibles.
        Quand k≥1, la lumière suit la courbure terrestre : la Terre paraît plate.
      </p>
    </div>

    <div className="mt-4 pt-4 flex flex-wrap items-center gap-5" style={{borderTop:'1px solid #1c2942'}}>
      <span className="text-[11px] font-tech-mono text-slate-400">ARTICLES :</span>
      <a href="/article/leau-ne-ment-pas" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;eau ne ment pas →</a>
      <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;hypothèse nulle →</a>
      <a href="/article/loeil-humain-la-machine-a-voir-qui-faconne-notre-realite" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;œil humain →</a>
    </div>
  </div>;
}
