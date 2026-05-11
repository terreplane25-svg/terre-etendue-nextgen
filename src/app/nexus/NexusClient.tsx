"use client";

import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const NexusGraph = dynamic(() => import("@/components/NexusGraph"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] rounded-xl bg-obs-surface border border-white/10 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-obs-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-gray-400 text-sm">Initialisation du graphe...</p>
      </div>
    </div>
  ),
});

export default function NexusClient() {
  return (
    <main className="min-h-screen bg-obs-dark pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <p className="text-obs-cyan font-mono text-sm tracking-widest mb-3">NEXUS</p>
          <h1 className="font-heading text-4xl md:text-5xl font-bold text-white mb-4">
            Le Nexus <span className="text-obs-cyan">\u2014</span> Graphe de Connaissances
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mb-10">
            Chaque point est un concept ou un article. Chaque lien une connexion intellectuelle.
            Explorez visuellement comment la science rejoint les sources sacr\u00e9es.
          </p>
        </motion.div>

        <NexusGraph />

        <div className="mt-8 grid grid-cols-2 md:grid-cols-4 gap-4">
          {[
            { label: "\u00c9pist\u00e9mologie", color: "bg-purple-500" },
            { label: "Empirique", color: "bg-obs-cyan" },
            { label: "Sources sacr\u00e9es", color: "bg-obs-gold" },
            { label: "Mod\u00e9lisation", color: "bg-emerald-500" },
          ].map((cat) => (
            <div key={cat.label} className="flex items-center gap-2 text-sm text-gray-400">
              <div className={`w-3 h-3 rounded-full ${cat.color}`} />
              {cat.label}
            </div>
          ))}
        </div>
      </div>
    </main>
  );
}
