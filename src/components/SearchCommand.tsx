'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { Search, X, Loader2, ArrowRight } from 'lucide-react';
import Link from 'next/link';

interface SearchResult {
  title: string;
  slug: string;
  category: string;
  excerpt: string;
}

export default function SearchCommand() {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const inputRef = useRef<HTMLInputElement>(null);

  // Cmd+K shortcut
  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(true);
      }
      if (e.key === 'Escape') {
        setOpen(false);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  // Focus input when opened
  useEffect(() => {
    if (open) {
      setTimeout(() => inputRef.current?.focus(), 100);
    } else {
      setQuery('');
      setResults([]);
    }
  }, [open]);

  // Search articles
  const doSearch = useCallback(async (q: string) => {
    if (q.length < 2) {
      setResults([]);
      return;
    }
    setLoading(true);
    try {
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}`);
      const data = await res.json();
      setResults(data.results || []);
    } catch {
      setResults([]);
    }
    setLoading(false);
  }, []);

  // Debounce search
  useEffect(() => {
    const timeout = setTimeout(() => doSearch(query), 250);
    return () => clearTimeout(timeout);
  }, [query, doSearch]);

  const catLabels: Record<string, string> = {
    headquarters: 'Q.G.',
    observatory: 'OBS',
    library: 'BIBLIO',
    lab: 'LAB',
  };

  return (
    <>
      {/* Trigger button */}
      <button
        onClick={() => setOpen(true)}
        className="flex items-center gap-2.5 px-4 py-2 text-[11px] text-[#C8D8E8]/30 hover:text-[#C8D8E8]/50 border border-[rgba(0,200,255,0.08)] hover:border-[rgba(0,200,255,0.2)] transition-all rounded-sm"
        style={{ fontFamily: 'Share Tech Mono, monospace' }}
      >
        <Search size={14} />
        <span className="hidden sm:inline">RECHERCHER</span>
        <kbd className="hidden sm:inline text-[9px] ml-1.5 px-1.5 py-0.5 border border-[rgba(0,200,255,0.12)] text-[#C8D8E8]/20 rounded-sm">
          ⌘K
        </kbd>
      </button>

      {/* Modal */}
      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 z-50"
              onClick={() => setOpen(false)}
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: -20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: -20 }}
              transition={{ duration: 0.2 }}
              className="fixed top-[15%] left-1/2 -translate-x-1/2 w-[90vw] max-w-[600px] z-50"
            >
              <div className="bg-[#0D1528] border border-[rgba(0,200,255,0.12)] shadow-[0_0_60px_rgba(0,200,255,0.05)] overflow-hidden">
                {/* Search input */}
                <div className="flex items-center gap-3 px-5 border-b border-[rgba(0,200,255,0.06)]">
                  <Search size={16} className="text-[#00C8FF]/40 flex-shrink-0" />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={(e) => setQuery(e.target.value)}
                    placeholder="Rechercher dans les articles..."
                    className="flex-1 bg-transparent py-4 text-[#C8D8E8] placeholder:text-[#C8D8E8]/15 text-sm focus:outline-none"
                    style={{ fontFamily: 'Rajdhani, sans-serif' }}
                  />
                  {loading && <Loader2 size={14} className="text-[#00C8FF]/40 animate-spin" />}
                  <button onClick={() => setOpen(false)} className="text-[#C8D8E8]/20 hover:text-[#C8D8E8]/40">
                    <X size={16} />
                  </button>
                </div>

                {/* Results */}
                <div className="max-h-[50vh] overflow-y-auto">
                  {query.length < 2 && (
                    <div className="p-6 text-center">
                      <p className="text-[11px] text-[#C8D8E8]/15" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
                        TAPEZ AU MOINS 2 CARACTÈRES
                      </p>
                    </div>
                  )}

                  {query.length >= 2 && !loading && results.length === 0 && (
                    <div className="p-6 text-center">
                      <p className="text-[11px] text-[#C8D8E8]/20" style={{ fontFamily: 'Share Tech Mono, monospace' }}>
                        AUCUN RÉSULTAT POUR &quot;{query}&quot;
                      </p>
                    </div>
                  )}

                  {results.map((r, i) => (
                    <Link
                      key={r.slug}
                      href={`/article/${r.slug}`}
                      onClick={() => setOpen(false)}
                      className="flex items-start gap-4 px-5 py-3.5 hover:bg-[rgba(0,200,255,0.04)] transition-colors border-b border-[rgba(0,200,255,0.03)] group"
                    >
                      <span
                        className={`text-[8px] mt-1 px-2 py-0.5 flex-shrink-0 ${
                          r.category === 'library'
                            ? 'text-[#D4A843]/50 bg-[rgba(212,168,67,0.08)]'
                            : 'text-[#00C8FF]/40 bg-[rgba(0,200,255,0.06)]'
                        }`}
                        style={{ fontFamily: 'Share Tech Mono, monospace', letterSpacing: '0.12em' }}
                      >
                        {catLabels[r.category] || 'Q.G.'}
                      </span>
                      <div className="flex-1 min-w-0">
                        <p className="text-sm text-[#C8D8E8]/60 group-hover:text-[#00C8FF] transition-colors truncate" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          {r.title}
                        </p>
                        <p className="text-[11px] text-[#C8D8E8]/15 mt-0.5 line-clamp-1" style={{ fontFamily: 'Rajdhani, sans-serif' }}>
                          {r.excerpt}
                        </p>
                      </div>
                      <ArrowRight size={12} className="text-[#C8D8E8]/10 group-hover:text-[#00C8FF]/30 mt-1.5 flex-shrink-0" />
                    </Link>
                  ))}
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
