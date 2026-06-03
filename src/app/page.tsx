import { getAllArticles } from '@/lib/articles';
import HomeClient from './HomeClient';

const EXCLUDE_FROM_RECENT = [
  'le-mouvement-zetetique-150-ans-de-resistance',
];

export default function HomePage() {
  const articles = getAllArticles() as any[];
  const counts = {
    total: articles.length,
    headquarters: articles.filter(a => a.category === 'headquarters').length,
    observatory: articles.filter(a => a.category === 'observatory').length,
    library: articles.filter(a => a.category === 'library').length,
    lab: articles.filter(a => a.category === 'lab').length,
    experiments: articles.filter(a => a.tags?.includes('physique-naturelle')).length,
  };
  const recent = articles
    .filter(a => !EXCLUDE_FROM_RECENT.includes(a.slug))
    .slice(0, 6)
    .map(a => ({
      slug: a.slug, title: a.title, category: a.category,
      tags: a.tags || [], pinned: a.pinned || false, readTime: a.readTime || 5,
      date: a.date || '', description: a.description || '',
    }));
  return <HomeClient counts={counts} recent={recent} />;
}
