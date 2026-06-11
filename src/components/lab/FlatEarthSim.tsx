'use client';
import React, { useRef, useState, useMemo, useEffect, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Line } from '@react-three/drei';
import * as THREE from 'three';
import { getAllPositions, latLngToFlatDisc, moonPhaseName, DEFAULT_OBSERVER, type CelestialPosition } from './celestialCalc';

const SUN_C = '#FFD040';
const MOON_C = '#C8C8D0';
const DISC_R = 6;

type PosData = ReturnType<typeof getAllPositions>;

function altText(p: CelestialPosition): string {
  if (p.altitude === undefined) return '';
  const arrow = p.altitude >= 0 ? '▲' : '▼';
  return ` ${arrow}${Math.abs(p.altitude).toFixed(0)}°`;
}

function Label({ text, color='#C8D8E8', show=true }:{ text:string; color?:string; show?:boolean }) {
  if(!show) return null;
  return <Html center distanceFactor={10} style={{pointerEvents:'none'}}>
    <div style={{color,fontSize:'10px',fontFamily:'monospace',textShadow:'0 0 6px rgba(0,0,0,0.9)',whiteSpace:'nowrap',fontWeight:'bold'}}>{text}</div>
  </Html>;
}

function EarthDisc({ sunLatLng }:{ sunLatLng:[number,number] }) {
  const meshRef = useRef<THREE.Mesh>(null);
  const mapTex = useMemo(()=>new THREE.TextureLoader().load('/textures/ae-map.jpg'),[]);

  // Terminateur réaliste : pour chaque fragment, on retrouve (lat, lng) depuis la
  // projection azimutale, puis on calcule le cosinus de l'angle zénithal solaire :
  // cos(Z) = sin(φ)·sin(φ☉) + cos(φ)·cos(φ☉)·cos(λ − λ☉).
  // cos(Z) = sin(altitude solaire) → on en déduit les 3 zones crépusculaires :
  // civile (−6°), nautique (−12°), astronomique (−18°), avec teinte orangée
  // dans la bande civile (diffusion de Rayleigh aux incidences rasantes).
  const shader = useMemo(()=>({
    uniforms: {
      uMap: { value: mapTex },
      uSunLat: { value: sunLatLng[0] * Math.PI / 180 },
      uSunLng: { value: sunLatLng[1] * Math.PI / 180 },
      uDiscR: { value: DISC_R },
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
      uniform float uSunLat;
      uniform float uSunLng;
      uniform float uDiscR;
      varying vec2 vUv;
      varying vec3 vPos;
      const float PI = 3.14159265358979;
      const float AE_OFFSET = 128.0;
      void main(){
        vec4 texColor = texture2D(uMap, vUv);
        // Projection azimutale inverse : position locale → (lat, lng)
        float r = length(vPos.xy);
        float lat = (90.0 - (r / uDiscR) * 180.0) * PI / 180.0;
        // géométrie locale (x,y) → monde (x,-y) après rotation -90° sur X ;
        // latLngToFlatDisc : x=sin(a)·r, z=-cos(a)·r avec a=(-lng+offset)
        float a = atan(vPos.x, vPos.y);
        float lng = (AE_OFFSET - a * 180.0 / PI) * PI / 180.0;
        // sin(altitude solaire) = cos(angle zénithal)
        float sinAlt = sin(lat) * sin(uSunLat) + cos(lat) * cos(uSunLat) * cos(lng - uSunLng);
        // Zones crépusculaires : sin(-6°)=-0.1045, sin(-12°)=-0.2079, sin(-18°)=-0.3090
        float day   = smoothstep(0.0, 0.06, sinAlt);
        float civil = smoothstep(-0.1045, 0.0, sinAlt);
        float naut  = smoothstep(-0.2079, -0.1045, sinAlt);
        float astro = smoothstep(-0.3090, -0.2079, sinAlt);
        float brightness = 0.05 + 0.05*astro + 0.08*naut + 0.22*civil + 0.60*day;
        // Teinte orangée dans la bande crépusculaire civile
        float band = civil * (1.0 - day);
        vec3 tint = mix(vec3(1.0), vec3(1.0, 0.58, 0.32), band * 0.65);
        gl_FragColor = vec4(texColor.rgb * brightness * tint, texColor.a);
      }
    `,
  // uniforms mis à jour impérativement dans le useEffect ci-dessous
  // eslint-disable-next-line react-hooks/exhaustive-deps
  }),[mapTex]);

  useEffect(()=>{
    if(meshRef.current){
      const mat = meshRef.current.material as THREE.ShaderMaterial;
      if(mat.uniforms){
        mat.uniforms.uSunLat.value = sunLatLng[0] * Math.PI / 180;
        mat.uniforms.uSunLng.value = sunLatLng[1] * Math.PI / 180;
      }
    }
  },[sunLatLng]);

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

function FlatScene({ speed, showLabels, isPlaying, showTropics, dateRef, onPosUpdate }:{
  speed:number; showLabels:boolean; isPlaying:boolean; showTropics:boolean;
  dateRef: React.MutableRefObject<Date>;
  onPosUpdate:(d:Date, p:PosData)=>void;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group|null)[]>([]);
  const lastMs = useRef(0);
  const frameCount = useRef(0);
  const [posData, setPosData] = useState<PosData>(() => getAllPositions(dateRef.current, DEFAULT_OBSERVER));
  const [sunLatLng, setSunLatLng] = useState<[number,number]>([posData.sun.lat, posData.sun.lng]);

  const SUN_H = 0.3;
  const MOON_H = 0.25;

  useFrame(()=>{
    if (isPlaying) {
      // 1 s réel = 30 min simulées × vitesse
      const dtMs = 0.016 * speed * 30 * 60 * 1000;
      dateRef.current = new Date(dateRef.current.getTime() + dtMs);
    }
    const ms = dateRef.current.getTime();
    frameCount.current++;
    // Recalcul si la date a changé (lecture OU saut manuel pendant la pause)
    if (ms === lastMs.current) return;
    lastMs.current = ms;

    const pos = getAllPositions(dateRef.current, DEFAULT_OBSERVER);

    const [sx,sz] = latLngToFlatDisc(pos.sun.lat, pos.sun.lng, DISC_R);
    if(sunRef.current) sunRef.current.position.set(sx, SUN_H, sz);
    setSunLatLng([pos.sun.lat, pos.sun.lng]);

    const [mx,mz] = latLngToFlatDisc(pos.moon.lat, pos.moon.lng, DISC_R);
    if(moonRef.current) moonRef.current.position.set(mx, MOON_H, mz);

    pos.planets.forEach((p,i)=>{
      const ref = planetRefs.current[i];
      if(!ref) return;
      const [px,pz] = latLngToFlatDisc(p.lat, p.lng, DISC_R);
      ref.position.set(px, 0.2, pz);
    });

    if (!isPlaying || frameCount.current % 20 === 0) {
      setPosData(pos);
      onPosUpdate(dateRef.current, pos);
    }
  });

  const initPos = useMemo(()=>{
    const p = getAllPositions(dateRef.current, DEFAULT_OBSERVER);
    return {
      sun: latLngToFlatDisc(p.sun.lat, p.sun.lng, DISC_R),
      moon: latLngToFlatDisc(p.moon.lat, p.moon.lng, DISC_R),
      planets: p.planets.map(pl => latLngToFlatDisc(pl.lat, pl.lng, DISC_R)),
    };
  // position initiale uniquement
  // eslint-disable-next-line react-hooks/exhaustive-deps
  },[]);

  return (
    <group>
      <ambientLight intensity={0.1} />
      <EarthDisc sunLatLng={sunLatLng} />
      {showTropics && <TropicCircles />}

      <group ref={sunRef} position={[initPos.sun[0],SUN_H,initPos.sun[1]]}>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.22,32]} />
          <meshBasicMaterial color={SUN_C} side={THREE.DoubleSide} />
        </mesh>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.45,32]} />
          <meshBasicMaterial color={SUN_C} transparent opacity={0.15} side={THREE.DoubleSide} />
        </mesh>
        <Label text={`Soleil ☉${altText(posData.sun)}`} color={SUN_C} show={showLabels} />
      </group>

      <group ref={moonRef} position={[initPos.moon[0],MOON_H,initPos.moon[1]]}>
        <mesh rotation={[-Math.PI/2,0,0]}>
          <circleGeometry args={[0.1,24]} />
          <meshBasicMaterial color={MOON_C} side={THREE.DoubleSide} />
        </mesh>
        <Label text={`Lune ☾${altText(posData.moon)}`} color={MOON_C} show={showLabels} />
      </group>

      {posData.planets.map((p,i)=>(
        <group key={p.name} ref={el=>{planetRefs.current[i]=el;}}
          position={[initPos.planets[i]?.[0] ?? 0, 0.2, initPos.planets[i]?.[1] ?? 0]}>
          <mesh rotation={[-Math.PI/2,0,0]}>
            <circleGeometry args={[p.size*0.6,16]} />
            <meshBasicMaterial color={p.color} side={THREE.DoubleSide} />
          </mesh>
          <Label text={`${p.name}${altText(p)}`} color={p.color} show={showLabels} />
        </group>
      ))}
    </group>
  );
}

/**
 * Icône SVG de phase lunaire : disque sombre + région éclairée délimitée par
 * un demi-cercle (limbe) et une demi-ellipse (terminateur, rx = r·|cos φ|).
 * phase : 0 = nouvelle lune, 90 = premier quartier, 180 = pleine, 270 = dernier quartier.
 */
function MoonPhaseIcon({ phase, size=34 }:{ phase:number; size?:number }) {
  const r = size/2 - 2;
  const cx = size/2, cy = size/2;
  const a = ((phase % 360) + 360) % 360;
  const c = Math.cos(a * Math.PI / 180);
  const rx = Math.abs(c) * r;
  const waxing = a < 180; // croissante → côté droit éclairé (vue hémisphère nord)
  const litPath = waxing
    ? `M ${cx} ${cy-r} A ${r} ${r} 0 0 1 ${cx} ${cy+r} A ${rx} ${r} 0 0 ${c > 0 ? 0 : 1} ${cx} ${cy-r} Z`
    : `M ${cx} ${cy-r} A ${r} ${r} 0 0 0 ${cx} ${cy+r} A ${rx} ${r} 0 0 ${c > 0 ? 1 : 0} ${cx} ${cy-r} Z`;
  return (
    <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
      <circle cx={cx} cy={cy} r={r} fill="#1A2030" stroke="#3A4458" strokeWidth="1" />
      <path d={litPath} fill="#E8E8F0" />
    </svg>
  );
}

function DateStepper({ label, value, onStep }:{ label:string; value:string; onStep:(delta:number)=>void }) {
  return (
    <div className="flex flex-col items-center gap-0.5">
      <span className="text-[7px] font-tech-mono text-slate-600 tracking-widest">{label}</span>
      <div className="flex items-center border border-slate-800 bg-[#060A14]">
        <button onClick={()=>onStep(-1)} className="px-1.5 py-1 text-[10px] font-tech-mono text-slate-500 hover:text-[var(--cyan)] hover:bg-[var(--cyan)]/10">−</button>
        <span className="px-1 text-[10px] font-tech-mono text-[var(--cyan)] min-w-[34px] text-center">{value}</span>
        <button onClick={()=>onStep(1)} className="px-1.5 py-1 text-[10px] font-tech-mono text-slate-500 hover:text-[var(--cyan)] hover:bg-[var(--cyan)]/10">+</button>
      </div>
    </div>
  );
}

const MONTHS_FR = ['JAN','FÉV','MAR','AVR','MAI','JUI','JUL','AOÛ','SEP','OCT','NOV','DÉC'];

export default function FlatEarthSim(){
  const [speed,setSpeed]=useState(1);
  const [showLabels,setShowLabels]=useState(true);
  const [isPlaying,setIsPlaying]=useState(true);
  const [showTropics,setShowTropics]=useState(false);
  const dateRef = useRef(new Date());
  const [simDate,setSimDate]=useState(()=>dateRef.current);
  const [posData,setPosData]=useState<PosData|null>(null);

  const onPosUpdate = useCallback((d:Date, p:PosData)=>{
    setSimDate(new Date(d));
    setPosData(p);
  },[]);

  const adjustDate = useCallback((unit:'year'|'month'|'day'|'hour'|'minute', delta:number)=>{
    const d = new Date(dateRef.current);
    if(unit==='year') d.setFullYear(d.getFullYear()+delta);
    else if(unit==='month') d.setMonth(d.getMonth()+delta);
    else if(unit==='day') d.setDate(d.getDate()+delta);
    else if(unit==='hour') d.setHours(d.getHours()+delta);
    else d.setMinutes(d.getMinutes()+delta*10);
    dateRef.current = d;
    setSimDate(d);
  },[]);

  const resetNow = useCallback(()=>{
    dateRef.current = new Date();
    setSimDate(dateRef.current);
  },[]);

  const seasonName = useMemo(() => {
    const m = simDate.getMonth();
    if (m >= 2 && m <= 4) return 'Printemps';
    if (m >= 5 && m <= 7) return 'Été';
    if (m >= 8 && m <= 10) return 'Automne';
    return 'Hiver';
  }, [simDate]);

  return <div className="w-full">
    <div className="flex flex-wrap items-center gap-2 mb-2">
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

    {/* Contrôles date/heure */}
    <div className="flex flex-wrap items-end gap-2 mb-3 p-2 border border-slate-800/50 bg-[var(--hull)]">
      <DateStepper label="JOUR" value={simDate.getDate().toString().padStart(2,'0')} onStep={d=>adjustDate('day',d)} />
      <DateStepper label="MOIS" value={MONTHS_FR[simDate.getMonth()]} onStep={d=>adjustDate('month',d)} />
      <DateStepper label="ANNÉE" value={simDate.getFullYear().toString()} onStep={d=>adjustDate('year',d)} />
      <div className="w-px h-8 bg-slate-800 mx-1 hidden md:block" />
      <DateStepper label="HEURE" value={simDate.getHours().toString().padStart(2,'0')+'h'} onStep={d=>adjustDate('hour',d)} />
      <DateStepper label="MIN ±10" value={simDate.getMinutes().toString().padStart(2,'0')} onStep={d=>adjustDate('minute',d)} />
      <button onClick={resetNow}
        className="ml-auto px-3 py-1.5 text-[8px] font-tech-mono tracking-widest border border-[var(--green)]/50 text-[var(--green)] hover:bg-[var(--green)]/10"
      >● MAINTENANT</button>
    </div>

    <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#020408] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-3 left-3 z-10">
        <div className="text-[9px] font-tech-mono text-[var(--green)] tracking-widest">◉ TERRE PLANE — VUE DU DESSUS</div>
        <div className="text-[8px] font-tech-mono text-slate-600 mt-1">Éphémérides : Astronomy Engine — Alt. depuis {DEFAULT_OBSERVER.name}</div>
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
      {/* Phase lunaire */}
      {posData && (
        <div className="absolute bottom-3 right-3 z-10 flex items-center gap-2.5 px-3 py-2 border border-slate-800/70 bg-[#060A14]/85 backdrop-blur-sm">
          <MoonPhaseIcon phase={posData.moonPhaseAngle} />
          <div className="text-right">
            <div className="text-[9px] font-tech-mono text-[#C8C8D0]">{moonPhaseName(posData.moonPhaseAngle)}</div>
            <div className="text-[8px] font-tech-mono text-slate-500">Illumination : {posData.moonIllumination.toFixed(0)} %</div>
          </div>
        </div>
      )}
      {/* Légende tropiques + crépuscule */}
      <div className="absolute bottom-3 left-3 z-10 flex flex-col gap-1">
        {showTropics && <>
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
        </>}
        <div className="flex items-center gap-2">
          <div className="w-4 h-1.5" style={{background:'linear-gradient(90deg, #FF9452, #3A2A1A, #0A0A12)'}} />
          <span className="text-[7px] font-tech-mono text-slate-500">Crépuscule civil → nautique → astro.</span>
        </div>
      </div>
      <Canvas camera={{position:[0,12,0.1],fov:50}}>
        <FlatScene speed={speed} showLabels={showLabels} isPlaying={isPlaying} showTropics={showTropics} dateRef={dateRef} onPosUpdate={onPosUpdate}/>
        <OrbitControls enablePan={false} minDistance={6} maxDistance={20} minPolarAngle={0} maxPolarAngle={Math.PI*0.3}/>
      </Canvas>
    </div>
    <div className="mt-3 border border-slate-800/50 bg-[var(--hull)] p-4">
      <p className="text-[13px] text-[var(--text-60)] font-rajdhani leading-relaxed">
        Modèle Terre plane : carte azimutale équidistante satellite. Le Soleil circule au-dessus du disque — la zone éclairée suit sa position avec les trois bandes crépusculaires (civile −6°, nautique −12°, astronomique −18°). Réglez la date et l&apos;heure pour explorer les éphémérides : positions du Soleil, de la Lune (avec sa phase) et des cinq planètes visibles, avec leur altitude vue depuis {DEFAULT_OBSERVER.name} (▲ au-dessus de l&apos;horizon, ▼ en dessous).
      </p>
      <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-600">ARTICLES :</span>
        <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">Le MGPP →</a>
        <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[var(--cyan)]/50 hover:text-[var(--cyan)]">L&apos;hypothèse nulle →</a>
      </div>
    </div>
  </div>;
}
