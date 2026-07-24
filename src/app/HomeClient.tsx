'use client';
import React from 'react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';
import ArticleCarousel from '@/components/ArticleCarousel';
import { TOOLS } from '@/lib/lab-tools';

interface A { slug: string; title: string; description: string; category: string; tags: string[]; readTime: number; date: string; pinned: boolean; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils', experiences: 'Expériences', meta: 'TEI' };
const CAT_COLOR: Record<string, string> = { headquarters: '#8B7EC8', observatory: '#3B8FD4', library: '#D4943A', lab: '#3D9E7C', experiences: '#C45E6A', meta: '#8B8F96' };

const ISLAMIC_SLUGS = [
  'debut-de-la-creation-selon-le-coran-et-la-sunna',
  'debut-de-la-creation-le-soleil-mobile-la-terre-immobile',
  'la-terre-dans-le-coran',
  'pres-de-cent-savants-de-lislam',
  'dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne',
  'la-qibla-et-la-direction-cote-ouest',
  'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
];

const PILIERS = [
  { href: '/library', label: 'Bibliothèque', color: '#D4943A', desc: 'Sources coraniques et hadiths, en édition critique savante.' },
  { href: '/headquarters', label: 'Centre de Recherche', color: '#8B7EC8', desc: 'L’épistémologie : distinguer ce qui est prouvé de ce qui est interprété.' },
  { href: '/observatory', label: 'Observatoire', color: '#3B8FD4', desc: 'Les données empiriques et officielles, examinées à la loupe.' },
  { href: '/experiences', label: 'Expériences', color: '#C45E6A', desc: 'La physique se vérifie à la main, chez soi, sans autorité à invoquer.' },
  { href: '/laboratoire', label: 'Laboratoire', color: '#3D9E7C', desc: 'Analyses d’observations longue distance, impossibles sur un globe.' },
];

function fmtDate(d: string) {
  try { return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }); }
  catch { return ''; }
}

function SectionTitle({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 28 }}>
      <div style={{ width: 5, height: 34, background: color, borderRadius: 2 }} />
      <h2 style={{ fontSize: 'clamp(1.6rem, 3vw, 2.25rem)', fontWeight: 800, color: 'var(--ink)', letterSpacing: '-0.02em', margin: 0 }}>{children}</h2>
    </div>
  );
}

