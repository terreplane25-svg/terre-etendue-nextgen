'use client';

import { useEffect, useState, useMemo, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ArrowLeft, Clock, User, ChevronRight, List, X } from 'lucide-react';
import Link from 'next/link';
import ViewModeSwitch, { useViewMode } from '@/components/ViewModeSwitch';
import { GLOSSARY } from '@/components/GlossaryTooltip';
import type { Article } from '@/lib/articles';

// ─── Labels lisibles ─────────────────────────────
const CATEGORY_LABELS: Record<string, { label: string; icon: string; color: string }> = {
  headquarters: { label: 'Le Q.G.', icon: '\u{1F9E0}', color: 'cyan' },
  observatory: { label: "L'Observatoire", icon: '\u{1F52D}', color: 'cyan' },
  library: { label: 'La Bibliothèque', icon: '\u{1F4DA}', color: 'gold' },
  lab: { label: 'Le Lab', icon: '\u2697\uFE0F', color: 'cyan' },
};

// ─── Types ───────────────────────────────────────
interface Heading {
  id: string;
  text: string;
  level: number;
  number: string;
}

// ─── Extraction des headings ─────────────────────
function extractHeadings(html: string): Heading[] {
  // Match full h2/h3 tags including all attributes and content
  const regex = /<h([23])(\s[^>]*)?>(.+?)<\/h\1>/gi;
  const headings: Heading[] = [];
  let match;
  while ((match = regex.exec(html)) !== null) {
    const level = parseInt(match[1]);
    const attrs = match[2] || '';
    const rawText = match[3];

    // Extract ID from attributes (separate regex, much more reliable)
    const idMatch = attrs.match(/id="([^"]*)"/);

    // Extract section number
    const numMatch = rawText.match(/tei-section-num">(\d+)<\/span>/);
    const number = numMatch ? numMatch[1] : '';

    // Clean text
    let text = rawText.replace(/<[^>]+>/g, '').trim();
    if (number && text.startsWith(number)) {
      text = text.substring(number.length).trim();
    }

    // Use existing ID from HTML, or generate from text as fallback
    const id = idMatch ? idMatch[1] : text.toLowerCase()
      .replace(/[^a-z0-9à-\u00ff]+/g, '-')
      .replace(/^-|-$/g, '');

    if (text.length > 0) {
      headings.push({ id, text, level, number });
    }
  }
  return headings;
}

// ─── Injection d'IDs dans les headings ───────────
function injectHeadingIds(html: string): string {
  return html.replace(/<h([234])([^>]*)>(.*?)<\/h\1>/gi, (full, level, attrs, content) => {
    if (attrs.includes('id=')) return full;
    const text = content.replace(/<[^>]+>/g, '').trim();
    // Remove leading numbers for ID generation
    const cleanText = text.replace(/^\d+\s*/, '');
    const id = cleanText.toLowerCase()
      .replace(/[^a-z0-9à-\u00ff]+/g, '-')
      .replace(/^-|-$/g, '');
    return `<h${level}${attrs} id="${id}">${content}</h${level}>`;
  });
}

// ─── Enrichissement glossaire ────────────────────
function enrichWithGlossary(html: string): string {
  let result = html;
  
  // Sort terms by length (longest first) to avoid partial matches
  const sortedTerms = Object.entries(GLOSSARY).sort((a, b) => b[0].length - a[0].length);
  
  for (const [key, entry] of sortedTerms) {
    // Build pattern: match the key or the title, case-insensitive
    // Avoid matching inside HTML tags or attributes
    const escapedKey = key.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    const pattern = new RegExp(
      `(?<![<\\/\\w-])\\b(${escapedKey})\\b(?![^<]*>)(?![^<]*<\\/a>)`,
      'gi'
    );
    
    let count = 0;
    const maxOccurrences = 2; // Mark first 2 occurrences
    
    result = result.replace(pattern, (match) => {
      if (count >= maxOccurrences) return match;
      // Don't replace if already inside a glossary span or link
      count++;
      return `<span class="glossary-inline" data-term="${key}">${match}</span>`;
    });
  }
  return result;
}

