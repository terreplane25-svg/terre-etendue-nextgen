'use client';
import { useState, useEffect, useRef } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, ChevronDown } from 'lucide-react';
import SearchCommand from '@/components/SearchCommand';

const SECTIONS = [
  {
    label: 'Bibliothèque', href: '/library', color: '#D4943A',
    subs: [
      { label: '📖 Coran & Sunna', href: '/library?filter=coran' },
      { label: '🕌 Textes historiques', href: '/library?filter=historique' },
      { label: '🌍 Cosmographie', href: '/library?filter=cosmographie' },
    ],
  },
  {
    label: 'Centre de Recherche', href: '/headquarters', color: '#8B7EC8',
    subs: [
      { label: '🧠 Épistémologie', href: '/headquarters?filter=epistemologie' },
      { label: '🔬 Méthode zététique', href: '/headquarters?filter=zetetique' },
      { label: '❓ Remise en question', href: '/headquarters?filter=question' },
    ],
  },
  {
    label: 'Observatoire', href: '/observatory', color: '#3B8FD4',
    subs: [
      { label: '🔭 Optique & horizon', href: '/observatory?filter=optique' },
      { label: '🌊 Hydrologie', href: '/observatory?filter=hydrologie' },
      { label: '🌙 Astronomie', href: '/observatory?filter=astronomie' },
    ],
  },
  {
    label: 'Expériences', href: '/experiences', color: '#C45E6A',
    subs: [
      { label: '💧 Fluides & matière', href: '/experiences?filter=fluides' },
      { label: '🔭 Optique & perspective', href: '/experiences?filter=optique' },
      { label: '👁 L\'œil humain', href: '/experiences?filter=oeil' },
      { label: '⚡ Forces & interactions', href: '/experiences?filter=forces' },
    ],
  },
  {
    label: 'Outils', href: '/lab', color: '#3D9E7C',
    subs: [],
  },
  {
    label: 'À propos', href: '/about', color: '#8B8F96',
    subs: [],
  },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [openDropdown, setOpenDropdown] = useState<string | null>(null);
  const [mobileExpanded, setMobileExpanded] = useState<string | null>(null);
  const [visible, setVisible] = useState(true);
  const lastScrollY = useRef(0);
  const timeoutRef = useRef<ReturnType<typeof setTimeout>>(undefined);

  useEffect(() => {
    const onScroll = () => {
      const y = window.scrollY;
      if (y < 80) {
        setVisible(true);
      } else if (y > lastScrollY.current + 5) {
        setVisible(false);
      } else if (y < lastScrollY.current - 5) {
        setVisible(true);
      }
      lastScrollY.current = y;
    };
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  return (
    <>
      <header style={{
        position: 'sticky', top: 0, zIndex: 90,
        background: '#fff',
        borderBottom: '1px solid #E8EAED',
        transform: visible ? 'translateY(0)' : 'translateY(-100%)',
        transition: 'transform 0.3s cubic-bezier(0.32, 0.72, 0, 1)',
      }}>
        {/* Single bar: logo + nav + search */}
        <div style={{ maxWidth: 1280, margin: '0 auto', padding: '0 20px', display: 'flex', alignItems: 'center', gap: 0 }}>
          {/* Logo */}
          <Link href="/" style={{
            fontSize: 20, fontWeight: 800, color: '#111', letterSpacing: '-0.02em',
            whiteSpace: 'nowrap', marginRight: 20, padding: '12px 0',
            flexShrink: 0,
          }}>
            Terre Étendue <span style={{ color: '#3D9E7C', fontWeight: 800 }}>Islam</span>
          </Link>

          {/* Desktop nav */}
          <nav className="hidden lg:flex" style={{ alignItems: 'center', gap: 0, flex: 1, minWidth: 0 }}>
            {SECTIONS.map(s => {
              const active = pathname === s.href || pathname?.startsWith(s.href + '/');
              return (
                <div
                  key={s.href}
                  style={{ position: 'relative' }}
                  onMouseEnter={() => {
                    if (s.subs.length > 0) {
                      if (timeoutRef.current) clearTimeout(timeoutRef.current);
                      setOpenDropdown(s.href);
                    }
                  }}
                  onMouseLeave={() => {
                    timeoutRef.current = setTimeout(() => setOpenDropdown(null), 150);
                  }}
                >
                  <Link href={s.href} style={{
                    display: 'flex', alignItems: 'center', gap: 4,
                    padding: '14px 11px',
                    fontSize: 14, fontWeight: 600,
                    color: active ? s.color : '#1A1D23',
                    borderBottom: active ? `3px solid ${s.color}` : '3px solid transparent',
                    transition: 'color 0.15s',
                    whiteSpace: 'nowrap',
                  }}>
                    {s.label}
                    {s.subs.length > 0 && <ChevronDown size={12} style={{ opacity: 0.4 }} />}
                  </Link>

                  {openDropdown === s.href && s.subs.length > 0 && (
                    <div style={{
                      position: 'absolute', top: '100%', left: 0, zIndex: 100,
                      background: '#fff', border: '1px solid #E8EAED', borderRadius: 10,
                      padding: '8px 0', minWidth: 240,
                      boxShadow: '0 8px 32px rgba(0,0,0,0.08)',
                      animation: 'fadeIn 0.15s ease',
                    }}>
                      {s.subs.map(sub => (
                        <Link key={sub.href} href={sub.href} style={{
                          display: 'block', padding: '10px 20px',
                          fontSize: 14, fontWeight: 500, color: '#1A1D23',
                          transition: 'background 0.1s',
                        }}
                        onMouseOver={e => { e.currentTarget.style.background = '#F4F5F7'; e.currentTarget.style.color = s.color; }}
                        onMouseOut={e => { e.currentTarget.style.background = 'transparent'; e.currentTarget.style.color = '#1A1D23'; }}>
                          {sub.label}
                        </Link>
                      ))}
                    </div>
                  )}
                </div>
              );
            })}
          </nav>

          {/* Search — pushed to the right */}
          <div style={{ marginLeft: 'auto', flexShrink: 0, display: 'flex', alignItems: 'center', gap: 8 }}>
            <div className="hidden sm:block">
              <SearchCommand inline />
            </div>
            <div className="sm:hidden">
              <SearchCommand />
            </div>
          </div>

          {/* Mobile hamburger */}
          <button className="lg:hidden" onClick={() => setMobileOpen(!mobileOpen)}
            style={{ padding: '12px 0 12px 12px', background: 'none', border: 'none', cursor: 'pointer', color: '#1A1D23' }}>
            {mobileOpen ? <X size={24} /> : <Menu size={24} />}
          </button>
        </div>
        {/* Accent line */}
        <div style={{ height: 3, background: 'linear-gradient(90deg, #D4943A, #8B7EC8, #3B8FD4, #C45E6A, #3D9E7C)' }} />
      </header>

      {/* Mobile menu */}
      {mobileOpen && (
        <div className="lg:hidden" style={{
          position: 'fixed', top: 0, left: 0, right: 0, bottom: 0, zIndex: 89,
          background: '#fff', overflowY: 'auto', paddingTop: 60,
        }}>
          <div style={{ padding: '12px 24px' }}>
            {SECTIONS.map(s => (
              <div key={s.href} style={{ borderBottom: '1px solid #F0F1F3' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                  <Link href={s.href} onClick={() => setMobileOpen(false)}
                    style={{ display: 'block', padding: '14px 0', fontSize: 17, fontWeight: 700, color: '#1A1D23', flex: 1 }}>
                    {s.label}
                  </Link>
                  {s.subs.length > 0 && (
                    <button onClick={() => setMobileExpanded(mobileExpanded === s.href ? null : s.href)}
                      style={{ padding: 8, background: 'none', border: 'none', cursor: 'pointer', color: '#8B8F96' }}>
                      <ChevronDown size={18} style={{
                        transform: mobileExpanded === s.href ? 'rotate(180deg)' : 'rotate(0)',
                        transition: 'transform 0.2s',
                      }} />
                    </button>
                  )}
                </div>
                {mobileExpanded === s.href && s.subs.length > 0 && (
                  <div style={{ paddingBottom: 8 }}>
                    {s.subs.map(sub => (
                      <Link key={sub.href} href={sub.href} onClick={() => setMobileOpen(false)}
                        style={{ display: 'block', padding: '8px 0 8px 16px', fontSize: 15, color: '#1A1D23' }}>
                        {sub.label}
                      </Link>
                    ))}
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </>
  );
}
