'use client';

import { useState, useRef, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// ─── Base de données du glossaire ─────────────────
const GLOSSARY: Record<string, { title: string; definition: string; domain: 'religion' | 'science' }> = {
  tawhid: {
    title: 'Tawhid (توحيد)',
    definition: "L'unicité absolue d'Allah. Fondement de la foi islamique affirmant qu'Allah est Un, sans associé ni semblable.",
    domain: 'religion',
  },
  kalam: {
    title: 'Kalâm (علم الكلام)',
    definition: "Théologie spéculative islamique. Discipline qui utilise la raison dialectique pour défendre les doctrines de la foi.",
    domain: 'religion',
  },
  singularite: {
    title: 'Singularité',
    definition: "Point de l'espace-temps où la courbure devient infinie. Les lois de la physique classique cessent de s'appliquer (ex : centre d'un trou noir, Big Bang).",
    domain: 'science',
  },
  fractale: {
    title: 'Fractale',
    definition: "Structure géométrique auto-similaire : chaque partie reproduit la forme du tout, à toutes les échelles. Concept fondamental de la géométrie non-euclidienne.",
    domain: 'science',
  },
  sourate: {
    title: 'Sourate (سورة)',
    definition: "Chapitre du Coran. Le Coran contient 114 sourates, chacune composée de versets (ayat).",
    domain: 'religion',
  },
  ayah: {
    title: 'Ayah (آية)',
    definition: "Verset coranique. Littéralement « signe » — chaque verset est un signe divin porteur de sens.",
    domain: 'religion',
  },
  geodesique: {
    title: 'Géodésique',
    definition: "Le plus court chemin entre deux points sur une surface courbe. Sur une sphère, c'est un arc de grand cercle. Concept central en relativité générale.",
    domain: 'science',
  },
  hadith: {
    title: 'Hadith (حديث)',
    definition: "Récit rapportant les paroles, actes ou approbations du Prophète Muhammad ﷺ. Source fondamentale après le Coran.",
    domain: 'religion',
  },
  topologie: {
    title: 'Topologie',
    definition: "Branche des mathématiques étudiant les propriétés des espaces qui sont préservées sous déformation continue (étirement, torsion, mais pas déchirure).",
    domain: 'science',
  },
  isnad: {
    title: 'Isnâd (إسناد)',
    definition: "Chaîne de transmission d'un hadith. Chaque maillon est un rapporteur dont la fiabilité est évaluée par la science du hadith.",
    domain: 'religion',
  },
};

// ─── Composant Tooltip ────────────────────────────
interface GlossaryTooltipProps {
  term: string;
  children: React.ReactNode;
}

export default function GlossaryTooltip({ term, children }: GlossaryTooltipProps) {
  const [show, setShow] = useState(false);
  const [position, setPosition] = useState<'top' | 'bottom'>('top');
  const ref = useRef<HTMLSpanElement>(null);
  const entry = GLOSSARY[term.toLowerCase()];

  useEffect(() => {
    if (show && ref.current) {
      const rect = ref.current.getBoundingClientRect();
      setPosition(rect.top < 200 ? 'bottom' : 'top');
    }
  }, [show]);

  if (!entry) {
    return <span>{children}</span>;
  }

  const accentClass = entry.domain === 'religion' ? 'border-accent-gold' : 'border-accent-cyan';
  const dotColor = entry.domain === 'religion' ? 'bg-accent-gold' : 'bg-accent-cyan';

  return (
    <span
      ref={ref}
      className="glossary-term inline-block"
      onMouseEnter={() => setShow(true)}
      onMouseLeave={() => setShow(false)}
      onFocus={() => setShow(true)}
      onBlur={() => setShow(false)}
      tabIndex={0}
      role="button"
      aria-describedby={`glossary-${term}`}
    >
      {children}

      <AnimatePresence>
        {show && (
          <motion.div
            id={`glossary-${term}`}
            role="tooltip"
            initial={{ opacity: 0, y: position === 'top' ? 8 : -8, scale: 0.96 }}
            animate={{ opacity: 1, y: 0, scale: 1 }}
            exit={{ opacity: 0, y: position === 'top' ? 8 : -8, scale: 0.96 }}
            transition={{ duration: 0.15, ease: 'easeOut' }}
            className={`absolute z-50 w-72 p-4 bg-surface border ${accentClass} rounded-lg shadow-xl ${
              position === 'top' ? 'bottom-full mb-2' : 'top-full mt-2'
            } left-1/2 -translate-x-1/2`}
          >
            {/* Header */}
            <div className="flex items-center gap-2 mb-2">
              <span className={`w-2 h-2 rounded-full ${dotColor}`} />
              <h4 className="font-display font-semibold text-sm text-[#E8E4DD]">{entry.title}</h4>
            </div>

            {/* Definition */}
            <p className="text-xs text-[#E8E4DD]/40 leading-relaxed">{entry.definition}</p>

            {/* Domain Badge */}
            <div className="mt-3 pt-2 border-t border-white/[0.06]">
              <span
                className={`text-xs uppercase tracking-widest font-medium ${
                  entry.domain === 'religion' ? 'text-accent-gold' : 'text-accent-cyan'
                }`}
              >
                {entry.domain === 'religion' ? '📚 Sources Sacrées' : '⚗️ Science'}
              </span>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </span>
  );
}

// ─── Helper : enrichir du HTML d'article avec des tooltips ───
export { GLOSSARY };
