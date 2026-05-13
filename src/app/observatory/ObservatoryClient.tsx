"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import type { ArticleMeta } from "@/lib/articles";

export default function PillarClient({ articles }: { articles: ArticleMeta[] }) {
  const [search, setSearch] = useState("");
  const filtered = search
    ? articles.filter(a => a.title.toLowerCase().includes(search.toLowerCase()) || a.tags.some(t => t.toLowerCase().includes(search.toLowerCase())))
    : articles;

  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="max-w-[960px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-[#00C8FF] shadow-[0_0_8px_rgba(0,200,255,0.4)]" />
            <span className="text-[9px] tracking-[0.2em] text-[#00C8FF]/50 uppercase" style={{fontFamily: "Orbitron, sans-serif"}}>Pilier 02</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#C8D8E8] mb-2" style={{fontFamily: "Orbitron, sans-serif"}}>
            L’OBSERVATOIRE
          </h1>
          <p className="text-sm text-[#C8D8E8]/30 max-w-xl leading-relaxed mb-8" style={{fontFamily: "Rajdhani, sans-serif"}}>
            Données brutes, observations astronomiques, mesures géodésiques.
          </p>
        </motion.div>

        <div className="mb-6">
          <input
            type="text"
            placeholder="Rechercher..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-sm px-4 py-2 bg-[#0D1528] border border-[rgba(0,200,255,0.08)] text-[#C8D8E8] placeholder:text-[#C8D8E8]/15 focus:border-[rgba(0,200,255,0.2)] focus:outline-none transition-colors text-sm"
            style={{fontFamily: "Share Tech Mono, monospace", fontSize: "12px"}}
          />
        </div>

        <div className="hud-divider mb-6" />

        <div className="space-y-2">
          {filtered.length === 0 ? (
            <p className="text-[#C8D8E8]/15 italic text-sm">Aucun article trouvé.</p>
          ) : (
            filtered.map((article, i) => (
              <motion.div
                key={article.slug}
                initial={{ opacity: 0, y: 12 }}
                animate={{ opacity: 1, y: 0 }}
                transition={{ delay: i * 0.04 }}
              >
                <Link href={`/article/${article.slug}`} className="block hud-card p-5 group">
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 min-w-0">
                      <h3 className="text-sm font-semibold text-[#C8D8E8]/70 group-hover:text-[#00C8FF] transition-colors truncate" style={{fontFamily: "Rajdhani, sans-serif"}}>
                        {article.title}
                      </h3>
                      <p className="text-[12px] text-[#C8D8E8]/20 mt-1 line-clamp-2" style={{fontFamily: "Rajdhani, sans-serif"}}>{article.description}</p>
                    </div>
                    <span className="text-[10px] text-[#C8D8E8]/10 mt-0.5 flex-shrink-0" style={{fontFamily: "Share Tech Mono, monospace"}}>
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
