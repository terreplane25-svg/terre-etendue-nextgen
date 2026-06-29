'use client';
import React from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { getArticleImage } from '@/lib/article-images';

interface A {
  slug: string; title: string; description: string;
  tags?: string[]; pinned?: boolean; readTime: number;
}
interface Section {
  id: string; label: string; icon: string;
  slugs?: string[];
  match?: (a: { slug: string; tags?: string[]; pinned?: boolean }) => boolean;
}

interface Props {
  sections: Section[];
  articles: A[];
  color: string;
  basePath: string;          // ex. "/library"
  perSection?: number;       // articles montrés par section (défaut 4)
  featuredSlug?: string;     // article du « Conseil de lecture »
  footer?: (a: A) => React.ReactNode;
}

// ── Carte compacte (grille) ───────────────────────────────────────
function MiniCard({ a, color, footer }: { a: A; color: string; footer?: (a: A) => React.ReactNode }) {
  const footerNode = footer ? footer(a) : null;
  return (
    <div className="carousel-card" style={{
      borderRadius: 10, overflow: 'hidden', background: 'var(--card)',
      border: '1px solid var(--border)', display: 'flex', flexDirection: 'column',
      transition: 'box-shadow 0.2s, border-color 0.2s',
    }}>
      <Link href={`/article/${a.slug}`} style={{ display: 'block', flex: 1 }}>
        <div style={{ position: 'relative', aspectRatio: '16/10', overflow: 'hidden' }}>
          <img src={getArticleImage(a.slug)} alt="" loading="lazy" className="carousel-card-img"
            style={{ width: '100%', height: '100%', objectFit: 'cover', display: 'block', transition: 'transform 0.3s' }} />
          {a.pinned && (
            <span style={{ position: 'absolute', top: 12, right: 14, fontSize: 10, fontWeight: 700, color: '#D4943A', background: 'rgba(0,0,0,0.5)', padding: '3px 8px', borderRadius: 4, backdropFilter: 'blur(4px)' }}>★</span>
          )}
        </div>
        <div style={{ padding: '13px 15px 16px' }}>
          <h3 style={{ fontSize: 15, fontWeight: 700, color: 'var(--ink)', lineHeight: 1.35, marginBottom: 6, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as never, overflow: 'hidden' }}>{a.title}</h3>
          <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.5, marginBottom: 10, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as never, overflow: 'hidden' }}>{a.description}</p>
          <div style={{ fontSize: 11, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>{a.readTime} min</div>
        </div>
      </Link>
      {footerNode && (
        <div style={{ padding: '10px 15px 14px', borderTop: '1px solid var(--border-soft)' }}>{footerNode}</div>
      )}
    </div>
  );
}

const grid: React.CSSProperties = {
  display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))', gap: 16,
};

// ── Conseil de lecture (encart valorisé) ──────────────────────────
function Featured({ a, color }: { a: A; color: string }) {
  return (
    <Link href={`/article/${a.slug}`} className="cat-featured" style={{
      display: 'flex', flexWrap: 'wrap', gap: 0, marginBottom: 44, overflow: 'hidden',
      borderRadius: 14, border: `1.5px solid ${color}55`,
      background: `linear-gradient(135deg, ${color}0d, var(--card) 60%)`,
      boxShadow: `0 6px 28px ${color}1f`,
    }}>
      <div style={{ flex: '1 1 300px', minWidth: 0, position: 'relative', minHeight: 220 }}>
        <img src={getArticleImage(a.slug)} alt="" loading="lazy"
          style={{ position: 'absolute', inset: 0, width: '100%', height: '100%', objectFit: 'cover' }} />
      </div>
      <div style={{ flex: '2 1 340px', minWidth: 0, padding: '26px 30px', display: 'flex', flexDirection: 'column', justifyContent: 'center' }}>
        <span style={{
          alignSelf: 'flex-start', fontSize: 10, fontWeight: 800, letterSpacing: '0.12em',
          color, background: `${color}1a`, border: `1px solid ${color}40`,
          padding: '4px 10px', borderRadius: 20, marginBottom: 14, fontFamily: "'JetBrains Mono', monospace",
        }}>★ CONSEIL DE LECTURE</span>
        <h2 style={{ fontSize: 24, fontWeight: 800, color: 'var(--ink)', lineHeight: 1.25, marginBottom: 12, letterSpacing: '-0.01em' }}>{a.title}</h2>
        {a.description && (
          <p style={{ fontSize: 15, color: 'var(--ink-muted)', lineHeight: 1.6, marginBottom: 16, display: '-webkit-box', WebkitLineClamp: 3, WebkitBoxOrient: 'vertical' as never, overflow: 'hidden' }}>{a.description}</p>
        )}
        <div style={{ display: 'flex', alignItems: 'center', gap: 14 }}>
          <span style={{ fontSize: 13, fontWeight: 700, color }}>Lire l&apos;article →</span>
          <span style={{ fontSize: 11, color: 'var(--ink-ghost)', fontFamily: "'JetBrains Mono', monospace" }}>{a.readTime} min de lecture</span>
        </div>
      </div>
    </Link>
  );
}

