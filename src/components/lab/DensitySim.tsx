'use client';
import { useState, useRef, useEffect, useCallback } from 'react';

interface Layer {
  id: number;
  name: string;
  density: number;
  color: string;
  height: number;
}

const DEFAULT_LAYERS: Layer[] = [
  { id: 1, name: 'Mercure', density: 13.5, color: '#A0A0A0', height: 60 },
  { id: 2, name: 'Eau', density: 1.0, color: '#4488CC', height: 80 },
  { id: 3, name: 'Huile', density: 0.9, color: '#E8C060', height: 60 },
  { id: 4, name: 'Air', density: 0.0012, color: '#80D0E0', height: 100 },
];

const OBJECTS = [
  { name: 'Bille d\'acier', density: 7.8, radius: 12, color: '#C8C8D0', emoji: '●' },
  { name: 'Bille de bois', density: 0.6, radius: 14, color: '#C8A060', emoji: '●' },
  { name: 'Balle de ping-pong', density: 0.08, radius: 16, color: '#F0F0F0', emoji: '○' },
  { name: 'Glaçon', density: 0.92, radius: 18, color: '#A0D8F0', emoji: '◇' },
  { name: 'Ballon d\'hélium', density: 0.000164, radius: 22, color: '#FF6060', emoji: '◎' },
  { name: 'Objet custom', density: 1.5, radius: 14, color: '#D4A843', emoji: '◆' },
];

function getObjectPosition(objDensity: number, layers: Layer[]): { y: number; layerName: string; status: string } {
  const sorted = [...layers].sort((a, b) => b.density - a.density);
  let yAccum = 0;

  for (let i = 0; i < sorted.length; i++) {
    const layer = sorted[i];
    const nextLayer = sorted[i + 1];
    const nextDensity = nextLayer ? nextLayer.density : 0;

    if (objDensity >= layer.density) {
      return { y: yAccum, layerName: layer.name, status: `Coule au fond (plus dense que ${layer.name})` };
    }
    if (objDensity >= nextDensity && objDensity < layer.density) {
      const frac = (layer.density - objDensity) / (layer.density - nextDensity || 1);
      return {
        y: yAccum + layer.height * frac,
        layerName: nextLayer ? `${layer.name}/${nextLayer.name}` : layer.name,
        status: nextLayer
          ? `Flotte à l'interface ${layer.name}/${nextLayer.name}`
          : `Flotte à la surface de ${layer.name}`,
      };
    }
    yAccum += layer.height;
  }
  return { y: yAccum + 20, layerName: 'au-dessus', status: 'S\'élève au-dessus de tout (hélium)' };
}

