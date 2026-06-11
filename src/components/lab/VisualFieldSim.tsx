'use client';
import { useState, useMemo } from 'react';

function arcMin(heightM: number, distM: number): number {
  if (distM <= 0) return Infinity;
  return Math.atan2(heightM, distM) * (180 / Math.PI) * 60;
}

function maxVisibleDist(heightM: number, limitArcMin: number): number {
  return heightM / Math.tan((limitArcMin / 60) * (Math.PI / 180));
}

const EYE_LIMIT = 1.0;

/** Critère de Rayleigh : θ_min = 1.22·λ/D (λ = 550 nm), converti en arc-minutes. */
function rayleighArcMin(apertureMm: number): number {
  const thetaRad = 1.22 * 550e-9 / (apertureMm / 1000);
  return thetaRad * (180 / Math.PI) * 60;
}

const INSTRUMENTS = [
  // L'œil : Rayleigh donne ~0.46' pour 5 mm, mais l'acuité pratique est ~1'
  { id: 'eye', label: 'Œil nu', aperture: 5, limit: EYE_LIMIT, zoom: 1 },
  { id: 'binos', label: 'Jumelles 10×50', aperture: 50, limit: rayleighArcMin(50), zoom: 10 },
  { id: 'p1000', label: 'Nikon P1000 (125×)', aperture: 70, limit: rayleighArcMin(70), zoom: 125 },
  { id: 'scope', label: 'Télescope 150 mm', aperture: 150, limit: rayleighArcMin(150), zoom: 75 },
];

const PRESETS = [
  { label: 'Personne (1.7 m) — 5 km', h: 1.7, d: 5000 },
  { label: 'Bateau (10 m) — 20 km', h: 10, d: 20000 },
  { label: 'Tour (100 m) — 50 km', h: 100, d: 50000 },
  { label: 'Gratte-ciel (400 m) — 100 km', h: 400, d: 100000 },
  { label: 'Montagne (3000 m) — 200 km', h: 3000, d: 200000 },
  { label: 'Étoile (?) — 3×10⁸ km', h: 1.4e9, d: 3e11 },
];

function EyeDiagram({ angSize, limit }: { angSize: number; limit: number }) {
  const W = 400, H = 180;
  const cx = 60, cy = H / 2;
  const fovDeg = Math.min(angSize * 2, 60);
  const fovRad = (fovDeg / 2) * (Math.PI / 180) * 20;
  const limitRad = (limit / 60) * (Math.PI / 180) * 20;
  const rayLen = 300;

  const visible = angSize >= limit;
  const col = visible ? '#00E87B' : '#FF4444';

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 180 }}>
      <rect width={W} height={H} fill="#050A12" rx={8} />
      {/* Œil */}
      <ellipse cx={cx} cy={cy} rx={18} ry={22} fill="none" stroke="#C8D8E8" strokeWidth={1.5} />
      <circle cx={cx} cy={cy} r={8} fill="#4488CC" />
      <circle cx={cx} cy={cy} r={3} fill="#0D1528" />
      {/* Rayons lumineux */}
      <line x1={cx + 18} y1={cy} x2={cx + rayLen} y2={cy - Math.sin(fovRad) * rayLen * 0.3}
        stroke={col} strokeWidth={1.5} opacity={0.6} />
      <line x1={cx + 18} y1={cy} x2={cx + rayLen} y2={cy + Math.sin(fovRad) * rayLen * 0.3}
        stroke={col} strokeWidth={1.5} opacity={0.6} />
      {/* Zone de résolution */}
      <line x1={cx + 18} y1={cy - Math.sin(limitRad) * rayLen * 0.3} x2={cx + rayLen} y2={cy - Math.sin(limitRad) * rayLen * 0.3}
        stroke="#D4A843" strokeWidth={0.5} strokeDasharray="4,3" opacity={0.5} />
      <line x1={cx + 18} y1={cy + Math.sin(limitRad) * rayLen * 0.3} x2={cx + rayLen} y2={cy + Math.sin(limitRad) * rayLen * 0.3}
        stroke="#D4A843" strokeWidth={0.5} strokeDasharray="4,3" opacity={0.5} />
      {/* Objet */}
      <line x1={cx + rayLen - 10} y1={cy - Math.sin(fovRad) * rayLen * 0.3}
        x2={cx + rayLen - 10} y2={cy + Math.sin(fovRad) * rayLen * 0.3}
        stroke={col} strokeWidth={3} />
      {/* Labels */}
      <text x={cx} y={cy + 40} fill="#C8D8E8" fontSize={9} fontFamily="monospace" textAnchor="middle">Œil</text>
      <text x={cx + rayLen - 10} y={cy + 40} fill={col} fontSize={9} fontFamily="monospace" textAnchor="middle">Objet</text>
      <text x={W - 10} y={cy - 8} fill="#D4A843" fontSize={8} fontFamily="monospace" textAnchor="end">seuil 1&apos;</text>
      {/* Taille angulaire */}
      <text x={cx + rayLen / 2} y={20} fill={col} fontSize={11} fontFamily="monospace" textAnchor="middle" fontWeight="bold">
        {angSize > 1000 ? `${(angSize / 60).toFixed(1)}°` : `${angSize.toFixed(2)}'`}
        {visible ? ' — RÉSOLU' : ' — NON RÉSOLU'}
      </text>
    </svg>
  );
}

