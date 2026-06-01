"use client";

import Link from "next/link";
import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";

interface ArticleEntry {
  slug: string;
  title: string;
  description: string;
  category: string;
  tags: string[];
  pinned: boolean;
  readTime: number;
}

interface ExperiencesClientProps {
  historical: ArticleEntry[];
  demonstrations: ArticleEntry[];
}

// ─── Famille groupings for demonstrations ───
const FAMILLES: { id: string; label: string; icon: string; tags: string[] }[] = [
  {
    id: "fluides",
    label: "Mécanique des fluides & matière",
    icon: "💧",
    tags: ["densité", "pression", "masse", "vide", "mécanique-des-fluides", "états-de-la-matière", "pression-réduite", "cloche-à-vide"],
  },
  {
    id: "optique",
    label: "Optique & perspective",
    icon: "🔭",
    tags: ["perspective", "angle-visuel", "taille-apparente", "point-de-fuite", "diffusion-rayleigh"],
  },
  {
    id: "oeil",
    label: "L'œil humain",
    icon: "👁",
    tags: ["champ-visuel", "stéréoscopie", "accommodation", "persistance-rétinienne", "cristallin", "œil-humain"],
  },
  {
    id: "forces",
    label: "Forces & interactions",
    icon: "⚡",
    tags: ["action-réaction", "magnétisme", "électromagnétisme", "charge-électrique", "électricité-statique"],
  },
];

function getFamille(article: ArticleEntry): string {
  for (const f of FAMILLES) {
    if (article.tags.some((t) => f.tags.includes(t))) return f.id;
  }
  return "other";
}

// ─── Category route mapping ───
function getCategoryRoute(category: string): string {
  const routes: Record<string, string> = {
    headquarters: "/headquarters",
    observatory: "/observatory",
    library: "/library",
    lab: "/lab",
    meta: "/about",
  };
  return routes[category] || "/observatory";
}

