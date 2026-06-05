'use client';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Search, Menu, X } from 'lucide-react';

const SECTIONS = [
  { label: 'Centre de Recherche', href: '/headquarters', color: '#7C6FC4',
    subs: ['Épistémologie', 'Méthode zététique', 'Remise en question'] },
  { label: 'Observatoire', href: '/observatory', color: '#3580C0',
    subs: ['Optique', 'Horizon', 'Perspective', 'Visibilité', 'Mécanique'] },
  { label: 'Bibliothèque', href: '/library', color: '#C48A2E',
    subs: ['Coran & Sunna', 'Textes historiques', 'Cosmographie'] },
  { label: 'Outils', href: '/lab', color: '#3A8F6E', subs: [] },
  { label: 'Expériences', href: '/experiences', color: '#B85460',
    subs: ['Fluides & matière', 'Optique & perspective', 'Œil humain', 'Forces'] },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const [openMenu, setOpenMenu] = useState<string | null>(null);
  const [mobileOpen, setMobileOpen] = useState(false);

  return (
    <>
      <header style={{ background: '#fff', borderBottom: '1px solid #eee' }}>
        {/* Top bar */}
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '14px 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          <Link href="/" style={{ fontSize: 22, fontWeight: 800, color: '#141210', letterSpacing: '-0.02em', fontFamily: "'Plus Jakarta Sans', sans-serif" }}>
            Terre Étendue <span style={{ color: '#7C6FC4', fontWeight: 700 }}>Islam</span>
          </Link>
          <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
            <div className="hidden sm:flex" style={{ alignItems: 'center', gap: 8, padding: '7px 14px', borderRadius: 6, border: '1px solid #e5e5e5', fontSize: 14, color: '#999' }}>
              <Search size={15} /><span>Rechercher...</span>
            </div>
          </div>
        </div>

        {/* Nav bar */}
        <div style={{ borderTop: '1px solid #eee' }}>
          <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
            <div className="hidden md:flex" style={{ alignItems: 'center', gap: 0 }}>
              {SECTIONS.map(s => {
                const active = pathname === s.href || pathname?.startsWith(s.href + '/');
                return (
                  <div key={s.href} style={{ position: 'relative' }}
                    onMouseEnter={() => s.subs.length > 0 ? setOpenMenu(s.href) : null}
                    onMouseLeave={() => setOpenMenu(null)}>
                    <Link href={s.href} style={{
                      display: 'flex', alignItems: 'center', gap: 4,
                      padding: '14px 18px', fontSize: 14, fontWeight: 600,
                      color: active ? s.color : '#3D3A35',
                      borderBottom: active ? `3px solid ${s.color}` : '3px solid transparent',
                      fontFamily: "'Plus Jakarta Sans', sans-serif",
                    }}>
                      {s.label}
                      {s.subs.length > 0 && <span style={{ fontSize: 10, opacity: 0.5 }}>▼</span>}
                    </Link>

                    {/* Dropdown */}
                    {openMenu === s.href && s.subs.length > 0 && (
                      <div style={{
                        position: 'absolute', top: '100%', left: 0, zIndex: 50,
                        background: '#fff', border: '1px solid #eee', borderRadius: 8,
                        padding: '12px 0', minWidth: 220, boxShadow: '0 8px 32px rgba(0,0,0,0.08)',
                      }}>
                        {s.subs.map(sub => (
                          <div key={sub} style={{
                            padding: '8px 20px', fontSize: 14, color: '#3D3A35', cursor: 'pointer',
                          }}
                          onMouseOver={e => (e.currentTarget.style.background = '#f8f8f8')}
                          onMouseOut={e => (e.currentTarget.style.background = 'transparent')}>
                            {sub}
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                );
              })}
            </div>
            <button className="md:hidden" onClick={() => setMobileOpen(!mobileOpen)}
              style={{ padding: '12px 0', background: 'none', border: 'none', cursor: 'pointer', color: '#3D3A35' }}>
              {mobileOpen ? <X size={22} /> : <Menu size={22} />}
            </button>
          </div>
          {/* Accent line */}
          <div style={{ height: 3, background: '#7C6FC4' }} />
        </div>
      </header>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="md:hidden" style={{ background: '#fff', borderBottom: '1px solid #eee', padding: '12px 24px' }}>
          {SECTIONS.map(s => (
            <Link key={s.href} href={s.href} onClick={() => setMobileOpen(false)}
              style={{ display: 'block', padding: '10px 0', fontSize: 15, fontWeight: 600, color: '#3D3A35', borderBottom: '1px solid #f5f5f5' }}>
              {s.label}
            </Link>
          ))}
        </div>
      )}
    </>
  );
}
