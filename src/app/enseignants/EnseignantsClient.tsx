'use client';
import React, { useState } from 'react';
import Link from 'next/link';
import { motion } from 'framer-motion';
import type { Fiche } from '@/lib/fiches';

const fade = (i: number) => ({
  initial: { opacity: 0, y: 14 },
  animate: { opacity: 1, y: 0 },
  transition: { delay: 0.08 + i * 0.06 },
});

const ACCENT = '#2B7A5F';
const ACCENT_SOFT = '#2B7A5F12';

const CYCLE_COLORS: Record<string, string> = {
  '3': '#3B8FD4',
  '4': '#8B7EC8',
};

const SIMULATEURS = [
  {
    id: 'classifier',
    titre: 'Trieur Fait / Modèle / Hypothèse',
    description: '24 affirmations scientifiques à classer. Feedback immédiat avec explication et source pour chaque réponse.',
    usage: 'L\'outil pédagogique central. Projetez-le au tableau et faites voter la classe avant de révéler la réponse. Question : "Pourquoi avez-vous classé ça comme un fait ?"',
    programme: 'Tous cycles — Épistémologie',
    icon: '🎯',
    color: '#2B7A5F',
  },
  {
    id: 'perspective',
    titre: 'Comment la taille apparente change avec la distance',
    description: 'Deux modèles côte à côte : disparition par perspective vs occultation par courbure. L\'élève manipule et observe la différence.',
    usage: 'Montrer que la diminution angulaire fait "disparaître" un objet avant qu\'il ne soit physiquement caché. Question : "À partir de quelle distance ne voit-on plus le bateau ?"',
    programme: 'Cycle 4 — Optique, propagation de la lumière',
    icon: '👁️',
    color: '#8B7EC8',
  },
  {
    id: 'density',
    titre: 'Pourquoi les objets flottent ou coulent',
    description: 'Colonne de fluides interactive. Lâchez des objets de différentes densités et observez leur comportement.',
    usage: 'Démontrer que la flottabilité dépend de la densité relative, pas d\'une "force" mystérieuse. Question : "Pourquoi le bois flotte et le fer coule ?"',
    programme: 'Cycle 3/4 — La matière, masse et volume',
    icon: '⚗️',
    color: '#3D9E7C',
  },
  {
    id: 'visualfield',
    titre: 'Les limites de résolution de l\'œil humain',
    description: 'Taille angulaire, arc-minute et distance maximale de visibilité. Pourquoi un objet peut disparaître sans être "caché".',
    usage: 'Montrer que l\'œil a une limite physique de résolution (~1 arc-minute). Question : "À quelle distance un objet de 1m devient-il invisible ?"',
    programme: 'Cycle 4 — Optique, SVT (l\'œil)',
    icon: '🔬',
    color: '#C45E6A',
  },
  {
    id: 'curvature',
    titre: 'Calculateur de courbure théorique',
    description: 'Entrez une distance et un indice de réfraction. Le calculateur affiche la chute théorique attendue sur une sphère.',
    usage: 'Comparer la prédiction théorique avec des observations réelles (bâtiments, îles visibles). Question : "Ce résultat correspond-il à ce qu\'on observe ?"',
    programme: 'Cycle 4 — Mathématiques (géométrie), Physique',
    icon: '📐',
    color: '#3D9E7C',
  },
  {
    id: 'geo',
    titre: 'Le système solaire en 3D',
    description: '8 planètes avec orbites, anneaux de Saturne, vitesses réelles. Mode classique (héliocentrique) ou vortex.',
    usage: 'Visualiser les échelles et les vitesses. Montrer que "modèle" signifie "représentation", pas "photographie". Question : "Pourquoi y a-t-il deux modes d\'affichage ?"',
    programme: 'Cycle 3 — Le système solaire',
    icon: '🪐',
    color: '#D4943A',
  },
  {
    id: 'laser',
    titre: 'Expérience laser sur plan d\'eau',
    description: 'Simulation d\'une expérience laser sur une surface d\'eau calme. Trajectoire droite vs écart de courbure prédit.',
    usage: 'Montrer le protocole d\'une expérience reproductible. Question : "Comment pourriez-vous faire cette expérience vous-mêmes ?"',
    programme: 'Cycle 4 — Optique, propagation rectiligne',
    icon: '🔴',
    color: '#C45E6A',
  },
];

const FAQ = [
  {
    q: 'Ce site est-il "anti-science" ?',
    a: 'Non. Toutes les sources citées proviennent de la littérature scientifique mainstream : Nature, Science, The Astrophysical Journal, prix Nobel. L\'objectif est d\'enseigner la science avec plus de rigueur, pas de la rejeter.',
  },
  {
    q: 'Puis-je utiliser ces ressources en classe ?',
    a: 'Oui. Les fiches et simulateurs sont conçus pour être utilisés directement. Le livret enseignant est téléchargeable en PDF. Tout est sourcé et vérifiable.',
  },
  {
    q: 'Comment justifier cette approche devant mon inspecteur ?',
    a: 'La distinction fait/modèle/hypothèse est au programme de philosophie de terminale et fait partie des recommandations des didacticiens des sciences (Giordan, De Vecchi, Viennot). Vous ne faites que l\'introduire plus tôt — ce qui est une bonne pratique pédagogique.',
  },
  {
    q: 'Ce site a-t-il un biais idéologique ?',
    a: 'Ce site a un biais explicite : la rigueur épistémologique. Nous pensons qu\'un modèle doit être présenté comme un modèle, une hypothèse comme une hypothèse, et un fait comme un fait. C\'est tout.',
  },
  {
    q: 'Pourquoi certaines formulations des manuels sont-elles problématiques ?',
    a: 'Parce qu\'elles effacent la distinction entre ce qui est observé et ce qui est interprété. Un élève qui apprend que "la gravité est une force prouvée" ne comprend pas que le mécanisme est encore débattu — y compris dans les revues de physique les plus prestigieuses.',
  },
];

