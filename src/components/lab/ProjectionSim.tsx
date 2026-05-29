'use client';
import { useState, useRef, useEffect, useCallback } from 'react';

type Proj = 'mercator' | 'azimuthal';
interface GeoPoint { lat:number; lng:number; label:string; }
interface Route { from:GeoPoint; to:GeoPoint; label:string; color:string; }

const ROUTES: Route[] = [
  { from:{lat:-33.87,lng:151.21,label:'Sydney'}, to:{lat:-33.45,lng:-70.67,label:'Santiago'}, label:'Sydney → Santiago', color:'#00C8FF' },
  { from:{lat:-26.20,lng:28.04,label:'Johannesburg'}, to:{lat:-31.95,lng:115.86,label:'Perth'}, label:'Johannesburg → Perth', color:'#00E87B' },
  { from:{lat:-34.60,lng:-58.38,label:'Buenos Aires'}, to:{lat:-36.85,lng:174.76,label:'Auckland'}, label:'Buenos Aires → Auckland', color:'#D4A843' },
  { from:{lat:51.47,lng:-0.46,label:'Londres'}, to:{lat:35.68,lng:139.69,label:'Tokyo'}, label:'Londres → Tokyo', color:'#FF6B6B' },
];

function toRad(d:number){return d*Math.PI/180;}

// AE offset calibré sur l'image satellite
const AE_OFFSET = 128;

function mercProj(lat:number,lng:number,w:number,h:number):[number,number]{
  const x=((lng+180)/360)*w;
  const lr=toRad(Math.max(-85,Math.min(85,lat)));
  const y=h/2-(Math.log(Math.tan(Math.PI/4+lr/2))*w)/(2*Math.PI);
  return [x,Math.max(0,Math.min(h,y))];
}

function aeProj(lat:number,lng:number,w:number,h:number):[number,number]{
  const r=((90-lat)/180);
  const angle=toRad(lng + AE_OFFSET);
  const cx=w/2, cy=h/2;
  const maxR=Math.min(w,h)*0.498;
  return [cx+Math.sin(angle)*r*maxR, cy-Math.cos(angle)*r*maxR];
}

function proj(t:Proj,lat:number,lng:number,w:number,h:number):[number,number]{
  return t==='mercator'?mercProj(lat,lng,w,h):aeProj(lat,lng,w,h);
}

function greatCircle(from:GeoPoint,to:GeoPoint,segs=60):GeoPoint[]{
  const lat1=toRad(from.lat),lng1=toRad(from.lng),lat2=toRad(to.lat),lng2=toRad(to.lng);
  const d=2*Math.asin(Math.sqrt(Math.sin((lat2-lat1)/2)**2+Math.cos(lat1)*Math.cos(lat2)*Math.sin((lng2-lng1)/2)**2));
  if(d<0.0001)return[from,to];
  const pts:GeoPoint[]=[];
  for(let i=0;i<=segs;i++){
    const f=i/segs;
    const A=Math.sin((1-f)*d)/Math.sin(d), B=Math.sin(f*d)/Math.sin(d);
    const x=A*Math.cos(lat1)*Math.cos(lng1)+B*Math.cos(lat2)*Math.cos(lng2);
    const y=A*Math.cos(lat1)*Math.sin(lng1)+B*Math.cos(lat2)*Math.sin(lng2);
    const z=A*Math.sin(lat1)+B*Math.sin(lat2);
    pts.push({lat:Math.atan2(z,Math.sqrt(x*x+y*y))*180/Math.PI, lng:Math.atan2(y,x)*180/Math.PI, label:''});
  }
  return pts;
}

