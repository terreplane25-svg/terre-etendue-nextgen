'use client';

import { useState, useMemo, useRef, useEffect } from 'react';
import { CONTINENTS } from './continentData';

// ─── Types ──────────────────────────────────────────
type ProjectionType = 'mercator' | 'azimuthal' | 'equirectangular';

interface GeoPoint {
  lat: number;
  lng: number;
  label: string;
}

interface Route {
  from: GeoPoint;
  to: GeoPoint;
  label: string;
  color: string;
}

// ─── Routes aériennes réelles ───────────────────────
const ROUTES: Route[] = [
  {
    from: { lat: -33.87, lng: 151.21, label: 'Sydney' },
    to: { lat: -33.45, lng: -70.67, label: 'Santiago' },
    label: 'Sydney → Santiago',
    color: '#00C8FF',
  },
  {
    from: { lat: -26.20, lng: 28.04, label: 'Johannesburg' },
    to: { lat: -31.95, lng: 115.86, label: 'Perth' },
    label: 'Johannesburg → Perth',
    color: '#00E87B',
  },
  {
    from: { lat: -34.60, lng: -58.38, label: 'Buenos Aires' },
    to: { lat: -36.85, lng: 174.76, label: 'Auckland' },
    label: 'Buenos Aires → Auckland',
    color: '#D4A843',
  },
  {
    from: { lat: 51.47, lng: -0.46, label: 'Londres' },
    to: { lat: 35.68, lng: 139.69, label: 'Tokyo' },
    label: 'Londres → Tokyo',
    color: '#FF6B6B',
  },
];

// ─── Fonctions de projection ────────────────────────
function toRadians(deg: number): number {
  return (deg * Math.PI) / 180;
}

function mercatorProject(lat: number, lng: number, width: number, height: number): [number, number] {
  const x = ((lng + 180) / 360) * width;
  const latRad = toRadians(Math.max(-85, Math.min(85, lat)));
  const mercN = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
  const y = height / 2 - (mercN * width) / (2 * Math.PI);
  return [x, Math.max(0, Math.min(height, y))];
}

function azimuthalProject(lat: number, lng: number, width: number, height: number): [number, number] {
  const latRad = toRadians(lat);
  const lngRad = toRadians(lng);
  const r = (Math.PI / 2 - latRad) / Math.PI;
  const cx = width / 2;
  const cy = height / 2;
  const maxR = Math.min(width, height) * 0.45;
  const x = cx + Math.sin(lngRad) * r * maxR;
  const y = cy - Math.cos(lngRad) * r * maxR;
  return [x, y];
}

function equirectProject(lat: number, lng: number, width: number, height: number): [number, number] {
  const x = ((lng + 180) / 360) * width;
  const y = ((90 - lat) / 180) * height;
  return [x, y];
}

function project(type: ProjectionType, lat: number, lng: number, w: number, h: number): [number, number] {
  switch (type) {
    case 'mercator': return mercatorProject(lat, lng, w, h);
    case 'azimuthal': return azimuthalProject(lat, lng, w, h);
    case 'equirectangular': return equirectProject(lat, lng, w, h);
  }
}

// ─── Great Circle interpolation ─────────────────────
function interpolateGreatCircle(from: GeoPoint, to: GeoPoint, segments: number = 60): GeoPoint[] {
  const lat1 = toRadians(from.lat);
  const lng1 = toRadians(from.lng);
  const lat2 = toRadians(to.lat);
  const lng2 = toRadians(to.lng);

  const d = 2 * Math.asin(
    Math.sqrt(
      Math.pow(Math.sin((lat2 - lat1) / 2), 2) +
      Math.cos(lat1) * Math.cos(lat2) * Math.pow(Math.sin((lng2 - lng1) / 2), 2)
    )
  );

  if (d < 0.0001) return [from, to];

  const points: GeoPoint[] = [];
  for (let i = 0; i <= segments; i++) {
    const f = i / segments;
    const A = Math.sin((1 - f) * d) / Math.sin(d);
    const B = Math.sin(f * d) / Math.sin(d);
    const x = A * Math.cos(lat1) * Math.cos(lng1) + B * Math.cos(lat2) * Math.cos(lng2);
    const y = A * Math.cos(lat1) * Math.sin(lng1) + B * Math.cos(lat2) * Math.sin(lng2);
    const z = A * Math.sin(lat1) + B * Math.sin(lat2);
    const lat = Math.atan2(z, Math.sqrt(x * x + y * y)) * (180 / Math.PI);
    const lng = Math.atan2(y, x) * (180 / Math.PI);
    points.push({ lat, lng, label: '' });
  }
  return points;
}

