'use client';
import React from 'react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';

interface A { slug: string; title: string; description: string; category: string; tags: string[]; readTime: number; date: string; pinned: boolean; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils', meta: 'TEI' };
const CAT_COLOR: Record<string, string> = { headquarters: '#7C6FC4', observatory: '#3580C0', library: '#C48A2E', lab: '#3A8F6E', meta: '#8A857D' };

const ISLAMIC_SLUGS = [
  'debut-de-la-creation-selon-le-coran-et-la-sunna',
  'debut-de-la-creation-le-soleil-mobile-la-terre-immobile',
  'la-terre-dans-le-coran',
  'pres-de-cent-savants-de-lislam',
  'dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne',
  'la-qibla-et-la-direction-cote-ouest',
  'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
];

export default function HomeClient({ articles }: { articles: A[] }) {
  const islamicArticles = ISLAMIC_SLUGS.map(slug => articles.find(a => a.slug === slug)).filter(Boolean) as A[];
  const nonIslamic = articles.filter(a => !ISLAMIC_SLUGS.includes(a.slug));
  const featured = nonIslamic[0];
  const medium = nonIslamic.slice(1, 4);
  const sidebar = nonIslamic.slice(4, 9);
  const latest = nonIslamic.slice(9, 18);

  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '24px 24px 80px', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>

      {/* ═══ TEXTES FONDATEURS — tout en haut ═══ */}
      {islamicArticles.length > 0 && (
        <div style={{ marginBottom: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, background: '#C48A2E', borderRadius: 2 }} />
            <div>
              <h2 style={{ fontSize: 22, fontWeight: 800, color: '#141210', lineHeight: 1.2 }}>Textes Fondateurs</h2>
              <p style={{ fontSize: 13, color: '#8A857D', marginTop: 2 }}>Coran, Sunna et patrimoine islamique</p>
            </div>
          </div>

          {/* 2 premiers articles — grandes cartes avec image */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))', gap: 20, marginBottom: 16 }}>
            {islamicArticles.slice(0, 2).map(a => (
              <Link key={a.slug} href={`/article/${a.slug}`} style={{
                position: 'relative', borderRadius: 8, overflow: 'hidden',
                display: 'block', minHeight: 200,
              }}>
                <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
                <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.8) 0%, rgba(0,0,0,0.1) 60%)' }} />
                <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '20px 18px' }}>
                  <span style={{ fontSize: 10, fontWeight: 700, color: '#C48A2E', textTransform: 'uppercase', letterSpacing: '0.08em' }}>
                    Bibliothèque
                  </span>
                  <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff', lineHeight: 1.3, marginTop: 4 }}>{a.title}</h3>
                  <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)', marginTop: 4, lineHeight: 1.4 }}>
                    {a.description?.slice(0, 100)}{a.description && a.description.length > 100 ? '...' : ''}
                  </p>
                </div>
              </Link>
            ))}
          </div>

          {/* Reste — liste compacte */}
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
            {islamicArticles.slice(2).map(a => (
              <Link key={a.slug} href={`/article/${a.slug}`} style={{
                display: 'flex', gap: 12, padding: '12px 14px',
                background: '#FBF8F1', border: '1px solid #EDE8DD',
                borderRadius: 6, alignItems: 'center',
              }}>
                <div style={{
                  width: 36, height: 36, borderRadius: 6, flexShrink: 0,
                  background: '#C48A2E15', display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 16, color: '#C48A2E',
                }}>
                  &#9789;
                </div>
                <div style={{ flex: 1, minWidth: 0 }}>
                  <h4 style={{ fontSize: 13, fontWeight: 700, color: '#141210', lineHeight: 1.3, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{a.title}</h4>
                  <div style={{ fontSize: 11, color: '#8A857D', marginTop: 2 }}>{a.readTime} min de lecture</div>
                </div>
              </Link>
            ))}
          </div>
        </div>
      )}

      {/* ═══ À LA UNE ═══ */}
      <div className="home-hero-grid" style={{ display: 'grid', gridTemplateColumns: '1fr', gap: 24, marginBottom: 48 }}>

        {/* Article principal */}
        {featured && (
          <Link href={`/article/${featured.slug}`} style={{ position: 'relative', borderRadius: 8, overflow: 'hidden', display: 'block', minHeight: 280 }}>
            <img src={getArticleImage(featured.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
            <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.75) 0%, transparent 60%)' }} />
            <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '28px 24px' }}>
              <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.7)', marginBottom: 8 }}>
                {featured.date && new Date(featured.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {featured.readTime} min
              </div>
              <h2 style={{ fontSize: 22, fontWeight: 700, color: '#fff', lineHeight: 1.3, marginBottom: 8 }}>{featured.title}</h2>
              <p className="hidden sm:block" style={{ fontSize: 14, color: 'rgba(255,255,255,0.8)', lineHeight: 1.5 }}>{featured.description}</p>
            </div>
          </Link>
        )}

        <div style={{ display: 'flex', flexDirection: 'column', gap: 20 }}>
          {medium.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{ display: 'flex', flexDirection: 'column', gap: 8, paddingBottom: 20, borderBottom: '1px solid #eee' }}>
              <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: 120, objectFit: 'cover', borderRadius: 6 }} />
              <div style={{ fontSize: 11, color: '#999' }}>{a.date && new Date(a.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {a.readTime} min</div>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#141210', lineHeight: 1.35 }}>{a.title}</h3>
            </Link>
          ))}
        </div>

        <div className="hidden lg:flex" style={{ flexDirection: 'column', gap: 0 }}>
          {sidebar.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{ display: 'block', padding: '14px 0', borderBottom: '1px solid #eee' }}>
              <div style={{ fontSize: 11, color: '#999', marginBottom: 4 }}>{a.date && new Date(a.date).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' })} | {a.readTime} min</div>
              <h4 style={{ fontSize: 14, fontWeight: 700, color: '#141210', lineHeight: 1.35 }}>{a.title}</h4>
            </Link>
          ))}
        </div>
      </div>

      {/* ═══ DERNIÈRES PUBLICATIONS ═══ */}
      <h2 style={{ fontSize: 28, fontWeight: 800, color: '#141210', marginBottom: 20, paddingBottom: 12, borderBottom: '3px solid #7C6FC4', display: 'inline-block' }}>Dernières publications</h2>
      <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
        {latest.map(a => (
          <Link key={a.slug} href={`/article/${a.slug}`} className="home-latest-item" style={{ display: 'flex', gap: 16, padding: '20px 0', borderBottom: '1px solid #eee', alignItems: 'flex-start' }}>
            <img src={getArticleImage(a.slug)} alt="" className="home-latest-img" style={{ width: 160, height: 100, objectFit: 'cover', borderRadius: 6, flexShrink: 0 }} />
            <div style={{ flex: 1, minWidth: 0 }}>
              <span style={{ fontSize: 11, fontWeight: 700, color: CAT_COLOR[a.category] || '#999', textTransform: 'uppercase', letterSpacing: '0.05em' }}>
                {CAT_LABEL[a.category] || a.category}
              </span>
              <h3 style={{ fontSize: 16, fontWeight: 700, color: '#141210', lineHeight: 1.35, margin: '4px 0' }}>{a.title}</h3>
              <div style={{ fontSize: 12, color: '#999' }}>
                {a.readTime} min
              </div>
              <p className="hidden sm:block" style={{ fontSize: 13, color: '#666', lineHeight: 1.5, marginTop: 4 }}>{a.description}</p>
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
