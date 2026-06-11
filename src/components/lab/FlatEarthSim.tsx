'use client';
import React, { useRef, useState, useMemo, useEffect, useCallback } from 'react';
import { Canvas, useFrame } from '@react-three/fiber';
import { OrbitControls, Html, Line, Billboard } from '@react-three/drei';
import * as THREE from 'three';
import { getAllPositions, latLngToFlatDisc, moonPhaseName, DEFAULT_OBSERVER, type CelestialPosition, type ObserverLocation } from './celestialCalc';

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

/**
 * Marqueur de l'observateur sur le disque : anneau + point verts.
 * Un trait court indique la direction du Nord (vers le centre du disque).
 */
function ObserverPin({ observer, show }:{ observer:ObserverLocation; show:boolean }) {
  const [x,z] = latLngToFlatDisc(observer.lat, observer.lng, DISC_R);
  // Direction du Nord sur la carte AE : vers le pôle (centre du disque)
  const d = Math.max(Math.hypot(x,z), 1e-6);
  const nx = -x/d, nz = -z/d;
  return <group position={[x,0.06,z]}>
    <mesh rotation={[-Math.PI/2,0,0]}>
      <ringGeometry args={[0.07,0.11,24]} />
      <meshBasicMaterial color="#00E87B" side={THREE.DoubleSide} />
    </mesh>
    <mesh rotation={[-Math.PI/2,0,0]}>
      <circleGeometry args={[0.035,16]} />
      <meshBasicMaterial color="#00E87B" />
    </mesh>
    <Line points={[new THREE.Vector3(0,0,0), new THREE.Vector3(nx*0.35,0,nz*0.35)]} color="#00E87B" opacity={0.7} transparent lineWidth={1.5} />
    <Label text={`📍 ${observer.name}`} color="#00E87B" show={show} />
  </group>;
}

