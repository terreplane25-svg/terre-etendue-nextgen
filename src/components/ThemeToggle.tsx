'use client';

import { useTheme } from './ThemeProvider';
import { Sun, Moon } from 'lucide-react';

export default function ThemeToggle() {
  const { theme, toggleTheme } = useTheme();

  return (
    <button
      onClick={toggleTheme}
      aria-label={theme === 'dark' ? 'Passer en mode clair' : 'Passer en mode sombre'}
      className="relative w-[52px] h-[28px] rounded-full border transition-all duration-300 flex items-center"
      style={{
        background: 'var(--hull)',
        borderColor: theme === 'dark' ? 'rgba(0,200,255,0.15)' : 'rgba(154,123,47,0.2)',
      }}
    >
      <Moon size={10} className="absolute left-[7px] transition-opacity duration-300"
        style={{ opacity: theme === 'dark' ? 0.15 : 0.4, color: theme === 'dark' ? 'var(--cyan)' : 'var(--text)' }} />
      <Sun size={10} className="absolute right-[7px] transition-opacity duration-300"
        style={{ opacity: theme === 'dark' ? 0.4 : 0.15, color: theme === 'dark' ? 'var(--text)' : 'var(--gold)' }} />
      <div className="absolute w-[22px] h-[22px] rounded-full transition-all duration-500"
        style={{
          left: theme === 'dark' ? '2px' : '27px',
          background: theme === 'dark' ? 'var(--cyan)' : 'var(--gold)',
          boxShadow: theme === 'dark' ? '0 0 10px rgba(0,200,255,0.4)' : '0 0 10px rgba(154,123,47,0.4)',
          transitionTimingFunction: 'cubic-bezier(0.68, -0.55, 0.27, 1.55)',
        }} />
    </button>
  );
}
