import Link from 'next/link';
import { FontOrbitron, FontTechMono } from '@/components/FontWrappers';

function GithubIcon({ size = 14 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 24 24" fill="currentColor">
      <path d="M12 0C5.37 0 0 5.37 0 12c0 5.31 3.435 9.795 8.205 11.385.6.105.825-.255.825-.57 0-.285-.015-1.23-.015-2.235-3.015.555-3.795-.735-4.035-1.41-.135-.345-.72-1.41-1.23-1.695-.42-.225-1.02-.78-.015-.795.945-.015 1.62.87 1.845 1.23 1.08 1.815 2.805 1.305 3.495.99.105-.78.42-1.305.765-1.605-2.67-.3-5.46-1.335-5.46-5.925 0-1.305.465-2.385 1.23-3.225-.12-.3-.54-1.53.12-3.18 0 0 1.005-.315 3.3 1.23.96-.27 1.98-.405 3-.405s2.04.135 3 .405c2.295-1.56 3.3-1.23 3.3-1.23.66 1.65.24 2.88.12 3.18.765.84 1.23 1.905 1.23 3.225 0 4.605-2.805 5.625-5.475 5.925.435.375.81 1.095.81 2.22 0 1.605-.015 2.895-.015 3.3 0 .315.225.69.825.57A12.02 12.02 0 0024 12c0-6.63-5.37-12-12-12z" />
    </svg>
  );
}

const STATS = [
  { label: 'Articles', value: '29', color: 'text-[#00C8FF]' },
  { label: 'Observations', value: '11K', color: 'text-[#00C8FF]' },
  { label: 'Sources', value: '450+', color: 'text-[#D4A843]' },
  { label: 'Modèles 3D', value: '3', color: 'text-[#00C8FF]' },
];

export default function Footer() {
  return (
    <footer className="relative z-10 border-t border-[rgba(0,200,255,0.06)] bg-[#0A1020]">
      <div className="max-w-[1200px] mx-auto px-6">
        {/* Stats bar */}
        <div className="grid grid-cols-2 md:grid-cols-4 gap-px border-b border-[rgba(0,200,255,0.06)]">
          {STATS.map((stat) => (
            <div key={stat.label} className="py-5 px-4 text-center">
              <p className={`text-xl font-bold ${stat.color} font-orbitron`}>{stat.value}</p>
              <p className="text-[9px] text-[#C8D8E8]/20 mt-1 tracking-[0.15em] uppercase font-tech-mono">{stat.label}</p>
            </div>
          ))}
        </div>

        {/* Footer content */}
        <div className="py-8 flex flex-col sm:flex-row items-center justify-between gap-6">
          <div className="flex items-center gap-3">
            <div className="relative w-6 h-6 flex items-center justify-center">
              <svg viewBox="0 0 30 30" fill="none" className="absolute inset-0 w-full h-full">
                <polygon points="15,2 27,9 27,21 15,28 3,21 3,9" stroke="rgba(0,200,255,0.2)" strokeWidth="1" fill="rgba(0,200,255,0.03)" />
              </svg>
              <FontOrbitron className="relative z-10 text-[8px] font-bold text-[#00C8FF]">TEI</FontOrbitron>
            </div>
            <FontTechMono className="text-[10px] text-[#C8D8E8]/20">
              &copy; {new Date().getFullYear()} TERRE ÉTENDUE ISLAM
            </FontTechMono>
          </div>

          <div className="flex items-center gap-6">
            {[
              { label: 'Q.G.', href: '/headquarters' },
              { label: 'Obs', href: '/observatory' },
              { label: 'Biblio', href: '/library' },
              { label: 'Lab', href: '/lab' },
              { label: 'Nexus', href: '/nexus' },
              { label: 'À propos', href: '/about' },
            ].map((item) => (
              <Link
                key={item.href}
                href={item.href}
                className="text-[10px] text-[#C8D8E8]/15 hover:text-[#C8D8E8]/40 transition-colors font-orbitron"
                style={{letterSpacing: '0.1em'}}
              >
                {item.label}
              </Link>
            ))}
          </div>

          <a
            href="https://github.com/terreplane25-svg/terre-etendue-nextgen"
            target="_blank"
            rel="noopener noreferrer"
            className="text-[#C8D8E8]/15 hover:text-[#C8D8E8]/40 transition-colors"
          >
            <GithubIcon />
          </a>
        </div>
      </div>
    </footer>
  );
}
