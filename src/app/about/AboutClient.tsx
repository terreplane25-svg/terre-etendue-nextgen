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
    <div className="min-h-screen pt-20 pb-16" style={{ background: '#FAFAF6', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
      <div className="max-w-[720px] mx-auto px-6">
        <motion.div initial={{ opacity: 0, y: -16 }} animate={{ opacity: 1, y: 0 }}>
          <div className="flex items-center gap-3 mb-4">
            <div className="w-8 h-[2px]" style={{ background: '#C48A2E' }} />
            <span
              className="text-[9px] tracking-[0.2em] uppercase"
              style={{ color: '#8A857D', fontWeight: 600, letterSpacing: '0.2em' }}
            >
              À propos
            </span>
          </div>
          <h1
            className="text-2xl md:text-3xl font-bold mb-10"
            style={{ color: '#141210', fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            TERRE ÉTENDUE ISLAM
          </h1>
        </motion.div>

        {/* Manifeste */}
        <section className="mb-16">
          <h2
            className="text-lg font-semibold mb-6 flex items-center gap-3"
            style={{ color: '#C48A2E', fontSize: '14px', letterSpacing: '0.1em', fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            <span className="w-6 h-[1px]" style={{ background: 'rgba(196,138,46,0.3)' }} />
            MANIFESTE
          </h2>
          <div
            className="leading-relaxed text-[15px]"
            style={{ color: '#3D3A35', lineHeight: 1.8 }}
            dangerouslySetInnerHTML={{ __html: manifeste }}
          />
        </section>

        <div className="mb-16 h-[1px]" style={{ background: 'rgba(20,18,16,0.06)' }} />

        {/* Méthodologie */}
        <section className="mb-16">
          <h2
            className="text-lg font-semibold mb-6 flex items-center gap-3"
            style={{ color: '#3580C0', fontSize: '14px', letterSpacing: '0.1em', fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            <span className="w-6 h-[1px]" style={{ background: 'rgba(53,128,192,0.2)' }} />
            MÉTHODOLOGIE
          </h2>
          <div
            className="leading-relaxed text-[15px]"
            style={{ color: '#3D3A35', lineHeight: 1.8 }}
            dangerouslySetInnerHTML={{ __html: methodologie }}
          />
        </section>

        <div className="mb-16 h-[1px]" style={{ background: 'rgba(20,18,16,0.06)' }} />

        {/* État des lieux */}
        <section className="mb-16">
          <h2
            className="text-lg font-semibold mb-6 flex items-center gap-3"
            style={{ color: '#3580C0', fontSize: '14px', letterSpacing: '0.1em', fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            <span className="w-6 h-[1px]" style={{ background: 'rgba(53,128,192,0.2)' }} />
            ÉTAT DES LIEUX
          </h2>
          <div
            className="leading-relaxed text-[15px]"
            style={{ color: '#3D3A35', lineHeight: 1.8 }}
            dangerouslySetInnerHTML={{ __html: etatDesLieux }}
          />
        </section>

        <div className="mb-16 h-[1px]" style={{ background: 'rgba(20,18,16,0.06)' }} />

        {/* Éthique */}
        <section>
          <h2
            className="text-lg font-semibold mb-6 flex items-center gap-3"
            style={{ color: '#3A8F6E', fontSize: '14px', letterSpacing: '0.1em', fontFamily: "'Plus Jakarta Sans', sans-serif" }}
          >
            <span className="w-6 h-[1px]" style={{ background: 'rgba(58,143,110,0.3)' }} />
            ÉTHIQUE INTELLECTUELLE
          </h2>
          <div
            className="leading-relaxed text-[15px]"
            style={{ color: '#3D3A35', lineHeight: 1.8 }}
            dangerouslySetInnerHTML={{ __html: ethique }}
          />
        </section>
      </div>
    </div>
  );
}