// ─── Détection texte arabe ───────────────────────
function enhanceArabicText(html: string): string {
  return html.replace(
    /([\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\uFC00-\uFCFF]{3,}(?:\s[\u0600-\u06FF\u0750-\u077F\uFB50-\uFDFF\uFE70-\uFEFF\uFC00-\uFCFF]+)*)/g,
    '<span class="tei-arabic">$1</span>'
  );
}

// ─── Composant Principal ─────────────────────────
interface ArticleReaderProps {
  article: Article;
}

export default function ArticleReader({ article }: ArticleReaderProps) {
  const { mode } = useViewMode();
  const [activeHeading, setActiveHeading] = useState('');
  const [tocOpen, setTocOpen] = useState(false);
  const [readProgress, setReadProgress] = useState(0);

  // Process HTML
  const processedHtml = useMemo(() => {
    let html = injectHeadingIds(article.htmlContent);
    html = enrichWithGlossary(html);
    html = enhanceArabicText(html);
    return html;
  }, [article.htmlContent]);

  const headings = useMemo(() => extractHeadings(processedHtml), [processedHtml]);

  // Reading progress bar
  useEffect(() => {
    const onScroll = () => {
      const scrollTop = window.scrollY;
      const docHeight = document.documentElement.scrollHeight - window.innerHeight;
      setReadProgress(docHeight > 0 ? Math.min(scrollTop / docHeight, 1) : 0);
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  // Heading intersection observer
  useEffect(() => {
    const observer = new IntersectionObserver(
      (entries) => {
        for (const entry of entries) {
          if (entry.isIntersecting) {
            setActiveHeading(entry.target.id);
          }
        }
      },
      { rootMargin: '-80px 0px -70% 0px' }
    );
    const elements = document.querySelectorAll('.prose-tei h2[id], .prose-tei h3[id]');
    elements.forEach((el) => observer.observe(el));
    return () => observer.disconnect();
  }, [processedHtml]);

  // Smooth scroll to heading
  const scrollToHeading = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) {
      const y = el.getBoundingClientRect().top + window.scrollY - 100;
      window.scrollTo({ top: y, behavior: 'smooth' });
      setTocOpen(false);
    }
  }, []);

  // Metadata
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
      {/* Reading progress bar */}
      <div className="fixed top-0 left-0 right-0 z-50 h-[3px] bg-transparent">
        <motion.div
          className="h-full bg-gradient-to-r from-[#00C8FF] to-[#00C8FF]/60"
          style={{ width: `${readProgress * 100}%` }}
          transition={{ duration: 0.1 }}
        />
      </div>

      {/* Top bar */}
      <div className="max-w-6xl mx-auto px-6 mb-8 flex items-center justify-between">
        <Link
          href={backMap[article.category] || '/'}
          className="inline-flex items-center gap-1.5 text-sm text-[#C8D8E8]/40 hover:text-[#00C8FF] transition-colors"
        >
          <ArrowLeft size={16} />
          {catInfo.label}
        </Link>
        <div className="flex items-center gap-3">
          {headings.length > 0 && (
            <button
              onClick={() => setTocOpen(true)}
              className="xl:hidden flex items-center gap-1.5 text-sm text-[#C8D8E8]/40 hover:text-[#00C8FF] transition-colors px-3 py-1.5 rounded-lg border border-white/[0.06]"
            >
              <List size={14} />
              Sommaire
            </button>
          )}
          <ViewModeSwitch />
        </div>
      </div>

      {/* Mobile TOC drawer overlay */}
      <AnimatePresence>
        {tocOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/60 z-40 xl:hidden"
              onClick={() => setTocOpen(false)}
            />
            <motion.div
              initial={{ x: '-100%' }}
              animate={{ x: 0 }}
              exit={{ x: '-100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 250 }}
              className="fixed left-0 top-0 bottom-0 w-80 max-w-[85vw] bg-[#050A12] border-r border-white/[0.06] z-50 xl:hidden overflow-y-auto"
            >
              <div className="p-6">
                <div className="flex items-center justify-between mb-6">
                  <p className="text-xs font-['Orbitron',sans-serif] font-semibold uppercase tracking-[0.2em] text-[#C8D8E8]/40/50">
                    Sommaire
                  </p>
                  <button
                    onClick={() => setTocOpen(false)}
                    className="p-1.5 rounded-lg hover:bg-[#0D1528] text-[#C8D8E8]/40"
                  >
                    <X size={18} />
                  </button>
                </div>

                {/* Progress in drawer */}
                <div className="mb-6 h-1 bg-[#0D1528] rounded-full overflow-hidden">
                  <div
                    className="h-full bg-[#00C8FF]/50 rounded-full transition-all duration-300"
                    style={{ width: `${readProgress * 100}%` }}
                  />
                </div>

                <nav className="space-y-1">
                  {headings.map((h) => (
                    <button
                      key={h.id}
                      onClick={() => scrollToHeading(h.id)}
                      className={`w-full text-left flex items-start gap-2.5 py-2 px-3 rounded-lg transition-all duration-200 ${
                        h.level > 2 ? 'ml-4' : ''
                      } ${
                        activeHeading === h.id
                          ? 'bg-[#00C8FF]/10 text-[#00C8FF]'
                          : 'text-[#C8D8E8]/40/70 hover:text-[#C8D8E8] hover:bg-[#0D1528]/50'
                      }`}
                    >
                      {h.number && h.level === 2 && (
                        <span className={`text-[0.65rem] font-bold font-mono mt-0.5 flex-shrink-0 w-5 ${
                          activeHeading === h.id ? 'text-[#00C8FF]' : 'text-[#00C8FF]/40'
                        }`}>
                          {h.number}
                        </span>
                      )}
                      <span className={`text-sm leading-snug ${h.level > 2 ? 'text-xs' : ''}`}>
                        {h.text}
                      </span>
                    </button>
                  ))}
                </nav>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>

      {/* Header */}
      <motion.header
        initial={{ opacity: 0, y: 16 }}
        animate={{ opacity: 1, y: 0 }}
        className="max-w-4xl mx-auto px-8 lg:px-12 pb-12 space-y-6 border-b border-white/[0.06]"
      >
        <span className={`inline-flex items-center gap-2 text-[11px] px-4 py-2 font-medium tracking-widest ${
          catInfo.color === 'gold'
            ? 'bg-[#D4A843]/10 text-[#D4A843]'
            : 'bg-[#00C8FF]/10 text-[#00C8FF]'
        }`} style={{fontFamily: 'Share Tech Mono, monospace', letterSpacing: '0.15em'}}>
          <span>{catInfo.icon}</span>
          {catInfo.label}
        </span>

        <h1 className="font-bold text-[clamp(1.8rem,4vw,2.8rem)] text-[#C8D8E8] leading-[1.15]" style={{fontFamily: 'Orbitron, sans-serif'}}>
          {article.title}
        </h1>

        {article.description && (
          <p className="text-[18px] text-[#C8D8E8]/45 leading-[1.8]" style={{fontFamily: 'Rajdhani, sans-serif'}}>
            {article.description}
          </p>
        )}

        <div className="flex flex-wrap gap-6 text-[13px] text-[#C8D8E8]/30 pt-2" style={{fontFamily: 'Share Tech Mono, monospace'}}>
          <span className="flex items-center gap-2">
            <Clock size={14} className="text-[#00C8FF]/50" />
            {readingTime} MIN
          </span>
          <span className="flex items-center gap-2">
            <User size={14} className="text-[#00C8FF]/50" />
            {article.author || 'Collectif TEI'}
          </span>
          <time dateTime={article.date} className="text-[#C8D8E8]/20">{date}</time>
        </div>
      </motion.header>

      {/* Body */}
      <div className="max-w-[1200px] mx-auto px-8 lg:px-12 flex gap-16 xl:gap-24 pt-14 pb-24">
        {/* Desktop TOC Sidebar */}
        <AnimatePresence>
          {mode === 'study' && headings.length > 0 && (
            <motion.aside
              initial={{ opacity: 0, x: -16 }}
              animate={{ opacity: 1, x: 0 }}
              exit={{ opacity: 0, x: -16 }}
              className="hidden xl:block w-72 shrink-0 sticky top-24 self-start max-h-[calc(100vh-8rem)] overflow-y-auto"
            >
              <p className="text-[10px] font-semibold uppercase tracking-[0.25em] text-[#C8D8E8]/25 mb-5 px-5" style={{fontFamily: 'Orbitron, sans-serif'}}>
                Sommaire
              </p>

              {/* Mini progress bar */}
              <div className="mx-5 mb-6 h-[2px] bg-[#0D1528] rounded-full overflow-hidden">
                <div
                  className="h-full bg-[#00C8FF]/40 rounded-full transition-all duration-300"
                  style={{ width: `${readProgress * 100}%` }}
                />
              </div>

              <nav className="space-y-1">
                {headings.map((h) => (
                  <button
                    key={h.id}
                    onClick={() => scrollToHeading(h.id)}
                    className={`w-full text-left flex items-start gap-2.5 py-2.5 px-5 rounded-r-lg transition-all duration-200 border-l-2 ${
                      h.level > 2 ? 'pl-10' : ''
                    } ${
                      activeHeading === h.id
                        ? 'border-[#00C8FF] text-[#00C8FF] bg-[#00C8FF]/5'
                        : 'border-transparent text-[#C8D8E8]/35 hover:text-[#C8D8E8]/60 hover:border-white/[0.06]'
                    }`}
                  >
                    {h.number && h.level === 2 && (
                      <span className={`text-[10px] font-bold mt-[2px] flex-shrink-0 ${
                        activeHeading === h.id ? 'text-[#00C8FF]' : 'text-[#00C8FF]/25'
                      }`} style={{fontFamily: 'Share Tech Mono, monospace'}}>
                        {h.number}
                      </span>
                    )}
                    <span className={`leading-snug ${
                      h.level > 2 ? 'text-[13px]' : 'text-[14px]'
                    } ${
                      activeHeading === h.id ? 'font-medium' : ''
                    }`} style={{fontFamily: 'Rajdhani, sans-serif'}}>
                      {h.text}
                    </span>
                  </button>
                ))}
              </nav>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Article Content */}
        <motion.article
          layout
          className={`flex-1 min-w-0 ${mode === 'lab' ? 'max-w-5xl mx-auto' : 'max-w-[720px]'}`}
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
                <div className="bg-[#0D1528] border border-[#00C8FF]/20 rounded-xl p-6 space-y-4">
                  <h3 className="font-['Orbitron',sans-serif] font-semibold text-[#00C8FF] flex items-center gap-2">
                    <ChevronRight size={16} /> Vue Lab
                  </h3>
                  <p className="text-sm text-[#C8D8E8]/40">
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
          <div className="mt-16 pt-8 border-t border-white/[0.06]">
            <div className="flex items-center justify-between">
              <Link
                href={backMap[article.category] || '/'}
                className="inline-flex items-center gap-1.5 text-sm text-[#C8D8E8]/40 hover:text-[#00C8FF] transition-colors"
              >
                <ArrowLeft size={14} />
                Retour
              </Link>
              <Link
                href="/nexus"
                className="inline-flex items-center gap-1.5 text-sm text-[#C8D8E8]/40 hover:text-[#00C8FF] transition-colors"
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
