'use client';
import { useState } from 'react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { Menu, X } from 'lucide-react';
import SearchCommand from '@/components/SearchCommand';

const SECTIONS = [
  { label: 'Centre de Recherche', href: '/headquarters', color: '#7C6FC4' },
  { label: 'Observatoire', href: '/observatory', color: '#3580C0' },
  { label: 'Bibliothèque', href: '/library', color: '#C48A2E' },
  { label: 'Outils', href: '/lab', color: '#3A8F6E' },
  { label: 'Expériences', href: '/experiences', color: '#B85460' },
  { label: 'Nexus', href: '/nexus', color: '#7C6FC4' },
  { label: 'À propos', href: '/about', color: '#8A857D' },
];

export default function DashboardNav() {
  const pathname = usePathname();
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
            <div className="hidden sm:block">
              <SearchCommand inline />
            </div>
            <div className="sm:hidden">
              <SearchCommand />
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
                  <Link key={s.href} href={s.href} style={{
                    display: 'flex', alignItems: 'center',
                    padding: '14px 18px', fontSize: 14, fontWeight: 600,
                    color: active ? s.color : '#3D3A35',
                    borderBottom: active ? `3px solid ${s.color}` : '3px solid transparent',
                    fontFamily: "'Plus Jakarta Sans', sans-serif",
                  }}>
                    {s.label}
                  </Link>
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
