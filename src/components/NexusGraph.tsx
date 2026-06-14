'use client';

import { useRef, useEffect, useState, useCallback } from 'react';
import { useRouter } from 'next/navigation';
import { NEXUS_NODES, NEXUS_LINKS, type NexusNodeData, type NexusLinkData } from '@/lib/nexus-data';

interface Node extends NexusNodeData {
  px: number;
  py: number;
  vx: number;
  vy: number;
}

const CAT_COLORS: Record<string, string> = {
  headquarters: '#8B7EC8',
  observatory: '#3B8FD4',
  library: '#D4943A',
  lab: '#3D9E7C',
};

const CAT_LABELS: Record<string, string> = {
  headquarters: 'Centre de Recherche',
  observatory: 'Observatoire',
  library: 'Bibliothèque',
  lab: 'Outils',
};

function initNodes(data: NexusNodeData[], w: number, h: number): Node[] {
  const cx = w / 2, cy = h / 2;
  return data.map((n, i) => {
    const angle = (i / data.length) * Math.PI * 2;
    const r = Math.min(w, h) * 0.32;
    return {
      ...n,
      px: cx + Math.cos(angle) * r + (Math.random() - 0.5) * 40,
      py: cy + Math.sin(angle) * r + (Math.random() - 0.5) * 40,
      vx: 0, vy: 0,
    };
  });
}

function simulate(nodes: Node[], links: NexusLinkData[], w: number, h: number) {
  const map = new Map(nodes.map(n => [n.id, n]));
  const cx = w / 2, cy = h / 2;

  for (let i = 0; i < nodes.length; i++) {
    for (let j = i + 1; j < nodes.length; j++) {
      const a = nodes[i], b = nodes[j];
      let dx = b.px - a.px, dy = b.py - a.py;
      const dist = Math.sqrt(dx * dx + dy * dy) || 1;
      const force = 1200 / (dist * dist);
      dx = (dx / dist) * force;
      dy = (dy / dist) * force;
      a.vx -= dx; a.vy -= dy;
      b.vx += dx; b.vy += dy;
    }
  }

  for (const link of links) {
    const a = map.get(link.source), b = map.get(link.target);
    if (!a || !b) continue;
    const dx = b.px - a.px, dy = b.py - a.py;
    const dist = Math.sqrt(dx * dx + dy * dy) || 1;
    const str = link.strength === 'strong' ? 0.008 : link.strength === 'medium' ? 0.005 : 0.003;
    const force = (dist - 140) * str;
    const fx = (dx / dist) * force, fy = (dy / dist) * force;
    a.vx += fx; a.vy += fy;
    b.vx -= fx; b.vy -= fy;
  }

  for (const n of nodes) {
    n.vx += (cx - n.px) * 0.003;
    n.vy += (cy - n.py) * 0.003;
    n.vx *= 0.82; n.vy *= 0.82;
    n.px += n.vx; n.py += n.vy;
    n.px = Math.max(80, Math.min(w - 80, n.px));
    n.py = Math.max(50, Math.min(h - 50, n.py));
  }
}

interface Props {
  mini?: boolean;
  highlightSlug?: string;
}

