import { NextRequest, NextResponse } from 'next/server';
import { searchArticles } from '@/lib/articles';

export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get('q') || '';
  
  if (q.length < 2) {
    return NextResponse.json({ results: [] });
  }

  const articles = searchArticles(q);
  
  const results = articles.slice(0, 8).map((a) => ({
    title: a.title,
    slug: a.slug,
    category: a.category,
    excerpt: a.description.substring(0, 120),
  }));

  return NextResponse.json({ results });
}
