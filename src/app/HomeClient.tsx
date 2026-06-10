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
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 24px 80px' }}>

      {/* ═══ TEXTES FONDATEURS ═══ */}
      {islamicArticles.length > 0 && (
        <div style={{ marginBottom: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, background: '#D4943A', borderRadius: 2 }} />
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: '#1A1D23', lineHeight: 1.2 }}>Textes Fondateurs</h2>
              <p style={{ fontSize: 13, color: '#8B8F96', marginTop: 2 }}>Coran, Sunna et patrimoine islamique</p>
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
                background: '#FBF8F1', border: '1px solid #EDE8DD',
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
                  <h4 style={{ fontSize: 13, fontWeight: 700, color: '#1A1D23', lineHeight: 1.3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.title}</h4>
                  <div style={{ fontSize: 11, color: '#8B8F96', marginTop: 2 }}>{a.readTime} min de lecture</div>
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
          <h2 style={{ fontSize: 22, fontWeight: 800, color: '#1A1D23' }}>À la une</h2>
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
          <h2 style={{ fontSize: 22, fontWeight: 800, color: '#1A1D23' }}>Dernières publications</h2>
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
          {latest.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} className="home-latest-item" style={{
              display: 'flex', gap: 16, padding: '20px 0', borderBottom: '1px solid #E8EAED', alignItems: 'flex-start',
            }}>
              <img src={getArticleImage(a.slug)} alt="" loading="lazy" className="home-latest-img" style={{ width: 160, height: 100, objectFit: 'cover', borderRadius: 6, flexShrink: 0 }} />
              <div style={{ flex: 1, minWidth: 0 }}>
                <span style={{ fontSize: 11, fontWeight: 700, color: CAT_COLOR[a.category] || '#8B8F96', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                  {CAT_LABEL[a.category] || a.category}
                </span>
                <h3 style={{ fontSize: 16, fontWeight: 700, color: '#1A1D23', lineHeight: 1.35, margin: '4px 0' }}>{a.title}</h3>
                <div style={{ fontSize: 12, color: '#8B8F96' }}>
                  {fmtDate(a.date)} · {a.readTime} min
                </div>
                <p className="hidden sm:block" style={{ fontSize: 13, color: '#4A4E57', lineHeight: 1.5, marginTop: 4 }}>{a.description}</p>
              </div>
            </Link>
          ))}
        </div>
      </div>
    </div>
  );
}
