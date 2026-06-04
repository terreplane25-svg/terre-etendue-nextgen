'use client';

import React, { useState } from 'react';

const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

interface DisplayCardProps {
  title: string;
  description: string;
  date: string;
  color: string;
  icon: string;
  offsetX?: number;
  offsetY?: number;
}

function DisplayCard({ title, description, date, color, icon, offsetX = 0, offsetY = 0 }: DisplayCardProps) {
  const [hov, setHov] = useState(false);
  return (
    <div onMouseEnter={() => setHov(true)} onMouseLeave={() => setHov(false)} style={{
      gridArea: 'stack',
      transform: `translateX(${offsetX}px) translateY(${offsetY + (hov ? -14 : 0)}px) skewY(-6deg)`,
      position: 'relative', width: 350, height: 145,
      background: hov ? '#fff' : '#F5F3EE',
      border: `1.5px solid ${hov ? color + '40' : 'rgba(20,18,16,0.06)'}`,
      borderRadius: 18, padding: '18px 22px',
      transition: `all 0.6s ${BEZ}`, cursor: 'pointer',
      boxShadow: hov ? `0 14px 44px ${color}18` : '0 2px 8px rgba(0,0,0,0.03)',
      display: 'flex', flexDirection: 'column', justifyContent: 'space-between',
      backdropFilter: 'blur(8px)', overflow: 'hidden',
    }}>
      <div style={{ position: 'absolute', right: -1, top: '-5%', height: '110%', width: 220, background: 'linear-gradient(to left, #FAFAF6, transparent)', pointerEvents: 'none' }} />
      <div style={{ display: 'flex', alignItems: 'center', gap: 10, position: 'relative' }}>
        <div style={{ width: 28, height: 28, borderRadius: 99, background: color + '20', display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 14 }}>{icon}</div>
        <span style={{ fontSize: 15, fontWeight: 700, color: hov ? color : '#141210', transition: `color 0.3s ${BEZ}` }}>{title}</span>
      </div>
      <p style={{ fontSize: 13, color: '#3D3A35', position: 'relative', whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis' }}>{description}</p>
      <p style={{ fontSize: 11, color: '#BAB5AC', position: 'relative' }}>{date}</p>
      {!hov && <div style={{ position: 'absolute', inset: 0, borderRadius: 18, background: 'rgba(250,250,246,0.35)', pointerEvents: 'none', transition: `opacity 0.5s ${BEZ}` }} />}
    </div>
  );
}

interface DisplayCardsProps {
  cards: DisplayCardProps[];
}

export default function DisplayCards({ cards }: DisplayCardsProps) {
  return (
    <div style={{ display: 'grid', gridTemplateAreas: "'stack'", placeItems: 'center', padding: '40px 0 60px' }}>
      {cards.map((c, i) => <DisplayCard key={c.title} {...c} offsetX={i * 52} offsetY={i * 35} />)}
    </div>
  );
}
