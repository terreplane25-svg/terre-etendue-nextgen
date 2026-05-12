"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const TawhidSimulation = dynamic(() => import("@/components/TawhidSimulation"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] rounded-xl bg-surface border border-white/[0.06] flex items-center justify-center">
      <div className="text-center">
        <div className="w-6 h-6 border-2 border-accent-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-[#E8E4DD]/25 text-sm font-mono">Chargement 3D...</p>
      </div>
    </div>
  ),
});

const sims = [
  { id: "tawhid", title: "Orbites du Tawhīd", desc: "Les attributs divins en orbite autour de l\u2019Essence." },
  { id: "geodesic", title: "Géodésiques", desc: "Lignes géodésiques sur différentes courbures. À venir.", disabled: true },
  { id: "fractal", title: "Fractales Coraniques", desc: "Structures auto-similaires dans les sourates. À venir.", disabled: true },
];

export default function LabClient() {
  const [active, setActive] = useState("tawhid");

  return (
    <div className="min-h-screen pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-4 mb-4">
            <span className="font-mono text-label uppercase text-accent-cyan/50">Pilier 04</span>
            <div className="h-px flex-1 bg-white/[0.04]" />
          </div>
          <h1 className="font-display text-title-lg font-bold text-[#E8E4DD] mb-10">
            Le Lab <span className="text-accent-cyan">&mdash;</span> <span className="text-[#E8E4DD]/50 font-heading font-normal text-2xl">Modélisation</span>
          </h1>
        </motion.div>

        <div className="flex gap-3 mb-8 overflow-x-auto pb-2">
          {sims.map((sim) => (
            <button
              key={sim.id}
              onClick={() => !sim.disabled && setActive(sim.id)}
              disabled={sim.disabled}
              className={`px-4 py-2 rounded-lg text-sm font-mono whitespace-nowrap transition-all border ${
                active === sim.id
                  ? "bg-accent-cyan/10 text-accent-cyan border-accent-cyan/20"
                  : sim.disabled
                  ? "bg-surface/50 text-[#E8E4DD]/15 cursor-not-allowed border-white/[0.03]"
                  : "bg-surface text-[#E8E4DD]/35 border-white/[0.06] hover:border-white/[0.1]"
              }`}
            >
              {sim.title}
            </button>
          ))}
        </div>

        <motion.div key={active} initial={{ opacity: 0 }} animate={{ opacity: 1 }} transition={{ duration: 0.4 }}>
          {active === "tawhid" && <TawhidSimulation />}
          {active !== "tawhid" && (
            <div className="w-full h-[400px] card flex items-center justify-center">
              <p className="text-[#E8E4DD]/20 font-mono text-sm">En cours de développement</p>
            </div>
          )}
        </motion.div>

        <div className="mt-8 card p-6">
          <h3 className="font-heading font-semibold text-[#E8E4DD]/70 mb-2">{sims.find(s => s.id === active)?.title}</h3>
          <p className="text-[#E8E4DD]/30 text-sm font-body">{sims.find(s => s.id === active)?.desc}</p>
        </div>
      </div>
    </div>
  );
}
