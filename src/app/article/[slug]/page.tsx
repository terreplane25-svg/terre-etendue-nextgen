import { notFound } from "next/navigation";
import { getArticle, getAllArticles } from "@/lib/articles";
import ArticleReader from "@/components/ArticleReader";

interface PageProps {
  params: Promise<{ slug: string }>;
}

export async function generateStaticParams() {
  const articles = getAllArticles();
  return articles.map((article) => ({ slug: article.slug }));
}

export async function generateMetadata({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticle(slug);
  if (!article) return { title: "Article introuvable" };
  return {
    title: article.title + " — Terre Etendue Islam",
    description: article.description,
  };
}

export default async function ArticlePage({ params }: PageProps) {
  const { slug } = await params;
  const article = await getArticle(slug);

  if (!article) notFound();

  return (
    <main className="min-h-screen bg-obs-dark pt-24 pb-16">
      <ArticleReader
        title={article.title}
        description={article.description}
        date={article.date}
        author={article.author}
        category={article.category}
        tags={article.tags}
        htmlContent={article.htmlContent}
      />
    </main>
  );
}
