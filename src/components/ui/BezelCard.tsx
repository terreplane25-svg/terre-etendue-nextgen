'use client';
import { useState } from 'react';

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
        background: '#FFFFFF',
        border: '1px solid rgba(20,18,16,0.08)',
        borderRadius: 6,
        overflow: 'hidden',
        transition: 'all 0.3s cubic-bezier(0.32, 0.72, 0, 1)',
        boxShadow: hov && hover ? '0 2px 8px rgba(0,0,0,0.06)' : 'none',
        ...style,
      }}
    >
      {children}
    </div>
  );
}
