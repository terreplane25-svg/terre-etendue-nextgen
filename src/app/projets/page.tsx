import type { Metadata } from 'next';

export const metadata: Metadata = {
  title: "Projets — Bientôt disponible",
  description: "Expériences scientifiques financées par la communauté. Page en construction.",
  robots: { index: false, follow: true },
};

export default function ProjetsPage() {
  return (
    <div style={{
      minHeight: '80vh', display: 'flex', flexDirection: 'column',
      alignItems: 'center', justifyContent: 'center', padding: '48px 24px',
      textAlign: 'center',
    }}>
      <div style={{ fontSize: 48, marginBottom: 20 }}>🔬</div>
      <h1 style={{
        fontSize: 28, fontWeight: 900, color: 'var(--ink)', marginBottom: 12,
        fontFamily: "'Plus Jakarta Sans', sans-serif", letterSpacing: '-0.02em',
      }}>
        Page en construction
      </h1>
      <p style={{
        fontSize: 16, color: 'var(--ink-soft)', lineHeight: 1.6,
        maxWidth: 480,
      }}>
        Des expériences scientifiques financées par la communauté arrivent bientôt.
        Budget transparent, protocole détaillé, résultats publiés quoi qu&apos;il arrive.
      </p>
      <p style={{
        fontSize: 13, color: 'var(--ink-muted)', marginTop: 24,
        fontFamily: "'JetBrains Mono', monospace",
      }}>
        En attendant, explorez les simulateurs et les articles.
      </p>
    </div>
  );
}
