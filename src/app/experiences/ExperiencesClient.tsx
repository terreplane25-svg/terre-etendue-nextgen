"use client";
import Link from "next/link";
import React from "react";
import { dash } from "@/lib/design-tokens";
import SectionHeader from "@/components/SectionHeader";
import PageIntro from "@/components/PageIntro";
import CategoryFlow from "@/components/CategoryFlow";

interface AE { slug: string; title: string; description: string; category: string; tags: string[]; pinned: boolean; readTime: number; }

const FAMILLES = [
  { id: "fluides", label: "Fluides & matière", icon: "💧", tags: ["densité","pression","masse","vide","mécanique-des-fluides","états-de-la-matière","pression-réduite","cloche-à-vide","eau"] },
  { id: "optique", label: "Optique & perspective", icon: "🔭", tags: ["perspective","angle-visuel","taille-apparente","point-de-fuite","diffusion-rayleigh"] },
  { id: "oeil", label: "L'œil humain", icon: "👁", tags: ["champ-visuel","stéréoscopie","accommodation","persistance-rétinienne","cristallin","œil-humain"] },
  { id: "forces", label: "Forces & interactions", icon: "⚡", tags: ["action-réaction","magnétisme","électromagnétisme","charge-électrique","électricité-statique"] },
];
const CROSS: Record<string, { slug: string; label: string }> = {
  "densite-et-flottabilite": { slug: "densite-pourquoi-les-choses-montent-et-descendent", label: "Analyse complète" },
  "la-pression-atmospherique": { slug: "pression-lumiere-halos-rayons-et-ondes", label: "Analyse complète" },
  "la-pression-atmospherique-un-ocean-d-air-invisible": { slug: "pression-lumiere-halos-rayons-et-ondes", label: "Analyse complète" },
  "la-perspective-lineaire": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Analyse optique" },
  "diminution-angulaire-taille-apparente": { slug: "la-perspective-pourquoi-les-objets-disparaissent", label: "Dossier optique complet" },
  "la-perspective-atmospherique": { slug: "lhorizon-la-perspective-et-la-refraction", label: "Analyse optique" },
  "magnetisme-et-electromagnetisme": { slug: "cartes-routes-boussoles-et-le-mystere-antarctique", label: "Analyse géographique" },
};

export default function ExperiencesClient({ demonstrations }: { demonstrations: AE[] }) {
  const all = demonstrations;

  const sections = FAMILLES.map(f => ({
    id: f.id, label: f.label, icon: f.icon,
    match: (a: { slug: string; tags?: string[] }) =>
      a.tags?.some(t => f.tags.includes(t)) ?? false,
  }));

  const demoFooter = (a: { slug: string }) => {
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
      <SectionHeader pillar="EXP" pillarNum="05" subtitle="Physique naturelle" title="Laboratoire de Physique Naturelle" color={dash.rose} count={demonstrations.length} countLabel="démonstrations reproductibles" />
      <PageIntro color={dash.rose}
        lede="Ne nous croyez pas. Faites-le vous-même."
        body="Chaque démonstration est reproductible chez soi : matériel courant, protocole pas à pas, ce qui se passe, ce que ça change. Densité, pression, perspective, électricité — la physique se vérifie à la main, sans autorité à invoquer." />
      <CategoryFlow sections={sections} articles={all} color={dash.rose} basePath="/experiences" footer={demoFooter} />
    </div>
  );
}
