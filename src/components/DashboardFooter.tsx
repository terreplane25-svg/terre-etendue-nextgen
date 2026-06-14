import Link from 'next/link';
import { getAllArticles } from '@/lib/articles';

const SOCIALS = [
  { icon: '▶', label: 'YouTube', href: 'https://www.youtube.com/@TERREETENDUE', color: '#FF0000' },
  { icon: '◉', label: 'Odysee', href: 'https://odysee.com/@terreetendue', color: '#E84A8A' },
  { icon: '✈', label: 'Telegram (canal)', href: 'https://t.me/LATERREETENDUE', color: '#0088CC' },
  { icon: '💬', label: 'Telegram (groupe)', href: 'https://t.me/terre_etendue', color: '#0088CC' },
  { icon: '♪', label: 'TikTok', href: 'https://tiktok.com/@terreetendue1', color: '#111' },
];

const SECTIONS = [
  { label: 'Bibliothèque', href: '/library' },
  { label: 'Centre de Recherche', href: '/headquarters' },
  { label: 'Observatoire', href: '/observatory' },
  { label: 'Expériences', href: '/experiences' },
  { label: 'Outils', href: '/lab' },
  { label: 'À propos', href: '/about' },
];

export default function DashboardFooter() {
  const count = getAllArticles().length;
  return (
    <footer style={{
      borderTop: '1px solid var(--border)',
      padding: '48px 24px 32px',
      marginTop: 'auto',
      background: 'var(--bg)',
    }}>
      <div style={{ maxWidth: 1200, margin: '0 auto' }}>
        {/* Top row: brand + nav + socials */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: '1fr',
          gap: 32,
        }} className="footer-grid">
          {/* Brand */}
          <div>
            <Link href="/" style={{ display: 'inline-block' }}>
              <div style={{
                fontSize: 24, fontWeight: 900, color: 'var(--ink)', letterSpacing: '-0.03em',
                lineHeight: 1.1, fontFamily: "'Plus Jakarta Sans', sans-serif",
              }}>
                Terre Étendue <span style={{ color: '#2B9E6E', fontWeight: 900 }}>Islam</span>
              </div>
            </Link>
            <div style={{
              fontSize: 11, color: 'var(--ink-muted)', letterSpacing: '0.03em',
              marginTop: 6, fontFamily: "'Plus Jakarta Sans', sans-serif", fontWeight: 500,
            }}>
              Explorer la création, honorer la Révélation
            </div>
          </div>

          {/* Navigation links */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px 24px' }}>
            {SECTIONS.map(s => (
              <Link key={s.href} href={s.href} style={{
                fontSize: 13, fontWeight: 600, color: 'var(--ink-soft)',
                transition: 'color 0.15s',
                fontFamily: "'Plus Jakarta Sans', sans-serif",
              }}>
                {s.label}
              </Link>
            ))}
          </div>

          {/* Social links */}
          <div style={{ display: 'flex', flexWrap: 'wrap', gap: 10 }}>
            {SOCIALS.map(s => (
              <a key={s.href} href={s.href} target="_blank" rel="noopener noreferrer"
                title={s.label}
                style={{
                  display: 'inline-flex', alignItems: 'center', gap: 6,
                  padding: '6px 12px', borderRadius: 6,
                  fontSize: 12, fontWeight: 600,
                  background: 'var(--card)', border: '1px solid var(--border)',
                  color: 'var(--ink-soft)', transition: 'all 0.15s',
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                }}>
                <span style={{ fontSize: 14 }}>{s.icon}</span>
                {s.label}
              </a>
            ))}
          </div>
        </div>

        {/* Bottom bar */}
        <div style={{
          marginTop: 32, paddingTop: 20,
          borderTop: '1px solid var(--border-soft)',
          display: 'flex', justifyContent: 'space-between', alignItems: 'center',
          flexWrap: 'wrap', gap: 12,
        }}>
          <div style={{ fontSize: 12, color: 'var(--ink-muted)' }}>
            Revue indépendante de cosmologie · {new Date().getFullYear()}
          </div>
          <div style={{
            fontSize: 11, color: 'var(--ink-ghost)',
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            {count} publications · 450+ sources
          </div>
        </div>
      </div>

      <style>{`
        @media (min-width: 768px) {
          .footer-grid { grid-template-columns: 1fr auto auto !important; align-items: start; }
        }
      `}</style>
    </footer>
  );
}
