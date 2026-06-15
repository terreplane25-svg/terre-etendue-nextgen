"use client";
import Link from "next/link";
import React, { useState } from "react";
import { useSearchParams } from "next/navigation";
import { AnimatePresence, motion } from "framer-motion";
import { dash } from "@/lib/design-tokens";
import SectionHeader from "@/components/SectionHeader";
import ArticleCarousel from "@/components/ArticleCarousel";

interface AE { slug: string; title: string; description: string; category: string; tags: string[]; pinned: boolean; readTime: number; }

const FAMILLES = [
  { id: "fluides", label: "Fluides & matière", icon: "💧", tags: ["densité","pression","masse","vide","mécanique-des-fluides","états-de-la-matière","pression-réduite","cloche-à-vide"] },
  { id: "optique", label: "Optique & perspective", icon: "🔭", tags: ["perspective","angle-visuel","taille-apparente","point-de-fuite","diffusion-rayleigh"] },
  { id: "oeil", label: "L'œil humain", icon: "👁", tags: ["champ-visuel","stéréoscopie","accommodation","persistance-rétinienne","cristallin","œil-humain"] },
  { id: "forces", label: "Forces & interactions", icon: "⚡", tags: ["action-réaction","magnétisme","électromagnétisme","charge-électrique","électricité-statique"] },
];
function getFam(a: AE) { for (const f of FAMILLES) { if (a.tags.some(t => f.tags.includes(t))) return f.id; } return "other"; }

const CROSS: Record<string, { slug: string; label: string }> = {
  "densite-et-flottabilite": { slug: "densite-pourquoi-les-choses-montent-et-descendent", label: "Analyse complète" },
  "la-pression-atmospherique": { slug: "pression-lumiere-halos-rayons-et-ondes", label: "Analyse complète" },
  "la-pression-atmospherique-un-ocean-d-air-invisible": { slug: "pression-lumiere-halos-rayons-et-ondes", label: "Analyse complète" },
  "la-perspective-lineaire": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Analyse optique" },
  "diminution-angulaire-taille-apparente": { slug: "la-perspective-pourquoi-les-objets-disparaissent", label: "Dossier optique complet" },
  "la-perspective-atmospherique": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Analyse optique" },
  "magnetisme-et-electromagnetisme": { slug: "cartes-routes-boussoles-et-le-mystere-antarctique", label: "Analyse géographique" },
};

export default function ExperiencesClient({ historical, demonstrations }: { historical: AE[]; demonstrations: AE[] }) {
  const searchParams = useSearchParams();
  const initialFilter = searchParams.get('filter');
  const [tab, setTab] = useState<"all"|"demos"|"hist">("all");
  const [fam, setFam] = useState<string|null>(initialFilter);
  const fd = fam ? demonstrations.filter(a => getFam(a) === fam) : demonstrations;

  const demoBadgeLabel = (a: AE) => {
    if (fam) return null;
    const famille = FAMILLES.find(f => f.id === getFam(a));
    return famille ? `${famille.icon} ${famille.label}` : null;
  };

  const demoFooter = (a: AE) => {
    const cr = CROSS[a.slug];
    if (!cr) return null;
    return (
      <Link href={`/article/${cr.slug}`} style={{ fontSize: 11, color: dash.lavender, fontWeight: 600 }}>
        ↗ {cr.label}
      </Link>
    );
  };

  return (
    <div>
      <SectionHeader pillar="EXP" pillarNum="05" subtitle="Physique naturelle" title="Laboratoire de Physique Naturelle" color={dash.rose} count={demonstrations.length + historical.length} countLabel="fiches — démonstrations et retracements historiques" />
      <div style={{ maxWidth: 960, margin: "0 auto", padding: "0 24px 64px" }}>

      <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: '1px solid var(--border)' }}>
        {([{ id: "all" as const, l: "Tout" }, { id: "demos" as const, l: "Démonstrations" }, { id: "hist" as const, l: "Historique" }]).map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); setFam(null); }} style={{
            padding: "8px 16px", fontSize: 13, fontWeight: 600, fontFamily: dash.fontMain, border: "none", background: "none", cursor: "pointer",
            color: tab === t.id ? 'var(--ink)' : 'var(--ink-muted)', borderBottom: tab === t.id ? '2px solid var(--ink)' : "2px solid transparent", marginBottom: -1,
          }}>{t.l}</button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {(tab === "all" || tab === "demos") && (
          <motion.div key="d" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ marginBottom: 40 }}>
            {tab === "all" && <h2 style={{ fontSize: 17, fontWeight: 750, color: 'var(--ink)', marginBottom: 16 }}>🔬 Démonstrations</h2>}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20 }}>
              <button onClick={() => setFam(null)} style={{ padding: "6px 14px", borderRadius: 6, fontSize: 13, fontWeight: 600, fontFamily: dash.fontMain, border: `1px solid ${!fam ? dash.rose : 'var(--border)'}`, background: !fam ? dash.rose : 'var(--card)', color: !fam ? "#fff" : 'var(--ink-muted)', cursor: "pointer" }}>Toutes</button>
              {FAMILLES.map(f => (
                <button key={f.id} onClick={() => setFam(f.id === fam ? null : f.id)} style={{ padding: "6px 14px", borderRadius: 6, fontSize: 13, fontWeight: 600, fontFamily: dash.fontMain, border: `1px solid ${fam === f.id ? dash.rose : 'var(--border)'}`, background: fam === f.id ? dash.rose : 'var(--card)', color: fam === f.id ? "#fff" : 'var(--ink-muted)', cursor: "pointer" }}>{f.icon} {f.label}</button>
              ))}
            </div>
            <ArticleCarousel
              articles={fd as any}
              color={dash.rose}
              badgeLabel={demoBadgeLabel as any}
              badgeColor={dash.rose}
              footer={demoFooter as any}
              showDate={false}
            />
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {(tab === "all" || tab === "hist") && (
          <motion.div key="h" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {tab === "all" && <h2 style={{ fontSize: 17, fontWeight: 750, color: 'var(--ink)', marginBottom: 16 }}>📜 Retracement historique</h2>}
            <ArticleCarousel
              articles={historical as any}
              color={dash.rose}
              showDate={false}
            />
            <div className="dash-card" style={{ marginTop: 24, padding: "18px 22px", display: "flex", alignItems: "center", gap: 14 }}>
              <span style={{ fontSize: 24 }}>📺</span>
              <div><div style={{ fontSize: 13, fontWeight: 650, color: 'var(--ink)' }}>Chaîne recommandée</div><div style={{ fontSize: 12, color: 'var(--ink-muted)' }}>Le Lab&apos;O Sciences</div></div>
              <a href="https://www.youtube.com/@lelabosciences2216" target="_blank" rel="noopener noreferrer" style={{ marginLeft: "auto", fontSize: 12, fontWeight: 600, color: dash.lavender }}>Voir →</a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
      </div>
    </div>
  );
}