// ── Titre de section ──────────────────────────────────────────────
function SecTitle({ icon, label, count, color }: { icon: string; label: string; count: number; color: string }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 18 }}>
      <div style={{ width: 4, height: 26, background: color, borderRadius: 2 }} />
      <span style={{ fontSize: 18 }}>{icon}</span>
      <h2 style={{ fontSize: 21, fontWeight: 800, color: 'var(--ink)', margin: 0 }}>{label}</h2>
      <span style={{ fontSize: 12, fontFamily: "'JetBrains Mono', monospace", color, background: `${color}14`, padding: '2px 8px', borderRadius: 12 }}>{count}</span>
    </div>
  );
}

export default function CategoryFlow({ sections, articles, color, basePath, perSection = 4, featuredSlug, footer }: Props) {
  const sp = useSearchParams();
  const filter = sp.get('filter') || 'all';
  const getSection = (a: A) => sections.find(s => s.match ? s.match(a) : (s.slugs?.includes(a.slug) ?? false))?.id ?? null;
  const uncategorized = articles.filter(a => getSection(a) === null);

  // ── Mode catégorie complète (?filter=…) ──
  if (filter !== 'all') {
    const sec = sections.find(s => s.id === filter);
    const list = filter === 'autres' ? uncategorized : articles.filter(a => getSection(a) === filter);
    const label = sec ? sec.label : 'Autres publications';
    const icon = sec ? sec.icon : '📄';
    return (
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '8px 24px 64px' }}>
        <Link href={basePath} style={{ display: 'inline-block', fontSize: 13, fontWeight: 600, color, marginBottom: 22 }}>← Toutes les catégories</Link>
        <SecTitle icon={icon} label={label} count={list.length} color={color} />
        <div style={grid}>
          {list.map(a => <MiniCard key={a.slug} a={a} color={color} footer={footer} />)}
        </div>
      </div>
    );
  }

  // ── Mode par défaut : conseil de lecture + sections défilantes ──
  const featured = (featuredSlug && articles.find(a => a.slug === featuredSlug))
    || articles.find(a => a.pinned) || articles[0];

  const blocks = [
    ...sections.map(s => ({ id: s.id, icon: s.icon, label: s.label,
      list: articles.filter(a => getSection(a) === s.id && a.slug !== featured?.slug) })),
    ...(uncategorized.filter(a => a.slug !== featured?.slug).length
      ? [{ id: 'autres', icon: '📄', label: 'Autres publications',
          list: uncategorized.filter(a => a.slug !== featured?.slug) }]
      : []),
  ].filter(b => b.list.length > 0);

  return (
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '4px 24px 64px' }}>
      {featured && <Featured a={featured} color={color} />}
      {blocks.map(b => (
        <section key={b.id} style={{ marginBottom: 44 }}>
          <SecTitle icon={b.icon} label={b.label} count={b.list.length} color={color} />
          <div style={grid}>
            {b.list.slice(0, perSection).map(a => <MiniCard key={a.slug} a={a} color={color} footer={footer} />)}
          </div>
          {b.list.length > perSection && (
            <Link href={`${basePath}?filter=${b.id}`} style={{
              display: 'inline-flex', alignItems: 'center', gap: 6, marginTop: 18,
              fontSize: 13, fontWeight: 700, color, border: `1px solid ${color}40`,
              background: `${color}0d`, padding: '8px 16px', borderRadius: 8,
            }}>Voir plus d&apos;articles ({b.list.length}) →</Link>
          )}
        </section>
      ))}
    </div>
  );
}
