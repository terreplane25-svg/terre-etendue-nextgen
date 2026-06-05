'use client';

import React from 'react';

interface OceanSceneProps {
  shipScale: number;
  showVignette: boolean;
  zoomLevel: number;
}

export default function OceanScene({ shipScale, showVignette, zoomLevel }: OceanSceneProps) {
  const horizonY = 255;
  const shipCenterY = horizonY - 2;
  const shipOpacity = Math.min(1, shipScale * 12);
  const shipBlur = Math.max(0, (1 - shipScale) * 3.5);

  return (
    <svg viewBox="0 0 800 500" style={{ width: '100%', height: '100%', display: 'block' }} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0e1c38"/><stop offset="30%" stopColor="#1a3558"/><stop offset="60%" stopColor="#2d5a7a"/><stop offset="100%" stopColor="#5a90ac"/></linearGradient>
        <linearGradient id="ocean" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#1a4a68"/><stop offset="35%" stopColor="#0f3852"/><stop offset="100%" stopColor="#071c2e"/></linearGradient>
        <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5a90ac" stopOpacity="0"/><stop offset="50%" stopColor="#6a9ab5" stopOpacity="1"/><stop offset="100%" stopColor="#5a90ac" stopOpacity="0.5"/></linearGradient>
        <radialGradient id="sunglow" cx="0.73" cy="0.22" r="0.35"><stop offset="0%" stopColor="#FFD700" stopOpacity="0.3"/><stop offset="70%" stopColor="#FFD700" stopOpacity="0.05"/><stop offset="100%" stopColor="#FFD700" stopOpacity="0"/></radialGradient>
        <radialGradient id="vignette" cx="0.5" cy="0.5" r="0.5"><stop offset="60%" stopColor="black" stopOpacity="0"/><stop offset="90%" stopColor="black" stopOpacity="0.6"/><stop offset="100%" stopColor="black" stopOpacity="0.85"/></radialGradient>
      </defs>

      {/* Sky */}
      <rect width="800" height={horizonY} fill="url(#sky)"/>
      <circle cx="610" cy="95" r="85" fill="url(#sunglow)"/>
      <circle cx="610" cy="95" r="9" fill="#FFD700" opacity="0.8"/>
      <circle cx="610" cy="95" r="4" fill="#FFFDE8" opacity="0.95"/>
      <ellipse cx="140" cy="65" rx="75" ry="12" fill="#fff" opacity="0.04"/>
      <ellipse cx="370" cy="95" rx="95" ry="10" fill="#fff" opacity="0.035"/>

      {/* Ocean */}
      <rect x="0" y={horizonY} width="800" height={500-horizonY} fill="url(#ocean)"/>
      <line x1="0" y1={horizonY} x2="800" y2={horizonY} stroke="#6a9ab5" strokeWidth="0.7" opacity="0.4"/>

      {/* Waves */}
      {[0,1,2,3,4,5,6,7,8,9].map(i=>{const y=horizonY+6+i*22;const amp=1.8+i*0.4;const op=Math.max(0,0.09-i*0.007);return<path key={i} d={`M0,${y} ${Array.from({length:21},(_,j)=>{const x=j*40;const w=Math.sin((x+i*22)*0.022)*amp;return`Q${x+20},${y+w*1.8} ${x+40},${y+w}`;}).join(' ')}`} fill="none" stroke="#fff" strokeWidth="0.55" opacity={op}/>;})}

      {/* Sun reflections */}
      {[0,1,2,3].map(i=><line key={`r${i}`} x1={598+i*7} y1={horizonY+5+i*9} x2={602+i*7} y2={horizonY+7+i*9} stroke="#FFD700" strokeWidth="1.3" opacity="0.1"/>)}

      {/* Haze */}
      <rect x="0" y={horizonY-45} width="800" height="90" fill="url(#haze)" opacity={Math.max(0,0.5-shipScale*0.45)}/>

      {/* Ship — scales uniformly, always fully visible */}
      <g transform={`translate(400,${shipCenterY}) scale(${shipScale})`} opacity={shipOpacity} style={{filter:`blur(${shipBlur}px)`,transformOrigin:'0 0'}}>
        <path d="M-75,0 L-65,-5 L65,-5 L75,0 L80,8 L-80,8 Z" fill="#1e1c18"/>
        <path d="M-70,-5 L70,-5 L75,0 L-75,0 Z" fill="#2a2720"/>
        <rect x="-68" y="-3" width="136" height="2.5" fill="#8a7560" opacity="0.35"/>
        <line x1="-75" y1="1" x2="75" y2="1" stroke="#883030" strokeWidth="1.5" opacity="0.5"/>
        <rect x="-60" y="-28" width="120" height="23" rx="2" fill="#3a3730"/>
        <rect x="-50" y="-25" width="18" height="16" rx="1" fill="#8a3030" opacity="0.7"/>
        <rect x="-28" y="-25" width="18" height="16" rx="1" fill="#2a5a8a" opacity="0.7"/>
        <rect x="-6" y="-25" width="18" height="16" rx="1" fill="#8a7a30" opacity="0.6"/>
        <rect x="18" y="-48" width="42" height="20" rx="2" fill="#4a4740"/>
        <rect x="22" y="-44" width="8" height="6" rx="1" fill="#5a8da8" opacity="0.5"/>
        <rect x="33" y="-44" width="8" height="6" rx="1" fill="#5a8da8" opacity="0.5"/>
        <rect x="44" y="-44" width="8" height="6" rx="1" fill="#5a8da8" opacity="0.4"/>
        <rect x="24" y="-64" width="32" height="16" rx="2" fill="#555550"/>
        <rect x="28" y="-60" width="24" height="7" rx="1" fill="#7abcd0" opacity="0.4"/>
        <rect x="48" y="-58" width="10" height="12" rx="1.5" fill="#222018"/>
        <rect x="49" y="-61" width="8" height="5" rx="1" fill="#883030" opacity="0.8"/>
        <rect x="38" y="-88" width="2.5" height="24" fill="#4a4740"/>
        <circle cx="39" cy="-88" r="2.5" fill="#cc3030" opacity="0.7"/>
        <path d="M-80,8 L-88,4 L-75,0 Z" fill="#1a1810"/>
        <path d="M80,8 L88,4 L75,0 Z" fill="#1a1810"/>
        <path d="M-85,6 Q-95,4 -115,8" stroke="#fff" strokeWidth="1" fill="none" opacity="0.12"/>
        <path d="M85,6 Q92,5 105,8" stroke="#fff" strokeWidth="0.6" fill="none" opacity="0.06"/>
      </g>

      {/* Vignette */}
      {showVignette && <rect width="800" height="500" fill="url(#vignette)" opacity={Math.min(0.7,zoomLevel*0.9)}/>}

      {/* Crosshair */}
      {showVignette && zoomLevel > 0.05 && (
        <g opacity={Math.min(0.2,zoomLevel*0.3)}>
          <circle cx="400" cy={horizonY-5} r={50+zoomLevel*60} fill="none" stroke="#fff" strokeWidth="0.6"/>
          <line x1={380-zoomLevel*20} y1={horizonY-5} x2={420+zoomLevel*20} y2={horizonY-5} stroke="#fff" strokeWidth="0.4"/>
          <line x1="400" y1={horizonY-25-zoomLevel*20} x2="400" y2={horizonY+15+zoomLevel*20} stroke="#fff" strokeWidth="0.4"/>
        </g>
      )}

      {/* Zoom indicator */}
      {zoomLevel > 0.02 && <text x="770" y="485" fill="#fff" opacity="0.3" fontSize="13" fontFamily="'JetBrains Mono',monospace" textAnchor="end">×{(1+zoomLevel*24).toFixed(0)}</text>}
    </svg>
  );
}
