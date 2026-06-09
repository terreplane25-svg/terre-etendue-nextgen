'use client';
import React, { useState, Suspense } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
import PageHero from '@/components/PageHero';
import ScrollReveal from '@/components/ui/ScrollReveal';

const CurvatureCalc = dynamic(() => import('@/components/lab/CurvatureCalc'), { ssr: false });
const FlatEarthSim = dynamic(() => import('@/components/lab/FlatEarthSim'), { ssr: false });
const GeoHelioSim = dynamic(() => import('@/components/lab/GeoHelioSim'), { ssr: false });
const PerspectiveSim = dynamic(() => import('@/components/lab/PerspectiveSim'), { ssr: false });
const DensitySim = dynamic(() => import('@/components/lab/DensitySim'), { ssr: false });
const VisualFieldSim = dynamic(() => import('@/components/lab/VisualFieldSim'), { ssr: false });
const LaserLakeSim = dynamic(() => import('@/components/lab/LaserLakeSim'), { ssr: false });

interface A { slug: string; title: string; description: string; tags: string[]; pinned: boolean; readTime: number; }

const TOOLS = [
  {
    id: 'curvature',
    label: 'Calculateur de Courbure',
    desc: "Calculez la courbure théorique avec réfraction. Graphique interactif, 6 cas réels documentés, export des résultats.",
    icon: '📐',
    color: dash.opal,
    colorSoft: dash.opalSoft,
    tags: ['courbure', 'réfraction', 'graphique'],
  },
  {
    id: 'perspective',
    label: 'Perspective vs Courbure',
    desc: "Comparez la disparition par perspective (point de fuite) et par courbure (occultation). Deux modèles côte à côte.",
    icon: '👁️',
    color: dash.lavender,
    colorSoft: dash.lavenderSoft,
    tags: ['perspective', 'point de fuite', '3D'],
  },
  {
    id: 'density',
    label: 'Simulateur de Densité',
    desc: "Colonne de fluides interactive. Lâchez des objets et observez la flottabilité par densité relative.",
    icon: '⚗️',
    color: dash.opal,
    colorSoft: dash.opalSoft,
    tags: ['densité', 'flottabilité', 'Archimède'],
  },
  {
    id: 'visualfield',
    label: 'Champ Visuel & Résolution',
    desc: "Calculez la taille angulaire d'un objet et la distance maximale de résolution de l'œil humain (1 arc-minute).",
    icon: '🔬',
    color: dash.rose,
    colorSoft: dash.roseSoft,
    tags: ['vision', 'arc-minute', 'résolution'],
  },
  {
    id: 'laser',
    label: 'Laser sur Lac',
    desc: "Simulation des expériences laser sur eau calme. Comparez trajectoire droite (plan) vs écart de courbure (globe).",
    icon: '🔴',
    color: dash.rose,
    colorSoft: dash.roseSoft,
    tags: ['laser', 'eau', 'courbure'],
  },
  {
    id: 'flat',
    label: 'Terre Plane — Vue du Dessus',
    desc: "Carte azimutale avec Soleil et Lune. Éphémérides réelles, tropiques, saisons et date en temps réel.",
    icon: '🗺️',
    color: dash.saffron,
    colorSoft: dash.saffronSoft,
    tags: ['3D', 'carte', 'éphémérides'],
  },
  {
    id: 'geo',
    label: 'Modèle Planétaire',
    desc: "8 planètes avec orbites réelles, anneaux de Saturne, vitesses orbitales. Mode classique ou vortex galactique.",
    icon: '🪐',
    color: dash.cyan,
    colorSoft: dash.cyanSoft,
    tags: ['3D', 'planètes', 'orbites'],
  },
];

const EXCLUDED_PATTERNS = ['mgpp', 'modele-geostationnaire', 'monde-plat-et-du-paradis'];

