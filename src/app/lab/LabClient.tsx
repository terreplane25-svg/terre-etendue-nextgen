'use client';
import React, { useState, Suspense, useEffect, useCallback } from 'react';
import Link from 'next/link';
import dynamic from 'next/dynamic';
import { motion, AnimatePresence } from 'framer-motion';
import { dash } from '@/lib/design-tokens';
import { getArticleImage } from '@/lib/article-images';
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
    id: 'flat',
    label: 'Carte Azimutale',
    desc: "Carte azimutale avec dôme céleste, éphémérides, terminateur, phases lunaires, boussole et géolocalisation.",
    icon: '🗺️',
    color: '#D4943A',
    num: '01',
    tags: ['3D', 'dôme', 'éphémérides', 'carte'],
  },
  {
    id: 'curvature',
    label: 'Calculateur de Courbure',
    desc: "Courbure théorique avec réfraction. Graphique interactif, 6 cas réels, export.",
    icon: '📐',
    color: '#3D9E7C',
    num: '02',
    tags: ['courbure', 'réfraction', 'graphique'],
  },
  {
    id: 'perspective',
    label: 'Perspective vs Courbure',
    desc: "Disparition par perspective vs occultation par courbure. Deux modèles côte à côte.",
    icon: '👁️',
    color: '#8B7EC8',
    num: '03',
    tags: ['perspective', 'point de fuite', '3D'],
  },
  {
    id: 'density',
    label: 'Simulateur de Densité',
    desc: "Colonne de fluides interactive. Lâchez des objets, observez la flottabilité.",
    icon: '⚗️',
    color: '#3D9E7C',
    num: '04',
    tags: ['densité', 'flottabilité', 'Archimède'],
  },
  {
    id: 'visualfield',
    label: 'Champ Visuel',
    desc: "Taille angulaire et distance maximale de résolution de l'œil humain.",
    icon: '🔬',
    color: '#C45E6A',
    num: '05',
    tags: ['vision', 'arc-minute', 'résolution'],
  },
  {
    id: 'laser',
    label: 'Laser sur Lac',
    desc: "Expériences laser sur eau calme. Trajectoire droite vs écart de courbure.",
    icon: '🔴',
    color: '#C45E6A',
    num: '06',
    tags: ['laser', 'eau', 'courbure'],
  },
  {
    id: 'geo',
    label: 'Système Solaire',
    desc: "8 planètes, anneaux de Saturne, vitesses orbitales. Classique ou vortex.",
    icon: '🪐',
    color: '#3B8FD4',
    num: '07',
    tags: ['3D', 'planètes', 'orbites'],
  },
];

const EXCLUDED_PATTERNS = ['mgpp', 'modele-geostationnaire', 'monde-plat-et-du-paradis'];

