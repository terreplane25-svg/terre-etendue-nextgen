'use client';
import React from 'react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';

interface A { slug: string; title: string; description: string; category: string; tags: string[]; readTime: number; date: string; pinned: boolean; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils', meta: 'TEI' };
const CAT_COLOR: Record<string, string> = { headquarters: '#8B7EC8', observatory: '#3B8FD4', library: '#D4943A', lab: '#3D9E7C', meta: '#8B8F96' };

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
];

function fmtDate(d: string) {
  try { return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }); }
  catch { return ''; }
}

export default function HomeClient({ articles }: { articles: A[] }) {
  const islamicArticles = ISLAMIC_SLUGS.map(slug => articles.find(a => a.slug === slug)).filter(Boolean) as A[];
  const nonIslamic = articles.filter(a => !ISLAMIC_SLUGS.includes(a.slug));
  const featured = nonIslamic.slice(0, 3);
  const latest = nonIslamic.slice(3, 15);

  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(135deg, #0D1528 0%, #1A2540 50%, #0D1528 100%)',
        padding: '56px 24px 48px',
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

      {/* ═══ TEXTES FONDATEURS ═══ */}
      {islamicArticles.length > 0 && (
        <div style={{ marginBottom: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, background: '#D4943A', borderRadius: 2 }} />
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)', lineHeight: 1.2 }}>Textes Fondateurs</h2>
              <p style={{ fontSize: 13, color: 'var(--ink-muted)', marginTop: 2 }}>Coran, Sunna et patrimoine islamique</p>
            </div>
          </div>

          {/* 2 flagship articles — large cards */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 20, marginBottom: 16 }}>
            {islamicArticles.slice(0, 2).map(a => (
              <Link key={a.slug} href={`/article/${a.slug}`} style={{
                position: 'relative', borderRadius: 12, overflow: 'hidden',
                display: 'block', minHeight: 340,
              }}>
                <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.85) 0%, rgba(0,0,0,0.1) 55%)' }} />
                <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '24px 22px' }}>
                  <span style={{ fontSize: 10, fontWeight: 700, color: '#D4943A', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                    Bibliothèque
                  </span>
                  <h3 style={{ fontSize: 22, fontWeight: 700, color: '#fff', lineHeight: 1.3, marginTop: 6 }}>{a.title}</h3>
                  <p style={{ fontSize: 14, color: 'rgba(255,255,255,0.75)', marginTop: 6, lineHeight: 1.5 }}>
                    {a.description?.slice(0, 120)}{a.description && a.description.length > 120 ? '…' : ''}
                  </p>
                </div>
              </Link>
            ))}
          </div>

          {/* Rest — compact list */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
            {islamicArticles.slice(2).map(a => (
              <Link key={a.slug} href={`/article/${a.slug}`} style={{
                display: 'flex', gap: 12, padding: '12px 14px',
                background: 'var(--cream)', border: '1px solid var(--border)',
                borderRadius: 6, alignItems: 'center',
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 6, flexShrink: 0,
                  background: '#D4943A15', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 16, color: '#D4943A',
                }}>
                  &#9789;
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h4 style={{ fontSize: 13, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.title}</h4>
                  <div style={{ fontSize: 11, color: 'var(--ink-muted)', marginTop: 2 }}>{a.readTime} min de lecture</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

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
      <div>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
          <div style={{ width: 4, height: 28, background: '#3B8FD4', borderRadius: 2 }} />
          <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Dernières publications</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {latest.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} className="home-latest-item" style={{
              display: 'flex', gap: 16, padding: '20px 0', borderBottom: '1px solid var(--border)', alignItems: 'flex-start',
            }}>
              <img src={getArticleImage(a.slug)} alt="" loading="lazy" className="home-latest-img" style={{ width: 160, height: 100, objectFit: 'cover', borderRadius: 6, flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: CAT_COLOR[a.category] || '#8B8F96', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {CAT_LABEL[a.category] || a.category}
                </span>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.35, margin: '4px 0' }}>{a.title}</h3>
                <div style={{ fontSize: 12, color: 'var(--ink-muted)' }}>
                  {fmtDate(a.date)} · {a.readTime} min
                </div>
                <p className="hidden sm:block" style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.5, marginTop: 4 }}>{a.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
      </div>
    </div>
  );
}
