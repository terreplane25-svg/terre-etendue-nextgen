'use client';
import React from 'react';
import Link from 'next/link';
import { getArticleImage } from '@/lib/article-images';
import ArticleCarousel from '@/components/ArticleCarousel';

interface A { slug: string; title: string; description: string; category: string; tags: string[]; readTime: number; date: string; pinned: boolean; }

const CAT_LABEL: Record<string, string> = { headquarters: 'Centre de Recherche', observatory: 'Observatoire', library: 'Bibliothèque', lab: 'Outils', experiences: 'Expériences', meta: 'TEI' };
const CAT_COLOR: Record<string, string> = { headquarters: '#8B7EC8', observatory: '#3B8FD4', library: '#D4943A', lab: '#3D9E7C', experiences: '#C45E6A', meta: '#8B8F96' };

const ISLAMIC_SLUGS = [
  'debut-de-la-creation-selon-le-coran-et-la-sunna',
  'debut-de-la-creation-le-soleil-mobile-la-terre-immobile',
  'la-terre-dans-le-coran',
  'pres-de-cent-savants-de-lislam',
  'dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne',
  'la-qibla-et-la-direction-cote-ouest',
  'la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre',
];


function fmtDate(d: string) {
  try { return new Date(d).toLocaleDateString('fr-FR', { day: 'numeric', month: 'short', year: 'numeric' }); }
  catch { return ''; }
}

function SectionTitle({ color, children }: { color: string; children: React.ReactNode }) {
  return (
    <div style={{ display: 'flex', alignItems: 'center', gap: 14, marginBottom: 28 }}>
      <div style={{ width: 5, height: 34, background: color, borderRadius: 2 }} />
      <h2 style={{ fontSize: 'clamp(1.6rem, 3vw, 2.25rem)', fontWeight: 800, color: 'var(--ink)', letterSpacing: '-0.02em', margin: 0 }}>{children}</h2>
    </div>
  );
}

