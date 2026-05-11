'use client';

import { useState, useEffect, useCallback } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X, Search, Command } from 'lucide-react';
import { motion, AnimatePresence } from 'framer-motion';

const NAV_ITEMS = [
  { label: 'Le Q.G.', href: '/headquarters', icon: '🧠', description: 'Épistémologie' },
  { label: "L'Observatoire", href: '/observatory', icon: '🔭', description: 'Empirique' },
  { label: 'La Bibliothèque', href: '/library', icon: '📚', description: 'Sources Sacrées' },
  { label: 'Le Lab', href: '/lab', icon: '⚗️', description: 'Modélisation' },
  { label: 'Nexus', href: '/nexus', icon: '🔗', description: 'Graphe de Liens' },
];

export default function Navigation() {
  const [mobileOpen, setMobileOpen] = useState(false);
  const [scrolled, setScrolled] = useState(false);
  const pathname = usePathname();

  const handleScroll = useCallback(() => {
    setScrolled(window.scrollY > 40);
  }, []);

  useEffect(() => {
    window.addEventListener('scroll', handleScroll, { passive: true });
    return () => window.removeEventListener('scroll', handleScroll);
  }, [handleScroll]);

  // Fermer le menu mobile quand on navigue
  useEffect(() => {
    setMobileOpen(false);
  }, [pathname]);

  return (
    <header
      className={`fixed top-0 inset-x-0 z-50 transition-all duration-300 ${
        scrolled
          ? 'bg-obs-dark/85 backdrop-blur-xl border-b border-obs-border'
          : 'bg-transparent'
      }`}
    >
      <nav className="max-w-7xl mx-auto px-6 h-16 flex items-center justify-between">
        {/* Logo */}
        <Link href="/" className="flex items-center gap-2 group">
          <span className="text-2xl">⊙</span>
          <span className="font-display font-bold text-lg text-obs-text-primary group-hover:text-obs-cyan transition-colors">
            TEI
          </span>
        </Link>

        {/* Desktop Links */}
        <div className="hidden lg:flex items-center gap-1">
          {NAV_ITEMS.map((item) => {
            const isActive = pathname === item.href || pathname.startsWith(item.href + '/');
            return (
              <Link
                key={item.href}
                href={item.href}
                className={`flex items-center gap-1.5 px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                  isActive
                    ? 'bg-obs-cyan/10 text-obs-cyan'
                    : 'text-obs-text-secondary hover:text-obs-text-primary hover:bg-obs-surface'
                }`}
              >
                <span className="text-base">{item.icon}</span>
                <span>{item.label}</span>
              </Link>
            );
          })}
        </div>

        {/* Right Actions */}
        <div className="flex items-center gap-3">
          {/* Search Hint (desktop) */}
          <div className="hidden md:flex items-center gap-2 bg-obs-surface border border-obs-border rounded-lg px-3 py-1.5 text-sm text-obs-text-secondary">
            <Search size={14} />
            <span>Rechercher…</span>
            <kbd className="ml-2 px-1.5 py-0.5 bg-obs-dark rounded text-xs border border-obs-border">
              <Command size={10} className="inline" />&thinsp;K
            </kbd>
          </div>

          {/* Mobile Toggle */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="lg:hidden p-2 rounded-lg hover:bg-obs-surface transition-colors"
            aria-label="Menu"
          >
            {mobileOpen ? <X size={22} className="text-obs-cyan" /> : <Menu size={22} />}
          </button>
        </div>
      </nav>

      {/* Mobile Overlay */}
      <AnimatePresence>
        {mobileOpen && (
          <motion.div
            initial={{ opacity: 0, y: -8 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -8 }}
            transition={{ duration: 0.2 }}
            className="lg:hidden bg-obs-surface border-t border-obs-border"
          >
            <div className="max-w-7xl mx-auto px-6 py-4 space-y-1">
              {NAV_ITEMS.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <Link
                    key={item.href}
                    href={item.href}
                    className={`flex items-center gap-3 px-4 py-3 rounded-lg transition-colors ${
                      isActive ? 'bg-obs-cyan/10 text-obs-cyan' : 'hover:bg-obs-dark'
                    }`}
                  >
                    <span className="text-xl">{item.icon}</span>
                    <div>
                      <p className="font-medium">{item.label}</p>
                      <p className="text-xs text-obs-text-secondary">{item.description}</p>
                    </div>
                  </Link>
                );
              })}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </header>
  );
}
