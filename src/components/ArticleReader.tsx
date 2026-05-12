'use client';

import { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Clock, User, ChevronRight, List } from 'lucide-react';
import Link from 'next/link';
import ViewModeSwitch, { useViewMode } from '@/components/ViewModeSwitch';
import GlossaryTooltip, { GLOSSARY } from '@/components/GlossaryTooltip';
import type { Article } from '@/lib/articles';

// ─── Labels lisibles pour les categories ─────────
const CATEGORY_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  headquarters: { label: 'Le Q.G.', icon: '\u{1F9E0}', color: 'cyan' },
  observatory: { label: "L'Observatoire", icon: '\u{1F52D}', color: 'cyan' },
  library: { label: 'La Biblioth\u00e8que', icon: '\u{1F4DA}', color: 'gold' },
  lab: { label: 'Le Lab', icon: '\u2697\uFE0F', color: 'cyan' },
};

// ─── Table des matieres extraite du HTML ──────────
interface Heading {
  id: string;
  text: string;
  level: number;
}

function extractHeadings(html: string): Heading[] {
  const regex = /<h([23])[^>]*?(?:id="([^"]*)")?[^>]*>(.*?)<\/h\1>/gi;
  const headings: Heading[] = [];
  let match;
  while ((match = regex.exec(html)) !== null) {
    const level = parseInt(match[1]);
    const id = match[2] || match[3].toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    const text = match[3].replace(/<[^>]*>/g, '');
    if (text.trim().length > 0) {
      headings.push({ id, text: text.trim(), level });
    }
  }
  return headings;
}

