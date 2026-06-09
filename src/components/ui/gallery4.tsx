'use client';

import React, { useRef, useState } from 'react';
import Link from 'next/link';

interface GalleryItem {
  id: string;
  title: string;
  description: string;
  href: string;
  image: string;
}

interface Gallery4Props {
  title: string;
  description: string;
  items: GalleryItem[];
  color?: string;
}

const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';

export function Gallery4({ title, description, items, color = '#7C6FC4' }: Gallery4Props) {
  const scrollRef = useRef<HTMLDivElement>(null);
  const [idx, setIdx] = useState(0);

  const scroll = (dir: number) => {
    const next = Math.max(0, Math.min(idx + dir, items.length - 1));
    setIdx(next);
    scrollRef.current?.children[next]?.scrollIntoView({ behavior: 'smooth', block: 'nearest', inline: 'start' });
  };

  return (
    <section style={{ padding: '60px 0 40px' }}>
      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 32px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-end', marginBottom: 28 }}>
          <div>
            <h2 style={{ fontSize: 32, fontWeight: 800, letterSpacing: '-0.02em', marginBottom: 8, color: '#141210' }}>{title}</h2>
            <p style={{ fontSize: 14, color: '#8A857D', maxWidth: 420 }}>{description}</p>
          </div>
          <div style={{ display: 'flex', gap: 8 }}>
            <button onClick={() => scroll(-1)} disabled={idx === 0} style={{
              width: 40, height: 40, borderRadius: 6, border: '1px solid #F5F3EE',
              background: '#fff', cursor: 'pointer', fontSize: 18,
              color: idx === 0 ? '#BAB5AC' : '#141210',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'system-ui',
            }}>←</button>
            <button onClick={() => scroll(1)} disabled={idx >= items.length - 2} style={{
              width: 40, height: 40, borderRadius: 6, border: '1px solid #F5F3EE',
              background: '#fff', cursor: 'pointer', fontSize: 18,
              color: idx >= items.length - 2 ? '#BAB5AC' : '#141210',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontFamily: 'system-ui',
            }}>→</button>
          </div>
        </div>
      </div>
      <div ref={scrollRef} style={{
        display: 'flex', gap: 20, overflowX: 'auto', scrollSnapType: 'x mandatory',
        padding: '0 32px 20px', scrollbarWidth: 'none', msOverflowStyle: 'none',
      }}>
        {items.map((item) => (
          <Link key={item.id} href={item.href} style={{
            minWidth: 340, maxWidth: 360, flexShrink: 0, scrollSnapAlign: 'start',
            borderRadius: 8, overflow: 'hidden', position: 'relative', height: 440,
            cursor: 'pointer', background: '#F5F3EE', border: '1px solid rgba(20,18,16,0.06)', padding: 6,
            display: 'block',
          }}>
            <div style={{ borderRadius: 6, overflow: 'hidden', height: '100%', position: 'relative' }}>
              <img src={item.image} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover' }} loading="lazy" />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(20,18,16,0.88) 0%, rgba(20,18,16,0.3) 40%, transparent 70%)' }} />
              <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '24px 22px' }}>
                <h3 style={{ fontSize: 18, fontWeight: 700, color: '#fff', lineHeight: 1.3, marginBottom: 8 }}>{item.title}</h3>
                <p style={{ fontSize: 13, color: 'rgba(255,255,255,0.7)', lineHeight: 1.5, display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any, overflow: 'hidden' }}>{item.description}</p>
                <div style={{ marginTop: 14, fontSize: 12, color: 'rgba(255,255,255,0.5)', display: 'flex', alignItems: 'center', gap: 6 }}>
                  Lire l&apos;article →
                </div>
              </div>
            </div>
          </Link>
        ))}
      </div>
      <div style={{ display: 'flex', justifyContent: 'center', gap: 6, marginTop: 12 }}>
        {items.map((_, i) => (
          <div key={i} onClick={() => { setIdx(i); scrollRef.current?.children[i]?.scrollIntoView({ behavior: 'smooth', inline: 'start' }); }}
            style={{ width: 8, height: 8, borderRadius: 99, cursor: 'pointer',
              background: i === idx ? color : color + '25',
              transition: `all 0.3s ${BEZ}`,
            }} />
        ))}
      </div>
    </section>
  );
}
