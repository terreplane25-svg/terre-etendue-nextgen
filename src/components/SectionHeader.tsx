'use client';
import { dash } from '@/lib/design-tokens';

interface Props {
  pillar: string;
  pillarNum: string;
  subtitle: string;
  title: string;
  color: string;
  count: number;
  countLabel: string;
}

export default function SectionHeader({ pillar, pillarNum, subtitle, title, color, count, countLabel }: Props) {
  return (
    <div style={{
      background: '#0D1528',
      padding: '40px 24px 36px',
      borderBottom: '1px solid #1a2540',
    }}>
      <div style={{ maxWidth: 1100, margin: '0 auto' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
          <span style={{
            fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700,
            color, letterSpacing: '0.12em',
            padding: '3px 8px', border: `1px solid ${color}40`, borderRadius: 3,
          }}>PILIER {pillarNum}</span>
          <div style={{ width: 24, height: 1, background: '#607890' }} />
          <span style={{ fontSize: 10, fontFamily: dash.fontMono, color: '#607890', letterSpacing: '0.08em', textTransform: 'uppercase' }}>
            {subtitle}
          </span>
        </div>
        <h1 style={{
          fontSize: 28, fontWeight: 800, color: '#C8D8E8',
          letterSpacing: '-0.01em', marginBottom: 6,
        }}>
          {title}
        </h1>
        <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
          <p style={{ fontSize: 14, color: '#607890', lineHeight: 1.5 }}>
            {count} {countLabel}
          </p>
          <div style={{ display: 'flex', gap: 8, marginLeft: 'auto' }}>
            {[dash.opal, dash.lavender, dash.rose, dash.saffron, dash.cyan].map((c, i) => (
              <div key={i} style={{ width: 6, height: 6, borderRadius: 1, background: c, opacity: 0.6 }} />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
