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
          padding: 20,
          maxWidth: '95vw',
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
            position: 'absolute', top: 10, right: 10,
            width: 32, height: 32, borderRadius: 4,
            border: '1px solid #ddd', background: '#fff',
            color: '#666', fontSize: 16, cursor: 'pointer',
            display: 'flex', alignItems: 'center', justifyContent: 'center',
            zIndex: 1,
          }}
        >
          ✕
        </button>
        <div
          dangerouslySetInnerHTML={{ __html: svgHtml }}
          style={{ minWidth: 600, maxWidth: '90vw' }}
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

  const closeLightbox = useCallback(() => setLightboxSvg(null), []);

  useEffect(() => {
    if (!contentRef.current) return;
    const svgs = contentRef.current.querySelectorAll('svg');
    const handlers: Array<{ el: SVGSVGElement; fn: () => void }> = [];

    svgs.forEach(svg => {
      svg.style.cursor = 'zoom-in';
      svg.setAttribute('title', 'Cliquez pour agrandir');

      const hint = document.createElement('div');
      hint.style.cssText = 'position:absolute;bottom:6px;right:8px;font-size:9px;font-family:monospace;color:#8A857D;opacity:0;transition:opacity 0.2s;pointer-events:none;background:rgba(255,255,255,0.85);padding:1px 5px;border-radius:2px;';
      hint.textContent = '⤢ Agrandir';

      const wrapper = svg.parentElement;
      if (wrapper) {
        wrapper.style.position = 'relative';
        wrapper.appendChild(hint);
        svg.addEventListener('mouseenter', () => { hint.style.opacity = '1'; });
        svg.addEventListener('mouseleave', () => { hint.style.opacity = '0'; });
      }

      const fn = () => {
        const clone = svg.cloneNode(true) as SVGSVGElement;
        clone.style.cursor = 'default';
        clone.style.width = '100%';
        clone.style.height = 'auto';
        clone.style.maxWidth = 'none';
        clone.style.background = '#fff';
        clone.style.border = 'none';
        clone.style.boxShadow = 'none';
        clone.style.padding = '0';
        clone.style.margin = '0';
        clone.style.display = 'block';
        setLightboxSvg(clone.outerHTML);
      };
      svg.addEventListener('click', fn);
      handlers.push({ el: svg, fn });
    });

    return () => {
      handlers.forEach(({ el, fn }) => el.removeEventListener('click', fn));
    };
  }, [content]);

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px 80px', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>

      <div style={{ fontSize: 12, fontWeight: 700, color: '#7C6FC4', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>
        {CAT_LABEL[category] || category}
      </div>

      <h1 style={{ fontSize: 36, fontWeight: 800, color: '#141210', lineHeight: 1.25, letterSpacing: '-0.02em', marginBottom: 14 }}>{title}</h1>

      {description && <p style={{ fontSize: 18, color: '#666', lineHeight: 1.6, marginBottom: 16 }}>{description}</p>}

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
