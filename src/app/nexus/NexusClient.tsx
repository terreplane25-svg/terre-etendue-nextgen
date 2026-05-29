"use client";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const NexusGraph = dynamic(() => import("@/components/NexusGraph"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] hud-panel flex items-center justify-center">
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-[var(--cyan)] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-[10px] text-[var(--text)]/20 font-tech-mono">INITIALIZING GRAPH...</p>
      </div>
    </div>
  ),
});

export default function NexusClient() {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="max-w-[1200px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-[var(--cyan)] shadow-[0_0_8px_var(--cyan-20)]" />
            <span className="text-[9px] tracking-[0.2em] text-[var(--cyan)]/50 uppercase font-orbitron">Graphe</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[var(--text)] mb-3 font-orbitron">LE NEXUS</h1>
          <p className="text-sm text-[var(--text)]/30 max-w-xl mb-8 font-rajdhani">
            Chaque point est un concept. Chaque lien une connexion intellectuelle.
          </p>
        </motion.div>
        <NexusGraph />
        <div className="mt-6 flex flex-wrap gap-5">
          {[{l:"Épistémologie",c:"bg-purple-500"},{l:"Empirique",c:"bg-[var(--cyan)]"},{l:"Sources sacrées",c:"bg-[var(--gold)]"},{l:"Modélisation",c:"bg-emerald-500"}].map((cat) => (
            <div key={cat.l} className="flex items-center gap-2 text-[10px] text-[var(--text)]/20 font-tech-mono">
              <div className={`w-2 h-2 rounded-full ${cat.c}`} />{cat.l}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
