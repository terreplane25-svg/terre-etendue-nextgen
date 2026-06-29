'use client';
import React from 'react';
import { dash } from '@/lib/design-tokens';
import SectionHeader from '@/components/SectionHeader';
import PageIntro from '@/components/PageIntro';
import CategoryFlow from '@/components/CategoryFlow';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const SECTIONS = [
  { id: 'coran', label: 'Coran & Sunna', icon: '📖', slugs: [
    'debut-de-la-creation-selon-le-coran-et-la-sunna',
    'debut-de-la-creation-le-soleil-mobile-la-terre-immobile',
    'la-terre-dans-le-coran',
    'dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne',
    'la-qibla-et-la-direction-cote-ouest',
  ]},
  { id: 'historique', label: 'Textes historiques', icon: '🕌', slugs: [
    'le-consensus-sur-la-sphericite',
    'pres-de-cent-savants-de-lislam',
    'sources-historiques-le-fonds-documentaire-1865-1920',
  ]},
  { id: 'cosmographie', label: 'Cosmographie', icon: '🌍', slugs: [
    'levolution-et-lislam',
    'mise-en-garde-la-kaaba-et-saturne',
  ]},
];

export default function LibraryClient({ priority, articles }: { priority: A[]; articles: A[] }) {
  const allArticles = [...priority, ...articles];
  return (
    <div>
      <SectionHeader pillar="BIBLIO" pillarNum="03" subtitle="Sources sacrées" title="La Bibliothèque" color={dash.saffron} count={allArticles.length} countLabel="publications — Coran, Sunna, textes historiques et cosmographie" />
      <PageIntro color={dash.saffron}
        lede="Ce que le texte établit — avant toute interprétation."
        body="Ici, le Coran et la Sunna sont lus comme une édition critique : verset en arabe, traduction, source datée et vérifiable. On y sépare ce que le texte dit de ce qu'on lui a fait dire — et l'on s'en tient aux références." />
      <CategoryFlow sections={SECTIONS} articles={allArticles} color={dash.saffron} basePath="/library" featuredSlug={priority[0]?.slug} />
    </div>
  );
}
