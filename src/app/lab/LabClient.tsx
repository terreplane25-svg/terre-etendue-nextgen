"use client";
import { useState } from "react";
import { motion } from "framer-motion";
import dynamic from "next/dynamic";

const GeoHelioSim = dynamic(() => import("@/components/lab/GeoHelioSim"), {
  ssr: false,
  loading: () => <SimLoader />,
});

const CurvatureCalc = dynamic(() => import("@/components/lab/CurvatureCalc"), {
  ssr: false,
  loading: () => <SimLoader />,
});

const TriangulationSim = dynamic(() => import("@/components/lab/TriangulationSim"), {
  ssr: false,
  loading: () => <SimLoader />,
});

const ProjectionSim = dynamic(() => import("@/components/lab/ProjectionSim"), {
  ssr: false,
  loading: () => <SimLoader />,
});

function SimLoader() {
  return (
    <div className="w-full h-[500px] border border-slate-800/50 bg-[#030810] flex items-center justify-center">
      <div className="text-center">
        <div className="w-5 h-5 border-2 border-[#00C8FF] border-t-transparent rounded-full animate-spin mx-auto mb-3" />
        <p className="text-[10px] text-[#C8D8E8]/20 font-tech-mono">CHARGEMENT 3D...</p>
      </div>
    </div>
  );
}

const SIMULATIONS = [
  {
    id: "geo-helio",
    title: "GÉO. VS HÉLIO.",
    desc: "Comparaison interactive des deux modèles. Les mêmes observations, deux géométries — l'équivalence cinématique rendue visible.",
    articles: ["L'hypothèse nulle", "200 ans de résultats nuls", "Le MGPP"],
  },
  {
    id: "curvature",
    title: "COURBURE VS PLAN",
    desc: "Calculateur de visibilité : entrez une distance et une hauteur, comparez la chute de courbure théorique avec les observations documentées.",
    articles: ["L'eau ne ment pas", "Ce qu'on voit", "L'horizon"],
  },
  {
    id: "triangulation",
    title: "TRIANGULATION",
    desc: "Deux stations, deux angles, une altitude. La trigonométrie plane appliquée au Soleil — protocole du théodolite céleste.",
    articles: ["Le théodolite céleste"],
  },
  {
    id: "projections",
    title: "PROJECTIONS",
    desc: "Mercator, azimutale équidistante, équirectangulaire. Routes aériennes réelles tracées sur chaque projection.",
    articles: ["Cartes, routes, boussoles"],
  },
];

export default function LabClient() {
  const [active, setActive] = useState("geo-helio");
  const activeSim = SIMULATIONS.find((s) => s.id === active)!;

  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="max-w-[1600px] mx-auto px-4 md:px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-[#00C8FF] shadow-[0_0_8px_rgba(0,200,255,0.4)]" />
            <span className="text-[9px] tracking-[0.2em] text-[#00C8FF]/50 uppercase font-orbitron">
              Pilier 04 // Modélisation
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#C8D8E8] mb-2 font-orbitron">LE LAB</h1>
          <p className="text-sm text-[#C8D8E8]/30 font-rajdhani mb-8">
            Simulations interactives dérivées des données et analyses des articles.
          </p>
        </motion.div>

        <div className="flex gap-2 mb-6 overflow-x-auto pb-2">
          {SIMULATIONS.map((sim) => (
            <button
              key={sim.id}
              onClick={() => setActive(sim.id)}
              className={`text-[8px] px-4 py-2 font-orbitron tracking-wider border whitespace-nowrap transition-all ${
                active === sim.id
                  ? "border-[#00C8FF]/50 bg-[#00C8FF]/10 text-[#00C8FF]"
                  : "border-slate-700 text-slate-500 hover:border-slate-500 hover:text-slate-300"
              }`}
              style={{ clipPath: "polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)" }}
            >
              {sim.title}
            </button>
          ))}
        </div>

        <motion.div key={active} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ duration: 0.3 }}>
          {active === "geo-helio" && <GeoHelioSim />}
          {active === "curvature" && <CurvatureCalc />}
          {active === "triangulation" && <TriangulationSim />}
          {active === "projections" && <ProjectionSim />}
        </motion.div>

        <div className="mt-6 border border-slate-800/40 bg-[#0A1020] p-5">
          <div className="flex items-center gap-3 mb-2">
            <div className="text-[8px] font-tech-mono text-[#00C8FF]/30 tracking-widest">
              SIM_{active.toUpperCase().replace('-', '_')}
            </div>
            <div className="flex-1 h-px bg-slate-800/40" />
          </div>
          <p className="text-sm text-[#C8D8E8]/40 font-rajdhani leading-relaxed">{activeSim.desc}</p>
          <div className="flex flex-wrap gap-2 mt-3 pt-3 border-t border-slate-800/20">
            <span className="text-[8px] font-tech-mono text-slate-600">BASÉ SUR :</span>
            {activeSim.articles.map((a) => (
              <span key={a} className="text-[8px] font-tech-mono text-[#00C8FF]/40 px-2 py-0.5 border border-slate-800/30">{a}</span>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
