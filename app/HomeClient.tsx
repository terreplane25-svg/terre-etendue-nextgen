"use client";

import Link from "next/link";
import { editorial } from "@/lib/editorial-tokens";
import ScrollReveal from "@/components/editorial/ScrollReveal";

// ─── Geometric Islamic-inspired background pattern ───
function GeometricBg() {
  return (
    <svg
      className="absolute inset-0 w-full h-full pointer-events-none"
      style={{ opacity: 0.025 }}
      viewBox="0 0 800 600"
      preserveAspectRatio="xMidYMid slice"
    >
      {[0, 1, 2, 3, 4, 5].map((i) =>
        [0, 1, 2, 3].map((j) => {
          const cx = 100 + i * 130;
          const cy = 80 + j * 150;
          return (
            <g key={`${i}-${j}`}>
              <polygon
                points={`${cx},${cy - 40} ${cx + 35},${cy - 20} ${cx + 35},${cy + 20} ${cx},${cy + 40} ${cx - 35},${cy + 20} ${cx - 35},${cy - 20}`}
                fill="none"
                stroke={editorial.ink}
                strokeWidth="0.5"
              />
              <circle cx={cx} cy={cy} r="12" fill="none" stroke={editorial.ink} strokeWidth="0.3" />
            </g>
          );
        })
      )}
    </svg>
  );
}

// ─── Pillar icon SVGs ───
const pillarIcons: Record<string, JSX.Element> = {
  headquarters: (
    <svg width="48" height="48" viewBox="0 0 48 48" className="opacity-60">
      <circle cx="24" cy="24" r="18" fill="none" stroke={editorial.ink} strokeWidth="0.8" />
      <circle cx="24" cy="24" r="10" fill="none" stroke={editorial.ink} strokeWidth="0.5" />
      <line x1="6" y1="24" x2="42" y2="24" stroke={editorial.ink} strokeWidth="0.3" />
      <line x1="24" y1="6" x2="24" y2="42" stroke={editorial.ink} strokeWidth="0.3" />
    </svg>
  ),
  observatory: (
    <svg width="48" height="48" viewBox="0 0 48 48" className="opacity-60">
      <line x1="4" y1="42" x2="44" y2="42" stroke={editorial.green} strokeWidth="0.8" />
      <line x1="4" y1="42" x2="4" y2="6" stroke={editorial.green} strokeWidth="0.8" />
      <polyline points="4,36 12,30 20,32 28,18 36,22 44,10" fill="none" stroke={editorial.green} strokeWidth="1.2" />
    </svg>
  ),
  library: (
    <svg width="48" height="48" viewBox="0 0 48 48" className="opacity-60">
      <rect x="10" y="4" width="28" height="40" rx="1" fill="none" stroke={editorial.bronze} strokeWidth="0.8" />
      <line x1="16" y1="14" x2="32" y2="14" stroke={editorial.bronze} strokeWidth="0.4" />
      <line x1="16" y1="20" x2="32" y2="20" stroke={editorial.bronze} strokeWidth="0.4" />
      <line x1="16" y1="26" x2="28" y2="26" stroke={editorial.bronze} strokeWidth="0.4" />
      <line x1="16" y1="32" x2="32" y2="32" stroke={editorial.bronze} strokeWidth="0.4" />
      <circle cx="24" cy="8" r="1.5" fill={editorial.bronze} opacity="0.4" />
    </svg>
  ),
  lab: (
    <svg width="48" height="48" viewBox="0 0 48 48" className="opacity-60">
      <ellipse cx="24" cy="30" rx="18" ry="8" fill="none" stroke={editorial.indigo} strokeWidth="0.8" />
      <ellipse cx="24" cy="24" rx="18" ry="8" fill="none" stroke={editorial.indigo} strokeWidth="0.5" />
      <ellipse cx="24" cy="18" rx="18" ry="8" fill="none" stroke={editorial.indigo} strokeWidth="0.5" />
    </svg>
  ),
};

