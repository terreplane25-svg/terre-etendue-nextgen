"use client";

import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const NexusGraph = dynamic(() => import("@/components/NexusGraph"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] card flex items-center justify-center">
      <div className="text-center">
        <div className="w-6 h-6 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-[#E8E4DD]/25 text-sm font-mono">Initialisation du graphe...</p>
      </div>
    </div>
  ),
});

export default function NexusClient() {
  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-4 mb-4">
            <span className="font-mono text-label uppercase text-accent-cyan/50">Graphe</span>
            <div className="h-px flex-1 bg-white/[0.04]" />
          </div>
          <h1 className="font-display text-title-lg font-bold text-[#E8E4DD] mb-4">
            Le Nexus
          </h1>
          <p className="text-[#E8E4DD]/35 text-lg max-w-2xl font-body leading-relaxed mb-10">
            Chaque point est un concept ou un article. Chaque lien une connexion intellectuelle.
          </p>
        </motion.div>

        <NexusGraph />

        <div className="mt-8 flex flex-wrap gap-6">
          {[
            { label: "Épistémologie", color: "bg-purple-500" },
            { label: "Empirique", color: "bg-accent-cyan" },
            { label: "Sources sacrées", color: "bg-accent-gold" },
            { label: "Modélisation", color: "bg-accent-emerald" },
          ].map((cat) => (
            <div key={cat.label} className="flex items-center gap-2 text-xs text-[#E8E4DD]/30 font-mono">
              <div className={`w-2.5 h-2.5 rounded-full ${cat.color}`} />
              {cat.label}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
