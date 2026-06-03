'use client';
import { useRef, useState, useEffect } from 'react';

const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

interface Props {
  children: React.ReactNode;
  delay?: number;
  y?: number;
  style?: React.CSSProperties;
}

export default function ScrollReveal({ children, delay = 0, y = 36, style = {} }: Props) {
  const ref = useRef<HTMLDivElement>(null);
  const [vis, setVis] = useState(false);
  useEffect(() => {
    const el = ref.current;
    if (!el) return;
    const obs = new IntersectionObserver(([e]) => { if (e.isIntersecting) { setVis(true); obs.disconnect(); } }, { threshold: 0.08 });
    obs.observe(el);
    return () => obs.disconnect();
  }, []);
  return (
    <div ref={ref} style={{
      ...style,
      transform: vis ? 'translateY(0) scale(1)' : `translateY(${y}px) scale(0.98)`,
      opacity: vis ? 1 : 0,
      filter: vis ? 'blur(0)' : 'blur(5px)',
      transition: `all 0.85s ${BEZ}`,
      transitionDelay: `${delay}ms`,
    }}>{children}</div>
  );
}
