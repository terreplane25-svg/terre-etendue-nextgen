'use client';

import React from 'react';

interface OceanSceneProps {
  progress: number;
}

export default function OceanScene({ progress }: OceanSceneProps) {
  const p = progress;
  const horizonY = 255;
  const shipBaseY = horizonY + 5;
  const shipTotalHeight = 110;
  const revealAmount = Math.max(0, (p - 0.08) / 0.85);
  const clipY = shipBaseY - (revealAmount * shipTotalHeight) - 5;
  const shipOpacity = Math.min(1, Math.max(0, (p - 0.08) * 5));
  const shipBlur = Math.max(0, (0.5 - p) * 4);
  const hazeOpacity = 0.65 - p * 0.6;
  const wavePhase = p * 40;
  const zoomFactor = 1 + p * 24;

  return (
    <svg viewBox="0 0 800 500" style={{ width: '100%', height: '100%', display: 'block' }} xmlns="http://www.w3.org/2000/svg">
      <defs>
        <linearGradient id="sky" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#0f1f3a"/><stop offset="35%" stopColor="#1a3555"/><stop offset="65%" stopColor="#2d5a78"/><stop offset="100%" stopColor="#5a8da8"/></linearGradient>
        <linearGradient id="ocean" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#1a4a65"/><stop offset="40%" stopColor="#0f3550"/><stop offset="100%" stopColor="#081e30"/></linearGradient>
        <linearGradient id="haze" x1="0" y1="0" x2="0" y2="1"><stop offset="0%" stopColor="#5a8da8" stopOpacity="0"/><stop offset="60%" stopColor="#6a98b0" stopOpacity="1"/><stop offset="100%" stopColor="#5a8da8" stopOpacity="0.6"/></linearGradient>
        <radialGradient id="sunglow" cx="0.72" cy="0.25" r="0.35"><stop offset="0%" stopColor="#FFD700" stopOpacity="0.35"/><stop offset="60%" stopColor="#FFD700" stopOpacity="0.08"/><stop offset="100%" stopColor="#FFD700" stopOpacity="0"/></radialGradient>
        <clipPath id="shipReveal"><rect x="0" y={clipY} width="800" height={500 - clipY}/></clipPath>
      </defs>
      <rect width="800" height={horizonY} fill="url(#sky)"/>
      <circle cx="600" cy="100" r="90" fill="url(#sunglow)"/>
      <circle cx="600" cy="100" r={10 + p * 4} fill="#FFD700" opacity={0.7 + p * 0.2}/>
      <circle cx="600" cy="100" r={5 + p * 2} fill="#FFFBE6" opacity="0.95"/>
      <ellipse cx={150 - p * 40} cy="70" rx="80" ry="14" fill="#ffffff" opacity={Math.max(0, 0.06 - p * 0.03)}/>
      <ellipse cx={380 - p * 30} cy="100" rx="100" ry="12" fill="#ffffff" opacity={Math.max(0, 0.05 - p * 0.03)}/>
      <rect x="0" y={horizonY} width="800" height={500 - horizonY} fill="url(#ocean)"/>
      <line x1="0" y1={horizonY} x2="800" y2={horizonY} stroke="#6a98b0" strokeWidth="0.8" opacity="0.4"/>
      {[0,1,2,3,4,5,6,7,8,9].map(i => {
        const y = horizonY + 8 + i * 22; const amp = 2 + i * 0.4; const opacity = 0.1 - i * 0.008;
        return <path key={i} d={`M0,${y} ${Array.from({length:21},(_,j)=>{const x=j*40;const wave=Math.sin((x+wavePhase+i*25)*0.02)*amp;return`Q${x+20},${y+wave*2} ${x+40},${y+wave}`;}).join(' ')}`} fill="none" stroke="#ffffff" strokeWidth="0.6" opacity={Math.max(0,opacity)}/>;
      })}
      {[0,1,2,3].map(i => <line key={`sr${i}`} x1={588+i*8} y1={horizonY+6+i*10} x2={593+i*8} y2={horizonY+8+i*10} stroke="#FFD700" strokeWidth="1.5" opacity={0.12+p*0.06}/>)}
      <g clipPath="url(#shipReveal)" opacity={shipOpacity} style={{filter:`blur(${shipBlur}px)`}}>
        <g transform={`translate(400,${shipBaseY})`}>
          <rect x="-1.5" y="-105" width="3" height="45" fill="#4a4540"/><circle cx="0" cy="-105" r="3" fill="#dd3333" opacity={0.6+p*0.4}/><circle cx="0" cy="-105" r="8" fill="#dd3333" opacity={p*0.15}/>
          <rect x="8" y="-98" width="1.5" height="20" fill="#5a5550"/><rect x="-10" y="-92" width="1.5" height="15" fill="#5a5550"/>
          <rect x="18" y="-78" width="16" height="20" rx="2" fill="#2a2520"/><rect x="20" y="-82" width="12" height="6" rx="1" fill="#993030"/>
          <ellipse cx="26" cy={-88-p*5} rx={4+p*3} ry={3+p*2} fill="#555" opacity={0.15*p}/>
          <rect x="-18" y="-72" width="36" height="18" rx="3" fill="#5a5550"/><rect x="-14" y="-68" width="28" height="8" rx="1.5" fill="#7abcd0" opacity="0.45"/><rect x="-14" y="-68" width="28" height="8" rx="1.5" fill="#aadde8" opacity={p*0.2}/>
          <rect x="-30" y="-54" width="60" height="24" rx="2" fill="#4a4540"/>
          <rect x="-25" y="-48" width="11" height="9" rx="1.5" fill="#5a8da8" opacity="0.5"/><rect x="-10" y="-48" width="11" height="9" rx="1.5" fill="#5a8da8" opacity="0.5"/><rect x="5" y="-48" width="11" height="9" rx="1.5" fill="#5a8da8" opacity="0.45"/><rect x="20" y="-48" width="8" height="9" rx="1.5" fill="#5a8da8" opacity="0.4"/>
          <line x1="-30" y1="-54" x2="30" y2="-54" stroke="#6a6560" strokeWidth="1"/>
          <path d="M-70,-30 L-60,-30 L-60,0 L60,0 L60,-30 L70,-30 L75,-10 L75,5 L-75,5 L-75,-10 Z" fill="#2a2520"/>
          <path d="M-68,-28 L68,-28 L72,-10 L-72,-10 Z" fill="#3a3530"/>
          <rect x="-68" y="-22" width="136" height="3" fill="#8a7560" opacity="0.4"/>
          <line x1="-72" y1="-8" x2="72" y2="-8" stroke="#993030" strokeWidth="2" opacity="0.5"/>
          <path d="M-75,-10 L-85,0 L-75,5 Z" fill="#222018"/><path d="M75,-10 L85,0 L75,5 Z" fill="#222018"/>
          <path d="M-90,3 Q-100,1 -120,5" stroke="#ffffff" strokeWidth="1.2" fill="none" opacity={0.15*revealAmount}/>
          <path d="M-85,7 Q-100,5 -130,10" stroke="#ffffff" strokeWidth="0.8" fill="none" opacity={0.1*revealAmount}/>
          <rect x="-65" y="6" width="130" height="20" fill="#ffffff" opacity={0.04*revealAmount} rx="2"/>
        </g>
      </g>
      <rect x="0" y={horizonY-50} width="800" height="100" fill="url(#haze)" opacity={hazeOpacity}/>
      {p>0.05&&p<0.8&&(()=>{const lo=Math.min(1,(p-0.05)*3)*(1-Math.max(0,(p-0.6)/0.2))*0.25;const lr=35+p*80;return<g opacity={lo}><circle cx="400" cy={horizonY-20} r={lr} fill="none" stroke="#fff" strokeWidth="1"/><line x1={400-lr*0.25} y1={horizonY-20} x2={400+lr*0.25} y2={horizonY-20} stroke="#fff" strokeWidth="0.5"/><line x1="400" y1={horizonY-20-lr*0.25} x2="400" y2={horizonY-20+lr*0.25} stroke="#fff" strokeWidth="0.5"/></g>;})()}
      {p>0.25&&<g opacity={Math.min(0.35,(p-0.25)*1.5)}>{[{x:200,d:"20km"},{x:340,d:"10km"},{x:460,d:"5km"}].map(m=><g key={m.d}><line x1={m.x} y1={horizonY-3} x2={m.x} y2={horizonY+3} stroke="#fff" strokeWidth="0.5"/><text x={m.x} y={horizonY-6} fill="#fff" fontSize="8" textAnchor="middle" fontFamily="'JetBrains Mono',monospace">{m.d}</text></g>)}</g>}
      <text x="770" y="485" fill="#ffffff" opacity="0.35" fontSize="13" fontFamily="'JetBrains Mono',monospace" textAnchor="end">×{zoomFactor.toFixed(0)}</text>
    </svg>
  );
}
