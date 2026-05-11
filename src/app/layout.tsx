import type { Metadata, Viewport } from 'next';
import { Inter, Montserrat, Source_Serif_4, Amiri } from 'next/font/google';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import '@/styles/globals.css';

const inter = Inter({
  subsets: ['latin'],
  variable: '--font-inter',
  display: 'swap',
});

const montserrat = Montserrat({
  subsets: ['latin'],
  variable: '--font-montserrat',
  display: 'swap',
});

const sourceSerif = Source_Serif_4({
  subsets: ['latin'],
  variable: '--font-source-serif',
  display: 'swap',
});

const amiri = Amiri({
  subsets: ['arabic', 'latin'],
  weight: ['400', '700'],
  variable: '--font-amiri',
  display: 'swap',
});

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#0A0F14',
};

export const metadata: Metadata = {
  title: {
    default: 'Terre Étendue Islam — Plateforme Académique',
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
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html
      lang="fr"
      className={`dark ${inter.variable} ${montserrat.variable} ${sourceSerif.variable} ${amiri.variable}`}
    >
      <body className="bg-obs-dark text-obs-text-primary min-h-screen flex flex-col font-sans antialiased">
        <Navigation />
        <main className="flex-1">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
