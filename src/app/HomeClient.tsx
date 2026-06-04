'use client';

import React, { useState, useEffect } from 'react';
import ScrollReveal from '@/components/ui/ScrollReveal';
import Pill from '@/components/ui/Pill';
import { Gallery4 } from '@/components/ui/gallery4';
import DisplayCards from '@/components/ui/display-cards';
import { getArticleImage } from '@/lib/article-images';

const C = { lavender: '#7C6FC4', saffron: '#C48A2E', opal: '#3A8F6E', cyan: '#3580C0', rose: '#B85460' };
const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

// ═══════════════════════════════════════
// SCROLL EXPAND HERO — zoom reveal animation
// A distant object (lighthouse) is invisible at first,
// then progressively appears as you "zoom in" by scrolling
// ═══════════════════════════════════════
function Hero({ onDone }: { onDone: () => void }) {
  const [p, setP] = useState(0);
  const [done, setDone] = useState(false);
  const [touchY, setTouchY] = useState(0);

  useEffect(() => {
    const wheel = (e: WheelEvent) => {
      if (done && e.deltaY < 0 && window.scrollY <= 5) { setDone(false); e.preventDefault(); }
      else if (!done) { e.preventDefault(); const n = Math.min(Math.max(p + e.deltaY * 0.001, 0), 1); setP(n); if (n >= 1) { setDone(true); onDone(); } }
    };
    const ts = (e: TouchEvent) => setTouchY(e.touches[0].clientY);
    const tm = (e: TouchEvent) => {
      if (!touchY) return; const dy = touchY - e.touches[0].clientY;
      if (done && dy < -20 && window.scrollY <= 5) { setDone(false); e.preventDefault(); }
      else if (!done) { e.preventDefault(); const n = Math.min(Math.max(p + dy * 0.005, 0), 1); setP(n); if (n >= 1) { setDone(true); onDone(); } setTouchY(e.touches[0].clientY); }
    };
    const sc = () => { if (!done) window.scrollTo(0, 0); };
    window.addEventListener('wheel', wheel, { passive: false });
    window.addEventListener('touchstart', ts, { passive: false });
    window.addEventListener('touchmove', tm, { passive: false });
    window.addEventListener('scroll', sc);
    return () => { window.removeEventListener('wheel', wheel); window.removeEventListener('touchstart', ts); window.removeEventListener('touchmove', tm); window.removeEventListener('scroll', sc); };
  }, [p, done, touchY, onDone]);

  const w = 340 + p * 1200;
  const h = 400 + p * 420;
  const tx = p * 130;
  const zoom = 1 + p * 4;

  // Lighthouse/ship reveal parameters
  const objectOpacity = Math.max(0, (p - 0.25) / 0.75); // starts appearing at 25% scroll
  const objectScale = 0.15 + p * 0.85; // grows from tiny to full
  const lensOpacity = p < 0.85 ? Math.min(1, p * 2) * (1 - Math.max(0, (p - 0.7) / 0.3)) : 0;

  return (
    <section style={{ position: 'relative', minHeight: '100vh', display: 'flex', alignItems: 'center', justifyContent: 'center', overflow: 'hidden', background: '#060a10' }}>
      {/* Static background — ocean horizon */}
      <div style={{
        position: 'absolute', inset: 0,
        opacity: 1 - p * 0.6,
        backgroundImage: 'url(https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/horizon_mer.jpg)',
        backgroundSize: 'cover', backgroundPosition: 'center 65%',
        filter: `brightness(${0.45 + p * 0.2})`,
      }} />

      {/* Expanding rectangle — the "telescope view" */}
      <div style={{
        position: 'absolute', top: '50%', left: '50%',
        transform: 'translate(-50%,-50%)',
        width: Math.min(w, 1500), height: Math.min(h, 850),
        maxWidth: '96vw', maxHeight: '88vh',
        borderRadius: 20 - p * 12, overflow: 'hidden',
        boxShadow: `0 0 ${30 + p * 50}px rgba(0,0,0,0.5)`,
        border: `${2 - p * 1.5}px solid rgba(255,255,255,${0.15 - p * 0.1})`,
      }}>
        {/* Ocean/horizon that zooms */}
        <div style={{
          width: '100%', height: '100%', position: 'absolute', inset: 0,
          backgroundImage: 'url(https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/horizon_mer.jpg)',
          backgroundSize: 'cover',
          backgroundPosition: `center ${58 - p * 15}%`,
          transform: `scale(${zoom})`,
          transformOrigin: 'center 58%',
        }} />

        {/* Dark overlay that fades */}
        <div style={{ position: 'absolute', inset: 0, background: `rgba(6,10,16,${0.5 - p * 0.4})` }} />

        {/* ═══ THE REVEAL: Lighthouse/ship SVG that appears with zoom ═══ */}
        <div style={{
          position: 'absolute',
          top: '38%', left: '50%',
          transform: `translate(-50%, -50%) scale(${objectScale})`,
          opacity: objectOpacity,
          transition: 'none',
          filter: `blur(${Math.max(0, (1 - p) * 3)}px)`,
        }}>
          <svg width="120" height="200" viewBox="0 0 120 200" fill="none">
            {/* Lighthouse body */}
            <rect x="42" y="40" width="36" height="130" rx="2" fill="#E8E0D0" stroke="#8A857D" strokeWidth="1"/>
            <rect x="38" y="40" width="44" height="12" rx="1" fill="#C45E6A" opacity="0.8"/>
            <rect x="38" y="72" width="44" height="8" rx="1" fill="#C45E6A" opacity="0.6"/>
            <rect x="38" y="100" width="44" height="8" rx="1" fill="#C45E6A" opacity="0.6"/>
            <rect x="38" y="128" width="44" height="8" rx="1" fill="#C45E6A" opacity="0.4"/>
            {/* Lighthouse top */}
            <rect x="45" y="20" width="30" height="20" rx="2" fill="#1A1D23"/>
            <rect x="48" y="22" width="24" height="16" rx="1" fill="#FFD700" opacity={0.5 + p * 0.5}/>
            {/* Light beam */}
            <path d={`M60 30 L${10 + p * 20} ${-20 - p * 30} L${110 - p * 20} ${-20 - p * 30} Z`} fill="#FFD700" opacity={p * 0.25}/>
            {/* Lighthouse cap */}
            <polygon points="40,20 60,5 80,20" fill="#3D3A35"/>
            {/* Base / rocks */}
            <ellipse cx="60" cy="172" rx="50" ry="12" fill="#5A5448" opacity="0.6"/>
            <rect x="30" y="160" width="60" height="14" rx="3" fill="#8A857D"/>
            {/* Water line */}
            <path d="M0 175 Q20 170, 40 175 Q60 180, 80 175 Q100 170, 120 175" stroke="#3580C0" strokeWidth="2" fill="none" opacity="0.4"/>
            <path d="M0 182 Q30 177, 60 182 Q90 187, 120 182" stroke="#3580C0" strokeWidth="1.5" fill="none" opacity="0.3"/>
          </svg>
        </div>

        {/* Zoom level indicator */}
        <div style={{
          position: 'absolute', bottom: 16, right: 20,
          fontFamily: "'JetBrains Mono', monospace",
          fontSize: 12, color: 'rgba(255,255,255,0.5)',
          opacity: p > 0.05 ? 1 : 0,
        }}>
          ×{zoom.toFixed(1)}
        </div>

        {/* Magnifying lens overlay */}
        {lensOpacity > 0 && (
          <div style={{
            position: 'absolute', inset: 0,
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            opacity: lensOpacity,
            pointerEvents: 'none',
          }}>
            <div style={{
              width: 90 + p * 250, height: 90 + p * 250,
              border: '1.5px solid rgba(255,255,255,0.2)',
              borderRadius: '50%',
            }}>
              {/* Crosshair */}
              <div style={{ position: 'absolute', top: '50%', left: '25%', right: '25%', height: 1, background: 'rgba(255,255,255,0.12)' }} />
              <div style={{ position: 'absolute', left: '50%', top: '25%', bottom: '25%', width: 1, background: 'rgba(255,255,255,0.12)' }} />
            </div>
          </div>
        )}

        {/* Text labels that appear during zoom */}
        {p > 0.15 && p < 0.6 && (
          <div style={{
            position: 'absolute', bottom: 50, left: '50%', transform: 'translateX(-50%)',
            textAlign: 'center', opacity: Math.min(1, (p - 0.15) * 4) * (1 - Math.max(0, (p - 0.45) / 0.15)),
          }}>
            <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.6)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.08em' }}>
              Le phare a « disparu » sous l&apos;horizon...
            </p>
          </div>
        )}
        {p > 0.65 && (
          <div style={{
            position: 'absolute', bottom: 50, left: '50%', transform: 'translateX(-50%)',
            textAlign: 'center', opacity: Math.min(1, (p - 0.65) * 4),
          }}>
            <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.06em', fontWeight: 600 }}>
              Un zoom suffisant le ramène.
            </p>
          </div>
        )}
      </div>

      {/* Split title */}
      <div style={{ position: 'relative', zIndex: 10, textAlign: 'center', display: 'flex', flexDirection: 'column', alignItems: 'center', gap: 8 }}>
        <h2 style={{ fontSize: 68, fontWeight: 800, color: '#F5F3EE', letterSpacing: '-0.04em', textShadow: '0 4px 32px rgba(0,0,0,0.6)', transform: `translateX(-${tx}vw)`, fontFamily: "'Plus Jakarta Sans', system-ui" }}>Observer.</h2>
        <h2 style={{ fontSize: 68, fontWeight: 800, color: C.lavender, letterSpacing: '-0.04em', textShadow: '0 4px 32px rgba(0,0,0,0.6)', transform: `translateX(${tx}vw)`, fontFamily: "'Plus Jakarta Sans', system-ui" }}>Comprendre.</h2>
      </div>

      {/* Scroll hint */}
      {!done && p < 0.2 && (
        <div style={{ position: 'absolute', bottom: 40, left: '50%', transform: 'translateX(-50%)', zIndex: 10, textAlign: 'center', opacity: 1 - p * 6 }}>
          <div style={{ fontSize: 11, color: '#F5F3EE70', fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.12em', textTransform: 'uppercase' }}>Scroll pour zoomer</div>
          <div style={{ width: 1, height: 28, background: 'linear-gradient(to bottom, #F5F3EE40, transparent)', margin: '8px auto 0' }} />
        </div>
      )}

      {/* Progress bar */}
      {!done && (
        <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, height: 3, background: '#ffffff10' }}>
          <div style={{ height: '100%', width: `${p * 100}%`, background: C.lavender, borderRadius: 99 }} />
        </div>
      )}
    </section>
  );
}

