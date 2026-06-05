'use client';

import React, { useState, useEffect, useRef, useCallback } from 'react';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Pill from '@/components/ui/Pill';
import { Gallery4 } from '@/components/ui/gallery4';
import DisplayCards from '@/components/ui/display-cards';
import { getArticleImage } from '@/lib/article-images';
import OceanScene from '@/components/ui/ocean-scene';

const CL = { lavender: '#7C6FC4', saffron: '#C48A2E', opal: '#3A8F6E', cyan: '#3580C0', rose: '#B85460' };
const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

function Spark({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data), min = Math.min(...data), r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * 100},${28 - ((v - min) / r) * 24 - 2}`).join(' ');
  return <svg width={100} height={28} viewBox="0 0 100 28"><polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" /></svg>;
}

function BezelKPI({ label, value, spark, color, delay }: { label: string; value: string; spark: number[]; color: string; delay: number }) {
  return (
    <ScrollReveal delay={delay}>
      <div style={{ background: '#F5F3EE', border: '1px solid rgba(20,18,16,0.06)', borderRadius: 24, padding: 6 }}>
        <div style={{ background: '#fff', borderRadius: 20, padding: '22px 24px', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
            <div style={{ width: 7, height: 7, borderRadius: 99, background: color }} />
            <span style={{ fontSize: 10, fontWeight: 700, color: '#8A857D', letterSpacing: '0.1em', textTransform: 'uppercase' as const }}>{label}</span>
          </div>
          <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
            <span style={{ fontSize: 34, fontWeight: 800, letterSpacing: '-0.02em', color: '#141210' }}>{value}</span>
            <Spark data={spark} color={color} />
          </div>
        </div>
      </div>
    </ScrollReveal>
  );
}

function Hero({ onSiteReady }: { onSiteReady: () => void }) {
  const [phase, setPhase] = useState<'recede'|'prompt'|'zoom'|'revealed'|'site'>('recede');
  const [recedeP, setRecedeP] = useState(0);
  const [zoomP, setZoomP] = useState(0);
  const [touchY, setTouchY] = useState(0);
  const animRef = useRef<number>(0);

  // Phase 1: auto-recede 6.5s
  useEffect(() => {
    const start = Date.now();
    const dur = 6500;
    const anim = () => {
      const t = Math.min((Date.now() - start) / dur, 1);
      setRecedeP(1 - Math.pow(1 - t, 2.5));
      if (t < 1) animRef.current = requestAnimationFrame(anim);
      else setTimeout(() => setPhase('prompt'), 800);
    };
    animRef.current = requestAnimationFrame(anim);
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  // Scroll phases 2-4
  useEffect(() => {
    if (phase !== 'prompt' && phase !== 'zoom' && phase !== 'revealed') return;
    const wheel = (e: WheelEvent) => {
      e.preventDefault();
      if (phase === 'revealed' && zoomP >= 1 && e.deltaY > 0) { setPhase('site'); onSiteReady(); return; }
      const next = Math.min(Math.max(zoomP + e.deltaY * 0.0008, 0), 1);
      setZoomP(next);
      if (next > 0.01 && phase === 'prompt') setPhase('zoom');
      if (next >= 1 && phase !== 'revealed') setPhase('revealed');
      if (next < 0.95 && phase === 'revealed') setPhase('zoom');
    };
    const ts = (e: TouchEvent) => setTouchY(e.touches[0].clientY);
    const tm = (e: TouchEvent) => {
      if (!touchY) return; e.preventDefault();
      const dy = touchY - e.touches[0].clientY;
      if (phase === 'revealed' && zoomP >= 1 && dy > 20) { setPhase('site'); onSiteReady(); return; }
      const next = Math.min(Math.max(zoomP + dy * 0.004, 0), 1);
      setZoomP(next);
      if (next > 0.01 && phase === 'prompt') setPhase('zoom');
      if (next >= 1 && phase !== 'revealed') setPhase('revealed');
      if (next < 0.95 && phase === 'revealed') setPhase('zoom');
      setTouchY(e.touches[0].clientY);
    };
    const sc = () => { window.scrollTo(0, 0); };
    window.addEventListener('wheel', wheel, { passive: false });
    window.addEventListener('touchstart', ts, { passive: false });
    window.addEventListener('touchmove', tm, { passive: false });
    window.addEventListener('scroll', sc);
    return () => { window.removeEventListener('wheel', wheel); window.removeEventListener('touchstart', ts); window.removeEventListener('touchmove', tm); window.removeEventListener('scroll', sc); };
  }, [phase, zoomP, touchY, onSiteReady]);

  const shipScale = phase === 'recede' ? Math.pow(1 - recedeP, 2) * 0.7 : Math.pow(zoomP, 1.2);
  const isSite = phase === 'site';

  return (
    <section style={{
      position: isSite ? 'relative' : 'fixed', inset: 0, width: '100%', height: '100vh',
      overflow: 'hidden', zIndex: 30,
      opacity: isSite ? 0 : 1, transform: isSite ? 'translateY(-80px)' : 'translateY(0)',
      transition: `all 0.9s ${BEZ}`, pointerEvents: isSite ? 'none' : 'auto',
      background: '#050910',
    }}>
      <OceanScene shipScale={shipScale} showVignette={phase === 'zoom' || phase === 'revealed'} zoomLevel={zoomP} />

      {/* Phase recede: watching */}
      {phase === 'recede' && recedeP < 0.25 && (
        <div style={{ position: 'absolute', top: 40, left: '50%', transform: 'translateX(-50%)', zIndex: 20, opacity: 1 - recedeP * 5 }}>
          <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.4)', fontFamily: "'JetBrains Mono',monospace", letterSpacing: '0.08em' }}>Observez le navire s&apos;éloigner...</p>
        </div>
      )}

      {/* Phase prompt: disappeared */}
      {(phase === 'prompt' || (phase === 'zoom' && zoomP < 0.1)) && (
        <div style={{ position: 'absolute', inset: 0, display: 'flex', alignItems: 'center', justifyContent: 'center', zIndex: 20, opacity: phase === 'prompt' ? 1 : Math.max(0, 1 - zoomP * 12) }}>
          <p style={{ fontSize: 30, fontWeight: 700, color: '#F0EDE6', letterSpacing: '-0.02em', textShadow: '0 3px 24px rgba(0,0,0,0.6)', textAlign: 'center', padding: '0 24px' }}>Le navire a disparu à l&apos;horizon...</p>
        </div>
      )}

      {/* Phase zoom: mid */}
      {phase === 'zoom' && zoomP >= 0.1 && zoomP < 0.8 && (
        <div style={{ position: 'absolute', bottom: 80, left: '50%', transform: 'translateX(-50%)', zIndex: 20, opacity: Math.min(0.6, (zoomP - 0.1) * 2.5) * (1 - Math.max(0, (zoomP - 0.65) / 0.15)) }}>
          <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.5)', fontFamily: "'JetBrains Mono',monospace", letterSpacing: '0.04em', textAlign: 'center' }}>L&apos;objet grandit uniformément — il était toujours là, entier.</p>
        </div>
      )}

      {/* Phase revealed */}
      {phase === 'revealed' && (
        <div style={{ position: 'absolute', bottom: 50, left: '50%', transform: 'translateX(-50%)', zIndex: 20, textAlign: 'center', maxWidth: 620, padding: '0 24px' }}>
          <p style={{ fontSize: 19, fontWeight: 600, color: '#F0EDE6', lineHeight: 1.65, textShadow: '0 2px 16px rgba(0,0,0,0.5)' }}>
            Le navire n&apos;avait pas disparu derrière une courbure.<br />
            <span style={{ color: CL.lavender }}>Sa taille apparente était simplement devenue trop petite pour l&apos;œil humain.</span>
          </p>
          <p style={{ fontSize: 11, color: 'rgba(255,255,255,0.3)', fontFamily: "'JetBrains Mono',monospace", marginTop: 24 }}>↓ Continuer</p>
        </div>
      )}

      {/* Scroll prompt */}
      {phase === 'prompt' && (
        <div style={{ position: 'absolute', bottom: 36, left: '50%', transform: 'translateX(-50%)', zIndex: 20, textAlign: 'center' }}>
          <p style={{ fontSize: 12, color: 'rgba(255,255,255,0.4)', fontFamily: "'JetBrains Mono',monospace", letterSpacing: '0.08em', textTransform: 'uppercase' as const }}>Scrollez pour regarder de plus près</p>
          <div style={{ width: 1, height: 28, background: 'linear-gradient(to bottom, rgba(255,255,255,0.25), transparent)', margin: '10px auto 0' }} />
        </div>
      )}

      {/* Progress */}
      {(phase === 'zoom' || phase === 'prompt') && (
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 3, background: 'rgba(255,255,255,0.05)', zIndex: 20 }}>
          <div style={{ height: '100%', width: `${zoomP * 100}%`, background: CL.lavender, borderRadius: 99 }} />
        </div>
      )}
    </section>
  );
}

interface HomeProps {
  counts: { total: number; headquarters: number; observatory: number; library: number; lab: number; experiments: number };
  obsArticles: { id: string; title: string; description: string; href: string; image: string }[];
  expArticles: { id: string; title: string; description: string; href: string; image: string }[];
  libArticles: { id: string; title: string; description: string; href: string; image: string }[];
}

export default function HomeClient({ counts, obsArticles, expArticles, libArticles }: HomeProps) {
  const [siteVisible, setSiteVisible] = useState(false);
  const addImg = (a: { id: string; title: string; description: string; href: string; image: string }) => ({ ...a, image: getArticleImage(a.id) || a.image });
  const handleSiteReady = useCallback(() => setSiteVisible(true), []);

  const aLaUne = [
    { title: 'Début de la Création : Selon le Coran et la Sunna', description: 'Sources coraniques et prophétiques sur la cosmologie', date: 'Bibliothèque · Lecture prioritaire', color: CL.saffron, icon: '📖' },
    { title: 'Pourquoi tout remettre en question', description: 'Épistémologie du doute méthodique', date: 'Centre de Recherche · Fondamental', color: CL.lavender, icon: '◎' },
    { title: "L'horizon, la perspective et la réfraction", description: 'Trois expériences reproductibles', date: 'Observatoire · 18 min', color: CL.cyan, icon: '🔭' },
  ];

  return (
    <div style={{ background: siteVisible ? '#FAFAF6' : '#050910', transition: `background 0.8s ${BEZ}` }}>
      <Hero onSiteReady={handleSiteReady} />
      <div style={{
        opacity: siteVisible ? 1 : 0, transform: siteVisible ? 'translateY(0)' : 'translateY(60px)',
        transition: `all 0.9s ${BEZ}`, background: '#FAFAF6', minHeight: '100vh',
        paddingTop: siteVisible ? 0 : '100vh',
      }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 32px 0' }}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 60 }}>
            <BezelKPI label="Publications" value={String(counts.total)} spark={[8,12,18,25,35,48,counts.total]} color={CL.lavender} delay={100} />
            <BezelKPI label="Sources" value="450+" spark={[40,80,150,250,350,420,450]} color={CL.saffron} delay={180} />
            <BezelKPI label="Observations" value="11K" spark={[2,3,5,6,8,10,11]} color={CL.opal} delay={260} />
            <BezelKPI label="Modèles 3D" value="3" spark={[0,0,1,1,2,3,3]} color={CL.cyan} delay={340} />
          </div>
          <ScrollReveal><Pill>En ce moment</Pill><h2 style={{ fontSize: 38, fontWeight: 800, marginTop: 12, letterSpacing: '-0.02em' }}>À la une</h2></ScrollReveal>
          <ScrollReveal delay={150}><DisplayCards cards={aLaUne} /></ScrollReveal>
        </div>
        <ScrollReveal><Gallery4 title="L'Observatoire" description="Analyses empiriques et observations documentées" items={obsArticles.map(addImg)} color={CL.cyan} /></ScrollReveal>
        <ScrollReveal><Gallery4 title="Les Expériences" description="Fiches pédagogiques avec protocoles reproductibles" items={expArticles.map(addImg)} color={CL.rose} /></ScrollReveal>
        <ScrollReveal><Gallery4 title="La Bibliothèque" description="Sources sacrées et textes historiques" items={libArticles.map(addImg)} color={CL.saffron} /></ScrollReveal>
      </div>
    </div>
  );
}
