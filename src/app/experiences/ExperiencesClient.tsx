"use client";
import Link from "next/link";
import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { dash } from "@/lib/design-tokens";
import { getArticleImage } from "@/lib/article-images";

interface AE { slug: string; title: string; description: string; category: string; tags: string[]; pinned: boolean; readTime: number; }

const FAMILLES = [
  { id: "fluides", label: "Fluides & matière", icon: "💧", tags: ["densité","pression","masse","vide","mécanique-des-fluides","états-de-la-matière","pression-réduite","cloche-à-vide"] },
  { id: "optique", label: "Optique & perspective", icon: "🔭", tags: ["perspective","angle-visuel","taille-apparente","point-de-fuite","diffusion-rayleigh"] },
  { id: "oeil", label: "L'œil humain", icon: "👁", tags: ["champ-visuel","stéréoscopie","accommodation","persistance-rétinienne","cristallin","œil-humain"] },
  { id: "forces", label: "Forces & interactions", icon: "⚡", tags: ["action-réaction","magnétisme","électromagnétisme","charge-électrique","électricité-statique"] },
];
function getFam(a: AE) { for (const f of FAMILLES) { if (a.tags.some(t => f.tags.includes(t))) return f.id; } return "other"; }

const CROSS: Record<string, { slug: string; label: string }> = {
  "densite-et-flottabilite": { slug: "pourquoi-les-choses-montent-et-descendent", label: "Analyse complète" },
  "la-pression-atmospherique": { slug: "pression-lumiere-halos-rayons-et-ondes", label: "Analyse complète" },
  "la-perspective-lineaire": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Analyse optique" },
  "diminution-angulaire-taille-apparente": { slug: "ce-quon-voit-quand-on-ne-devrait-plus-voir", label: "Observations" },
  "la-perspective-atmospherique": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Analyse optique" },
  "magnetisme-et-electromagnetisme": { slug: "cartes-routes-boussoles-et-le-mystere-antarctique", label: "Analyse géographique" },
};

