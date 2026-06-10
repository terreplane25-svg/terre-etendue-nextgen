import { notFound } from "next/navigation";
import { getArticle, getAllArticles } from "@/lib/articles";
import { getArticleImage } from "@/lib/article-images";
import ArticleReader from "@/components/ArticleReader";
import RelatedArticles from "@/components/RelatedArticles";
import ArticleNexusMini from "@/components/ArticleNexusMini";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const articles = getAllArticles();
  return articles.map((article) => ({ slug: article.slug }));
}

const SITE_URL = 'https://terre-etendue-islam.fr';

const CATEGORY_LABELS: Record<string, string> = {
  headquarters: 'Le Q.G. — Épistémologie',
  observatory: "L'Observatoire — Empirique",
  library: 'La Bibliothèque — Sources Sacrées',
  lab: 'Le Lab — Modélisation',
  meta: 'À propos',
};

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticle(slug);
  if (!article) return { title: "Article introuvable" };

  const categoryLabel = CATEGORY_LABELS[article.category] || article.category;

  return {
    title: article.title,
    description: article.description,
    keywords: article.tags?.join(', '),
    authors: [{ name: article.author || 'Collectif TEI' }],
    openGraph: {
      title: article.title,
      description: article.description,
      url: `${SITE_URL}/article/${slug}`,
      siteName: 'Terre Étendue Islam',
      locale: 'fr_FR',
      type: 'article',
      publishedTime: article.date,
      authors: [article.author || 'Collectif TEI'],
      tags: article.tags,
      images: [{ url: getArticleImage(slug), width: 600, height: 400 }],
    },
    twitter: {
      card: 'summary_large_image',
      title: article.title,
      description: article.description,
      images: [getArticleImage(slug)],
    },
    alternates: {
      canonical: `${SITE_URL}/article/${slug}`,
    },
    other: {
      'article:section': categoryLabel,
    },
  };
}

export default async function ArticlePage({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) notFound();

  const allArticles = getAllArticles().map(a => ({
    slug: a.slug,
    title: a.title,
    description: a.description || '',
    category: a.category,
    tags: a.tags || [],
  }));

  const jsonLd = {
    '@context': 'https://schema.org',
    '@type': 'Article',
    headline: article.title,
    description: article.description,
    datePublished: article.date,
    author: { '@type': 'Organization', name: article.author || 'Collectif TEI' },
    publisher: { '@type': 'Organization', name: 'Terre Étendue Islam' },
    url: `${SITE_URL}/article/${slug}`,
    mainEntityOfPage: `${SITE_URL}/article/${slug}`,
  };

  return (
    <main className="min-h-screen pt-24 pb-16" style={{ background: 'var(--bg)' }}>
      <script type="application/ld+json" dangerouslySetInnerHTML={{ __html: JSON.stringify(jsonLd) }} />
      <div className="article-layout" style={{ display: 'grid', gridTemplateColumns: '1fr', maxWidth: 1200, margin: '0 auto', gap: 32, padding: '0 24px' }}>
        <div>
          <ArticleReader article={article} />
          <div className="max-w-[800px] mx-auto px-6">
            <RelatedArticles
              currentSlug={slug}
              currentTags={article.tags || []}
              allArticles={allArticles}
            />
          </div>
        </div>
        <aside className="hidden lg:block">
          <ArticleNexusMini slug={slug} />
        </aside>
      </div>
    </main>
  );
}
