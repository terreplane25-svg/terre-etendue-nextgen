"use client";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const NexusGraph = dynamic(() => import("@/components/NexusGraph"), {
  ssr: false,
  loading: () => (
    <div
      className="w-full h-[600px] rounded-lg border flex items-center justify-center"
      style={{ background: '#FFFFFF', borderColor: 'rgba(20,18,16,0.06)' }}
    >
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-t-transparent rounded-full animate-spin mx-auto mb-3" style={{ borderColor: '#3580C0', borderTopColor: 'transparent' }} />
        <p className="text-[10px]" style={{ color: '#BAB5AC', fontFamily: "'Plus Jakarta Sans', sans-serif", letterSpacing: '0.05em' }}>INITIALIZING GRAPH...</p>
      </div>
    </div>
  ),
});

export default function NexusClient() {
  return (
    <div className="min-h-screen pt-20 pb-16" style={{ background: '#FAFAF6', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <div className="max-w-[1200px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px]" style={{ background: '#3580C0' }} />
            <span className="text-[9px] tracking-[0.2em] uppercase" style={{ color: 'rgba(53,128,192,0.5)', fontWeight: 600 }}>Graphe</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold mb-3" style={{ color: '#141210' }}>LE NEXUS</h1>
          <p className="text-sm max-w-xl mb-8" style={{ color: '#8A857D' }}>
            Chaque point est un concept. Chaque lien une connexion intellectuelle.
          </p>
        </motion.div>
        <NexusGraph />
        <div className="mt-6 flex flex-wrap gap-5">
          {[
            { l: "Épistémologie", c: "#7C6FC4" },
            { l: "Empirique", c: "#3580C0" },
            { l: "Sources sacrées", c: "#C48A2E" },
            { l: "Modélisation", c: "#3A8F6E" },
          ].map((cat) => (
            <div key={cat.l} className="flex items-center gap-2 text-[10px]" style={{ color: '#BAB5AC', letterSpacing: '0.05em' }}>
              <div className="w-2 h-2 rounded-full" style={{ background: cat.c }} />{cat.l}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
