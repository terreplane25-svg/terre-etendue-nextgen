'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { Search, X, Loader2, ArrowRight, Clock, Tag } from 'lucide-react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import { dash, PILLARS } from '@/lib/design-tokens';

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

const catMeta: Record<string, { label: string; color: string }> = {};
for (const p of PILLARS) {
  catMeta[p.id] = { label: p.name.replace(/^(Le |La |L'|Les )/, ''), color: p.color };
}
catMeta.meta = { label: 'Meta', color: dash.inkMuted };

function highlightText(text: string, query: string): React.ReactNode {
  if (!query || query.length < 2) return text;
  const escaped = query.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
  const regex = new RegExp(`(${escaped})`, 'gi');
  const parts = text.split(regex);
  return parts.map((part, i) =>
    regex.test(part)
      ? <mark key={i} style={{ background: dash.lavenderSoft, color: dash.lavender, borderRadius: 2, padding: '0 2px' }}>{part}</mark>
      : part
  );
}

export default function SearchCommand({ inline }: { inline?: boolean }) {
  const [open, setOpen] = useState(false);
  const [query, setQuery] = useState('');
  const [results, setResults] = useState<SearchResult[]>([]);
  const [loading, setLoading] = useState(false);
  const [selectedIndex, setSelectedIndex] = useState(0);
  const [activeCategory, setActiveCategory] = useState<string | null>(null);
  const [meta, setMeta] = useState({ count: 0, totalMs: 0 });
  const router = useRouter();
  const inputRef = useRef<HTMLInputElement>(null);
  const resultsRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const handler = (e: KeyboardEvent) => {
      if ((e.metaKey || e.ctrlKey) && e.key === 'k') {
        e.preventDefault();
        setOpen(prev => !prev);
      }
    };
    window.addEventListener('keydown', handler);
    return () => window.removeEventListener('keydown', handler);
  }, []);

  const closeModal = useCallback(() => {
    document.body.style.overflow = '';
    setOpen(false);
    setQuery('');
    setResults([]);
    setSelectedIndex(0);
    setActiveCategory(null);
    setMeta({ count: 0, totalMs: 0 });
  }, []);

  const navigateTo = useCallback((slug: string) => {
    document.body.style.overflow = '';
    setOpen(false);
    setTimeout(() => router.push(`/article/${slug}`), 50);
  }, [router]);

  useEffect(() => {
    if (open) {
      document.body.style.overflow = 'hidden';
      setTimeout(() => inputRef.current?.focus(), 100);
    }
    return () => { document.body.style.overflow = ''; };
  }, [open]);

  const doSearch = useCallback(async (q: string, cat: string | null) => {
    if (q.length < 2) {
      setResults([]);
      setMeta({ count: 0, totalMs: 0 });
      return;
    }
    setLoading(true);
    try {
      const catParam = cat ? `&categories=${cat}` : '';
      const res = await fetch(`/api/search?q=${encodeURIComponent(q)}${catParam}`);
      const data: SearchResponse = await res.json();
      setResults(data.results || []);
      setMeta({ count: data.count || 0, totalMs: data.totalMs || 0 });
      setSelectedIndex(0);
    } catch {
      setResults([]);
      setMeta({ count: 0, totalMs: 0 });
    }
    setLoading(false);
  }, []);

  useEffect(() => {
    const t = setTimeout(() => doSearch(query, activeCategory), 200);
    return () => clearTimeout(t);
  }, [query, activeCategory, doSearch]);

  const handleKeyDown = useCallback((e: React.KeyboardEvent) => {
    if (e.key === 'ArrowDown') {
      e.preventDefault();
      setSelectedIndex(prev => Math.min(prev + 1, results.length - 1));
    } else if (e.key === 'ArrowUp') {
      e.preventDefault();
      setSelectedIndex(prev => Math.max(prev - 1, 0));
    } else if (e.key === 'Enter' && results[selectedIndex]) {
      e.preventDefault();
      navigateTo(results[selectedIndex].slug);
    } else if (e.key === 'Escape') {
      closeModal();
    }
  }, [results, selectedIndex, navigateTo, closeModal]);

  useEffect(() => {
    if (resultsRef.current) {
      const el = resultsRef.current.querySelector(`[data-index="${selectedIndex}"]`);
      el?.scrollIntoView({ block: 'nearest', behavior: 'smooth' });
    }
  }, [selectedIndex]);

  const toggleCategory = (key: string) => {
    setActiveCategory(prev => prev === key ? null : key);
  };

  return (
    <>
      {inline ? (
        <div
          onClick={() => setOpen(true)}
          style={{
            display: 'flex', alignItems: 'center', gap: 8,
            padding: '7px 14px', borderRadius: 6,
            border: `1px solid ${dash.border}`,
            fontSize: 14, color: dash.inkGhost, cursor: 'pointer',
            transition: 'border-color 0.2s',
          }}
          onMouseOver={e => (e.currentTarget.style.borderColor = dash.lavender)}
          onMouseOut={e => (e.currentTarget.style.borderColor = dash.border)}
        >
          <Search size={15} />
          <span>Rechercher...</span>
          <kbd style={{
            marginLeft: 'auto', fontSize: 11, padding: '1px 6px',
            border: `1px solid ${dash.border}`, borderRadius: 4,
            color: dash.inkGhost, fontFamily: dash.fontMono,
          }}>
            Ctrl+K
          </kbd>
        </div>
      ) : (
        <button
          onClick={() => setOpen(true)}
          style={{
            display: 'flex', alignItems: 'center', gap: 6,
            padding: '6px 12px', border: `1px solid ${dash.border}`,
            borderRadius: 6, background: 'transparent',
            fontSize: 13, color: dash.inkMuted, cursor: 'pointer',
          }}
        >
          <Search size={16} />
        </button>
      )}

      <AnimatePresence>
        {open && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              style={{
                position: 'fixed', inset: 0, zIndex: 100,
                background: 'rgba(20, 18, 16, 0.4)',
                backdropFilter: 'blur(4px)',
              }}
              onClick={closeModal}
            />

            <motion.div
              initial={{ opacity: 0, y: -10, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.98 }}
              transition={{ duration: 0.2, ease: [0.32, 0.72, 0, 1] }}
              style={{
                position: 'fixed', top: '8%',
                left: 0, right: 0,
                margin: '0 auto',
                width: '94vw', maxWidth: 640, zIndex: 101,
              }}
              onKeyDown={handleKeyDown}
            >
              <div style={{
                background: 'var(--card)',
                border: `1px solid ${dash.border}`,
                borderRadius: 12,
                boxShadow: '0 16px 64px rgba(0,0,0,0.12), 0 4px 16px rgba(0,0,0,0.06)',
                overflow: 'hidden',
              }}>
                {/* Input */}
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 12,
                  padding: '14px 20px',
                  borderBottom: `1px solid ${dash.borderSoft}`,
                }}>
                  <Search size={18} style={{ color: dash.lavender, flexShrink: 0 }} />
                  <input
                    ref={inputRef}
                    type="text"
                    value={query}
                    onChange={e => setQuery(e.target.value)}
                    placeholder="Rechercher un article, un sujet..."
                    style={{
                      flex: 1, border: 'none', outline: 'none',
                      fontSize: 15, color: 'var(--ink)', background: 'transparent',
                      fontFamily: dash.fontMain,
                    }}
                  />
                  {loading && <Loader2 size={16} style={{ color: dash.lavender, animation: 'spin 1s linear infinite' }} />}
                  <button onClick={closeModal} style={{
                    border: 'none', background: 'none', cursor: 'pointer',
                    padding: 4, color: dash.inkGhost,
                  }}>
                    <X size={16} />
                  </button>
                </div>

                {/* Category filters */}
                <div style={{
                  display: 'flex', alignItems: 'center', gap: 6,
                  padding: '10px 20px',
                  borderBottom: `1px solid ${dash.borderSoft}`,
                  flexWrap: 'wrap',
                }}>
                  <span style={{ fontSize: 11, color: dash.inkGhost, fontWeight: 600, marginRight: 4 }}>FILTRES</span>
                  {PILLARS.map(p => {
                    const active = activeCategory === p.id;
                    return (
                      <button key={p.id} onClick={() => toggleCategory(p.id)} style={{
                        fontSize: 11, fontWeight: 600, padding: '3px 10px',
                        borderRadius: 4,
                        border: `1px solid ${active ? p.color : dash.border}`,
                        background: active ? p.colorSoft : 'transparent',
                        color: active ? p.color : dash.inkMuted,
                        cursor: 'pointer', transition: 'all 0.15s',
                      }}>
                        {p.icon} {p.name.replace(/^(Le |La |L'|Les )/, '')}
                      </button>
                    );
                  })}
                  {query.length >= 2 && !loading && (
                    <span style={{ marginLeft: 'auto', fontSize: 11, color: dash.inkGhost, fontFamily: dash.fontMono }}>
                      {meta.count} résultat{meta.count !== 1 ? 's' : ''} · {meta.totalMs}ms
                    </span>
                  )}
                </div>

                {/* Results */}
                <div ref={resultsRef} style={{ maxHeight: '50vh', overflowY: 'auto' }}>
                  {query.length < 2 && (
                    <div style={{ padding: '48px 20px', textAlign: 'center' }}>
                      <div style={{
                        width: 48, height: 48, borderRadius: '50%',
                        border: `1px solid ${dash.border}`,
                        display: 'inline-flex', alignItems: 'center', justifyContent: 'center',
                        marginBottom: 12,
                      }}>
                        <Search size={20} style={{ color: dash.inkGhost }} />
                      </div>
                      <p style={{ fontSize: 13, color: dash.inkGhost }}>Tapez au moins 2 caractères</p>
                    </div>
                  )}

                  {query.length >= 2 && !loading && results.length === 0 && (
                    <div style={{ padding: '48px 20px', textAlign: 'center' }}>
                      <p style={{ fontSize: 13, color: dash.inkMuted }}>
                        Aucun résultat pour &laquo; {query} &raquo;
                      </p>
                    </div>
                  )}

                  {results.map((r, i) => {
                    const isSelected = i === selectedIndex;
                    const cm = catMeta[r.category] || { label: 'Article', color: dash.lavender };
                    return (
                      <div
                        key={r.slug}
                        data-index={i}
                        role="button"
                        tabIndex={-1}
                        onMouseEnter={() => setSelectedIndex(i)}
                        onClick={() => navigateTo(r.slug)}
                        style={{
                          display: 'flex', alignItems: 'flex-start', gap: 14,
                          padding: '12px 20px',
                          borderBottom: `1px solid ${dash.borderSoft}`,
                          cursor: 'pointer',
                          background: isSelected ? dash.bg : 'transparent',
                          borderLeft: isSelected ? `3px solid ${cm.color}` : '3px solid transparent',
                          transition: 'background 0.1s',
                        }}
                      >
                        <span style={{
                          fontSize: 10, fontWeight: 700, padding: '2px 8px',
                          borderRadius: 4, flexShrink: 0, marginTop: 3,
                          background: cm.color + '12', color: cm.color,
                          border: `1px solid ${cm.color}25`,
                        }}>
                          {cm.label.slice(0, 12).toUpperCase()}
                        </span>

                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{
                            fontSize: 14, fontWeight: 600,
                            color: isSelected ? cm.color : dash.ink,
                            lineHeight: 1.35,
                            whiteSpace: 'nowrap', overflow: 'hidden', textOverflow: 'ellipsis',
                          }}>
                            {highlightText(r.title, query)}
                          </div>
                          {r.description && (
                            <div style={{
                              fontSize: 12, color: dash.inkMuted, marginTop: 2,
                              lineHeight: 1.4,
                              display: '-webkit-box', WebkitLineClamp: 1,
                              WebkitBoxOrient: 'vertical', overflow: 'hidden',
                            }}>
                              {highlightText(r.description.slice(0, 140), query)}
                            </div>
                          )}
                          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginTop: 4, flexWrap: 'wrap' }}>
                            {r.tags?.slice(0, 3).map(tag => (
                              <span key={tag} style={{
                                display: 'inline-flex', alignItems: 'center', gap: 3,
                                fontSize: 10, color: dash.inkGhost,
                              }}>
                                <Tag size={8} /> {tag}
                              </span>
                            ))}
                            {r.readTime && (
                              <span style={{ display: 'inline-flex', alignItems: 'center', gap: 3, fontSize: 10, color: dash.inkGhost }}>
                                <Clock size={8} /> {r.readTime} min
                              </span>
                            )}
                          </div>
                        </div>

                        <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'flex-end', gap: 4, flexShrink: 0, marginTop: 2 }}>
                          <span style={{ fontSize: 10, color: dash.inkGhost, fontFamily: dash.fontMono }}>{r.score}%</span>
                          <div style={{ width: 48, height: 3, background: dash.borderSoft, borderRadius: 2, overflow: 'hidden' }}>
                            <div style={{
                              height: '100%', borderRadius: 2,
                              width: `${r.score}%`,
                              background: cm.color,
                            }} />
                          </div>
                          <ArrowRight size={10} style={{
                            color: isSelected ? cm.color : dash.inkGhost,
                            transition: 'color 0.15s',
                          }} />
                        </div>
                      </div>
                    );
                  })}
                </div>

                {/* Footer */}
                <div style={{
                  display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                  padding: '8px 20px',
                  borderTop: `1px solid ${dash.borderSoft}`,
                  background: dash.bg,
                }}>
                  <div style={{ display: 'flex', gap: 16 }}>
                    {[
                      { keys: '↑↓', label: 'Naviguer' },
                      { keys: '⏎', label: 'Ouvrir' },
                    ].map(s => (
                      <span key={s.label} style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: dash.inkGhost }}>
                        <kbd style={{
                          padding: '1px 5px', fontSize: 10,
                          border: `1px solid ${dash.border}`, borderRadius: 3,
                          fontFamily: dash.fontMono,
                        }}>{s.keys}</kbd>
                        {s.label}
                      </span>
                    ))}
                  </div>
                  <span style={{ display: 'inline-flex', alignItems: 'center', gap: 4, fontSize: 11, color: dash.inkGhost }}>
                    <kbd style={{
                      padding: '1px 5px', fontSize: 10,
                      border: `1px solid ${dash.border}`, borderRadius: 3,
                      fontFamily: dash.fontMono,
                    }}>Esc</kbd>
                    Fermer
                  </span>
                </div>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
