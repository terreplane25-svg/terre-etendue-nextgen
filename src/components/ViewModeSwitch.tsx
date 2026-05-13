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
    <div className="inline-flex items-center bg-[#0D1528] border border-white/[0.06] rounded-lg p-1">
      <button
        onClick={() => set('study')}
        className={`relative flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          mode === 'study' ? 'text-[#C8D8E8]-primary' : 'text-[#C8D8E8]-secondary hover:text-[#C8D8E8]-primary'
        }`}
        aria-label="Mode Étude"
      >
        {mode === 'study' && (
          <motion.div
            layoutId="viewmode-bg"
            className="absolute inset-0 bg-[#00C8FF]/10 border border-[#00C8FF]/30 rounded-md"
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <BookOpen size={16} className="relative z-10" />
        <span className="relative z-10">Étude</span>
      </button>

      <button
        onClick={() => set('lab')}
        className={`relative flex items-center gap-2 px-4 py-2 rounded-md text-sm font-medium transition-colors ${
          mode === 'lab' ? 'text-[#C8D8E8]-primary' : 'text-[#C8D8E8]-secondary hover:text-[#C8D8E8]-primary'
        }`}
        aria-label="Mode Lab"
      >
        {mode === 'lab' && (
          <motion.div
            layoutId="viewmode-bg"
            className="absolute inset-0 bg-[#D4A843]/10 border border-[#D4A843]/30 rounded-md"
            transition={{ type: 'spring', stiffness: 500, damping: 30 }}
          />
        )}
        <FlaskConical size={16} className="relative z-10" />
        <span className="relative z-10">Lab</span>
      </button>
    </div>
  );
}
