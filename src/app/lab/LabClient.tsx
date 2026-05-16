"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const TawhidSimulation = dynamic(() => import("@/components/TawhidSimulation"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] hud-panel flex items-center justify-center">
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-[#00C8FF] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-[10px] text-[#C8D8E8]/20 font-tech-mono">LOADING 3D...</p>
      </div>
    </div>
  ),
});

const sims = [
  { id: "tawhid", title: "ORBITES DU TAWHID", desc: "Les attributs divins en orbite autour de l’Essence." },
  { id: "geodesic", title: "GEODESIQUES", desc: "Lignes geodesiques sur differentes courbures. A venir.", disabled: true },
  { id: "fractal", title: "FRACTALES", desc: "Structures auto-similaires dans les sourates. A venir.", disabled: true },
];

export default function LabClient() {
  const [active, setActive] = useState("tawhid");
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="max-w-[1200px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-[#00C8FF] shadow-[0_0_8px_rgba(0,200,255,0.4)]" />
            <span className="text-[9px] tracking-[0.2em] text-[#00C8FF]/50 uppercase font-orbitron">Pilier 04</span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#C8D8E8] mb-8 font-orbitron">LE LAB</h1>
        </motion.div>
        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {sims.map((sim) => (
            <button key={sim.id} onClick={() => !sim.disabled && setActive(sim.id)} disabled={sim.disabled}
              className={`hud-btn text-[8px] px-4 py-2 font-orbitron ${active === sim.id ? '' : sim.disabled ? 'opacity-20 cursor-not-allowed' : 'opacity-40'}`}
            >{sim.title}</button>
          ))}
        </div>
        <motion.div key={active} initial={{ opacity: 0 }} animate={{ opacity: 1 }}>
          {active === "tawhid" && <TawhidSimulation />}
          {active !== "tawhid" && <div className="w-full h-[400px] hud-panel flex items-center justify-center"><p className="text-[#C8D8E8]/15 text-sm font-tech-mono">EN DÉVELOPPEMENT</p></div>}
        </motion.div>
        <div className="mt-6 hud-panel p-5">
          <p className="hud-label text-[#C8D8E8]/25 mb-2">{sims.find(s => s.id === active)?.title}</p>
          <p className="text-sm text-[#C8D8E8]/30 font-rajdhani">{sims.find(s => s.id === active)?.desc}</p>
        </div>
      </div>
    </div>
  );
}
