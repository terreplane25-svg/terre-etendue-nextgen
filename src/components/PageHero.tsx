'use client';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';

interface PageHeroProps {
  num: string;
  title: string;
  subtitle: string;
  color: string;
  image: string;
}

export default function PageHero({ num, title, subtitle, color, image }: PageHeroProps) {
  return (
    <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.7 }}
      style={{ position: 'relative', overflow: 'hidden', height: 240, display: 'flex', alignItems: 'flex-end', marginBottom: 32 }}>
      <img src={image} alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(244,245,247,0.98) 0%, rgba(244,245,247,0.55) 50%, rgba(244,245,247,0.15) 100%)' }} />
      <div style={{ position: 'relative', maxWidth: 1200, margin: '0 auto', padding: '0 24px 28px', width: '100%' }}>
        <div style={{ fontSize: 11, fontWeight: 700, color, letterSpacing: '0.1em', textTransform: 'uppercase', marginBottom: 6, fontFamily: dash.fontMono }}>{num}</div>
        <h1 style={{ fontSize: 30, fontWeight: 800, color: dash.ink, marginBottom: 4, lineHeight: 1.2 }}>{title}</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>{subtitle}</p>
      </div>
    </motion.section>
  );
}
