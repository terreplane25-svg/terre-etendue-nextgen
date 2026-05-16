'use client';

import { useState, useRef, useEffect } from 'react';

// ─── Glossary Database ────────────────────────────
export interface GlossaryEntry {
  title: string;
  definition: string;
  domain: 'religion' | 'science' | 'method' | 'history';
  arabic?: string;
  seeAlso?: string; // slug of related article
}

export const GLOSSARY: Record<string, GlossaryEntry> = {
  // ── Sciences / Physique ──
  courbure: {
    title: 'Courbure',
    definition: "Mesure de la déviation d'une surface par rapport à un plan. Sur une sphère de rayon R, la chute due à la courbure vaut h = d²/(2R).",
    domain: 'science',
  },
  réfraction: {
    title: 'Réfraction atmosphérique',
    definition: "Déviation de la lumière traversant des couches d'air de densités différentes. Peut rendre visibles des objets théoriquement cachés par la courbure.",
    domain: 'science',
  },
  parallaxe: {
    title: 'Parallaxe',
    definition: "Déplacement apparent d'un objet quand on change de point d'observation. Utilisée pour mesurer les distances stellaires.",
    domain: 'science',
  },
  azimut: {
    title: 'Azimut',
    definition: "Angle horizontal mesuré depuis le nord géographique dans le sens des aiguilles d'une montre (0° à 360°).",
    domain: 'science',
  },
  zénith: {
    title: 'Zénith',
    definition: "Point du ciel situé exactement à la verticale au-dessus de l'observateur.",
    domain: 'science',
  },
  théodolite: {
    title: 'Théodolite',
    definition: "Instrument de mesure d'angles horizontaux et verticaux. Le « théodolite céleste » utilise les occultations stellaires pour tester la géométrie terrestre.",
    domain: 'science',
    seeAlso: 'le-theodolite-celeste',
  },
  occultation: {
    title: 'Occultation',
    definition: "Disparition d'un astre derrière un obstacle (montagne, Lune). Permet de mesurer des angles géométriques avec précision.",
    domain: 'science',
  },
  éclipse: {
    title: 'Éclipse',
    definition: "Phénomène où un astre est temporairement obscurci par un autre. Les éclipses solaires et lunaires fournissent des données géométriques précieuses.",
    domain: 'science',
  },
  selenelion: {
    title: 'Sélénélion',
    definition: "Éclipse lunaire où le Soleil ET la Lune sont tous deux visibles au-dessus de l'horizon — théoriquement impossible si les trois corps sont alignés.",
    domain: 'science',
  },
  singularité: {
    title: 'Singularité',
    definition: "Point où les lois physiques habituelles cessent de s'appliquer. Le centre d'un trou noir ou le temps zéro du Big Bang.",
    domain: 'science',
  },
  géodésique: {
    title: 'Géodésique',
    definition: "Plus court chemin entre deux points sur une surface courbe. Sur une sphère, c'est un arc de grand cercle.",
    domain: 'science',
  },
  topologie: {
    title: 'Topologie',
    definition: "Branche des mathématiques étudiant les propriétés qui se conservent par déformation continue (sans déchirer ni coller).",
    domain: 'science',
  },
  thermosphère: {
    title: 'Thermosphère',
    definition: "Couche atmosphérique entre ~85 et ~700 km d'altitude. Température extrêmement élevée (~2500°C) mais air si raréfié que la chaleur n'est pas ressentie.",
    domain: 'science',
  },
  ionosphère: {
    title: 'Ionosphère',
    definition: "Région de la haute atmosphère (60-1000 km) ionisée par le rayonnement solaire. Réfléchit les ondes radio.",
    domain: 'science',
  },
  fractale: {
    title: 'Fractale',
    definition: "Structure géométrique auto-similaire : chaque partie reproduit le tout à une échelle différente.",
    domain: 'science',
  },
  mgpp: {
    title: 'MGPP',
    definition: "Modèle Géocentrique à Plans Parallèles. Modèle géométrique alternatif proposé par Terre Étendue Islam.",
    domain: 'science',
    seeAlso: 'le-modele-geocentrique-a-plans-paralleles-mgpp',
  },

  // ── Religion / Théologie ──
  tawhîd: {
    title: 'Tawhîd',
    definition: "Unicité absolue de Dieu en Islam. Principe fondamental de la théologie islamique.",
    domain: 'religion',
    arabic: 'توحيد',
  },
  kalâm: {
    title: 'Kalâm',
    definition: "Théologie discursive islamique. Discipline rationnelle visant à défendre les croyances par l'argumentation logique.",
    domain: 'religion',
    arabic: 'كلام',
  },
  sourate: {
    title: 'Sourate',
    definition: "Chapitre du Coran. Le Coran contient 114 sourates de longueurs variables.",
    domain: 'religion',
    arabic: 'سورة',
  },
  ayah: {
    title: 'Ayah (verset)',
    definition: "Verset du Coran. Littéralement « signe » en arabe. Le Coran compte plus de 6200 versets.",
    domain: 'religion',
    arabic: 'آية',
  },
  hadith: {
    title: 'Hadith',
    definition: "Parole, acte ou approbation attribué au Prophète Muhammad ﷺ, transmis par une chaîne de rapporteurs.",
    domain: 'religion',
    arabic: 'حديث',
  },
  isnad: {
    title: 'Isnad',
    definition: "Chaîne de transmission d'un hadith, de rapporteur en rapporteur jusqu'au Prophète ﷺ. Critère central d'authentification.",
    domain: 'religion',
    arabic: 'إسناد',
  },
  exégèse: {
    title: 'Exégèse (Tafsîr)',
    definition: "Commentaire et interprétation du texte coranique. Les grands tafsîr classiques sont ceux d'al-Tabarî, al-Qurtubî, Ibn Kathîr.",
    domain: 'religion',
    arabic: 'تفسير',
  },
  tafsir: {
    title: 'Tafsîr',
    definition: "Commentaire exégétique du Coran. Science islamique majeure visant à expliquer le sens des versets.",
    domain: 'religion',
    arabic: 'تفسير',
  },
  concordisme: {
    title: 'Concordisme',
    definition: "Approche qui cherche à faire coïncider les textes sacrés avec les découvertes scientifiques modernes. Critiqué par TEI.",
    domain: 'religion',
    seeAlso: 'le-concordisme',
  },
  dahā: {
    title: 'Dahā (دحاها)',
    definition: "Terme coranique (79:30) signifiant « aplanir, étaler ». Souvent faussement traduit par « donner la forme d'un œuf ».",
    domain: 'religion',
    arabic: 'دحاها',
    seeAlso: 'la-terre-dans-le-coran',
  },
  sutihat: {
    title: 'Sutihat (سُطِحَتْ)',
    definition: "Terme coranique (88:20) signifiant « nivelée, aplanie ». Décrit la surface terrestre.",
    domain: 'religion',
    arabic: 'سُطِحَتْ',
  },

  // ── Méthodologie ──
  falsifiabilité: {
    title: 'Falsifiabilité',
    definition: "Critère de Karl Popper : une théorie est scientifique si elle peut en principe être réfutée par une observation.",
    domain: 'method',
  },
  'hypothèse nulle': {
    title: 'Hypothèse nulle',
    definition: "En statistique, hypothèse par défaut supposant l'absence d'effet. On ne la rejette que si les données l'imposent.",
    domain: 'method',
    seeAlso: 'lhypothese-nulle-dynamique-et-cinematique',
  },
  paradigme: {
    title: 'Paradigme',
    definition: "Cadre théorique dominant à une époque donnée (Thomas Kuhn). Un changement de paradigme est une révolution scientifique.",
    domain: 'method',
  },

  // ── Personnages historiques ──
  ptolémée: {
    title: 'Ptolémée (~100-170)',
    definition: "Astronome grec auteur de l'Almageste. Son modèle géocentrique a dominé l'astronomie pendant 1400 ans.",
    domain: 'history',
  },
  ératosthène: {
    title: 'Ératosthène (~276-194 av. J.-C.)',
    definition: "Savant grec qui aurait mesuré la circonférence terrestre. TEI analyse les limites de sa méthode.",
    domain: 'history',
    seeAlso: 'le-mythe-deratosthene',
  },
  copernic: {
    title: 'Copernic (1473-1543)',
    definition: "Astronome polonais, auteur du modèle héliocentrique plaçant le Soleil au centre du système.",
    domain: 'history',
  },
  géocentrique: {
    title: 'Géocentrisme',
    definition: "Modèle cosmologique plaçant la Terre au centre de l'univers. Position classique en astronomie avant Copernic.",
    domain: 'history',
  },
  héliocentrique: {
    title: 'Héliocentrisme',
    definition: "Modèle plaçant le Soleil au centre du système solaire. Proposé par Copernic, adopté après Galilée et Newton.",
    domain: 'history',
  },
};