function FlatScene({ speed, showLabels, isPlaying, showTropics, dateRef, observer, onPosUpdate }:{
  speed:number; showLabels:boolean; isPlaying:boolean; showTropics:boolean;
  dateRef: React.MutableRefObject<Date>;
  observer: ObserverLocation;
  onPosUpdate:(d:Date, p:PosData)=>void;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group|null)[]>([]);
  const lastMs = useRef(0);
  const frameCount = useRef(0);
  const [posData, setPosData] = useState<PosData>(() => getAllPositions(dateRef.current, observer));
  const [sunLatLng, setSunLatLng] = useState<[number,number]>([posData.sun.lat, posData.sun.lng]);

  const SUN_H = 0.3;
  const MOON_H = 0.25;

  // Forcer un recalcul quand l'observateur change (les altitudes en dépendent)
  useEffect(()=>{ lastMs.current = 0; },[observer]);

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

    const pos = getAllPositions(dateRef.current, observer);

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
    const p = getAllPositions(dateRef.current, observer);
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
      <ObserverPin observer={observer} show={showLabels} />

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

// ————— VUE DÔME (observateur au sol) —————

const DOME_R = 50;

/** Coordonnées horizontales → position 3D : azimut 0°=Nord (−z), 90°=Est (+x) */
function altAzToVec(altDeg: number, azDeg: number, r: number): [number, number, number] {
  const alt = altDeg * Math.PI / 180, az = azDeg * Math.PI / 180;
  return [Math.cos(alt) * Math.sin(az) * r, Math.sin(alt) * r, -Math.cos(alt) * Math.cos(az) * r];
}

function DomeScene({ speed, showLabels, isPlaying, dateRef, observer, onPosUpdate }:{
  speed:number; showLabels:boolean; isPlaying:boolean;
  dateRef: React.MutableRefObject<Date>;
  observer: ObserverLocation;
  onPosUpdate:(d:Date, p:PosData)=>void;
}) {
  const sunRef = useRef<THREE.Group>(null);
  const moonRef = useRef<THREE.Group>(null);
  const planetRefs = useRef<(THREE.Group|null)[]>([]);
  const skyMatRef = useRef<THREE.ShaderMaterial>(null);
  const starsMatRef = useRef<THREE.PointsMaterial>(null);
  const lastMs = useRef(0);
  const frameCount = useRef(0);
  const [posData, setPosData] = useState<PosData>(() => getAllPositions(dateRef.current, observer));

  useEffect(()=>{ lastMs.current = 0; },[observer]);

  // Ciel : gradient zénith/horizon jour↔nuit + lueur crépusculaire orangée vers le Soleil
  const skyShader = useMemo(()=>({
    uniforms: { uSunDir: { value: new THREE.Vector3(0,1,0) } },
    vertexShader: `
      varying vec3 vDir;
      void main(){
        vDir = normalize(position);
        gl_Position = projectionMatrix * modelViewMatrix * vec4(position,1.0);
      }
    `,
    fragmentShader: `
      uniform vec3 uSunDir;
      varying vec3 vDir;
      void main(){
        float h = max(vDir.y, 0.0);
        float sunAlt = uSunDir.y; // sin(altitude solaire)
        float day = smoothstep(-0.12, 0.12, sunAlt);
        vec3 zen = mix(vec3(0.008, 0.012, 0.030), vec3(0.10, 0.32, 0.65), day);
        vec3 hor = mix(vec3(0.025, 0.035, 0.070), vec3(0.55, 0.72, 0.88), day);
        vec3 col = mix(hor, zen, pow(h, 0.6));
        float cosToSun = dot(vDir, normalize(uSunDir));
        // Lueur crépusculaire : Soleil bas (−18°..+20°), concentrée vers son azimut et l'horizon
        float twi = smoothstep(-0.31, 0.0, sunAlt) * (1.0 - smoothstep(0.05, 0.34, sunAlt));
        col += vec3(0.90, 0.35, 0.12) * pow(max(cosToSun, 0.0), 4.0) * (1.0 - h) * twi * 0.85;
        // Halo diurne autour du Soleil
        col += vec3(1.0, 0.9, 0.7) * pow(max(cosToSun, 0.0), 60.0) * day * 0.5;
        gl_FragColor = vec4(col, 1.0);
      }
    `,
  }),[]);

  // Champ d'étoiles fixes (positions aléatoires sur le dôme, opacité liée à la nuit)
  const starGeom = useMemo(()=>{
    const n = 450;
    const arr = new Float32Array(n*3);
    for(let i=0;i<n;i++){
      const az = Math.random()*360;
      const alt = Math.asin(Math.random())*180/Math.PI; // distribution uniforme sur la sphère
      const [x,y,z] = altAzToVec(alt, az, DOME_R*0.98);
      arr[i*3]=x; arr[i*3+1]=y; arr[i*3+2]=z;
    }
    const g = new THREE.BufferGeometry();
    g.setAttribute('position', new THREE.BufferAttribute(arr,3));
    return g;
  },[]);

  useFrame(()=>{
    if (isPlaying) {
      const dtMs = 0.016 * speed * 30 * 60 * 1000;
      dateRef.current = new Date(dateRef.current.getTime() + dtMs);
    }
    const ms = dateRef.current.getTime();
    frameCount.current++;
    if (ms === lastMs.current) return;
    lastMs.current = ms;

    const pos = getAllPositions(dateRef.current, observer);

    if (sunRef.current && pos.sun.altitude !== undefined)
      sunRef.current.position.set(...altAzToVec(pos.sun.altitude, pos.sun.azimuth!, DOME_R*0.9));
    if (moonRef.current && pos.moon.altitude !== undefined)
      moonRef.current.position.set(...altAzToVec(pos.moon.altitude, pos.moon.azimuth!, DOME_R*0.9));
    pos.planets.forEach((p,i)=>{
      const ref = planetRefs.current[i];
      if(ref && p.altitude !== undefined) ref.position.set(...altAzToVec(p.altitude, p.azimuth!, DOME_R*0.9));
    });

    const sunDir = altAzToVec(pos.sun.altitude ?? 0, pos.sun.azimuth ?? 0, 1);
    if (skyMatRef.current) skyMatRef.current.uniforms.uSunDir.value.set(...sunDir);
    if (starsMatRef.current) {
      const day = THREE.MathUtils.smoothstep(sunDir[1], -0.12, 0.12);
      starsMatRef.current.opacity = (1 - day) * 0.9;
    }

    if (!isPlaying || frameCount.current % 20 === 0) {
      setPosData(pos);
      onPosUpdate(dateRef.current, pos);
    }
  });

  const altCircle = (altDeg:number) => {
    const pts: THREE.Vector3[] = [];
    for(let i=0;i<=96;i++){
      pts.push(new THREE.Vector3(...altAzToVec(altDeg, (i/96)*360, DOME_R*0.96)));
    }
    return pts;
  };

  const initSun = useMemo(()=>altAzToVec(posData.sun.altitude ?? 0, posData.sun.azimuth ?? 0, DOME_R*0.9),
  // position initiale uniquement
  // eslint-disable-next-line react-hooks/exhaustive-deps
  []);

  return (
    <group>
      {/* Dôme céleste */}
      <mesh>
        <sphereGeometry args={[DOME_R, 48, 24, 0, Math.PI*2, 0, Math.PI*0.55]} />
        <shaderMaterial ref={skyMatRef}
          uniforms={skyShader.uniforms}
          vertexShader={skyShader.vertexShader}
          fragmentShader={skyShader.fragmentShader}
          side={THREE.BackSide} depthWrite={false}
        />
      </mesh>
      <points geometry={starGeom}>
        <pointsMaterial ref={starsMatRef} color="#FFFFFF" size={0.22} sizeAttenuation transparent opacity={0} depthWrite={false} />
      </points>

      {/* Sol */}
      <mesh rotation={[-Math.PI/2,0,0]} position={[0,-0.02,0]}>
        <circleGeometry args={[DOME_R*1.1, 64]} />
        <meshBasicMaterial color="#070A06" />
      </mesh>

      {/* Horizon + cercles d'altitude 30° et 60° */}
      <Line points={altCircle(0)} color="#3A6648" opacity={0.7} transparent lineWidth={1.5} />
      <Line points={altCircle(30)} color="#2A4458" opacity={0.3} transparent lineWidth={1} />
      <Line points={altCircle(60)} color="#2A4458" opacity={0.2} transparent lineWidth={1} />

      {/* Points cardinaux */}
      {[['N',0,'#00E87B'],['E',90,'#8090A8'],['S',180,'#8090A8'],['O',270,'#8090A8']].map(([t,az,c])=>(
        <group key={t as string} position={altAzToVec(1.5, az as number, DOME_R*0.93)}>
          <Label text={t as string} color={c as string} show />
        </group>
      ))}

      {/* Soleil */}
      <group ref={sunRef} position={initSun}>
        <Billboard>
          <mesh><circleGeometry args={[2,32]} /><meshBasicMaterial color={SUN_C} /></mesh>
          <mesh><circleGeometry args={[4.2,32]} /><meshBasicMaterial color={SUN_C} transparent opacity={0.15} depthWrite={false} /></mesh>
        </Billboard>
        <Label text={`Soleil ☉${altText(posData.sun)}`} color={SUN_C} show={showLabels && (posData.sun.altitude ?? 0) > -3} />
      </group>

      {/* Lune */}
      <group ref={moonRef}>
        <Billboard>
          <mesh><circleGeometry args={[1.4,32]} /><meshBasicMaterial color={MOON_C} /></mesh>
        </Billboard>
        <Label text={`Lune ☾${altText(posData.moon)}`} color={MOON_C} show={showLabels && (posData.moon.altitude ?? 0) > -3} />
      </group>

      {/* Planètes */}
      {posData.planets.map((p,i)=>(
        <group key={p.name} ref={el=>{planetRefs.current[i]=el;}}>
          <Billboard>
            <mesh><circleGeometry args={[p.size*4,16]} /><meshBasicMaterial color={p.color} /></mesh>
          </Billboard>
          <Label text={`${p.name}${altText(p)}`} color={p.color} show={showLabels && (p.altitude ?? 0) > -3} />
        </group>
      ))}
    </group>
  );
}

/**
 * Boussole : azimuts du Soleil et de la Lune vus depuis l'observateur.
 * Aiguilles pleines au-dessus de l'horizon, estompées en dessous.
 */
function CompassHUD({ sun, moon }:{ sun:CelestialPosition; moon:CelestialPosition }) {
  const size = 92, cx = size/2, cy = size/2, R = 33;
  const needle = (azDeg:number, len:number) => {
    const a = azDeg * Math.PI / 180;
    return { x: cx + Math.sin(a)*len, y: cy - Math.cos(a)*len };
  };
  const bodies = [
    { p: sun, color: SUN_C, sym: '☉' },
    { p: moon, color: MOON_C, sym: '☾' },
  ].filter(b => b.p.azimuth !== undefined);
  return (
    <div className="flex flex-col items-center gap-1 px-2.5 py-2 border border-slate-800/70 bg-[#060A14]/85 backdrop-blur-sm">
      <svg width={size} height={size} viewBox={`0 0 ${size} ${size}`}>
        <circle cx={cx} cy={cy} r={R+6} fill="none" stroke="#2A3448" strokeWidth="1" />
        {[0,45,90,135,180,225,270,315].map(a=>{
          const o = needle(a, R+6), i = needle(a, a%90===0 ? R : R+3);
          return <line key={a} x1={i.x} y1={i.y} x2={o.x} y2={o.y} stroke="#3A4458" strokeWidth="1" />;
        })}
        {[['N',0,'#00E87B'],['E',90,'#8090A8'],['S',180,'#8090A8'],['O',270,'#8090A8']].map(([t,a,c])=>{
          const pos = needle(a as number, R+13);
          return <text key={t as string} x={pos.x} y={pos.y+3} textAnchor="middle" fontSize="8" fontFamily="monospace" fill={c as string} fontWeight="bold">{t}</text>;
        })}
        {bodies.map(({p,color})=>{
          const tip = needle(p.azimuth!, R-2);
          const vis = (p.altitude ?? 0) >= 0;
          return <g key={p.name} opacity={vis ? 1 : 0.3}>
            <line x1={cx} y1={cy} x2={tip.x} y2={tip.y} stroke={color} strokeWidth="1.5" />
            <circle cx={tip.x} cy={tip.y} r="3" fill={color} />
          </g>;
        })}
        <circle cx={cx} cy={cy} r="2" fill="#4A5468" />
      </svg>
      <div className="text-[7px] font-tech-mono text-slate-500 whitespace-nowrap">
        {bodies.map(({p,sym},i)=>(
          <span key={p.name}>{i>0 && ' · '}{sym} {p.azimuth!.toFixed(0)}°</span>
        ))}
      </div>
    </div>
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
  const [observer,setObserver]=useState<ObserverLocation>(DEFAULT_OBSERVER);
  const [geoStatus,setGeoStatus]=useState<'idle'|'loading'|'error'>('idle');
  const [viewMode,setViewMode]=useState<'map'|'dome'>('map');

  const isCustomObs = observer.name === 'Ma position';

  const locateMe = useCallback(()=>{
    if (isCustomObs) { setObserver(DEFAULT_OBSERVER); setGeoStatus('idle'); return; }
    if (!navigator.geolocation) { setGeoStatus('error'); return; }
    setGeoStatus('loading');
    navigator.geolocation.getCurrentPosition(
      p => {
        setObserver({ lat: p.coords.latitude, lng: p.coords.longitude, name: 'Ma position' });
        setGeoStatus('idle');
      },
      () => setGeoStatus('error'),
      { timeout: 10000 }
    );
  },[isCustomObs]);

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
      <div className="flex border border-slate-800">
        <button onClick={()=>setViewMode('map')}
          className={`px-3 py-1.5 text-[8px] font-tech-mono tracking-widest ${viewMode==='map'?'bg-[var(--cyan)]/15 text-[var(--cyan)]':'text-slate-600 hover:text-slate-400'}`}
        >🗺 CARTE</button>
        <button onClick={()=>setViewMode('dome')}
          className={`px-3 py-1.5 text-[8px] font-tech-mono tracking-widest ${viewMode==='dome'?'bg-[var(--cyan)]/15 text-[var(--cyan)]':'text-slate-600 hover:text-slate-400'}`}
        >⛰ DÔME</button>
      </div>
      {viewMode==='map' && <button onClick={()=>setShowTropics(!showTropics)}
        className={`px-3 py-1 text-[8px] font-tech-mono border ${showTropics?'border-[#D4A843]/50 text-[#D4A843]':'border-slate-800 text-slate-600'}`}
      >TROPIQUES: {showTropics?'ON':'OFF'}</button>}
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
      <div className="ml-auto flex items-center gap-2 flex-wrap">
        <button onClick={locateMe} disabled={geoStatus==='loading'}
          className={`px-3 py-1.5 text-[8px] font-tech-mono tracking-widest border ${
            isCustomObs ? 'border-[var(--cyan)]/50 text-[var(--cyan)] hover:bg-[var(--cyan)]/10'
            : 'border-[#00E87B]/50 text-[#00E87B] hover:bg-[#00E87B]/10'
          } disabled:opacity-50`}
        >{geoStatus==='loading' ? '… LOCALISATION' : isCustomObs ? `↺ ${DEFAULT_OBSERVER.name.toUpperCase()}` : '📍 MA POSITION'}</button>
        <button onClick={resetNow}
          className="px-3 py-1.5 text-[8px] font-tech-mono tracking-widest border border-[var(--green)]/50 text-[var(--green)] hover:bg-[var(--green)]/10"
        >● MAINTENANT</button>
      </div>
      {geoStatus==='error' && (
        <span className="w-full text-[8px] font-tech-mono text-[#FF6655]">Géolocalisation indisponible — vérifiez les permissions du navigateur.</span>
      )}
    </div>

    <div className="w-full h-[55vh] md:h-[70vh] border border-slate-800/50 bg-[#020408] relative overflow-hidden">
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[var(--cyan-20)] z-10"/>
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[var(--cyan-20)] z-10"/>
      <div className="absolute top-3 left-3 z-10">
        <div className="text-[9px] font-tech-mono text-[var(--green)] tracking-widest">
          {viewMode==='map' ? '◉ TERRE PLANE — VUE DU DESSUS' : '◉ DÔME CÉLESTE — VUE DE L’OBSERVATEUR'}
        </div>
        <div className="text-[8px] font-tech-mono text-slate-600 mt-1">Éphémérides : Astronomy Engine — {viewMode==='map'?'Alt. depuis':'Observateur :'} {observer.name} ({observer.lat.toFixed(1)}°, {observer.lng.toFixed(1)}°)</div>
        {viewMode==='dome' && <div className="text-[8px] font-tech-mono text-slate-700 mt-0.5">Glissez pour regarder autour de vous</div>}
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
      {/* Boussole + phase lunaire */}
      {posData && (
        <div className="absolute bottom-3 right-3 z-10 flex flex-col items-end gap-2">
          <CompassHUD sun={posData.sun} moon={posData.moon} />
          <div className="flex items-center gap-2.5 px-3 py-2 border border-slate-800/70 bg-[#060A14]/85 backdrop-blur-sm">
            <MoonPhaseIcon phase={posData.moonPhaseAngle} />
            <div className="text-right">
              <div className="text-[9px] font-tech-mono text-[#C8C8D0]">{moonPhaseName(posData.moonPhaseAngle)}</div>
              <div className="text-[8px] font-tech-mono text-slate-500">Illumination : {posData.moonIllumination.toFixed(0)} %</div>
            </div>
          </div>
        </div>
      )}
      {/* Légende tropiques + crépuscule */}
      {viewMode==='map' && <div className="absolute bottom-3 left-3 z-10 flex flex-col gap-1">
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
      </div>}
      {viewMode==='map' ? (
        <Canvas key="map" camera={{position:[0,12,0.1],fov:50}}>
          <FlatScene speed={speed} showLabels={showLabels} isPlaying={isPlaying} showTropics={showTropics} dateRef={dateRef} observer={observer} onPosUpdate={onPosUpdate}/>
          <OrbitControls enablePan={false} minDistance={6} maxDistance={20} minPolarAngle={0} maxPolarAngle={Math.PI*0.3}/>
        </Canvas>
      ) : (
        <Canvas key="dome" camera={{position:[0,1.6,0.12],fov:65}}>
          <DomeScene speed={speed} showLabels={showLabels} isPlaying={isPlaying} dateRef={dateRef} observer={observer} onPosUpdate={onPosUpdate}/>
          <OrbitControls enablePan={false} enableZoom={false} target={[0,1.6,0]}
            minDistance={0.12} maxDistance={0.12} rotateSpeed={-0.35}
            minPolarAngle={Math.PI*0.12} maxPolarAngle={Math.PI*0.58}/>
        </Canvas>
      )}
    </div>
    <div className="mt-3 border border-slate-800/50 bg-[var(--hull)] p-4">
      <p className="text-[13px] text-[#C8D8E8]/80 font-rajdhani leading-relaxed">
        Modèle Terre plane : carte azimutale équidistante satellite. Le Soleil circule au-dessus du disque — la zone éclairée suit sa position avec les trois bandes crépusculaires (civile −6°, nautique −12°, astronomique −18°). Réglez la date et l&apos;heure pour explorer les éphémérides : positions du Soleil, de la Lune (avec sa phase) et des cinq planètes visibles, avec leur altitude vue depuis {observer.name} (▲ au-dessus de l&apos;horizon, ▼ en dessous). Le marqueur vert indique l&apos;observateur — utilisez 📍 MA POSITION pour le placer chez vous (le trait pointe vers le Nord, c&apos;est-à-dire le centre du disque). La boussole donne les azimuts du Soleil et de la Lune depuis ce point. Le mode ⛰ DÔME place la caméra au sol, à la position de l&apos;observateur : glissez pour balayer le ciel — chaque astre y est placé à son altitude et azimut réels, avec lueur crépusculaire vers le Soleil couchant et étoiles la nuit.
      </p>
      <div className="flex flex-wrap items-center gap-3 mt-3 pt-3 border-t border-slate-800/30">
        <span className="text-[8px] font-tech-mono text-slate-400">ARTICLES :</span>
        <a href="/article/le-modele-geocentrique-a-plans-paralleles-mgpp" className="text-[9px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">Le MGPP →</a>
        <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[9px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;hypothèse nulle →</a>
      </div>
    </div>
  </div>;
}
