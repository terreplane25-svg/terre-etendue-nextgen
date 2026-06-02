"use client";

import Link from "next/link";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { dash, TAG_COLORS } from "@/lib/design-tokens";

interface ArticleEntry {
  slug: string; title: string; description: string;
  category: string; tags: string[]; pinned: boolean; readTime: number;
}

const FAMILLES = [
  { id: "fluides", label: "Fluides & matière", icon: "💧",
    tags: ["densité", "pression", "masse", "vide", "mécanique-des-fluides", "états-de-la-matière", "pression-réduite", "cloche-à-vide"] },
  { id: "optique", label: "Optique & perspective", icon: "🔭",
    tags: ["perspective", "angle-visuel", "taille-apparente", "point-de-fuite", "diffusion-rayleigh"] },
  { id: "oeil", label: "L'œil humain", icon: "👁",
    tags: ["champ-visuel", "stéréoscopie", "accommodation", "persistance-rétinienne", "cristallin", "œil-humain"] },
  { id: "forces", label: "Forces & interactions", icon: "⚡",
    tags: ["action-réaction", "magnétisme", "électromagnétisme", "charge-électrique", "électricité-statique"] },
];

function getFamille(a: ArticleEntry): string {
  for (const f of FAMILLES) { if (a.tags.some(t => f.tags.includes(t))) return f.id; }
  return "other";
}

// Cross-links: experiment → related analysis
const CROSS_LINKS: Record<string, { slug: string; label: string }> = {
  "densite-et-flottabilite": { slug: "pourquoi-les-choses-montent-et-descendent", label: "Voir l'analyse complète" },
  "la-pression-atmospherique": { slug: "pression-lumiere-halos-rayons-et-ondes", label: "Voir l'analyse complète" },
  "la-perspective-lineaire": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Voir l'analyse optique" },
  "diminution-angulaire-taille-apparente": { slug: "ce-quon-voit-quand-on-ne-devrait-plus-voir", label: "Voir les observations" },
  "la-perspective-atmospherique": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Voir l'analyse optique" },
  "magnetisme-et-electromagnetisme": { slug: "cartes-routes-boussoles-et-le-mystere-antarctique", label: "Voir l'analyse géographique" },
};