export default function ProjectionSim(){
  const [projection,setProjection]=useState<Proj>('mercator');
  const [showRoutes,setShowRoutes]=useState(true);
  const [selected,setSelected]=useState<Set<number>>(new Set([0,1,2,3]));
  const canvasRef=useRef<HTMLCanvasElement>(null);
  const [imgCache,setImgCache]=useState<Record<string,HTMLImageElement>>({});
  const activeRoutes=ROUTES.filter((_,i)=>selected.has(i));
  const toggle=(i:number)=>{setSelected(p=>{const n=new Set(p);n.has(i)?n.delete(i):n.add(i);return n;});};
  const W=1200,H=projection==='azimuthal'?1200:750;

  useEffect(()=>{
    const imgs:Record<string,HTMLImageElement>={};
    let loaded=0;
    const check=()=>{loaded++;if(loaded===2)setImgCache({...imgs});};
    const m=new Image();m.crossOrigin='anonymous';m.onload=()=>{imgs['mercator']=m;check();};m.src='/textures/mercator-map.jpg';
    const a=new Image();a.crossOrigin='anonymous';a.onload=()=>{imgs['azimuthal']=a;check();};a.src='/textures/ae-map-routes.jpg';
  },[]);

  const draw=useCallback(()=>{
    const cv=canvasRef.current;const img=imgCache[projection];
    if(!cv||!img)return;
    cv.width=W;cv.height=H;
    const ctx=cv.getContext('2d');if(!ctx)return;
    ctx.fillStyle='#050A12';ctx.fillRect(0,0,W,H);
    ctx.drawImage(img,0,0,W,H);
    if(!showRoutes || projection==='azimuthal') return;

    activeRoutes.forEach(route=>{
      const pts=greatCircle(route.from,route.to);
      ctx.strokeStyle=route.color;ctx.lineWidth=3;ctx.lineJoin='round';ctx.lineCap='round';ctx.setLineDash([]);
      ctx.beginPath();let started=false;let prevX=0;
      pts.forEach(pt=>{
        const [x,y]=mercProj(pt.lat,pt.lng,W,H);
        if(!started){ctx.moveTo(x,y);started=true;prevX=x;return;}
        if(Math.abs(x-prevX)>W*0.4){ctx.moveTo(x,y);}else{ctx.lineTo(x,y);}
        prevX=x;
      });
      ctx.stroke();

      const [fx,fy]=mercProj(route.from.lat,route.from.lng,W,H);
      const [tx,ty]=mercProj(route.to.lat,route.to.lng,W,H);
      [{x:fx,y:fy,l:route.from.label},{x:tx,y:ty,l:route.to.label}].forEach(({x,y,l})=>{
        ctx.fillStyle=route.color;ctx.beginPath();ctx.arc(x,y,6,0,Math.PI*2);ctx.fill();
        ctx.globalAlpha=0.2;ctx.beginPath();ctx.arc(x,y,12,0,Math.PI*2);ctx.fill();ctx.globalAlpha=1;
        ctx.font='bold 13px monospace';ctx.fillText(l,x+14,y+5);
      });
    });
    ctx.fillStyle='rgba(200,216,232,0.4)';ctx.font='14px monospace';
    ctx.fillText(projection==='mercator'?'MERCATOR':'AZIMUTALE ÉQUIDISTANTE',14,26);
  },[projection,activeRoutes,showRoutes,imgCache,W,H]);

  useEffect(()=>{draw();},[draw]);

  return <div className="w-full">
    <div className="flex flex-wrap items-center gap-2 mb-4">
      {(['mercator','azimuthal'] as const).map(p=>(
        <button key={p} onClick={()=>setProjection(p)}
          className={`px-4 py-2 text-[9px] font-orbitron tracking-widest border transition-all ${projection===p?'border-[var(--cyan-50)] bg-[var(--cyan-08)] text-[var(--cyan)]':'border-slate-700 text-slate-500 hover:border-slate-500'}`}
          style={{clipPath:'polygon(6px 0,100% 0,calc(100% - 6px) 100%,0 100%)'}}
        >{p==='mercator'?'MERCATOR':'AZIMUTALE ÉQ.'}</button>
      ))}
      <button onClick={()=>setShowRoutes(!showRoutes)}
        className={`ml-auto px-3 py-1 text-[8px] font-tech-mono border ${showRoutes?'border-slate-600 text-slate-400':'border-slate-800 text-slate-600'}`}
      >ROUTES: {showRoutes?'ON':'OFF'}</button>
    </div>
    {showRoutes&&<div className="flex flex-wrap gap-2 mb-4">
      {ROUTES.map((r,i)=>(
        <button key={i} onClick={()=>toggle(i)}
          className={`px-3 py-1 text-[8px] font-tech-mono border transition-all ${selected.has(i)?'':'border-slate-800 text-slate-600 opacity-40'}`}
          style={{borderColor:selected.has(i)?r.color:undefined,color:selected.has(i)?r.color:undefined,backgroundColor:selected.has(i)?r.color+'15':undefined}}
        >{r.label}</button>
      ))}
    </div>}
    <div className="w-full border border-slate-800/50 relative overflow-hidden bg-[var(--void)]">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[var(--cyan-20)] z-10"/>
      <canvas ref={canvasRef} width={W} height={H} className="w-full h-auto"/>
    </div>
    <div className="mt-4 border border-slate-800/50 bg-[var(--hull)] p-4">
      <p className="text-[13px] text-[var(--text-60)] font-rajdhani leading-relaxed">
        {projection==='mercator'
          ?"Mercator (1569) conserve les angles mais déforme les aires. Les routes great-circle apparaissent courbes."
          :"L\u2019azimutale équidistante préserve les distances depuis le pôle Nord. Les lignes droites sur cette carte représentent le plus court chemin."}
      </p>
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLE :</span>
        <a href="/article/cartes-routes-boussoles-et-le-mystere-antarctique" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">Cartes, routes, boussoles →</a>
      </div>
    </div>
  </div>;
}
