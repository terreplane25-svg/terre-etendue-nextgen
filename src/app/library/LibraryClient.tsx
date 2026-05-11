"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import Link from "next/link";
import type { ArticleMeta } from "@/lib/articles";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.5 } }),
};

export default function LibraryClient({ articles }: { articles: ArticleMeta[] }) {
  const [search, setSearch] = useState("");

  const filtered = articles.filter(
    (a) =>
      a.title.toLowerCase().includes(search.toLowerCase()) ||
      a.tags.some((t) => t.toLowerCase().includes(search.toLowerCase()))
  );

  return (
    <main className="min-h-screen bg-obs-dark pt-24 pb-16">
      <div className="max-w-5xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <p className="text-obs-gold font-mono text-sm tracking-widest mb-3">PILIER 03</p>
          <h1 className="font-heading text-4xl md:text-5xl font-bold text-white mb-4">
            La Bibliothèque <span className="text-obs-gold">—</span> Sources Sacrées
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mb-8">
            Coran, hadiths, ouvrages classiques du Kalâm et références théologiques.
            Chaque source est contextualisée et reliée aux modèles du Lab.
          </p>
        </motion.div>

        <div className="mb-8">
          <input
            type="text"
            placeholder="Rechercher dans la bibliothèque..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full max-w-md px-4 py-3 rounded-lg bg-obs-surface border border-white/10 text-white placeholder:text-gray-500 focus:border-obs-gold/50 focus:outline-none focus:ring-1 focus:ring-obs-gold/30 transition-colors"
          />
        </div>

        <div className="border-t border-white/10 pt-8">
          <h2 className="text-white/60 font-mono text-xs tracking-widest mb-6">SOURCES ({filtered.length})</h2>
          {filtered.length === 0 ? (
            <p className="text-gray-500 italic">Aucune source trouvée.</p>
          ) : (
            <div className="space-y-4">
              {filtered.map((article, i) => (
                <motion.div key={article.slug} custom={i} initial="hidden" animate="visible" variants={fadeUp}>
                  <Link
                    href={`/article/${article.slug}`}
                    className="block p-6 rounded-lg bg-obs-surface border border-white/5 hover:border-obs-gold/30 transition-all duration-300 group"
                  >
                    <h3 className="text-white font-semibold text-lg group-hover:text-obs-gold transition-colors">
                      {article.title}
                    </h3>
                    <p className="text-gray-400 mt-2 text-sm">{article.description}</p>
                    <div className="flex gap-2 mt-3">
                      {article.tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-obs-gold/10 text-obs-gold">
                          {tag}
                        </span>
                      ))}
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
          )}
        </div>
      </div>
    </main>
  );
}
