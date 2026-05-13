"use client";

import { motion } from "framer-motion";

interface Props {
  manifeste: string;
  methodologie: string;
  ethique: string;
}

export default function AboutClient({ manifeste, methodologie, ethique }: Props) {
  return (
    <div className="min-h-screen pt-20 pb-16">
      <div className="max-w-[720px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px] bg-[#D4A843] shadow-[0_0_8px_rgba(212,168,67,0.4)]" />
            <span className="text-[9px] tracking-[0.2em] text-[#D4A843]/50 uppercase" style={{fontFamily: 'Orbitron, sans-serif'}}>
              À propos
            </span>
          </div>
          <h1 className="text-2xl md:text-3xl font-bold text-[#C8D8E8] mb-10" style={{fontFamily: 'Orbitron, sans-serif'}}>
            TERRE ÉTENDUE ISLAM
          </h1>
        </motion.div>

        {/* Manifeste */}
        <section className="mb-16">
          <h2 className="text-lg font-semibold text-[#D4A843] mb-6 flex items-center gap-3" style={{fontFamily: 'Orbitron, sans-serif', fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[#D4A843]/30" />
            MANIFESTE
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: manifeste }} />
        </section>

        <div className="hud-divider mb-16" />

        {/* Méthodologie */}
        <section className="mb-16">
          <h2 className="text-lg font-semibold text-[#00C8FF] mb-6 flex items-center gap-3" style={{fontFamily: 'Orbitron, sans-serif', fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[#00C8FF]/30" />
            MÉTHODOLOGIE
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: methodologie }} />
        </section>

        <div className="hud-divider mb-16" />

        {/* Éthique */}
        <section>
          <h2 className="text-lg font-semibold text-[#00E87B] mb-6 flex items-center gap-3" style={{fontFamily: 'Orbitron, sans-serif', fontSize: '14px', letterSpacing: '0.1em'}}>
            <span className="w-6 h-[1px] bg-[#00E87B]/30" />
            ÉTHIQUE INTELLECTUELLE
          </h2>
          <div className="prose-tei" dangerouslySetInnerHTML={{ __html: ethique }} />
        </section>
      </div>
    </div>
  );
}
