"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import type { ArticleMeta } from "@/lib/articles";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.06, duration: 0.5, ease: [0.16, 1, 0.3, 1] } }),
};

export default function PillarClient({ articles }: { articles: ArticleMeta[] }) {
  const [search, setSearch] = useState("");
  const filtered = search
    ? articles.filter(a => a.title.toLowerCase().includes(search.toLowerCase()) || a.tags.some(t => t.toLowerCase().includes(search.toLowerCase())))
    : articles;

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-5xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <div className="flex items-center gap-4 mb-4">
            <span className="font-mono text-label uppercase text-accent-cyan/50">Pilier 02</span>
            <div className="h-px flex-1 bg-white/[0.04]" />
          </div>
          <h1 className="font-display text-title-lg font-bold text-[#E8E4DD] mb-3">
            L\u2019Observatoire <span className="text-accent-cyan">&mdash;</span> <span className="text-[#E8E4DD]/50 font-heading font-normal text-2xl">Empirique</span>
          </h1>
          <p className="text-[#E8E4DD]/35 text-lg max-w-2xl font-body leading-relaxed mb-10">
            Donn\u00e9es brutes, observations astronomiques, mesures g\u00e9od\u00e9siques. Ce que la science peut mesurer, nous le mesurons.
          </p>
        </motion.div>

        <div className="mb-8">
          <input
            type="text"
            placeholder="Rechercher..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-sm px-4 py-2.5 rounded-lg bg-surface border border-white/[0.06] text-[#E8E4DD] placeholder:text-[#E8E4DD]/20 focus:border-accent-cyan/30 focus:outline-none focus:ring-1 focus:ring-accent-cyan/10 transition-colors font-body text-sm"
          />
        </div>

        <div className="geo-line mb-8" />

        <div className="space-y-3">
          {filtered.length === 0 ? (
            <p className="text-[#E8E4DD]/20 italic font-body">Aucun article trouv\u00e9.</p>
          ) : (
            filtered.map((article, i) => (
              <motion.div key={article.slug} custom={i} initial="hidden" animate="visible" variants={fadeUp}>
                <Link
                  href={`/article/${article.slug}`}
                  className="block group card card-hover p-5"
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="font-heading text-base font-semibold text-[#E8E4DD]/80 group-hover:text-accent-cyan transition-colors truncate">
                        {article.title}
                      </h3>
                      <p className="text-[#E8E4DD]/25 text-sm mt-1.5 font-body line-clamp-2">{article.description}</p>
                    </div>
                    <span className="font-mono text-[0.6rem] text-[#E8E4DD]/15 mt-1 flex-shrink-0">
                      {new Date(article.date).toLocaleDateString("fr-FR", { month: "short", year: "numeric" })}
                    </span>
                  </div>
                </Link>
              </motion.div>
            ))
          )}
        </div>
      </div>
    </div>
  );
}