function injectHeadingIds(html: string): string {
  return html.replace(/<h([234])([^>]*)>(.*?)<\/h\1>/gi, (full, level, attrs, content) => {
    if (attrs.includes('id=')) return full;
    const id = content.replace(/<[^>]*>/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    return `<h${level}${attrs} id="${id}">${content}</h${level}>`;
  });
}

function enrichWithGlossary(html: string): string {
  let result = html;
  for (const [key, entry] of Object.entries(GLOSSARY)) {
    const pattern = new RegExp(`(?<![<\\/a-z])\\b(${key}|${entry.title.split(' ')[0]})\\b(?![^<]*>)`, 'gi');
    let replaced = false;
    result = result.replace(pattern, (match) => {
      if (replaced) return match;
      replaced = true;
      return `<span class="glossary-inline" data-term="${key}">${match}</span>`;
    });
  }
  return result;
}

function enhanceArabicText(html: string): string {
  return html.replace(
    /([\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\uFC00-\uFCFF]{3,}(?:\s[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\uFC00-\uFCFF]+)*)/g,
    '<span class="arabic-text">$1</span>'
  );
}

// ─── Composant Principal ──────────────────────────
interface ArticleReaderProps {
  article: Article;
}

export default function ArticleReader({ article }: ArticleReaderProps) {
  const { mode } = useViewMode();
  const [activeHeading, setActiveHeading] = useState('');
  const [tocOpen, setTocOpen] = useState(false);

  const processedHtml = useMemo(() => {
    let html = injectHeadingIds(article.htmlContent);
    html = enrichWithGlossary(html);
    html = enhanceArabicText(html);
    return html;
  }, [article.htmlContent]);

  const headings = useMemo(() => extractHeadings(processedHtml), [processedHtml]);

  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveHeading(entry.target.id);
          }
        }
      },
      { rootMargin: '-20% 0px -70% 0px' }
    );
    const elements = document.querySelectorAll('.prose-tei h2, .prose-tei h3');
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [processedHtml]);

  const date = new Date(article.date).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const wordCount = article.htmlContent.replace(/<[^>]*>/g, '').split(/\s+/).length;
  const readingTime = Math.ceil(wordCount / 200);
  const catInfo = CATEGORY_LABELS[article.category] || CATEGORY_LABELS.headquarters;

  const backMap: Record<string, string> = {
    headquarters: '/headquarters',
    observatory: '/observatory',
    library: '/library',
    lab: '/lab',
  };

  return (
    <div className="min-h-screen pt-24">
      {/* Top bar */}
      <div className="max-w-6xl mx-auto px-6 mb-8 flex items-center justify-between">
        <Link
          href={backMap[article.category] || '/'}
          className="inline-flex items-center gap-1.5 text-sm text-obs-text-secondary hover:text-obs-cyan transition-colors"
        >
          <ArrowLeft size={16} />
          {catInfo.label}
        </Link>
        <div className="flex items-center gap-3">
          {headings.length > 0 && (
            <button
              onClick={() => setTocOpen(!tocOpen)}
              className="xl:hidden flex items-center gap-1.5 text-sm text-obs-text-secondary hover:text-obs-cyan transition-colors px-3 py-1.5 rounded-lg border border-obs-border"
            >
              <List size={14} />
              Sommaire
            </button>
          )}
          <ViewModeSwitch />
        </div>
      </div>

      {/* Mobile TOC dropdown */}
      <AnimatePresence>
        {tocOpen && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: 'auto' }}
            exit={{ opacity: 0, height: 0 }}
            className="xl:hidden max-w-3xl mx-auto px-6 mb-6 overflow-hidden"
          >
            <nav className="bg-obs-surface border border-obs-border rounded-xl p-4 space-y-1">
              {headings.map((h) => (
                <a
                  key={h.id}
                  href={`#${h.id}`}
                  onClick={() => setTocOpen(false)}
                  className={`block text-sm py-1.5 transition-colors ${
                    h.level > 2 ? 'pl-4 text-xs' : 'font-medium'
                  } text-obs-text-secondary hover:text-obs-cyan`}
                >
                  {h.text}
                </a>
              ))}
            </nav>
          </motion.div>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl mx-auto px-6 pb-10 space-y-5 border-b border-obs-border"
      >
        <span className={`inline-flex items-center gap-1.5 text-xs px-3 py-1.5 rounded-full font-medium tracking-wide ${
          catInfo.color === 'gold'
            ? 'bg-obs-gold/10 text-obs-gold'
            : 'bg-obs-cyan/10 text-obs-cyan'
        }`}>
          <span>{catInfo.icon}</span>
          {catInfo.label}
        </span>

        <h1 className="font-display font-bold text-3xl md:text-4xl lg:text-[2.75rem] text-obs-text-primary leading-[1.15]">
          {article.title}
        </h1>

        {article.description && (
          <p className="text-lg text-obs-text-secondary/80 font-serif leading-relaxed">
            {article.description}
          </p>
        )}

        <div className="flex flex-wrap gap-5 text-sm text-obs-text-secondary pt-2">
          <span className="flex items-center gap-1.5">
            <Clock size={14} className="text-obs-cyan/60" />
            {readingTime} min de lecture
          </span>
          <span className="flex items-center gap-1.5">
            <User size={14} className="text-obs-cyan/60" />
            {article.author || 'Collectif TEI'}
          </span>
          <time dateTime={article.date} className="text-obs-text-secondary/60">{date}</time>
        </div>
      </motion.header>

      {/* Body */}
      <div className="max-w-6xl mx-auto px-6 flex gap-12 pt-12 pb-20">
        {/* TOC Sidebar desktop */}
        <AnimatePresence>
          {mode === 'study' && headings.length > 0 && (
            <motion.aside
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              className="hidden xl:block w-60 shrink-0 sticky top-24 self-start max-h-[calc(100vh-8rem)] overflow-y-auto pr-4"
            >
              <p className="text-[0.65rem] font-display font-semibold uppercase tracking-[0.2em] text-obs-text-secondary/50 mb-5">
                Sommaire
              </p>
              <nav className="space-y-0.5 border-l border-obs-border">
                {headings.map((h) => (
                  <a
                    key={h.id}
                    href={`#${h.id}`}
                    className={`block text-[0.8rem] leading-snug transition-all duration-200 py-1.5 ${
                      h.level > 2 ? 'pl-6' : 'pl-4'
                    } ${
                      activeHeading === h.id
                        ? 'text-obs-cyan border-l-2 border-obs-cyan -ml-px font-medium'
                        : 'text-obs-text-secondary/60 hover:text-obs-text-primary border-l-2 border-transparent -ml-px'
                    }`}
                  >
                    {h.text}
                  </a>
                ))}
              </nav>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Article Content */}
        <motion.article
          layout
          className={`flex-1 min-w-0 ${mode === 'lab' ? 'max-w-4xl mx-auto' : 'max-w-3xl'}`}
        >
          <AnimatePresence mode="wait">
            {mode === 'study' ? (
              <motion.div
                key="study"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="prose-tei"
                dangerouslySetInnerHTML={{ __html: processedHtml }}
              />
            ) : (
              <motion.div
                key="lab"
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
                className="space-y-8"
              >
                <div className="bg-obs-surface border border-obs-cyan/20 rounded-xl p-6 space-y-4">
                  <h3 className="font-display font-semibold text-obs-cyan flex items-center gap-2">
                    <ChevronRight size={16} /> Vue Lab
                  </h3>
                  <p className="text-sm text-obs-text-secondary">
                    Titres, citations, tableaux et listes uniquement.
                  </p>
                </div>
                <div
                  className="prose-tei [&>p]:hidden [&>h2]:block [&>h3]:block [&>blockquote]:block [&>table]:block [&>ul]:block [&>ol]:block [&>pre]:block"
                  dangerouslySetInnerHTML={{ __html: processedHtml }}
                />
              </motion.div>
            )}
          </AnimatePresence>

          {/* Article footer */}
          <div className="mt-16 pt-8 border-t border-obs-border">
            <div className="flex items-center justify-between">
              <Link
                href={backMap[article.category] || '/'}
                className="inline-flex items-center gap-1.5 text-sm text-obs-text-secondary hover:text-obs-cyan transition-colors"
              >
                <ArrowLeft size={14} />
                Retour
              </Link>
              <Link
                href="/nexus"
                className="inline-flex items-center gap-1.5 text-sm text-obs-text-secondary hover:text-obs-cyan transition-colors"
              >
                Voir dans le Nexus
                <ChevronRight size={14} />
              </Link>
            </div>
          </div>
        </motion.article>
      </div>
    </div>
  );
}
