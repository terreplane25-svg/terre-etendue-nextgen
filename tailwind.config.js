/** @type {import('tailwindcss').Config} */
module.exports = {
  content: [
    './src/**/*.{js,ts,jsx,tsx,mdx}',
  ],
  darkMode: 'class',
  theme: {
    extend: {
      colors: {
        'obs-dark': '#0A0F14',
        'obs-surface': '#161D26',
        'obs-cyan': '#00D1FF',
        'obs-gold': '#D4AF37',
        'obs-text-primary': '#F5F7FA',
        'obs-text-secondary': '#B0B8C1',
        'obs-border': '#2A3138',
        'obs-cyan-dim': '#0099CC',
        'obs-gold-dim': '#AA8C2B',
      },
      fontFamily: {
        sans: ['var(--font-inter)', 'ui-sans-serif', 'system-ui'],
        serif: ['var(--font-source-serif)', 'Georgia', 'serif'],
        display: ['var(--font-montserrat)', 'ui-sans-serif'],
      },
      fontSize: {
        'display-lg': ['3.5rem', { lineHeight: '1.1', fontWeight: '700' }],
        'display': ['2.5rem', { lineHeight: '1.2', fontWeight: '700' }],
        'heading-lg': ['2rem', { lineHeight: '1.3', fontWeight: '600' }],
        'heading': ['1.5rem', { lineHeight: '1.4', fontWeight: '600' }],
        'subheading': ['1.125rem', { lineHeight: '1.5', fontWeight: '500' }],
      },
      boxShadow: {
        'obs-cyan': '0 4px 24px rgba(0, 209, 255, 0.12)',
        'obs-gold': '0 4px 24px rgba(212, 175, 55, 0.12)',
      },
      animation: {
        'fade-in': 'fadeIn 0.6s ease-out',
        'slide-up': 'slideUp 0.8s cubic-bezier(0.16, 1, 0.3, 1)',
      },
      keyframes: {
        fadeIn: {
          from: { opacity: '0' },
          to: { opacity: '1' },
        },
        slideUp: {
          from: { opacity: '0', transform: 'translateY(24px)' },
          to: { opacity: '1', transform: 'translateY(0)' },
        },
      },
    },
  },
  plugins: [
    require('@tailwindcss/typography'),
  ],
};