// ─── Composant SVG de carte ─────────────────────────
function MapView({ 
  projection, routes, showRoutes, width, height 
}: { 
  projection: ProjectionType; 
  routes: Route[]; 
  showRoutes: boolean;
  width: number; 
  height: number; 
}) {
  // Grille lat/lng
  const gridLines = useMemo(() => {
    const lines: string[] = [];
    for (let lat = -80; lat <= 80; lat += 20) {
      const pts: string[] = [];
      for (let lng = -180; lng <= 180; lng += 3) {
        const [x, y] = project(projection, lat, lng, width, height);
        pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
      }
      lines.push(pts.join(' '));
    }
    for (let lng = -180; lng < 180; lng += 30) {
      const pts: string[] = [];
      for (let lat = -85; lat <= 85; lat += 3) {
        const [x, y] = project(projection, lat, lng, width, height);
        pts.push(`${x.toFixed(1)},${y.toFixed(1)}`);
      }
      lines.push(pts.join(' '));
    }
    return lines;
  }, [projection, width, height]);

  // Continents depuis les données détaillées
  const continentPaths = useMemo(() => {
    return CONTINENTS.flatMap((continent) =>
      continent.paths.map((path) => {
        const pts = path.map(([lng, lat]) => {
          const [x, y] = project(projection, lat, lng, width, height);
          return `${x.toFixed(1)},${y.toFixed(1)}`;
        });
        return pts.join(' ');
      })
    );
  }, [projection, width, height]);

  return (
    <svg 
      viewBox={`0 0 ${width} ${height}`} 
      className="w-full h-auto bg-[#030810]"
      preserveAspectRatio="xMidYMid meet"
    >
      {/* Grille */}
      {gridLines.map((pts, i) => (
        <polyline key={`grid-${i}`} points={pts} fill="none" stroke="#00C8FF" strokeWidth={0.5} opacity={0.06} />
      ))}

      {/* Continents — fill + stroke */}
      {continentPaths.map((pts, i) => (
        <polygon 
          key={`cont-${i}`} 
          points={pts} 
          fill="#0D1528" 
          fillOpacity={0.8}
          stroke="#00C8FF" 
          strokeWidth={0.8} 
          opacity={0.5}
          strokeLinejoin="round"
        />
      ))}

      {/* Routes */}
      {showRoutes && routes.map((route, ri) => {
        const gcPoints = interpolateGreatCircle(route.from, route.to);
        const pathParts: string[][] = [[]];
        let prevX = 0;
        
        gcPoints.forEach((pt) => {
          const [x, y] = project(projection, pt.lat, pt.lng, width, height);
          if (Math.abs(x - prevX) > width * 0.4 && prevX !== 0) {
            pathParts.push([]);
          }
          pathParts[pathParts.length - 1].push(`${x.toFixed(1)},${y.toFixed(1)}`);
          prevX = x;
        });

        const [fx, fy] = project(projection, route.from.lat, route.from.lng, width, height);
        const [tx, ty] = project(projection, route.to.lat, route.to.lng, width, height);

        return (
          <g key={`route-${ri}`}>
            {pathParts.map((part, pi) => (
              <polyline
                key={pi}
                points={part.join(' ')}
                fill="none"
                stroke={route.color}
                strokeWidth={2}
                opacity={0.85}
                strokeLinecap="round"
                strokeLinejoin="round"
              />
            ))}
            <circle cx={fx} cy={fy} r={4} fill={route.color} />
            <circle cx={fx} cy={fy} r={8} fill={route.color} fillOpacity={0.15} />
            <text x={fx + 10} y={fy + 4} fill={route.color} fontSize={10} fontFamily="monospace" opacity={0.9}>{route.from.label}</text>
            <circle cx={tx} cy={ty} r={4} fill={route.color} />
            <circle cx={tx} cy={ty} r={8} fill={route.color} fillOpacity={0.15} />
            <text x={tx + 10} y={ty + 4} fill={route.color} fontSize={10} fontFamily="monospace" opacity={0.9}>{route.to.label}</text>
          </g>
        );
      })}

      {/* Projection label */}
      <text x={12} y={20} fill="#C8D8E8" fillOpacity={0.35} fontSize={11} fontFamily="monospace" letterSpacing="0.1em">
        {projection === 'mercator' ? 'MERCATOR (1569)' : projection === 'azimuthal' ? 'AZIMUTALE ÉQUIDISTANTE' : 'ÉQUIRECTANGULAIRE'}
      </text>
    </svg>
  );
}

