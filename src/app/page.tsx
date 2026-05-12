'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

const PILLARS = [
  {
    marker: '01',
    title: 'Le Q.G.',
    subtitle: 'Épistémologie',
    description: 'Fondations conceptuelles. Comment articuler méthode scientifique et principes révélés sans confondre les registres.',
    href: '/headquarters',
    color: 'cyan',
  },
  {
    marker: '02',
    title: "L'Observatoire",
    subtitle: 'Empirique',
    description: "Données mesurables et observations du terrain. Ce que l'on peut voir, mesurer, reproduire.",
    href: '/observatory',
    color: 'cyan',
  },
  {
    marker: '03',
    title: 'La Bibliothèque',
    subtitle: 'Sources Sacrées',
    description: 'Coran, hadiths, exégèses classiques. Le socle textuel, contextualisé et connecté aux modèles.',
    href: '/library',
    color: 'gold',
  },
  {
    marker: '04',
    title: 'Le Lab',
    subtitle: 'Modélisation',
    description: 'Simulations 3D, modèles géométriques, visualisations interactives. Les concepts deviennent tangibles.',
    href: '/lab',
    color: 'cyan',
  },
];

const stagger = {
  hidden: {},
  show: { transition: { staggerChildren: 0.08 } },
};

const fadeUp = {
  hidden: { opacity: 0, y: 30 },
  show: { opacity: 1, y: 0, transition: { duration: 0.8, ease: [0.16, 1, 0.3, 1] } },
};

