"use client";

import { useState, useEffect, useRef, useMemo, useCallback } from "react";
import Link from "next/link";
import { editorial, PillarSlug } from "@/lib/editorial-tokens";

// ─── Types ───
interface TocItem {
  id: string;
  text: string;
  level: number;
}

interface ArticleReaderProps {
  title: string;
  subtitle?: string;
  content: string; // HTML natif depuis le JSON
  pillar: PillarSlug;
  pillarIndex?: number;
  articleType?: string;
  tags?: string[];
  citations?: number;
  charCount?: number;
  pinned?: boolean;
  prevArticle?: { slug: string; title: string } | null;
  nextArticle?: { slug: string; title: string } | null;
}

// ─── Extract TOC from HTML content ───
function extractToc(html: string): TocItem[] {
  const regex = /<h([23])\s+id="([^"]*)"[^>]*>(.*?)<\/h[23]>/gi;
  const items: TocItem[] = [];
  let match;
  while ((match = regex.exec(html)) !== null) {
    items.push({
      level: parseInt(match[1]),
      id: match[2],
      text: match[3].replace(/<[^>]*>/g, ""), // strip nested HTML
    });
  }
  return items;
}

export default function ArticleReader({
  title,
  subtitle,
  content,
  pillar,
  pillarIndex,
  articleType = "Publication",
  tags = [],
  citations = 0,
  charCount,
  pinned,
  prevArticle,
  nextArticle,
}: ArticleReaderProps) {
  const [activeTocId, setActiveTocId] = useState<string>("");
  const [drawerOpen, setDrawerOpen] = useState(false);
  const contentRef = useRef<HTMLDivElement>(null);

  const toc = useMemo(() => extractToc(content), [content]);
  const pillarColor = editorial.pillarColors[pillar] || editorial.ink;
  const pillarLabel = editorial.pillarLabels[pillar] || pillar;
  const pillarNumeral = editorial.pillarNumerals[pillar] || "—";
  const computedCharCount = charCount || content.length;
  const basePath = `/${pillar}`;

  // ─── Intersection Observer for TOC highlighting ───
  useEffect(() => {
    if (!contentRef.current || toc.length === 0) return;

    const headings = toc
      .map((item) => document.getElementById(item.id))
      .filter(Boolean) as HTMLElement[];

    if (headings.length === 0) return;

    const observer = new IntersectionObserver(
      (entries) => {
        // Find the first visible heading
        const visible = entries
          .filter((e) => e.isIntersecting)
          .sort((a, b) => a.boundingClientRect.top - b.boundingClientRect.top);

        if (visible.length > 0) {
          setActiveTocId(visible[0].target.id);
        }
      },
      {
        rootMargin: "-80px 0px -60% 0px",
        threshold: 0,
      }
    );

    headings.forEach((h) => observer.observe(h));
    return () => observer.disconnect();
  }, [toc]);

  // ─── Smooth scroll to section ───
  const scrollToSection = useCallback((id: string) => {
    const el = document.getElementById(id);
    if (el) {
      el.scrollIntoView({ behavior: "smooth", block: "start" });
      setActiveTocId(id);
      setDrawerOpen(false);
    }
  }, []);

  // ─── Lock body when drawer open ───
  useEffect(() => {
    document.body.style.overflow = drawerOpen ? "hidden" : "";
    return () => { document.body.style.overflow = ""; };
  }, [drawerOpen]);

  return (
    <article className="animate-fade-in">
      <div className="max-w-[1060px] mx-auto px-6 md:px-10">
        <div className="grid grid-cols-1 md:grid-cols-[200px_1fr] gap-8 md:gap-14">

          {/* ═══════ SIDEBAR TOC (desktop) ═══════ */}
          <aside className="hidden md:block sticky top-[88px] self-start pt-16 pb-8">
            {toc.length > 0 && (
              <>
                <span
                  className="block text-[10px] font-semibold tracking-[0.22em] uppercase mb-4"
                  style={{ fontFamily: editorial.fontLabel, color: editorial.inkGhost }}
                >
                  Sommaire
                </span>
                <nav className="space-y-0.5">
                  {toc.map((item) => (
                    <button
                      key={item.id}
                      onClick={() => scrollToSection(item.id)}
                      className="block w-full text-left transition-all duration-200"
                      style={{
                        fontFamily: editorial.fontSans,
                        fontSize: item.level === 3 ? 11.5 : 12.5,
                        fontWeight: activeTocId === item.id ? 600 : 400,
                        color: activeTocId === item.id ? editorial.ink : editorial.inkGhost,
                        padding: `8px 0 8px ${item.level === 3 ? 28 : 16}px`,
                        borderLeft: activeTocId === item.id
                          ? `2px solid ${editorial.bronze}`
                          : `1px solid ${editorial.ruleFaint}`,
                        lineHeight: 1.4,
                        background: "none",
                        border: "none",
                        borderLeftWidth: activeTocId === item.id ? 2 : 1,
                        borderLeftStyle: "solid",
                        borderLeftColor: activeTocId === item.id ? editorial.bronze : editorial.ruleFaint,
                      }}
                    >
                      {item.text}
                    </button>
                  ))}
                </nav>
              </>
            )}

            {/* Metadata panel */}
            <div
              className="mt-8 pt-5"
              style={{ borderTop: `1px solid ${editorial.ruleFaint}` }}
            >
              <span
                className="block text-[10px] font-semibold tracking-[0.15em] uppercase mb-3"
                style={{ fontFamily: editorial.fontLabel, color: editorial.inkGhost }}
              >
                Métadonnées
              </span>
              <div
                className="text-[11px] leading-[2]"
                style={{ fontFamily: editorial.fontMono, color: editorial.inkGhost }}
              >
                Pilier {pillarNumeral} · {pillarLabel}
                <br />
                Type : {articleType}
                <br />
                {citations > 0 && <>{citations} citation{citations > 1 ? "s" : ""}<br /></>}
                {new Intl.NumberFormat("fr-FR").format(computedCharCount)} caractères
              </div>
            </div>
          </aside>

          {/* ═══════ MOBILE TOC BUTTON ═══════ */}
          <button
            className="md:hidden fixed bottom-6 right-6 z-40 w-12 h-12 rounded-full flex items-center justify-center shadow-lg"
            style={{
              background: editorial.ink,
              color: editorial.bgWarm,
              border: "none",
            }}
            onClick={() => setDrawerOpen(true)}
            aria-label="Ouvrir le sommaire"
          >
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5">
              <line x1="3" y1="6" x2="21" y2="6" />
              <line x1="3" y1="12" x2="15" y2="12" />
              <line x1="3" y1="18" x2="18" y2="18" />
            </svg>
          </button>

          {/* ═══════ MOBILE DRAWER ═══════ */}
          {drawerOpen && (
            <div className="md:hidden fixed inset-0 z-50">
              <div
                className="absolute inset-0 bg-black/30"
                onClick={() => setDrawerOpen(false)}
              />
              <div
                className="absolute right-0 top-0 bottom-0 w-[280px] overflow-y-auto p-6 pt-8"
                style={{ background: editorial.bg }}
              >
                <button
                  className="mb-6 text-sm"
                  style={{
                    background: "none",
                    border: "none",
                    fontFamily: editorial.fontSans,
                    color: editorial.inkMuted,
                  }}
                  onClick={() => setDrawerOpen(false)}
                >
                  ✕ Fermer
                </button>
                <span
                  className="block text-[10px] font-semibold tracking-[0.22em] uppercase mb-3"
                  style={{ fontFamily: editorial.fontLabel, color: editorial.inkGhost }}
                >
                  Sommaire
                </span>
                {toc.map((item) => (
                  <button
                    key={item.id}
                    onClick={() => scrollToSection(item.id)}
                    className="block w-full text-left py-3 transition-colors duration-200"
                    style={{
                      background: "none",
                      border: "none",
                      fontFamily: editorial.fontSans,
                      fontSize: 14,
                      fontWeight: activeTocId === item.id ? 600 : 400,
                      color: activeTocId === item.id ? editorial.ink : editorial.inkMuted,
                      paddingLeft: item.level === 3 ? 16 : 0,
                      borderBottom: `1px solid ${editorial.ruleFaint}`,
                    }}
                  >
                    {item.text}
                  </button>
                ))}
              </div>
            </div>
          )}

          {/* ═══════ MAIN CONTENT ═══════ */}
          <main className="pt-12 md:pt-16 pb-24 md:pb-32">
            {/* Article header */}
            <header className="mb-12 md:mb-14">
              <span
                className="block text-[10px] font-semibold tracking-[0.15em] uppercase mb-3"
                style={{ fontFamily: editorial.fontLabel, color: pillarColor }}
              >
                {pillarNumeral} — {pillarIndex ? String(pillarIndex).padStart(2, "0") : ""}
                {pillarIndex ? " · " : ""}
                {articleType.toUpperCase()}
              </span>

              <h1
                className="text-3xl md:text-[46px] font-medium leading-[1.1] tracking-tight mb-4"
                style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
              >
                {title}
              </h1>

              {subtitle && (
                <p
                  className="text-base md:text-lg font-light italic leading-[1.7] max-w-[540px]"
                  style={{ fontFamily: editorial.fontBody, color: editorial.inkMuted }}
                >
                  {subtitle}
                </p>
              )}

              {/* Accent rule */}
              <div
                className="w-[60px] h-[2px] rounded-full mt-8"
                style={{ background: editorial.bronze }}
              />
            </header>

            {/* ─── Article HTML content ─── */}
            <div
              ref={contentRef}
              className="prose-tei"
              dangerouslySetInnerHTML={{ __html: content }}
            />

            {/* ─── Tags ─── */}
            {tags.length > 0 && (
              <div
                className="mt-16 pt-8 flex gap-2 flex-wrap"
                style={{ borderTop: `1px solid ${editorial.ruleFaint}` }}
              >
                {tags.map((tag) => (
                  <span
                    key={tag}
                    className="text-[10px] px-2.5 py-1"
                    style={{
                      fontFamily: editorial.fontMono,
                      color: editorial.inkGhost,
                      border: `1px solid ${editorial.ruleFaint}`,
                      borderRadius: 1,
                    }}
                  >
                    {tag}
                  </span>
                ))}
              </div>
            )}

            {/* ─── Prev / Next navigation ─── */}
            {(prevArticle || nextArticle) && (
              <nav
                className="mt-12 pt-8 grid grid-cols-2 gap-8"
                style={{ borderTop: `1px solid ${editorial.rule}` }}
              >
                {prevArticle ? (
                  <Link
                    href={`${basePath}/${prevArticle.slug}`}
                    className="no-underline group"
                  >
                    <span
                      className="block text-[10px] tracking-[0.15em] uppercase mb-2"
                      style={{ fontFamily: editorial.fontLabel, color: editorial.inkGhost }}
                    >
                      ← PRÉCÉDENT
                    </span>
                    <span
                      className="block text-base font-medium leading-snug group-hover:underline"
                      style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
                    >
                      {prevArticle.title}
                    </span>
                  </Link>
                ) : <div />}
                {nextArticle ? (
                  <Link
                    href={`${basePath}/${nextArticle.slug}`}
                    className="no-underline text-right group"
                  >
                    <span
                      className="block text-[10px] tracking-[0.15em] uppercase mb-2"
                      style={{ fontFamily: editorial.fontLabel, color: editorial.inkGhost }}
                    >
                      SUIVANT →
                    </span>
                    <span
                      className="block text-base font-medium leading-snug group-hover:underline"
                      style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
                    >
                      {nextArticle.title}
                    </span>
                  </Link>
                ) : <div />}
              </nav>
            )}
          </main>
        </div>
      </div>
    </article>
  );
}
