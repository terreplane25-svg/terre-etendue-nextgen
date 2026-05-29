"use client";

import { motion } from "framer-motion";

interface Props {
  manifeste: string;
  methodologie: string;
  ethique: string;
  etatDesLieux: string;
}

export default function AboutClient({ manifeste, methodologie, ethique, etatDesLieux }: Props) {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="max-w-[720px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-[var(--gold)] shadow-[0_0_8px_var(--gold-20)]" />
            <span className="text-[9px] tracking-[0.2em] text-[var(--gold-50)] uppercase font-orbitron">
              À propos
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[var(--text)] mb-10 font-orbitron">
            TERRE ÉTENDUE ISLAM
          </h1>
        </motion.div>

        {/* Manifeste */}
        <section className="mb-16">
          <h2 className="text-lg font-semibold text-[var(--gold)] mb-6 flex items-center gap-3 font-orbitron" style={{fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[var(--gold)]/30" />
            MANIFESTE
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: manifeste }} />
        </section>

        <div className="hud-divider mb-16" />

        {/* Méthodologie */}
        <section className="mb-16">
          <h2 className="text-lg font-semibold text-[var(--cyan)] mb-6 flex items-center gap-3 font-orbitron" style={{fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[var(--cyan-20)]" />
            MÉTHODOLOGIE
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: methodologie }} />
        </section>

        <div className="hud-divider mb-16" />

        {/* État des lieux */}
        <section className="mb-16">
          <h2 className="text-lg font-semibold text-[var(--cyan)] mb-6 flex items-center gap-3 font-orbitron" style={{fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[var(--cyan-20)]" />
            ÉTAT DES LIEUX
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: etatDesLieux }} />
        </section>

        <div className="hud-divider mb-16" />

        {/* Éthique */}
        <section>
          <h2 className="text-lg font-semibold text-[var(--green)] mb-6 flex items-center gap-3 font-orbitron" style={{fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[var(--green)]/30" />
            ÉTHIQUE INTELLECTUELLE
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: ethique }} />
        </section>
      </div>
    </div>
  );
}