// ═══ SPARKLINE ═══
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

// ═══ PROPS ═══
interface HomeProps {
  counts: { total: number; headquarters: number; observatory: number; library: number; lab: number; experiments: number };
  obsArticles: { id: string; title: string; description: string; href: string; image: string }[];
  expArticles: { id: string; title: string; description: string; href: string; image: string }[];
  libArticles: { id: string; title: string; description: string; href: string; image: string }[];
}

export default function HomeClient({ counts, obsArticles, expArticles, libArticles }: HomeProps) {
  const [expanded, setExpanded] = useState(false);
  const addImg = (a: any) => ({ ...a, image: getArticleImage(a.id) || a.image });

  // ── "À la une" — 3 specific articles ──
  const aLaUne = [
    { title: 'Début de la Création : Selon le Coran et la Sunna', description: 'Sources coraniques et prophétiques sur la cosmologie', date: 'Bibliothèque · Lecture prioritaire', color: C.saffron, icon: '📖' },
    { title: 'Pourquoi tout remettre en question', description: 'Épistémologie du doute méthodique appliquée au modèle standard', date: 'Centre de Recherche · Fondamental', color: C.lavender, icon: '◎' },
    { title: "L'horizon, la perspective et la réfraction", description: 'Trois expériences reproductibles pour comprendre l\'horizon', date: 'Observatoire · 18 min', color: C.cyan, icon: '🔭' },
  ];

  return (
    <div style={{ background: expanded ? '#FAFAF6' : '#060a10', transition: `background 0.7s ${BEZ}` }}>
      <Hero onDone={() => setExpanded(true)} />

      <div style={{ opacity: expanded ? 1 : 0, transform: expanded ? 'translateY(0)' : 'translateY(40px)', transition: `all 0.7s ${BEZ}`, background: '#FAFAF6' }}>
        <div style={{ maxWidth: 1100, margin: '0 auto', padding: '40px 32px 0' }}>
          {/* KPIs */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 60 }}>
            <BezelKPI label="Publications" value={String(counts.total)} spark={[8,12,18,25,35,48,counts.total]} color={C.lavender} delay={100} />
            <BezelKPI label="Sources" value="450+" spark={[40,80,150,250,350,420,450]} color={C.saffron} delay={180} />
            <BezelKPI label="Observations" value="11K" spark={[2,3,5,6,8,10,11]} color={C.opal} delay={260} />
            <BezelKPI label="Modèles 3D" value="3" spark={[0,0,1,1,2,3,3]} color={C.cyan} delay={340} />
          </div>

          {/* À la une — 3 specific articles */}
          <ScrollReveal><Pill>En ce moment</Pill><h2 style={{ fontSize: 38, fontWeight: 800, marginTop: 12, letterSpacing: '-0.02em' }}>À la une</h2></ScrollReveal>
          <ScrollReveal delay={150}><DisplayCards cards={aLaUne} /></ScrollReveal>
        </div>

        {/* Gallery4 — Observatoire */}
        <ScrollReveal>
          <Gallery4 title="L'Observatoire" description="Analyses empiriques et observations documentées" items={obsArticles.map(addImg)} color={C.cyan} />
        </ScrollReveal>

        {/* Gallery4 — Expériences */}
        <ScrollReveal>
          <Gallery4 title="Les Expériences" description="Fiches pédagogiques avec protocoles reproductibles" items={expArticles.map(addImg)} color={C.rose} />
        </ScrollReveal>

        {/* Gallery4 — Bibliothèque */}
        <ScrollReveal>
          <Gallery4 title="La Bibliothèque" description="Sources sacrées et textes historiques" items={libArticles.map(addImg)} color={C.saffron} />
        </ScrollReveal>
      </div>
    </div>
  );
}
