import { getArticlesByCategory } from '@/lib/articles';
import LibraryClient from './LibraryClient';
import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: "La Bibliothèque — Sources sacrées & historiques",
  description: "Sources coraniques, hadith, textes historiques et analyses des fondements cosmologiques.",
};

const PRIORITY_SLUGS = [
  "debut-de-la-creation-selon-le-coran-et-la-sunna",
  "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
];

export default function LibraryPage() {
  const articles = getArticlesByCategory('library') as any[];
  
  const priority = articles
    .filter((a: any) => PRIORITY_SLUGS.includes(a.slug))
    .map((a: any) => ({
      slug: a.slug, title: a.title, description: a.description || '',
      tags: a.tags || [], pinned: true, readTime: a.readTime || 5,
    }));

  const others = articles
    .filter((a: any) => !PRIORITY_SLUGS.includes(a.slug))
    .map((a: any) => ({
      slug: a.slug, title: a.title, description: a.description || '',
      tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
    }));

  return <LibraryClient priority={priority} articles={others} />;
}
