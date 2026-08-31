import fs from 'fs';
import path from 'path';
import { annotateGlossary } from './glossary';

const articlesDirectory = path.join(process.cwd(), 'content/articles');

/**
 * QW2: Sanitize article descriptions — strip CSS artifacts from Elementor migration.
 * Catches patterns like .nx-nav{width:100%;...} that leaked into descriptions.
 */
function sanitizeDescription(raw: string): string {
  if (!raw) return '';
  let clean = raw;
  // Strip CSS rule blocks: .class{...} or tag{...}
  clean = clean.replace(/[.#]?[\w-]+\{[^}]*\}/g, '');
  // Strip @import, @font-face
  clean = clean.replace(/@[\w-]+[^;]*;/g, '');
  // Strip remaining CSS-like artifacts: property:value pairs outside tags
  clean = clean.replace(/[\w-]+:\s*[^;{}"']+;/g, '');
  // Collapse whitespace
  clean = clean.replace(/\s{2,}/g, ' ').trim();
  // If description is now too short or empty, return fallback
  if (clean.length < 20) return '';
  return clean;
}

export interface ArticleMeta {
  slug: string;
  title: string;
  description: string;
  date: string;
  /** Date de dernière révision de fond. Absente si l'article n'a pas été repris. */
  updated?: string;
  author: string;
  category: 'headquarters' | 'observatory' | 'library' | 'lab' | 'meta' | 'experiences';
  tags: string[];
  pinned?: boolean;
  readTime?: number; // minutes, calculated from htmlBody
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
    // Calculate read time from actual htmlBody content
    const bodyText = (data.htmlBody || '').replace(/<[^>]+>/g, ' ').replace(/\s+/g, ' ').trim();
    const wordCount = bodyText.split(/\s+/).filter((w: string) => w.length > 0).length;
    const readTime = Math.max(2, Math.ceil(wordCount / 200)); // 200 words/min average
    return {
      slug,
      title: data.title || slug,
      description: sanitizeDescription(data.description || ''),
      date: data.date || '',
      updated: data.updated || undefined,
      author: data.author || 'Terre Etendue',
      category: data.category || 'headquarters',
      tags: data.tags || [],
      pinned: data.pinned || false,
      readTime,
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

  return articles.sort((a, b) => {
    // Pinned articles first
    if (a.pinned && !b.pinned) return -1;
    if (!a.pinned && b.pinned) return 1;
    // Then by date descending
    return a.date > b.date ? -1 : 1;
  });
}

export async function getArticle(slug: string): Promise<Article | null> {
  // Try JSON first
  const jsonPath = path.join(articlesDirectory, `${slug}.json`);
  if (fs.existsSync(jsonPath)) {
    const fileContents = fs.readFileSync(jsonPath, 'utf8');
    const data = JSON.parse(fileContents);
    // Annotation des termes du glossaire (survol -> définition), faite une
    // seule fois : les identifiants d'infobulle doivent rester uniques dans
    // le document si les deux champs venaient à être rendus ensemble.
    const annote = annotateGlossary(data.htmlBody || '', slug);
    return {
      slug,
      title: data.title || slug,
      description: sanitizeDescription(data.description || ''),
      date: data.date || '',
      updated: data.updated || undefined,
      author: data.author || 'Terre Etendue',
      category: data.category || 'headquarters',
      tags: data.tags || [],
      content: annote,
      htmlContent: annote,
    };
  }

  return null;
}

export function getArticlesByCategory(category: string): ArticleMeta[] {
  return getAllArticles().filter((a) => a.category === category);
}

export function searchArticles(query: string): ArticleMeta[] {
  const q = query.toLowerCase();
  
  if (!fs.existsSync(articlesDirectory)) return [];
  
  const fileNames = fs.readdirSync(articlesDirectory).filter(f => f.endsWith('.json'));
  
  const scored: { meta: ArticleMeta; score: number }[] = [];
  
  for (const fileName of fileNames) {
    const slug = fileName.replace('.json', '');
    const fullPath = path.join(articlesDirectory, fileName);
    const fileContents = fs.readFileSync(fullPath, 'utf8');
    const data = JSON.parse(fileContents);
    
    let score = 0;
    
    // Title match = highest priority
    if (data.title?.toLowerCase().includes(q)) score += 10;
    
    // Description match
    if (data.description?.toLowerCase().includes(q)) score += 5;
    
    // Tags match
    if (data.tags?.some((t: string) => t.toLowerCase().includes(q))) score += 3;
    
    // Body content match (strip HTML)
    const bodyText = (data.htmlBody || '').replace(/<[^>]+>/g, '').toLowerCase();
    if (bodyText.includes(q)) score += 1;
    
    if (score > 0) {
      scored.push({
        meta: {
          slug,
          title: data.title || slug,
          description: sanitizeDescription(data.description || ''),
          date: data.date || '',
          author: data.author || 'Terre Etendue',
          category: data.category || 'headquarters',
          tags: data.tags || [],
        },
        score,
      });
    }
  }
  
  return scored
    .sort((a, b) => b.score - a.score)
    .map((s) => s.meta);
}

/**
 * Le nombre de sources classées A/B/C/D dans tout le corpus.
 *
 * Compté plutôt qu'écrit en dur : le pied de page annonçait « 450+ sources »
 * depuis des mois, sans que rien ne relie ce nombre au corpus. Sur un site dont
 * la règle est de publier le chiffre exact, un ordre de grandeur figé est
 * exactement ce qu'il ne faut pas faire — d'autant qu'il se démode dans le
 * mauvais sens, en sous-estimant le travail fait.
 *
 * Les renvois vers nos propres articles (`grade-lien`) sont exclus : ce ne sont
 * pas des sources, et les compter reviendrait à se citer soi-même.
 */
export function countSources(): number {
  if (!fs.existsSync(articlesDirectory)) return 0;
  let total = 0;
  for (const fileName of fs.readdirSync(articlesDirectory)) {
    if (!fileName.endsWith('.json')) continue;
    const raw = fs.readFileSync(path.join(articlesDirectory, fileName), 'utf8');
    const body = (JSON.parse(raw).htmlBody as string) || '';
    total += (body.match(/tei-grade grade-[abcd]"/g) || []).length;
  }
  return total;
}
