'use client';
import React from 'react';
import Link from 'next/link';
import { dash } from '@/lib/design-tokens';
import SectionHeader from '@/components/SectionHeader';
import PageIntro from '@/components/PageIntro';
import CategoryFlow from '@/components/CategoryFlow';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const SECTIONS = [
  { id: 'optique', label: 'Optique & horizon', icon: '🔭', slugs: [
    'la-perspective-pourquoi-les-objets-disparaissent',
    'loeil-humain-la-machine-a-voir-qui-faconne-notre-realite',
    'pression-lumiere-halos-rayons-et-ondes',
  ]},
  { id: 'hydrologie', label: 'Hydrologie', icon: '🌊', slugs: [
    'leau-ne-ment-pas',
    'cartes-routes-boussoles-et-le-mystere-antarctique',
    'les-marees-contre-lheliocentrisme',
    'le-pole-sud-nexiste-pas',
    'lespace-une-frontiere-infranchissable',
    'densite-pourquoi-les-choses-montent-et-descendent',
  ]},
  { id: 'astronomie', label: 'Astronomie', icon: '🌙', slugs: [
    'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
    'la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas',
    'la-lune-fonction-et-anomalies',
    'le-theodolite-celeste',
    'la-rotation-terrestre-deux-experiences-zero-preuve',
  ]},
];

const EXP_LINKS: Record<string, { slug: string; label: string }> = {
  "densite-pourquoi-les-choses-montent-et-descendent": { slug: "densite-pourquoi-les-choses-montent-et-descendent", label: "Fiche expérience : densité" },
  "pression-lumiere-halos-rayons-et-ondes": { slug: "la-pression-atmospherique-un-ocean-d-air-invisible", label: "Fiche expérience : pression" },
  "lhorizon-la-perspective-et-la-refraction": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "la-perspective-pourquoi-les-objets-disparaissent": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "cartes-routes-boussoles-et-le-mystere-antarctique": { slug: "magnetisme-et-electromagnetisme", label: "Fiche expérience : magnétisme" },
};

export default function ObservatoryClient({ articles }: { articles: A[] }) {
  const articleFooter = (a: { slug: string }) => {
    const exp = EXP_LINKS[a.slug];
    if (!exp) return null;
    return (
      <Link href={`/article/${exp.slug}`} style={{ fontSize: 11, color: dash.opal, fontWeight: 600 }}>
        🧪 {exp.label}
      </Link>
    );
  };

  return (
    <div>
      <SectionHeader pillar="OBS" pillarNum="02" subtitle="Données empiriques" title="L'Observatoire" color={dash.cyan} count={articles.length} countLabel="analyses — observations, optique, hydrologie et astronomie" />
      <PageIntro color={dash.cyan}
        lede="Regardez ce que vous observez vraiment."
        body="L'Observatoire confronte le modèle aux données : marées, horizon, réfraction, trajectoires célestes. Tableaux de mesures, sources institutionnelles (NOAA, NASA, ESA, SHOM) et schémas optiques à l'appui. Pas d'opinion — ce que montrent les chiffres." />
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '12px 32px 0' }}>
        <Link href="/experiences" style={{ fontSize: 13, fontWeight: 600, color: dash.opal, padding: '6px 14px', borderRadius: 6, background: `${dash.opal}10` }}>
          Voir les fiches expériences →
        </Link>
      </div>
      <CategoryFlow sections={SECTIONS} articles={articles} color={dash.cyan} basePath="/observatory" footer={articleFooter} />
    </div>
  );
}
