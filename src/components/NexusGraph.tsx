'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { motion } from 'framer-motion';

// ─── Types ────────────────────────────────────────
interface NexusNode {
  id: string;
  label: string;
  category: 'headquarters' | 'observatory' | 'library' | 'lab';
  x: number;
  y: number;
  vx: number;
  vy: number;
}

interface NexusEdge {
  source: string;
  target: string;
  strength: number; // 0–1
}

// ─── Données du graphe ────────────────────────────
const NODES: Omit<NexusNode, 'x' | 'y' | 'vx' | 'vy'>[] = [
  { id: 'tawhid-geo', label: 'Géométrie du Tawhid', category: 'library' },
  { id: 'singularite', label: 'Singularité Quantique', category: 'lab' },
  { id: 'geodesique-terre', label: 'Géodésiques Terrestres', category: 'observatory' },
  { id: 'epistemologie-islam', label: 'Épistémologie Islamique', category: 'headquarters' },
  { id: 'fractales-coran', label: 'Fractales Coraniques', category: 'library' },
  { id: 'modele-orbital', label: 'Modèle Orbital', category: 'lab' },
  { id: 'observations-terrain', label: 'Observations de Terrain', category: 'observatory' },
  { id: 'kalaam-moderne', label: 'Kalâm Moderne', category: 'headquarters' },
  { id: 'topologie-sacree', label: 'Topologie Sacrée', category: 'library' },
  { id: 'constantes-physiques', label: 'Constantes Physiques', category: 'lab' },
  { id: 'isnads-network', label: 'Réseau des Isnâds', category: 'library' },
  { id: 'courbure-espace', label: "Courbure de l'Espace", category: 'observatory' },
];

const EDGES: NexusEdge[] = [
  { source: 'tawhid-geo', target: 'singularite', strength: 0.9 },
  { source: 'tawhid-geo', target: 'fractales-coran', strength: 0.8 },
  { source: 'tawhid-geo', target: 'epistemologie-islam', strength: 0.7 },
  { source: 'singularite', target: 'modele-orbital', strength: 0.85 },
  { source: 'singularite', target: 'constantes-physiques', strength: 0.7 },
  { source: 'geodesique-terre', target: 'observations-terrain', strength: 0.9 },
  { source: 'geodesique-terre', target: 'courbure-espace', strength: 0.8 },
  { source: 'epistemologie-islam', target: 'kalaam-moderne', strength: 0.9 },
  { source: 'epistemologie-islam', target: 'topologie-sacree', strength: 0.6 },
  { source: 'fractales-coran', target: 'topologie-sacree', strength: 0.75 },
  { source: 'fractales-coran', target: 'isnads-network', strength: 0.5 },
  { source: 'modele-orbital', target: 'geodesique-terre', strength: 0.6 },
  { source: 'kalaam-moderne', target: 'singularite', strength: 0.55 },
  { source: 'constantes-physiques', target: 'courbure-espace', strength: 0.7 },
  { source: 'isnads-network', target: 'epistemologie-islam', strength: 0.65 },
  { source: 'topologie-sacree', target: 'courbure-espace', strength: 0.5 },
];

const CATEGORY_COLORS: Record<string, string> = {
  headquarters: '#00D1FF',
  observatory: '#00D1FF',
  library: '#D4AF37',
  lab: '#D4AF37',
};

const CATEGORY_LABELS: Record<string, string> = {
  headquarters: '🧠 Q.G.',
  observatory: '🔭 Observatoire',
  library: '📚 Bibliothèque',
  lab: '⚗️ Lab',
};

// ─── Simulation de forces simple (pas de D3) ─────
function initNodes(width: number, height: number): NexusNode[] {
  return NODES.map((n, i) => ({
    ...n,
    x: width / 2 + Math.cos((i / NODES.length) * Math.PI * 2) * Math.min(width, height) * 0.3,
    y: height / 2 + Math.sin((i / NODES.length) * Math.PI * 2) * Math.min(width, height) * 0.3,
    vx: 0,
    vy: 0,
  }));
}

