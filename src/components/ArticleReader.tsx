'use client';

import React, { useState, useEffect, useRef } from 'react';
import Link from 'next/link';

const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

interface ArticleReaderProps {
  article?: any;
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

const CAT_COLORS: Record<string, string> = {
  observatory: '#3580C0', headquarters: '#7C6FC4', library: '#C48A2E', lab: '#3A8F6E', meta: '#8A857D',
};

export default function ArticleReader(props: ArticleReaderProps) {
  const a = props.article || props;
  const title = a.title || 'Article';
  const description = a.description || '';
  const content = a.content || a.htmlContent || '';
  const category = a.category || 'observatory';
  const tags = a.tags || [];
  const readTime = a.readTime;
  const date = a.date;
  const author = a.author;

  const color = CAT_COLORS[category] || '#7C6FC4';
  const toc = extractTOC(content);
  const [activeId, setActiveId] = useState(toc[0]?.id || '');
  const contentRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => { for (const e of entries) { if (e.isIntersecting) setActiveId(e.target.id); } },
      { rootMargin: '-80px 0px -60% 0px' }
    );
    contentRef.current?.querySelectorAll('h2[id]').forEach(h => observer.observe(h));
    return () => observer.disconnect();
  }, [content]);

  return (
    <div style={{ display: 'flex', minHeight: '100vh', background: '#FAFAF6' }}>

      {/* ═══ SIDEBAR ═══ */}
      <aside className="hidden lg:flex" style={{
        width: 280, flexShrink: 0,
        padding: '32px 0', position: 'sticky', top: 56,
        height: 'calc(100vh - 56px)', flexDirection: 'column',
      }}>
        <div style={{ margin: '0 16px', background: '#F5F3EE', borderRadius: 24, padding: 6, flex: 1, display: 'flex', flexDirection: 'column' }}>
          <div style={{ background: '#fff', borderRadius: 20, flex: 1, display: 'flex', flexDirection: 'column', boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>

            {/* Header */}
            <div style={{ padding: '22px 20px 18px', borderBottom: '1px solid rgba(20,18,16,0.06)' }}>
              <span style={{
                fontSize: 10, fontWeight: 600, letterSpacing: '0.14em', textTransform: 'uppercase',
                fontFamily: "'JetBrains Mono', monospace",
                padding: '3px 10px', borderRadius: 99,
                background: color + '0F', color,
              }}>{category === 'observatory' ? 'OBS' : category === 'headquarters' ? 'QG' : category === 'library' ? 'BIB' : 'TEI'}</span>
              <h2 style={{ fontSize: 15, fontWeight: 750, color: '#141210', marginTop: 12, lineHeight: 1.35 }}>{title}</h2>
              {readTime && (
                <div style={{ fontSize: 11, color: '#BAB5AC', marginTop: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                  {readTime} min de lecture
                </div>
              )}
            </div>

            {/* TOC */}
            <nav style={{ flex: 1, padding: '14px 0', overflowY: 'auto' }}>
              {toc.map(item => (
                <a key={item.id} href={`#${item.id}`} style={{
                  display: 'block', padding: '9px 20px', fontSize: 12,
                  fontWeight: activeId === item.id ? 700 : 500,
                  color: activeId === item.id ? '#141210' : '#8A857D',
                  background: activeId === item.id ? '#FAFAF6' : 'transparent',
                  borderLeft: activeId === item.id ? `3px solid ${color}` : '3px solid transparent',
                  transition: `all 0.2s ${BEZ}`, textDecoration: 'none',
                  overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                }}>{item.text}</a>
              ))}
            </nav>

            {/* Back */}
            <div style={{ padding: '14px 20px', borderTop: '1px solid rgba(20,18,16,0.06)' }}>
              <Link href={`/${category}`} style={{ fontSize: 12, color: '#8A857D', textDecoration: 'none' }}>← Retour</Link>
            </div>
          </div>
        </div>
      </aside>

      {/* ═══ CONTENT ═══ */}
      <div style={{ flex: 1, padding: '36px 24px 80px', maxWidth: 820, margin: '0 auto' }}>

        {/* Article card — Bezel (Doppelrand) */}
        <div style={{ background: '#F5F3EE', border: '1px solid rgba(20,18,16,0.06)', borderRadius: 24, padding: 6 }}>
          <div style={{ background: '#fff', borderRadius: 20, boxShadow: '0 2px 8px rgba(0,0,0,0.03)' }}>

            {/* Header */}
            <div style={{ padding: '44px 48px 32px' }}>
              <div style={{ display: 'flex', gap: 8, marginBottom: 16, flexWrap: 'wrap' }}>
                {tags.slice(0, 4).map((t: string) => (
                  <span key={t} style={{
                    fontSize: 10, fontWeight: 600, letterSpacing: '0.1em', textTransform: 'uppercase',
                    fontFamily: "'JetBrains Mono', monospace",
                    padding: '3px 10px', borderRadius: 99,
                    background: '#F5F3EE', color: '#8A857D',
                  }}>{t}</span>
                ))}
              </div>
              <h1 style={{ fontSize: 30, fontWeight: 800, color: '#141210', lineHeight: 1.3, letterSpacing: '-0.02em', marginBottom: 10 }}>{title}</h1>
              {description && <p style={{ fontSize: 16, color: '#8A857D', lineHeight: 1.6 }}>{description}</p>}
              {(date || author) && (
                <div style={{ fontSize: 12, color: '#BAB5AC', marginTop: 14, fontFamily: "'JetBrains Mono', monospace" }}>
                  {date && <span>{new Date(date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })}</span>}
                  {author && <span> · {author}</span>}
                </div>
              )}
              <div style={{ height: 1, background: 'rgba(20,18,16,0.06)', marginTop: 28 }} />
            </div>

            {/* Body */}
            <div ref={contentRef} className="prose-dash" style={{ padding: '0 48px 48px' }} dangerouslySetInnerHTML={{ __html: content }} />
          </div>
        </div>
      </div>
    </div>
  );
}
