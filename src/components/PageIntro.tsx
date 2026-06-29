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
    <div style={{ maxWidth: 960, margin: '0 auto', padding: '30px 24px 6px' }}>
      <div style={{ borderLeft: `3px solid ${color}`, paddingLeft: 18 }}>
        <p style={{
          fontSize: 19, fontWeight: 750, color: 'var(--ink)',
          lineHeight: 1.45, marginBottom: 10, letterSpacing: '-0.01em',
        }}>{lede}</p>
        <p style={{
          fontSize: 14.5, color: 'var(--ink-muted)', lineHeight: 1.7, maxWidth: 760,
        }}>{body}</p>
      </div>
    </div>
  );
}