function simulate(nodes: NexusNode[], edges: NexusEdge[], width: number, height: number) {
  const nodeMap = new Map(nodes.map((n) => [n.id, n]));
  const cx = width / 2;
  const cy = height / 2;

  // Répulsion entre nœuds
  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i];
      const b = nodes[j];
      let dx = b.x - a.x;
      let dy = b.y - a.y;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = 800 / (dist * dist);
      dx = (dx / dist) * force;
      dy = (dy / dist) * force;
      a.vx -= dx;
      a.vy -= dy;
      b.vx += dx;
      b.vy += dy;
    }
  }

  // Attraction sur les arêtes
  for (const edge of edges) {
    const a = nodeMap.get(edge.source);
    const b = nodeMap.get(edge.target);
    if (!a || !b) continue;
    const dx = b.x - a.x;
    const dy = b.y - a.y;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const force = (dist - 120) * 0.005 * edge.strength;
    const fx = (dx / dist) * force;
    const fy = (dy / dist) * force;
    a.vx += fx;
    a.vy += fy;
    b.vx -= fx;
    b.vy -= fy;
  }

  // Gravité vers le centre
  for (const n of nodes) {
    n.vx += (cx - n.x) * 0.002;
    n.vy += (cy - n.y) * 0.002;
  }

  // Appliquer vitesse avec friction
  for (const n of nodes) {
    n.vx *= 0.85;
    n.vy *= 0.85;
    n.x += n.vx;
    n.y += n.vy;
    // Contraindre aux bords
    n.x = Math.max(60, Math.min(width - 60, n.x));
    n.y = Math.max(40, Math.min(height - 40, n.y));
  }
}

