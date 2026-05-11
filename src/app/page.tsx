'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';
import PillarCard from '@/components/PillarCard';

const PILLARS = [
  {
    title: 'Le Q.G.',
    subtitle: 'Épistémologie',
    description: 'Fondations conceptuelles réconciliant la méthode scientifique et les principes spirituels islamiques.',
    href: '/headquarters',
    icon: '🧠',
    accent: 'cyan' as const,
    stats: [
      { label: 'Articles', value: '24' },
      { label: 'Concepts', value: '156' },
    ],
  },
  {
    title: "L'Observatoire",
    subtitle: 'Empirique',
    description: "Données mesurables et observations du terrain. Les faits qui ancrent la théorie dans le réel.",
    href: '/observatory',
    icon: '🔭',
    accent: 'cyan' as const,
    stats: [
      { label: 'Études', value: '42' },
      { label: 'Données', value: '1.2K' },
    ],
  },
  {
    title: 'La Bibliothèque',
    subtitle: 'Sources Sacrées',
    description: 'Coran, Hadith et écrits spirituels : la base textuelle de notre analyse géométrique.',
    href: '/library',
    icon: '📚',
    accent: 'gold' as const,
    stats: [
      { label: 'Textes', value: '87' },
      { label: 'Références', value: '3.5K' },
    ],
  },
  {
    title: 'Le Lab',
    subtitle: 'Modélisation',
    description: 'Simulations 3D interactives et modèles géométriques. Visualisez les concepts, manipulez les paramètres.',
    href: '/lab',
    icon: '⚗️',
    accent: 'gold' as const,
    stats: [
      { label: 'Modèles', value: '18' },
      { label: 'Simulations', value: '67' },
    ],
  },
];

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.12 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 20 },
  show: { opacity: 1, y: 0, transition: { duration: 0.6, ease: [0.16, 1, 0.3, 1] } },
};

export default function HomePage() {
  return (
    <div className="min-h-screen pt-20 pb-24">
      {/* ═══ Hero ═══ */}
      <section className="max-w-7xl mx-auto px-6 pt-16 pb-24">
        <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-8">
          <motion.p variants={fadeUp} className="font-display text-sm font-semibold uppercase tracking-[0.2em] text-obs-cyan">
            Plateforme Académique
          </motion.p>

          <motion.h1 variants={fadeUp} className="text-display-lg leading-[1.05]">
            <span className="text-obs-cyan">Terre Étendue</span>
            <br />
            <span className="text-obs-gold">Islam</span>
          </motion.h1>

          <motion.p variants={fadeUp} className="text-xl text-obs-text-secondary max-w-2xl font-serif leading-relaxed">
            Réconcilier l'épistémologie, les observations empiriques, les sources sacrées islamiques
            et la modélisation géométrique — dans une interface de recherche moderne.
          </motion.p>

          <motion.div variants={fadeUp} className="flex flex-wrap gap-4 pt-2">
            <Link
              href="/nexus"
              className="px-7 py-3 rounded-lg bg-obs-cyan text-obs-dark font-semibold text-sm hover:brightness-110 transition-all"
            >
              Explorer le Nexus
            </Link>
            <Link
              href="/library"
              className="px-7 py-3 rounded-lg border border-obs-gold/40 text-obs-gold font-semibold text-sm hover:bg-obs-gold/10 transition-colors"
            >
              Parcourir la Bibliothèque
            </Link>
          </motion.div>
        </motion.div>
      </section>

      {/* ═══ Piliers ═══ */}
      <section className="max-w-7xl mx-auto px-6 space-y-10">
        <motion.h2
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="text-heading-lg font-display font-bold"
        >
          Les Quatre Piliers
        </motion.h2>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          {PILLARS.map((pillar, i) => (
            <motion.div
              key={pillar.href}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.1, duration: 0.5, ease: [0.16, 1, 0.3, 1] }}
              viewport={{ once: true, margin: '-80px' }}
            >
              <PillarCard {...pillar} />
            </motion.div>
          ))}
        </div>
      </section>

      {/* ═══ Nexus CTA ═══ */}
      <section className="max-w-7xl mx-auto px-6 pt-24">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="card-surface rounded-xl p-10 text-center space-y-6"
        >
          <span className="text-4xl">🔗</span>
          <h2 className="text-heading-lg font-display font-bold">Nexus Graph</h2>
          <p className="text-obs-text-secondary max-w-xl mx-auto leading-relaxed">
            Visualisez les connexions entre physique, théologie et géométrie.
            Chaque article est un nœud, chaque lien conceptuel est une arête.
          </p>
          <Link
            href="/nexus"
            className="inline-block px-7 py-3 rounded-lg bg-obs-cyan text-obs-dark font-semibold text-sm hover:brightness-110 transition-all"
          >
            Ouvrir le Nexus →
          </Link>
        </motion.div>
      </section>
    </div>
  );
}
