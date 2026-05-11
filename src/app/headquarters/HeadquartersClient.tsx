"use client";

import { motion } from "framer-motion";
import Link from "next/link";
import type { ArticleMeta } from "@/lib/articles";

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.1, duration: 0.5 } }),
};

export default function HeadquartersClient({ articles }: { articles: ArticleMeta[] }) {
  return (
    <main className="min-h-screen bg-obs-dark pt-24 pb-16">
      <div className="max-w-5xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <p className="text-obs-cyan font-mono text-sm tracking-widest mb-3">PILIER 01</p>
          <h1 className="font-heading text-4xl md:text-5xl font-bold text-white mb-4">
            Le Q.G. <span className="text-obs-cyan">—</span> Épistémologie
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mb-12">
            Fondements méthodologiques de la recherche. Ici, on définit les règles du jeu :
            comment articuler science empirique et sources sacrées sans confondre les registres.
          </p>
        </motion.div>

        <div className="border-t border-white/10 pt-8">
          <h2 className="text-white/60 font-mono text-xs tracking-widest mb-6">ARTICLES ({articles.length})</h2>
          {articles.length === 0 ? (
            <p className="text-gray-500 italic">Aucun article dans ce pilier pour le moment.</p>
          ) : (
            <div className="space-y-4">
              {articles.map((article, i) => (
                <motion.div key={article.slug} custom={i} initial="hidden" animate="visible" variants={fadeUp}>
                  <Link
                    href={`/article/${article.slug}`}
                    className="block p-6 rounded-lg bg-obs-surface border border-white/5 hover:border-obs-cyan/30 transition-all duration-300 group"
                  >
                    <h3 className="text-white font-semibold text-lg group-hover:text-obs-cyan transition-colors">
                      {article.title}
                    </h3>
                    <p className="text-gray-400 mt-2 text-sm">{article.description}</p>
                    <div className="flex gap-2 mt-3">
                      {article.tags.slice(0, 3).map((tag) => (
                        <span key={tag} className="text-xs px-2 py-0.5 rounded-full bg-obs-cyan/10 text-obs-cyan">
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