export default function ExperiencesClient({ historical, demonstrations }: { historical: AE[]; demonstrations: AE[] }) {
  const [tab, setTab] = useState<"all"|"demos"|"hist">("all");
  const [fam, setFam] = useState<string|null>(null);
  const fd = fam ? demonstrations.filter(a => getFam(a) === fam) : demonstrations;

  return (
    <div style={{ maxWidth: 960, margin: "0 auto", padding: "32px 24px 64px" }}>
      <motion.div initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} style={{ marginBottom: 28 }}>
        <div style={{ fontSize: 11, fontWeight: 700, color: dash.rose, letterSpacing: "0.1em", textTransform: "uppercase", marginBottom: 6, fontFamily: dash.fontMono }}>05 · Expériences</div>
        <h1 style={{ fontSize: 28, fontWeight: 800, color: dash.ink, marginBottom: 4 }}>Laboratoire de Physique Naturelle</h1>
        <p style={{ fontSize: 14, color: dash.inkMuted }}>{demonstrations.length} démonstrations · {historical.length} retracements historiques</p>
      </motion.div>

      <div style={{ display: "flex", gap: 4, marginBottom: 24, borderBottom: `1px solid ${dash.border}` }}>
        {([{ id: "all" as const, l: "Tout" }, { id: "demos" as const, l: "Démonstrations" }, { id: "hist" as const, l: "Historique" }]).map(t => (
          <button key={t.id} onClick={() => { setTab(t.id); setFam(null); }} style={{
            padding: "8px 16px", fontSize: 13, fontWeight: 600, fontFamily: dash.fontMain, border: "none", background: "none", cursor: "pointer",
            color: tab === t.id ? dash.ink : dash.inkMuted, borderBottom: tab === t.id ? `2px solid ${dash.ink}` : "2px solid transparent", marginBottom: -1,
          }}>{t.l}</button>
        ))}
      </div>

      <AnimatePresence mode="wait">
        {(tab === "all" || tab === "demos") && (
          <motion.div key="d" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }} style={{ marginBottom: 40 }}>
            {tab === "all" && <h2 style={{ fontSize: 17, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>🔬 Démonstrations</h2>}
            <div style={{ display: "flex", gap: 6, flexWrap: "wrap", marginBottom: 20 }}>
              <button onClick={() => setFam(null)} style={{ padding: "5px 12px", borderRadius: 8, fontSize: 12, fontWeight: 600, fontFamily: dash.fontMain, border: `1px solid ${!fam ? dash.ink : dash.border}`, background: !fam ? dash.ink : dash.card, color: !fam ? "#fff" : dash.inkMuted, cursor: "pointer" }}>Toutes</button>
              {FAMILLES.map(f => (
                <button key={f.id} onClick={() => setFam(f.id === fam ? null : f.id)} style={{ padding: "5px 12px", borderRadius: 8, fontSize: 12, fontWeight: 600, fontFamily: dash.fontMain, border: `1px solid ${fam === f.id ? dash.ink : dash.border}`, background: fam === f.id ? dash.ink : dash.card, color: fam === f.id ? "#fff" : dash.inkMuted, cursor: "pointer" }}>{f.icon} {f.label}</button>
              ))}
            </div>
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {fd.map((a, i) => {
                const cr = CROSS[a.slug];
                return (
                  <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                    <div className="dash-card" style={{ overflow: "hidden" }}>
                      <Link href={`/article/${a.slug}`} style={{ display: "flex", cursor: "pointer" }}>
                        <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: "hidden" }}>
                          <img src={getArticleImage(a.slug)} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} loading="lazy" />
                        </div>
                        <div style={{ padding: "18px 24px", flex: 1, minWidth: 0 }}>
                          <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 4, lineHeight: 1.3 }}>{a.title}</div>
                          <div style={{ fontSize: 11, color: dash.inkGhost, marginBottom: 6, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                          {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.5, overflow: "hidden", textOverflow: "ellipsis", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" as any }}>{a.description}</div>}
                        </div>
                      </Link>
                      {cr && <div style={{ padding: "8px 20px 12px", borderTop: `1px solid ${dash.borderSoft}` }}><Link href={`/article/${cr.slug}`} style={{ fontSize: 11, color: dash.lavender, fontWeight: 600 }}>↗ {cr.label}</Link></div>}
                    </div>
                  </motion.div>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>

      <AnimatePresence mode="wait">
        {(tab === "all" || tab === "hist") && (
          <motion.div key="h" initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}>
            {tab === "all" && <h2 style={{ fontSize: 17, fontWeight: 750, color: dash.ink, marginBottom: 16 }}>📜 Retracement historique</h2>}
            <div style={{ display: "flex", flexDirection: "column", gap: 14 }}>
              {historical.map((a, i) => (
                <motion.div key={a.slug} initial={{ opacity: 0, y: 8 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.04 }}>
                  <Link href={`/article/${a.slug}`} className="dash-card" style={{ display: "flex", overflow: "hidden", cursor: "pointer" }}>
                    <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: "hidden" }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: "100%", height: "100%", objectFit: "cover" }} loading="lazy" />
                    </div>
                    <div style={{ padding: "18px 24px", flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 4, lineHeight: 1.3 }}>{a.title}</div>
                      <div style={{ fontSize: 11, color: dash.inkGhost, marginBottom: 6, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                      {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.5, overflow: "hidden", textOverflow: "ellipsis", display: "-webkit-box", WebkitLineClamp: 2, WebkitBoxOrient: "vertical" as any }}>{a.description}</div>}
                    </div>
                  </Link>
                </motion.div>
              ))}
            </div>
            <div className="dash-card" style={{ marginTop: 24, padding: "18px 22px", display: "flex", alignItems: "center", gap: 14 }}>
              <span style={{ fontSize: 24 }}>📺</span>
              <div><div style={{ fontSize: 13, fontWeight: 650, color: dash.ink }}>Chaîne recommandée</div><div style={{ fontSize: 12, color: dash.inkMuted }}>Le Lab&apos;O Sciences</div></div>
              <a href="https://www.youtube.com/@lelabosciences2216" target="_blank" rel="noopener noreferrer" style={{ marginLeft: "auto", fontSize: 12, fontWeight: 600, color: dash.lavender }}>Voir →</a>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
