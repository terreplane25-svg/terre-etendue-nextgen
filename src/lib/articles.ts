import fs from 'fs';
import path from 'path';

const articlesDirectory = path.join(process.cwd(), 'content/articles');

export interface ArticleMeta {
  slug: string;
  title: string;
  description: string;
  date: string;
  author: string;
  category: 'headquarters' | 'observatory' | 'library' | 'lab';
  tags: string[];
}

export interface Article extends ArticleMeta {
  content: string;
  htmlContent: string;
}

function readArticleFile(fileName: string): ArticleMeta | null {
  const slug = fileName.replace(/\.(json|md)$/, '');
  const fullPath = path.join(articlesDirectory, fileName);
  const fileContents = fs.readFileSync(fullPath, 'utf8');

  if (fileName.endsWith('.json')) {
    const data = JSON.parse(fileContents);
    return {
      slug,
      title: data.title || slug,
      description: data.description || '',
      date: data.date || '',
      author: data.author || 'Terre Etendue',
      category: data.category || 'headquarters',
      tags: data.tags || [],
    };
  }

  return null;
}

export function getAllArticles(): ArticleMeta[] {
  if (!fs.existsSync(articlesDirectory)) return [];

  const fileNames = fs.readdirSync(articlesDirectory).filter(
    (f) => f.endsWith('.json') || f.endsWith('.md')
  );

  const articles = fileNames
    .map((fileName) => readArticleFile(fileName))
    .filter((a): a is ArticleMeta => a !== null);

  return articles.sort((a, b) => (a.date > b.date ? -1 : 1));
}

export async function getArticle(slug: string): Promise<Article | null> {
  // Try JSON first
  const jsonPath = path.join(articlesDirectory, `${slug}.json`);
  if (fs.existsSync(jsonPath)) {
    const fileContents = fs.readFileSync(jsonPath, 'utf8');
    const data = JSON.parse(fileContents);
    return {
      slug,
      title: data.title || slug,
      description: data.description || '',
      date: data.date || '',
      author: data.author || 'Terre Etendue',
      category: data.category || 'headquarters',
      tags: data.tags || [],
      content: data.htmlBody || '',
      htmlContent: data.htmlBody || '',
    };
  }

  return null;
}

export function getArticlesByCategory(category: string): ArticleMeta[] {
  return getAllArticles().filter((a) => a.category === category);
}

export function searchArticles(query: string): ArticleMeta[] {
  const q = query.toLowerCase();
  return getAllArticles().filter(
    (a) =>
      a.title.toLowerCase().includes(q) ||
      a.description.toLowerCase().includes(q) ||
      a.tags.some((t) => t.toLowerCase().includes(q))
  );
}
