/** @type {import('tailwindcss').Config} */
module.exports = {
  content: ['./src/**/*.{js,ts,jsx,tsx,mdx}'],
  theme: {
    extend: {
      colors: {
        void: '#070B10',
        surface: {
          DEFAULT: '#0E1319',
          raised: '#141A23',
        },
        accent: {
          cyan: '#00B4E6',
          gold: '#C9A84C',
          emerald: '#3DA67A',
        },
      },
      fontFamily: {
        display: ['var(--font-display)', 'Playfair Display', 'Georgia', 'serif'],
        heading: ['var(--font-heading)', 'Crimson Pro', 'Georgia', 'serif'],
        body: ['var(--font-body)', 'Source Serif 4', 'Georgia', 'serif'],
        mono: ['var(--font-mono)', 'JetBrains Mono', 'monospace'],
        arabic: ['var(--font-amiri)', 'Traditional Arabic', 'serif'],
      },
      fontSize: {
        'hero': ['clamp(3rem, 8vw, 6rem)', { lineHeight: '1.05', letterSpacing: '-0.03em' }],
        'title-lg': ['clamp(1.8rem, 4vw, 2.75rem)', { lineHeight: '1.15', letterSpacing: '-0.02em' }],
        'label': ['0.62rem', { lineHeight: '1', letterSpacing: '0.18em' }],
      },
      borderColor: {
        DEFAULT: 'rgba(255, 255, 255, 0.06)',
      },
      boxShadow: {
        'glow-cyan': '0 0 60px rgba(0, 180, 230, 0.06)',
        'glow-gold': '0 0 60px rgba(201, 168, 76, 0.06)',
      },
    },
  },
  plugins: [require('@tailwindcss/typography')],
};
