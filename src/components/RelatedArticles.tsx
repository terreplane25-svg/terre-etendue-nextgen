'use client';

import Link from 'next/link';

interface Article {
  slug: string;
  title: string;
  description: string;
  category: string;
  tags?: string[];
}

interface Props {
  currentSlug: string;
  currentTags: string[];
  allArticles: Article[];
  maxItems?: number;
}

const CATEGORY_COLORS: Record<string, string> = {
  headquarters: '#3580C0',
  observatory: '#3A8F6E',
  library: '#C48A2E',
  lab: '#3580C0',
  meta: '#141210',
};

const CATEGORY_LABELS: Record<string, string> = {
  headquarters: 'LE Q.G.',
  observatory: "L'OBSERVATOIRE",
  library: 'LA BIBLIOTHÈQUE',
  lab: 'LE LAB',
  meta: 'À PROPOS',
};

export default function RelatedArticles({ currentSlug, currentTags, allArticles, maxItems = 3 }: Props) {
  // Calculer le score de similarité par tags communs
  const scored = allArticles
    .filter(a => a.slug !== currentSlug)
    .map(a => {
      const commonTags = (a.tags || []).filter(t => currentTags.includes(t));
      return { ...a, score: commonTags.length };
    })
    .filter(a => a.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, maxItems);

  if (scored.length === 0) return null;

  return (
    <div className="mt-12 pt-8" style={{ borderTop: '1px solid var(--border-soft)', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <div className="flex items-center gap-3 mb-6">
        <div className="w-6 h-[1px]" style={{ background: '#3580C0' }} />
        <span
          className="text-[10px] tracking-[0.2em]"
          style={{ color: 'var(--ink-muted)', fontWeight: 600, letterSpacing: '0.2em' }}
        >
          ARTICLES CONNEXES
        </span>
        <div className="flex-1 h-[1px]" style={{ background: 'var(--border-soft)' }} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {scored.map(article => (
          <Link
            key={article.slug}
            href={`/article/${article.slug}`}
            className="block p-4 border rounded-lg transition-all hover:-translate-y-0.5"
            style={{
              background: 'var(--card)',
              borderColor: 'var(--border-soft)',
            }}
          >
            <div
              className="text-[8px] tracking-[0.2em] uppercase mb-2"
              style={{ color: CATEGORY_COLORS[article.category] || '#3580C0', opacity: 0.6, fontWeight: 600 }}
            >
              {CATEGORY_LABELS[article.category] || article.category}
            </div>
            <div className="text-[15px] font-semibold mb-2" style={{ color: 'var(--ink)' }}>
              {article.title}
            </div>
            <div
              className="text-[12px] line-clamp-2"
              style={{ color: 'var(--ink-muted)' }}
            >
              {article.description}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