const fadeIn = {
  hidden: { opacity: 0 },
  show: { opacity: 1, transition: { duration: 1.2, ease: 'easeOut' } },
};

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* ═══ Hero ═══ */}
      <section className="relative min-h-[85vh] flex items-center overflow-hidden">
        {/* Geometric background lines */}
        <div className="absolute inset-0 pointer-events-none overflow-hidden">
          <svg className="absolute top-0 right-0 w-[600px] h-[600px] opacity-[0.03]" viewBox="0 0 600 600">
            <circle cx="300" cy="300" r="280" fill="none" stroke="#C9A84C" strokeWidth="0.5" />
            <circle cx="300" cy="300" r="200" fill="none" stroke="#C9A84C" strokeWidth="0.5" />
            <circle cx="300" cy="300" r="120" fill="none" stroke="#00B4E6" strokeWidth="0.5" />
            <circle cx="300" cy="300" r="40" fill="none" stroke="#00B4E6" strokeWidth="0.5" />
            <line x1="0" y1="300" x2="600" y2="300" stroke="#C9A84C" strokeWidth="0.3" />
            <line x1="300" y1="0" x2="300" y2="600" stroke="#C9A84C" strokeWidth="0.3" />
          </svg>
        </div>

        <div className="max-w-7xl mx-auto px-6 pt-32 pb-20 relative z-10">
          <motion.div variants={stagger} initial="hidden" animate="show" className="space-y-10">
            <motion.div variants={fadeIn} className="flex items-center gap-4">
              <div className="h-px w-12 bg-accent-gold/40" />
              <span className="font-mono text-label uppercase text-accent-gold/60">
                Plateforme de Recherche Académique
              </span>
            </motion.div>

            <motion.h1 variants={fadeUp} className="text-hero font-display font-bold">
              <span className="text-[#E8E4DD]">Terre</span>{' '}
              <span className="text-accent-cyan">Étendue</span>
              <br />
              <span className="text-accent-gold">Islam</span>
            </motion.h1>

            <motion.p variants={fadeUp} className="text-lg md:text-xl text-[#E8E4DD]/45 max-w-2xl font-body leading-[1.8]">
              Réconcilier l'épistémologie, les observations empiriques, les sources sacrées
              islamiques et la modélisation géométrique — dans une interface
              de recherche moderne.
            </motion.p>

            <motion.div variants={fadeUp} className="flex flex-wrap gap-4 pt-4">
              <Link
                href="/nexus"
                className="group relative px-8 py-3.5 rounded-lg bg-accent-cyan/10 border border-accent-cyan/20 text-accent-cyan font-heading text-sm tracking-wide hover:bg-accent-cyan/15 hover:border-accent-cyan/30 transition-all duration-300"
              >
                Explorer le Nexus
                <span className="ml-2 inline-block transition-transform group-hover:translate-x-1">→</span>
              </Link>
              <Link
                href="/library"
                className="group px-8 py-3.5 rounded-lg border border-accent-gold/15 text-accent-gold/70 font-heading text-sm tracking-wide hover:border-accent-gold/30 hover:text-accent-gold transition-all duration-300"
              >
                Parcourir la Bibliothèque
              </Link>
            </motion.div>
          </motion.div>
        </div>
      </section>

      {/* ═══ Divider ═══ */}
      <div className="max-w-7xl mx-auto px-6">
        <div className="geo-line-gold" />
      </div>

      {/* ═══ Piliers ═══ */}
      <section className="max-w-7xl mx-auto px-6 py-24">
        <motion.div
          initial={{ opacity: 0 }}
          whileInView={{ opacity: 1 }}
          viewport={{ once: true }}
          className="flex items-center gap-4 mb-16"
        >
          <span className="font-mono text-label uppercase text-[#E8E4DD]/25">Architecture</span>
          <div className="h-px flex-1 bg-white/[0.04]" />
        </motion.div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-5">
          {PILLARS.map((pillar, i) => (
            <motion.div
              key={pillar.href}
              initial={{ opacity: 0, y: 24 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.08, duration: 0.6, ease: [0.16, 1, 0.3, 1] }}
              viewport={{ once: true, margin: '-60px' }}
            >
              <Link href={pillar.href} className="block group">
                <div className="card card-hover p-7 space-y-4 h-full">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <span className={`font-mono text-[0.6rem] font-bold ${
                        pillar.color === 'gold' ? 'text-accent-gold/40' : 'text-accent-cyan/40'
                      }`}>
                        {pillar.marker}
                      </span>
                      <h3 className="font-display text-xl font-bold text-[#E8E4DD] group-hover:text-accent-cyan transition-colors duration-300">
                        {pillar.title}
                      </h3>
                    </div>
                    <span className={`font-mono text-label uppercase ${
                      pillar.color === 'gold' ? 'text-accent-gold/30' : 'text-accent-cyan/30'
                    }`}>
                      {pillar.subtitle}
                    </span>
                  </div>
                  <p className="text-[#E8E4DD]/35 text-sm font-body leading-relaxed">
                    {pillar.description}
                  </p>
                  <div className={`h-px w-0 group-hover:w-full transition-all duration-500 ${
                    pillar.color === 'gold'
                      ? 'bg-gradient-to-r from-accent-gold/30 to-transparent'
                      : 'bg-gradient-to-r from-accent-cyan/30 to-transparent'
                  }`} />
                </div>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* ═══ Nexus CTA ═══ */}
      <section className="max-w-7xl mx-auto px-6 pb-24">
        <motion.div
          initial={{ opacity: 0, y: 24 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="card p-12 text-center space-y-6 relative overflow-hidden"
        >
          {/* Decorative circles */}
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[300px] h-[300px] rounded-full border border-accent-cyan/[0.04] pointer-events-none" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] rounded-full border border-accent-gold/[0.04] pointer-events-none" />
          
          <div className="relative z-10">
            <span className="font-mono text-label uppercase text-accent-cyan/40 block mb-4">Graphe de connaissances</span>
            <h2 className="text-title-lg font-display font-bold text-[#E8E4DD]">Nexus</h2>
            <p className="text-[#E8E4DD]/35 max-w-lg mx-auto leading-relaxed font-body mt-4">
              Chaque article est un nœud. Chaque connexion conceptuelle est visible.
              Voyez comment la physique rejoint une sourate.
            </p>
            <Link
              href="/nexus"
              className="inline-block mt-8 px-8 py-3.5 rounded-lg bg-accent-cyan/10 border border-accent-cyan/20 text-accent-cyan font-heading text-sm tracking-wide hover:bg-accent-cyan/15 transition-all"
            >
              Ouvrir le Nexus →
            </Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