// ─── Composant Principal ──────────────────────────
export default function NexusGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<NexusNode[]>([]);
  const [hovered, setHovered] = useState<NexusNode | null>(null);
  const [dimensions, setDimensions] = useState({ w: 900, h: 600 });
  const animRef = useRef<number>(0);
  const dragRef = useRef<{ node: NexusNode | null; offsetX: number; offsetY: number }>({
    node: null,
    offsetX: 0,
    offsetY: 0,
  });

  // Init
  useEffect(() => {
    const container = canvasRef.current?.parentElement;
    if (!container) return;
    const w = container.clientWidth;
    const h = Math.max(500, Math.min(700, window.innerHeight * 0.65));
    setDimensions({ w, h });
    nodesRef.current = initNodes(w, h);
  }, []);

  // Animation loop
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = dimensions.w * dpr;
    canvas.height = dimensions.h * dpr;
    ctx.scale(dpr, dpr);

    let running = true;

    function draw() {
      if (!running || !ctx) return;

      const nodes = nodesRef.current;
      const { w, h } = dimensions;

      // Simuler
      simulate(nodes, EDGES, w, h);

      // Clear
      ctx.clearRect(0, 0, w, h);

      const nodeMap = new Map(nodes.map((n) => [n.id, n]));

      // Dessiner les arêtes
      for (const edge of EDGES) {
        const a = nodeMap.get(edge.source);
        const b = nodeMap.get(edge.target);
        if (!a || !b) continue;

        const isHighlighted =
          hovered && (hovered.id === edge.source || hovered.id === edge.target);

        ctx.beginPath();
        ctx.moveTo(a.x, a.y);
        ctx.lineTo(b.x, b.y);
        ctx.strokeStyle = isHighlighted
          ? `rgba(0, 209, 255, ${0.4 + edge.strength * 0.4})`
          : `rgba(42, 49, 56, ${0.3 + edge.strength * 0.3})`;
        ctx.lineWidth = isHighlighted ? 2 : 1;
        ctx.stroke();
      }

      // Dessiner les nœuds
      for (const node of nodes) {
        const color = CATEGORY_COLORS[node.category];
        const isHovered = hovered?.id === node.id;
        const isConnected =
          hovered &&
          EDGES.some(
            (e) =>
              (e.source === hovered.id && e.target === node.id) ||
              (e.target === hovered.id && e.source === node.id)
          );
        const radius = isHovered ? 10 : isConnected ? 8 : 6;
        const alpha = hovered ? (isHovered || isConnected ? 1 : 0.3) : 0.9;

        // Glow
        if (isHovered) {
          ctx.beginPath();
          ctx.arc(node.x, node.y, 18, 0, Math.PI * 2);
          ctx.fillStyle = color.replace(')', ', 0.12)').replace('rgb', 'rgba');
          ctx.fill();
        }

        // Dot
        ctx.beginPath();
        ctx.arc(node.x, node.y, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.globalAlpha = alpha;
        ctx.fill();
        ctx.globalAlpha = 1;

        // Label
        ctx.font = `${isHovered ? '600' : '400'} ${isHovered ? '13' : '11'}px var(--font-inter), system-ui, sans-serif`;
        ctx.fillStyle = isHovered
          ? '#F5F7FA'
          : hovered && !isConnected
          ? 'rgba(176, 184, 193, 0.3)'
          : '#B0B8C1';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y - radius - 6);
      }

      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => {
      running = false;
      cancelAnimationFrame(animRef.current);
    };
  }, [dimensions, hovered]);

  // Mouse interactions
  const getNodeAt = useCallback(
    (mx: number, my: number): NexusNode | null => {
      for (const n of nodesRef.current) {
        const dx = mx - n.x;
        const dy = my - n.y;
        if (dx * dx + dy * dy < 20 * 20) return n;
      }
      return null;
    },
    []
  );

  const handleMouseMove = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;

      // Dragging
      if (dragRef.current.node) {
        dragRef.current.node.x = mx - dragRef.current.offsetX;
        dragRef.current.node.y = my - dragRef.current.offsetY;
        dragRef.current.node.vx = 0;
        dragRef.current.node.vy = 0;
        return;
      }

      const node = getNodeAt(mx, my);
      setHovered(node);

      if (canvasRef.current) {
        canvasRef.current.style.cursor = node ? 'grab' : 'default';
      }
    },
    [getNodeAt]
  );

  const handleMouseDown = useCallback(
    (e: React.MouseEvent<HTMLCanvasElement>) => {
      const rect = canvasRef.current?.getBoundingClientRect();
      if (!rect) return;
      const mx = e.clientX - rect.left;
      const my = e.clientY - rect.top;
      const node = getNodeAt(mx, my);
      if (node) {
        dragRef.current = { node, offsetX: mx - node.x, offsetY: my - node.y };
        if (canvasRef.current) canvasRef.current.style.cursor = 'grabbing';
      }
    },
    [getNodeAt]
  );

  const handleMouseUp = useCallback(() => {
    dragRef.current = { node: null, offsetX: 0, offsetY: 0 };
    if (canvasRef.current) canvasRef.current.style.cursor = 'default';
  }, []);

  return (
    <div className="relative w-full">
      <canvas
        ref={canvasRef}
        style={{ width: dimensions.w, height: dimensions.h }}
        className="w-full rounded-xl border border-white/[0.06] bg-[#070B10]"
        onMouseMove={handleMouseMove}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => {
          setHovered(null);
          handleMouseUp();
        }}
      />

      {/* Légende */}
      <div className="absolute bottom-4 left-4 flex flex-wrap gap-3">
        {Object.entries(CATEGORY_LABELS).map(([key, label]) => (
          <div key={key} className="flex items-center gap-1.5 text-xs text-[#E8E4DD]/40">
            <span
              className="w-2.5 h-2.5 rounded-full"
              style={{ backgroundColor: CATEGORY_COLORS[key] }}
            />
            <span>{label}</span>
          </div>
        ))}
      </div>

      {/* Tooltip */}
      {hovered && (
        <motion.div
          initial={{ opacity: 0, y: 4 }}
          animate={{ opacity: 1, y: 0 }}
          className="absolute top-4 right-4 bg-surface border border-white/[0.06] rounded-lg p-4 shadow-xl max-w-xs"
        >
          <div className="flex items-center gap-2 mb-1">
            <span
              className="w-3 h-3 rounded-full"
              style={{ backgroundColor: CATEGORY_COLORS[hovered.category] }}
            />
            <h4 className="font-display font-semibold text-sm">{hovered.label}</h4>
          </div>
          <p className="text-xs text-[#E8E4DD]/40">
            {CATEGORY_LABELS[hovered.category]} · Cliquez pour ouvrir l'article
          </p>
          <p className="text-xs text-[#E8E4DD]/40 mt-1">
            {EDGES.filter((e) => e.source === hovered.id || e.target === hovered.id).length} connexions
          </p>
        </motion.div>
      )}

      {/* Instructions */}
      <div className="absolute bottom-4 right-4 text-xs text-[#E8E4DD]/40/60">
        Glisser les nœuds · Survoler pour explorer
      </div>
    </div>
  );
}
