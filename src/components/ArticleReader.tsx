'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';

interface ArticleProp {
  title: string;
  description?: string;
  content?: string;
  htmlContent?: string;
  category?: string;
  tags?: string[];
  readTime?: number;
  date?: string;
  author?: string;
  slug?: string;
}

interface ArticleReaderProps {
  // Accept either individual props or an article object
  article?: ArticleProp;
  title?: string;
  description?: string;
  content?: string;
  category?: string;
  tags?: string[];
  readTime?: number;
  date?: string;
  author?: string;
}

function extractTOC(html: string) {
  const regex = /<h2[^>]*id="([^"]*)"[^>]*>(.*?)<\/h2>/gi;
  const items: { id: string; text: string }[] = [];
  let m;
  while ((m = regex.exec(html)) !== null) {
    const text = m[2].replace(/<[^>]+>/g, '').replace(/\d{2}\s*/, '').trim();
    if (text) items.push({ id: m[1], text });
  }
  return items;
}

const SECTION_ICONS: Record<string, string> = {
  'ce-quon-observe': '👁', 'experience': '🧪', 'materiel': '🧫',
  'protocole': '📋', 'resultat': '✅', 'pourquoi': '⚙',
  'ce-que-ca-change': '→', 'synthese': '📊', 'references': '📚',
  'refraction': '🔍', 'mirages': '🌫', 'intro': '◎', 'horizon': '◉',
  'perspective': '△', 'fisheye': '📷', 'visibilite': '👁',
};

function getIcon(id: string) {
  for (const [key, icon] of Object.entries(SECTION_ICONS)) {
    if (id.toLowerCase().includes(key)) return icon;
  }
  return '○';
}

export default function ArticleReader(props: ArticleReaderProps) {
  // Normalize: accept either article={} or individual props
  const a = props.article || props;
  const title = a.title || 'Article';
  const description = a.description || '';
  const content = (a as any).content || (a as any).htmlContent || '';
  const category = a.category || 'observatory';
  const tags = a.tags || [];
  const readTime = a.readTime;
  const date = a.date;
  const author = a.author;

  const toc = extractTOC(content);
  const [activeId, setActiveId] = useState(toc[0]?.id || '');
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) setActiveId(entry.target.id);
        }
      },
      { rootMargin: '-80px 0px -60% 0px' }
    );
    const headings = contentRef.current?.querySelectorAll('h2[id]');
    headings?.forEach(h => observer.observe(h));
    return () => observer.disconnect();
  }, [content]);

  const catLabel = ({ headquarters: 'Q.G.', observatory: 'OBS', library: 'BIBLIO', lab: 'LAB' } as Record<string, string>)[category] || 'TEI';
  const catColor = category === 'observatory' ? { bg: dash.cyanSoft, fg: dash.cyan } : { bg: dash.lavenderSoft, fg: dash.lavender };

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: dash.bg }}>
      {/* ═══ SIDEBAR ═══ */}
      <aside className="hidden lg:flex" style={{
        width: 260, flexShrink: 0, background: dash.card,
        borderRight: `1px solid ${dash.borderSoft}`,
        padding: '28px 0', position: 'sticky', top: 56, height: 'calc(100vh - 56px)',
        flexDirection: 'column',
      }}>
        <div style={{ padding: '0 20px 20px', borderBottom: `1px solid ${dash.borderSoft}` }}>
          <span className="badge" style={{ background: catColor.bg, color: catColor.fg }}>{catLabel}</span>
          <h2 style={{ fontSize: 15, fontWeight: 750, color: dash.ink, marginTop: 10, lineHeight: 1.35 }}>{title}</h2>
          {readTime && (
            <div style={{ fontSize: 11, color: dash.inkGhost, marginTop: 8, fontFamily: dash.fontMono }}>
              {readTime} min de lecture
            </div>
          )}
        </div>

        <nav style={{ flex: 1, padding: '12px 0', overflowY: 'auto' }}>
          {toc.map(item => (
            <a key={item.id} href={`#${item.id}`} style={{
              display: 'flex', alignItems: 'center', gap: 10,
              padding: '9px 20px', fontSize: 12,
              fontWeight: activeId === item.id ? 700 : 500,
              color: activeId === item.id ? dash.ink : dash.inkMuted,
              background: activeId === item.id ? dash.bg : 'transparent',
              borderLeft: activeId === item.id ? `3px solid ${dash.lavender}` : '3px solid transparent',
              transition: 'all 0.15s', textDecoration: 'none',
            }}>
              <span style={{ fontSize: 13, opacity: 0.5, width: 18, textAlign: 'center' }}>{getIcon(item.id)}</span>
              <span style={{ overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap' }}>{item.text}</span>
            </a>
          ))}
        </nav>

        <div style={{ padding: '14px 20px', borderTop: `1px solid ${dash.borderSoft}` }}>
          <Link href={`/${category}`} style={{ fontSize: 12, color: dash.inkMuted, display: 'flex', alignItems: 'center', gap: 6 }}>
            ← Retour
          </Link>
        </div>
      </aside>

      {/* ═══ MOBILE TOC ═══ */}
      <button className="lg:hidden" onClick={() => setSidebarOpen(!sidebarOpen)} style={{
        position: 'fixed', bottom: 20, right: 20, zIndex: 40,
        width: 48, height: 48, borderRadius: 14,
        background: dash.ink, color: '#fff', border: 'none',
        boxShadow: '0 4px 16px rgba(0,0,0,0.15)', cursor: 'pointer',
        display: 'flex', alignItems: 'center', justifyContent: 'center', fontSize: 18,
      }}>☰</button>

      {/* ═══ CONTENT ═══ */}
      <motion.div initial={{ opacity: 0, y: 16 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.4 }}
        style={{ flex: 1, padding: '36px 24px 64px', maxWidth: 800, margin: '0 auto' }}>
        <div className="dash-card" style={{ padding: '44px 48px', marginBottom: 24 }}>
          <div style={{ marginBottom: 32 }}>
            <div style={{ display: 'flex', gap: 8, marginBottom: 12, flexWrap: 'wrap' }}>
              {tags.slice(0, 4).map(t => (
                <span key={t} className="badge" style={{ background: dash.bg, color: dash.inkMuted }}>{t}</span>
              ))}
            </div>
            <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, lineHeight: 1.3, marginBottom: 8 }}>{title}</h1>
            {description && <p style={{ fontSize: 15, color: dash.inkMuted, lineHeight: 1.6 }}>{description}</p>}
            {(date || author) && (
              <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 12, fontFamily: dash.fontMono }}>
                {date && <span>{new Date(date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })}</span>}
                {author && <span> · {author}</span>}
              </div>
            )}
          </div>
          <div ref={contentRef} className="prose-dash" dangerouslySetInnerHTML={{ __html: content }} />
        </div>
      </motion.div>
    </div>
  );
}
