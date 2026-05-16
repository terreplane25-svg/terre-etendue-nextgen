"use client";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const NexusGraph = dynamic(() => import("@/components/NexusGraph"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[600px] hud-panel flex items-center justify-center">
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-[#00C8FF] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-[10px] text-[#C8D8E8]/20" style={{fontFamily:'Share Tech Mono,monospace'}}>INITIALIZING GRAPH...</p>
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
            <div className="w-8 h-[2px] bg-[#00C8FF] shadow-[0_0_8px_rgba(0,200,255,0.4)]" />
            <span className="text-[9px] tracking-[0.2em] text-[#00C8FF]/50 uppercase" style={{fontFamily:'Orbitron,sans-serif'}}>Graphe</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#C8D8E8] mb-3" style={{fontFamily:'Orbitron,sans-serif'}}>LE NEXUS</h1>
          <p className="text-sm text-[#C8D8E8]/30 max-w-xl mb-8" style={{fontFamily:'Rajdhani,sans-serif'}}>
            Chaque point est un concept. Chaque lien une connexion intellectuelle.
          </p>
        </motion.div>
        <NexusGraph />
        <div className="mt-6 flex flex-wrap gap-5">
          {[{l:"Épistémologie",c:"bg-purple-500"},{l:"Empirique",c:"bg-[#00C8FF]"},{l:"Sources sacrées",c:"bg-[#D4A843]"},{l:"Modélisation",c:"bg-emerald-500"}].map((cat) => (
            <div key={cat.l} className="flex items-center gap-2 text-[10px] text-[#C8D8E8]/20" style={{fontFamily:'Share Tech Mono,monospace'}}>
              <div className={`w-2 h-2 rounded-full ${cat.c}`} />{cat.l}
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
