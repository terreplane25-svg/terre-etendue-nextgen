'use client';

import React, { useCallback, useEffect, useState } from 'react';
import useEmblaCarousel from 'embla-carousel-react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';

interface Article {
  slug: string;
  title: string;
  description: string;
  category?: string;
  tags?: string[];
  readTime: number;
  date?: string;
  pinned?: boolean;
}

interface ArticleCarouselProps {
  articles: Article[];
  title?: string;
  color?: string;
  badgeLabel?: (a: Article) => string | null;
  badgeColor?: string;
  footer?: (a: Article) => React.ReactNode;
  showDate?: boolean;
}

const CAT_LABEL: Record<string, string> = {
  headquarters: 'Centre de Recherche',
  observatory: 'Observatoire',
  library: 'Bibliothèque',
  lab: 'Outils',
  experiences: 'Expériences',
  meta: 'TEI',
};

const CAT_COLOR: Record<string, string> = {
  headquarters: '#8B7EC8',
  observatory: '#3B8FD4',
  library: '#D4943A',
  lab: '#3D9E7C',
  experiences: '#C45E6A',
  meta: '#8B8F96',
};

function fmtDate(d: string) {
  try {
    return new Date(d).toLocaleDateString('fr-FR', {
      day: 'numeric',
      month: 'short',
      year: 'numeric',
    });
  } catch {
    return '';
  }
}