export default function HomeClient({ articles }: { articles: A[] }) {
  // Le protocole était écarté d'ici parce qu'il avait son propre bandeau plus
  // haut, et l'afficher deux fois sur le même écran n'aurait rien apporté. Ce
  // bandeau ouvre maintenant le simulateur : sans cette réintégration,
  // l'article disparaîtrait de la page d'accueil au lieu d'y descendre.
  const nonIslamic = articles.filter(a => !ISLAMIC_SLUGS.includes(a.slug));
  const featured = nonIslamic.slice(0, 3);
  const latest = nonIslamic.slice(3, 15);



  return (
    <div>
      {/* ═══ HERO ═══ */}
      <div style={{
        background: 'linear-gradient(180deg, rgba(13,21,40,0.42) 0%, rgba(13,21,40,0.34) 45%, rgba(13,21,40,0.60) 100%), url("https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/07/StockCake-Horizon_de_Lever_de_Soleil_Ethere-297875-standard.jpg") center/cover no-repeat',
        padding: '132px 24px 104px',
        borderBottom: '3px solid',
        borderImage: 'linear-gradient(90deg, #D4943A, #8B7EC8, #3B8FD4, #C45E6A, #3D9E7C) 1',
      }}>
        <div style={{ maxWidth: 1120, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            display: 'inline-block',
            fontSize: 12, fontWeight: 700, letterSpacing: '0.18em', textTransform: 'uppercase',
            color: '#5CE0B0', marginBottom: 22,
            fontFamily: "'JetBrains Mono', monospace",
            background: 'rgba(13,21,40,0.55)', border: '1px solid rgba(92,224,176,0.35)',
            padding: '7px 16px', borderRadius: 100, backdropFilter: 'blur(4px)',
          }}>
            Revue indépendante de cosmologie
          </div>
          <h1 style={{
            fontSize: 'clamp(2.75rem, 6.5vw, 5rem)', fontWeight: 900, color: '#F4F8FC', letterSpacing: '-0.03em',
            lineHeight: 1.06, marginBottom: 26,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
            textShadow: '0 2px 28px rgba(0,0,0,0.6)',
          }}>
            Explorer la création,<br />honorer la Révélation
          </h1>
          <p style={{
            fontSize: 'clamp(1.05rem, 1.6vw, 1.3rem)', color: '#E6ECF4', lineHeight: 1.6, maxWidth: 720,
            margin: '0 auto',
            textShadow: '0 1px 14px rgba(0,0,0,0.6)',
          }}>
            La cosmologie coranique et la science moderne, examinées avec la même rigueur.
          </p>
          <div style={{ marginTop: 38, display: 'flex', justifyContent: 'center', gap: 16, flexWrap: 'wrap' }}>
            <Link href="/library" style={{
              fontSize: 15.5, fontWeight: 700, color: '#0D1528', background: '#4FD1A0',
              padding: '15px 30px', borderRadius: 10, boxShadow: '0 6px 24px rgba(79,209,160,0.35)',
            }}>
              Commencer l’exploration
            </Link>
            <Link href="/article/participer-aux-campagnes-de-mesure" style={{
              fontSize: 15.5, fontWeight: 700, color: '#F4F8FC', background: 'rgba(255,255,255,0.08)',
              padding: '15px 30px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.35)',
              backdropFilter: 'blur(4px)',
            }}>
              Participer aux mesures
            </Link>
          </div>
        </div>
      </div>

      {/* ═══ COMMENCER PAR LE SIMULATEUR (pleine largeur, tonalité foncée) ═══
          Ce bandeau portait le protocole. Un document de 38 pages est ce qu'on
          lit APRÈS avoir compris la question, pas ce qu'on rencontre en
          arrivant : il ouvre maintenant l'outil qui rend la question tangible
          en trois champs, et le protocole reste à un clic. */}
      <div id="simulateur" style={{ background: '#0D1528', borderBottom: '1px solid #1a2540' }}>
        <div style={{ maxWidth: 1120, margin: '0 auto', padding: '96px 24px' }}>
          <div style={{
            display: 'inline-block', fontSize: 11.5, fontWeight: 700, letterSpacing: '0.16em',
            textTransform: 'uppercase', color: '#4FD1A0', marginBottom: 20,
            fontFamily: "'JetBrains Mono', monospace",
            border: '1px solid rgba(79,209,160,0.4)', padding: '6px 14px', borderRadius: 100,
          }}>
            Par où commencer — Simulateur de visée
          </div>

          <h2 style={{
            fontSize: 'clamp(1.75rem, 3.4vw, 2.6rem)', fontWeight: 800, color: '#F4F8FC',
            letterSpacing: '-0.025em', lineHeight: 1.15, margin: '0 0 22px', maxWidth: 860,
          }}>
            Ce que vous devriez voir, avant d’aller le regarder
          </h2>

          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 18px' }}>
            «&nbsp;Voit-on encore le bâtiment à cette distance&nbsp;?&nbsp;» appelle une réponse par oui
            ou par non, et une réponse par oui ou par non se laisse expliquer par la brume, l’objectif,
            le contraste ou l’heure. Le simulateur pose la question autrement&nbsp;: deux positions,
            deux hauteurs, et&nbsp;
            <strong style={{ color: '#F4F8FC' }}>quelle part de la cible chaque modèle prédit qu’on
            devrait voir</strong> — le sphérique et le plat, côte à côte.
          </p>
          <p style={{ fontSize: 17, color: '#a8b8cc', lineHeight: 1.7, maxWidth: 760, margin: '0 0 34px' }}>
            Ce qui compte n’est pas la valeur, c’est <strong style={{ color: '#F4F8FC' }}>l’écart entre
            les deux</strong>. S’il est trop faible, aucune photographie ne les départagera, et le
            simulateur le dit au lieu de laisser croire à une observation décisive. Le seuil est
            explicite&nbsp;: la part masquée à la base doit dépasser 10&nbsp;% de la hauteur de la
            cible. Au-delà, la visée est discriminante — et il reste à aller la photographier.
          </p>
          <div style={{ display: 'flex', gap: 14, flexWrap: 'wrap', alignItems: 'center' }}>
            <Link href="/lab?sim=visee-optique" style={{
              fontSize: 15.5, fontWeight: 700, color: '#0D1528', background: '#4FD1A0',
              padding: '15px 30px', borderRadius: 10, boxShadow: '0 6px 24px rgba(79,209,160,0.3)',
            }}>
              Ouvrir le simulateur
            </Link>
            <Link href="/article/les-protocoles-ce-que-c-est-et-pourquoi" style={{
              fontSize: 15, fontWeight: 700, color: '#F4F8FC', background: 'rgba(255,255,255,0.06)',
              padding: '15px 26px', borderRadius: 10, border: '1px solid rgba(255,255,255,0.22)',
            }}>
              Comprendre le protocole
            </Link>
          </div>

          <p style={{ fontSize: 13.5, color: '#6f829c', lineHeight: 1.65, marginTop: 26, maxWidth: 760 }}>
            Géométrie seule&nbsp;: distance géodésique, altitudes, réfraction atmosphérique
            (k&nbsp;=&nbsp;0,13 par défaut, ajustable). Aucun relief n’est modélisé — un obstacle
            local relève de l’analyse de l’image réelle. Le simulateur <strong>prédit</strong>&nbsp;;
            il ne mesure rien, et ne conclut sur aucun modèle.
          </p>
        </div>
      </div>

      {/* ═══ À LA UNE ═══ */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '96px 24px 0' }}>
        <SectionTitle color="#8B7EC8">À la une</SectionTitle>
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(320px, 1fr))', gap: 24 }}>
          {featured.map(a => (
            <Link key={a.slug} href={`/article/${a.slug}`} style={{
              position: 'relative', borderRadius: 12, overflow: 'hidden',
              display: 'block', minHeight: 300,
            }}>
              <img src={getArticleImage(a.slug)} alt="" style={{ width: '100%', height: '100%', objectFit: 'cover', position: 'absolute', inset: 0 }} />
              <div style={{ position: 'absolute', inset: 0, background: 'linear-gradient(to top, rgba(0,0,0,0.78) 0%, transparent 62%)' }} />
              <div style={{ position: 'absolute', bottom: 0, left: 0, right: 0, padding: '24px 22px' }}>
                <span style={{ fontSize: 10.5, fontWeight: 700, color: CAT_COLOR[a.category] || '#8B8F96', textTransform: 'uppercase', letterSpacing: '0.06em' }}>
                  {CAT_LABEL[a.category] || a.category}
                </span>
                <h3 style={{ fontSize: 20, fontWeight: 750, color: '#fff', lineHeight: 1.28, marginTop: 6 }}>{a.title}</h3>
                <div style={{ fontSize: 12, color: 'rgba(255,255,255,0.6)', marginTop: 8 }}>
                  {fmtDate(a.date)} · {a.readTime} min
                </div>
              </div>
            </Link>
          ))}
        </div>
      </div>

      {/* ═══ DERNIÈRES PUBLICATIONS ═══ */}
      <div style={{ maxWidth: 1200, margin: '0 auto', padding: '96px 24px 100px' }}>
        <SectionTitle color="#3B8FD4">Dernières publications</SectionTitle>
        <ArticleCarousel articles={latest} />
      </div>
    </div>
  );
}
