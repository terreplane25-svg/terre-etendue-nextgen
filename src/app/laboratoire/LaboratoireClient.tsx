'use client';
import { useState } from 'react';
import Link from 'next/link';
import { CATEGORIES, ANALYSES, type CategoryId, type AnalyseMedia } from '@/lib/lab-analyses';

const TABS = [
  { id: 'video' as const, label: 'Vidéos', icon: '🎬' },
  { id: 'image' as const, label: 'Images', icon: '🖼️' },
];

function AnalyseCard({ item }: { item: AnalyseMedia }) {
  const cat = CATEGORIES.find(c => c.id === item.category);
  const [expandedSections, setExpandedSections] = useState<Record<string, boolean>>({
    observation: true, analyse: false, demarche: false, checklist: false,
  });

  const toggle = (key: string) =>
    setExpandedSections(prev => ({ ...prev, [key]: !prev[key] }));

  const sections = [
    { key: 'observation', icon: '🔬', label: 'Observation', color: '#3B8FD4' },
    { key: 'analyse', icon: '🧪', label: 'Analyse scientifique', color: '#8B7EC8' },
    { key: 'demarche', icon: '📐', label: 'Démarche méthodologique', color: '#D4943A' },
    { key: 'checklist', icon: '✅', label: 'Checklist de rigueur', color: '#3D9E7C' },
  ];

  return (
    <div style={{
      background: 'var(--card)', border: '1px solid var(--border)',
      borderRadius: 14, overflow: 'hidden', marginBottom: 32,
    }}>
      {/* Header */}
      <div style={{ padding: '20px 24px 16px', borderBottom: '1px solid var(--border)' }}>
        <div style={{ display: 'flex', alignItems: 'center', gap: 8, marginBottom: 8 }}>
          {cat && (
            <span style={{
              fontSize: 11, fontWeight: 700, color: cat.color,
              background: cat.color + '15', padding: '3px 10px',
              borderRadius: 20, fontFamily: "'JetBrains Mono', monospace",
              textTransform: 'uppercase', letterSpacing: '0.05em',
            }}>
              {cat.icon} {cat.label}
            </span>
          )}
          <span style={{
            fontSize: 11, fontWeight: 700, color: 'var(--ink-muted)',
            background: 'var(--bg)', padding: '3px 10px',
            borderRadius: 20, fontFamily: "'JetBrains Mono', monospace",
            textTransform: 'uppercase',
          }}>
            {item.type === 'video' ? '🎬 Vidéo' : '🖼️ Image'}
          </span>
        </div>
        <h3 style={{
          fontSize: 22, fontWeight: 800, color: 'var(--ink)',
          lineHeight: 1.3, margin: 0,
          fontFamily: "'Plus Jakarta Sans', sans-serif",
        }}>
          {item.title}
        </h3>
        <div style={{
          display: 'flex', flexWrap: 'wrap', gap: 12, marginTop: 8,
          fontSize: 12, color: 'var(--ink-muted)',
          fontFamily: "'JetBrains Mono', monospace",
        }}>
          {item.location && <span>📍 {item.location}</span>}
          {item.duration && <span>⏱ {item.duration}</span>}
          {item.source && <span>📋 {item.source}</span>}
        </div>
      </div>

      {/* Media embed */}
      <div style={{ padding: '0 24px', marginTop: 20 }}>
        {item.type === 'video' && item.embedUrl && (
          <div style={{
            position: 'relative', paddingBottom: '56.25%', height: 0,
            overflow: 'hidden', borderRadius: 10, marginBottom: 20,
          }}>
            <iframe
              src={item.embedUrl}
              style={{ position: 'absolute', top: 0, left: 0, width: '100%', height: '100%', border: 0 }}
              allowFullScreen
              loading="lazy"
            />
          </div>
        )}
        {item.type === 'image' && item.imageUrl && (
          <img
            src={item.imageUrl}
            alt={item.title}
            style={{ width: '100%', borderRadius: 10, marginBottom: 20 }}
            loading="lazy"
            data-zoomable
          />
        )}
      </div>

      {/* SVG Diagram */}
      {item.svgDiagram && (
        <div style={{ padding: '0 24px', marginBottom: 20 }}>
          <div dangerouslySetInnerHTML={{ __html: item.svgDiagram }} />
        </div>
      )}

      {/* Collapsible sections */}
      <div style={{ padding: '0 24px 24px' }}>
        {sections.map(s => {
          const isOpen = expandedSections[s.key];
          return (
            <div key={s.key} style={{
              border: `1px solid ${isOpen ? s.color + '40' : 'var(--border)'}`,
              borderRadius: 10, marginBottom: 10,
              transition: 'border-color 0.2s',
            }}>
              <button
                onClick={() => toggle(s.key)}
                style={{
                  width: '100%', display: 'flex', alignItems: 'center',
                  gap: 10, padding: '14px 18px', background: 'none',
                  border: 'none', cursor: 'pointer', textAlign: 'left',
                }}
              >
                <span style={{ fontSize: 16 }}>{s.icon}</span>
                <span style={{
                  flex: 1, fontSize: 14, fontWeight: 700,
                  color: isOpen ? s.color : 'var(--ink)',
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                }}>
                  {s.label}
                </span>
                <span style={{
                  fontSize: 18, color: 'var(--ink-muted)',
                  transform: isOpen ? 'rotate(180deg)' : 'rotate(0)',
                  transition: 'transform 0.2s',
                }}>
                  ▾
                </span>
              </button>

              {isOpen && (
                <div style={{
                  padding: '0 18px 16px',
                  fontSize: 14.5, lineHeight: 1.7, color: 'var(--ink-soft)',
                  borderTop: `1px solid ${s.color}20`,
                }}>
                  {s.key === 'observation' && (
                    <p style={{ margin: '12px 0 0' }}>{item.observation}</p>
                  )}
                  {s.key === 'analyse' && (
                    <div
                      style={{ marginTop: 12 }}
                      dangerouslySetInnerHTML={{ __html: item.analyse }}
                    />
                  )}
                  {s.key === 'demarche' && (
                    <ol style={{ margin: '12px 0 0', paddingLeft: 20, display: 'flex', flexDirection: 'column', gap: 8 }}>
                      {item.demarche.map((step, i) => (
                        <li key={i} style={{ color: 'var(--ink-soft)' }}>
                          <strong style={{ color: s.color }}>{i + 1}.</strong> {step}
                        </li>
                      ))}
                    </ol>
                  )}
                  {s.key === 'checklist' && (
                    <div style={{ marginTop: 12, display: 'flex', flexDirection: 'column', gap: 6 }}>
                      {item.checklist.map((point, i) => (
                        <label key={i} style={{
                          display: 'flex', alignItems: 'flex-start', gap: 10,
                          padding: '8px 12px', borderRadius: 6,
                          background: 'var(--bg)', cursor: 'pointer',
                        }}>
                          <input type="checkbox" style={{ marginTop: 3, accentColor: s.color }} />
                          <span>{point}</span>
                        </label>
                      ))}
                    </div>
                  )}
                </div>
              )}
            </div>
          );
        })}
      </div>

      {/* Related article link */}
      {item.relatedArticle && (
        <div style={{
          padding: '12px 24px 16px',
          borderTop: '1px solid var(--border)',
          fontSize: 13, color: 'var(--ink-muted)',
        }}>
          📖 Article lié : <Link
            href={`/article/${item.relatedArticle}`}
            style={{ color: '#D4943A', fontWeight: 600 }}
          >
            Lire l&apos;article complet →
          </Link>
        </div>
      )}
    </div>
  );
}

