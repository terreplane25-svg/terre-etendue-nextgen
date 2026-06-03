'use client';
import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Search } from 'lucide-react';
import { dash } from '@/lib/design-tokens';

const NAV_LINKS = [
  { label: 'Quartier Général', href: '/headquarters', num: '01', color: dash.lavender },
  { label: 'Observatoire', href: '/observatory', num: '02', color: dash.cyan },
  { label: 'Bibliothèque', href: '/library', num: '03', color: dash.saffron },
  { label: 'Lab', href: '/lab', num: '04', color: dash.opal },
  { label: 'Expériences', href: '/experiences', num: '05', color: dash.rose },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 8);
    window.addEventListener('scroll', fn, { passive: true });
    return () => window.removeEventListener('scroll', fn);
  }, []);

  return (
    <>
      <nav className="dash-nav" style={{ boxShadow: scrolled ? '0 1px 8px rgba(0,0,0,0.04)' : 'none' }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Premium title */}
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 0 }}>
            <span style={{
              fontSize: 17, fontWeight: 800, color: dash.ink, letterSpacing: '-0.01em',
              fontFamily: dash.fontMain,
            }}>Terre Étendue <span style={{ fontWeight: 600, color: dash.lavender }}>Islam</span></span>
          </Link>

          {/* Desktop — colored links */}
          <div className="hidden md:flex" style={{ alignItems: 'center', gap: 2 }}>
            {NAV_LINKS.map(link => {
              const active = pathname === link.href || pathname?.startsWith(link.href + '/');
              return (
                <Link key={link.href} href={link.href} style={{
                  padding: '7px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                  fontFamily: dash.fontMain, transition: 'all 0.2s',
                  background: active ? link.color + '12' : 'transparent',
                  color: active ? link.color : dash.inkMuted,
                  border: active ? `1px solid ${link.color}25` : '1px solid transparent',
                }}>
                  <span style={{ fontFamily: dash.fontMono, fontSize: 10, opacity: 0.5, marginRight: 4 }}>{link.num}</span>
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="hidden sm:flex" style={{
              padding: '6px 14px', borderRadius: 8, background: dash.bg,
              border: `1px solid ${dash.border}`, fontSize: 12, color: dash.inkGhost,
              fontFamily: dash.fontMain, alignItems: 'center', gap: 6, cursor: 'pointer',
            }}><Search size={13} strokeWidth={2} /><span>Rechercher...</span></div>
            <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden"
              style={{ background: 'none', border: 'none', cursor: 'pointer', color: dash.inkMuted, padding: 4 }}>
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile drawer */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 50 }} className="md:hidden" onClick={() => setMobileOpen(false)} />
            <motion.div initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              style={{ position: 'fixed', right: 0, top: 0, bottom: 0, width: 280, background: dash.card, borderLeft: `1px solid ${dash.borderSoft}`, zIndex: 55, padding: 24 }} className="md:hidden">
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 24 }}>
                <button onClick={() => setMobileOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: dash.inkGhost }}><X size={18} /></button>
              </div>
              <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {NAV_LINKS.map(link => {
                  const active = pathname === link.href;
                  return (
                    <Link key={link.href} href={link.href} onClick={() => setMobileOpen(false)} style={{
                      display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px',
                      borderRadius: 8, fontSize: 13, fontWeight: active ? 700 : 500,
                      background: active ? link.color + '10' : 'transparent',
                      color: active ? link.color : dash.inkMuted,
                    }}>
                      <span style={{ fontFamily: dash.fontMono, fontSize: 10, opacity: 0.4, width: 20 }}>{link.num}</span>
                      {link.label}
                    </Link>
                  );
                })}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
