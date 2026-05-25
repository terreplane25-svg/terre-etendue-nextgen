import { NextRequest, NextResponse } from 'next/server';
import { searchArticlesAdvanced } from '@/lib/articles';

export async function GET(request: NextRequest) {
  const q = request.nextUrl.searchParams.get('q') || '';
  const cats = request.nextUrl.searchParams.get('categories') || '';
  
  if (q.length < 2) {
    return NextResponse.json({ results: [], totalMs: 0, count: 0 });
  }

  const categories = cats ? cats.split(',').filter(Boolean) : undefined;
  const { results, totalMs } = searchArticlesAdvanced(q, categories);

  return NextResponse.json({
    results,
    totalMs,
    count: results.length,
  });
}
