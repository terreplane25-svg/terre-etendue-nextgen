import { getArticlesByCategory } from '@/lib/articles';
import LabClient from './LabClient';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  alternates: { canonical: '/lab' },
  title: "Le Lab — Modélisation 3D",
  description: "Simulateurs interactifs, calculateur de courbure et modèles 3D du dôme céleste.",
};

export default function LabPage() {
  const articles = getArticlesByCategory('lab') as any[];

  const formatted = articles.map((a: any) => ({
    slug: a.slug, title: a.title, description: a.description || '',
    tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
  }));

  return <LabClient articles={formatted} />;
}
