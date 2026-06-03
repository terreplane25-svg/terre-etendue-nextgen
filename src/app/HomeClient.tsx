'use client';
import React from 'react';
import Link from 'next/link';
import ScrollReveal from '@/components/ui/ScrollReveal';
import BezelCard from '@/components/ui/BezelCard';
import Pill from '@/components/ui/Pill';
import { getArticleImage } from '@/lib/article-images';

const C = { lavender: '#7C6FC4', saffron: '#C48A2E', opal: '#3A8F6E', cyan: '#3580C0', rose: '#B85460' };

function Spark({ data, color }: { data: number[]; color: string }) {
  const max = Math.max(...data), min = Math.min(...data), r = max - min || 1;
  const pts = data.map((v, i) => `${(i / (data.length - 1)) * 100},${28 - ((v - min) / r) * 24 - 2}`).join(' ');
  return <svg width={100} height={28} viewBox="0 0 100 28"><polyline points={pts} fill="none" stroke={color} strokeWidth="2" strokeLinecap="round" /></svg>;
}

const PILLARS = [
  { id: 'headquarters', name: 'Le Centre de Recherche', sub: 'Épistémologie & Méthode', num: '01', c: C.lavender, href: '/headquarters', img: 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/livres_ia.jpg' },
  { id: 'observatory', name: "L'Observatoire", sub: 'Données empiriques', num: '02', c: C.cyan, href: '/observatory', img: 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/imgage_accueil.png' },
  { id: 'library', name: 'La Bibliothèque', sub: 'Sources sacrées', num: '03', c: C.saffron, href: '/library', img: 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/architecture-brutaliste-batiment-marais-scaled.jpg' },
  { id: 'lab', name: 'Outils & Simulateurs', sub: 'Modélisation & Calcul', num: '04', c: C.opal, href: '/lab', img: 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2025/10/cropped-entete-logo-e1760704486721.png' },
  { id: 'experiences', name: 'Les Expériences', sub: 'Physique naturelle', num: '05', c: C.rose, href: '/experiences', img: 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/tanrica-medical-laboratory-9839358_1920.png' },
];

interface HomeProps {
  counts: { total: number; headquarters: number; observatory: number; library: number; lab: number; experiments: number };
  recent: { slug: string; title: string; category: string; tags: string[]; pinned: boolean; readTime: number; description?: string }[];
}

export default function HomeClient({ counts, recent }: HomeProps) {
  const pillarCount = (id: string) => id === 'headquarters' ? counts.headquarters : id === 'observatory' ? counts.observatory : id === 'library' ? counts.library : id === 'lab' ? counts.lab : counts.experiments;

  return (
    <div>
      {/* HERO */}
      <section style={{ position: 'relative', minHeight: '82vh', display: 'flex', alignItems: 'flex-end', overflow: 'hidden' }}>
        <img src="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/fond_horizon.jpg"
          alt="" style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover', objectPosition: 'center 60%' }} />
        <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(250,250,246,0.92) 0%, transparent 50%)' }} />
        <div style={{ position: 'relative', maxWidth: 1100, margin: '0 auto', padding: '0 32px 80px', width: '100%' }}>
          <ScrollReveal delay={200}><Pill>Revue indépendante de cosmologie</Pill></ScrollReveal>
          <ScrollReveal delay={350}>
            <h1 style={{ fontSize: 60, fontWeight: 800, lineHeight: 1.05, marginTop: 20, letterSpacing: '-0.03em', maxWidth: 700 }}>
              Observer. Questionner.<br /><span style={{ color: C.lavender }}>Comprendre.</span>
            </h1>
          </ScrollReveal>
          <ScrollReveal delay={500}>
            <p style={{ fontSize: 17, color: '#3D3A35', maxWidth: 440, marginTop: 20, lineHeight: 1.65 }}>
              Examen critique du modèle cosmologique standard à travers les données empiriques, les sources sacrées et l'expérimentation directe.
            </p>
          </ScrollReveal>
        </div>
      </section>

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 32px' }}>
        {/* KPIs */}
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginTop: -40, position: 'relative', zIndex: 5 }}>
          {[
            { l: 'Publications', v: String(counts.total), s: [8,12,18,25,35,48,counts.total], c: C.lavender },
            { l: 'Sources', v: '450+', s: [40,80,150,250,350,420,450], c: C.saffron },
            { l: 'Observations', v: '11K', s: [2,3,5,6,8,10,11], c: C.opal },
            { l: 'Modèles 3D', v: '3', s: [0,0,1,1,2,3,3], c: C.cyan },
          ].map((k, i) => (
            <ScrollReveal key={k.l} delay={100 + i * 80}>
              <BezelCard>
                <div style={{ padding: '22px 24px' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 10 }}>
                    <div style={{ width: 7, height: 7, borderRadius: 99, background: k.c }} />
                    <span style={{ fontSize: 10, fontWeight: 700, color: '#8A857D', letterSpacing: '0.1em', textTransform: 'uppercase' as const }}>{k.l}</span>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'flex-end', justifyContent: 'space-between' }}>
                    <span style={{ fontSize: 34, fontWeight: 800, letterSpacing: '-0.02em' }}>{k.v}</span>
                    <Spark data={k.s} color={k.c} />
                  </div>
                </div>
              </BezelCard>
            </ScrollReveal>
          ))}
        </div>

        {/* PILIERS */}
        <div style={{ padding: '80px 0 40px' }}>
          <ScrollReveal>
            <Pill>Architecture du savoir</Pill>
            <h2 style={{ fontSize: 40, fontWeight: 800, marginTop: 12, letterSpacing: '-0.02em' }}>Les cinq piliers</h2>
          </ScrollReveal>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 18, marginTop: 36 }}>
            {PILLARS.map((p, i) => (
              <ScrollReveal key={p.id} delay={100 + i * 80}>
                <Link href={p.href}><BezelCard>
                  <div style={{ cursor: 'pointer' }}>
                    <div style={{ height: 180, overflow: 'hidden' }}>
                      <img src={p.img} alt={p.name} style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                    </div>
                    <div style={{ padding: '22px 26px' }}>
                      <Pill color={p.c}>{p.num}</Pill>
                      <h3 style={{ fontSize: 19, fontWeight: 750, marginTop: 10, letterSpacing: '-0.01em' }}>{p.name}</h3>
                      <p style={{ fontSize: 14, color: '#8A857D', marginTop: 4 }}>{p.sub}</p>
                      <p style={{ fontSize: 12, color: '#BAB5AC', marginTop: 12 }}>{pillarCount(p.id)} publications</p>
                    </div>
                  </div>
                </BezelCard></Link>
              </ScrollReveal>
            ))}
          </div>
        </div>

        {/* RECENT */}
        <div style={{ padding: '40px 0 100px' }}>
          <ScrollReveal>
            <Pill>Dernières publications</Pill>
            <h2 style={{ fontSize: 36, fontWeight: 800, marginTop: 12, letterSpacing: '-0.02em' }}>À lire</h2>
          </ScrollReveal>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 16, marginTop: 32 }}>
            {recent.map((a, i) => (
              <ScrollReveal key={a.slug} delay={80 + i * 60}>
                <Link href={`/article/${a.slug}`}><BezelCard>
                  <div style={{ display: 'flex', cursor: 'pointer' }}>
                    <div style={{ width: 200, minHeight: 150, flexShrink: 0, overflow: 'hidden' }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                    </div>
                    <div style={{ padding: '24px 28px', flex: 1, minWidth: 0 }}>
                      <h3 style={{ fontSize: 18, fontWeight: 700, letterSpacing: '-0.01em', lineHeight: 1.3, marginBottom: 8 }}>{a.title}</h3>
                      {a.description && <p style={{ fontSize: 14, color: '#8A857D', lineHeight: 1.55, marginBottom: 10, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any }}>{a.description}</p>}
                      <span style={{ fontSize: 11, color: '#BAB5AC', fontFamily: "'JetBrains Mono', monospace" }}>Terre Etendue · {a.readTime} min</span>
                    </div>
                  </div>
                </BezelCard></Link>
              </ScrollReveal>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
