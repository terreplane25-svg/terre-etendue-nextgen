'use client';

import Link from 'next/link';

interface PillarCardProps {
  title: string;
  subtitle: string;
  description: string;
  href: string;
  icon: string;
  accent: 'cyan' | 'gold';
  stats?: { label: string; value: string }[];
}

export default function PillarCard({ title, subtitle, description, href, accent, stats }: PillarCardProps) {
  const accentColor = accent === 'gold' ? '[#D4A843]' : '[#00C8FF]';

  return (
    <Link href={href} className="block group">
      <div className="card card-hover p-7 space-y-4 h-full">
        <div className="flex items-center justify-between">
          <h3 className={`font-display text-xl font-bold text-[#E8E4DD] group-hover:text-${accentColor} transition-colors duration-300`}>
            {title}
          </h3>
          <span className={`font-mono text-label uppercase text-${accentColor}/30`}>
            {subtitle}
          </span>
        </div>
        <p className="text-[#E8E4DD]/35 text-sm font-body leading-relaxed">
          {description}
        </p>
        {stats && (
          <div className="flex gap-6 pt-2">
            {stats.map((stat) => (
              <div key={stat.label}>
                <span className={`font-mono text-sm font-bold text-${accentColor}/60`}>{stat.value}</span>
                <span className="text-[#E8E4DD]/20 text-xs ml-1.5 font-mono">{stat.label}</span>
              </div>
            ))}
          </div>
        )}
        <div className={`h-px w-0 group-hover:w-full transition-all duration-500 bg-gradient-to-r from-${accentColor}/30 to-transparent`} />
      </div>
    </Link>
  );
}
