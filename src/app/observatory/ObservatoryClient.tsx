'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import PageHero from '@/components/PageHero';

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }
const EXP_LINKS: Record<string, { slug: string; label: string }> = {
  "pourquoi-les-choses-montent-et-descendent": { slug: "densite-et-flottabilite", label: "Fiche expérience : densité" },
  "pression-lumiere-halos-rayons-et-ondes": { slug: "la-pression-atmospherique", label: "Fiche expérience : pression" },
  "lhorizon-la-perspective-et-la-refraction": { slug: "la-perspective-lineaire", label: "Fiche expérience : perspective" },
  "ce-quon-voit-quand-on-ne-devrait-plus-voir": { slug: "diminution-angulaire-taille-apparente", label: "Fiche expérience : angle visuel" },
  "cartes-routes-boussoles-et-le-mystere-antarctique": { slug: "magnetisme-et-electromagnetisme", label: "Fiche expérience : magnétisme" },
};

export default function ObservatoryClient({ articles }: { articles: A[] }) {
  const [filter, setFilter] = useState('all');
  const filtered = filter === 'all' ? articles : filter === 'pinned' ? articles.filter(a => a.pinned) : articles;

  return (
    <div>
      <PageHero title="L'Observatoire" subtitle={`${articles.length} analyses · Données empiriques`} color={dash.cyan} image="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/imgage_accueil.png" />
      <div style={{ maxWidth: 960, margin: '0 auto', padding: '0 24px 64px' }}>
        <div style={{ display: 'flex', gap: 8, marginBottom: 20 }}>
          <Link href="/experiences" style={{ fontSize: 13, fontWeight: 600, color: dash.opal, padding: '6px 14px', borderRadius: 4, background: dash.opalSoft }}>Voir les fiches expériences →</Link>
        </div>
        <div style={{ display: 'flex', gap: 6, marginBottom: 24 }}>
          {[{ id: 'all', l: 'Tout' }, { id: 'pinned', l: '★ Épinglés' }].map(f => (
            <button key={f.id} onClick={() => setFilter(f.id)} style={{ padding: '7px 16px', borderRadius: 4, fontSize: 13, fontWeight: 600, fontFamily: dash.fontMain, border: `1px solid ${filter === f.id ? dash.ink : dash.border}`, background: filter === f.id ? dash.ink : dash.card, color: filter === f.id ? '#fff' : dash.inkMuted, cursor: 'pointer' }}>{f.l}</button>
          ))}
        </div>
        <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
          {filtered.map((a, i) => {
            const exp = EXP_LINKS[a.slug];
            return (
              <motion.div key={a.slug} initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }} transition={{ delay: i * 0.03 }}>
                <div className="dash-card" style={{ overflow: 'hidden' }}>
                  <Link href={`/article/${a.slug}`} style={{ display: 'flex', cursor: 'pointer' }}>
                    <div style={{ width: 180, minHeight: 140, flexShrink: 0, overflow: 'hidden' }}>
                      <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
                    </div>
                    <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                      <div style={{ fontSize: 17, fontWeight: 700, color: dash.ink, marginBottom: 6, lineHeight: 1.35 }}>{a.pinned && <span style={{ color: dash.saffron, marginRight: 6 }}>★</span>}{a.title}</div>
                      <div style={{ fontSize: 12, color: dash.inkGhost, marginBottom: 8, fontFamily: dash.fontMono }}>Terre Etendue · {a.readTime} min</div>
                      {a.description && <div style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.55, overflow: 'hidden', textOverflow: 'ellipsis', display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any }}>{a.description}</div>}
                    </div>
                  </Link>
                  {exp && <div style={{ padding: '10px 24px 14px', borderTop: `1px solid ${dash.borderSoft}` }}><Link href={`/article/${exp.slug}`} style={{ fontSize: 12, color: dash.opal, fontWeight: 600 }}>🧪 {exp.label}</Link></div>}
                </div>
              </motion.div>
            );
          })}
        </div>
      </div>
    </div>
  );
}
