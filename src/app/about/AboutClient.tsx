"use client";

interface Props {
  manifeste: string;
  methodologie: string;
  ethique: string;
  etatDesLieux: string;
}

const SECTIONS_DATA = [
  { key: 'manifeste', title: 'MANIFESTE', color: '#D4943A' },
  { key: 'methodologie', title: 'MÉTHODOLOGIE', color: '#3B8FD4' },
  { key: 'etatDesLieux', title: 'ÉTAT DES LIEUX', color: '#3B8FD4' },
  { key: 'ethique', title: 'ÉTHIQUE INTELLECTUELLE', color: '#3D9E7C' },
] as const;

export default function AboutClient({ manifeste, methodologie, ethique, etatDesLieux }: Props) {
  const content: Record<string, string> = { manifeste, methodologie, ethique, etatDesLieux };

  return (
    <div style={{ minHeight: '100vh', padding: '40px 0 80px' }}>
      <div style={{ maxWidth: 720, margin: '0 auto', padding: '0 24px' }}>
        <div style={{ marginBottom: 40 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <div style={{ width: 4, height: 28, background: '#8B8F96', borderRadius: 2 }} />
            <span style={{ fontSize: 11, fontWeight: 700, color: '#8B8F96', letterSpacing: '0.15em', textTransform: 'uppercase' as const }}>À propos</span>
          </div>
          <h1 style={{ fontSize: 28, fontWeight: 800, color: '#1A1D23', letterSpacing: '-0.02em' }}>Terre Étendue Islam</h1>
        </div>

        {SECTIONS_DATA.map((section, i) => (
          <div key={section.key}>
            {i > 0 && <div style={{ height: 1, background: '#E8EAED', margin: '48px 0' }} />}
            <section style={{ marginBottom: 48 }}>
              <h2 style={{
                display: 'flex', alignItems: 'center', gap: 12,
                fontSize: 14, fontWeight: 700, color: section.color,
                letterSpacing: '0.1em', marginBottom: 24,
              }}>
                <span style={{ width: 24, height: 1, background: section.color, opacity: 0.3 }} />
                {section.title}
              </h2>
              <div
                className="prose-dash"
                dangerouslySetInnerHTML={{ __html: content[section.key] }}
              />
            </section>
          </div>
        ))}
      </div>
    </div>
  );
}
