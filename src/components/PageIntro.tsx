'use client';

interface Props {
  lede: string;
  body: string;
  color: string;
}

// Accroche éditoriale sobre placée sous l'en-tête d'une page de catégorie :
// une phrase forte (lede) + 2-3 phrases sur la démarche de la page, avec un
// filet à la couleur du pilier. Donne un contexte avant la liste d'articles.
export default function PageIntro({ lede, body, color }: Props) {
  return (
    <div style={{ maxWidth: 1200, margin: '0 auto', padding: '44px 32px 10px' }}>
      <div style={{ borderLeft: `4px solid ${color}`, paddingLeft: 22 }}>
        <p style={{
          fontSize: 26, fontWeight: 750, color: 'var(--ink)',
          lineHeight: 1.35, marginBottom: 14, letterSpacing: '-0.015em',
        }}>{lede}</p>
        <p style={{
          fontSize: 17, color: 'var(--ink-muted)', lineHeight: 1.75, maxWidth: 880,
        }}>{body}</p>
      </div>
    </div>
  );
}
