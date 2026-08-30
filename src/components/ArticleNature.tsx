'use client';
import React from 'react';
import { getNature, GENRE_LABEL, GENRE_COULEUR, GENRE_DEFINITION } from '@/lib/nature-articles';

/**
 * L'encadré « Ce que cet article est ».
 *
 * Placé avant le corps du texte, il dit trois choses : le genre de l'article,
 * ce sur quoi il repose, et ce qu'il n'établit pas.
 *
 * La dernière ligne est celle qui compte. Un site qui écrit en tête de chaque
 * page la limite de ce qu'il avance se juge lui-même avant qu'on le juge ;
 * c'est aussi ce qui permet à un lecteur de faire la différence entre une
 * mesure que nous avons faite et un livre de 1922 que nous n'avons pas vérifié.
 *
 * Sobre à dessein. Ce n'est pas un encadré-clé — ceux-là (`tei-fait`) portent
 * un fait et vivent dans le corps du texte. Celui-ci porte un avertissement et
 * vit au-dessus. Les deux ne doivent pas se confondre.
 *
 * Un article sans notice n'affiche rien plutôt qu'un texte creux : une case
 * vide se voit, une formule passe-partout se recopie.
 */
export default function ArticleNature({ slug }: { slug: string }) {
  const n = getNature(slug);
  if (!n) return null;

  const couleur = GENRE_COULEUR[n.genre];

  return (
    <div
      style={{
        border: '1px solid var(--border)',
        borderLeft: `3px solid ${couleur}`,
        borderRadius: 6,
        background: 'var(--cream)',
        padding: '18px 20px',
        margin: '0 0 32px',
      }}
    >
      <div
        style={{
          display: 'flex',
          alignItems: 'baseline',
          gap: 10,
          flexWrap: 'wrap',
          marginBottom: 14,
        }}
      >
        <span
          style={{
            fontSize: 10.5,
            fontWeight: 700,
            letterSpacing: '0.12em',
            textTransform: 'uppercase',
            color: 'var(--ink-muted)',
            fontFamily: "'JetBrains Mono', ui-monospace, monospace",
          }}
        >
          Ce que cet article est
        </span>
        <span
          title={GENRE_DEFINITION[n.genre]}
          style={{
            fontSize: 14.5,
            fontWeight: 700,
            color: couleur,
            letterSpacing: '-0.01em',
            cursor: 'help',
          }}
        >
          {GENRE_LABEL[n.genre]}
        </span>
      </div>

      <Ligne intitule="Repose sur">{n.repose}</Ligne>
      <Ligne intitule="N’établit pas" dernier>
        {n.netablit}
      </Ligne>
    </div>
  );
}

function Ligne({
  intitule,
  children,
  dernier,
}: {
  intitule: string;
  children: React.ReactNode;
  dernier?: boolean;
}) {
  return (
    <div style={{ marginBottom: dernier ? 0 : 10 }}>
      <span
        style={{
          fontSize: 11,
          fontWeight: 700,
          letterSpacing: '0.05em',
          textTransform: 'uppercase',
          color: 'var(--ink-muted)',
          fontFamily: "'JetBrains Mono', ui-monospace, monospace",
          marginRight: 8,
        }}
      >
        {intitule}
      </span>
      <span style={{ fontSize: 14.5, color: 'var(--ink-soft)', lineHeight: 1.65 }}>
        {children}
      </span>
    </div>
  );
}
