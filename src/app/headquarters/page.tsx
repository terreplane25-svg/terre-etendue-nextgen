import { Suspense } from 'react';
import { getArticlesByCategory } from '@/lib/articles';
import type { Metadata } from 'next';
import HeadquartersClient from './HeadquartersClient';

export const metadata: Metadata = {
  title: "Le Quartier Général — Épistémologie",
};

export default function HeadquartersPage() {
  const articles = getArticlesByCategory('headquarters') as any[];
  const formatted = articles.map((a: any) => ({
    slug: a.slug, title: a.title, description: a.description || '',
    tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
  }));
  return (
    <Suspense>
      <HeadquartersClient articles={formatted} />
    </Suspense>
  );
}
