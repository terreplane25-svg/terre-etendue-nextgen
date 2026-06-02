'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Search } from 'lucide-react';
import { dash, PILLARS } from '@/lib/design-tokens';

const NAV_LINKS = PILLARS.map(p => ({ label: p.name.replace(/^(Le |La |Les |L')/, ''), href: p.href, num: p.num, color: p.color }));

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
      <nav className="dash-nav" style={{
        boxShadow: scrolled ? '0 1px 8px rgba(0,0,0,0.04)' : 'none',
      }}>
        <div style={{ maxWidth: 1200, margin: '0 auto', padding: '0 24px', height: '100%', display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
          {/* Logo */}
          <Link href="/" style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div style={{
              width: 32, height: 32, borderRadius: 8, background: dash.ink,
              display: 'flex', alignItems: 'center', justifyContent: 'center',
              fontSize: 11, fontWeight: 800, color: '#fff', letterSpacing: '0.05em',
              fontFamily: dash.fontMain,
            }}>TEI</div>
            <span style={{ fontSize: 13, fontWeight: 600, color: dash.inkSoft, fontFamily: dash.fontMain }}
              className="hidden sm:inline">Terre Étendue</span>
          </Link>

          {/* Desktop links */}
          <div className="hidden md:flex" style={{ alignItems: 'center', gap: 2 }}>
            {NAV_LINKS.map(link => {
              const active = pathname === link.href || pathname?.startsWith(link.href + '/');
              return (
                <Link key={link.href} href={link.href} style={{
                  padding: '7px 14px', borderRadius: 8, fontSize: 12, fontWeight: 600,
                  fontFamily: dash.fontMain,
                  background: active ? dash.ink : 'transparent',
                  color: active ? '#fff' : dash.inkMuted,
                  transition: 'all 0.2s',
                }}>
                  <span style={{ fontFamily: dash.fontMono, fontSize: 10, opacity: 0.5, marginRight: 4 }}>{link.num}</span>
                  {link.label}
                </Link>
              );
            })}
          </div>

          {/* Right side */}
          <div style={{ display: 'flex', alignItems: 'center', gap: 10 }}>
            <div className="hidden sm:flex" style={{
              padding: '6px 14px', borderRadius: 8, background: dash.bg,
              border: `1px solid ${dash.border}`, fontSize: 12, color: dash.inkGhost,
              fontFamily: dash.fontMain, alignItems: 'center', gap: 6, cursor: 'pointer',
            }}>
              <Search size={13} strokeWidth={2} />
              <span>Rechercher...</span>
            </div>
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
            <motion.div
              initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.3)', zIndex: 50 }}
              className="md:hidden" onClick={() => setMobileOpen(false)}
            />
            <motion.div
              initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 300 }}
              style={{
                position: 'fixed', right: 0, top: 0, bottom: 0, width: 280,
                background: dash.card, borderLeft: `1px solid ${dash.borderSoft}`,
                zIndex: 55, padding: 24,
              }} className="md:hidden"
            >
              <div style={{ display: 'flex', justifyContent: 'flex-end', marginBottom: 24 }}>
                <button onClick={() => setMobileOpen(false)} style={{ background: 'none', border: 'none', cursor: 'pointer', color: dash.inkGhost }}>
                  <X size={18} />
                </button>
              </div>
              <nav style={{ display: 'flex', flexDirection: 'column', gap: 4 }}>
                {NAV_LINKS.map(link => {
                  const active = pathname === link.href;
                  return (
                    <Link key={link.href} href={link.href} onClick={() => setMobileOpen(false)} style={{
                      display: 'flex', alignItems: 'center', gap: 10, padding: '10px 14px',
                      borderRadius: 8, fontSize: 13, fontWeight: active ? 700 : 500,
                      fontFamily: dash.fontMain,
                      background: active ? dash.bg : 'transparent',
                      color: active ? dash.ink : dash.inkMuted,
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
