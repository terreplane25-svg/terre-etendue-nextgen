'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, X, Loader2, ArrowRight, Clock, Tag, Calendar } from 'lucide-react';
import { useRouter } from 'next/navigation';

// ── Types ─────────────────────────────────────────────────────────────────

interface SearchResult {
  title: string;
  slug: string;
  category: string;
  description: string;
  tags: string[];
  date: string;
  readTime?: number;
  score: number;
}

interface SearchResponse {
  results: SearchResult[];
  totalMs: number;
  count: number;
}

// ── Constants ─────────────────────────────────────────────────────────────

const CATEGORIES = [
  { key: 'headquarters', label: 'Q.G.', color: '#0088AA' },
  { key: 'observatory', label: 'OBS', color: '#0088AA' },
  { key: 'library', label: 'BIBLIO', color: '#9A7B2F' },
  { key: 'lab', label: 'LAB', color: '#0088AA' },
] as const;

const catColorMap: Record<string, string> = {
  headquarters: '#0088AA',
  observatory: '#0088AA',
  library: '#9A7B2F',
  lab: '#0088AA',
  meta: '#888',
};

const catLabelMap: Record<string, string> = {
  headquarters: 'Q.G.',
  observatory: 'OBS',
  library: 'BIBLIO',
  lab: 'LAB',
  meta: 'META',
};

// ── Highlight helper ──────────────────────────────────────────────────────

function highlightText(text: string, query: string): React.ReactNode {
  if (!query || query.length < 2) return text;
  const regex = new RegExp(`(${query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&')})`, 'gi');
  const parts = text.split(regex);
  return parts.map((part, i) =>
    regex.test(part) ? (
      <mark key={i} className="bg-[var(--cyan)]/20 text-[var(--cyan)] rounded-sm px-0.5">{part}</mark>
    ) : (
      part
    )
  );
}

// ── Component ─────────────────────────────────────────────────────────────

