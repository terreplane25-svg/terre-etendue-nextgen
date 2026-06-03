'use client';
import { useState, useEffect } from 'react';
import { AnimatePresence, motion } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Search } from 'lucide-react';

const BEZ = 'cubic-bezier(0.32, 0.72, 0, 1)';
const LINKS = [
  { label: 'Quartier Général', href: '/headquarters', num: '01', color: '#7C6FC4' },
  { label: 'Observatoire', href: '/observatory', num: '02', color: '#3580C0' },
  { label: 'Bibliothèque', href: '/library', num: '03', color: '#C48A2E' },
  { label: 'Lab', href: '/lab', num: '04', color: '#3A8F6E' },
  { label: 'Expériences', href: '/experiences', num: '05', color: '#B85460' },
];

export default function DashboardNav() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  useEffect(() => {
    const fn = () => setScrolled(window.scrollY > 40);
    window.addEventListener('scroll', fn, { passive: true });
    return () => window.removeEventListener('scroll', fn);
  }, []);

  return (
    <>
      <nav style={{
        position: 'fixed', top: scrolled ? 12 : 20, left: '50%', transform: 'translateX(-50%)',
        zIndex: 40, display: 'flex', alignItems: 'center', gap: 4,
        padding: '6px 8px 6px 22px', borderRadius: 99, maxWidth: 'calc(100vw - 32px)',
        background: scrolled ? 'rgba(255,255,255,0.88)' : 'rgba(255,255,255,0.65)',
        backdropFilter: 'blur(24px) saturate(1.8)',
        border: '1px solid rgba(20,18,16,0.06)',
        boxShadow: scrolled ? '0 4px 28px rgba(0,0,0,0.06)' : '0 2px 12px rgba(0,0,0,0.02)',
        transition: `all 0.7s ${BEZ}`,
      }}>
        <Link href="/" style={{ fontSize: 15, fontWeight: 800, marginRight: 14, letterSpacing: '-0.01em', whiteSpace: 'nowrap' }}>
          Terre Étendue <span style={{ color: '#7C6FC4', fontWeight: 600 }}>Islam</span>
        </Link>
        <div className="hidden md:flex" style={{ alignItems: 'center', gap: 2 }}>
          {LINKS.map(l => {
            const active = pathname === l.href || pathname?.startsWith(l.href + '/');
            return (
              <Link key={l.href} href={l.href} style={{
                padding: '7px 13px', borderRadius: 99, fontSize: 12, fontWeight: 600,
                background: active ? l.color + '12' : 'transparent',
                color: active ? l.color : '#8A857D',
                transition: `all 0.4s ${BEZ}`, whiteSpace: 'nowrap',
              }}>{l.label}</Link>
            );
          })}
        </div>
        <div className="hidden sm:flex" style={{
          padding: '6px 13px', borderRadius: 99, background: 'rgba(20,18,16,0.04)',
          fontSize: 12, color: '#BAB5AC', alignItems: 'center', gap: 5, cursor: 'pointer', marginLeft: 6,
        }}><Search size={12} /><span>Rechercher</span></div>
        <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden"
          style={{ background: 'none', border: 'none', cursor: 'pointer', color: '#8A857D', padding: 6, marginLeft: 4 }}>
          {mobileOpen ? <X size={18} /> : <Menu size={18} />}
        </button>
      </nav>

      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div initial={{ opacity: 0 }} animate={{ opacity: 1 }} exit={{ opacity: 0 }}
              style={{ position: 'fixed', inset: 0, background: 'rgba(0,0,0,0.25)', backdropFilter: 'blur(8px)', zIndex: 50 }}
              className="md:hidden" onClick={() => setMobileOpen(false)} />
            <motion.div initial={{ x: '100%' }} animate={{ x: 0 }} exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 28, stiffness: 280 }}
              style={{ position: 'fixed', right: 0, top: 0, bottom: 0, width: 280, background: '#fff', zIndex: 55, padding: 28 }} className="md:hidden">
              <button onClick={() => setMobileOpen(false)} style={{ float: 'right', background: 'none', border: 'none', cursor: 'pointer', color: '#BAB5AC' }}><X size={18} /></button>
              <nav style={{ marginTop: 48, display: 'flex', flexDirection: 'column', gap: 4 }}>
                {LINKS.map((l, i) => (
                  <motion.div key={l.href} initial={{ opacity: 0, x: 20 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                    <Link href={l.href} onClick={() => setMobileOpen(false)} style={{
                      display: 'block', padding: '10px 14px', borderRadius: 12, fontSize: 14, fontWeight: 600,
                      color: pathname === l.href ? l.color : '#8A857D',
                      background: pathname === l.href ? l.color + '0A' : 'transparent',
                    }}>{l.label}</Link>
                  </motion.div>
                ))}
              </nav>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