export default function HomeClient({ articles }: { articles: A[] }) {
  const nonIslamic = articles.filter(a => !ISLAMIC_SLUGS.includes(a.slug));
  const featured = nonIslamic.slice(0, 3);
  const latest = nonIslamic.slice(3, 15);

  const stats = [
    { n: String(articles.length), label: 'Articles publiés' },
    { n: String(TOOLS.length), label: 'Simulateurs interactifs' },
    { n: String(PILIERS.length), label: 'Univers thématiques' },
    { n: '100 %', label: 'Sources vérifiables' },
  ];

  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(180deg, rgba(13,21,40,0.42) 0%, rgba(13,21,40,0.34) 45%, rgba(13,21,40,0.60) 100%), url("https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/07/StockCake-Horizon_de_Lever_de_Soleil_Ethere-297875-standard.jpg") center/cover no-repeat',
        padding: '132px 24px 104px',
        borderBottom: '3px solid',
        borderImage: 'linear-gradient(90deg, #D4943A, #8B7EC8, #3B8FD4, #C45E6A, #3D9E7C) 1',
      }}>
        <div style={{ maxWidth: 1120, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            display: 'inline-block',
            fontSize: 12, fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase',
            color: '#5CE0B0', marginBottom: 22,
            fontFamily: "'JetBrains Mono', monospace",
            background: 'rgba(13,21,40,0.55)', border: '1px solid rgba(92,224,176,0.35)',
            padding: '7px 16px', borderRadius: 100, backdropFilter: 'blur(4px)',
          }}>
            Revue indépendante de cosmologie
          </div>
          <h1 style={{
            fontSize: 'clamp(2.75rem, 6.5vw, 5rem)', fontWeight: 900, color: '#F4F8FC', letterSpacing: '-0.03em',
            lineHeight: 1.06, marginBottom: 26,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            textShadow: '0 2px 28px rgba(0,0,0,0.6)',
          }}>
            Explorer la création,<br />honorer la Révélation
          </h1>
          <p style={{
            fontSize: 'clamp(1.05rem, 1.6vw, 1.3rem)', color: '#E6ECF4', lineHeight: 1.6, maxWidth: 720,
            margin: '0 auto',
            textShadow: '0 1px 14px rgba(0,0,0,0.6)',
          }}>
            La cosmologie coranique et la science moderne, examinées avec la même rigueur.
          </p>
          <div style={{ marginTop: 38, display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
            <a href="#piliers" style={{
              fontSize: 15.5, fontWeight: 700, color: '#0D1528', background: '#4FD1A0',
              padding: '15px 30px', borderRadius: 10, boxShadow: '0 6px 24px rgba(79,209,160,0.35)',
            }}>
              Commencer l’exploration
            </a>
            <Link href="/about" style={{
              fontSize: 15.5, fontWeight: 700, color: '#F4F8FC', background: 'rgba(255,255,255,0.08)',
              padding: '15px 30px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.35)',
              backdropFilter: 'blur(4px)',
            }}>
              Lire le manifeste
            </Link>
          </div>
        </div>
      </div>

      {/* ═══ BANDE CHIFFRES (pleine largeur) ═══ */}
      <div style={{ background: 'var(--cream)', borderBottom: '1px solid var(--border)' }}>
        <div style={{
          maxWidth: 1200, margin: '0 auto', padding: '56px 24px',
          display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 32, textAlign: 'center',
        }}>
          {stats.map((s, i) => (
            <div key={i}>
              <div style={{
                fontSize: 'clamp(2.5rem, 5vw, 3.5rem)', fontWeight: 900, color: 'var(--ink)',
                letterSpacing: '-0.03em', lineHeight: 1, fontFamily: "'Plus Jakarta Sans', sans-serif",
              }}>{s.n}</div>
              <div style={{
                fontSize: 13, color: 'var(--ink-muted)', marginTop: 12, letterSpacing: '0.04em',
                textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace",
              }}>{s.label}</div>
            </div>
          ))}
        </div>
      </div>

      {/* ═══ PARCOURIR PAR PILIER (pleine largeur, tonalité foncée) ═══ */}
      <div id="piliers" style={{ background: '#0D1528', borderBottom: '1px solid #1a2540' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '96px 24px' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 12 }}>
            <div style={{ width: 5, height: 34, background: '#4FD1A0', borderRadius: 2 }} />
            <h2 style={{ fontSize: 'clamp(1.6rem, 3vw, 2.25rem)', fontWeight: 800, color: '#F4F8FC', letterSpacing: '-0.02em', margin: 0 }}>Parcourir par pilier</h2>
          </div>
          <p style={{ fontSize: 16, color: '#8fa0b8', lineHeight: 1.6, marginBottom: 40, maxWidth: 640 }}>
            Cinq univers pour aborder la même question sous cinq angles : le texte, la méthode, les données, l’expérience, l’analyse.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20 }}>
            {PILIERS.map(p => (
              <Link key={p.href} href={p.href} style={{
                display: 'block', padding: '30px 28px', borderRadius: 14,
                background: 'rgba(255,255,255,0.03)', border: '1px solid #1e2c48',
                borderTop: `3px solid ${p.color}`, transition: 'background 0.2s, transform 0.2s',
              }}>
                <div style={{ fontSize: 21, fontWeight: 800, color: '#F4F8FC', marginBottom: 10, letterSpacing: '-0.01em' }}>{p.label}</div>
                <p style={{ fontSize: 14.5, color: '#9fb0c8', lineHeight: 1.6, margin: 0 }}>{p.desc}</p>
                <div style={{ marginTop: 16, fontSize: 13.5, fontWeight: 700, color: p.color }}>Explorer →</div>
              </Link>
            ))}
          </div>
        </div>
      </div>

      {/* ═══ À LA UNE ═══ */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '96px 24px 0' }}>
        <SectionTitle color="#8B7EC8">À la une</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
          {featured.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{
              position: 'relative', borderRadius: 12, overflow: 'hidden',
              display: 'block', minHeight: 300,
            }}>
              <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.78) 0%, transparent 62%)' }} />
              <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '24px 22px' }}>
                <span style={{ fontSize: 10.5, fontWeight: 700, color: CAT_COLOR[a.category] || '#8B8F96', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {CAT_LABEL[a.category] || a.category}
                </span>
                <h3 style={{ fontSize: 20, fontWeight: 750, color: '#fff', lineHeight: 1.28, marginTop: 6 }}>{a.title}</h3>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)', marginTop: 8 }}>
                  {fmtDate(a.date)} · {a.readTime} min
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ═══ DERNIÈRES PUBLICATIONS ═══ */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '96px 24px 100px' }}>
        <SectionTitle color="#3B8FD4">Dernières publications</SectionTitle>
        <ArticleCarousel articles={latest} />
      </div>
    </div>
  );
}
