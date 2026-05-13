'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X } from 'lucide-react';
import SearchCommand from '@/components/SearchCommand';

const NAV_ITEMS = [
  { label: 'Q.G.', href: '/headquarters', num: '01' },
  { label: 'OBS', href: '/observatory', num: '02' },
  { label: 'BIBLIO', href: '/library', num: '03' },
  { label: 'LAB', href: '/lab', num: '04' },
  { label: 'NEXUS', href: '/nexus', num: '\u2B21' },
];

export default function Navigation() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 10);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <nav className={`fixed top-0 left-0 right-0 z-40 transition-all duration-300 border-b ${
        scrolled
          ? 'bg-[#0A1020]/95 backdrop-blur-md border-[rgba(0,200,255,0.08)]'
          : 'bg-[#0A1020] border-[rgba(0,200,255,0.08)]'
      }`}>
        <div className="max-w-[1100px] mx-auto px-6 h-14 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="relative w-9 h-9 flex items-center justify-center">
              <svg viewBox="0 0 30 30" fill="none" className="absolute inset-0 w-full h-full">
                <polygon points="15,2 27,9 27,21 15,28 3,21 3,9" stroke="rgba(0,200,255,0.35)" strokeWidth="1.2" fill="rgba(0,200,255,0.05)" className="group-hover:stroke-[rgba(0,200,255,0.7)] transition-all" />
              </svg>
              <span className="relative z-10 text-[12px] font-bold text-[#00C8FF]" style={{fontFamily: 'Orbitron, sans-serif'}}>TEI</span>
            </div>
            <span className="hidden lg:block text-[13px] tracking-[0.12em] text-[#C8D8E8]/50" style={{fontFamily: 'Orbitron, sans-serif'}}>
              TERRE ÉTENDUE
            </span>
          </Link>

          {/* Desktop nav tabs */}
          <div className="hidden md:flex items-center gap-1.5">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`text-[11px] tracking-[0.1em] px-5 py-2 transition-all relative ${
                    isActive
                      ? 'text-[#00C8FF] bg-[rgba(0,200,255,0.1)] border border-[rgba(0,200,255,0.25)]'
                      : 'text-[#C8D8E8]/40 hover:text-[#C8D8E8]/70 border border-transparent'
                  }`}
                  style={{
                    fontFamily: 'Orbitron, sans-serif',
                    clipPath: 'polygon(8px 0, 100% 0, calc(100% - 8px) 100%, 0 100%)',
                  }}
                >
                  <span className="opacity-40 mr-1.5">{item.num}</span>
                  {item.label}
                </Link>
              );
            })}
          </div>

          {/* Search + Status + mobile burger */}
          <div className="flex items-center gap-4">
            <SearchCommand />
            <div className="hidden sm:flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-[#00E87B] shadow-[0_0_8px_#00E87B] animate-[pulse-dot_2s_ease-in-out_infinite]" />
              <span className="text-[11px] text-[#C8D8E8]/30" style={{fontFamily: 'Share Tech Mono, monospace'}}>ONLINE</span>
            </div>
            <button onClick={() => setMobileOpen(!mobileOpen)} className="md:hidden p-1.5 text-[#C8D8E8]/50">
              {mobileOpen ? <X size={20} /> : <Menu size={20} />}
            </button>
          </div>
        </div>
      </nav>

      {/* Mobile menu */}
      <AnimatePresence>
        {mobileOpen && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              className="fixed inset-0 bg-black/80 z-40 md:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 250 }}
              className="fixed right-0 top-0 bottom-0 w-64 bg-[#0A1020] border-l border-[rgba(0,200,255,0.08)] z-50 md:hidden p-6"
            >
              <div className="flex justify-end mb-8">
                <button onClick={() => setMobileOpen(false)} className="p-1.5 text-[#C8D8E8]/40"><X size={18} /></button>
              </div>
              <nav className="space-y-1">
                {NAV_ITEMS.map((item, i) => {
                  const isActive = pathname === item.href;
                  return (
                    <motion.div key={item.href} initial={{ opacity: 0, x: 16 }} animate={{ opacity: 1, x: 0 }} transition={{ delay: i * 0.05 }}>
                      <Link
                        href={item.href}
                        onClick={() => setMobileOpen(false)}
                        className={`flex items-center gap-3 px-4 py-3 text-sm transition-colors ${
                          isActive ? 'bg-[rgba(0,200,255,0.08)] text-[#00C8FF]' : 'text-[#C8D8E8]/35 hover:text-[#C8D8E8]/60'
                        }`}
                        style={{ fontFamily: 'Orbitron, sans-serif', fontSize: '10px', letterSpacing: '0.1em' }}
                      >
                        <span className="opacity-30 w-5">{item.num}</span>{item.label}
                      </Link>
                    </motion.div>
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
