import { Suspense } from 'react';
import { getArticlesByCategory } from '@/lib/articles';
import ObservatoryClient from './ObservatoryClient';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  alternates: { canonical: '/observatory' },
  title: "L'Observatoire — Données empiriques",
  description: 'Publications analytiques : données empiriques, analyses optiques, observations documentées.',
};

export default function ObservatoryPage() {
  const allObs = getArticlesByCategory('observatory') as any[];

  const analysisArticles = allObs.filter(
    (a: any) => !a.tags?.includes('physique-naturelle')
  );

  const formatted = analysisArticles.map((a: any) => ({
    slug: a.slug,
    title: a.title,
    description: a.description || '',
    tags: a.tags || [],
    pinned: a.pinned || false,
    readTime: a.readTime || 5,
  }));

  return (
    <Suspense>
      <ObservatoryClient articles={formatted} />
    </Suspense>
  );
}
