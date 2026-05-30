'use client';


import Link from 'next/link';
import { Clock, Layers, Terminal, Compass, BookOpen, FlaskConical, Brain } from 'lucide-react';
import { FontOrbitron } from '@/components/FontWrappers';
import type { ArticleMeta } from '@/lib/articles';

// Pillar config
interface PillarConfig {
  num: string;
  code: string;
  title: string;
  subtitle: string;
  accent: 'cyan' | 'gold';
  icon: React.ReactNode;
}

const PILLAR_CONFIGS: Record<string, PillarConfig> = {
  headquarters: {
    num: '01',
    code: 'ÉPISTÉMO',
    title: "Le Q.G.",
    subtitle: "Fondements méthodologiques, cadre de pensée et philosophie de la recherche.",
    accent: 'cyan',
    icon: <Brain className="w-4 h-4" />,
  },
  observatory: {
    num: '02',
    code: 'EMPIRIQUE',
    title: "L'Observatoire",
    subtitle: "Données brutes, observations astronomiques, mesures géodésiques.",
    accent: 'cyan',
    icon: <Compass className="w-4 h-4" />,
  },
  library: {
    num: '03',
    code: 'SOURCES',
    title: "La Bibliothèque",
    subtitle: "Coran, hadiths, exégèses classiques. Le socle textuel.",
    accent: 'gold',
    icon: <BookOpen className="w-4 h-4" />,
  },
  lab: {
    num: '04',
    code: 'MODÉLI.',
    title: "Le Lab",
    subtitle: "Simulations 3D, modèles géométriques, visualisations interactives.",
    accent: 'cyan',
    icon: <FlaskConical className="w-4 h-4" />,
  },
};

interface Props {
  articles: ArticleMeta[];
  category: string;
}

function formatReadTime(article: ArticleMeta): string {
  return `${article.readTime || 3} min`;
}