// ─── Composant Principal ────────────────────────────
export default function ProjectionSim() {
  const [projection, setProjection] = useState<ProjectionType>('mercator');
  const [showRoutes, setShowRoutes] = useState(true);
  const [selectedRoutes, setSelectedRoutes] = useState<Set<number>>(new Set([0, 1, 2, 3]));

  const activeRoutes = ROUTES.filter((_, i) => selectedRoutes.has(i));

  const toggleRoute = (i: number) => {
    setSelectedRoutes(prev => {
      const next = new Set(prev);
      if (next.has(i)) next.delete(i);
      else next.add(i);
      return next;
    });
  };

  const svgW = 900;
  const svgH = projection === 'azimuthal' ? 700 : 500;

  return (
    <div className="w-full">
      {/* Sélection de projection */}
      <div className="flex flex-wrap items-center gap-2 mb-4">
        {([
          { id: 'mercator' as const, label: 'MERCATOR' },
          { id: 'azimuthal' as const, label: 'AZIMUTALE ÉQ.' },
          { id: 'equirectangular' as const, label: 'ÉQUIRECT.' },
        ]).map((p) => (
          <button
            key={p.id}
            onClick={() => setProjection(p.id)}
            className={`px-4 py-2 text-[9px] font-orbitron tracking-widest border transition-all ${
              projection === p.id
                ? 'border-[#00C8FF]/60 bg-[#00C8FF]/10 text-[#00C8FF]'
                : 'border-slate-700 text-slate-500 hover:border-slate-500'
            }`}
            style={{ clipPath: 'polygon(6px 0, 100% 0, calc(100% - 6px) 100%, 0 100%)' }}
          >
            {p.label}
          </button>
        ))}

        <button
          onClick={() => setShowRoutes(!showRoutes)}
          className={`ml-auto px-3 py-1 text-[8px] font-tech-mono border transition-all ${
            showRoutes ? 'border-slate-600 text-slate-400' : 'border-slate-800 text-slate-600'
          }`}
        >
          ROUTES: {showRoutes ? 'ON' : 'OFF'}
        </button>
      </div>

      {/* Sélection de routes */}
      {showRoutes && (
        <div className="flex flex-wrap gap-2 mb-4">
          {ROUTES.map((r, i) => (
            <button
              key={i}
              onClick={() => toggleRoute(i)}
              className={`px-3 py-1 text-[8px] font-tech-mono border transition-all ${
                selectedRoutes.has(i)
                  ? ''
                  : 'border-slate-800 text-slate-600 opacity-40'
              }`}
              style={{
                borderColor: selectedRoutes.has(i) ? r.color : undefined,
                color: selectedRoutes.has(i) ? r.color : undefined,
                backgroundColor: selectedRoutes.has(i) ? `${r.color}15` : undefined,
              }}
            >
              {r.label}
            </button>
          ))}
        </div>
      )}

      {/* Carte */}
      <div className="w-full border border-slate-800/50 relative overflow-hidden">
        <div className="absolute top-0 left-0 w-4 h-4 border-t border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute top-0 right-0 w-4 h-4 border-t border-r border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 left-0 w-4 h-4 border-b border-l border-[#00C8FF]/30 z-10" />
        <div className="absolute bottom-0 right-0 w-4 h-4 border-b border-r border-[#00C8FF]/30 z-10" />

        <MapView
          projection={projection}
          routes={activeRoutes}
          showRoutes={showRoutes}
          width={svgW}
          height={svgH}
        />
      </div>

      {/* Infos */}
      <div className="mt-4 border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[9px] font-tech-mono text-[#00C8FF]/40 tracking-widest mb-2">
          ANALYSE // DISTORSIONS DE PROJECTION
        </div>
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          {projection === 'mercator' && "La projection de Mercator (1569) conserve les angles mais déforme les aires : le Groenland paraît aussi grand que l\u2019Afrique (×14 en réalité). Les routes great-circle apparaissent courbes — ce qui trompe sur les distances réelles."}
          {projection === 'azimuthal' && "La projection azimutale équidistante, centrée sur le pôle Nord, préserve les distances depuis le centre. C\u2019est la projection utilisée par le logo de l\u2019ONU et par l\u2019OACI pour la navigation polaire. Les routes aériennes y apparaissent différemment qu\u2019en Mercator."}
          {projection === 'equirectangular' && "La projection équirectangulaire est la plus simple (latitude/longitude → x/y). Elle ne conserve ni les angles ni les aires, mais rend visible la vraie répartition des masses continentales."}
        </p>
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLE LIÉ :</span>
          <a href="/article/cartes-routes-boussoles-et-le-mystere-antarctique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">Cartes, routes, boussoles →</a>
        </div>
      </div>
    </div>
  );
}
