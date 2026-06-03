'use client';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Pill from '@/components/ui/Pill';

interface Props { title: string; subtitle: string; color: string; image: string; }

export default function PageHero({ title, subtitle, color, image }: Props) {
  return (
    <section style={{ position: 'relative', height: 360, overflow: 'hidden', display: 'flex', alignItems: 'flex-end' }}>
      <img src={image} alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(250,250,246,0.88) 0%, transparent 45%)' }} />
      <div style={{ position: 'relative', maxWidth: 1100, margin: '0 auto', padding: '0 32px 40px', width: '100%' }}>
        <ScrollReveal delay={100}>
          <h1 style={{ fontSize: 46, fontWeight: 800, color, letterSpacing: '-0.025em', lineHeight: 1.1, textShadow: '0 2px 16px rgba(255,255,255,0.5)' }}>{title}</h1>
        </ScrollReveal>
        <ScrollReveal delay={200}>
          <p style={{ fontSize: 16, color: '#3D3A35', marginTop: 8, textShadow: '0 1px 8px rgba(255,255,255,0.5)' }}>{subtitle}</p>
        </ScrollReveal>
      </div>
    </section>
  );
}