export default function ExperiencesClient({
  historical,
  demonstrations,
}: ExperiencesClientProps) {
  const [activeTab, setActiveTab] = useState<"all" | "historical" | "demos">("all");
  const [activeFamille, setActiveFamille] = useState<string | null>(null);

  const filteredDemos = activeFamille
    ? demonstrations.filter((a) => getFamille(a) === activeFamille)
    : demonstrations;

  return (
    <div className="min-h-screen">
      {/* ═══════ HERO ═══════ */}
      <section className="relative overflow-hidden px-6 md:px-12 pt-16 md:pt-24 pb-12 md:pb-16">
        <div className="max-w-4xl mx-auto">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6 }}
          >
            <p className="text-xs font-mono tracking-[0.2em] uppercase opacity-50 mb-4">
              Pilier V · Physique Naturelle
            </p>
            <h1 className="text-3xl md:text-5xl font-bold leading-tight mb-4">
              Laboratoire de Physique Naturelle
            </h1>
            <p className="text-lg md:text-xl opacity-70 leading-relaxed max-w-2xl mb-8">
              Comprendre les phénomènes physiques par l'expérience directe.
              Retracements historiques des grandes expériences et démonstrations
              pédagogiques reproductibles chez vous.
            </p>
          </motion.div>

          {/* Stats */}
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.6, delay: 0.2 }}
            className="flex gap-8 md:gap-12 text-sm font-mono"
          >
            <div>
              <span className="text-2xl font-bold block">{historical.length}</span>
              <span className="opacity-50 text-xs tracking-wider">RETRACEMENTS</span>
            </div>
            <div>
              <span className="text-2xl font-bold block">{demonstrations.length}</span>
              <span className="opacity-50 text-xs tracking-wider">DÉMONSTRATIONS</span>
            </div>
            <div>
              <span className="text-2xl font-bold block">34+</span>
              <span className="opacity-50 text-xs tracking-wider">PROTOCOLES</span>
            </div>
            <div>
              <span className="text-2xl font-bold block">4</span>
              <span className="opacity-50 text-xs tracking-wider">FAMILLES</span>
            </div>
          </motion.div>
        </div>
      </section>

      {/* ═══════ TABS ═══════ */}
      <section className="px-6 md:px-12 mb-8">
        <div className="max-w-4xl mx-auto">
          <div className="flex gap-2 border-b border-white/10 pb-0">
            {[
              { id: "all" as const, label: "Tout" },
              { id: "historical" as const, label: "Retracement historique" },
              { id: "demos" as const, label: "Comprendre par l'expérience" },
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => { setActiveTab(tab.id); setActiveFamille(null); }}
                className={`px-4 py-3 text-sm font-medium transition-all duration-200 border-b-2 -mb-[1px] ${
                  activeTab === tab.id
                    ? "border-current opacity-100"
                    : "border-transparent opacity-50 hover:opacity-75"
                }`}
              >
                {tab.label}
              </button>
            ))}
          </div>
        </div>
      </section>

      {/* ═══════ SECTION 1: RETRACEMENT HISTORIQUE ═══════ */}
      <AnimatePresence mode="wait">
        {(activeTab === "all" || activeTab === "historical") && (
          <motion.section
            key="historical"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3 }}
            className="px-6 md:px-12 mb-16"
          >
            <div className="max-w-4xl mx-auto">
              {activeTab === "all" && (
                <div className="mb-8">
                  <h2 className="text-xl md:text-2xl font-bold mb-2">
                    📜 Retracement historique
                  </h2>
                  <p className="opacity-60 text-sm max-w-xl">
                    Les grandes expériences qui ont jalonné le débat cosmologique :
                    de Rowbotham (1838) à Michelson-Morley (1887), en passant par
                    Foucault (1851) et Airy (1871).
                  </p>
                </div>
              )}

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                {historical.map((article, i) => (
                  <motion.div
                    key={article.slug}
                    initial={{ opacity: 0, y: 16 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ duration: 0.4, delay: i * 0.05 }}
                  >
                    <Link
                      href={`${getCategoryRoute(article.category)}/${article.slug}`}
                      className="block p-5 rounded-lg border border-white/10 hover:border-white/20 transition-all duration-200 hover:bg-white/[0.03] group no-underline"
                    >
                      <div className="flex items-start justify-between gap-3 mb-2">
                        <span className="text-xs font-mono opacity-40 tracking-wider uppercase">
                          {article.category === "headquarters" ? "QG" : "OBS"}
                        </span>
                        <span className="text-xs font-mono opacity-30">
                          {article.readTime} min
                        </span>
                      </div>
                      <h3 className="text-base font-semibold leading-snug mb-2 group-hover:opacity-100 opacity-90 transition-opacity">
                        {article.title}
                      </h3>
                      {article.description && (
                        <p className="text-sm opacity-50 line-clamp-2 leading-relaxed">
                          {article.description}
                        </p>
                      )}
                    </Link>
                  </motion.div>
                ))}
              </div>
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* ═══════ SECTION 2: DÉMONSTRATIONS ═══════ */}
      <AnimatePresence mode="wait">
        {(activeTab === "all" || activeTab === "demos") && (
          <motion.section
            key="demos"
            initial={{ opacity: 0, y: 12 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -12 }}
            transition={{ duration: 0.3 }}
            className="px-6 md:px-12 mb-16"
          >
            <div className="max-w-4xl mx-auto">
              {activeTab === "all" && (
                <div className="mb-8 pt-8 border-t border-white/10">
                  <h2 className="text-xl md:text-2xl font-bold mb-2">
                    🔬 Comprendre par l'expérience
                  </h2>
                  <p className="opacity-60 text-sm max-w-xl">
                    Fiches pédagogiques avec protocoles reproductibles chez vous.
                    Chaque expérience démontre un phénomène physique fondamental et
                    le relie aux analyses du site.
                  </p>
                </div>
              )}

              {/* Famille filters */}
              <div className="flex flex-wrap gap-2 mb-8">
                <button
                  onClick={() => setActiveFamille(null)}
                  className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 border ${
                    activeFamille === null
                      ? "border-white/40 opacity-100"
                      : "border-white/10 opacity-50 hover:opacity-75"
                  }`}
                >
                  Toutes les familles
                </button>
                {FAMILLES.map((f) => (
                  <button
                    key={f.id}
                    onClick={() => setActiveFamille(f.id === activeFamille ? null : f.id)}
                    className={`px-3 py-1.5 rounded-full text-xs font-medium transition-all duration-200 border ${
                      activeFamille === f.id
                        ? "border-white/40 opacity-100"
                        : "border-white/10 opacity-50 hover:opacity-75"
                    }`}
                  >
                    {f.icon} {f.label}
                  </button>
                ))}
              </div>

              {/* Grouped by famille */}
              {activeFamille === null ? (
                // Show all, grouped
                FAMILLES.map((famille) => {
                  const familleArticles = demonstrations.filter(
                    (a) => getFamille(a) === famille.id
                  );
                  if (familleArticles.length === 0) return null;
                  return (
                    <div key={famille.id} className="mb-12">
                      <h3 className="text-lg font-semibold mb-4 flex items-center gap-2">
                        <span>{famille.icon}</span>
                        <span>{famille.label}</span>
                        <span className="text-xs font-mono opacity-30 ml-2">
                          {familleArticles.length} fiches
                        </span>
                      </h3>
                      <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                        {familleArticles.map((article, i) => (
                          <motion.div
                            key={article.slug}
                            initial={{ opacity: 0, y: 16 }}
                            animate={{ opacity: 1, y: 0 }}
                            transition={{ duration: 0.4, delay: i * 0.05 }}
                          >
                            <Link
                              href={`/observatory/${article.slug}`}
                              className="block p-5 rounded-lg border border-white/10 hover:border-white/20 transition-all duration-200 hover:bg-white/[0.03] group no-underline"
                            >
                              <div className="flex items-start justify-between gap-3 mb-2">
                                <div className="flex gap-2 flex-wrap">
                                  {article.tags
                                    .filter((t) => t !== "expériences" && t !== "physique-naturelle")
                                    .slice(0, 3)
                                    .map((tag) => (
                                      <span
                                        key={tag}
                                        className="text-[10px] font-mono opacity-30 px-1.5 py-0.5 rounded border border-white/10"
                                      >
                                        {tag}
                                      </span>
                                    ))}
                                </div>
                                <span className="text-xs font-mono opacity-30 whitespace-nowrap">
                                  {article.readTime} min
                                </span>
                              </div>
                              <h4 className="text-base font-semibold leading-snug mb-2 group-hover:opacity-100 opacity-90 transition-opacity">
                                {article.title}
                              </h4>
                              {article.description && (
                                <p className="text-sm opacity-50 line-clamp-2 leading-relaxed">
                                  {article.description}
                                </p>
                              )}
                            </Link>
                          </motion.div>
                        ))}
                      </div>
                    </div>
                  );
                })
              ) : (
                // Show filtered famille
                <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                  {filteredDemos.map((article, i) => (
                    <motion.div
                      key={article.slug}
                      initial={{ opacity: 0, y: 16 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ duration: 0.4, delay: i * 0.05 }}
                    >
                      <Link
                        href={`/observatory/${article.slug}`}
                        className="block p-5 rounded-lg border border-white/10 hover:border-white/20 transition-all duration-200 hover:bg-white/[0.03] group no-underline"
                      >
                        <div className="flex items-start justify-between gap-3 mb-2">
                          <div className="flex gap-2 flex-wrap">
                            {article.tags
                              .filter((t) => t !== "expériences" && t !== "physique-naturelle")
                              .slice(0, 3)
                              .map((tag) => (
                                <span
                                  key={tag}
                                  className="text-[10px] font-mono opacity-30 px-1.5 py-0.5 rounded border border-white/10"
                                >
                                  {tag}
                                </span>
                              ))}
                          </div>
                          <span className="text-xs font-mono opacity-30 whitespace-nowrap">
                            {article.readTime} min
                          </span>
                        </div>
                        <h4 className="text-base font-semibold leading-snug mb-2 group-hover:opacity-100 opacity-90 transition-opacity">
                          {article.title}
                        </h4>
                        {article.description && (
                          <p className="text-sm opacity-50 line-clamp-2 leading-relaxed">
                            {article.description}
                          </p>
                        )}
                      </Link>
                    </motion.div>
                  ))}
                </div>
              )}
            </div>
          </motion.section>
        )}
      </AnimatePresence>

      {/* ═══════ YOUTUBE CHANNEL CALLOUT ═══════ */}
      <section className="px-6 md:px-12 mb-16">
        <div className="max-w-4xl mx-auto">
          <div className="p-6 rounded-lg border border-white/10 bg-white/[0.02]">
            <p className="text-sm font-medium mb-2">📺 Chaîne recommandée</p>
            <p className="text-sm opacity-60 mb-3">
              Le Lab&apos;O Sciences propose de nombreuses démonstrations
              en vidéo couvrant la plupart des phénomènes abordés ici.
            </p>
            <a
              href="https://www.youtube.com/@lelabosciences2216"
              target="_blank"
              rel="noopener noreferrer"
              className="inline-block text-sm font-mono opacity-70 hover:opacity-100 transition-opacity"
            >
              youtube.com/@lelabosciences2216 →
            </a>
          </div>
        </div>
      </section>
    </div>
  );
}
