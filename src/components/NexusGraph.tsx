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

// Les quatre piliers, plus les pages de méthode. Les couleurs sont celles de
// la charte (globals.css) ; aucune ne doit être inventée ici.
// Toute catégorie présente dans le corpus doit figurer dans les deux tables :
// une catégorie manquante donnait un point gris et un libellé « undefined ».
const CAT_COLORS: Record<string, string> = {
  headquarters: '#8B7EC8',
  observatory: '#3B8FD4',
  library: '#D4943A',
  experiences: '#C45E6A',
  meta: '#B8941F',
};

const CAT_LABELS: Record<string, string> = {
  headquarters: 'Centre de Recherche',
  observatory: 'Observatoire',
  library: 'Bibliothèque',
  experiences: 'Expériences',
  meta: 'Méthode',
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

// Le graphe s'affiche sur /nexus, en pleine largeur. Il a longtemps eu un mode
// « mini » pour une colonne latérale d'article, repliée derrière un bouton et
// masquée sous 1024 px ; cette colonne a été retirée, et le mode avec elle.
export default function NexusGraph() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const nodesRef = useRef<Node[]>([]);
  const [hovered, setHovered] = useState<Node | null>(null);
  const [dims, setDims] = useState({ w: 900, h: 600 });
  const [sombre, setSombre] = useState(false);
  const animRef = useRef<number>(0);
  const router = useRouter();
  const dragRef = useRef<{ node: Node | null; ox: number; oy: number; bouge: boolean }>(
    { node: null, ox: 0, oy: 0, bouge: false });

  const filteredLinks = NEXUS_LINKS;
  const nodeData = NEXUS_NODES;

  // Le canevas ne peut pas lire les variables CSS : les libellés sont peints,
  // pas stylés. Sans ce suivi du thème, ils restaient en encre sombre sur fond
  // sombre — c'est-à-dire illisibles.
  useEffect(() => {
    const racine = document.documentElement;
    const lire = () => setSombre(racine.getAttribute('data-theme') === 'dark');
    lire();
    const obs = new MutationObserver(lire);
    obs.observe(racine, { attributes: true, attributeFilter: ['data-theme'] });
    return () => obs.disconnect();
  }, []);

  useEffect(() => {
    const container = canvasRef.current?.parentElement;
    if (!container) return;
    const w = container.clientWidth;
    const h = Math.max(480, Math.min(650, window.innerHeight * 0.6));
    setDims({ w, h });
    nodesRef.current = initNodes(nodeData, w, h);
  }, [nodeData.length]);

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
        ctx.beginPath();
        ctx.moveTo(a.px, a.py);
        ctx.lineTo(b.px, b.py);
        ctx.strokeStyle = isHL
          ? `rgba(139, 126, 200, 0.6)`
          : `rgba(${sombre ? '150, 155, 165' : '200, 200, 200'}, ${link.strength === 'strong' ? 0.4 : link.strength === 'medium' ? 0.25 : 0.15})`;
        ctx.lineWidth = isHL ? 2.5 : 1;
        ctx.stroke();
      }

      for (const node of nodes) {
        const color = CAT_COLORS[node.category] || '#8B8F96';
        const isHovered = hovered?.id === node.id;
        const isConnected = hovered && filteredLinks.some(
          e => (e.source === hovered.id && e.target === node.id) || (e.target === hovered.id && e.source === node.id)
        );
        const radius = isHovered ? 10 : isConnected ? 7 : 5;
        const alpha = hovered ? (isHovered || isConnected ? 1 : 0.25) : 0.8;

        if (isHovered) {
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

        const fontSize = isHovered ? 13 : 11;
        ctx.font = `${isHovered ? '600' : '400'} ${fontSize}px system-ui, sans-serif`;
        ctx.fillStyle = isHovered
          ? (sombre ? '#F2F4F8' : '#1A1D23')
          : hovered && !isConnected
          ? (sombre ? '#5A5F68' : '#B8BBC2')
          : (sombre ? '#A8ADB6' : '#4A4E57');
        ctx.textAlign = 'center';

        const label = node.title.length > 30 ? node.title.slice(0, 28) + '…' : node.title;
        ctx.fillText(label, node.px, node.py - radius - 6);
      }

      animRef.current = requestAnimationFrame(draw);
    }

    draw();
    return () => { running = false; cancelAnimationFrame(animRef.current); };
  }, [dims, hovered, filteredLinks, sombre]);

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
      const avantX = dragRef.current.node.px, avantY = dragRef.current.node.py;
      dragRef.current.node.px = mx - dragRef.current.ox;
      dragRef.current.node.py = my - dragRef.current.oy;
      dragRef.current.node.vx = 0;
      dragRef.current.node.vy = 0;
      if (Math.abs(dragRef.current.node.px - avantX)
          + Math.abs(dragRef.current.node.py - avantY) > 1) {
        dragRef.current.bouge = true;
      }
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
      dragRef.current = { node, ox: mx - node.px, oy: my - node.py, bouge: false };
      if (canvasRef.current) canvasRef.current.style.cursor = 'grabbing';
    }
  }, [getNodeAt]);

  // Un seul chemin vers l'article : le relâchement sur un nœud qu'on n'a pas
  // déplacé. Il y avait aussi un `onClick` sans garde, qui ouvrait l'article
  // dès qu'on lâchait un nœud après l'avoir traîné — le geste « ranger le
  // graphe » envoyait donc lire.
  const handleMouseUp = useCallback(() => {
    const { node, bouge } = dragRef.current;
    dragRef.current = { node: null, ox: 0, oy: 0, bouge: false };
    if (canvasRef.current) canvasRef.current.style.cursor = node ? 'pointer' : 'default';
    if (node && !bouge) router.push(`/article/${node.id}`);
  }, [router]);

  return (
    <div style={{ position: 'relative', width: '100%' }}>
      <canvas
        ref={canvasRef}
        style={{ width: dims.w, height: dims.h, borderRadius: 12, border: '1px solid var(--border)', background: 'var(--card)' }}
        onMouseMove={handleMouseMove}
        onMouseDown={handleMouseDown}
        onMouseUp={handleMouseUp}
        onMouseLeave={() => { setHovered(null); dragRef.current = { node: null, ox: 0, oy: 0, bouge: false }; }}
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
      <div style={{ display: 'flex', flexWrap: 'wrap', gap: 16, marginTop: 12 }}>
        {Object.entries(CAT_LABELS).map(([key, label]) => (
          <div key={key} style={{ display: 'flex', alignItems: 'center', gap: 6, fontSize: 11, color: 'var(--ink-muted)' }}>
            <span style={{ width: 8, height: 8, borderRadius: '50%', background: CAT_COLORS[key] }} />
            {label}
          </div>
        ))}
        <span style={{ marginLeft: 'auto', fontSize: 11, color: 'var(--ink-muted)' }}>
          Glissez les nœuds · Cliquez pour ouvrir
        </span>
      </div>
    </div>
  );
}