export default function ArticleCarousel({
  articles,
  title,
  color = '#3B8FD4',
  badgeLabel,
  badgeColor,
  footer,
  showDate = true,
}: ArticleCarouselProps) {
  const [emblaRef, emblaApi] = useEmblaCarousel({
    align: 'start',
    slidesToScroll: 1,
    containScroll: 'trimSnaps',
    breakpoints: {
      '(max-width: 768px)': { dragFree: true },
    },
  });

  const [canPrev, setCanPrev] = useState(false);
  const [canNext, setCanNext] = useState(false);
  const [current, setCurrent] = useState(0);

  const onSelect = useCallback(() => {
    if (!emblaApi) return;
    setCanPrev(emblaApi.canScrollPrev());
    setCanNext(emblaApi.canScrollNext());
    setCurrent(emblaApi.selectedScrollSnap());
  }, [emblaApi]);

  useEffect(() => {
    if (!emblaApi) return;
    onSelect();
    emblaApi.on('select', onSelect);
    emblaApi.on('reInit', onSelect);
    return () => {
      emblaApi.off('select', onSelect);
      emblaApi.off('reInit', onSelect);
    };
  }, [emblaApi, onSelect]);

  const scrollPrev = useCallback(() => emblaApi?.scrollPrev(), [emblaApi]);
  const scrollNext = useCallback(() => emblaApi?.scrollNext(), [emblaApi]);
  const scrollTo = useCallback((i: number) => emblaApi?.scrollTo(i), [emblaApi]);

  const snapCount = emblaApi?.scrollSnapList().length ?? 0;

  return (
    <div>
      {/* Header with arrows */}
      <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 20 }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
          {title && (
            <>
              <div style={{ width: 4, height: 28, background: color, borderRadius: 2 }} />
              <h2 style={{ fontSize: 22, fontWeight: 800, color: 'var(--ink)' }}>{title}</h2>
            </>
          )}
        </div>
        <div style={{ display: 'flex', gap: 8 }}>
          <button
            onClick={scrollPrev}
            disabled={!canPrev}
            aria-label="Précédent"
            style={{
              width: 36, height: 36, borderRadius: '50%',
              border: '1px solid var(--border)',
              background: 'var(--card)',
              color: canPrev ? 'var(--ink)' : 'var(--ink-ghost)',
              cursor: canPrev ? 'pointer' : 'default',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18, transition: 'all 0.2s',
              opacity: canPrev ? 1 : 0.4,
            }}
          >
            ‹
          </button>
          <button
            onClick={scrollNext}
            disabled={!canNext}
            aria-label="Suivant"
            style={{
              width: 36, height: 36, borderRadius: '50%',
              border: '1px solid var(--border)',
              background: 'var(--card)',
              color: canNext ? 'var(--ink)' : 'var(--ink-ghost)',
              cursor: canNext ? 'pointer' : 'default',
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 18, transition: 'all 0.2s',
              opacity: canNext ? 1 : 0.4,
            }}
          >
            ›
          </button>
        </div>
      </div>

      {/* Carousel viewport */}
      <div ref={emblaRef} style={{ overflow: 'hidden' }}>
        <div style={{ display: 'flex', gap: 16 }}>
          {articles.map(a => {
            const label = badgeLabel ? badgeLabel(a) : (a.category ? (CAT_LABEL[a.category] || a.category) : null);
            const bColor = badgeColor || (a.category ? (CAT_COLOR[a.category] || '#8B8F96') : color);
            const footerNode = footer ? footer(a) : null;

            return (
              <div
                key={a.slug}
                style={{ flex: '0 0 auto', width: 300, minWidth: 0 }}
                className="sm:!w-[320px] lg:!w-[340px]"
              >
                <div
                  style={{
                    borderRadius: 10,
                    overflow: 'hidden',
                    background: 'var(--card)',
                    border: '1px solid var(--border)',
                    transition: 'box-shadow 0.2s, border-color 0.2s',
                    height: '100%',
                    display: 'flex',
                    flexDirection: 'column',
                  }}
                  className="carousel-card"
                >
                  <Link
                    href={`/article/${a.slug}`}
                    style={{ display: 'block', flex: 1 }}
                  >
                    <div style={{ position: 'relative', aspectRatio: '16/10', overflow: 'hidden' }}>
                      <img
                        src={getArticleImage(a.slug)}
                        alt=""
                        loading="lazy"
                        style={{
                          width: '100%', height: '100%',
                          objectFit: 'cover', display: 'block',
                          transition: 'transform 0.3s',
                        }}
                        className="carousel-card-img"
                      />
                      <div style={{
                        position: 'absolute', inset: 0,
                        background: 'linear-gradient(to top, rgba(0,0,0,0.55) 0%, transparent 50%)',
                      }} />
                      {label && (
                        <span style={{
                          position: 'absolute', bottom: 12, left: 14,
                          fontSize: 10, fontWeight: 700,
                          color: bColor,
                          textTransform: 'uppercase', letterSpacing: '0.06em',
                          background: 'rgba(0,0,0,0.5)',
                          padding: '3px 8px', borderRadius: 4,
                          backdropFilter: 'blur(4px)',
                        }}>
                          {label}
                        </span>
                      )}
                      {a.pinned && (
                        <span style={{
                          position: 'absolute', top: 12, right: 14,
                          fontSize: 10, fontWeight: 700, color: '#D4943A',
                          background: 'rgba(0,0,0,0.5)',
                          padding: '3px 8px', borderRadius: 4,
                          backdropFilter: 'blur(4px)',
                        }}>
                          ★
                        </span>
                      )}
                    </div>
                    <div style={{ padding: '14px 16px 18px' }}>
                      <h3 style={{
                        fontSize: 15, fontWeight: 700, color: 'var(--ink)',
                        lineHeight: 1.35, marginBottom: 6,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}>
                        {a.title}
                      </h3>
                      <p style={{
                        fontSize: 13, color: 'var(--ink-soft)',
                        lineHeight: 1.5, marginBottom: 10,
                        display: '-webkit-box',
                        WebkitLineClamp: 2,
                        WebkitBoxOrient: 'vertical',
                        overflow: 'hidden',
                      }}>
                        {a.description}
                      </p>
                      <div style={{ fontSize: 11, color: 'var(--ink-muted)', fontFamily: "'JetBrains Mono', monospace" }}>
                        {showDate && a.date ? `${fmtDate(a.date)} · ` : ''}{a.readTime} min
                      </div>
                    </div>
                  </Link>
                  {footerNode && (
                    <div style={{ padding: '10px 16px 14px', borderTop: '1px solid var(--border-soft)' }}>
                      {footerNode}
                    </div>
                  )}
                </div>
              </div>
            );
          })}
        </div>
      </div>

      {/* Dot indicators */}
      {snapCount > 1 && (
        <div style={{ display: 'flex', justifyContent: 'center', gap: 6, marginTop: 20 }}>
          {Array.from({ length: snapCount }).map((_, i) => (
            <button
              key={i}
              onClick={() => scrollTo(i)}
              aria-label={`Aller au groupe ${i + 1}`}
              style={{
                width: current === i ? 20 : 8,
                height: 8,
                borderRadius: 4,
                border: 'none',
                background: current === i ? color : 'var(--border)',
                cursor: 'pointer',
                transition: 'all 0.3s',
                padding: 0,
              }}
            />
          ))}
        </div>
      )}
    </div>
  );
}
