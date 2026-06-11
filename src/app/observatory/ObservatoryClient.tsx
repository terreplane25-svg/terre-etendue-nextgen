'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { useSearchParams } from 'next/navigation';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import SectionHeader from '@/components/SectionHeader';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const SECTIONS = [
  { id: 'optique', label: 'Optique & horizon', icon: '🔭', slugs: [
    'ce-quon-voit-quand-on-ne-devrait-plus-voir',
    'la-perspective-pourquoi-les-objets-disparaissent',
    'les-telescopes-et-la-courbure-terrestre',
    'loeil-humain-la-machine-a-voir-qui-faconne-notre-realite',
    'pression-lumiere-halos-rayons-et-ondes',
  ]},
  { id: 'hydrologie', label: 'Hydrologie', icon: '🌊', slugs: [
    'leau-ne-ment-pas',
    'cartes-routes-boussoles-et-le-mystere-antarctique',
    'les-marees-contre-lheliocentrisme',
    'le-pole-sud-nexiste-pas',
    'lespace-une-frontiere-infranchissable',
    'pourquoi-les-choses-montent-et-descendent',
  ]},
  { id: 'astronomie', label: 'Astronomie', icon: '🌙', slugs: [
    'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
    'la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas',
    'la-lune-fonction-et-anomalies',
    'le-theodolite-celeste',
    'le-pendule-de-foucault-une-preuve-contestee',
    'les-horloges-atomiques-ne-prouvent-rien',
  ]},
];

function getSection(slug: string) {
  for (const s of SECTIONS) { if (s.slugs.includes(slug)) return s.id; }
  return null;
}

const EXP_LINKS: Record<string, { slug: string; label: string }> = {
  "pourquoi-les-choses-montent-et-descendent": { slug: "densite-pourquoi-les-choses-montent-et-descendent", label: "Fiche expérience : densité" },
  "pression-lumiere-halos-rayons-et-ondes": { slug: "la-pression-atmospherique-un-ocean-d-air-invisible", label: "Fiche expérience : pression" },
  "lhorizon-la-perspective-et-la-refraction": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "ce-quon-voit-quand-on-ne-devrait-plus-voir": { slug: "diminution-angulaire-taille-apparente", label: "Fiche expérience : angle visuel" },
  "cartes-routes-boussoles-et-le-mystere-antarctique": { slug: "magnetisme-et-electromagnetisme", label: "Fiche expérience : magnétisme" },
};

export default function ObservatoryClient({ articles }: { articles: A[] }) {
  const searchParams = useSearchParams();
  const initialFilter = searchParams.get('filter') || 'all';
  const [filter, setFilter] = useState(initialFilter);

  const filtered = filter === 'all'
    ? articles
    : articles.filter(a => getSection(a.slug) === filter);

  return (
    <div>
      <SectionHeader pillar="OBS" pillarNum="02" subtitle="Données empiriques" title="L'Observatoire" color={dash.cyan} count={articles.length} countLabel="analyses — observations, optique, hydrologie et astronomie" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          <Link href="/experiences" style={{ fontSize: 13, fontWeight: 600, color: dash.opal, padding: '6px 14px', borderRadius: 6, background: `${dash.opal}10` }}>
            Voir les fiches expériences →
          </Link>
        </div>

        {/* Section filters */}
        <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap', marginBottom: 24 }}>
          <button onClick={() => setFilter('all')} style={{
            padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
            border: `1px solid ${filter === 'all' ? dash.cyan : dash.border}`,
            background: filter === 'all' ? dash.cyan : dash.card,
            color: filter === 'all' ? '#fff' : dash.inkMuted,
            cursor: 'pointer', fontFamily: dash.fontMain,
          }}>Tout ({articles.length})</button>
          {SECTIONS.map(s => {
            const count = articles.filter(a => getSection(a.slug) === s.id).length;
            if (count === 0) return null;
            return (
              <button key={s.id} onClick={() => setFilter(filter === s.id ? 'all' : s.id)} style={{
                padding: '6px 14px', borderRadius: 6, fontSize: 13, fontWeight: 600,
                border: `1px solid ${filter === s.id ? dash.cyan : dash.border}`,
                background: filter === s.id ? dash.cyan : dash.card,
                color: filter === s.id ? '#fff' : dash.inkMuted,
                cursor: 'pointer', fontFamily: dash.fontMain,
              }}>{s.icon} {s.label} ({count})</button>
            );
          })}
        </div>

        {/* Articles list */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {filtered.map((a, i) => {
            const exp = EXP_LINKS[a.slug];
            const section = SECTIONS.find(s => s.id === getSection(a.slug));
            return (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                <div className="dash-card" style={{ overflow: 'hidden' }}>
                  <Link href={`/article/${a.slug}`} className="article-card-row" style={{ display: 'flex', cursor: 'pointer' }}>
                    <div className="article-card-thumb" style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                    </div>
                    <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                      {section && filter === 'all' && (
                        <div style={{ fontSize: 11, fontWeight: 700, color: dash.cyan, marginBottom: 4, letterSpacing: '0.04em' }}>
                          {section.icon} {section.label}
                        </div>
                      )}
                      <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>
                        {a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}
                      </div>
                      <div style={{ fontSize: 12, color: dash.inkGhost, marginBottom: 8, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                      {a.description && (
                        <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as never }}>{a.description}</div>
                      )}
                    </div>
                  </Link>
                  {exp && (
                    <div style={{ padding: '10px 24px 14px', borderTop: `1px solid ${dash.borderSoft}` }}>
                      <Link href={`/article/${exp.slug}`} style={{ fontSize: 12, color: dash.opal, fontWeight: 600 }}>🧪 {exp.label}</Link>
                    </div>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