// ─── Domain labels and colors ─────────────────────
const DOMAIN_STYLES: Record<string, { label: string; color: string; bg: string; border: string }> = {
  religion: { label: 'SACRÉ', color: 'text-[#D4A843]', bg: 'bg-[rgba(212,168,67,0.08)]', border: 'border-[rgba(212,168,67,0.15)]' },
  science: { label: 'SCIENCE', color: 'text-[#00C8FF]', bg: 'bg-[rgba(0,200,255,0.06)]', border: 'border-[rgba(0,200,255,0.12)]' },
  method: { label: 'MÉTHODE', color: 'text-[#00E87B]', bg: 'bg-[rgba(0,232,123,0.06)]', border: 'border-[rgba(0,232,123,0.12)]' },
  history: { label: 'HISTOIRE', color: 'text-[#C8D8E8]/50', bg: 'bg-[rgba(200,216,232,0.04)]', border: 'border-[rgba(200,216,232,0.08)]' },
};

// ─── Tooltip Component ────────────────────────────
interface TooltipProps {
  term: string;
  children: React.ReactNode;
}

export default function GlossaryTooltip({ term, children }: TooltipProps) {
  const [visible, setVisible] = useState(false);
  const [pos, setPos] = useState<{ top: number; left: number }>({ top: 0, left: 0 });
  const ref = useRef<HTMLSpanElement>(null);
  const entry = GLOSSARY[term.toLowerCase()];

  if (!entry) return <>{children}</>;

  const domain = DOMAIN_STYLES[entry.domain] || DOMAIN_STYLES.science;

  const show = () => {
    if (ref.current) {
      const rect = ref.current.getBoundingClientRect();
      setPos({
        top: rect.bottom + window.scrollY + 8,
        left: Math.max(16, Math.min(rect.left + rect.width / 2 - 160, window.innerWidth - 336)),
      });
    }
    setVisible(true);
  };

  return (
    <>
      <span
        ref={ref}
        className={`glossary-inline cursor-help ${domain.color}`}
        onMouseEnter={show}
        onMouseLeave={() => setVisible(false)}
        onFocus={show}
        onBlur={() => setVisible(false)}
        tabIndex={0}
      >
        {children}
      </span>

      {visible && (
        <div
          className="fixed z-[80] w-[320px] bg-[#0D1528] border border-[rgba(0,200,255,0.12)] shadow-[0_0_40px_rgba(0,0,0,0.5)] p-0 overflow-hidden"
          style={{ top: pos.top, left: pos.left, position: 'absolute' }}
        >
          {/* Top accent line */}
          <div className={`h-[2px] ${entry.domain === 'religion' ? 'bg-[#D4A843]' : entry.domain === 'science' ? 'bg-[#00C8FF]' : entry.domain === 'method' ? 'bg-[#00E87B]' : 'bg-[#C8D8E8]/20'}`} />

          <div className="p-4">
            {/* Header */}
            <div className="flex items-center justify-between mb-2">
              <h4 className="text-sm font-semibold text-[#C8D8E8] font-rajdhani">
                {entry.title}
              </h4>
              <span
                className={`text-[7px] tracking-[0.15em] px-2 py-0.5 ${domain.bg} ${domain.border} border ${domain.color} font-tech-mono`}
              >
                {domain.label}
              </span>
            </div>

            {/* Arabic */}
            {entry.arabic && (
              <p className="text-[#D4A843] text-lg mb-2 font-arabic" style={{ direction: 'rtl' }}>
                {entry.arabic}
              </p>
            )}

            {/* Definition */}
            <p className="text-[12px] text-[#C8D8E8]/50 leading-relaxed font-rajdhani">
              {entry.definition}
            </p>

            {/* See also link */}
            {entry.seeAlso && (
              <a
                href={`/article/${entry.seeAlso}`}
                className="block mt-3 pt-2 border-t border-[rgba(0,200,255,0.06)] text-[10px] text-[#00C8FF]/40 hover:text-[#00C8FF]/70 transition-colors"
                style={{letterSpacing: '0.1em' }}
              >
                → VOIR L&apos;ARTICLE
              </a>
            )}
          </div>
        </div>
      )}
    </>
  );
}
