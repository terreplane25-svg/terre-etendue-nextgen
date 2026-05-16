'use client';

import { useState } from 'react';
import { FontOrbitron } from '@/components/FontWrappers';

// ─── Image Component ──────────────────────────────
interface TeiImageProps {
  src: string;
  alt: string;
  caption?: string;
  wide?: boolean;
}

export function TeiImage({ src, alt, caption, wide }: TeiImageProps) {
  const [loaded, setLoaded] = useState(false);
  const [error, setError] = useState(false);

  return (
    <figure className={`my-10 ${wide ? 'mx-[-2rem]' : ''}`}>
      <div className="relative border border-[rgba(0,200,255,0.08)] rounded overflow-hidden bg-[#0A1220]">
        {/* Corner marks */}
        <div className="absolute top-0 left-0 w-2.5 h-2.5 border-t border-l border-cyan-400/30 z-10" />
        <div className="absolute bottom-0 right-0 w-2.5 h-2.5 border-b border-r border-cyan-400/30 z-10" />

        {!error ? (
          <img
            src={src}
            alt={alt}
            onLoad={() => setLoaded(true)}
            onError={() => setError(true)}
            className={`w-full transition-opacity duration-500 ${loaded ? 'opacity-100' : 'opacity-0'}`}
          />
        ) : (
          <div className="w-full h-48 flex items-center justify-center">
            <div className="text-center">
              <div className="font-mono text-[9px] text-cyan-500/30 tracking-widest mb-2">MEDIA_PENDING</div>
              <p className="text-[12px] text-slate-500 max-w-xs px-4 font-rajdhani">{alt}</p>
            </div>
          </div>
        )}

        {!loaded && !error && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="w-5 h-5 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin" />
          </div>
        )}
      </div>

      {caption && (
        <figcaption className="mt-3 px-1 flex items-start gap-2">
          <span className="font-mono text-[8px] text-cyan-500/40 tracking-widest mt-0.5 flex-shrink-0">FIG.</span>
          <span className="text-[12px] text-slate-400 leading-relaxed font-rajdhani">
            {caption}
          </span>
        </figcaption>
      )}
    </figure>
  );
}

// ─── Video Component ──────────────────────────────
interface TeiVideoProps {
  src: string;
  caption?: string;
  poster?: string;
}

export function TeiVideo({ src, caption, poster }: TeiVideoProps) {
  return (
    <figure className="my-10">
      <div className="relative border border-[rgba(0,200,255,0.08)] rounded overflow-hidden bg-[#0A1220]">
        <div className="absolute top-0 left-0 w-2.5 h-2.5 border-t border-l border-cyan-400/30 z-10" />
        <div className="absolute bottom-0 right-0 w-2.5 h-2.5 border-b border-r border-cyan-400/30 z-10" />
        <video
          src={src}
          poster={poster}
          controls
          className="w-full"
          preload="metadata"
        />
      </div>
      {caption && (
        <figcaption className="mt-3 px-1 flex items-start gap-2">
          <span className="font-mono text-[8px] text-cyan-500/40 tracking-widest mt-0.5 flex-shrink-0">VID.</span>
          <span className="text-[12px] text-slate-400 leading-relaxed font-rajdhani">
            {caption}
          </span>
        </figcaption>
      )}
    </figure>
  );
}

// ─── Data Visualizer Placeholder ──────────────────
interface TeiDataVisualizerProps {
  type: '3d-mesh' | 'vector-graph' | 'timeline' | 'comparison' | 'geometric';
  title: string;
  description: string;
}

export function TeiDataVisualizer({ type, title, description }: TeiDataVisualizerProps) {
  const typeLabels: Record<string, string> = {
    '3d-mesh': '3D_MESH',
    'vector-graph': 'VECTOR_GRAPH',
    'timeline': 'TIMELINE',
    'comparison': 'COMPARISON',
    'geometric': 'GEOMETRIC_TRACE',
  };

  return (
    <figure className="my-10">
      <div className="relative border border-cyan-500/20 rounded overflow-hidden bg-gradient-to-br from-[#0A1220] to-[#060D1A] p-8 min-h-[200px] flex items-center justify-center">
        {/* Corner marks */}
        <div className="absolute top-0 left-0 w-3 h-3 border-t-2 border-l-2 border-cyan-400/30" />
        <div className="absolute bottom-0 right-0 w-3 h-3 border-b-2 border-r-2 border-cyan-400/30" />
        <div className="absolute top-0 right-0 w-3 h-3 border-t-2 border-r-2 border-cyan-400/10" />
        <div className="absolute bottom-0 left-0 w-3 h-3 border-b-2 border-l-2 border-cyan-400/10" />

        {/* Grid pattern */}
        <div className="absolute inset-0 opacity-[0.03]" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 29px, rgba(0,200,255,0.3) 29px, rgba(0,200,255,0.3) 30px), repeating-linear-gradient(90deg, transparent, transparent 29px, rgba(0,200,255,0.3) 29px, rgba(0,200,255,0.3) 30px)'
        }} />

        <div className="relative z-10 text-center space-y-3">
          <div className="font-mono text-[9px] text-cyan-500/40 tracking-[0.3em]">
            {typeLabels[type] || 'VISUALIZATION'} // RENDER_PENDING
          </div>
          <h4 className="text-lg text-slate-200 font-orbitron" style={{fontSize: '14px'}}>
            {title}
          </h4>
          <p className="text-[12px] text-slate-500 max-w-md mx-auto leading-relaxed font-rajdhani">
            {description}
          </p>
          <div className="flex items-center justify-center gap-2 pt-2">
            <div className="w-2 h-2 rounded-full bg-amber-500/50 animate-pulse" />
            <span className="font-mono text-[8px] text-amber-500/40 tracking-widest">EN DÉVELOPPEMENT</span>
          </div>
        </div>
      </div>
    </figure>
  );
}