const pillars = [
  {
    slug: "headquarters" as const,
    num: "I",
    title: "Le Quartier Général",
    sub: "Épistémologie & Méthode",
    desc: "Quinze études fondatrices — de la chronologie du modèle héliocentrique aux failles méthodologiques des preuves classiques de la rotondité. L'hypothèse nulle, le mythe d'Ératosthène, la gravité réexaminée.",
    href: "/headquarters",
  },
  {
    slug: "observatory" as const,
    num: "II",
    title: "L'Observatoire",
    sub: "Données Empiriques",
    desc: "Quatorze rapports d'observation — l'horizon et la réfraction, le Bedford Level, le pendule de Foucault, les anomalies lunaires, les distances cosmiques. Chaque fait est sourcé, chiffré, vérifié.",
    href: "/observatory",
  },
  {
    slug: "library" as const,
    num: "III",
    title: "La Bibliothèque",
    sub: "Sources Sacrées",
    desc: "Dix analyses textuelles du Coran, de la Sunna et du patrimoine savant islamique. Les versets cosmologiques, le consensus historique et les figures clés de la tradition.",
    href: "/library",
  },
  {
    slug: "lab" as const,
    num: "IV",
    title: "Le Laboratoire",
    sub: "Modélisation 3D",
    desc: "Trois simulations interactives — le modèle de la Terre Étendue, le calculateur de courbure et réfraction, et la comparaison géocentrique/héliocentrique.",
    href: "/lab",
  },
];

interface HomeClientProps {
  articleCount: number;
  pillarCounts: Record<string, number>;
}

