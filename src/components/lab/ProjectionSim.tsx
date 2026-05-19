'use client';
import { useState, useMemo, useRef, useEffect } from 'react';

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

// Mercator
function mercProj(lat:number,lng:number,w:number,h:number):[number,number]{
  const x=((lng+180)/360)*w;
  const lr=toRad(Math.max(-85,Math.min(85,lat)));
  const y=h/2-(Math.log(Math.tan(Math.PI/4+lr/2))*w)/(2*Math.PI);
  return [x,Math.max(0,Math.min(h,y))];
}

// Azimutale equidistante (pôle Nord)
function aeProj(lat:number,lng:number,w:number,h:number):[number,number]{
  const lr=toRad(lng), r=((90-lat)/180), cx=w/2, cy=h/2, mr=Math.min(w,h)*0.45;
  return [cx+Math.sin(lr)*r*mr, cy-Math.cos(lr)*r*mr];
}

function proj(t:Proj,lat:number,lng:number,w:number,h:number):[number,number]{
  return t==='mercator'?mercProj(lat,lng,w,h):aeProj(lat,lng,w,h);
}

// Great circle pour Mercator, LIGNE DROITE pour AE
function interpolate(from:GeoPoint,to:GeoPoint,type:Proj,segs=60):GeoPoint[]{
  if(type==='azimuthal'){
    // Lignes droites sur AE — pas d'interpolation great circle
    return [from, to];
  }
  // Great circle pour Mercator
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

function MapView({projection,routes,showRoutes,width,height}:{
  projection:Proj; routes:Route[]; showRoutes:boolean; width:number; height:number;
}){
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const imgRef = useRef<HTMLImageElement|null>(null);
  const [imgLoaded, setImgLoaded] = useState(false);

  const texSrc = projection==='mercator'?'/textures/mercator-map.jpg':'/textures/ae-map.jpg';

  useEffect(()=>{
    const img = new Image();
    img.crossOrigin = 'anonymous';
    img.onload = ()=>{ imgRef.current = img; setImgLoaded(true); };
    img.src = texSrc;
  },[texSrc]);

  useEffect(()=>{
    const cv = canvasRef.current;
    const img = imgRef.current;
    if(!cv||!img||!imgLoaded) return;
    const ctx = cv.getContext('2d');
    if(!ctx) return;

    ctx.clearRect(0,0,width,height);
    ctx.drawImage(img, 0, 0, width, height);

    // Routes
    if(showRoutes){
      routes.forEach(route=>{
        const pts = interpolate(route.from, route.to, projection);
        // Dessiner
        ctx.strokeStyle = route.color;
        ctx.lineWidth = 2.5;
        ctx.setLineDash([]);
        ctx.beginPath();
        let prevX = 0;
        let started = false;
        pts.forEach(pt=>{
          const [x,y] = proj(projection, pt.lat, pt.lng, width, height);
          if(!started){ctx.moveTo(x,y);started=true;prevX=x;return;}
          if(Math.abs(x-prevX)>width*0.4){ctx.moveTo(x,y);}
          else{ctx.lineTo(x,y);}
          prevX=x;
        });
        ctx.stroke();

        // Points de départ/arrivée
        const [fx,fy]=proj(projection, route.from.lat, route.from.lng, width, height);
        const [tx,ty]=proj(projection, route.to.lat, route.to.lng, width, height);

        [
          {x:fx,y:fy,l:route.from.label},
          {x:tx,y:ty,l:route.to.label},
        ].forEach(({x,y,l})=>{
          ctx.fillStyle=route.color;
          ctx.beginPath();ctx.arc(x,y,5,0,Math.PI*2);ctx.fill();
          ctx.beginPath();ctx.arc(x,y,10,0,Math.PI*2);
          ctx.fillStyle=route.color+'30';ctx.fill();
          ctx.fillStyle=route.color;
          ctx.font='11px monospace';
          ctx.fillText(l, x+12, y+4);
        });
      });
    }

    // Label projection
    ctx.fillStyle='rgba(200,216,232,0.4)';
    ctx.font='12px monospace';
    ctx.fillText(projection==='mercator'?'MERCATOR':'AZIMUTALE ÉQUIDISTANTE', 12, 22);
  },[projection,routes,showRoutes,width,height,imgLoaded]);

  return <canvas ref={canvasRef} width={width} height={height}
    className="w-full h-auto" style={{imageRendering:'auto'}} />;
}

export default function ProjectionSim(){
  const [projection,setProjection]=useState<Proj>('mercator');
  const [showRoutes,setShowRoutes]=useState(true);
  const [selected,setSelected]=useState<Set<number>>(new Set([0,1,2,3]));
  const activeRoutes = ROUTES.filter((_,i)=>selected.has(i));
  const toggle=(i:number)=>{setSelected(p=>{const n=new Set(p);n.has(i)?n.delete(i):n.add(i);return n;});};
  const W=900, H=projection==='azimuthal'?900:600;

  return <div className="w-full">
    <div className="flex flex-wrap items-center gap-2 mb-4">
      {(['mercator','azimuthal'] as const).map(p=>(
        <button key={p} onClick={()=>setProjection(p)}
          className={`px-4 py-2 text-[9px] font-orbitron tracking-widest border transition-all ${projection===p?'border-[#00C8FF]/60 bg-[#00C8FF]/10 text-[#00C8FF]':'border-slate-700 text-slate-500 hover:border-slate-500'}`}
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
    <div className="w-full border border-slate-800/50 relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10"/>
      <MapView projection={projection} routes={activeRoutes} showRoutes={showRoutes} width={W} height={H} />
    </div>
    <div className="mt-4 border border-slate-800/50 bg-[#0A1020] p-4">
      <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
        {projection==='mercator'
          ?"Mercator (1569) conserve les angles mais déforme les aires. Le Groenland paraît aussi grand que l\u2019Afrique (×14 en réalité). Les routes great-circle apparaissent courbes."
          :"L\u2019azimutale équidistante, centrée sur le pôle Nord, préserve les distances depuis le centre. Les routes aériennes y apparaissent en lignes droites — ce qui correspond au plus court chemin sur cette projection."}
      </p>
      <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLE :</span>
        <a href="/article/cartes-routes-boussoles-et-le-mystere-antarctique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF]">Cartes, routes, boussoles →</a>
      </div>
    </div>
  </div>;
}
