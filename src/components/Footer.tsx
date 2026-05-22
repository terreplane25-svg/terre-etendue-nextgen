import Link from 'next/link';
import { FontOrbitron, FontTechMono } from '@/components/FontWrappers';



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

        </div>
      </div>
    </footer>
  );
}
