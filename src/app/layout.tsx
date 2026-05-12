import type { Metadata, Viewport } from 'next';
import { Playfair_Display, Crimson_Pro, Source_Serif_4, Amiri, JetBrains_Mono } from 'next/font/google';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import '@/styles/globals.css';

// Display font: Playfair Display — editorial luxury, art deco DNA
const playfair = Playfair_Display({
  subsets: ['latin'],
  variable: '--font-display',
  display: 'swap',
});

// Heading font: Crimson Pro — refined, not generic
const crimson = Crimson_Pro({
  subsets: ['latin'],
  variable: '--font-heading',
  display: 'swap',
});

// Body: Source Serif 4 — optimal for long-form reading
const sourceSerif = Source_Serif_4({
  subsets: ['latin'],
  variable: '--font-body',
  display: 'swap',
});

// Arabic: Amiri — calligraphic beauty
const amiri = Amiri({
  subsets: ['arabic', 'latin'],
  weight: ['400', '700'],
  variable: '--font-amiri',
  display: 'swap',
});

// Mono: JetBrains Mono — for data, numbers, labels
const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  variable: '--font-mono',
  display: 'swap',
});

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#070B10',
};

export const metadata: Metadata = {
  title: {
    default: 'Terre Étendue Islam',
    template: '%s | Terre Étendue Islam',
  },
  description:
    'Plateforme de recherche académique réconciliant épistémologie, observations empiriques, sources sacrées islamiques et modélisation géométrique.',
  keywords: ['islam', 'science', 'géométrie', 'terre étendue', 'recherche', 'épistémologie', 'coran'],
  openGraph: {
    title: 'Terre Étendue Islam',
    description: 'Plateforme de recherche académique et scientifique',
    type: 'website',
    locale: 'fr_FR',
  },
  twitter: {
    card: 'summary',
    title: 'Terre Étendue Islam',
    description: 'Plateforme de recherche académique et scientifique',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="fr"
      className={`dark ${playfair.variable} ${crimson.variable} ${sourceSerif.variable} ${amiri.variable} ${jetbrains.variable}`}
    >
      <body className="bg-[#070B10] text-[#E8E4DD] min-h-screen flex flex-col antialiased selection:bg-[#D4AF37]/20 selection:text-[#D4AF37]">
        {/* Grain overlay */}
        <div className="fixed inset-0 pointer-events-none z-[100] opacity-[0.03]" style={{backgroundImage: 'url("data:image/svg+xml,%3Csvg viewBox=%270 0 256 256%27 xmlns=%27http://www.w3.org/2000/svg%27%3E%3Cfilter id=%27noise%27%3E%3CfeTurbulence type=%27fractalNoise%27 baseFrequency=%270.9%27 numOctaves=%274%27 stitchTiles=%27stitch%27/%3E%3C/filter%3E%3Crect width=%27100%25%27 height=%27100%25%27 filter=%27url(%23noise)%27/%3E%3C/svg%3E")', backgroundRepeat: 'repeat', backgroundSize: '256px 256px'}} />
        
        {/* Ambient glow */}
        <div className="fixed top-0 left-1/2 -translate-x-1/2 w-[800px] h-[600px] pointer-events-none z-0 opacity-30"
          style={{background: 'radial-gradient(ellipse at center, rgba(0,180,230,0.08) 0%, rgba(212,175,55,0.04) 40%, transparent 70%)'}}
        />

        <Navigation />
        <main className="flex-1 relative z-10">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