const REFERENCES = [
  { auteur: 'Karl Popper', titre: 'La Logique de la découverte scientifique', annee: '1934', note: 'Le critère de réfutabilité' },
  { auteur: 'Thomas Kuhn', titre: 'La Structure des révolutions scientifiques', annee: '1962', note: 'Les paradigmes' },
  { auteur: 'André Giordan', titre: 'Apprendre !', annee: '1998', note: 'Didactique des sciences' },
  { auteur: 'Gérard De Vecchi', titre: 'Enseigner le vrai ou le vraisemblable ?', annee: '2006', note: 'Pédagogie critique' },
  { auteur: 'Lee Smolin', titre: 'Rien ne va plus en physique', annee: '2006', note: 'Problèmes ouverts' },
  { auteur: 'Sabine Hossenfelder', titre: 'Lost in Math', annee: '2018', note: 'Biais esthétiques en physique' },
];

const SIM_LABELS: Record<string, string> = {
  density: 'Simulateur de densité',
  perspective: 'Simulateur de perspective',
  visualfield: 'Champ visuel',
  curvature: 'Calculateur de courbure',
  geo: 'Système solaire 3D',
  laser: 'Expérience laser',
  classifier: 'Trieur Fait/Modèle/Hypothèse',
};

interface Props {
  fiches: Fiche[];
}