function ResolutionGraph({ heightM, instLimit }: { heightM: number; instLimit: number }) {
  const W = 500, H = 160, PAD = 50;
  const maxDist = maxVisibleDist(heightM, Math.min(EYE_LIMIT, instLimit)) * 1.5;
  if (!isFinite(maxDist) || maxDist <= 0) return null;
  const steps = 100;

  const points = useMemo(() => {
    const pts: { x: number; y: number; d: number; a: number }[] = [];
    let maxA = 0;
    for (let i = 1; i <= steps; i++) {
      const d = (i / steps) * maxDist;
      const a = arcMin(heightM, d);
      if (a > maxA) maxA = a;
      pts.push({ x: 0, y: 0, d, a });
    }
    maxA = Math.max(maxA, EYE_LIMIT * 3);
    for (const p of pts) {
      p.x = PAD + (p.d / maxDist) * (W - PAD * 2);
      p.y = H - PAD - (Math.min(p.a, maxA) / maxA) * (H - PAD * 2);
    }
    return { pts, maxA, maxDist };
  }, [heightM, maxDist]);

  const pathD = points.pts.map((p, i) => `${i === 0 ? 'M' : 'L'}${p.x},${p.y}`).join(' ');
  const limitY = H - PAD - (EYE_LIMIT / points.maxA) * (H - PAD * 2);
  const instY = H - PAD - (instLimit / points.maxA) * (H - PAD * 2);
  const showInstLine = instLimit < EYE_LIMIT;

  return (
    <svg viewBox={`0 0 ${W} ${H}`} className="w-full" style={{ maxHeight: 160 }}>
      <rect x={PAD} y={4} width={W - PAD * 2} height={H - PAD - 4} fill="#050A12" rx={4} />
      {/* Seuil œil 1' */}
      <line x1={PAD} y1={limitY} x2={W - PAD} y2={limitY}
        stroke="#D4A843" strokeWidth={1} strokeDasharray="4,3" opacity={0.6} />
      <text x={W - PAD + 4} y={limitY + 3} fill="#D4A843" fontSize={8} fontFamily="monospace">œil 1&apos;</text>
      {/* Seuil instrument (Rayleigh) */}
      {showInstLine && <>
        <line x1={PAD} y1={instY} x2={W - PAD} y2={instY}
          stroke="#00E87B" strokeWidth={1} strokeDasharray="4,3" opacity={0.6} />
        <text x={W - PAD + 4} y={instY + 3} fill="#00E87B" fontSize={8} fontFamily="monospace">instr.</text>
      </>}
      {/* Courbe */}
      <path d={pathD} fill="none" stroke="#00C8FF" strokeWidth={2} />
      {/* Remplissage sous le seuil = zone invisible */}
      <clipPath id="below-limit">
        <rect x={PAD} y={limitY} width={W - PAD * 2} height={H - PAD - limitY} />
      </clipPath>
      <path d={pathD + ` L${W - PAD},${H - PAD} L${PAD},${H - PAD} Z`} fill="#FF4444" opacity={0.08} clipPath="url(#below-limit)" />
      {/* Axes */}
      <line x1={PAD} y1={H - PAD} x2={W - PAD} y2={H - PAD} stroke="#607890" strokeWidth={1} />
      <line x1={PAD} y1={4} x2={PAD} y2={H - PAD} stroke="#607890" strokeWidth={1} />
      <text x={W / 2} y={H - 4} fill="#607890" fontSize={9} fontFamily="monospace" textAnchor="middle">Distance</text>
      <text x={8} y={H / 2} fill="#607890" fontSize={9} fontFamily="monospace" textAnchor="middle" transform={`rotate(-90,8,${H / 2})`}>Arc-min</text>
      <text x={PAD} y={H - PAD + 12} fill="#607890" fontSize={8} fontFamily="monospace" textAnchor="middle">0</text>
      <text x={W - PAD} y={H - PAD + 12} fill="#607890" fontSize={8} fontFamily="monospace" textAnchor="middle">
        {maxDist >= 1000 ? `${(maxDist / 1000).toFixed(0)} km` : `${maxDist.toFixed(0)} m`}
      </text>
    </svg>
  );
}

