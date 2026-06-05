import { getAllArticles } from '@/lib/articles';
import HomeClient from './HomeClient';

const EXCLUDE = ['le-mouvement-zetetique-150-ans-de-resistance'];

export default function HomePage() {
  const articles = getAllArticles() as any[];
  const visible = articles.filter(a => !EXCLUDE.includes(a.slug));
  const mapped = visible.map(a => ({
    slug: a.slug, title: a.title, description: a.description || '',
    category: a.category, tags: a.tags || [], readTime: a.readTime || 5,
    date: a.date || '', pinned: a.pinned || false,
  }));
  return <HomeClient articles={mapped} />;
}
