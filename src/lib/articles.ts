import fs from 'fs';
import path from 'path';
import matter from 'gray-matter';
import { remark } from 'remark';
import html from 'remark-html';

const articlesDirectory = path.join(process.cwd(), 'content/articles');

export interface ArticleMeta {
  slug: string;
  title: string;
  description: string;
  date: string;
  author: string;
  category: 'headquarters' | 'observatory' | 'library' | 'lab';
  tags: string[];
  connections?: string[];
}

export interface Article extends ArticleMeta {
  content: string;
  htmlContent: string;
}

export function getAllArticles(): ArticleMeta[] {
  if (!fs.existsSync(articlesDirectory)) return [];

  const fileNames = fs.readdirSync(articlesDirectory).filter(f => f.endsWith('.md'));

  const articles = fileNames.map((fileName) => {
    const slug = fileName.replace(/\.md$/, '');
    const fullPath = path.join(articlesDirectory, fileName);
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    const { data } = matter(fileContents);

    return {
      slug,
      title: data.title || slug,
      description: data.description || '',
      date: data.date || '',
      author: data.author || 'Anonyme',
      category: data.category || 'headquarters',
      tags: data.tags || [],
      connections: data.connections || [],
    } as ArticleMeta;
  });

  return articles.sort((a, b) => (a.date > b.date ? -1 : 1));
}

export async function getArticle(slug: string): Promise<Article | null> {
  const fullPath = path.join(articlesDirectory, `${slug}.md`);

  if (!fs.existsSync(fullPath)) return null;

  const fileContents = fs.readFileSync(fullPath, 'utf8');
  const { data, content } = matter(fileContents);

  const processedContent = await remark().use(html).process(content);
  const htmlContent = processedContent.toString();

  return {
    slug,
    title: data.title || slug,
    description: data.description || '',
    date: data.date || '',
    author: data.author || 'Anonyme',
    category: data.category || 'headquarters',
    tags: data.tags || [],
    connections: data.connections || [],
    content,
    htmlContent,
  };
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
