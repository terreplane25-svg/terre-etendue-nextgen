import Link from 'next/link';

interface Props {
  titre: string;
  objectif: number;
  collecte: number;
  donateurs: number;
  id: string;
  variant?: 'article' | 'footer' | 'minimal';
}

export default function ExperimentCTA({ titre, objectif, collecte, donateurs, id, variant = 'article' }: Props) {
  const pct = Math.min(100, Math.round((collecte / objectif) * 100));

  if (variant === 'minimal') {
    return (
      <Link href={`/projets#${id}`} style={{
        display: 'flex', alignItems: 'center', gap: 10,
        fontSize: 13, fontWeight: 600, color: '#2B7A5F',
        textDecoration: 'none',
      }}>
        <span>🧪</span>
        <span>Soutenir une expérience</span>
      </Link>
    );
  }

  if (variant === 'footer') {
    return (
      <Link href="/projets" style={{
        display: 'block', padding: '14px 16px', borderRadius: 8,
        background: '#2B7A5F10', border: '1px solid #2B7A5F25',
        textDecoration: 'none', transition: 'border-color 0.15s',
      }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          <span style={{ fontSize: 16 }}>🧪</span>
          <span style={{ fontSize: 12, fontWeight: 700, color: '#2B7A5F', letterSpacing: '0.04em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace" }}>
            Expérience en cours
          </span>
        </div>
        <div style={{ fontSize: 13, fontWeight: 600, color: 'var(--ink)', marginBottom: 8, lineHeight: 1.35 }}>
          {titre}
        </div>
        <div style={{ height: 4, background: 'var(--border)', borderRadius: 2, overflow: 'hidden', marginBottom: 6 }}>
          <div style={{
            height: '100%', borderRadius: 2, background: '#2B7A5F',
            width: `${pct}%`, transition: 'width 0.5s',
          }} />
        </div>
        <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: 11, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
          <span>{collecte}€ / {objectif}€</span>
          <span>{donateurs} contributeur{donateurs > 1 ? 's' : ''}</span>
        </div>
      </Link>
    );
  }

  return (
    <div style={{
      marginTop: 48, padding: '28px 24px', borderRadius: 12,
      background: 'var(--card)', border: '1px solid var(--border)',
      borderLeft: '4px solid #2B7A5F',
    }}>
      <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 12 }}>
        <span style={{ fontSize: 18 }}>🧪</span>
        <span style={{ fontSize: 11, fontWeight: 700, color: '#2B7A5F', letterSpacing: '0.06em', textTransform: 'uppercase', fontFamily: "'JetBrains Mono', monospace" }}>
          Expérience en financement
        </span>
      </div>

      <div style={{ fontSize: 17, fontWeight: 750, color: 'var(--ink)', marginBottom: 8, lineHeight: 1.35 }}>
        {titre}
      </div>

      <p style={{ fontSize: 14, color: 'var(--ink-soft)', lineHeight: 1.6, marginBottom: 16 }}>
        Ce contenu est gratuit et le restera. Mais les expériences réelles coûtent de l&apos;argent réel. Chaque euro finance du matériel, pas des serveurs.
      </p>

      <div style={{ height: 6, background: 'var(--border)', borderRadius: 3, overflow: 'hidden', marginBottom: 8 }}>
        <div style={{
          height: '100%', borderRadius: 3, background: 'linear-gradient(90deg, #2B7A5F, #3D9E7C)',
          width: `${pct}%`, transition: 'width 0.5s',
        }} />
      </div>

      <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: 18, fontSize: 12, fontFamily: "'JetBrains Mono', monospace" }}>
        <span style={{ fontWeight: 700, color: '#2B7A5F' }}>{collecte}€ / {objectif}€ ({pct}%)</span>
        <span style={{ color: 'var(--ink-muted)' }}>{donateurs} contributeur{donateurs > 1 ? 's' : ''}</span>
      </div>

      <div style={{ display: 'flex', gap: 10, flexWrap: 'wrap' }}>
        <Link href={`/projets#${id}`} style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '10px 20px', borderRadius: 8,
          background: '#2B7A5F', color: '#fff',
          fontSize: 13, fontWeight: 700, textDecoration: 'none',
          transition: 'opacity 0.15s',
        }}>
          Soutenir cette expérience
        </Link>
        <Link href="/projets" style={{
          display: 'inline-flex', alignItems: 'center', gap: 8,
          padding: '10px 20px', borderRadius: 8,
          background: 'var(--bg)', color: 'var(--ink-soft)',
          border: '1px solid var(--border)',
          fontSize: 13, fontWeight: 600, textDecoration: 'none',
        }}>
          Voir tous les projets →
        </Link>
      </div>
    </div>
  );
}
