'use client';

import { useEffect, useState, useMemo } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Clock, User, ChevronRight } from 'lucide-react';
import Link from 'next/link';
import ViewModeSwitch, { useViewMode } from '@/components/ViewModeSwitch';
import GlossaryTooltip, { GLOSSARY } from '@/components/GlossaryTooltip';
import type { Article } from '@/lib/articles';

// ─── Table des matières extraite du HTML ──────────
interface Heading {
  id: string;
  text: string;
  level: number;
}

function extractHeadings(html: string): Heading[] {
  // Regex pour trouver h2/h3/h4 dans le HTML
  const regex = /<h([234])[^>]*?(?:id="([^"]*)")?[^>]*>(.*?)<\/h\1>/gi;
  const headings: Heading[] = [];
  let match;
  while ((match = regex.exec(html)) !== null) {
    const level = parseInt(match[1]);
    const id = match[2] || match[3].toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    const text = match[3].replace(/<[^>]*>/g, ''); // strip inner HTML
    headings.push({ id, text, level });
  }
  return headings;
}

// ─── Injecter des IDs dans les headings HTML ──────
function injectHeadingIds(html: string): string {
  return html.replace(/<h([234])([^>]*)>(.*?)<\/h\1>/gi, (full, level, attrs, content) => {
    if (attrs.includes('id=')) return full;
    const id = content.replace(/<[^>]*>/g, '').toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '');
    return `<h${level}${attrs} id="${id}">${content}</h${level}>`;
  });
}

// ─── Enrichir le HTML avec les termes du glossaire ─
function enrichWithGlossary(html: string): string {
  let result = html;
  for (const [key, entry] of Object.entries(GLOSSARY)) {
    // Créer un pattern qui matche le terme (insensible à la casse) SAUF dans les tags HTML
    const pattern = new RegExp(`(?<![<\\/a-z])\\b(${key}|${entry.title.split(' ')[0]})\\b(?![^<]*>)`, 'gi');
    // Remplacer la première occurrence uniquement
    let replaced = false;
    result = result.replace(pattern, (match) => {
      if (replaced) return match;
      replaced = true;
      return `<span class="glossary-inline" data-term="${key}">${match}</span>`;
    });
  }
  return result;
}

// ─── Composant Principal ──────────────────────────
interface ArticleReaderProps {
  article: Article;
}

export default function ArticleReader({ article }: ArticleReaderProps) {
  const { mode } = useViewMode();
  const [activeHeading, setActiveHeading] = useState('');

  // Process le HTML
  const processedHtml = useMemo(() => {
    let html = injectHeadingIds(article.htmlContent);
    html = enrichWithGlossary(html);
    return html;
  }, [article.htmlContent]);

  const headings = useMemo(() => extractHeadings(processedHtml), [processedHtml]);

  // Observer les headings pour la TOC active
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

    const elements = document.querySelectorAll('.prose-tei h2, .prose-tei h3, .prose-tei h4');
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [processedHtml]);

  // Metadata
  const date = new Date(article.date).toLocaleDateString('fr-FR', {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const wordCount = article.htmlContent.replace(/<[^>]*>/g, '').split(/\s+/).length;
  const readingTime = Math.ceil(wordCount / 200);

  // Le back href selon la catégorie
  const backMap: Record<string, string> = {
    headquarters: '/headquarters',
    observatory: '/observatory',
    library: '/library',
    lab: '/lab',
  };

  return (
    <div className="min-h-screen pt-24">
      {/* Top bar */}
      <div className="max-w-6xl mx-auto px-6 mb-8 flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <Link
          href={backMap[article.category] || '/'}
          className="inline-flex items-center gap-1.5 text-sm text-obs-text-secondary hover:text-obs-cyan transition-colors"
        >
          <ArrowLeft size={16} />
          Retour
        </Link>
        <ViewModeSwitch />
      </div>

      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-3xl mx-auto px-6 pb-10 space-y-5 border-b border-obs-border"
      >
        <div className="flex flex-wrap gap-2">
          <span className="text-xs px-2.5 py-1 rounded-full bg-obs-cyan/10 text-obs-cyan uppercase tracking-wider font-medium">
            {article.category}
          </span>
          {article.tags?.map((tag) => (
            <span key={tag} className="text-xs px-2.5 py-1 rounded-full bg-obs-gold/10 text-obs-gold uppercase tracking-wider">
              {tag}
            </span>
          ))}
        </div>

        <h1 className="text-display font-display font-bold text-obs-text-primary leading-tight">
          {article.title}
        </h1>

        <div className="flex flex-wrap gap-5 text-sm text-obs-text-secondary">
          <span className="flex items-center gap-1.5">
            <Clock size={14} className="text-obs-cyan" />
            {readingTime} min
          </span>
          <span className="flex items-center gap-1.5">
            <User size={14} className="text-obs-cyan" />
            {article.author || 'Collectif TEI'}
          </span>
          <time dateTime={article.date}>{date}</time>
        </div>
      </motion.header>

      {/* Body */}
      <div className="max-w-6xl mx-auto px-6 flex gap-10 pt-10 pb-20">
        {/* TOC Sidebar — visible en mode Étude */}
        <AnimatePresence>
          {mode === 'study' && headings.length > 0 && (
            <motion.aside
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              className="hidden xl:block w-56 shrink-0 sticky top-24 self-start max-h-[calc(100vh-8rem)] overflow-y-auto"
            >
              <p className="text-xs font-display font-semibold uppercase tracking-widest text-obs-text-secondary mb-4">
                Sommaire
              </p>
              <nav className="space-y-1.5">
                {headings.map((h) => (
                  <a
                    key={h.id}
                    href={`#${h.id}`}
                    className={`block text-sm transition-colors py-0.5 ${
                      h.level > 2 ? 'pl-4' : ''
                    } ${
                      activeHeading === h.id
                        ? 'text-obs-cyan font-medium'
                        : 'text-obs-text-secondary hover:text-obs-text-primary'
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
                {/* Mode Lab : focus sur les blocs de données, citations, tables */}
                <div className="bg-obs-surface border border-obs-cyan/20 rounded-xl p-6 space-y-4">
                  <h3 className="font-display font-semibold text-obs-cyan flex items-center gap-2">
                    <ChevronRight size={16} /> Vue Lab — Données Extraites
                  </h3>
                  <p className="text-sm text-obs-text-secondary">
                    Ce mode filtre l'article pour mettre en avant les données quantifiables, les citations sources, et les modèles référencés.
                  </p>
                </div>

                {/* Rendre le HTML mais avec un style plus "data" */}
                <div
                  className="prose-tei [&>p]:hidden [&>h2]:block [&>h3]:block [&>blockquote]:block [&>table]:block [&>ul]:block [&>ol]:block [&>pre]:block"
                  dangerouslySetInnerHTML={{ __html: processedHtml }}
                />
              </motion.div>
            )}
          </AnimatePresence>
        </motion.article>
      </div>
    </div>
  );
}
