'use client';
import React from 'react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';
import ArticleCarousel from '@/components/ArticleCarousel';

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

const PILLARS = [
  { label: 'Bibliothèque', desc: 'Coran, Sunna, patrimoine islamique', icon: '📖', href: '/library', color: '#D4943A' },
  { label: 'Centre de Recherche', desc: 'Épistémologie et méthode', icon: '🧠', href: '/headquarters', color: '#8B7EC8' },
  { label: 'Observatoire', desc: 'Données empiriques et optique', icon: '🔭', href: '/observatory', color: '#3B8FD4' },
  { label: 'Expériences', desc: 'Physique et phénomènes naturels', icon: '⚗️', href: '/experiences', color: '#C45E6A' },
  { label: 'Simulateurs', desc: '7 outils interactifs 3D', icon: '🗺️', href: '/lab', color: '#3D9E7C' },
  { label: 'Laboratoire', desc: 'Analyse de médias et méthode', icon: '🔬', href: '/laboratoire', color: '#8B7EC8' },
];

function fmtDate(d: string) {
  try { return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }); }
  catch { return ''; }
}

export default function HomeClient({ articles }: { articles: A[] }) {
  const nonIslamic = articles.filter(a => !ISLAMIC_SLUGS.includes(a.slug));
  const featured = nonIslamic.slice(0, 3);
  const latest = nonIslamic.slice(3, 15);

  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(135deg, rgba(13,21,40,0.88) 0%, rgba(26,37,64,0.82) 50%, rgba(13,21,40,0.92) 100%), url("https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/07/StockCake-Horizon_de_Lever_de_Soleil_Ethere-297875-standard.jpg") center/cover no-repeat',
        padding: '100px 24px 48px',
        borderBottom: '3px solid',
        borderImage: 'linear-gradient(90deg, #D4943A, #8B7EC8, #3B8FD4, #C45E6A, #3D9E7C) 1',
      }}>
        <div style={{ maxWidth: 960, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            fontSize: 11, fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase',
            color: '#3D9E7C', marginBottom: 16,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            Revue indépendante de cosmologie
          </div>
          <h1 style={{
            fontSize: 42, fontWeight: 900, color: '#E8EDF4', letterSpacing: '-0.02em',
            lineHeight: 1.15, marginBottom: 16,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}>
            Explorer la création,<br />honorer la Révélation
          </h1>
          <p style={{
            fontSize: 17, color: '#8A95A8', lineHeight: 1.65, maxWidth: 640,
            margin: '0 auto 32px',
          }}>
            Le Coran et la Sunna décrivent une cosmologie cohérente. La science moderne repose sur des hypothèses — certaines solides, d&apos;autres non vérifiables. Ce site examine les deux avec la même rigueur.
          </p>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fit, minmax(160px, 1fr))',
            gap: 10, maxWidth: 860, margin: '0 auto',
          }}>
            {PILLARS.map(p => (
              <Link key={p.href} href={p.href} style={{
                padding: '14px 12px', borderRadius: 8,
                background: 'rgba(255,255,255,0.04)',
                border: '1px solid rgba(255,255,255,0.08)',
                textAlign: 'center',
                transition: 'background 0.2s, border-color 0.2s',
              }}
              onMouseEnter={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.08)'; e.currentTarget.style.borderColor = p.color + '60'; }}
              onMouseLeave={e => { e.currentTarget.style.background = 'rgba(255,255,255,0.04)'; e.currentTarget.style.borderColor = 'rgba(255,255,255,0.08)'; }}
              >
                <div style={{ fontSize: 22, marginBottom: 6 }}>{p.icon}</div>
                <div style={{ fontSize: 13, fontWeight: 700, color: p.color, marginBottom: 2 }}>{p.label}</div>
                <div style={{ fontSize: 11, color: '#607890' }}>{p.desc}</div>
              </Link>
            ))}
          </div>
          <div style={{ marginTop: 24, display: 'flex', justifyContent: 'center', gap: 16 }}>
            <span style={{ fontSize: 12, color: '#607890', fontFamily: "'JetBrains Mono', monospace" }}>
              {articles.length} articles
            </span>
            <span style={{ fontSize: 12, color: '#3D4E60' }}>·</span>
            <span style={{ fontSize: 12, color: '#607890', fontFamily: "'JetBrains Mono', monospace" }}>
              7 simulateurs
            </span>
            <span style={{ fontSize: 12, color: '#3D4E60' }}>·</span>
            <span style={{ fontSize: 12, color: '#607890', fontFamily: "'JetBrains Mono', monospace" }}>
              Sources vérifiables
            </span>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '36px 24px 80px' }}>

      {/* ═══ À LA UNE ═══ */}
      <div style={{ marginBottom: 48 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div style={{ width: 4, height: 28, background: '#8B7EC8', borderRadius: 2 }} />
          <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>À la une</h2>
        </div>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20 }}>
          {featured.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{
              position: 'relative', borderRadius: 10, overflow: 'hidden',
              display: 'block', minHeight: 240,
            }}>
              <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 60%)' }} />
              <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '20px 18px' }}>
                <span style={{ fontSize: 10, fontWeight: 700, color: CAT_COLOR[a.category] || '#8B8F96', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {CAT_LABEL[a.category] || a.category}
                </span>
                <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff', lineHeight: 1.3, marginTop: 4 }}>{a.title}</h3>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)', marginTop: 6 }}>
                  {fmtDate(a.date)} · {a.readTime} min
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ═══ DERNIÈRES PUBLICATIONS ═══ */}
      <ArticleCarousel articles={latest} />
      </div>
    </div>
  );
}
