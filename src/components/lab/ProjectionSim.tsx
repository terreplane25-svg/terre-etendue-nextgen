'use client';

import { useState, useMemo } from 'react';

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
  const latRad = toRadians(lat);
  const mercN = Math.log(Math.tan(Math.PI / 4 + latRad / 2));
  const y = height / 2 - (mercN * width) / (2 * Math.PI);
  return [x, Math.max(0, Math.min(height, y))];
}

function azimuthalProject(lat: number, lng: number, width: number, height: number): [number, number] {
  // Azimutale équidistante centrée sur le pôle Nord
  const latRad = toRadians(lat);
  const lngRad = toRadians(lng);
  const r = (Math.PI / 2 - latRad) / Math.PI; // 0 au pôle, 1 à l'équateur
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

// ─── Génération de la route (great circle interpolé) ─
function interpolateGreatCircle(from: GeoPoint, to: GeoPoint, segments: number = 50): GeoPoint[] {
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
  // Grille de latitude/longitude
  const gridLines = useMemo(() => {
    const lines: string[] = [];
    // Latitudes
    for (let lat = -80; lat <= 80; lat += 20) {
      const pts: string[] = [];
      for (let lng = -180; lng <= 180; lng += 5) {
        const [x, y] = project(projection, lat, lng, width, height);
        pts.push(`${x},${y}`);
      }
      lines.push(pts.join(' '));
    }
    // Longitudes
    for (let lng = -180; lng < 180; lng += 30) {
      const pts: string[] = [];
      for (let lat = -80; lat <= 80; lat += 5) {
        const [x, y] = project(projection, lat, lng, width, height);
        pts.push(`${x},${y}`);
      }
      lines.push(pts.join(' '));
    }
    return lines;
  }, [projection, width, height]);

  // Contours continentaux simplifiés (points clés)
  const continentOutlines = useMemo(() => {
    // Points simplifiés des continents principaux
    const continents: { points: [number, number][]; name: string }[] = [
      { name: 'Afrique', points: [[-5,37],[10,32],[32,31],[42,12],[50,2],[40,-15],[35,-34],[18,-35],[12,-17],[8,5],[-17,15],[-5,37]] },
      { name: 'Europe', points: [[-10,36],[0,43],[5,47],[15,54],[30,60],[40,55],[28,41],[20,38],[0,36],[-10,36]] },
      { name: 'Asie', points: [[30,60],[50,55],[70,55],[90,45],[100,35],[120,30],[140,35],[145,45],[160,60],[180,65],[170,55],[130,50],[105,20],[80,8],[65,25],[40,55],[30,60]] },
      { name: 'AmériqueN', points: [[-170,65],[-140,60],[-125,50],[-120,35],[-105,25],[-90,18],[-85,10],[-80,25],[-75,45],[-60,50],[-55,48],[-65,60],[-95,70],[-170,65]] },
      { name: 'AmériqueS', points: [[-80,10],[-75,0],[-70,-15],[-68,-23],[-65,-55],[-72,-50],[-75,-40],[-80,-5],[-80,10]] },
      { name: 'Australie', points: [[115,-35],[130,-15],[145,-15],[153,-28],[150,-38],[130,-35],[115,-35]] },
    ];

    return continents.map((c) => {
      const pts = c.points.map(([lng, lat]) => {
        const [x, y] = project(projection, lat, lng, width, height);
        return `${x},${y}`;
      });
      return pts.join(' ');
    });
  }, [projection, width, height]);

  return (
    <svg width={width} height={height} className="bg-[#030810]">
      {/* Grille */}
      {gridLines.map((pts, i) => (
        <polyline key={`grid-${i}`} points={pts} fill="none" stroke="#00C8FF" strokeWidth={0.5} opacity={0.08} />
      ))}

      {/* Continents */}
      {continentOutlines.map((pts, i) => (
        <polyline key={`cont-${i}`} points={pts} fill="#0D1528" stroke="#00C8FF" strokeWidth={1} opacity={0.3} />
      ))}

      {/* Routes */}
      {showRoutes && routes.map((route, ri) => {
        const gcPoints = interpolateGreatCircle(route.from, route.to);
        const pathParts: string[][] = [[]];
        let prevX = 0;
        
        gcPoints.forEach((pt) => {
          const [x, y] = project(projection, pt.lat, pt.lng, width, height);
          // Détecter les sauts de bord (wrapping)
          if (Math.abs(x - prevX) > width * 0.5 && prevX !== 0) {
            pathParts.push([]);
          }
          pathParts[pathParts.length - 1].push(`${x},${y}`);
          prevX = x;
        });

        return (
          <g key={`route-${ri}`}>
            {pathParts.map((part, pi) => (
              <polyline
                key={pi}
                points={part.join(' ')}
                fill="none"
                stroke={route.color}
                strokeWidth={2}
                opacity={0.8}
                strokeLinecap="round"
              />
            ))}
            {/* Labels */}
            {(() => {
              const [fx, fy] = project(projection, route.from.lat, route.from.lng, width, height);
              const [tx, ty] = project(projection, route.to.lat, route.to.lng, width, height);
              return (
                <>
                  <circle cx={fx} cy={fy} r={4} fill={route.color} />
                  <text x={fx + 8} y={fy + 3} fill={route.color} fontSize={9} fontFamily="monospace">{route.from.label}</text>
                  <circle cx={tx} cy={ty} r={4} fill={route.color} />
                  <text x={tx + 8} y={ty + 3} fill={route.color} fontSize={9} fontFamily="monospace">{route.to.label}</text>
                </>
              );
            })()}
          </g>
        );
      })}

      {/* Projection label */}
      <text x={10} y={20} fill="#C8D8E8" fillOpacity={0.3} fontSize={10} fontFamily="monospace">
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
                  ? 'border-opacity-60 bg-opacity-10'
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
          width={800}
          height={projection === 'azimuthal' ? 600 : 450}
        />
      </div>

      {/* Infos */}
      <div className="mt-4 border border-slate-800/50 bg-[#0A1020] p-4">
        <div className="text-[9px] font-tech-mono text-[#00C8FF]/40 tracking-widest mb-2">
          ANALYSE // DISTORSIONS DE PROJECTION
        </div>
        <p className="text-[13px] text-[#C8D8E8]/60 font-rajdhani leading-relaxed">
          {projection === 'mercator' && "La projection de Mercator (1569) conserve les angles mais déforme les aires : le Groenland paraît aussi grand que l'Afrique (x14 en réalité). Les routes great-circle apparaissent courbes — ce qui trompe sur les distances réelles."}
          {projection === 'azimuthal' && "La projection azimutale équidistante, centrée sur le pôle Nord, préserve les distances depuis le centre. C'est la projection utilisée par le logo de l'ONU et par l'OACI pour la navigation polaire. Les routes aériennes y apparaissent plus rectilignes qu'en Mercator."}
          {projection === 'equirectangular' && "La projection équirectangulaire est la plus simple (latitude/longitude → x/y). Elle ne conserve ni les angles ni les aires, mais rend visible la vraie répartition des masses continentales. Les routes great-circle y sont courbées."}
        </p>
        <div className="flex items-center gap-4 mt-3 pt-3 border-t border-slate-800/30">
          <span className="text-[8px] font-tech-mono text-slate-600">ARTICLE LIÉ :</span>
          <a href="/article/cartes-routes-boussoles-et-le-mystere-antarctique" className="text-[9px] font-tech-mono text-[#00C8FF]/50 hover:text-[#00C8FF] transition-colors">Cartes, routes, boussoles →</a>
        </div>
      </div>
    </div>
  );
}