export default function SearchCommand() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [activeCategories, setActiveCategories] = useState<string[]>([]);
  const [searchMeta, setSearchMeta] = useState<{ count: number; totalMs: number }>({ count: 0, totalMs: 0 });
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  // ── Keyboard shortcut: Cmd+K / Ctrl+K ─────────────────────────────────
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen((prev) => !prev);
      }
      if (e.key === 'Escape') {
        closeModal();
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // ── Focus input on open, reset on close ───────────────────────────────
  // Fonction de fermeture explicite — restaure TOUJOURS le body
  const closeModal = useCallback(() => {
    document.body.style.overflow = '';
    document.body.style.pointerEvents = '';
    setOpen(false);
    setQuery('');
    setResults([]);
    setSelectedIndex(0);
    setActiveCategories([]);
    setSearchMeta({ count: 0, totalMs: 0 });
  }, []);

  // Fonction navigation — ferme puis navigue
  const navigateTo = useCallback((slug: string) => {
    document.body.style.overflow = '';
    document.body.style.pointerEvents = '';
    setOpen(false);
    // Petit délai pour laisser React démonter le modal
    setTimeout(() => {
      router.push(`/article/${slug}`);
    }, 50);
  }, [router]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      setTimeout(() => inputRef.current?.focus(), 100);
    }
    return () => {
      document.body.style.overflow = '';
      document.body.style.pointerEvents = '';
    };
  }, [open]);

  // ── Search API call ───────────────────────────────────────────────────
  const doSearch = useCallback(async (q: string, cats: string[]) => {
    if (q.length < 2) {
      setResults([]);
      setSearchMeta({ count: 0, totalMs: 0 });
      return;
    }
    setLoading(true);
    try {
      const catParam = cats.length > 0 ? `&categories=${cats.join(',')}` : '';
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}${catParam}`);
      const data: SearchResponse = await res.json();
      setResults(data.results || []);
      setSearchMeta({ count: data.count || 0, totalMs: data.totalMs || 0 });
      setSelectedIndex(0);
    } catch {
      setResults([]);
      setSearchMeta({ count: 0, totalMs: 0 });
    }
    setLoading(false);
  }, []);

  // ── Debounced search on query or category change ──────────────────────
  useEffect(() => {
    const timeout = setTimeout(() => doSearch(query, activeCategories), 200);
    return () => clearTimeout(timeout);
  }, [query, activeCategories, doSearch]);

  // ── Keyboard navigation inside results ────────────────────────────────
  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex((prev) => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && results.length > 0) {
      e.preventDefault();
      const selected = results[selectedIndex];
      if (selected) {
        navigateTo(selected.slug);
      }
    } else if (e.key === 'Tab') {
      e.preventDefault();
      // Cycle through category filters
      const allKeys: string[] = CATEGORIES.map(c => c.key);
      if (activeCategories.length === 0) {
        setActiveCategories([allKeys[0]]);
      } else {
        const lastActive = activeCategories[activeCategories.length - 1];
        const idx = allKeys.indexOf(lastActive);
        const nextIdx = (idx + 1) % allKeys.length;
        if (nextIdx === 0) {
          setActiveCategories([]);
        } else {
          setActiveCategories([allKeys[nextIdx]]);
        }
      }
    }
  }, [results, selectedIndex, activeCategories]);

  // ── Scroll selected result into view ──────────────────────────────────
  useEffect(() => {
    if (resultsRef.current) {
      const selectedEl = resultsRef.current.querySelector(`[data-index="${selectedIndex}"]`);
      selectedEl?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [selectedIndex]);

  // ── Toggle category filter ────────────────────────────────────────────
  const toggleCategory = (key: string) => {
    setActiveCategories((prev) =>
      prev.includes(key) ? prev.filter((c) => c !== key) : [...prev, key]
    );
  };

  // ── Format date ───────────────────────────────────────────────────────
  const formatDate = (dateStr: string) => {
    if (!dateStr) return '';
    try {
      return new Date(dateStr).toLocaleDateString('fr-FR', {
        day: 'numeric',
        month: 'short',
        year: 'numeric',
      });
    } catch {
      return dateStr;
    }
  };

  return (
    <>
      {/* ── Trigger Button ──────────────────────────────────────────── */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2.5 px-4 py-2 text-[11px] text-[var(--text)]/30 hover:text-[var(--text)]/50 border border-[var(--panel-edge)] hover:border-[var(--cyan-20)] transition-all rounded-sm font-tech-mono group"
      >
        <Search size={14} className="group-hover:text-[var(--cyan)]/60 transition-colors" />
        <span className="hidden sm:inline">RECHERCHER</span>
        <kbd className="hidden sm:inline text-[9px] ml-1.5 px-1.5 py-0.5 border border-[var(--panel-edge)] text-[var(--text)]/20 rounded-sm">
          ⌘K
        </kbd>
      </button>

      {/* ── Modal ───────────────────────────────────────────────────── */}
      {open && (
          <>
            {/* Backdrop */}
            <div
              className="fixed inset-0 bg-black/70 backdrop-blur-sm z-50"
              onClick={closeModal}
            />

            {/* Modal container */}
            <div
              className="fixed top-[12%] left-1/2 -translate-x-1/2 w-[92vw] max-w-[660px] z-50"
              onKeyDown={handleKeyDown}
            >
              <div className="bg-[var(--panel)] border border-[var(--panel-edge)] shadow-lg overflow-hidden rounded-sm">

                {/* ── Scan line effect ──────────────────────────────── */}
                <div className="absolute inset-0 pointer-events-none overflow-hidden rounded-sm">
                  <div className="absolute inset-0 opacity-[0.02]"
                    style={{
                      backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 2px, var(--panel-edge) 2px, var(--panel-edge) 4px)',
                    }}
                  />
                </div>

                {/* ── Search Input ──────────────────────────────────── */}
                <div className="relative flex items-center gap-3 px-5 border-b border-[var(--panel-edge)]">
                  <Search size={18} className="text-[var(--cyan)]/50 flex-shrink-0" />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Rechercher dans les articles..."
                    className="flex-1 bg-transparent py-4 text-[var(--text)] placeholder:text-[var(--text)]/20 text-sm focus:outline-none font-rajdhani tracking-wide"
                  />
                  {loading && (
                    <Loader2 size={14} className="text-[var(--cyan)]/50 animate-spin flex-shrink-0" />
                  )}
                  <button
                    onClick={closeModal}
                    className="text-[var(--text)]/20 hover:text-[var(--text)]/50 transition-colors p-1"
                  >
                    <X size={16} />
                  </button>
                </div>

                {/* ── Category Filters ──────────────────────────────── */}
                <div className="flex items-center gap-2 px-5 py-2.5 border-b border-[var(--panel-edge)]">
                  <span className="text-[9px] text-[var(--text)]/20 tracking-[0.15em] uppercase font-tech-mono mr-1">
                    FILTRES
                  </span>
                  {CATEGORIES.map((cat) => {
                    const isActive = activeCategories.includes(cat.key);
                    return (
                      <button
                        key={cat.key}
                        onClick={() => toggleCategory(cat.key)}
                        className="relative text-[9px] tracking-[0.1em] px-2.5 py-1 transition-all font-tech-mono rounded-sm"
                        style={{
                          color: isActive ? cat.color : 'rgba(200, 216, 232, 0.25)',
                          backgroundColor: isActive ? `${cat.color}15` : 'transparent',
                          border: `1px solid ${isActive ? `${cat.color}40` : 'var(--panel-edge)'}`,
                          boxShadow: isActive ? `0 0 12px ${cat.color}10` : 'none',
                        }}
                      >
                        {cat.label}
                      </button>
                    );
                  })}

                  {/* Result count + timing */}
                  {query.length >= 2 && !loading && (
                    <span className="ml-auto text-[9px] text-[var(--text)]/15 font-tech-mono tracking-wider">
                      {searchMeta.count} résultat{searchMeta.count !== 1 ? 's' : ''} · {searchMeta.totalMs}ms
                    </span>
                  )}
                </div>

                {/* ── Results ───────────────────────────────────────── */}
                <div ref={resultsRef} className="max-h-[55vh] overflow-y-auto scrollbar-thin">
                  {/* Empty state: waiting for input */}
                  {query.length < 2 && (
                    <div className="p-10 text-center">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full border border-[var(--panel-edge)] mb-4">
                        <Search size={20} className="text-[var(--cyan)]/20" />
                      </div>
                      <p className="text-[11px] text-[var(--text)]/15 font-tech-mono tracking-[0.1em]">
                        TAPEZ AU MOINS 2 CARACTÈRES
                      </p>
                    </div>
                  )}

                  {/* No results */}
                  {query.length >= 2 && !loading && results.length === 0 && (
                    <div className="p-10 text-center">
                      <div className="inline-flex items-center justify-center w-12 h-12 rounded-full border border-[var(--panel-edge)] mb-4">
                        <X size={20} className="text-[var(--text)]/15" />
                      </div>
                      <p className="text-[11px] text-[var(--text)]/20 font-tech-mono tracking-[0.1em]">
                        AUCUN RÉSULTAT POUR &quot;{query}&quot;
                      </p>
                    </div>
                  )}

                  {/* Result items */}
                  {results.map((r, i) => {
                    const isSelected = i === selectedIndex;
                    const catColor = catColorMap[r.category] || '#0088AA';

                    return (
                      <div
                        key={r.slug}
                        role="button"
                        tabIndex={-1}
                        data-index={i}
                        onMouseEnter={() => setSelectedIndex(i)}
                        onClick={() => navigateTo(r.slug)}
                        className={`group flex items-start gap-4 px-5 py-3.5 transition-all border-b border-[var(--cyan-08)] relative cursor-pointer ${
                          isSelected
                            ? 'bg-[var(--panel-edge)]'
                            : 'hover:bg-[var(--cyan-08)]'
                        }`}
                      >
                        {/* Selected indicator */}
                        {isSelected && (
                          <div
                            className="absolute left-0 top-0 bottom-0 w-[2px]"
                            style={{ backgroundColor: catColor }}
                          />
                        )}

                        {/* Category badge */}
                        <span
                          className="text-[8px] mt-1.5 px-2 py-0.5 flex-shrink-0 tracking-[0.12em] font-tech-mono rounded-sm"
                          style={{
                            color: `${catColor}90`,
                            backgroundColor: `${catColor}10`,
                            border: `1px solid ${catColor}20`,
                          }}
                        >
                          {catLabelMap[r.category] || 'Q.G.'}
                        </span>

                        {/* Content */}
                        <div className="flex-1 min-w-0">
                          {/* Title */}
                          <p className={`text-sm font-rajdhani truncate transition-colors ${
                            isSelected ? 'text-[var(--cyan)]' : 'text-[var(--text)]/60 group-hover:text-[var(--text)]/80'
                          }`}>
                            {highlightText(r.title, query)}
                          </p>

                          {/* Description */}
                          <p className="text-[11px] text-[var(--text)]/20 mt-0.5 line-clamp-1 font-rajdhani">
                            {highlightText(r.description.substring(0, 140), query)}
                          </p>

                          {/* Tags + meta row */}
                          <div className="flex items-center gap-3 mt-1.5 flex-wrap">
                            {/* Tags */}
                            {r.tags && r.tags.slice(0, 3).map((tag) => (
                              <span
                                key={tag}
                                className="inline-flex items-center gap-1 text-[8px] text-[var(--text)]/15 font-tech-mono"
                              >
                                <Tag size={7} className="opacity-50" />
                                {tag}
                              </span>
                            ))}

                            {/* Date */}
                            {r.date && (
                              <span className="inline-flex items-center gap-1 text-[8px] text-[var(--text)]/12 font-tech-mono">
                                <Calendar size={7} className="opacity-50" />
                                {formatDate(r.date)}
                              </span>
                            )}

                            {/* Read time */}
                            {r.readTime && (
                              <span className="inline-flex items-center gap-1 text-[8px] text-[var(--text)]/12 font-tech-mono">
                                <Clock size={7} className="opacity-50" />
                                {r.readTime} min
                              </span>
                            )}
                          </div>
                        </div>

                        {/* Score bar */}
                        <div className="flex flex-col items-end gap-1 flex-shrink-0 mt-1">
                          <span className="text-[8px] text-[var(--text)]/15 font-tech-mono">
                            {r.score}%
                          </span>
                          <div className="w-14 h-[3px] bg-[var(--panel-edge)] rounded-full overflow-hidden">
                            <div
                              className="h-full rounded-full"
                              style={{
                                width: `${r.score}%`,
                                background: `linear-gradient(90deg, ${catColor}60, ${catColor})`,
                                boxShadow: `0 0 6px ${catColor}40`,
                              }}
                            />
                          </div>
                          <ArrowRight
                            size={10}
                            className={`mt-0.5 transition-all ${
                              isSelected
                                ? 'text-[var(--cyan)]/50 translate-x-0'
                                : 'text-[var(--text)]/10 -translate-x-1'
                            }`}
                          />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* ── Footer: keyboard shortcuts ───────────────────── */}
                <div className="flex items-center justify-between px-5 py-2.5 border-t border-[var(--panel-edge)] bg-[var(--void)]">
                  <div className="flex items-center gap-4">
                    <span className="inline-flex items-center gap-1.5 text-[9px] text-[var(--text)]/15 font-tech-mono">
                      <kbd className="px-1 py-0.5 border border-[var(--panel-edge)] rounded-sm text-[8px]">↑↓</kbd>
                      Naviguer
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-[9px] text-[var(--text)]/15 font-tech-mono">
                      <kbd className="px-1 py-0.5 border border-[var(--panel-edge)] rounded-sm text-[8px]">⏎</kbd>
                      Ouvrir
                    </span>
                    <span className="inline-flex items-center gap-1.5 text-[9px] text-[var(--text)]/15 font-tech-mono">
                      <kbd className="px-1 py-0.5 border border-[var(--panel-edge)] rounded-sm text-[8px]">Tab</kbd>
                      Filtres
                    </span>
                  </div>
                  <span className="inline-flex items-center gap-1.5 text-[9px] text-[var(--text)]/15 font-tech-mono">
                    <kbd className="px-1 py-0.5 border border-[var(--panel-edge)] rounded-sm text-[8px]">Esc</kbd>
                    Fermer
                  </span>
                </div>
              </div>
            </div>
          </>
        )}
    </>
  );
}
