import Link from 'next/link';

function GithubIcon({ size = 16 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
    </svg>
  );
}

const PILLARS = [
  { label: 'Le Q.G.', href: '/headquarters' },
  { label: "L'Observatoire", href: '/observatory' },
  { label: 'La Bibliothèque', href: '/library' },
  { label: 'Le Lab', href: '/lab' },
  { label: 'Le Nexus', href: '/nexus' },
];

export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-white/[0.04]">
      <div className="max-w-7xl mx-auto px-6 py-16">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-12">
          {/* Brand */}
          <div className="space-y-4">
            <div className="flex items-center gap-3">
              <div className="w-8 h-8 rounded-lg border border-accent-gold/30 flex items-center justify-center">
                <span className="text-accent-gold font-display text-sm font-bold">T</span>
              </div>
              <span className="font-heading text-sm text-[#E8E4DD]/50">Terre Étendue Islam</span>
            </div>
            <p className="text-[#E8E4DD]/25 text-sm font-body leading-relaxed max-w-xs">
              Plateforme de recherche académique réconciliant épistémologie, observations empiriques et sources sacrées.
            </p>
          </div>

          {/* Navigation */}
          <div>
            <p className="font-mono text-label uppercase text-[#E8E4DD]/20 mb-5">Piliers</p>
            <nav className="space-y-2.5">
              {PILLARS.map((item) => (
                <Link
                  key={item.href}
                  href={item.href}
                  className="block text-sm text-[#E8E4DD]/30 hover:text-[#E8E4DD]/60 transition-colors font-heading"
                >
                  {item.label}
                </Link>
              ))}
            </nav>
          </div>

          {/* Links */}
          <div>
            <p className="font-mono text-label uppercase text-[#E8E4DD]/20 mb-5">Liens</p>
            <div className="space-y-2.5">
              <a
                href="https://github.com/terreplane25-svg/terre-etendue-nextgen"
                target="_blank"
                rel="noopener noreferrer"
                className="flex items-center gap-2 text-sm text-[#E8E4DD]/30 hover:text-[#E8E4DD]/60 transition-colors font-heading"
              >
                <GithubIcon size={14} />
                GitHub
              </a>
              <a
                href="mailto:contact@terretendue.com"
                className="block text-sm text-[#E8E4DD]/30 hover:text-[#E8E4DD]/60 transition-colors font-heading"
              >
                Contact
              </a>
            </div>
          </div>
        </div>

        <div className="geo-line mt-12 mb-8" />

        <div className="flex flex-col sm:flex-row items-center justify-between gap-4 text-[#E8E4DD]/15 text-xs font-mono">
          <span>&copy; {new Date().getFullYear()} Terre Étendue Islam</span>
          <span>Next.js &middot; Vercel &middot; Open Source</span>
        </div>
      </div>
    </footer>
  );
}
