'use client';
import React, { useState, useEffect, useRef, useCallback } from 'react';
import { getArticleImage } from '@/lib/article-images';

interface ArticleReaderProps { article?: any; title?: string; description?: string; content?: string; category?: string; tags?: string[]; readTime?: number; date?: string; author?: string; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils' };

function SvgLightbox({ svgHtml, onClose }: { svgHtml: string; onClose: () => void }) {
  useEffect(() => {
    const handleKey = (e: KeyboardEvent) => { if (e.key === 'Escape') onClose(); };
    document.addEventListener('keydown', handleKey);
    document.body.style.overflow = 'hidden';
    return () => {
      document.removeEventListener('keydown', handleKey);
      document.body.style.overflow = '';
    };
  }, [onClose]);

  return (
    <div
      onClick={onClose}
      style={{
        position: 'fixed', inset: 0, zIndex: 9999,
        background: 'rgba(0,0,0,0.85)',
        display: 'flex', alignItems: 'center', justifyContent: 'center',
        cursor: 'zoom-out',
        padding: 24,
      }}
    >
      <div
        onClick={e => e.stopPropagation()}
        style={{
          background: '#fff',
          borderRadius: 6,
          padding: 24,
          width: '92vw',
          maxWidth: 1200,
          maxHeight: '92vh',
          overflow: 'auto',
          cursor: 'default',
          position: 'relative',
          boxShadow: '0 8px 40px rgba(0,0,0,0.3)',
        }}
      >
        <button
          onClick={onClose}
          style={{
            position: 'sticky', top: 0, float: 'right',
            width: 36, height: 36, borderRadius: 4,
            border: '1px solid #ddd', background: '#fff',
            color: '#666', fontSize: 18, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1, marginBottom: -36,
          }}
        >
          ✕
        </button>
        <div
          dangerouslySetInnerHTML={{ __html: svgHtml }}
          className="svg-lightbox-content"
        />
      </div>
    </div>
  );
}

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
  const slug = a.slug || '';
  const heroImg = getArticleImage(slug);

  const contentRef = useRef<HTMLDivElement>(null);
  const [lightboxSvg, setLightboxSvg] = useState<string | null>(null);
  const hintsAdded = useRef(false);

  const closeLightbox = useCallback(() => setLightboxSvg(null), []);

  useEffect(() => {
    const container = contentRef.current;
    if (!container) return;

    if (!hintsAdded.current) {
      hintsAdded.current = true;

      container.querySelectorAll('table').forEach(table => {
        if (table.parentElement?.classList.contains('table-scroll-wrapper')) return;
        const wrapper = document.createElement('div');
        wrapper.className = 'table-scroll-wrapper';
        table.parentNode?.insertBefore(wrapper, table);
        wrapper.appendChild(table);
      });

      container.querySelectorAll('svg').forEach(svg => {
        svg.style.cursor = 'zoom-in';
        svg.setAttribute('title', 'Cliquez pour agrandir');
        const hint = document.createElement('div');
        hint.className = 'svg-zoom-hint';
        hint.style.cssText = 'position:absolute;bottom:6px;right:8px;font-size:9px;font-family:monospace;color:#8A857D;opacity:0;transition:opacity 0.2s;pointer-events:none;background:rgba(255,255,255,0.85);padding:1px 5px;border-radius:2px;';
        hint.textContent = '⤢ Agrandir';
        const wrapper = svg.parentElement;
        if (wrapper) {
          wrapper.style.position = 'relative';
          wrapper.appendChild(hint);
          svg.addEventListener('mouseenter', () => { hint.style.opacity = '1'; });
          svg.addEventListener('mouseleave', () => { hint.style.opacity = '0'; });
        }
      });
    }

    const handleClick = (e: MouseEvent) => {
      const target = e.target as Element;
      const svg = target.closest('svg');
      if (!svg || !container.contains(svg)) return;

      e.stopPropagation();
      const clone = svg.cloneNode(true) as SVGSVGElement;
      clone.removeAttribute('width');
      clone.removeAttribute('height');
      clone.style.cssText = 'width:100%;height:auto;max-width:none;display:block;background:transparent;border:none;box-shadow:none;padding:0;margin:0;cursor:default;';
      setLightboxSvg(clone.outerHTML);
    };

    container.addEventListener('click', handleClick);
    return () => container.removeEventListener('click', handleClick);
  }, [content]);

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 16px 80px', fontFamily: "'Plus Jakarta Sans', sans-serif" }} className="sm:!px-6">

      <div style={{ fontSize: 12, fontWeight: 700, color: '#7C6FC4', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>
        {CAT_LABEL[category] || category}
      </div>

      <h1 className="text-[26px] sm:text-[32px] md:text-[36px]" style={{ fontWeight: 800, color: '#141210', lineHeight: 1.25, letterSpacing: '-0.02em', marginBottom: 14, overflowWrap: 'break-word' }}>{title}</h1>

      {description && <p className="text-[16px] sm:text-[18px]" style={{ color: '#666', lineHeight: 1.6, marginBottom: 16 }}>{description}</p>}

      <div style={{ fontSize: 13, color: '#999', marginBottom: 24 }}>
        {author && <span>{author} | </span>}
        {date && <span>{new Date(date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })} | </span>}
        {readTime && <span>{readTime} min</span>}
      </div>

      {heroImg && (
        <div style={{ marginBottom: 24, borderRadius: 6, overflow: 'hidden' }}>
          <img src={heroImg} alt="" style={{ width: '100%', height: 'auto', maxHeight: 480, objectFit: 'cover', display: 'block' }} />
        </div>
      )}

      <div style={{ height: 1, background: '#eee', margin: '0 0 32px' }} />

      <div ref={contentRef} className="prose-dash" dangerouslySetInnerHTML={{ __html: content }} />

      {lightboxSvg && <SvgLightbox svgHtml={lightboxSvg} onClose={closeLightbox} />}
    </div>
  );
}