function ToolCard({ tool, active, onClick }: { tool: typeof TOOLS[0]; active: boolean; onClick: () => void }) {
  return (
    <button
      onClick={onClick}
      className="dash-card"
      style={{
        padding: '20px 20px',
        textAlign: 'left' as const,
        cursor: 'pointer',
        width: '100%',
        border: active ? `2px solid ${tool.color}` : `1px solid ${dash.border}`,
        background: active ? tool.colorSoft : dash.card,
        transition: 'all 0.25s ease',
        position: 'relative' as const,
        overflow: 'hidden' as const,
      }}
    >
      {active && (
        <div style={{
          position: 'absolute', top: 0, left: 0, width: 4, height: '100%',
          background: tool.color,
        }} />
      )}
      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 10 }}>
        <div style={{
          width: 42, height: 42, borderRadius: 12,
          background: active ? tool.color + '20' : tool.colorSoft,
          display: 'flex', alignItems: 'center', justifyContent: 'center',
          fontSize: 20, flexShrink: 0,
        }}>{tool.icon}</div>
        <div>
          <div style={{
            fontSize: 15, fontWeight: 700,
            color: active ? tool.color : dash.ink,
            lineHeight: 1.3,
          }}>{tool.label}</div>
        </div>
      </div>
      <div style={{
        fontSize: 13, color: dash.inkMuted, lineHeight: 1.5,
        marginBottom: 10,
      }}>{tool.desc}</div>
      <div style={{ display: 'flex', gap: 6, flexWrap: 'wrap' as const }}>
        {tool.tags.map(tag => (
          <span key={tag} style={{
            fontSize: 10, fontWeight: 600, fontFamily: dash.fontMono,
            padding: '3px 8px', borderRadius: 6,
            background: active ? tool.color + '15' : dash.bg,
            color: active ? tool.color : dash.inkGhost,
          }}>{tag}</span>
        ))}
      </div>
    </button>
  );
}

function SimulatorLoader() {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: 400, background: dash.bg, borderRadius: 16,
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: 40, height: 40, borderRadius: '50%',
          border: `3px solid ${dash.border}`, borderTopColor: dash.opal,
          animation: 'spin 0.8s linear infinite',
          margin: '0 auto 12px',
        }} />
        <div style={{ fontSize: 13, color: dash.inkMuted, fontFamily: dash.fontMono }}>
          Chargement du simulateur...
        </div>
      </div>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}

