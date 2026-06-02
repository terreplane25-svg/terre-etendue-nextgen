import { getAllArticles } from '@/lib/articles';
import HomeClient from './HomeClient';

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

  const recent = articles.slice(0, 6).map(a => ({
    slug: a.slug,
    title: a.title,
    category: a.category,
    tags: a.tags || [],
    pinned: a.pinned || false,
    readTime: a.readTime || 5,
  }));

  return <HomeClient counts={counts} recent={recent} />;
}
