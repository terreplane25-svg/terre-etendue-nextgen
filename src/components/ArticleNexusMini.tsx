'use client';

import { useState } from 'react';
import dynamic from 'next/dynamic';
import { NEXUS_NODES, NEXUS_LINKS } from '@/lib/nexus-data';

const NexusGraph = dynamic(() => import('@/components/NexusGraph'), { ssr: false });

export default function ArticleNexusMini({ slug }: { slug: string }) {
  const [open, setOpen] = useState(false);

  const node = NEXUS_NODES.find(n => n.id === slug);
  const connections = NEXUS_LINKS.filter(l => l.source === slug || l.target === slug);

  if (!node || connections.length === 0) return null;

  return (
    <div style={{ position: 'sticky', top: 100 }}>
      <button
        onClick={() => setOpen(!open)}
        style={{
          width: '100%', padding: '10px 14px',
          background: '#FAFBFC', border: '1px solid #E8EAED', borderRadius: 8,
          cursor: 'pointer', display: 'flex', alignItems: 'center', justifyContent: 'space-between',
          fontSize: 13, fontWeight: 600, color: '#4A4E57',
        }}
      >
        <span>Nexus · {connections.length} connexions</span>
        <span style={{ transform: open ? 'rotate(180deg)' : 'rotate(0)', transition: 'transform 0.2s', fontSize: 10, color: '#8B8F96' }}>▼</span>
      </button>
      {open && (
        <div style={{ marginTop: 8, borderRadius: 8, overflow: 'hidden', border: '1px solid #E8EAED' }}>
          <NexusGraph mini highlightSlug={slug} />
        </div>
      )}
    </div>
  );
}