export default function NexusGraph({ mini, highlightSlug }: Props) {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const [hovered, setHovered] = useState<Node | null>(null);
  const [dims, setDims] = useState({ w: 900, h: mini ? 300 : 600 });
  const animRef = useRef<number>(0);
  const router = useRouter();
  const dragRef = useRef<{ node: Node | null; ox: number; oy: number }>({ node: null, ox: 0, oy: 0 });

  const filteredLinks = mini && highlightSlug
    ? NEXUS_LINKS.filter(l => l.source === highlightSlug || l.target === highlightSlug)
    : NEXUS_LINKS;

  const filteredNodeIds = mini && highlightSlug
    ? new Set([highlightSlug, ...filteredLinks.map(l => l.source), ...filteredLinks.map(l => l.target)])
    : null;

  const nodeData = filteredNodeIds
    ? NEXUS_NODES.filter(n => filteredNodeIds.has(n.id))
    : NEXUS_NODES;

  useEffect(() => {
    const container = canvasRef.current?.parentElement;
    if (!container) return;
    const w = container.clientWidth;
    const h = mini ? 280 : Math.max(480, Math.min(650, window.innerHeight * 0.6));
    setDims({ w, h });
    nodesRef.current = initNodes(nodeData, w, h);
  }, [nodeData.length, mini]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const dpr = window.devicePixelRatio || 1;
    canvas.width = dims.w * dpr;
    canvas.height = dims.h * dpr;
    ctx.scale(dpr, dpr);

    let running = true;

    function draw() {
      if (!running || !ctx) return;
      const nodes = nodesRef.current;
      simulate(nodes, filteredLinks, dims.w, dims.h);
      ctx.clearRect(0, 0, dims.w, dims.h);

      const map = new Map(nodes.map(n => [n.id, n]));

      for (const link of filteredLinks) {
        const a = map.get(link.source), b = map.get(link.target);
        if (!a || !b) continue;
        const isHL = hovered && (hovered.id === link.source || hovered.id === link.target);
        const isArticle = highlightSlug && (link.source === highlightSlug || link.target === highlightSlug);
        ctx.beginPath();
        ctx.moveTo(a.px, a.py);
        ctx.lineTo(b.px, b.py);
        ctx.strokeStyle = isHL
          ? `rgba(139, 126, 200, 0.6)`
          : isArticle
          ? `rgba(139, 126, 200, 0.3)`
          : `rgba(200, 200, 200, ${link.strength === 'strong' ? 0.4 : link.strength === 'medium' ? 0.25 : 0.15})`;
        ctx.lineWidth = isHL ? 2.5 : isArticle ? 2 : 1;
        ctx.stroke();
      }

      for (const node of nodes) {
        const color = CAT_COLORS[node.category] || '#8B8F96';
        const isHovered = hovered?.id === node.id;
        const isHighlight = node.id === highlightSlug;
        const isConnected = hovered && filteredLinks.some(
          e => (e.source === hovered.id && e.target === node.id) || (e.target === hovered.id && e.source === node.id)
        );
        const radius = isHovered ? 10 : isHighlight ? 9 : isConnected ? 7 : 5;
        const alpha = hovered ? (isHovered || isConnected ? 1 : 0.25) : isHighlight ? 1 : 0.8;

        if (isHovered || isHighlight) {
          ctx.beginPath();
          ctx.arc(node.px, node.py, radius + 8, 0, Math.PI * 2);
          ctx.fillStyle = color + '18';
          ctx.fill();
        }

        ctx.beginPath();
        ctx.arc(node.px, node.py, radius, 0, Math.PI * 2);
        ctx.fillStyle = color;
        ctx.globalAlpha = alpha;
        ctx.fill();
        ctx.globalAlpha = 1;

        const fontSize = mini ? (isHovered ? 11 : 9) : (isHovered ? 13 : 11);
        ctx.font = `${isHovered || isHighlight ? '600' : '400'} ${fontSize}px system-ui, sans-serif`;
        ctx.fillStyle = isHovered ? '#1A1D23' : hovered && !isConnected ? '#B8BBC2' : '#4A4E57';
        ctx.textAlign = 'center';

        const label = node.title.length > 30 ? node.title.slice(0, 28) + '…' : node.title;
        ctx.fillText(label, node.px, node.py - radius - 6);
      }

      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => { running = false; cancelAnimationFrame(animRef.current); };
  }, [dims, hovered, filteredLinks, highlightSlug, mini]);

  const getNodeAt = useCallback((mx: number, my: number): Node | null => {
    for (const n of nodesRef.current) {
      const dx = mx - n.px, dy = my - n.py;
      if (dx * dx + dy * dy < 20 * 20) return n;
    }
    return null;
  }, []);

  const handleMouseMove = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    if (dragRef.current.node) {
      dragRef.current.node.px = mx - dragRef.current.ox;
      dragRef.current.node.py = my - dragRef.current.oy;
      dragRef.current.node.vx = 0;
      dragRef.current.node.vy = 0;
      return;
    }
    const node = getNodeAt(mx, my);
    setHovered(node);
    if (canvasRef.current) canvasRef.current.style.cursor = node ? 'pointer' : 'default';
  }, [getNodeAt]);

  const handleMouseDown = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const node = getNodeAt(mx, my);
    if (node) {
      dragRef.current = { node, ox: mx - node.px, oy: my - node.py };
      if (canvasRef.current) canvasRef.current.style.cursor = 'grabbing';
    }
  }, [getNodeAt]);

  const handleMouseUp = useCallback(() => {
    if (dragRef.current.node && hovered && dragRef.current.node.id === hovered.id) {
      const moved = Math.abs(dragRef.current.ox) + Math.abs(dragRef.current.oy);
      if (moved < 5) {
        router.push(`/article/${hovered.id}`);
      }
    }
    dragRef.current = { node: null, ox: 0, oy: 0 };
    if (canvasRef.current) canvasRef.current.style.cursor = 'default';
  }, [hovered, router]);

  const handleClick = useCallback((e: React.MouseEvent<HTMLCanvasElement>) => {
    const rect = canvasRef.current?.getBoundingClientRect();
    if (!rect) return;
    const mx = e.clientX - rect.left, my = e.clientY - rect.top;
    const node = getNodeAt(mx, my);
    if (node) router.push(`/article/${node.id}`);
  }, [getNodeAt, router]);

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <canvas
        ref={canvasRef}
        style={{ width: dims.w, height: dims.h, borderRadius: mini ? 8 : 12, border: '1px solid #E8EAED', background: '#FAFBFC' }}
        onMouseMove={handleMouseMove}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onClick={handleClick}
        onMouseLeave={() => { setHovered(null); dragRef.current = { node: null, ox: 0, oy: 0 }; }}
      />

      {/* Tooltip */}
      {hovered && (
        <div style={{
          position: 'absolute', top: 12, right: 12,
          background: 'var(--card)', border: '1px solid var(--border)', borderRadius: 10,
          padding: '12px 16px', boxShadow: '0 4px 16px rgba(0,0,0,0.08)',
          maxWidth: 260, pointerEvents: 'none',
        }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 4 }}>
            <span style={{ width: 10, height: 10, borderRadius: '50%', background: CAT_COLORS[hovered.category] }} />
            <span style={{ fontSize: 12, fontWeight: 700, color: 'var(--ink)' }}>{hovered.title}</span>
          </div>
          <div style={{ fontSize: 11, color: 'var(--ink-muted)' }}>
            {CAT_LABELS[hovered.category]} · {filteredLinks.filter(e => e.source === hovered.id || e.target === hovered.id).length} connexions
          </div>
          <div style={{ fontSize: 10, color: 'var(--ink-ghost)', marginTop: 4 }}>
            Cliquez pour ouvrir l&apos;article →
          </div>
        </div>
      )}

      {/* Legend */}
      {!mini && (
        <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 12 }}>
          {Object.entries(CAT_LABELS).map(([key, label]) => (
            <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: '#8B8F96' }}>
              <span style={{ width: 8, height: 8, borderRadius: '50%', background: CAT_COLORS[key] }} />
              {label}
            </div>
          ))}
          <span style={{ marginLeft: 'auto', fontSize: 11, color: '#B8BBC2' }}>
            Glissez les nœuds · Cliquez pour ouvrir
          </span>
        </div>
      )}
    </div>
  );
}
