"use client";

import Link from "next/link";
import { editorial, PillarSlug } from "@/lib/editorial-tokens";
import ScrollReveal from "@/components/editorial/ScrollReveal";

interface ArticleEntry {
  slug: string;
  title: string;
  description?: string;
  type?: string;
  charCount?: number;
  citations?: number;
  pinned?: boolean;
  order?: number;
}

interface EditorialArticleListProps {
  pillar: PillarSlug;
  articles: ArticleEntry[];
  title: string;
  subtitle: string;
  description: string;
}

export default function EditorialArticleList({
  pillar,
  articles,
  title,
  subtitle,
  description,
}: EditorialArticleListProps) {
  const pillarColor = editorial.pillarColors[pillar] || editorial.ink;
  const pillarNumeral = editorial.pillarNumerals[pillar] || "—";
  const basePath = `/${pillar}`;

  // Separate pinned from rest
  const pinned = articles.filter((a) => a.pinned);
  const rest = articles.filter((a) => !a.pinned);

  return (
    <div className="max-w-[860px] mx-auto px-6 md:px-10 pt-14 md:pt-[72px] pb-20 md:pb-28 animate-fade-up">
      {/* ─── Header ─── */}
      <span
        className="block text-[10px] font-semibold tracking-[0.22em] uppercase mb-3"
        style={{ fontFamily: editorial.fontLabel, color: pillarColor }}
      >
        Pilier {pillarNumeral} · {subtitle}
      </span>

      <h1
        className="text-3xl md:text-[44px] font-medium leading-[1.1] mb-2"
        style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
      >
        {title}
      </h1>

      <p
        className="text-base md:text-[17px] font-light leading-[1.7] max-w-[540px] mb-10 md:mb-12"
        style={{ fontFamily: editorial.fontBody, color: editorial.inkMuted }}
      >
        {description}
      </p>

      {/* ─── Pinned articles (essentiels) ─── */}
      {pinned.length > 0 && (
        <section className="mb-12">
          <span
            className="block text-[9px] font-semibold tracking-[0.18em] uppercase mb-4"
            style={{ fontFamily: editorial.fontLabel, color: editorial.bronze }}
          >
            ESSENTIELS
          </span>
          <div
            className="grid grid-cols-1 md:grid-cols-2 gap-px"
            style={{ background: editorial.ruleFaint }}
          >
            {pinned.map((article) => (
              <Link
                key={article.slug}
                href={`${basePath}/${article.slug}`}
                className="no-underline block group"
              >
                <div
                  className="p-6 transition-colors duration-200 group-hover:bg-black/[0.015] h-full"
                  style={{ background: editorial.card }}
                >
                  <span
                    className="block text-[9px] font-semibold tracking-[0.15em] uppercase mb-2"
                    style={{ fontFamily: editorial.fontLabel, color: pillarColor }}
                  >
                    {article.type || "Publication"}
                  </span>
                  <h3
                    className="text-lg md:text-xl font-medium leading-snug mb-2"
                    style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
                  >
                    {article.title}
                  </h3>
                  {article.description && (
                    <p
                      className="text-sm font-light leading-relaxed line-clamp-2"
                      style={{ fontFamily: editorial.fontBody, color: editorial.inkMuted }}
                    >
                      {article.description}
                    </p>
                  )}
                  <span
                    className="inline-block mt-3 text-[10px]"
                    style={{ fontFamily: editorial.fontMono, color: editorial.inkGhost }}
                  >
                    {article.charCount
                      ? new Intl.NumberFormat("fr-FR").format(article.charCount) + " car."
                      : ""}
                    {article.citations ? ` · ${article.citations} cit.` : ""}
                  </span>
                </div>
              </Link>
            ))}
          </div>
        </section>
      )}

      {/* ─── Full article list ─── */}
      <div style={{ borderTop: `2px solid ${editorial.ink}` }}>
        {(pinned.length > 0 ? rest : articles).map((article, i) => (
          <ScrollReveal key={article.slug} delay={i * 40}>
            <Link
              href={`${basePath}/${article.slug}`}
              className="no-underline block group"
            >
              <div
                className="grid grid-cols-[48px_1fr_auto] gap-5 items-start py-7 transition-all duration-300 group-hover:pl-3 group-hover:bg-black/[0.01]"
                style={{ borderBottom: `1px solid ${editorial.ruleFaint}` }}
              >
                {/* Number */}
                <span
                  className="text-xl font-light italic pt-1"
                  style={{ fontFamily: editorial.fontDisplay, color: editorial.ruleFaint }}
                >
                  {String(article.order || i + 1).padStart(2, "0")}
                </span>

                {/* Content */}
                <div>
                  <div className="flex items-center gap-3 mb-1.5">
                    <span
                      className="text-[9px] font-semibold tracking-[0.15em] uppercase"
                      style={{ fontFamily: editorial.fontLabel, color: pillarColor }}
                    >
                      {(article.type || "Publication").toUpperCase()}
                    </span>
                    {article.pinned && (
                      <span
                        className="text-[9px] px-2 py-0.5"
                        style={{
                          fontFamily: editorial.fontMono,
                          color: editorial.bronze,
                          border: `1px solid rgba(139,105,20,0.25)`,
                          borderRadius: 1,
                        }}
                      >
                        ESSENTIEL
                      </span>
                    )}
                  </div>
                  <h3
                    className="text-lg md:text-[22px] font-medium leading-snug"
                    style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
                  >
                    {article.title}
                  </h3>
                </div>

                {/* Char count */}
                <span
                  className="hidden md:block text-[10px] pt-6 whitespace-nowrap"
                  style={{ fontFamily: editorial.fontMono, color: editorial.inkGhost }}
                >
                  {article.charCount
                    ? new Intl.NumberFormat("fr-FR").format(article.charCount) + " car."
                    : ""}
                </span>
              </div>
            </Link>
          </ScrollReveal>
        ))}
      </div>

      {/* ─── Total ─── */}
      <div
        className="mt-8 text-[11px]"
        style={{ fontFamily: editorial.fontMono, color: editorial.inkGhost }}
      >
        {articles.length} publication{articles.length > 1 ? "s" : ""} dans ce pilier
      </div>
    </div>
  );
}