export default function EnseignantsClient({ fiches }: Props) {
  const [expandedFiche, setExpandedFiche] = useState<string | null>(null);

  const cycle3 = fiches.filter(f => f.cycle === '3');
  const cycle4 = fiches.filter(f => f.cycle === '4');
  const groups = [
    { label: 'Cycle 3 (CM1–CM2–6e)', color: CYCLE_COLORS['3'], fiches: cycle3 },
    { label: 'Cycle 4 (5e–4e–3e)', color: CYCLE_COLORS['4'], fiches: cycle4 },
  ];

  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(135deg, #0D2818 0%, #1A3A2A 50%, #0D2818 100%)',
        padding: '64px 24px 56px',
        borderBottom: `3px solid ${ACCENT}`,
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            fontSize: 11, fontWeight: 700, letterSpacing: '0.15em', textTransform: 'uppercase',
            color: ACCENT, marginBottom: 16,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            Espace enseignants
          </div>
          <h1 style={{
            fontSize: 38, fontWeight: 900, color: '#E8EDF4', letterSpacing: '-0.02em',
            lineHeight: 1.2, marginBottom: 16,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}>
            Enseigner la science<br />comme elle est réellement
          </h1>
          <p style={{
            fontSize: 17, color: '#8A95A8', lineHeight: 1.65, maxWidth: 620,
            margin: '0 auto 32px',
          }}>
            Ressources pédagogiques pour distinguer <strong style={{ color: '#C8D8E8' }}>fait</strong>, <strong style={{ color: '#C8D8E8' }}>modèle</strong> et <strong style={{ color: '#C8D8E8' }}>hypothèse</strong> en classe. Fiches alignées sur les programmes, simulateurs interactifs et guide téléchargeable.
          </p>

          <a
            href="/livret-enseignant.pdf"
            download
            style={{
              display: 'inline-flex', alignItems: 'center', gap: 10,
              padding: '14px 28px', borderRadius: 8,
              background: ACCENT, color: '#fff',
              fontSize: 15, fontWeight: 700,
              textDecoration: 'none',
              transition: 'opacity 0.2s',
            }}
            onMouseEnter={e => { e.currentTarget.style.opacity = '0.9'; }}
            onMouseLeave={e => { e.currentTarget.style.opacity = '1'; }}
          >
            📄 Télécharger le livret enseignant (PDF)
          </a>
          <div style={{ fontSize: 12, color: '#607890', marginTop: 10, fontFamily: "'JetBrains Mono', monospace" }}>
            30 pages · 6 études de cas · 2 activités en classe · Sources vérifiables
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: '0 auto', padding: '48px 24px 80px' }}>

        {/* ═══ POURQUOI ═══ */}
        <motion.section {...fade(0)}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: ACCENT }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Pourquoi cet espace existe</h2>
          </div>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, padding: '28px 24px' }}>
            <p style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75, marginBottom: 16 }}>
              Les manuels scolaires présentent régulièrement des <strong style={{ color: 'var(--ink)' }}>modèles comme des faits</strong> et des <strong style={{ color: 'var(--ink)' }}>hypothèses comme des certitudes</strong>. Ce n&apos;est pas un reproche — c&apos;est un constat documenté par les didacticiens des sciences (Giordan, De Vecchi, Viennot).
            </p>
            <p style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75, marginBottom: 16 }}>
              Or la <strong style={{ color: 'var(--ink)' }}>distinction entre fait, modèle et hypothèse</strong> est le fondement même de la méthode scientifique. Un élève qui ne la maîtrise pas apprend un rapport d&apos;autorité à la science — pas un rapport de méthode.
            </p>
            <p style={{ fontSize: 15, color: 'var(--ink-soft)', lineHeight: 1.75, margin: 0 }}>
              Cet espace propose des outils concrets pour réintroduire cette rigueur dans l&apos;enseignement — <strong style={{ color: 'var(--ink)' }}>sans rejeter les modèles enseignés</strong>, mais en les présentant pour ce qu&apos;ils sont réellement.
            </p>
          </div>
        </motion.section>

        {/* ═══ LES 3 RÉFLEXES ═══ */}
        <motion.section {...fade(1)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#3B8FD4' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Les 3 questions réflexes à enseigner</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))', gap: 14 }}>
            {[
              { num: '1', q: 'Est-ce une observation ou une interprétation ?', ex: '« Les objets tombent » → observation. « C\'est la gravité » → interprétation.', color: '#3B8FD4' },
              { num: '2', q: 'Peut-on le vérifier soi-même ?', ex: '« L\'eau bout à 100°C » → oui. « Le Soleil est à 150M km » → non, c\'est un calcul.', color: '#8B7EC8' },
              { num: '3', q: 'Y a-t-il d\'autres explications possibles ?', ex: 'Chercher des alternatives n\'est pas du relativisme — c\'est la base de la méthode scientifique.', color: '#C45E6A' },
            ].map((r, i) => (
              <motion.div key={i} {...fade(i + 2)} style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
                padding: '22px 20px',
              }}>
                <div style={{
                  width: 32, height: 32, borderRadius: 8, background: `${r.color}15`,
                  display: 'flex', alignItems: 'center', justifyContent: 'center',
                  fontSize: 14, fontWeight: 800, color: r.color,
                  fontFamily: "'JetBrains Mono', monospace", marginBottom: 12,
                }}>{r.num}</div>
                <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--ink)', marginBottom: 8, lineHeight: 1.35 }}>{r.q}</div>
                <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.55, margin: 0 }}>{r.ex}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ GARDE-FOUS ═══ */}
        <motion.section {...fade(2)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: ACCENT }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Garde-fous : douter avec méthode</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Cet esprit critique n&apos;a de valeur que s&apos;il reste rigoureux. La ligne à tenir en classe : renforcer la confiance dans <strong style={{ color: 'var(--ink-soft)' }}>la méthode</strong>, jamais la défiance envers les scientifiques.
          </p>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '2px solid var(--border)' }}>
              <div style={{ padding: '12px 18px', fontSize: 11, fontWeight: 700, color: '#C45E6A', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace" }}>✗ Ce que ce n&apos;est PAS</div>
              <div style={{ padding: '12px 18px', fontSize: 11, fontWeight: 700, color: ACCENT, letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace", borderLeft: '1px solid var(--border)' }}>✓ Ce que c&apos;est</div>
            </div>
            {[
              ['« Les scientifiques nous mentent. »', 'Où passe exactement la frontière entre ce qu&apos;on mesure et ce qu&apos;on en déduit ?'],
              ['« Toutes les opinions se valent. »', 'Une hypothèse se juge à sa réfutabilité et à ses preuves — non, elles ne se valent pas toutes.'],
              ['« Le modèle est faux. »', 'Le modèle est un modèle : utile, prédictif, et révisable si les données changent.'],
              ['« Il faut tout remettre en cause. »', 'On doute là où c&apos;est justifié, avec des arguments — pas par principe.'],
              ['« C&apos;est un complot. »', 'Une erreur d&apos;interprétation n&apos;est pas un mensonge : la science se corrige elle-même (la masse de Neptune corrigée par Voyager 2, le désaccord persistant sur la constante G…).'],
            ].map(([non, oui], i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '1px solid var(--border)' }}>
                <div style={{ padding: '14px 18px', fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.55 }} dangerouslySetInnerHTML={{ __html: non }} />
                <div style={{ padding: '14px 18px', fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.55, borderLeft: '1px solid var(--border)' }} dangerouslySetInnerHTML={{ __html: oui }} />
              </div>
            ))}
          </div>
          <div style={{ marginTop: 14, padding: '14px 18px', background: `${ACCENT}0d`, border: `1px solid ${ACCENT}20`, borderRadius: 8, fontSize: 13.5, color: 'var(--ink-soft)', lineHeight: 1.6 }}>
            <strong style={{ color: ACCENT }}>Règle d&apos;or :</strong> toute critique s&apos;appuie sur une source vérifiable (revue à comité de lecture). Sans source, ce n&apos;est plus de la science — c&apos;est une opinion.
          </div>
        </motion.section>

        {/* ═══ FICHES PAR NIVEAU ═══ */}
        <motion.section {...fade(2)} id="fiches" style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#8B7EC8' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Fiches par niveau et chapitre du programme</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 24, lineHeight: 1.6 }}>
            Chaque fiche est alignée sur le programme officiel (Éducation nationale — France). Cliquez sur une fiche pour voir les sources, l&apos;activité détaillée et les articles liés.
          </p>

          {groups.map((groupe, gi) => (
            <div key={gi} style={{ marginBottom: 36 }}>
              <div style={{
                fontSize: 13, fontWeight: 700, color: groupe.color, letterSpacing: '0.04em',
                textTransform: 'uppercase', marginBottom: 14,
                fontFamily: "'JetBrains Mono', monospace",
              }}>
                {groupe.label}
              </div>
              <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                {groupe.fiches.map((fiche, fi) => {
                  const isExpanded = expandedFiche === fiche.id;
                  return (
                    <motion.div key={fiche.id} {...fade(gi * 3 + fi + 3)} style={{
                      background: 'var(--card)', border: `1px solid ${isExpanded ? groupe.color + '40' : 'var(--border)'}`,
                      borderRadius: 10, overflow: 'hidden',
                      transition: 'border-color 0.2s',
                    }}>
                      <button
                        onClick={() => setExpandedFiche(isExpanded ? null : fiche.id)}
                        style={{
                          width: '100%', padding: '22px 24px', background: 'none', border: 'none',
                          cursor: 'pointer', textAlign: 'left',
                        }}
                      >
                        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', gap: 12 }}>
                          <div style={{ flex: 1 }}>
                            <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 6, flexWrap: 'wrap' }}>
                              <span style={{
                                fontSize: 10, fontWeight: 700, color: groupe.color, letterSpacing: '0.08em',
                                textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace",
                              }}>
                                {fiche.matiere} — {fiche.chapitre}
                              </span>
                              <span style={{
                                fontSize: 10, fontWeight: 600, color: 'var(--ink-muted)',
                                padding: '2px 6px', background: 'var(--bg)', borderRadius: 4,
                                fontFamily: "'JetBrains Mono', monospace",
                              }}>
                                {fiche.niveau}
                              </span>
                            </div>
                            <div style={{ fontSize: 16, fontWeight: 750, color: 'var(--ink)', marginBottom: 6, lineHeight: 1.35 }}>
                              {fiche.titre}
                            </div>
                            <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, margin: 0 }}>
                              {fiche.accroche}
                            </p>
                          </div>
                          <div style={{
                            flexShrink: 0, width: 28, height: 28, borderRadius: 6,
                            background: `${groupe.color}10`, display: 'flex', alignItems: 'center', justifyContent: 'center',
                            fontSize: 14, color: groupe.color, transition: 'transform 0.2s',
                            transform: isExpanded ? 'rotate(180deg)' : 'rotate(0)',
                          }}>
                            ▾
                          </div>
                        </div>
                      </button>

                      {isExpanded && (
                        <div style={{ padding: '0 24px 24px', borderTop: `1px solid var(--border)` }}>

                          {/* Ce que dit le programme */}
                          <div style={{ marginTop: 20 }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: groupe.color, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                              📋 Ce que dit le programme
                            </div>
                            <div style={{
                              fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6,
                              padding: '12px 16px', background: 'var(--bg)', borderRadius: 8,
                              borderLeft: `3px solid ${groupe.color}`,
                              fontStyle: 'italic',
                            }}>
                              {fiche.cequeditrogram}
                            </div>
                          </div>

                          {/* Ce que dit le manuel */}
                          <div style={{ marginTop: 18 }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: '#C45E6A', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                              📖 Ce que disent les manuels
                            </div>
                            <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, margin: 0 }}>
                              {fiche.cequeditlemanuel}
                            </p>
                          </div>

                          {/* Sources scientifiques */}
                          <div style={{ marginTop: 18 }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: '#D4943A', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 10, fontFamily: "'JetBrains Mono', monospace" }}>
                              🔬 Ce que dit la littérature scientifique
                            </div>
                            <div style={{ display: 'flex', flexDirection: 'column', gap: 10 }}>
                              {fiche.cequedirlalitterature.map((src, si) => (
                                <div key={si} style={{
                                  padding: '14px 16px', background: 'var(--bg)', borderRadius: 8,
                                  borderLeft: '3px solid #D4943A30',
                                }}>
                                  <div style={{ fontSize: 12, fontWeight: 700, color: 'var(--ink)', marginBottom: 6 }}>
                                    {src.source}
                                  </div>
                                  <div style={{
                                    fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.6,
                                    fontStyle: 'italic', marginBottom: 6,
                                    paddingLeft: 12, borderLeft: '2px solid var(--border)',
                                  }}>
                                    « {src.citation} »
                                  </div>
                                  <div style={{ fontSize: 12, color: 'var(--ink-muted)', lineHeight: 1.5 }}>
                                    → {src.commentaire}
                                  </div>
                                </div>
                              ))}
                            </div>
                          </div>

                          {/* Formulation rigoureuse */}
                          <div style={{ marginTop: 18 }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: ACCENT, letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 8, fontFamily: "'JetBrains Mono', monospace" }}>
                              ✓ Formulation rigoureuse à utiliser en classe
                            </div>
                            <div style={{
                              fontSize: 14, color: 'var(--ink)', lineHeight: 1.7,
                              padding: '16px 18px', background: `${ACCENT}08`, borderRadius: 8,
                              border: `1px solid ${ACCENT}20`,
                              fontWeight: 500,
                            }}>
                              {fiche.formulation}
                            </div>
                          </div>

                          {/* Activité */}
                          <div style={{ marginTop: 18 }}>
                            <div style={{ fontSize: 11, fontWeight: 700, color: '#3B8FD4', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 10, fontFamily: "'JetBrains Mono', monospace" }}>
                              🧪 Activité en classe
                            </div>
                            <div style={{
                              padding: '18px 20px', background: 'var(--bg)', borderRadius: 10,
                              border: '1px solid var(--border)',
                            }}>
                              <div style={{ fontSize: 15, fontWeight: 750, color: 'var(--ink)', marginBottom: 8 }}>
                                {fiche.activite.titre}
                              </div>
                              <div style={{ display: 'flex', gap: 16, marginBottom: 14, flexWrap: 'wrap' }}>
                                <span style={{ fontSize: 12, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                                  ⏱ {fiche.activite.duree}
                                </span>
                                <span style={{ fontSize: 12, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                                  🧰 {fiche.activite.materiel}
                                </span>
                              </div>
                              <div style={{ display: 'flex', flexDirection: 'column', gap: 8 }}>
                                {fiche.activite.deroulement.map((step, si) => (
                                  <div key={si} style={{ display: 'flex', gap: 10, alignItems: 'flex-start' }}>
                                    <div style={{
                                      flexShrink: 0, width: 22, height: 22, borderRadius: 6,
                                      background: `#3B8FD415`, color: '#3B8FD4',
                                      display: 'flex', alignItems: 'center', justifyContent: 'center',
                                      fontSize: 11, fontWeight: 800, fontFamily: "'JetBrains Mono', monospace",
                                      marginTop: 1,
                                    }}>
                                      {si + 1}
                                    </div>
                                    <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.55, margin: 0 }}>
                                      {step}
                                    </p>
                                  </div>
                                ))}
                              </div>
                            </div>
                          </div>

                          {/* Links row */}
                          <div style={{ marginTop: 18, display: 'flex', gap: 12, flexWrap: 'wrap', alignItems: 'center' }}>
                            {fiche.simulateur && (
                              <Link href={`/lab?tool=${fiche.simulateur}`} style={{
                                fontSize: 12, fontWeight: 600, color: '#8B7EC8',
                                padding: '6px 12px', borderRadius: 6,
                                background: '#8B7EC810', border: '1px solid #8B7EC820',
                                textDecoration: 'none',
                              }}>
                                🖥️ {SIM_LABELS[fiche.simulateur] || fiche.simulateur}
                              </Link>
                            )}
                            {fiche.articlesLies.map(slug => (
                              <Link key={slug} href={`/article/${slug}`} style={{
                                fontSize: 12, fontWeight: 600, color: 'var(--ink-muted)',
                                padding: '6px 12px', borderRadius: 6,
                                background: 'var(--bg)', border: '1px solid var(--border)',
                                textDecoration: 'none',
                                maxWidth: 260, overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap',
                              }}>
                                📄 {slug.replace(/-/g, ' ').replace(/^./, c => c.toUpperCase())}
                              </Link>
                            ))}
                          </div>

                        </div>
                      )}
                    </motion.div>
                  );
                })}
              </div>
            </div>
          ))}
        </motion.section>

        {/* ═══ SIMULATEURS ═══ */}
        <motion.section {...fade(3)} id="simulateurs" style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#3D9E7C' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Simulateurs interactifs</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 24, lineHeight: 1.6 }}>
            7 outils manipulables en classe, sur tableau interactif ou en salle informatique. Chacun est accompagné d&apos;une suggestion d&apos;utilisation pédagogique.
          </p>

          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(300px, 1fr))', gap: 14 }}>
            {SIMULATEURS.map((sim, i) => (
              <motion.div key={sim.id} {...fade(i + 4)}>
                <Link href={`/lab?tool=${sim.id}`} style={{
                  display: 'block', background: 'var(--card)', border: '1px solid var(--border)',
                  borderRadius: 10, padding: '22px 20px', height: '100%',
                  transition: 'box-shadow 0.2s, border-color 0.2s',
                }}
                className="carousel-card"
                >
                  <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 12 }}>
                    <span style={{ fontSize: 22 }}>{sim.icon}</span>
                    <span style={{
                      fontSize: 10, fontWeight: 700, color: sim.color, letterSpacing: '0.08em',
                      padding: '3px 8px', border: `1px solid ${sim.color}30`, borderRadius: 4,
                      fontFamily: "'JetBrains Mono', monospace", textTransform: 'uppercase',
                    }}>
                      {sim.programme}
                    </span>
                  </div>
                  <div style={{ fontSize: 15, fontWeight: 750, color: 'var(--ink)', marginBottom: 6, lineHeight: 1.35 }}>
                    {sim.titre}
                  </div>
                  <p style={{ fontSize: 13, color: 'var(--ink-soft)', lineHeight: 1.55, marginBottom: 10 }}>
                    {sim.description}
                  </p>
                  <div style={{
                    fontSize: 12, color: 'var(--ink-muted)', lineHeight: 1.5,
                    padding: '8px 10px', background: 'var(--bg)', borderRadius: 6,
                    borderLeft: `3px solid ${sim.color}`,
                  }}>
                    <strong style={{ color: 'var(--ink-soft)' }}>En classe :</strong> {sim.usage}
                  </div>
                </Link>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ PROGRESSION SPIRALAIRE ═══ */}
        <motion.section {...fade(4)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#3B8FD4' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Progression spiralaire — le réflexe niveau par niveau</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 22, lineHeight: 1.6 }}>
            Le même réflexe — distinguer ce qu&apos;on mesure de ce qu&apos;on en déduit — se construit et s&apos;approfondit du CM1 à la terminale.
          </p>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 0 }}>
            {[
              ['Cycle 3 · CM1–6e', '#3B8FD4', 'Distinguer ce qu&apos;on voit de ce qu&apos;on en dit. Un modèle = une maquette, une image utile — pas la réalité elle-même.'],
              ['Cycle 4 · 5e–3e', '#8B7EC8', 'Nommer explicitement fait / modèle / hypothèse. Chercher et citer la source d&apos;une affirmation.'],
              ['2de', '#3D9E7C', 'Introduire l&apos;incertitude de mesure et les chiffres significatifs. Un modèle se juge à ses prédictions.'],
              ['1re · Enseignement scientifique', '#D4943A', 'Nature du savoir scientifique, histoire des sciences, rôle de la controverse et de la revue par les pairs.'],
              ['Terminale · Philosophie / Ens. scientifique', '#C45E6A', 'Réfutabilité (Popper), paradigmes (Kuhn), limites et révisions de la connaissance.'],
            ].map(([niveau, color, txt], i, arr) => (
              <div key={i} style={{ display: 'flex', gap: 16, alignItems: 'stretch' }}>
                <div style={{ display: 'flex', flexDirection: 'column', alignItems: 'center', width: 16 }}>
                  <div style={{ width: 13, height: 13, borderRadius: '50%', background: color as string, marginTop: 4, flexShrink: 0 }} />
                  {i < arr.length - 1 && <div style={{ width: 2, flex: 1, background: 'var(--border)', marginTop: 2 }} />}
                </div>
                <div style={{ paddingBottom: i < arr.length - 1 ? 22 : 0 }}>
                  <div style={{ fontSize: 13, fontWeight: 700, color: color as string, fontFamily: "'JetBrains Mono', monospace", marginBottom: 4 }}>{niveau}</div>
                  <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, margin: 0 }} dangerouslySetInnerHTML={{ __html: txt as string }} />
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ GRILLE D'ÉVALUATION ═══ */}
        <motion.section {...fade(4)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#D4943A' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Grille d&apos;évaluation de l&apos;esprit critique</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Une grille par niveaux, réutilisable pour toute activité — orale, écrite ou en débat.
          </p>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden', overflowX: 'auto' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr 1fr 1fr', borderBottom: '2px solid var(--border)', minWidth: 640 }}>
              {['Critère', 'À développer', 'En cours', 'Maîtrisé'].map((th, i) => (
                <div key={i} style={{ padding: '12px 14px', fontSize: 11, fontWeight: 700, color: i === 0 ? 'var(--ink)' : ['#C45E6A', '#D4943A', '#3D9E7C'][i - 1], letterSpacing: '0.05em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace", borderLeft: i > 0 ? '1px solid var(--border)' : 'none' }}>{th}</div>
              ))}
            </div>
            {[
              ['Observation vs interprétation', 'Confond ce qui est vu et ce qui est déduit.', 'Distingue les deux avec de l&apos;aide.', 'Distingue spontanément et justifie.'],
              ['Statut d&apos;un énoncé', 'Confond fait, modèle et hypothèse.', 'Classe la plupart des énoncés.', 'Classe et justifie le statut.'],
              ['Recours à une source', 'Affirme sans source.', 'Cite une source.', 'Évalue la fiabilité de la source.'],
              ['Alternative testable', 'N&apos;envisage aucune alternative.', 'Propose une alternative.', 'Propose une alternative réfutable.'],
              ['Prise en compte de l&apos;incertitude', 'Ignore la marge d&apos;erreur.', 'Mentionne l&apos;incertitude.', 'Interprète barres d&apos;erreur et écarts.'],
            ].map((row, i, arr) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1.3fr 1fr 1fr 1fr', borderBottom: i < arr.length - 1 ? '1px solid var(--border)' : 'none', minWidth: 640 }}>
                {row.map((cell, j) => (
                  <div key={j} style={{ padding: '13px 14px', fontSize: 13, lineHeight: 1.5, color: j === 0 ? 'var(--ink)' : 'var(--ink-soft)', fontWeight: j === 0 ? 700 : 400, borderLeft: j > 0 ? '1px solid var(--border)' : 'none' }} dangerouslySetInnerHTML={{ __html: cell }} />
                ))}
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ AVANT / APRÈS ═══ */}
        <motion.section {...fade(4)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#D4943A' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Reformuler avec rigueur</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Même contenu. Même programme. Vocabulaire plus juste.
          </p>

          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '2px solid var(--border)' }}>
              <div style={{ padding: '12px 18px', fontSize: 11, fontWeight: 700, color: '#C45E6A', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace" }}>
                ✗ Formulation courante
              </div>
              <div style={{ padding: '12px 18px', fontSize: 11, fontWeight: 700, color: '#3D9E7C', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace", borderLeft: '1px solid var(--border)' }}>
                ✓ Formulation rigoureuse
              </div>
            </div>
            {[
              ['La gravité attire les objets.', 'Les objets tombent. Le modèle gravitationnel décrit ce comportement — le mécanisme exact reste étudié.'],
              ['La Terre tourne autour du Soleil.', 'Dans le modèle héliocentrique, la Terre tourne autour du Soleil. Ce modèle permet des prédictions précises.'],
              ['L\'Univers a 13,8 milliards d\'années.', 'Selon le modèle du Big Bang, l\'Univers aurait 13,8 milliards d\'années. Certaines observations récentes questionnent ce chiffre.'],
              ['Ératosthène a prouvé que la Terre est ronde.', 'Ératosthène a mesuré un angle et estimé une circonférence — dans le cadre d\'un modèle sphérique avec Soleil lointain.'],
              ['L\'homme descend du singe.', 'La théorie de l\'évolution propose que les humains et les grands singes partagent un ancêtre commun.'],
              ['Rien ne va plus vite que la lumière.', 'Selon la relativité d\'Einstein, rien ne dépasse la vitesse de la lumière. C\'est un postulat du modèle, confirmé expérimentalement.'],
            ].map(([avant, apres], i) => (
              <div key={i} style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', borderBottom: '1px solid var(--border)' }}>
                <div style={{ padding: '14px 18px', fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.55 }}>
                  {avant}
                </div>
                <div style={{ padding: '14px 18px', fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.55, borderLeft: '1px solid var(--border)' }}>
                  {apres}
                </div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ GLOSSAIRE ═══ */}
        <motion.section {...fade(5)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#8B7EC8' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Glossaire pour la classe</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 20, lineHeight: 1.6 }}>
            Les huit mots à distinguer pour parler juste. Projetables au tableau.
          </p>
          <div style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, overflow: 'hidden' }}>
            {[
              ['Fait', 'Ce qu&apos;on observe ou mesure directement.', 'Un objet lâché tombe. L&apos;eau bout.'],
              ['Loi', 'Une régularité mesurée, souvent une formule. Décrit, n&apos;explique pas.', 'Loi de Kepler : a³/T² est constant.'],
              ['Modèle', 'Une représentation qui explique et prédit. Pas la réalité elle-même.', 'Le modèle héliocentrique.'],
              ['Hypothèse', 'Une explication proposée, encore à tester.', 'La « matière noire ».'],
              ['Théorie', 'Un ensemble cohérent et éprouvé d&apos;explications — pas une « simple supposition ».', 'La théorie de l&apos;évolution.'],
              ['Paradigme', 'Le cadre de pensée dominant d&apos;une époque (Kuhn).', 'Géocentrisme, puis héliocentrisme.'],
              ['Réfutabilité', 'Une affirmation est scientifique si une expérience pourrait la contredire (Popper).', '« Tous les corbeaux sont noirs » est réfutable.'],
              ['Incertitude', 'Toute mesure a une marge d&apos;erreur ; un résultat sans incertitude est incomplet.', 'g = 9,81 ± 0,01 m/s².'],
            ].map(([terme, def, ex], i) => (
              <div key={i} style={{
                display: 'grid', gridTemplateColumns: '140px 1fr 1fr',
                borderBottom: i < 7 ? '1px solid var(--border)' : 'none', alignItems: 'start',
              }} className="gloss-row">
                <div style={{ padding: '13px 18px', fontSize: 14, fontWeight: 750, color: '#8B7EC8' }}>{terme}</div>
                <div style={{ padding: '13px 16px', fontSize: 13.5, color: 'var(--ink-soft)', lineHeight: 1.55, borderLeft: '1px solid var(--border)' }} dangerouslySetInnerHTML={{ __html: def as string }} />
                <div style={{ padding: '13px 16px', fontSize: 13, color: 'var(--ink-muted)', lineHeight: 1.55, borderLeft: '1px solid var(--border)', fontStyle: 'italic' }} dangerouslySetInnerHTML={{ __html: ex as string }} />
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ MESURE & INCERTITUDE ═══ */}
        <motion.section {...fade(5)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#3D9E7C' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Mesure &amp; incertitude</h2>
          </div>
          <p style={{ fontSize: 14, color: 'var(--ink-muted)', marginBottom: 22, lineHeight: 1.6 }}>
            Un chiffre seul ne dit rien. Toute mesure porte une marge d&apos;erreur — l&apos;ignorer, c&apos;est confondre <strong style={{ color: 'var(--ink-soft)' }}>précision</strong> et <strong style={{ color: 'var(--ink-soft)' }}>vérité</strong>. C&apos;est ici que se joue la frontière entre un fait et son interprétation.
          </p>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(260px, 1fr))', gap: 14, marginBottom: 20 }}>
            {[
              ['Chiffres significatifs', 'N&apos;afficher que la précision réellement mesurée.', 'Une règle au cm donne 3,14 m — pas 3,14159 m.'],
              ['La barre d&apos;erreur (±)', 'Une valeur sans sa marge est incomplète.', 'g = 9,81 ± 0,01 m/s².'],
              ['Moyenne &amp; écart-type', 'Plusieurs mesures se dispersent ; l&apos;écart-type mesure cette dispersion.', '4 horloges donnant 30, 55, 78, 73 ns : la moyenne cache une forte dispersion.'],
              ['Le seuil de 5σ', 'En physique, on parle de « découverte » quand la probabilité que ce soit le hasard est inférieure à 1 sur 3,5 millions.', 'C&apos;est le critère annoncé pour le boson de Higgs et pour GW150914.'],
            ].map(([titre, def, ex], i) => (
              <div key={i} style={{ background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10, padding: '18px 18px' }}>
                <div style={{ fontSize: 14.5, fontWeight: 750, color: '#3D9E7C', marginBottom: 8 }} dangerouslySetInnerHTML={{ __html: titre as string }} />
                <p style={{ fontSize: 13.5, color: 'var(--ink-soft)', lineHeight: 1.55, marginBottom: 8 }} dangerouslySetInnerHTML={{ __html: def as string }} />
                <p style={{ fontSize: 12.5, color: 'var(--ink-muted)', lineHeight: 1.5, margin: 0, fontStyle: 'italic' }} dangerouslySetInnerHTML={{ __html: ex as string }} />
              </div>
            ))}
          </div>
          <div style={{ background: 'var(--bg)', border: '1px solid var(--border)', borderRadius: 10, padding: '20px 22px' }}>
            <div style={{ fontSize: 11, fontWeight: 700, color: '#3B8FD4', letterSpacing: '0.06em', textTransform: 'uppercase', marginBottom: 12, fontFamily: "'JetBrains Mono', monospace" }}>🧪 En classe — deux mesures qui se contredisent</div>
            <div style={{ display: 'flex', gap: 20, flexWrap: 'wrap', alignItems: 'center' }}>
              <svg viewBox="0 0 420 130" style={{ width: 320, maxWidth: '100%' }} role="img" aria-label="Deux mesures avec barres d'erreur qui ne se recouvrent pas">
                <line x1="30" y1="105" x2="400" y2="105" stroke="var(--ink-muted)" strokeWidth="1" />
                <text x="215" y="122" textAnchor="middle" fill="var(--ink-muted)" fontSize="10" fontFamily="monospace">valeur mesurée →</text>
                <line x1="90" y1="45" x2="150" y2="45" stroke="#3D9E7C" strokeWidth="2.5" />
                <line x1="90" y1="38" x2="90" y2="52" stroke="#3D9E7C" strokeWidth="2.5" />
                <line x1="150" y1="38" x2="150" y2="52" stroke="#3D9E7C" strokeWidth="2.5" />
                <circle cx="120" cy="45" r="4" fill="#3D9E7C" />
                <text x="120" y="30" textAnchor="middle" fill="#3D9E7C" fontSize="11" fontWeight="700" fontFamily="monospace">mesure A</text>
                <line x1="250" y1="75" x2="330" y2="75" stroke="#C45E6A" strokeWidth="2.5" />
                <line x1="250" y1="68" x2="250" y2="82" stroke="#C45E6A" strokeWidth="2.5" />
                <line x1="330" y1="68" x2="330" y2="82" stroke="#C45E6A" strokeWidth="2.5" />
                <circle cx="290" cy="75" r="4" fill="#C45E6A" />
                <text x="290" y="98" textAnchor="middle" fill="#C45E6A" fontSize="11" fontWeight="700" fontFamily="monospace">mesure B</text>
                <line x1="150" y1="45" x2="250" y2="75" stroke="var(--border)" strokeWidth="1" strokeDasharray="3,3" />
              </svg>
              <p style={{ flex: 1, minWidth: 220, fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.65, margin: 0 }}>
                Quand les barres d&apos;erreur de deux mesures <strong style={{ color: 'var(--ink)' }}>ne se recouvrent pas</strong>, le désaccord est <strong style={{ color: 'var(--ink)' }}>réel</strong> : il reste quelque chose à comprendre. C&apos;est exactement le cas des mesures de la constante gravitationnelle <em>G</em>, en désaccord au-delà de leurs incertitudes déclarées.{' '}
                <Link href="/article/la-gravite-70-theories-et-aucune-preuve" style={{ color: '#3D9E7C', fontWeight: 600 }}>Voir l&apos;article →</Link>
              </p>
            </div>
          </div>
        </motion.section>

        {/* ═══ FAQ ═══ */}
        <motion.section {...fade(5)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: '#C45E6A' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Questions fréquentes</h2>
          </div>
          <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
            {FAQ.map((f, i) => (
              <motion.div key={i} {...fade(i + 6)} style={{
                background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
                padding: '22px 24px',
              }}>
                <div style={{ fontSize: 15, fontWeight: 750, color: 'var(--ink)', marginBottom: 8 }}>{f.q}</div>
                <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.65, margin: 0 }}>{f.a}</p>
              </motion.div>
            ))}
          </div>
        </motion.section>

        {/* ═══ RÉFÉRENCES ═══ */}
        <motion.section {...fade(6)} style={{ marginTop: 48 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10, marginBottom: 20 }}>
            <div style={{ width: 4, height: 28, borderRadius: 2, background: 'var(--ink-ghost)' }} />
            <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>Références</h2>
          </div>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(280px, 1fr))', gap: 10 }}>
            {REFERENCES.map((r, i) => (
              <div key={i} style={{
                padding: '14px 18px', background: 'var(--bg)', borderRadius: 8,
                borderLeft: '3px solid var(--border)',
              }}>
                <div style={{ fontSize: 14, fontWeight: 700, color: 'var(--ink)', marginBottom: 2 }}>{r.auteur}</div>
                <div style={{ fontSize: 13, color: 'var(--ink-soft)', fontStyle: 'italic' }}>{r.titre} ({r.annee})</div>
                <div style={{ fontSize: 11, color: 'var(--ink-muted)', marginTop: 4 }}>{r.note}</div>
              </div>
            ))}
          </div>
        </motion.section>

        {/* ═══ CTA FINAL ═══ */}
        <motion.section {...fade(7)} style={{ marginTop: 56 }}>
          <div style={{
            padding: '36px 28px', background: 'linear-gradient(135deg, #0D2818, #1A3A2A)',
            borderRadius: 12, textAlign: 'center',
          }}>
            <p style={{ fontSize: 20, fontWeight: 700, color: '#E8EDF4', marginBottom: 8 }}>
              La science n&apos;est pas un dogme. C&apos;est une méthode.
            </p>
            <p style={{ fontSize: 15, color: '#8A95A8', marginBottom: 24, lineHeight: 1.6 }}>
              Enseignons la méthode.
            </p>
            <div style={{ display: 'flex', gap: 14, justifyContent: 'center', flexWrap: 'wrap' }}>
              <a
                href="/livret-enseignant.pdf"
                download
                style={{
                  padding: '12px 24px', borderRadius: 8,
                  background: ACCENT, color: '#fff',
                  fontSize: 14, fontWeight: 700, textDecoration: 'none',
                }}
              >
                📄 Télécharger le livret
              </a>
              <Link
                href="/lab"
                style={{
                  padding: '12px 24px', borderRadius: 8,
                  background: 'rgba(255,255,255,0.1)', color: '#C8D8E8',
                  border: '1px solid rgba(255,255,255,0.15)',
                  fontSize: 14, fontWeight: 700, textDecoration: 'none',
                }}
              >
                🖥️ Explorer les simulateurs
              </Link>
            </div>
          </div>
        </motion.section>

      </div>
    </div>
  );
}
