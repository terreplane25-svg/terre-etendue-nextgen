/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      fontFamily: {
        orbitron: ['var(--font-orbitron)', 'Orbitron', 'sans-serif'],
        'tech-mono': ['var(--font-tech-mono)', 'Share Tech Mono', 'monospace'],
        rajdhani: ['var(--font-raj)', 'Rajdhani', 'sans-serif'],
        body: ['var(--font-body)', 'Source Serif 4', 'Georgia', 'serif'],
        arabic: ['var(--font-amiri)', 'Amiri', 'Traditional Arabic', 'serif'],
      },
      animation: {
        'pulse-dot': 'pulse-dot 2s ease-in-out infinite',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
