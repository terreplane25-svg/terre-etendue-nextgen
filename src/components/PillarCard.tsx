'use client';

import Link from 'next/link';
import { motion } from 'framer-motion';
import { ArrowUpRight } from 'lucide-react';

interface PillarCardProps {
  title: string;
  description: string;
  href: string;
  icon: string;
  stats: { label: string; value: string }[];
  accent: 'cyan' | 'gold';
}

export default function PillarCard({ title, description, href, icon, stats, accent }: PillarCardProps) {
  const accentMap = {
    cyan: {
      border: 'group-hover:border-obs-cyan/60',
      shadow: 'group-hover:shadow-obs-cyan',
      text: 'text-obs-cyan',
      bg: 'from-obs-cyan/5',
    },
    gold: {
      border: 'group-hover:border-obs-gold/60',
      shadow: 'group-hover:shadow-obs-gold',
      text: 'text-obs-gold',
      bg: 'from-obs-gold/5',
    },
  };

  const a = accentMap[accent];

  return (
    <Link href={href} className="block group">
      <motion.div
        whileHover={{ y: -6 }}
        whileTap={{ scale: 0.98 }}
        transition={{ type: 'spring', stiffness: 400, damping: 25 }}
        className={`relative overflow-hidden rounded-xl border border-obs-border bg-obs-surface p-8 transition-all duration-300 ${a.border} ${a.shadow}`}
      >
        {/* Gradient on hover */}
        <div
          className={`absolute inset-0 bg-gradient-to-br ${a.bg} to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-500 pointer-events-none`}
        />

        <div className="relative z-10 flex flex-col gap-6">
          {/* Header */}
          <div className="flex items-start justify-between">
            <span className="text-4xl">{icon}</span>
            <ArrowUpRight
              size={20}
              className={`${a.text} opacity-0 group-hover:opacity-100 transition-all duration-300 translate-x-0 group-hover:translate-x-1 -translate-y-0 group-hover:-translate-y-1`}
            />
          </div>

          {/* Content */}
          <div className="space-y-2">
            <h3 className="text-xl font-display font-bold text-obs-text-primary">{title}</h3>
            <p className="text-sm text-obs-text-secondary leading-relaxed">{description}</p>
          </div>

          {/* Stats */}
          <div className="flex gap-6 pt-4 border-t border-obs-border">
            {stats.map((stat) => (
              <div key={stat.label}>
                <p className={`text-lg font-bold ${a.text}`}>{stat.value}</p>
                <p className="text-xs text-obs-text-secondary uppercase tracking-wider">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </motion.div>
    </Link>
  );
}
