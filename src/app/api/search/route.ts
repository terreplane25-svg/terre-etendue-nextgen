import { NextRequest, NextResponse } from 'next/server';
import { searchArticles } from '@/lib/articles';

export async function GET(request: NextRequest) {
  const start = Date.now();
  const q = request.nextUrl.searchParams.get('q') || '';
  const categories = request.nextUrl.searchParams.get('categories')?.split(',').filter(Boolean) || [];

  if (q.length < 2) {
    return NextResponse.json({ results: [], count: 0, totalMs: 0 });
  }

  let articles = searchArticles(q);

  // Filtrer par catégories si spécifiées
  if (categories.length > 0) {
    articles = articles.filter(a => categories.includes(a.category));
  }

  const results = articles.slice(0, 10).map((a, i) => ({
    title: a.title,
    slug: a.slug,
    category: a.category,
    description: a.description || '',
    tags: a.tags || [],
    date: a.date || '',
    readTime: a.readTime,
    score: Math.max(10, 100 - i * 12),
  }));

  const totalMs = Date.now() - start;

  return NextResponse.json({ results, count: results.length, totalMs });
}
