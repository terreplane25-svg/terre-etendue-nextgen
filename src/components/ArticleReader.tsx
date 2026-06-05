'use client';
import React from 'react';
import { getArticleImage } from '@/lib/article-images';

interface ArticleReaderProps { article?: any; title?: string; description?: string; content?: string; category?: string; tags?: string[]; readTime?: number; date?: string; author?: string; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils' };

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

  return (
    <div style={{ maxWidth: 900, margin: '0 auto', padding: '32px 24px 80px', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>

      {/* Category */}
      <div style={{ fontSize: 12, fontWeight: 700, color: '#7C6FC4', textTransform: 'uppercase', letterSpacing: '0.06em', marginBottom: 12 }}>
        {CAT_LABEL[category] || category}
      </div>

      {/* Title */}
      <h1 style={{ fontSize: 36, fontWeight: 800, color: '#141210', lineHeight: 1.25, letterSpacing: '-0.02em', marginBottom: 14 }}>{title}</h1>

      {/* Description */}
      {description && <p style={{ fontSize: 18, color: '#666', lineHeight: 1.6, marginBottom: 16 }}>{description}</p>}

      {/* Meta */}
      <div style={{ fontSize: 13, color: '#999', marginBottom: 24 }}>
        {author && <span>{author} | </span>}
        {date && <span>{new Date(date).toLocaleDateString('fr-FR', { year: 'numeric', month: 'long', day: 'numeric' })} | </span>}
        {readTime && <span>{readTime} min</span>}
      </div>

      {/* Hero image */}
      {heroImg && (
        <div style={{ marginBottom: 24, borderRadius: 8, overflow: 'hidden' }}>
          <img src={heroImg} alt="" style={{ width: '100%', height: 'auto', maxHeight: 480, objectFit: 'cover', display: 'block' }} />
        </div>
      )}

      {/* Separator */}
      <div style={{ height: 1, background: '#eee', margin: '0 0 32px' }} />

      {/* Article body */}
      <div className="prose-dash" dangerouslySetInnerHTML={{ __html: content }} />
    </div>
  );
}
