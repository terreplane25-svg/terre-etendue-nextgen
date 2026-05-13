'use client';

import { motion } from 'framer-motion';
import Link from 'next/link';

const PILLARS = [
  { num: '01', title: 'Le Q.G.', tag: 'Épistémologie', tagColor: 'cyan', desc: 'Fondations conceptuelles. Méthode scientifique et principes révélés.', href: '/headquarters' },
  { num: '02', title: "L'Observatoire", tag: 'Empirique', tagColor: 'cyan', desc: 'Données mesurables. Ce que l\'on peut voir, mesurer, reproduire.', href: '/observatory' },
  { num: '03', title: 'La Bibliothèque', tag: 'Sources sacrées', tagColor: 'gold', desc: 'Coran, hadiths, exégèses classiques. Le socle textuel.', href: '/library' },
  { num: '04', title: 'Le Lab', tag: 'Modélisation', tagColor: 'cyan', desc: 'Simulations 3D, modèles géométriques, visualisations.', href: '/lab' },
];

const fadeUp = {
  hidden: { opacity: 0, y: 24 },
  show: { opacity: 1, y: 0, transition: { duration: 0.7, ease: [0.16, 1, 0.3, 1] } },
};

const stagger = { hidden: {}, show: { transition: { staggerChildren: 0.08 } } };

export default function HomePage() {
  return (
    <div className="min-h-screen">
      {/* Scanline - homepage only */}
      <div className="fixed top-0 left-0 right-0 h-[2px] z-[60] pointer-events-none animate-[scan_4s_linear_infinite]" style={{
        background: 'linear-gradient(90deg, transparent, rgba(0,200,255,0.2), transparent)'
      }} />
      {/* Hero */}
      <section className="relative max-w-[960px] mx-auto px-6 pt-28 pb-16">
        {/* Corner marks */}
        <div className="absolute top-20 left-4 right-4 bottom-8 pointer-events-none">
          <div className="absolute top-0 left-0 w-5 h-5 border-t border-l border-[rgba(0,200,255,0.15)]" />
          <div className="absolute bottom-0 right-0 w-5 h-5 border-b border-r border-[rgba(0,200,255,0.15)]" />
        </div>

        <motion.div variants={stagger} initial="hidden" animate="show" className="relative z-10">
          <motion.div variants={fadeUp} className="flex items-center gap-3 mb-6">
            <div className="w-8 h-[2px] bg-[#00C8FF] shadow-[0_0_10px_rgba(0,200,255,0.5)]" />
            <span className="text-[9px] tracking-[0.25em] text-[#00C8FF] uppercase" style={{fontFamily: 'Orbitron, sans-serif'}}>
              Plateforme de recherche académique
            </span>
          </motion.div>

          <motion.h1 variants={fadeUp} className="text-[clamp(2.5rem,7vw,3.5rem)] font-bold leading-[1.1] tracking-tight mb-6" style={{fontFamily: 'Orbitron, sans-serif'}}>
            <span className="text-[#C8D8E8]">TERRE </span>
            <span className="text-[#00C8FF]" style={{textShadow: '0 0 30px rgba(0,200,255,0.2)'}}>ÉTENDUE</span>
            <br />
            <span className="text-[#D4A843]" style={{textShadow: '0 0 30px rgba(212,168,67,0.2)'}}>ISLAM</span>
          </motion.h1>

          <motion.p variants={fadeUp} className="text-base text-[#C8D8E8]/45 max-w-lg leading-[1.8] mb-8" style={{fontFamily: 'Rajdhani, sans-serif'}}>
            Réconcilier l&apos;épistémologie, les observations empiriques, les sources sacrées
            islamiques et la modélisation géométrique.
          </motion.p>

          <motion.div variants={fadeUp} className="flex flex-wrap gap-3">
            <Link href="/nexus" className="hud-btn">EXPLORER LE NEXUS →</Link>
            <Link href="/library" className="hud-btn hud-btn-gold">BIBLIOTHÈQUE</Link>
          </motion.div>
        </motion.div>
      </section>

      {/* Divider */}
      <div className="max-w-[960px] mx-auto px-6"><div className="hud-divider" /></div>

      {/* Pillars */}
      <section className="max-w-[960px] mx-auto px-6 py-12">
        <div className="hud-section-label mb-8"><span>Architecture du système</span></div>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
          {PILLARS.map((p, i) => (
            <motion.div
              key={p.href}
              initial={{ opacity: 0, y: 16 }}
              whileInView={{ opacity: 1, y: 0 }}
              transition={{ delay: i * 0.06, duration: 0.5 }}
              viewport={{ once: true }}
            >
              <Link href={p.href} className={`block hud-card ${p.tagColor === 'gold' ? 'hud-card-gold' : ''} p-6`}>
                <div className="flex items-center justify-between mb-2">
                  <div className="flex items-center gap-2">
                    <span className="text-[9px] text-[#C8D8E8]/20" style={{fontFamily: 'Share Tech Mono, monospace'}}>{p.num}</span>
                    <h3 className="text-sm font-semibold" style={{fontFamily: 'Orbitron, sans-serif'}}>{p.title}</h3>
                  </div>
                  <span className={`hud-label ${p.tagColor === 'gold' ? 'text-[#D4A843]/40' : 'text-[#00C8FF]/30'}`}>{p.tag}</span>
                </div>
                <p className="text-[13px] text-[#C8D8E8]/25 leading-relaxed" style={{fontFamily: 'Rajdhani, sans-serif'}}>{p.desc}</p>
              </Link>
            </motion.div>
          ))}
        </div>
      </section>

      {/* Nexus CTA */}
      <section className="max-w-[960px] mx-auto px-6 pb-16">
        <motion.div
          initial={{ opacity: 0, y: 16 }}
          whileInView={{ opacity: 1, y: 0 }}
          viewport={{ once: true }}
          className="hud-panel p-10 text-center relative overflow-hidden"
        >
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[200px] h-[200px] rounded-full border border-[rgba(0,200,255,0.04)] pointer-events-none" />
          <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[140px] h-[140px] rounded-full border border-[rgba(212,168,67,0.04)] pointer-events-none" />
          <div className="relative z-10">
            <p className="hud-label text-[#00C8FF]/30 mb-4">Graphe de connaissances</p>
            <h2 className="text-2xl font-bold text-[#C8D8E8] mb-3" style={{fontFamily: 'Orbitron, sans-serif'}}>NEXUS</h2>
            <p className="text-sm text-[#C8D8E8]/25 max-w-md mx-auto mb-6" style={{fontFamily: 'Rajdhani, sans-serif'}}>
              Chaque article est un nœud. Chaque connexion conceptuelle est visible.
            </p>
            <Link href="/nexus" className="hud-btn inline-block">OUVRIR LE NEXUS →</Link>
          </div>
        </motion.div>
      </section>
    </div>
  );
}