export default function HomeClient({ articleCount, pillarCounts }: HomeClientProps) {
  return (
    <div>
      {/* ═══════ HERO ═══════ */}
      <section
        className="relative overflow-hidden px-6 md:px-12 pt-20 md:pt-28 pb-16 md:pb-20"
        style={{ background: `linear-gradient(180deg, ${editorial.bg} 0%, ${editorial.bgWarm} 100%)` }}
      >
        <GeometricBg />
        <div className="relative max-w-[800px] mx-auto text-center">
          {/* Volume label */}
          <div className="animate-fade-up">
            <span
              className="text-[10px] font-semibold tracking-[0.22em] uppercase"
              style={{ fontFamily: editorial.fontLabel, color: editorial.bronze }}
            >
              Revue de Cosmologie Indépendante · Vol. I · 2026
            </span>
          </div>

          {/* Title */}
          <div className="animate-fade-up-delay-1">
            <h1
              className="mt-5 leading-[1.08] tracking-tight"
              style={{ fontFamily: editorial.fontDisplay }}
            >
              <span className="block text-5xl md:text-7xl font-medium" style={{ color: editorial.ink }}>
                Terre Étendue
              </span>
              <span
                className="block text-5xl md:text-7xl font-light italic"
                style={{ color: editorial.ink }}
              >
                Islam
              </span>
            </h1>
          </div>

          {/* Accent rule */}
          <div className="animate-fade-up-delay-2 flex justify-center my-7">
            <div className="w-[60px] h-[2px] rounded-full" style={{ background: editorial.bronze }} />
          </div>

          {/* Subtitle */}
          <div className="animate-fade-up-delay-2">
            <p
              className="text-lg md:text-[19px] font-light leading-[1.8] max-w-[580px] mx-auto"
              style={{ fontFamily: editorial.fontBody, color: editorial.inkSoft }}
            >
              Plateforme de recherche dédiée à l'examen critique du modèle
              cosmologique standard à la lumière des données empiriques,
              de l'épistémologie et des sources sacrées de l'Islam.
            </p>
          </div>

          {/* Stats bar */}
          <div className="animate-fade-up-delay-4 flex justify-center gap-12 md:gap-14 mt-12">
            {[
              { n: String(articleCount), l: "Publications" },
              { n: "111", l: "Citations" },
              { n: "450+", l: "Sources" },
              { n: "3", l: "Modèles 3D" },
            ].map((s) => (
              <div key={s.l} className="text-center">
                <div
                  className="text-3xl md:text-4xl font-semibold"
                  style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
                >
                  {s.n}
                </div>
                <div
                  className="text-[9px] font-semibold tracking-[0.18em] mt-1 uppercase"
                  style={{ fontFamily: editorial.fontLabel, color: editorial.inkGhost }}
                >
                  {s.l}
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════ BISMILLAH DIVIDER ═══════ */}
      <div className="text-center py-10" style={{ background: editorial.bg }}>
        <span
          className="text-3xl opacity-40"
          style={{ fontFamily: editorial.fontArabic, color: editorial.bronzeL }}
        >
          ﷽
        </span>
      </div>

      {/* ═══════ PILLAR SECTIONS ═══════ */}
      <section className="max-w-[1000px] mx-auto px-6 md:px-12 pb-20">
        {pillars.map((p, i) => (
          <ScrollReveal key={p.slug} delay={i * 60}>
            <Link href={p.href} className="no-underline block group">
              <div
                className="grid grid-cols-1 md:grid-cols-[56px_1fr_80px] gap-4 md:gap-8 py-12 md:py-14 transition-colors duration-300 group-hover:bg-black/[0.015]"
                style={{
                  borderTop:
                    i === 0
                      ? `2px solid ${editorial.ink}`
                      : `1px solid ${editorial.ruleFaint}`,
                }}
              >
                {/* Numeral */}
                <div className="hidden md:block pt-1.5">
                  <span
                    className="text-3xl font-light italic"
                    style={{
                      fontFamily: editorial.fontDisplay,
                      color: editorial.ruleFaint,
                    }}
                  >
                    {p.num}
                  </span>
                </div>

                {/* Content */}
                <div>
                  <span
                    className="md:hidden text-sm font-light italic mr-3"
                    style={{ fontFamily: editorial.fontDisplay, color: editorial.ruleFaint }}
                  >
                    {p.num}
                  </span>
                  <h2
                    className="inline md:block text-2xl md:text-[32px] font-medium leading-tight mb-1"
                    style={{ fontFamily: editorial.fontDisplay, color: editorial.ink }}
                  >
                    {p.title}
                  </h2>
                  <div
                    className="text-[10px] font-semibold tracking-[0.18em] uppercase mb-4"
                    style={{
                      fontFamily: editorial.fontLabel,
                      color: editorial.pillarColors[p.slug],
                    }}
                  >
                    {p.sub}
                  </div>
                  <p
                    className="text-base font-light leading-[1.8] max-w-[540px]"
                    style={{ fontFamily: editorial.fontBody, color: editorial.inkMuted }}
                  >
                    {p.desc}
                  </p>
                  <span
                    className="inline-block mt-4 text-[11px]"
                    style={{ fontFamily: editorial.fontMono, color: editorial.inkGhost }}
                  >
                    {pillarCounts[p.slug] || "—"} publications →
                  </span>
                </div>

                {/* Icon */}
                <div className="hidden md:flex items-center justify-center">
                  {pillarIcons[p.slug]}
                </div>
              </div>
            </Link>
          </ScrollReveal>
        ))}
      </section>

      {/* ═══════ FEATURED ARTICLE (inverse) ═══════ */}
      <ScrollReveal>
        <section
          className="px-6 md:px-12 py-16 md:py-20"
          style={{ background: editorial.ink }}
        >
          <div className="max-w-[720px] mx-auto">
            <span
              className="block text-[10px] font-semibold tracking-[0.22em] uppercase mb-4"
              style={{ fontFamily: editorial.fontLabel, color: editorial.bronzeL }}
            >
              Lecture Recommandée
            </span>
            <h2
              className="text-3xl md:text-[38px] font-medium leading-[1.2] mb-5"
              style={{ fontFamily: editorial.fontDisplay, color: editorial.bgWarm }}
            >
              L'horizon, la perspective et la réfraction
            </h2>
            <p
              className="text-base md:text-[17px] font-light leading-[1.8] max-w-[560px] mb-7"
              style={{
                fontFamily: editorial.fontBody,
                color: "rgba(237,232,224,0.7)",
              }}
            >
              L'article le plus complet de l'Observatoire — dix planches d'audit
              optique, les calculs de courbure théorique confrontés aux observations
              réelles, et l'héritage oublié d'Ibn al-Haytham.
            </p>
            <Link
              href="/observatory/lhorizon-la-perspective-et-la-refraction"
              className="inline-block no-underline text-[10px] font-semibold tracking-[0.2em] px-7 py-3 transition-all duration-300 hover:bg-[#C49B30] hover:text-[#0C0A09]"
              style={{
                fontFamily: editorial.fontLabel,
                border: `1px solid ${editorial.bronzeL}`,
                color: editorial.bronzeL,
              }}
            >
              LIRE L'ARTICLE
            </Link>
          </div>
        </section>
      </ScrollReveal>
    </div>
  );
}
