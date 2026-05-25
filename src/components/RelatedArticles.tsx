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
  headquarters: 'var(--cyan)',
  observatory: 'var(--green)',
  library: 'var(--gold)',
  lab: 'var(--cyan)',
  meta: 'var(--text)',
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
    <div className="mt-12 border-t border-[var(--panel-edge)] pt-8">
      <div className="flex items-center gap-3 mb-6">
        <div className="w-6 h-[1px]" style={{ background: 'var(--cyan)' }} />
        <span className="text-[10px] font-tech-mono tracking-[0.2em]" style={{ color: 'var(--text-30)' }}>
          ARTICLES CONNEXES
        </span>
        <div className="flex-1 h-[1px]" style={{ background: 'var(--panel-edge)' }} />
      </div>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {scored.map(article => (
          <Link
            key={article.slug}
            href={`/article/${article.slug}`}
            className="block p-4 border transition-all hover:-translate-y-0.5"
            style={{
              background: 'var(--panel)',
              borderColor: 'var(--panel-edge)',
            }}
          >
            <div
              className="text-[8px] font-tech-mono tracking-[0.2em] uppercase mb-2"
              style={{ color: CATEGORY_COLORS[article.category] || 'var(--cyan)', opacity: 0.6 }}
            >
              {CATEGORY_LABELS[article.category] || article.category}
            </div>
            <div className="text-[15px] font-semibold mb-2" style={{ color: 'var(--text)' }}>
              {article.title}
            </div>
            <div
              className="text-[12px] line-clamp-2"
              style={{ color: 'var(--text-60)' }}
            >
              {article.description}
            </div>
          </Link>
        ))}
      </div>
    </div>
  );
}