function ToolCard({ tool, active, onClick }: { tool: typeof TOOLS[0]; active: boolean; onClick: () => void }) {
  return (
    <motion.button
      onClick={onClick}
      whileHover={{ y: -1 }}
      transition={{ duration: 0.2 }}
      style={{
        padding: 0,
        textAlign: 'left' as const,
        cursor: 'pointer',
        width: '100%',
        border: active ? `1.5px solid ${tool.color}` : `1px solid ${dash.border}`,
        background: active ? tool.color + '08' : '#FFFFFF',
        borderRadius: 6,
        position: 'relative' as const,
        overflow: 'hidden' as const,
        boxShadow: active ? `0 0 0 1px ${tool.color}20` : 'none',
      }}
    >
      {/* Top accent bar */}
      <div style={{
        height: 3,
        background: active ? tool.color : tool.color + '30',
        transition: 'background 0.2s ease',
      }} />
      <div style={{ padding: '14px 16px 16px' }}>
        <div style={{ display: 'flex', alignItems: 'flex-start', justifyContent: 'space-between', marginBottom: 8 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <span style={{ fontSize: 18 }}>{tool.icon}</span>
            <div style={{
              fontSize: 13, fontWeight: 700,
              color: active ? tool.color : dash.ink,
              lineHeight: 1.3,
            }}>{tool.label}</div>
          </div>
          <span style={{
            fontSize: 9, fontFamily: dash.fontMono, fontWeight: 700,
            color: tool.color, opacity: 0.5,
            letterSpacing: '0.05em',
          }}>{tool.num}</span>
        </div>
        <div style={{
          fontSize: 12, color: dash.inkMuted, lineHeight: 1.5,
          marginBottom: 10,
        }}>{tool.desc}</div>
        <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' as const }}>
          {tool.tags.map(tag => (
            <span key={tag} style={{
              fontSize: 9, fontWeight: 600, fontFamily: dash.fontMono,
              padding: '2px 6px', borderRadius: 3,
              background: active ? tool.color + '12' : '#F4F5F7',
              color: active ? tool.color : dash.inkGhost,
              letterSpacing: '0.02em',
            }}>{tag}</span>
          ))}
        </div>
      </div>
    </motion.button>
  );
}

function SimulatorLoader() {
  return (
    <div style={{
      display: 'flex', alignItems: 'center', justifyContent: 'center',
      minHeight: 400,
    }}>
      <div style={{ textAlign: 'center' }}>
        <div style={{
          width: 32, height: 32, borderRadius: '50%',
          border: `2px solid ${dash.border}`, borderTopColor: dash.opal,
          animation: 'spin 0.8s linear infinite',
          margin: '0 auto 10px',
        }} />
        <div style={{ fontSize: 11, color: dash.inkMuted, fontFamily: dash.fontMono }}>
          Chargement...
        </div>
      </div>
      <style>{`@keyframes spin{to{transform:rotate(360deg)}}`}</style>
    </div>
  );
}

export default function LabClient({ articles }: { articles: A[] }) {
  const [activeTool, setActiveTool] = useState<string | null>(null);
  const filtered = articles.filter(a => !EXCLUDED_PATTERNS.some(p => a.slug.includes(p)));

  useEffect(()=>{
    if (activeTool) {
      document.body.style.overflow = 'hidden';
    } else {
      document.body.style.overflow = '';
    }
    return ()=>{ document.body.style.overflow = ''; };
  },[activeTool]);

  const handleEsc = useCallback((e: KeyboardEvent)=>{
    if (e.key === 'Escape' && activeTool) setActiveTool(null);
  },[activeTool]);

  useEffect(()=>{
    document.addEventListener('keydown', handleEsc);
    return ()=>document.removeEventListener('keydown', handleEsc);
  },[handleEsc]);

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

  return (
    <div style={{ background: '#F4F5F7', minHeight: '100vh' }}>

      {/* ── HEADER ── */}
      <div style={{
        background: '#0D1528',
        padding: '40px 24px 36px',
        borderBottom: '1px solid #1a2540',
      }}>
        <div style={{ maxWidth: 960, margin: '0 auto' }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 8 }}>
            <span style={{
              fontSize: 10, fontFamily: dash.fontMono, fontWeight: 700,
              color: '#3D9E7C', letterSpacing: '0.12em',
              padding: '3px 8px', border: '1px solid #3D9E7C40', borderRadius: 3,
            }}>PILIER 04</span>
            <div style={{ width: 24, height: 1, background: '#607890' }} />
            <span style={{ fontSize: 10, fontFamily: dash.fontMono, color: '#607890', letterSpacing: '0.08em' }}>
              MODÉLISATION & CALCUL
            </span>
          </div>
          <h1 style={{
            fontSize: 28, fontWeight: 800, color: '#C8D8E8',
            letterSpacing: '-0.01em', marginBottom: 6,
          }}>
            Outils & Simulateurs
          </h1>
          <div style={{ display: 'flex', alignItems: 'center', gap: 16 }}>
            <p style={{ fontSize: 14, color: '#607890', lineHeight: 1.5 }}>
              {TOOLS.length} simulateurs interactifs — modélisation 3D, calcul et visualisation
            </p>
            <div style={{
              display: 'flex', gap: 8, marginLeft: 'auto',
            }}>
              {[dash.opal, dash.lavender, dash.rose, dash.saffron, dash.cyan].map((c, i) => (
                <div key={i} style={{ width: 6, height: 6, borderRadius: 1, background: c, opacity: 0.6 }} />
              ))}
            </div>
          </div>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: '0 auto', padding: '28px 24px 64px' }}>

        {/* ── TOOL CARDS GRID ── */}
        <ScrollReveal delay={100}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: 10,
            marginBottom: 20,
          }}>
            {TOOLS.slice(0, 4).map((tool, i) => (
              <ToolCard
                key={tool.id}
                tool={tool}
                active={activeTool === tool.id}
                onClick={() => setActiveTool(activeTool === tool.id ? null : tool.id)}
              />
            ))}
          </div>
        </ScrollReveal>
        <ScrollReveal delay={160}>
          <div style={{
            display: 'grid',
            gridTemplateColumns: 'repeat(auto-fill, minmax(240px, 1fr))',
            gap: 10,
            marginBottom: 28,
          }}>
            {TOOLS.slice(4).map((tool, i) => (
              <ToolCard
                key={tool.id}
                tool={tool}
                active={activeTool === tool.id}
                onClick={() => setActiveTool(activeTool === tool.id ? null : tool.id)}
              />
            ))}
          </div>
        </ScrollReveal>

        {/* ── ACTIVE SIMULATOR (fullscreen overlay) ── */}
        <AnimatePresence mode="wait">
          {activeTool && activeToolData && (
            <motion.div
              key={activeTool}
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.25 }}
              style={{
                position: 'fixed', top: 0, left: 0, right: 0, bottom: 0,
                zIndex: 9999, display: 'flex', flexDirection: 'column',
                background: '#080E1A',
              }}
            >
              {/* Sim header bar (sticky top) */}
              <div style={{
                display: 'flex', alignItems: 'center', justifyContent: 'space-between',
                padding: '8px 16px',
                background: '#0D1528',
                borderBottom: `2px solid ${activeToolData.color}`,
                flexShrink: 0,
              }}>
                <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
                  <span style={{ fontSize: 15 }}>{activeToolData.icon}</span>
                  <span style={{
                    fontSize: 13, fontWeight: 700, color: '#C8D8E8',
                    fontFamily: dash.fontMono,
                  }}>{activeToolData.label}</span>
                  <span style={{
                    fontSize: 8, fontFamily: dash.fontMono, fontWeight: 700,
                    padding: '2px 6px', borderRadius: 2,
                    background: activeToolData.color + '25',
                    color: activeToolData.color,
                    letterSpacing: '0.08em',
                  }}>INTERACTIF</span>
                </div>
                <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                  <button
                    onClick={() => setActiveTool(null)}
                    style={{
                      padding: '4px 12px', borderRadius: 4,
                      border: `1px solid #607890`,
                      background: 'transparent',
                      color: '#C8D8E8',
                      fontSize: 11, fontWeight: 600, cursor: 'pointer',
                      fontFamily: dash.fontMono,
                      letterSpacing: '0.05em',
                    }}
                  >
                    ✕ FERMER
                  </button>
                </div>
              </div>

              {/* Sim body (fills remaining space, scrollable) */}
              <div style={{
                flex: 1, overflow: 'auto',
                padding: '16px 20px 24px',
              }}>
                <Suspense fallback={<SimulatorLoader />}>
                  {renderSimulator()}
                </Suspense>
              </div>
            </motion.div>
          )}
        </AnimatePresence>

        {/* Prompt when nothing selected */}
        {!activeTool && (
          <ScrollReveal delay={250}>
            <div style={{
              textAlign: 'center',
              padding: '36px 24px',
              background: '#FFFFFF',
              borderRadius: 6,
              marginBottom: 32,
              border: `1px dashed ${dash.border}`,
            }}>
              <div style={{ fontSize: 11, fontFamily: dash.fontMono, color: dash.inkGhost, letterSpacing: '0.08em' }}>
                SÉLECTIONNEZ UN OUTIL CI-DESSUS
              </div>
            </div>
          </ScrollReveal>
        )}

        {/* ── ARTICLES ── */}
        {filtered.length > 0 && (
          <ScrollReveal delay={300}>
            <div style={{ marginTop: 8 }}>
              <div style={{
                display: 'flex', alignItems: 'center', gap: 10,
                marginBottom: 16, paddingBottom: 10,
                borderBottom: `1px solid ${dash.border}`,
              }}>
                <h2 style={{ fontSize: 18, fontWeight: 800, color: dash.ink, margin: 0 }}>
                  Publications
                </h2>
                <span style={{
                  fontSize: 10, fontFamily: dash.fontMono, fontWeight: 600,
                  padding: '2px 8px', borderRadius: 3,
                  background: dash.opalSoft, color: dash.opal,
                }}>{filtered.length}</span>
              </div>

              <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fill, minmax(320px, 1fr))', gap: 10 }}>
                {filtered.map((a, i) => (
                  <motion.div
                    key={a.slug}
                    initial={{ opacity: 0, y: 6 }}
                    animate={{ opacity: 1, y: 0 }}
                    transition={{ delay: 0.05 + i * 0.03 }}
                  >
                    <Link href={`/article/${a.slug}`} style={{
                      display: 'flex', overflow: 'hidden', cursor: 'pointer',
                      background: '#FFFFFF', borderRadius: 6,
                      border: `1px solid ${dash.border}`,
                      textDecoration: 'none',
                      transition: 'box-shadow 0.2s ease',
                    }}
                    onMouseEnter={e => (e.currentTarget.style.boxShadow = '0 2px 12px rgba(0,0,0,0.06)')}
                    onMouseLeave={e => (e.currentTarget.style.boxShadow = 'none')}
                    >
                      <div style={{
                        width: 120, minHeight: 90, flexShrink: 0, overflow: 'hidden',
                      }}>
                        <img
                          src={getArticleImage(a.slug)}
                          alt=""
                          style={{ width: '100%', height: '100%', objectFit: 'cover' }}
                          loading="lazy"
                        />
                      </div>
                      <div style={{ padding: '12px 16px', flex: 1, minWidth: 0 }}>
                        <div style={{
                          fontSize: 14, fontWeight: 700, color: dash.ink,
                          marginBottom: 4, lineHeight: 1.35,
                          overflow: 'hidden', textOverflow: 'ellipsis',
                          display: '-webkit-box', WebkitLineClamp: 2, WebkitBoxOrient: 'vertical' as any,
                        }}>{a.title}</div>
                        <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                          <span style={{
                            fontSize: 10, color: dash.inkGhost, fontFamily: dash.fontMono,
                          }}>{a.readTime} min</span>
                          {a.pinned && (
                            <span style={{
                              fontSize: 9, fontWeight: 600, fontFamily: dash.fontMono,
                              padding: '1px 6px', borderRadius: 2,
                              background: dash.saffronSoft, color: dash.saffron,
                            }}>REC</span>
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