export default function LabClient({ articles }: { articles: A[] }) {
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const filtered = articles.filter(a => !EXCLUDED_PATTERNS.some(p => a.slug.includes(p)));

  const renderSimulator = () => {
    switch (activeTool) {
      case 'curvature': return <CurvatureCalc />;
      case 'perspective': return <PerspectiveSim />;
      case 'density': return <DensitySim />;
      case 'visualfield': return <VisualFieldSim />;
      case 'laser': return <LaserLakeSim />;
      case 'flat': return <FlatEarthSim />;
      case 'geo': return <GeoHelioSim />;
      default: return null;
    }
  };

  const activeToolData = TOOLS.find(t => t.id === activeTool);
  const isDarkBg = ['curvature', 'flat', 'geo', 'perspective', 'density', 'visualfield', 'laser'].includes(activeTool || '');

  return (
    <div>
      <PageHero
        title="Outils & Simulateurs"
        subtitle="7 simulateurs interactifs — modélisation 3D, calcul et visualisation"
        color={dash.opal}
        image="https://green-gnat-134443.hostingersite.com/wp-content/uploads/2025/10/cropped-entete-logo-e1760704486721.png"
      />

      <div style={{ maxWidth: 1100, margin: '0 auto', padding: '0 24px 64px' }}>

        {/* Stats bar */}
        <ScrollReveal delay={100}>
          <div className="dash-card" style={{
            display: 'flex', alignItems: 'center', gap: 24,
            padding: '16px 24px', marginBottom: 32,
            flexWrap: 'wrap',
          }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
              <span style={{
                fontSize: 11, fontWeight: 700, fontFamily: dash.fontMono,
                color: dash.opal, letterSpacing: '0.08em',
              }}>PILIER 04</span>
              <span style={{ fontSize: 11, color: dash.inkGhost }}>—</span>
              <span style={{ fontSize: 13, fontWeight: 600, color: dash.ink }}>
                Modélisation & Calcul
              </span>
            </div>
            <div style={{ marginLeft: 'auto', display: 'flex', gap: 20 }}>
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: dash.ink }}>{TOOLS.length}</div>
                <div style={{ fontSize: 10, color: dash.inkGhost, fontFamily: dash.fontMono }}>OUTILS</div>
              </div>
              <div style={{ width: 1, background: dash.border }} />
              <div style={{ textAlign: 'center' }}>
                <div style={{ fontSize: 20, fontWeight: 800, color: dash.ink }}>{filtered.length}</div>
                <div style={{ fontSize: 10, color: dash.inkGhost, fontFamily: dash.fontMono }}>ARTICLES</div>
              </div>
            </div>
          </div>
        </ScrollReveal>

        {/* Section title */}
        <ScrollReveal delay={150}>
          <div style={{ marginBottom: 20 }}>
            <h2 style={{ fontSize: 22, fontWeight: 800, color: dash.ink, marginBottom: 6 }}>
              Simulateurs Interactifs
            </h2>
            <p style={{ fontSize: 14, color: dash.inkMuted, lineHeight: 1.6 }}>
              Sélectionnez un outil pour l&apos;ouvrir. Chaque simulateur est interactif et paramétrable.
            </p>
          </div>
        </ScrollReveal>

        {/* Tool cards grid */}
        <div style={{
          display: 'grid',
          gridTemplateColumns: 'repeat(auto-fit, minmax(260px, 1fr))',
          gap: 14,
          marginBottom: 24,
        }}>
          {TOOLS.map((tool, i) => (
            <ScrollReveal key={tool.id} delay={200 + i * 60}>
              <ToolCard
                tool={tool}
                active={activeTool === tool.id}
                onClick={() => setActiveTool(activeTool === tool.id ? null : tool.id)}
              />
            </ScrollReveal>
          ))}
        </div>

        {/* Active simulator */}
        <AnimatePresence mode="wait">
          {activeTool && (
            <motion.div
              key={activeTool}
              initial={{ opacity: 0, y: 20, scale: 0.98 }}
              animate={{ opacity: 1, y: 0, scale: 1 }}
              exit={{ opacity: 0, y: -10, scale: 0.98 }}
              transition={{ duration: 0.35, ease: [0.32, 0.72, 0, 1] }}
              style={{ marginBottom: 40 }}
            >
              {/* Simulator header */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '14px 20px',
                background: activeToolData!.colorSoft,
                borderRadius: '16px 16px 0 0',
                borderBottom: `1px solid ${activeToolData!.color}25`,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 18 }}>{activeToolData!.icon}</span>
                  <span style={{
                    fontSize: 14, fontWeight: 700, color: activeToolData!.color,
                  }}>{activeToolData!.label}</span>
                  <span style={{
                    fontSize: 9, fontFamily: dash.fontMono, fontWeight: 600,
                    padding: '3px 8px', borderRadius: 6,
                    background: activeToolData!.color + '18',
                    color: activeToolData!.color,
                    letterSpacing: '0.06em',
                  }}>INTERACTIF</span>
                </div>
                <button
                  onClick={() => setActiveTool(null)}
                  style={{
                    width: 30, height: 30, borderRadius: 8,
                    border: `1px solid ${activeToolData!.color}30`,
                    background: 'transparent',
                    color: activeToolData!.color,
                    fontSize: 16, cursor: 'pointer',
                    display: 'flex', alignItems: 'center', justifyContent: 'center',
                  }}
                >
                  ✕
                </button>
              </div>

              {/* Simulator body */}
              <div style={{
                background: isDarkBg ? '#080E1A' : dash.card,
                borderRadius: '0 0 16px 16px',
                padding: 20,
                border: `1px solid ${dash.border}`,
                borderTop: 'none',
                overflow: 'hidden',
              }}>
                <Suspense fallback={<SimulatorLoader />}>
                  {renderSimulator()}
                </Suspense>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Prompt to select if nothing active */}
        {!activeTool && (
          <ScrollReveal delay={500}>
            <div style={{
              textAlign: 'center',
              padding: '48px 24px',
              background: dash.bg,
              borderRadius: 16,
              marginBottom: 40,
              border: `1px dashed ${dash.border}`,
            }}>
              <div style={{ fontSize: 36, marginBottom: 12 }}>△</div>
              <div style={{ fontSize: 15, fontWeight: 600, color: dash.inkSoft, marginBottom: 6 }}>
                Sélectionnez un outil ci-dessus
              </div>
              <div style={{ fontSize: 13, color: dash.inkGhost }}>
                Le simulateur s&apos;ouvrira ici avec tous ses contrôles interactifs
              </div>
            </div>
          </ScrollReveal>
        )}

        {/* Articles section */}
        {filtered.length > 0 && (
          <ScrollReveal delay={300}>
            <div style={{ marginTop: 24 }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 12,
                marginBottom: 20, paddingBottom: 12,
                borderBottom: `1px solid ${dash.border}`,
              }}>
                <h2 style={{ fontSize: 20, fontWeight: 800, color: dash.ink }}>
                  Publications du Lab
                </h2>
                <span style={{
                  fontSize: 11, fontFamily: dash.fontMono, fontWeight: 600,
                  padding: '3px 10px', borderRadius: 6,
                  background: dash.opalSoft, color: dash.opal,
                }}>{filtered.length} articles</span>
              </div>

              <div style={{ display: 'flex', flexDirection: 'column', gap: 14 }}>
                {filtered.map((a, i) => (
                  <motion.div
                    key={a.slug}
                    initial={{ opacity: 0, y: 8 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.1 + i * 0.04 }}
                  >
                    <Link href={`/article/${a.slug}`} className="dash-card" style={{
                      display: 'flex', overflow: 'hidden', cursor: 'pointer',
                    }}>
                      <div style={{
                        width: 180, minHeight: 130, flexShrink: 0, overflow: 'hidden',
                      }}>
                        <img
                          src={getArticleImage(a.slug)}
                          alt=""
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          loading="lazy"
                        />
                      </div>
                      <div style={{ padding: '18px 24px', flex: 1, minWidth: 0 }}>
                        <div style={{
                          fontSize: 16, fontWeight: 700, color: dash.ink,
                          marginBottom: 6, lineHeight: 1.35,
                        }}>{a.title}</div>
                        {a.description && (
                          <div style={{
                            fontSize: 13, color: dash.inkMuted, lineHeight: 1.5,
                            marginBottom: 8,
                            overflow: 'hidden', textOverflow: 'ellipsis',
                            display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any,
                          }}>{a.description}</div>
                        )}
                        <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                          <span style={{
                            fontSize: 11, color: dash.inkGhost, fontFamily: dash.fontMono,
                          }}>{a.readTime} min de lecture</span>
                          {a.pinned && (
                            <span style={{
                              fontSize: 10, fontWeight: 600, fontFamily: dash.fontMono,
                              padding: '2px 8px', borderRadius: 4,
                              background: dash.saffronSoft, color: dash.saffron,
                            }}>RECOMMANDÉ</span>
                          )}
                        </div>
                      </div>
                    </Link>
                  </motion.div>
                ))}
              </div>
            </div>
          </ScrollReveal>
        )}
      </div>
    </div>
  );
}
