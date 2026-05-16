'use client';

import { useState } from 'react';
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
    code: 'EPISTEMO',
    title: "Le Q.G.",
    subtitle: "Fondements méthodologiques, cadre de pensée et philosophie de la recherche.",
    accent: 'cyan',
    icon: <Brain className="w-4 h-4" />,
  },
  observatory: {
    num: '02',
    code: 'EMPIRICAL',
    title: "L'Observatoire",
    subtitle: "Données brutes, observations astronomiques, mesures géodésiques.",
    accent: 'cyan',
    icon: <Compass className="w-4 h-4" />,
  },
  library: {
    num: '03',
    code: 'SACRED_SRC',
    title: "La Bibliothèque",
    subtitle: "Coran, hadiths, exégèses classiques. Le socle textuel.",
    accent: 'gold',
    icon: <BookOpen className="w-4 h-4" />,
  },
  lab: {
    num: '04',
    code: 'MODELING',
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

function estimateReadTime(desc: string): string {
  const words = desc.split(/\s+/).length;
  return `${Math.max(3, Math.ceil(words / 30))} min`;
}

export default function HudArticleList({ articles, category }: Props) {
  const [search, setSearch] = useState('');
  const config = PILLAR_CONFIGS[category] || PILLAR_CONFIGS.headquarters;

  const filtered = search
    ? articles.filter(a =>
        a.title.toLowerCase().includes(search.toLowerCase()) ||
        a.description.toLowerCase().includes(search.toLowerCase())
      )
    : articles;

  const [featured, ...rest] = filtered;

  const accentBorder = config.accent === 'gold' ? 'border-amber-500/30' : 'border-cyan-500/30';
  const accentHover = config.accent === 'gold' ? 'hover:border-amber-500/60' : 'hover:border-cyan-500/40';
  const accentText = config.accent === 'gold' ? 'text-amber-500' : 'text-cyan-400';
  const accentBg = config.accent === 'gold' ? 'bg-amber-950/80 border-amber-500/40 text-amber-400' : 'bg-cyan-950/80 border-cyan-500/40 text-cyan-400';

  return (
    <div className="w-full min-h-screen bg-[#050A12] text-slate-100 p-6 md:p-12 pt-20 md:pt-24">

      {/* HUD Header */}
      <div className="w-full border-b border-cyan-900/40 pb-6 mb-10 flex flex-col md:flex-row justify-between items-start md:items-end gap-4">
        <div>
          <div className={`flex items-center gap-2 ${accentText} font-mono text-xs tracking-[0.3em] uppercase mb-2`}>
            {config.icon} PILIER {config.num} // COMMAND_CENTER
          </div>
          <h1 className="text-3xl md:text-5xl uppercase tracking-tight text-transparent bg-clip-text bg-gradient-to-r from-white via-slate-200 to-cyan-500 font-orbitron">
            {config.title}
          </h1>
          <p className="text-slate-400 text-sm italic mt-2 font-body">
            {config.subtitle}
          </p>
        </div>
        <div className="font-mono text-xs text-right text-cyan-700 hidden md:block">
          <div>SYS_STATUS: ACTIVE</div>
          <div>DATABASE_INDEXED: {articles.length}_NODES</div>
        </div>
      </div>

      {/* Search */}
      <div className="max-w-[1800px] mx-auto mb-8">
        <input
          type="text"
          placeholder="FILTER_QUERY..."
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          className="w-full max-w-sm px-4 py-2 bg-[#0A1220] border border-slate-800 text-slate-300 placeholder:text-slate-600 focus:border-cyan-500/40 focus:outline-none transition-colors font-mono text-xs tracking-wider"
        />
      </div>

      {/* Article Grid */}
      <div className="w-full max-w-[1800px] mx-auto space-y-8">

        {filtered.length === 0 && (
          <p className="text-slate-500 font-mono text-sm">NO_RESULTS // QUERY_EMPTY</p>
        )}

        {/* Featured Card */}
        {featured && (
          <Link
            href={`/article/${featured.slug}`}
            className={`group block relative bg-gradient-to-r from-[#0A1220] to-[#060D1A] border ${accentBorder} rounded-lg overflow-hidden p-6 md:p-8 transition-all duration-500 ${accentHover} hover:shadow-[0_0_30px_rgba(6,182,212,0.05)]`}
          >
            {/* Corner marks */}
            <div className={`absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 ${config.accent === 'gold' ? 'border-amber-400 group-hover:border-amber-300' : 'border-cyan-400 group-hover:border-cyan-300'} transition-colors`} />
            <div className={`absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 ${config.accent === 'gold' ? 'border-amber-400 group-hover:border-amber-300' : 'border-cyan-400 group-hover:border-cyan-300'} transition-colors`} />

            {/* Watermark icon */}
            <div className="absolute right-6 top-1/2 -translate-y-1/2 opacity-[0.02] group-hover:opacity-[0.05] transition-opacity duration-500 pointer-events-none hidden lg:block">
              <Compass className="w-80 h-80 text-cyan-400 stroke-[0.5]" />
            </div>

            <div className="relative z-10 flex flex-col justify-between h-full gap-6">
              <div className="flex justify-between items-start">
                <span className={`font-mono text-xs px-2 py-1 ${accentBg} border rounded tracking-widest`}>
                  TEI-{config.num}.01 // CORE_FOCUS
                </span>
                <span className="font-mono text-xs text-amber-500 tracking-widest uppercase animate-pulse">
                  ⚡ Lecture Prioritaire
                </span>
              </div>

              <div className="max-w-3xl my-4">
                <h2 className={`text-2xl md:text-4xl uppercase text-white group-hover:${config.accent === 'gold' ? 'text-amber-400' : 'text-cyan-400'} transition-colors duration-300 font-orbitron`}>
                  {featured.title}
                </h2>
                <p className="text-slate-300 text-base md:text-lg leading-relaxed mt-4 opacity-90 line-clamp-3 font-body">
                  {featured.description}
                </p>
              </div>

              <div className="flex flex-wrap items-center gap-6 border-t border-slate-800/60 pt-4 font-mono text-xs text-slate-400">
                <span className="flex items-center gap-1.5"><Clock className="w-4 h-4 text-cyan-500" /> {estimateReadTime(featured.description)}</span>
                <span className="flex items-center gap-1.5"><Layers className="w-4 h-4 text-cyan-500" /> {config.code}</span>
                <span className="ml-auto text-slate-500">
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
                className="group relative bg-[#070F1C] border border-slate-800 rounded-lg p-6 flex flex-col justify-between min-h-[240px] transition-all duration-300 hover:bg-[#0A1526] hover:border-cyan-500/40"
              >
                {/* HUD micro detail */}
                <div className="absolute top-2 right-2 font-mono text-[9px] text-cyan-800 opacity-0 group-hover:opacity-100 transition-opacity">
                  + SYS_INDEX_{config.num}.{String(i + 2).padStart(2, '0')}
                </div>

                <div>
                  <div className="flex justify-between items-center mb-4">
                    <span className={`font-mono text-[11px] ${accentText} tracking-wider`}>
                      [TEI-{config.num}.{String(i + 2).padStart(2, '0')}]
                    </span>
                    <span className="font-mono text-[10px] text-slate-500">
                      {new Date(article.date).toLocaleDateString('fr-FR', { month: 'short', year: 'numeric' })}
                    </span>
                  </div>

                  <h3 className="text-xl uppercase text-slate-100 group-hover:text-cyan-400 transition-colors duration-200 line-clamp-2 font-orbitron" style={{fontSize: '16px'}}>
                    {article.title}
                  </h3>

                  <p className="text-slate-400 text-sm leading-relaxed mt-3 line-clamp-3 opacity-80 group-hover:opacity-100 transition-opacity font-body">
                    {article.description}
                  </p>
                </div>

                <div className="flex items-center gap-4 mt-6 pt-3 border-t border-slate-800/40 font-mono text-xs text-slate-500">
                  <span className="flex items-center gap-1 group-hover:text-slate-300 transition-colors">
                    <Clock className="w-3.5 h-3.5" /> {estimateReadTime(article.description)}
                  </span>
                  <span className="flex items-center gap-1">
                    <Terminal className="w-3.5 h-3.5" /> {config.code}
                  </span>
                  <span className="ml-auto flex items-center gap-1 text-cyan-600 group-hover:text-cyan-400 group-hover:translate-x-1 transition-all">
                    <span className="text-[10px] opacity-0 group-hover:opacity-100 transition-opacity tracking-widest">ACCESS</span> →
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
