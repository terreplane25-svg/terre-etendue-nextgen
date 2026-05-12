'use client';

import { create } from 'zustand';
import { BookOpen, FlaskConical } from 'lucide-react';
import { motion } from 'framer-motion';

// ─── Store global ────────────────────────────────
type ViewMode = 'study' | 'lab';

interface ViewModeStore {
  mode: ViewMode;
  toggle: () => void;
  set: (mode: ViewMode) => void;
}

export const useViewMode = create<ViewModeStore>((set) => ({
  mode: 'study',
  toggle: () => set((s) => ({ mode: s.mode === 'study' ? 'lab' : 'study' })),
  set: (mode) => set({ mode }),
}));

// ─── Composant Switch ────────────────────────────
export default function ViewModeSwitch() {
  const { mode, set } = useViewMode();

  return (
    <div className="inline-flex items-center bg-surface border border-white/[0.06] rounded-lg p-1">
      <button
        onClick={() => set('study')}
        className={`relative flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          mode === 'study' ? 'text-[#E8E4DD]-primary' : 'text-[#E8E4DD]-secondary hover:text-[#E8E4DD]-primary'
        }`}
        aria-label="Mode Étude"
      >
        {mode === 'study' && (
          <motion.div
            layoutId="viewmode-bg"
            className="absolute inset-0 bg-accent-cyan/10 border border-accent-cyan/30 rounded-md"
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <BookOpen size={16} className="relative z-10" />
        <span className="relative z-10">Étude</span>
      </button>

      <button
        onClick={() => set('lab')}
        className={`relative flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          mode === 'lab' ? 'text-[#E8E4DD]-primary' : 'text-[#E8E4DD]-secondary hover:text-[#E8E4DD]-primary'
        }`}
        aria-label="Mode Lab"
      >
        {mode === 'lab' && (
          <motion.div
            layoutId="viewmode-bg"
            className="absolute inset-0 bg-accent-gold/10 border border-accent-gold/30 rounded-md"
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <FlaskConical size={16} className="relative z-10" />
        <span className="relative z-10">Lab</span>
      </button>
    </div>
  );
}