export default function DensitySim() {
  const [layers, setLayers] = useState<Layer[]>(DEFAULT_LAYERS);
  const [selectedObj, setSelectedObj] = useState(0);
  const [customDensity, setCustomDensity] = useState(1.5);
  const [animY, setAnimY] = useState(0);
  const [dropped, setDropped] = useState(false);
  const animRef = useRef<number>(0);

  const obj = OBJECTS[selectedObj];
  const objDensity = selectedObj === OBJECTS.length - 1 ? customDensity : obj.density;
  const sortedLayers = [...layers].sort((a, b) => b.density - a.density);
  const totalH = sortedLayers.reduce((s, l) => s + l.height, 0);

  const target = getObjectPosition(objDensity, layers);

  const drop = useCallback(() => {
    setDropped(true);
    setAnimY(totalH + 40);
    const startY = totalH + 40;
    const endY = target.y;
    const startTime = Date.now();
    const duration = 1200 + Math.abs(startY - endY) * 3;

    const animate = () => {
      const elapsed = Date.now() - startTime;
      const t = Math.min(elapsed / duration, 1);
      const ease = 1 - Math.pow(1 - t, 3);
      const bounce = t >= 0.85 ? Math.sin((t - 0.85) * 20) * (1 - t) * 8 : 0;
      setAnimY(startY + (endY - startY) * ease + bounce);
      if (t < 1) animRef.current = requestAnimationFrame(animate);
    };
    cancelAnimationFrame(animRef.current);
    animRef.current = requestAnimationFrame(animate);
  }, [target.y, totalH]);

  useEffect(() => {
    return () => cancelAnimationFrame(animRef.current);
  }, []);

  const reset = () => {
    setDropped(false);
    setAnimY(totalH + 40);
    cancelAnimationFrame(animRef.current);
  };

  const colW = 220;
  const colX = 60;

  return <div className="w-full">
    {/* Contrôles */}
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      {/* Sélection d'objet */}
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-slate-400 tracking-widest mb-3">OBJET</div>
        <div className="grid grid-cols-3 gap-2">
          {OBJECTS.map((o, i) => (
            <button key={o.name} onClick={() => { setSelectedObj(i); reset(); }}
              className="border p-2 text-center transition-all"
              style={{
                borderColor: i === selectedObj ? '#D4A843' : '#1e293b',
                backgroundColor: i === selectedObj ? '#D4A8431a' : 'transparent',
              }}>
              <div className="text-[16px]" style={{ color: o.color }}>{o.emoji}</div>
              <div className="text-[9px] font-tech-mono text-slate-400 mt-1">{o.name}</div>
              <div className="text-[8px] font-tech-mono text-slate-600">ρ = {o.density}</div>
            </button>
          ))}
        </div>
        {selectedObj === OBJECTS.length - 1 && (
          <div className="mt-3 flex items-center gap-3">
            <label className="text-[10px] font-tech-mono text-[#D4A843]">DENSITÉ CUSTOM :</label>
            <input type="range" min={0.0001} max={20} step={0.01} value={customDensity}
              onChange={e => { setCustomDensity(+e.target.value); reset(); }}
              className="flex-1 accent-[#D4A843] h-2" />
            <input type="number" min={0.0001} max={20} step={0.01} value={customDensity}
              onChange={e => { const v = +e.target.value; if (!isNaN(v) && v > 0) { setCustomDensity(v); reset(); } }}
              className="w-20 bg-[#050A12] border border-[#D4A843]/40 text-[13px] font-tech-mono text-[#D4A843] px-2 py-1 text-right rounded-none" />
          </div>
        )}
      </div>

      {/* Couches de fluide */}
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-slate-400 tracking-widest mb-3">COUCHES DE FLUIDE</div>
        <div className="space-y-2">
          {sortedLayers.map(l => (
            <div key={l.id} className="flex items-center gap-3">
              <div className="w-3 h-3 rounded-full flex-shrink-0" style={{ background: l.color }} />
              <span className="text-[11px] font-tech-mono text-slate-300 w-20">{l.name}</span>
              <span className="text-[10px] font-tech-mono text-slate-500">ρ =</span>
              <input type="number" min={0.0001} max={20} step={0.01} value={l.density}
                onChange={e => {
                  const v = +e.target.value;
                  if (!isNaN(v) && v > 0) {
                    setLayers(prev => prev.map(x => x.id === l.id ? { ...x, density: v } : x));
                    reset();
                  }
                }}
                className="w-20 bg-[#050A12] border border-slate-700 text-[11px] font-tech-mono text-slate-300 px-2 py-1 text-right rounded-none" />
              <span className="text-[9px] font-tech-mono text-slate-600">g/cm³</span>
            </div>
          ))}
        </div>
      </div>
    </div>

    {/* Boutons action */}
    <div className="flex gap-3 mb-4">
      <button onClick={drop}
        className="px-6 py-2.5 text-[11px] font-tech-mono tracking-widest border border-[#00E87B]/50 text-[#00E87B] bg-[#00E87B]/10 hover:bg-[#00E87B]/20 transition-all">
        LÂCHER L&apos;OBJET
      </button>
      <button onClick={reset}
        className="px-5 py-2.5 text-[11px] font-tech-mono tracking-widest border border-slate-600 text-slate-400 hover:text-white transition-all">
        RESET
      </button>
    </div>

    {/* Visualisation SVG */}
    <div className="w-full border border-slate-800/50 bg-[#030810] relative overflow-hidden" style={{ minHeight: totalH + 100 }}>
      <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00E87B]/30 z-10" />
      <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00E87B]/30 z-10" />
      <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00E87B]/30 z-10" />
      <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00E87B]/30 z-10" />
      <svg viewBox={`0 0 400 ${totalH + 80}`} className="w-full" style={{ maxHeight: 450 }}>
        {/* Couches de fluide */}
        {(() => {
          let yAcc = totalH + 40;
          return sortedLayers.map(l => {
            yAcc -= l.height;
            return (
              <g key={l.id}>
                <rect x={colX} y={yAcc} width={colW} height={l.height}
                  fill={l.color} opacity={0.15} stroke={l.color} strokeWidth={0.5} strokeOpacity={0.3} />
                <text x={colX + colW + 10} y={yAcc + l.height / 2 + 4}
                  fill={l.color} fontSize={10} fontFamily="monospace" opacity={0.8}>
                  {l.name} (ρ={l.density})
                </text>
                {/* Densité gauge */}
                <rect x={colX - 20} y={yAcc} width={12} height={l.height}
                  fill={l.color} opacity={0.3} rx={2} />
              </g>
            );
          });
        })()}

        {/* Parois du récipient */}
        <line x1={colX} y1={0} x2={colX} y2={totalH + 40} stroke="#607890" strokeWidth={2} />
        <line x1={colX + colW} y1={0} x2={colX + colW} y2={totalH + 40} stroke="#607890" strokeWidth={2} />
        <line x1={colX} y1={totalH + 40} x2={colX + colW} y2={totalH + 40} stroke="#607890" strokeWidth={2} />

        {/* Objet */}
        <circle
          cx={colX + colW / 2}
          cy={totalH + 40 - animY}
          r={obj.radius}
          fill={obj.color}
          stroke="#fff"
          strokeWidth={0.5}
          strokeOpacity={0.3}
          style={{ transition: dropped ? 'none' : 'cy 0.3s ease' }}
        />
        <text
          x={colX + colW / 2}
          y={totalH + 40 - animY + 4}
          fill="#0D1528"
          fontSize={10}
          fontFamily="monospace"
          fontWeight="bold"
          textAnchor="middle"
        >{obj.emoji}</text>

        {/* Titre */}
        <text x={colX + colW / 2} y={16} fill="#C8D8E8" fontSize={11} fontFamily="monospace" textAnchor="middle" fontWeight="bold">
          COLONNE DE DENSITÉ
        </text>
      </svg>
    </div>

    {/* Résultats */}
    <div className="mt-4 grid grid-cols-1 md:grid-cols-3 gap-3">
      <div className="border border-amber-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-amber-400/70 tracking-widest mb-2">OBJET</div>
        <div className="text-[16px] font-tech-mono text-amber-400 font-bold">{obj.name}</div>
        <div className="text-[12px] font-tech-mono text-slate-500 mt-1">ρ = {objDensity} g/cm³</div>
      </div>
      <div className={`border p-4 ${objDensity > sortedLayers[0]?.density ? 'border-red-900/30 bg-red-950/20' : 'border-green-900/30 bg-green-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">COMPORTEMENT</div>
        <div className="text-[14px] font-tech-mono font-bold" style={{ color: objDensity > sortedLayers[0]?.density ? '#FF4444' : '#00E87B' }}>
          {target.status}
        </div>
      </div>
      <div className="border border-cyan-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">PRINCIPE</div>
        <div className="text-[12px] font-tech-mono text-slate-400 leading-relaxed">
          Un objet monte ou descend jusqu&apos;à trouver un fluide de même densité. Pas besoin de « force gravitationnelle » — la densité relative suffit.
        </div>
      </div>
    </div>

    <div className="mt-4 border border-[#00E87B]/20 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-[#00E87B]/60 mb-2">DENSITÉ VS GRAVITÉ</div>
      <p className="text-[12px] text-[#C8D8E8]/50 font-rajdhani leading-relaxed">
        La « gravité » newtonienne attire tout vers le centre. Mais l&apos;observation montre que les objets s&apos;ordonnent par densité relative :
        le mercure coule sous l&apos;eau, l&apos;huile flotte dessus, l&apos;hélium monte dans l&apos;air.
        Chaque chose trouve son niveau naturel — c&apos;est le principe de flottabilité (Archimède), qui n&apos;a besoin que d&apos;un milieu plus dense en dessous.
      </p>
    </div>

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex flex-wrap items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-500">ARTICLES :</span>
      <a href="/article/la-pression-atmospherique-un-ocean-d-air-invisible" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">L&apos;océan d&apos;air invisible →</a>
      <a href="/article/la-gravite-70-theories-et-aucune-preuve" className="text-[12px] font-tech-mono text-[#00C8FF]/60 hover:text-[#00C8FF]">La gravité : 70 théories →</a>
    </div>
  </div>;
}