export default function ExperiencesClient({ historical, demonstrations }: { historical: ArticleEntry[]; demonstrations: ArticleEntry[] }) {
  const [tab, setTab] = useState<"all" | "demos" | "historical">("all");
  const [famille, setFamille] = useState<string | null>(null);

  const filteredDemos = famille
    ? demonstrations.filter(a => getFamille(a) === famille)
    : demonstrations;

  return (
    <div style={{ maxWidth: 1000, margin: "0 auto", padding: "32px 24px 64px" }}>

      {/* Header */}
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.rose, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, fontFamily: dash.fontMono }}>05 · Expériences</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>Laboratoire de Physique Naturelle</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>
          {demonstrations.length} démonstrations reproductibles · {historical.length} retracements historiques · 34+ protocoles
        </p>
      </motion.div>

      {/* Tabs */}
      <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: `1px solid ${dash.border}`, paddingBottom: 0 }}>
        {([
          { id: "all" as const, label: "Tout" },
          { id: "demos" as const, label: "Comprendre par l'expérience" },
          { id: "historical" as const, label: "Retracement historique" },
        ]).map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); setFamille(null); }} style={{
            padding: "8px 16px", fontSize: 13, fontWeight: 600, fontFamily: dash.fontMain,
            border: "none", background: "none", cursor: "pointer",
            color: tab === t.id ? dash.ink : dash.inkMuted,
            borderBottom: tab === t.id ? `2px solid ${dash.ink}` : "2px solid transparent",
            marginBottom: -1, transition: "all 0.2s",
          }}>{t.label}</button>
        ))}
      </div>

      {/* ═══ DEMONSTRATIONS ═══ */}
      <AnimatePresence mode="wait">
        {(tab === "all" || tab === "demos") && (
          <motion.div key="demos" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} style={{ marginBottom: 40 }}>
            {tab === "all" && <h2 style={{ fontSize: 17, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>🔬 Comprendre par l'expérience</h2>}

            {/* Famille filters */}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20 }}>
              <button onClick={() => setFamille(null)} style={{
                padding: "5px 12px", borderRadius: 8, fontSize: 12, fontWeight: 600, fontFamily: dash.fontMain,
                border: `1px solid ${!famille ? dash.ink : dash.border}`,
                background: !famille ? dash.ink : dash.card, color: !famille ? "#fff" : dash.inkMuted, cursor: "pointer",
              }}>Toutes</button>
              {FAMILLES.map(f => (
                <button key={f.id} onClick={() => setFamille(f.id === famille ? null : f.id)} style={{
                  padding: "5px 12px", borderRadius: 8, fontSize: 12, fontWeight: 600, fontFamily: dash.fontMain,
                  border: `1px solid ${famille === f.id ? dash.ink : dash.border}`,
                  background: famille === f.id ? dash.ink : dash.card, color: famille === f.id ? "#fff" : dash.inkMuted, cursor: "pointer",
                }}>{f.icon} {f.label}</button>
              ))}
            </div>

            <div style={{ display: "flex", flexDirection: "column", gap: 8 }}>
              {filteredDemos.map((a, i) => {
                const cross = CROSS_LINKS[a.slug];
                return (
                  <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                    <div className="dash-card-sm" style={{ padding: "14px 18px" }}>
                      <Link href={`/article/${a.slug}`} style={{ display: "flex", alignItems: "center", gap: 14, cursor: "pointer" }}>
                        <span className="badge" style={{ background: dash.opalSoft, color: dash.opal, minWidth: 40, textAlign: "center" }}>EXP</span>
                        <div style={{ flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 14, fontWeight: 600, color: dash.ink, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.title}</div>
                          {a.description && <div style={{ fontSize: 12, color: dash.inkGhost, marginTop: 2, overflow: "hidden", textOverflow: "ellipsis", whiteSpace: "nowrap" }}>{a.description}</div>}
                        </div>
                        <span style={{ fontSize: 12, color: dash.inkGhost, fontFamily: dash.fontMono }}>{a.readTime}m</span>
                      </Link>
                      {cross && (
                        <div style={{ marginTop: 8, paddingTop: 8, borderTop: `1px solid ${dash.borderSoft}` }}>
                          <Link href={`/article/${cross.slug}`} style={{ fontSize: 11, color: dash.lavender, fontWeight: 600 }}>
                            ↗ {cross.label}
                          </Link>
                        </div>
                      )}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      {/* ═══ HISTORICAL ═══ */}
      <AnimatePresence mode="wait">
        {(tab === "all" || tab === "historical") && (
          <motion.div key="hist" initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }}>
            {tab === "all" && <h2 style={{ fontSize: 17, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>📜 Retracement historique</h2>}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fill, minmax(300px, 1fr))", gap: 12 }}>
              {historical.map((a, i) => (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                  <Link href={`/article/${a.slug}`} className="dash-card-sm" style={{ display: "block", padding: "16px 18px", cursor: "pointer" }}>
                    <span className="badge" style={{ background: dash.lavenderSoft, color: dash.lavender, marginBottom: 8, display: "inline-block" }}>OBS</span>
                    <div style={{ fontSize: 14, fontWeight: 650, color: dash.ink, marginBottom: 4, lineHeight: 1.35 }}>{a.title}</div>
                    <div style={{ fontSize: 12, color: dash.inkGhost }}>{a.readTime} min</div>
                  </Link>
                </motion.div>
              ))}
            </div>

            {/* YouTube callout */}
            <div className="dash-card" style={{ marginTop: 24, padding: "18px 22px", display: "flex", alignItems: "center", gap: 14 }}>
              <span style={{ fontSize: 24 }}>📺</span>
              <div>
                <div style={{ fontSize: 13, fontWeight: 650, color: dash.ink }}>Chaîne recommandée</div>
                <div style={{ fontSize: 12, color: dash.inkMuted }}>Le Lab&apos;O Sciences — démonstrations en vidéo</div>
              </div>
              <a href="https://www.youtube.com/@lelabosciences2216" target="_blank" rel="noopener noreferrer"
                style={{ marginLeft: "auto", fontSize: 12, fontWeight: 600, color: dash.lavender }}>Voir →</a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
