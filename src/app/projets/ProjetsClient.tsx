'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import type { Projet } from '@/lib/projets';

const fade = (i: number) => ({
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: 0.08 + i * 0.06 },
});

const ACCENT = '#2B7A5F';

const STATUT_MAP: Record<string, { label: string; color: string; icon: string }> = {
  financement: { label: 'En financement', color: '#D4943A', icon: '🟡' },
  preparation: { label: 'En préparation', color: '#3B8FD4', icon: '🔵' },
  'en-cours': { label: 'En cours', color: '#8B7EC8', icon: '🟣' },
  terminee: { label: 'Réalisée', color: '#3D9E7C', icon: '🟢' },
  publiee: { label: 'Résultats publiés', color: '#2B7A5F', icon: '📄' },
};

const DONATE_URL = 'https://ko-fi.com/terreetendue';

interface Props {
  projets: Projet[];
}

export default function ProjetsClient({ projets }: Props) {
  const [expandedBudget, setExpandedBudget] = useState<string | null>(null);

  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(135deg, #0D1528 0%, #1A2538 50%, #0D1528 100%)',
        padding: '64px 24px 56px',
        borderBottom: `3px solid ${ACCENT}`,
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            fontSize: 11, fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase',
            color: ACCENT, marginBottom: 16,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            Projets & Expériences
          </div>
          <h1 style={{
            fontSize: 36, fontWeight: 900, color: '#E8EDF4', letterSpacing: '-0.02em',
            lineHeight: 1.2, marginBottom: 16,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}>
            Financez la prochaine expérience
          </h1>
          <p style={{
            fontSize: 17, color: '#8A95A8', lineHeight: 1.65, maxWidth: 640,
            margin: '0 auto 12px',
          }}>
            Tout le contenu du site est <strong style={{ color: '#C8D8E8' }}>gratuit et le restera</strong>. Ici, vous financez des expériences scientifiques réelles — avec un budget transparent, un protocole détaillé et des résultats publiés <strong style={{ color: '#C8D8E8' }}>quoi qu&apos;il arrive</strong>.
          </p>
          <p style={{ fontSize: 14, color: '#607890', lineHeight: 1.6 }}>
            Chaque euro finance du matériel et des déplacements. Pas des serveurs, pas des salaires.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 900, margin: '0 auto', padding: '48px 24px 80px' }}>

        {/* ═══ PRINCIPES ═══ */}
        <motion.section {...fade(0)}>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(240px, 1fr))', gap: 14, marginBottom: 48 }}>
            {[
              { icon: '🔬', title: 'Protocole public', desc: 'Chaque expérience est documentée avant, pendant et après. Vous savez exactement ce qui sera fait.' },
              { icon: '💶', title: 'Budget transparent', desc: 'Chaque poste de dépense est détaillé. Pas de frais cachés, pas d\'intermédiaire.' },
              { icon: '📊', title: 'Résultats publiés', desc: 'Données brutes, photos, vidéos. Même si le résultat contredit notre hypothèse.' },
              { icon: '🗳️', title: 'Communauté décide', desc: 'Les contributeurs votent pour la prochaine expérience à financer.' },
            ].map((p, i) => (
              <motion.div key={i} {...fade(i + 1)} style={{
                padding: '20px 18px', borderRadius: 10,
                background: 'var(--card)', border: '1px solid var(--border)',
              }}>
                <div style={{ fontSize: 24, marginBottom: 10 }}>{p.icon}</div>
                <div style={{ fontSize: 14, fontWeight: 750, color: 'var(--ink)', marginBottom: 6 }}>{p.title}</div>
                <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.5, margin: 0 }}>{p.desc}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ PROJECTS ═══ */}
        {projets.map((projet, pi) => {
          const pct = Math.min(100, Math.round((projet.collecte / projet.objectif) * 100));
          const statut = STATUT_MAP[projet.statut] || STATUT_MAP.financement;
          const budgetTotal = projet.budget.reduce((sum, b) => sum + b.montant, 0);
          const isExpanded = expandedBudget === projet.id;

          return (
            <motion.section key={projet.id} id={projet.id} {...fade(pi + 2)} style={{ marginBottom: 40 }}>
              <div style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 14,
                overflow: 'hidden',
              }}>
                {/* Header */}
                <div style={{ padding: '28px 28px 0' }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 14, flexWrap: 'wrap' }}>
                    <span style={{
                      fontSize: 11, fontWeight: 700, color: statut.color,
                      padding: '4px 10px', borderRadius: 6, background: `${statut.color}12`,
                      border: `1px solid ${statut.color}25`,
                      fontFamily: "'JetBrains Mono', monospace", letterSpacing: '0.04em',
                      textTransform: 'uppercase',
                    }}>
                      {statut.icon} {statut.label}
                    </span>
                    {projet.simulateur && (
                      <Link href={`/lab?tool=${projet.simulateur}`} style={{
                        fontSize: 10, fontWeight: 600, color: '#8B7EC8',
                        padding: '4px 10px', borderRadius: 6, background: '#8B7EC810',
                        border: '1px solid #8B7EC820', textDecoration: 'none',
                        fontFamily: "'JetBrains Mono', monospace",
                      }}>
                        🖥️ Simulateur lié
                      </Link>
                    )}
                  </div>

                  <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)', lineHeight: 1.3, marginBottom: 14 }}>
                    {projet.titre}
                  </h2>

                  {/* Progress bar */}
                  <div style={{ marginBottom: 8 }}>
                    <div style={{ height: 8, background: 'var(--border)', borderRadius: 4, overflow: 'hidden' }}>
                      <div style={{
                        height: '100%', borderRadius: 4,
                        background: pct >= 100
                          ? 'linear-gradient(90deg, #2B7A5F, #3D9E7C)'
                          : `linear-gradient(90deg, ${statut.color}, ${statut.color}CC)`,
                        width: `${pct}%`, transition: 'width 0.8s ease',
                      }} />
                    </div>
                    <div style={{ display: 'flex', justifyContent: 'space-between', marginTop: 6 }}>
                      <span style={{ fontSize: 14, fontWeight: 800, color: statut.color, fontFamily: "'JetBrains Mono', monospace" }}>
                        {projet.collecte}€ / {projet.objectif}€
                      </span>
                      <span style={{ fontSize: 12, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                        {pct}% · {projet.donateurs} contributeur{projet.donateurs > 1 ? 's' : ''}
                      </span>
                    </div>
                  </div>
                </div>

                {/* Content */}
                <div style={{ padding: '20px 28px 28px' }}>

                  {/* Question */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#3B8FD4', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                      ❓ La question
                    </div>
                    <div style={{
                      fontSize: 15, color: 'var(--ink)', lineHeight: 1.6, fontWeight: 500,
                      padding: '14px 16px', background: '#3B8FD408', borderRadius: 8,
                      border: '1px solid #3B8FD415', fontStyle: 'italic',
                    }}>
                      {projet.question}
                    </div>
                  </div>

                  {/* Protocole */}
                  <div style={{ marginBottom: 20 }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: '#8B7EC8', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                      🔬 Le protocole
                    </div>
                    <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.65, margin: 0 }}>
                      {projet.protocole}
                    </p>
                  </div>

                  {/* Budget */}
                  <div style={{ marginBottom: 20 }}>
                    <button
                      onClick={() => setExpandedBudget(isExpanded ? null : projet.id)}
                      style={{
                        display: 'flex', alignItems: 'center', gap: 8, width: '100%',
                        background: 'none', border: 'none', cursor: 'pointer', padding: 0, marginBottom: 10,
                      }}
                    >
                      <span style={{ fontSize: 11, fontWeight: 700, color: '#D4943A', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace" }}>
                        💶 Budget détaillé ({budgetTotal}€)
                      </span>
                      <span style={{
                        fontSize: 12, color: 'var(--ink-muted)', transition: 'transform 0.2s',
                        transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)',
                      }}>▾</span>
                    </button>
                    {isExpanded && (
                      <div style={{
                        background: 'var(--bg)', borderRadius: 8, overflow: 'hidden',
                        border: '1px solid var(--border)',
                      }}>
                        {projet.budget.map((b, i) => (
                          <div key={i} style={{
                            display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                            padding: '10px 16px',
                            borderBottom: i < projet.budget.length - 1 ? '1px solid var(--border)' : 'none',
                          }}>
                            <span style={{ fontSize: 13, color: 'var(--ink-soft)' }}>{b.poste}</span>
                            <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--ink)', fontFamily: "'JetBrains Mono', monospace" }}>
                              {b.montant}€
                            </span>
                          </div>
                        ))}
                        <div style={{
                          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
                          padding: '10px 16px', borderTop: '2px solid var(--border)',
                          background: 'var(--card)',
                        }}>
                          <span style={{ fontSize: 13, fontWeight: 700, color: 'var(--ink)' }}>Total</span>
                          <span style={{ fontSize: 14, fontWeight: 800, color: '#D4943A', fontFamily: "'JetBrains Mono', monospace" }}>
                            {budgetTotal}€
                          </span>
                        </div>
                      </div>
                    )}
                  </div>

                  {/* Engagement */}
                  <div style={{
                    padding: '14px 16px', borderRadius: 8,
                    background: `${ACCENT}08`, border: `1px solid ${ACCENT}20`,
                    marginBottom: 20,
                  }}>
                    <div style={{ fontSize: 11, fontWeight: 700, color: ACCENT, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 6, fontFamily: "'JetBrains Mono', monospace" }}>
                      ✋ Notre engagement
                    </div>
                    <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.6, margin: 0 }}>
                      {projet.engagement}
                    </p>
                  </div>

                  {/* Links */}
                  <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap', marginBottom: 20 }}>
                    {projet.articlesLies.map(slug => (
                      <Link key={slug} href={`/article/${slug}`} style={{
                        fontSize: 12, fontWeight: 600, color: 'var(--ink-muted)',
                        padding: '5px 10px', borderRadius: 6,
                        background: 'var(--bg)', border: '1px solid var(--border)',
                        textDecoration: 'none',
                      }}>
                        📄 {slug.replace(/-/g, ' ').replace(/^./, c => c.toUpperCase()).substring(0, 40)}…
                      </Link>
                    ))}
                  </div>

                  {/* CTA */}
                  {projet.statut === 'financement' && (
                    <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
                      <a
                        href={DONATE_URL}
                        target="_blank"
                        rel="noopener noreferrer"
                        style={{
                          display: 'inline-flex', alignItems: 'center', gap: 8,
                          padding: '12px 24px', borderRadius: 8,
                          background: ACCENT, color: '#fff',
                          fontSize: 14, fontWeight: 700, textDecoration: 'none',
                          transition: 'opacity 0.15s',
                        }}
                        onMouseEnter={e => { e.currentTarget.style.opacity = '0.85'; }}
                        onMouseLeave={e => { e.currentTarget.style.opacity = '1'; }}
                      >
                        🧪 Soutenir cette expérience
                      </a>
                      <div style={{ fontSize: 12, color: 'var(--ink-muted)', display: 'flex', alignItems: 'center', gap: 6 }}>
                        <span>via Ko-fi · 0% commission</span>
                      </div>
                    </div>
                  )}

                  {/* Timeline */}
                  <div style={{ marginTop: 16, display: 'flex', gap: 16, fontSize: 11, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                    <span>Créé le {new Date(projet.dateCreation).toLocaleDateString('fr-FR', { day: 'numeric', month: 'long', year: 'numeric' })}</span>
                    <span>Objectif : {new Date(projet.dateObjectif).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}</span>
                  </div>
                </div>
              </div>
            </motion.section>
          );
        })}

        {/* ═══ COMMENT ÇA MARCHE ═══ */}
        <motion.section {...fade(projets.length + 2)} style={{ marginTop: 24 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#8B7EC8' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Comment ça marche</h2>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 0, position: 'relative' }}>
            {[
              { num: '1', label: 'Financement', desc: 'Vous contribuez au montant nécessaire. Le budget est détaillé poste par poste.', color: '#D4943A' },
              { num: '2', label: 'Préparation', desc: 'Le matériel est acheté, les lieux repérés, le protocole finalisé. Journal de bord partagé.', color: '#3B8FD4' },
              { num: '3', label: 'Expérience', desc: 'L\'expérience est réalisée selon le protocole publié. Tout est filmé et documenté.', color: '#8B7EC8' },
              { num: '4', label: 'Publication', desc: 'Résultats, données brutes, photos et vidéos publiés sur le site. Remerciement des contributeurs.', color: '#3D9E7C' },
            ].map((step, i) => (
              <div key={i} style={{ display: 'flex', gap: 16, paddingBottom: i < 3 ? 24 : 0 }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center' }}>
                  <div style={{
                    width: 36, height: 36, borderRadius: 10,
                    background: `${step.color}15`, color: step.color,
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                    fontSize: 15, fontWeight: 800, fontFamily: "'JetBrains Mono', monospace",
                    flexShrink: 0,
                  }}>
                    {step.num}
                  </div>
                  {i < 3 && (
                    <div style={{ width: 2, flex: 1, background: 'var(--border)', marginTop: 4 }} />
                  )}
                </div>
                <div style={{ paddingTop: 6 }}>
                  <div style={{ fontSize: 15, fontWeight: 750, color: 'var(--ink)', marginBottom: 4 }}>{step.label}</div>
                  <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.55, margin: 0 }}>{step.desc}</p>
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ CONTREPARTIES ═══ */}
        <motion.section {...fade(projets.length + 3)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#D4943A' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Contreparties</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Pas de contreparties matérielles. Que du symbolique à forte valeur.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: 14 }}>
            {[
              {
                level: 'Tout contributeur',
                color: '#3D9E7C',
                items: [
                  'Nom sur le mur des contributeurs',
                  'Accès au journal de bord de l\'expérience',
                  'Remerciement dans le rapport',
                ],
              },
              {
                level: 'Contributeur majeur (>25€)',
                color: '#3B8FD4',
                items: [
                  'Tout le niveau précédent',
                  'Vote sur la prochaine expérience',
                  'Mention nominative dans les résultats',
                ],
              },
              {
                level: 'Sponsor (>100€)',
                color: '#D4943A',
                items: [
                  'Tout les niveaux précédents',
                  '"Rendue possible grâce à [nom]" en tête du rapport',
                  'Proposer une question à tester',
                ],
              },
            ].map((tier, i) => (
              <motion.div key={i} {...fade(i + projets.length + 4)} style={{
                padding: '22px 20px', borderRadius: 10,
                background: 'var(--card)', border: `1px solid ${tier.color}25`,
                borderTop: `3px solid ${tier.color}`,
              }}>
                <div style={{ fontSize: 14, fontWeight: 750, color: tier.color, marginBottom: 12 }}>{tier.level}</div>
                <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                  {tier.items.map((item, j) => (
                    <div key={j} style={{ display: 'flex', gap: 8, alignItems: 'flex-start' }}>
                      <span style={{ color: tier.color, fontSize: 12, marginTop: 2, flexShrink: 0 }}>✓</span>
                      <span style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.4 }}>{item}</span>
                    </div>
                  ))}
                </div>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ CTA FINAL ═══ */}
        <motion.section {...fade(projets.length + 5)} style={{ marginTop: 56 }}>
          <div style={{
            padding: '36px 28px', background: 'linear-gradient(135deg, #0D1528, #1A2538)',
            borderRadius: 12, textAlign: 'center',
          }}>
            <p style={{ fontSize: 20, fontWeight: 700, color: '#E8EDF4', marginBottom: 8 }}>
              Vous ne payez pas pour consommer du contenu.
            </p>
            <p style={{ fontSize: 16, color: '#8A95A8', marginBottom: 24, lineHeight: 1.6 }}>
              Vous payez pour faire exister la suite.
            </p>
            <a
              href={DONATE_URL}
              target="_blank"
              rel="noopener noreferrer"
              style={{
                display: 'inline-flex', alignItems: 'center', gap: 10,
                padding: '14px 28px', borderRadius: 8,
                background: ACCENT, color: '#fff',
                fontSize: 15, fontWeight: 700, textDecoration: 'none',
              }}
            >
              🧪 Soutenir une expérience sur Ko-fi
            </a>
            <div style={{ fontSize: 12, color: '#607890', marginTop: 10, fontFamily: "'JetBrains Mono', monospace" }}>
              0% de commission · 100% va au matériel
            </div>
          </div>
        </motion.section>

      </div>
    </div>
  );
}