export default function VisualFieldSim() {
  const [heightM, setHeightM] = useState(10);
  const [distM, setDistM] = useState(20000);
  const [instrument, setInstrument] = useState(0);

  const inst = INSTRUMENTS[instrument];
  const angSz = arcMin(heightM, distM);
  const maxVisDist = maxVisibleDist(heightM, inst.limit);
  const maxVisDistEye = maxVisibleDist(heightM, EYE_LIMIT);
  const visible = angSz >= inst.limit;
  const visibleEye = angSz >= EYE_LIMIT;
  // Récupérable au zoom : invisible à l'œil nu, mais résolu par l'instrument
  const recoverable = !visibleEye && visible && instrument > 0;
  const distKm = distM / 1000;

  return <div className="w-full">
    <div className="grid grid-cols-1 md:grid-cols-2 gap-4 mb-4">
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">HAUTEUR DE L&apos;OBJET</label>
        <div className="flex items-center gap-3">
          <input type="range" min={0.1} max={5000} step={0.1} value={heightM}
            onChange={e => setHeightM(+e.target.value)} className="flex-1 accent-[#00E87B] h-2" />
          <input type="number" min={0.1} max={50000} step={0.1} value={heightM}
            onChange={e => { const v = +e.target.value; if (!isNaN(v) && v > 0) setHeightM(v); }}
            className="w-24 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#00E87B] px-3 py-2 text-right rounded-none" />
          <span className="text-[12px] font-tech-mono text-slate-500">m</span>
        </div>
      </div>
      <div className="border border-slate-800/50 bg-[#0A1020] p-4">
        <label className="text-[11px] font-tech-mono text-slate-400 tracking-widest block mb-2">DISTANCE</label>
        <div className="flex items-center gap-3">
          <input type="range" min={100} max={500000} step={100} value={distM}
            onChange={e => setDistM(+e.target.value)} className="flex-1 accent-[#00C8FF] h-2" />
          <input type="number" min={100} max={5000000} step={100} value={distM}
            onChange={e => { const v = +e.target.value; if (!isNaN(v) && v > 0) setDistM(v); }}
            className="w-24 bg-[#050A12] border border-slate-600 text-[14px] font-tech-mono text-[#00C8FF] px-3 py-2 text-right rounded-none" />
          <span className="text-[12px] font-tech-mono text-slate-500">m</span>
        </div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">= {distKm.toFixed(1)} km</div>
      </div>
    </div>

    {/* Presets */}
    <div className="mb-4 grid grid-cols-2 md:grid-cols-3 gap-2">
      {PRESETS.map(p => (
        <button key={p.label} onClick={() => { setHeightM(p.h); setDistM(p.d); }}
          className="border border-slate-700 bg-[#0A1020] p-3 text-left hover:border-[#C45E6A]/50 transition-all group">
          <div className="text-[11px] font-tech-mono text-slate-200 group-hover:text-[#C45E6A] font-bold">{p.label}</div>
        </button>
      ))}
    </div>

    {/* Instrument optique */}
    <div className="mb-4 border border-[#00E87B]/20 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-[#00E87B]/70 tracking-widest mb-3">INSTRUMENT — critère de Rayleigh θ = 1.22·λ/D</div>
      <div className="flex flex-wrap gap-2">
        {INSTRUMENTS.map((ins, i) => (
          <button key={ins.id} onClick={() => setInstrument(i)}
            className="px-4 py-2 text-[10px] font-tech-mono border transition-all"
            style={{
              borderColor: i === instrument ? '#00E87B99' : '#334155',
              backgroundColor: i === instrument ? '#00E87B1a' : 'transparent',
              color: i === instrument ? '#00E87B' : '#64748b',
            }}>
            {ins.label}
            <span className="block text-[8px] opacity-60">
              D = {ins.aperture} mm · θ = {ins.limit >= 1 ? `${ins.limit.toFixed(1)}'` : `${(ins.limit * 60).toFixed(2)}"`}
            </span>
          </button>
        ))}
      </div>
      {recoverable && (
        <div className="mt-3 px-3 py-2 border border-[#00E87B]/40 bg-[#00E87B]/10 text-[11px] font-tech-mono text-[#00E87B]">
          ✓ RÉCUPÉRABLE AU ZOOM — l&apos;objet ({angSz.toFixed(3)}&apos;) est sous le seuil de l&apos;œil (1&apos;) mais au-dessus
          de celui de {inst.label}. La disparition était angulaire, pas physique : un objet caché par une courbure
          réelle ne reviendrait avec aucun zoom.
        </div>
      )}
    </div>

    {/* Diagramme œil */}
    <div className="mb-4 border border-slate-800/50 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-slate-400 tracking-widest mb-3">
        RÉSOLUTION — {inst.label.toUpperCase()}
      </div>
      <EyeDiagram angSize={angSz} limit={inst.limit} />
    </div>

    {/* Graphique résolution vs distance */}
    <div className="mb-4 border border-slate-800/50 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-slate-400 tracking-widest mb-3">TAILLE ANGULAIRE VS DISTANCE</div>
      <ResolutionGraph heightM={heightM} instLimit={inst.limit} />
      <div className="flex items-center gap-4 mt-2">
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-[#00C8FF]" />
          <span className="text-[9px] font-tech-mono text-slate-500">taille angulaire</span>
        </div>
        <div className="flex items-center gap-2">
          <div className="w-4 h-0.5 bg-[#D4A843] opacity-60" style={{ borderTop: '1px dashed #D4A843' }} />
          <span className="text-[9px] font-tech-mono text-slate-500">seuil œil (1&apos;)</span>
        </div>
        {inst.limit < EYE_LIMIT && (
          <div className="flex items-center gap-2">
            <div className="w-4 h-0.5 bg-[#00E87B] opacity-60" style={{ borderTop: '1px dashed #00E87B' }} />
            <span className="text-[9px] font-tech-mono text-slate-500">seuil {inst.label}</span>
          </div>
        )}
        <div className="flex items-center gap-2">
          <div className="w-3 h-3 bg-[#FF4444] opacity-15" />
          <span className="text-[9px] font-tech-mono text-slate-500">zone invisible</span>
        </div>
      </div>
    </div>

    {/* Résultats */}
    <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
      <div className="border border-cyan-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-cyan-400/70 tracking-widest mb-2">TAILLE ANGULAIRE</div>
        <div className="text-[20px] font-tech-mono text-cyan-400 font-bold">
          {angSz > 60 ? `${(angSz / 60).toFixed(2)}°` : `${angSz.toFixed(2)}'`}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">
          {angSz.toFixed(4)} arc-minutes
        </div>
      </div>
      <div className="border border-amber-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-amber-400/70 tracking-widest mb-2">DISTANCE MAX ({inst.label.toUpperCase()})</div>
        <div className="text-[20px] font-tech-mono text-amber-400 font-bold">
          {maxVisDist >= 1000 ? `${(maxVisDist / 1000).toFixed(1)} km` : `${maxVisDist.toFixed(0)} m`}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-600 mt-1">
          {instrument > 0
            ? `œil nu : ${maxVisDistEye >= 1000 ? `${(maxVisDistEye / 1000).toFixed(1)} km` : `${maxVisDistEye.toFixed(0)} m`}`
            : `pour un objet de ${heightM} m`}
        </div>
      </div>
      <div className={`border p-4 ${recoverable ? 'border-green-900/30 bg-green-950/20' : visible ? 'border-green-900/30 bg-green-950/20' : 'border-red-900/30 bg-red-950/20'}`}>
        <div className="text-[11px] font-tech-mono text-slate-400/70 tracking-widest mb-2">VERDICT</div>
        <div className={`text-[18px] font-tech-mono font-bold ${visible ? 'text-green-400' : 'text-red-400'}`}>
          {recoverable ? '✓ ZOOM RÉCUPÈRE' : visible ? '✓ RÉSOLU' : '✗ NON RÉSOLU'}
        </div>
        <div className="text-[10px] font-tech-mono text-slate-500 mt-1">
          seuil : {inst.limit >= 1 ? `${inst.limit.toFixed(1)}'` : `${(inst.limit * 60).toFixed(2)}"`} (Rayleigh)
        </div>
      </div>
      <div className="border border-purple-900/30 bg-[#0A1020] p-4">
        <div className="text-[11px] font-tech-mono text-purple-400/70 tracking-widest mb-2">COMPARAISON</div>
        <div className="text-[12px] font-tech-mono text-slate-400 leading-relaxed">
          {angSz >= 30 ? 'Gros comme la Lune dans le ciel' :
           angSz >= 1 ? 'Visible mais petit' :
           angSz >= 0.1 ? 'Nécessite des jumelles' :
           'Nécessite un télescope'}
        </div>
      </div>
    </div>

    <div className="mt-4 border border-[#C45E6A]/20 bg-[#0A1020] p-4">
      <div className="text-[11px] font-tech-mono text-[#C45E6A]/60 mb-2">LA RÉSOLUTION ANGULAIRE</div>
      <p className="text-[12px] text-[#C8D8E8]/80 font-rajdhani leading-relaxed">
        L&apos;œil humain a une résolution d&apos;environ 1 arc-minute (1/60°). Un objet dont la taille angulaire passe sous ce seuil
        devient invisible — non pas parce qu&apos;il « disparaît derrière la courbure », mais parce que l&apos;œil ne peut plus le résoudre.
        C&apos;est la limite de diffraction de la pupille (~2-5 mm). Un zoom optique (jumelles, télescope) réduit le seuil et ramène l&apos;objet en vue.
        Si l&apos;objet avait disparu derrière une courbure physique, aucun zoom ne pourrait le ramener.
      </p>
    </div>

    <div className="mt-4 border-t border-slate-800/30 pt-4 flex flex-wrap items-center gap-5">
      <span className="text-[11px] font-tech-mono text-slate-400">ARTICLES :</span>
      <a href="/article/loeil-humain-la-machine-a-voir-qui-faconne-notre-realite" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;œil humain →</a>
      <a href="/article/lhypothese-nulle-dynamique-et-cinematique" className="text-[12px] font-tech-mono text-[#00C8FF] hover:text-[#40E0FF]">L&apos;hypothèse nulle →</a>
    </div>
  </div>;
}