export default function LaboratoireClient() {
  const [activeTab, setActiveTab] = useState<'video' | 'image'>('video');
  const [activeCategory, setActiveCategory] = useState<CategoryId | 'all'>('all');

  const filtered = ANALYSES.filter(a => {
    if (a.type !== activeTab) return false;
    if (activeCategory !== 'all' && a.category !== activeCategory) return false;
    return true;
  });

  const countByTab = (type: 'video' | 'image') =>
    ANALYSES.filter(a => a.type === type && (activeCategory === 'all' || a.category === activeCategory)).length;

  const countByCat = (catId: string) =>
    ANALYSES.filter(a => a.type === activeTab && (catId === 'all' || a.category === catId)).length;

  return (
    <div>
      {/* Hero */}
      <div style={{
        background: 'linear-gradient(135deg, #0D1528 0%, #1A2540 50%, #0D1528 100%)',
        padding: '100px 24px 48px',
        borderBottom: '3px solid',
        borderImage: 'linear-gradient(90deg, #3B8FD4, #8B7EC8, #D4943A, #3D9E7C) 1',
      }}>
        <div style={{ maxWidth: 800, margin: '0 auto', textAlign: 'center' }}>
          <div style={{
            fontSize: 11, fontWeight: 700, letterSpacing: '0.15em',
            textTransform: 'uppercase', color: '#8B7EC8', marginBottom: 16,
            fontFamily: "'JetBrains Mono', monospace",
          }}>
            Laboratoire d&apos;analyse
          </div>
          <h1 style={{
            fontSize: 38, fontWeight: 900, color: '#E8EDF4',
            letterSpacing: '-0.02em', lineHeight: 1.15, marginBottom: 16,
            fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}>
            Observer, analyser, vérifier
          </h1>
          <p style={{
            fontSize: 16, color: '#8A95A8', lineHeight: 1.65,
            maxWidth: 620, margin: '0 auto',
          }}>
            Chaque vidéo et chaque image est soumise à la même grille d&apos;analyse :
            observation factuelle, explication scientifique, démarche méthodologique
            et checklist de rigueur. La méthode avant la conclusion.
          </p>
        </div>
      </div>

      <div style={{ maxWidth: 960, margin: '0 auto', padding: '32px 24px 80px' }}>

        {/* Tabs */}
        <div style={{
          display: 'flex', gap: 0, marginBottom: 20,
          borderRadius: 10, overflow: 'hidden',
          border: '1px solid var(--border)',
          background: 'var(--card)',
        }}>
          {TABS.map(tab => {
            const isActive = activeTab === tab.id;
            const count = countByTab(tab.id);
            return (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                style={{
                  flex: 1, padding: '14px 20px', border: 'none',
                  cursor: 'pointer',
                  background: isActive ? '#8B7EC815' : 'transparent',
                  borderBottom: isActive ? '3px solid #8B7EC8' : '3px solid transparent',
                  color: isActive ? '#8B7EC8' : 'var(--ink-muted)',
                  fontSize: 15, fontWeight: 700,
                  fontFamily: "'Plus Jakarta Sans', sans-serif",
                  transition: 'all 0.2s',
                }}
              >
                {tab.icon} {tab.label}
                <span style={{
                  marginLeft: 8, fontSize: 11,
                  background: isActive ? '#8B7EC830' : 'var(--bg)',
                  padding: '2px 8px', borderRadius: 10,
                  fontFamily: "'JetBrains Mono', monospace",
                }}>
                  {count}
                </span>
              </button>
            );
          })}
        </div>

        {/* Category filters */}
        <div style={{
          display: 'flex', flexWrap: 'wrap', gap: 8, marginBottom: 28,
        }}>
          <button
            onClick={() => setActiveCategory('all')}
            style={{
              padding: '7px 14px', borderRadius: 20,
              border: activeCategory === 'all' ? '1.5px solid #8B7EC8' : '1px solid var(--border)',
              background: activeCategory === 'all' ? '#8B7EC815' : 'var(--card)',
              color: activeCategory === 'all' ? '#8B7EC8' : 'var(--ink-muted)',
              fontSize: 12, fontWeight: 700, cursor: 'pointer',
              fontFamily: "'JetBrains Mono', monospace",
            }}
          >
            Tous ({countByCat('all')})
          </button>
          {CATEGORIES.map(cat => {
            const isActive = activeCategory === cat.id;
            const count = countByCat(cat.id);
            return (
              <button
                key={cat.id}
                onClick={() => setActiveCategory(cat.id)}
                style={{
                  padding: '7px 14px', borderRadius: 20,
                  border: isActive ? `1.5px solid ${cat.color}` : '1px solid var(--border)',
                  background: isActive ? cat.color + '15' : 'var(--card)',
                  color: isActive ? cat.color : 'var(--ink-muted)',
                  fontSize: 12, fontWeight: 700, cursor: 'pointer',
                  fontFamily: "'JetBrains Mono', monospace",
                  opacity: count === 0 ? 0.4 : 1,
                }}
              >
                {cat.icon} {cat.label} ({count})
              </button>
            );
          })}
        </div>

        {/* Results */}
        {filtered.length === 0 ? (
          <div style={{
            textAlign: 'center', padding: '60px 20px',
            color: 'var(--ink-muted)', fontSize: 15,
          }}>
            <div style={{ fontSize: 40, marginBottom: 12 }}>🔬</div>
            <p>Aucune analyse dans cette catégorie pour l&apos;instant.</p>
            <p style={{ fontSize: 13, marginTop: 8 }}>
              Les analyses sont ajoutées progressivement.
            </p>
          </div>
        ) : (
          filtered.map(item => <AnalyseCard key={item.id} item={item} />)
        )}

        {/* Methodology box */}
        <div style={{
          background: 'linear-gradient(135deg, #1a1f2e 0%, #0d1117 100%)',
          border: '1px solid #2a3140', borderRadius: 12,
          padding: 28, marginTop: 40,
        }}>
          <h2 style={{
            fontSize: 18, fontWeight: 800, color: '#D4943A', margin: '0 0 16px',
            fontFamily: "'Plus Jakarta Sans', sans-serif",
          }}>
            📐 Principes méthodologiques
          </h2>
          <div style={{
            display: 'grid', gap: 12,
            gridTemplateColumns: 'repeat(auto-fit, minmax(280px, 1fr))',
          }}>
            {[
              { num: '01', title: 'Observer sans interpréter', text: 'Décrire ce qu\'on voit factuellement avant de proposer une explication. Séparer l\'observation du jugement.' },
              { num: '02', title: 'Documenter les conditions', text: 'Lieu, date, météo, matériel, distance, hauteur — chaque variable compte pour reproduire ou invalider.' },
              { num: '03', title: 'Considérer les alternatives', text: 'Toujours envisager au moins deux explications possibles avant de conclure. Un seul modèle n\'est pas de la science.' },
              { num: '04', title: 'Exiger la reproductibilité', text: 'Un phénomène observé une seule fois n\'est pas une preuve. La science demande la répétabilité.' },
            ].map(p => (
              <div key={p.num} style={{
                padding: 16, borderRadius: 8,
                background: 'rgba(255,255,255,0.03)',
                border: '1px solid rgba(255,255,255,0.06)',
              }}>
                <div style={{
                  fontSize: 11, fontWeight: 900, color: '#D4943A',
                  fontFamily: "'JetBrains Mono', monospace", marginBottom: 6,
                }}>
                  {p.num}
                </div>
                <div style={{
                  fontSize: 14, fontWeight: 700, color: '#e8edf4',
                  marginBottom: 6,
                }}>
                  {p.title}
                </div>
                <div style={{ fontSize: 13, color: '#8A95A8', lineHeight: 1.6 }}>
                  {p.text}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>
    </div>
  );
}