export default function HudArticleList({ articles, category }: Props) {
  const config = PILLAR_CONFIGS[category] || PILLAR_CONFIGS.headquarters;

  const [featured, ...rest] = articles;

  const accentBorder = config.accent === 'gold' ? 'border-[var(--gold-20)]' : 'border-[var(--cyan-20)]';
  const accentHover = config.accent === 'gold' ? 'hover:border-[var(--gold-50)]' : 'hover:border-[var(--cyan-50)]';
  const accentText = config.accent === 'gold' ? 'text-[var(--gold)]' : 'text-[var(--cyan)]';
  const accentBg = config.accent === 'gold' ? 'bg-[var(--panel)] border-[var(--gold-20)] text-[var(--gold)]' : 'bg-[var(--panel)] border-[var(--cyan-50)] text-[var(--cyan)]';

  return (
    <div className="w-full min-h-screen bg-[var(--void)] text-[var(--text)] p-6 md:p-12 pt-20 md:pt-24">

      {/* HUD Header */}
      <div className="w-full border-b border-[var(--panel-edge)] pb-6 mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <div className={`flex items-center gap-2 ${accentText} font-mono text-xs tracking-[0.3em] uppercase mb-2`}>
            {config.icon} PILIER {config.num} // CENTRE_COMMANDE
          </div>
          <h1 className="text-3xl md:text-5xl uppercase tracking-tight text-[var(--text)] font-orbitron">
            {config.title}
          </h1>
          <p className="text-[var(--text-60)] text-sm italic mt-2 font-body">
            {config.subtitle}
          </p>
        </div>
        <div className="font-mono text-xs text-right text-[var(--cyan-50)] hidden md:block">
          <div>ÉTAT_SYS: ACTIF</div>
          <div>BASE_INDEXÉE: {articles.length}_NŒUDS</div>
        </div>
      </div>

      {/* Article Grid */}
      <div className="w-full max-w-[1800px] mx-auto space-y-8">

        {/* Featured Card */}
        {featured && (
          <Link
            href={`/article/${featured.slug}`}
            className={`group block relative bg-[var(--panel)] border ${accentBorder} rounded-lg overflow-hidden p-6 md:p-8 transition-all duration-500 ${accentHover} hover:shadow-[0_0_30px_rgba(6,182,212,0.05)]`}
          >
            {/* Corner marks */}
            <div className={`absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 ${config.accent === 'gold' ? 'border-[var(--gold)] group-hover:border-[var(--gold)]' : 'border-[var(--cyan)] group-hover:border-[var(--cyan)]'} transition-colors`} />
            <div className={`absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 ${config.accent === 'gold' ? 'border-[var(--gold)] group-hover:border-[var(--gold)]' : 'border-[var(--cyan)] group-hover:border-[var(--cyan)]'} transition-colors`} />

            {/* Watermark icon */}
            <div className="absolute right-6 top-1/2 -translate-y-1/2 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity duration-500 pointer-events-none hidden lg:block">
              <Compass className="w-80 h-80 text-[var(--cyan)] stroke-[0.5]" />
            </div>

            <div className="relative z-10 flex flex-col justify-between h-full gap-6">
              <div className="flex justify-between items-start">
                <span className={`font-mono text-xs px-2 py-1 ${accentBg} border rounded tracking-widest`}>
                  TEI-{config.num}.01 // LECTURE_CLÉ
                </span>
                <span className="font-mono text-xs text-[var(--gold)] tracking-widest uppercase animate-pulse">
                  ⚡ Lecture prioritaire
                </span>
              </div>

              <div className="max-w-3xl my-4">
                <h2 className={`text-2xl md:text-4xl uppercase text-[var(--text)] group-hover:${config.accent === 'gold' ? 'text-[var(--gold)]' : 'text-[var(--cyan)]'} transition-colors duration-300 font-orbitron`}>
                  {featured.title}
                </h2>
                <p className="text-[var(--text-60)] text-base md:text-lg leading-relaxed mt-4 opacity-90 line-clamp-3 font-body">
                  {featured.description}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-6 border-t border-[var(--panel-edge)]/60 pt-4 font-mono text-xs text-[var(--text-60)]">
                <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-[var(--cyan)]" /> {formatReadTime(featured)}</span>
                <span className="flex items-center gap-1.5"><Layers className="w-4 h-4 text-[var(--cyan)]" /> {config.code}</span>
                <span className="ml-auto text-[var(--text-30)]">
                  {new Date(featured.date).toLocaleDateString('fr-FR', { month: 'long', year: 'numeric' })}
                </span>
              </div>
            </div>
          </Link>
        )}

        {/* Regular Grid */}
        {rest.length > 0 && (
          <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
            {rest.map((article, i) => (
              <Link
                key={article.slug}
                href={`/article/${article.slug}`}
                className="group relative bg-[var(--panel)] border border-[var(--panel-edge)] rounded-lg p-6 flex flex-col justify-between min-h-[240px] transition-all duration-300 hover:bg-[var(--panel)] hover:border-[var(--cyan-50)]"
              >
                {/* HUD micro detail */}
                <div className="absolute top-2 right-2 font-mono text-[9px] text-[var(--cyan-20)] opacity-0 group-hover:opacity-100 transition-opacity">
                  + INDEX_{config.num}.{String(i + 2).padStart(2, '0')}
                </div>

                <div>
                  <div className="flex justify-between items-center mb-4">
                    <span className={`font-mono text-[11px] ${accentText} tracking-wider`}>
                      [TEI-{config.num}.{String(i + 2).padStart(2, '0')}]
                    </span>
                    <span className="font-mono text-[10px] text-[var(--text-30)]">
                      {new Date(article.date).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
                    </span>
                  </div>

                  <h3 className="text-xl uppercase text-[var(--text)] group-hover:text-[var(--cyan)] transition-colors duration-200 line-clamp-2 font-orbitron" style={{fontSize: '16px'}}>
                    {article.title}
                  </h3>

                  <p className="text-[var(--text-60)] text-sm leading-relaxed mt-3 line-clamp-3 opacity-80 group-hover:opacity-100 transition-opacity font-body">
                    {article.description}
                  </p>
                </div>

                <div className="flex items-center gap-4 mt-6 pt-3 border-t border-[var(--panel-edge)] font-mono text-xs text-[var(--text-30)]">
                  <span className="flex items-center gap-1 group-hover:text-[var(--text-60)] transition-colors">
                    <Clock className="w-3.5 h-3.5" /> {formatReadTime(article)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Terminal className="w-3.5 h-3.5" /> {config.code}
                  </span>
                  <span className="ml-auto flex items-center gap-1 text-[var(--cyan-50)] group-hover:text-[var(--cyan)] group-hover:translate-x-1 transition-all">
                    <span className="text-[10px] opacity-0 group-hover:opacity-100 transition-opacity tracking-widest">ACCÈS</span> →
                  </span>
                </div>
              </Link>
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
