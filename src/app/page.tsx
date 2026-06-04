import { getAllArticles } from '@/lib/articles';
import HomeClient from './HomeClient';

const EXCLUDE = ['le-mouvement-zetetique-150-ans-de-resistance'];

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

  const obsArticles = articles.filter(a => a.category === 'observatory' && !a.tags?.includes('physique-naturelle')).slice(0, 6);
  const expArticles = articles.filter(a => a.tags?.includes('physique-naturelle')).slice(0, 6);
  const libArticles = articles.filter(a => a.category === 'library').slice(0, 6);

  const mapA = (a: any) => ({ id: a.slug, title: a.title, description: a.description || '', href: `/article/${a.slug}`, image: '' });

  return <HomeClient
    counts={counts}
    obsArticles={obsArticles.map(mapA)}
    expArticles={expArticles.map(mapA)}
    libArticles={libArticles.map(mapA)}
  />;
}
