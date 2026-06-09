'use client';
import { useState } from 'react';

const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

interface Props {
  children: React.ReactNode;
  style?: React.CSSProperties;
  hover?: boolean;
}

export default function BezelCard({ children, style = {}, hover = true }: Props) {
  const [hov, setHov] = useState(false);
  return (
    <div
      onMouseEnter={() => setHov(true)}
      onMouseLeave={() => setHov(false)}
      style={{
        background: '#F5F3EE',
        border: '1px solid rgba(20,18,16,0.06)',
        borderRadius: 8,
        padding: 6,
        transition: `all 0.6s ${BEZ}`,
        transform: hov && hover ? 'translateY(-2px) scale(1.003)' : 'translateY(0) scale(1)',
        ...style,
      }}
    >
      <div style={{
        background: '#FFFFFF',
        borderRadius: 6,
        overflow: 'hidden',
        boxShadow: hov
          ? '0 8px 32px rgba(0,0,0,0.06), inset 0 1px 1px rgba(255,255,255,0.8)'
          : '0 2px 8px rgba(0,0,0,0.03), inset 0 1px 1px rgba(255,255,255,0.6)',
        transition: `box-shadow 0.6s ${BEZ}`,
      }}>{children}</div>
    </div>
  );
}
