'use client';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';

interface PageHeroProps {
  title: string;
  subtitle: string;
  color: string;
  image: string;
}

export default function PageHero({ title, subtitle, color, image }: PageHeroProps) {
  return (
    <motion.section initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.7 }}
      style={{ position: 'relative', overflow: 'hidden', height: 300, display: 'flex', alignItems: 'flex-end', marginBottom: 32 }}>
      <img src={image} alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(244,245,247,0.92) 0%, rgba(244,245,247,0.25) 55%, rgba(0,0,0,0.02) 100%)' }} />
      <div style={{ position: 'relative', maxWidth: 1200, margin: '0 auto', padding: '0 24px 32px', width: '100%' }}>
        <h1 style={{ fontSize: 34, fontWeight: 800, color, marginBottom: 6, lineHeight: 1.2 }}>{title}</h1>
        <p style={{ fontSize: 15, color: dash.inkMuted }}>{subtitle}</p>
      </div>
    </motion.section>
  );
}
