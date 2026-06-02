import { getArticlesByCategory } from '@/lib/articles';
import ObservatoryClient from './ObservatoryClient';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: "L'Observatoire — Données empiriques",
  description: 'Publications de données empiriques, analyses optiques et expériences de physique naturelle.',
};

export default function ObservatoryPage() {
  const articles = getArticlesByCategory('observatory') as any[];

  const formatted = articles.map((a: any) => ({
    slug: a.slug,
    title: a.title,
    description: a.description || '',
    tags: a.tags || [],
    pinned: a.pinned || false,
    readTime: a.readTime || 5,
  }));

  return <ObservatoryClient articles={formatted} />;
}
