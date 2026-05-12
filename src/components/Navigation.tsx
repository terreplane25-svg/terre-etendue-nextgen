'use client';

import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X } from 'lucide-react';

const NAV_ITEMS = [
  { label: 'Q.G.', href: '/headquarters', marker: '01' },
  { label: 'Observatoire', href: '/observatory', marker: '02' },
  { label: 'Bibliothèque', href: '/library', marker: '03' },
  { label: 'Lab', href: '/lab', marker: '04' },
  { label: 'Nexus', href: '/nexus', marker: '⬡' },
];

export default function Navigation() {
  const pathname = usePathname();
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 20);
    window.addEventListener('scroll', onScroll, { passive: true });
    return () => window.removeEventListener('scroll', onScroll);
  }, []);

  return (
    <>
      <nav
        className={`fixed top-0 left-0 right-0 z-40 transition-all duration-500 ${
          scrolled
            ? 'bg-[#070B10]/90 backdrop-blur-xl border-b border-white/[0.04]'
            : 'bg-transparent'
        }`}
      >
        <div className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
          {/* Logo */}
          <Link href="/" className="flex items-center gap-3 group">
            <div className="w-8 h-8 rounded-lg border border-accent-gold/30 flex items-center justify-center group-hover:border-accent-gold/60 transition-colors">
              <span className="text-accent-gold font-display text-sm font-bold">T</span>
            </div>
            <span className="font-heading text-sm tracking-wide text-[#E8E4DD]/70 group-hover:text-[#E8E4DD] transition-colors hidden sm:block">
              Terre Étendue
            </span>
          </Link>

          {/* Desktop Nav */}
          <div className="hidden md:flex items-center gap-1">
            {NAV_ITEMS.map((item) => {
              const isActive = pathname === item.href || pathname?.startsWith(item.href + '/');
              return (
                <Link
                  key={item.href}
                  href={item.href}
                  className={`relative flex items-center gap-2 px-3.5 py-2 rounded-lg text-sm transition-all duration-300 ${
                    isActive
                      ? 'text-accent-cyan'
                      : 'text-[#E8E4DD]/40 hover:text-[#E8E4DD]/70'
                  }`}
                >
                  <span className="font-mono text-[0.6rem] opacity-40">{item.marker}</span>
                  <span className="font-heading">{item.label}</span>
                  {isActive && (
                    <motion.div
                      layoutId="nav-active"
                      className="absolute inset-0 bg-accent-cyan/[0.06] border border-accent-cyan/10 rounded-lg"
                      transition={{ type: 'spring', stiffness: 350, damping: 30 }}
                    />
                  )}
                </Link>
              );
            })}
          </div>

          {/* Mobile burger */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="md:hidden p-2 text-[#E8E4DD]/50 hover:text-[#E8E4DD]"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
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
              className="fixed inset-0 bg-black/70 z-40 md:hidden"
              onClick={() => setMobileOpen(false)}
            />
            <motion.div
              initial={{ x: '100%' }}
              animate={{ x: 0 }}
              exit={{ x: '100%' }}
              transition={{ type: 'spring', damping: 25, stiffness: 250 }}
              className="fixed right-0 top-0 bottom-0 w-72 bg-[#0E1319] border-l border-white/[0.04] z-50 md:hidden p-8"
            >
              <div className="flex justify-end mb-8">
                <button onClick={() => setMobileOpen(false)} className="p-2 text-[#E8E4DD]/50">
                  <X size={20} />
                </button>
              </div>
              <nav className="space-y-2">
                {NAV_ITEMS.map((item, i) => {
                  const isActive = pathname === item.href;
                  return (
                    <motion.div
                      key={item.href}
                      initial={{ opacity: 0, x: 20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: i * 0.05 }}
                    >
                      <Link
                        href={item.href}
                        onClick={() => setMobileOpen(false)}
                        className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                          isActive
                            ? 'bg-accent-cyan/10 text-accent-cyan'
                            : 'text-[#E8E4DD]/50 hover:text-[#E8E4DD] hover:bg-white/[0.02]'
                        }`}
                      >
                        <span className="font-mono text-[0.6rem] opacity-40 w-5">{item.marker}</span>
                        <span className="font-heading">{item.label}</span>
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
