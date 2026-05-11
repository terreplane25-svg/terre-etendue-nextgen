"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const TawhidSimulation = dynamic(() => import("@/components/TawhidSimulation"), {
  ssr: false,
  loading: () => (
    <div className="w-full h-[500px] rounded-xl bg-obs-surface border border-white/10 flex items-center justify-center">
      <div className="text-center">
        <div className="w-8 h-8 border-2 border-obs-cyan border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-gray-400 text-sm">Chargement de la simulation 3D...</p>
      </div>
    </div>
  ),
});

const simulations = [
  {
    id: "tawhid",
    title: "Orbites du Tawh\u00eed",
    description: "Les attributs divins en orbite autour de l\u2019Essence (Dh\u00e2t) : une mod\u00e9lisation g\u00e9om\u00e9trique du concept d\u2019Unicit\u00e9.",
  },
  {
    id: "geodesic",
    title: "G\u00e9od\u00e9siques de la Terre \u00c9tendue",
    description: "Visualisation des lignes g\u00e9od\u00e9siques sur diff\u00e9rentes courbures de surface. \u00c0 venir.",
    disabled: true,
  },
  {
    id: "fractal",
    title: "Fractales Coraniques",
    description: "Structures auto-similaires dans l\u2019organisation des sourates. \u00c0 venir.",
    disabled: true,
  },
];

export default function LabClient() {
  const [activeSim, setActiveSim] = useState("tawhid");

  return (
    <main className="min-h-screen bg-obs-dark pt-24 pb-16">
      <div className="max-w-6xl mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -20 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.6 }}>
          <p className="text-obs-cyan font-mono text-sm tracking-widest mb-3">PILIER 04</p>
          <h1 className="font-heading text-4xl md:text-5xl font-bold text-white mb-4">
            Le Lab <span className="text-obs-cyan">\u2014</span> Mod\u00e9lisation
          </h1>
          <p className="text-gray-400 text-lg max-w-2xl mb-10">
            Simulations interactives et mod\u00e8les 3D. Ici, les concepts deviennent tangibles.
          </p>
        </motion.div>

        <div className="flex gap-3 mb-8 overflow-x-auto pb-2">
          {simulations.map((sim) => (
            <button
              key={sim.id}
              onClick={() => !sim.disabled && setActiveSim(sim.id)}
              disabled={sim.disabled}
              className={`px-4 py-2 rounded-lg text-sm font-medium whitespace-nowrap transition-all ${
                activeSim === sim.id
                  ? "bg-obs-cyan/20 text-obs-cyan border border-obs-cyan/30"
                  : sim.disabled
                  ? "bg-obs-surface/50 text-gray-600 cursor-not-allowed border border-white/5"
                  : "bg-obs-surface text-gray-400 border border-white/5 hover:border-white/20"
              }`}
            >
              {sim.title}
              {sim.disabled && " \ud83d\udd12"}
            </button>
          ))}
        </div>

        <motion.div
          key={activeSim}
          initial={{ opacity: 0, scale: 0.98 }}
          animate={{ opacity: 1, scale: 1 }}
          transition={{ duration: 0.4 }}
        >
          {activeSim === "tawhid" && <TawhidSimulation />}
          {activeSim === "geodesic" && (
            <div className="w-full h-[400px] rounded-xl bg-obs-surface border border-white/10 flex items-center justify-center">
              <p className="text-gray-500">Simulation en cours de d\u00e9veloppement</p>
            </div>
          )}
          {activeSim === "fractal" && (
            <div className="w-full h-[400px] rounded-xl bg-obs-surface border border-white/10 flex items-center justify-center">
              <p className="text-gray-500">Simulation en cours de d\u00e9veloppement</p>
            </div>
          )}
        </motion.div>

        <div className="mt-8 p-6 rounded-xl bg-obs-surface border border-white/10">
          <h3 className="text-white font-semibold mb-2">\u00c0 propos de cette simulation</h3>
          <p className="text-gray-400 text-sm leading-relaxed">
            {simulations.find((s) => s.id === activeSim)?.description}
          </p>
        </div>
      </div>
    </main>
  );
}
