import type { Metadata, Viewport } from 'next';
import { fontVariables } from '@/lib/fonts';
import Navigation from '@/components/Navigation';
import Footer from '@/components/Footer';
import '@/styles/globals.css';

export const viewport: Viewport = {
  width: 'device-width',
  initialScale: 1,
  maximumScale: 5,
  themeColor: '#050A12',
};

export const metadata: Metadata = {
  title: {
    default: 'Terre Étendue Islam',
    template: '%s | TEI',
  },
  description: 'Plateforme de recherche académique réconciliant épistémologie, observations empiriques, sources sacrées islamiques et modélisation géométrique.',
  keywords: ['islam', 'science', 'géométrie', 'terre étendue', 'recherche', 'coran'],
  openGraph: {
    title: 'Terre Étendue Islam',
    description: 'Plateforme de recherche académique et scientifique',
    type: 'website',
    locale: 'fr_FR',
  },
  twitter: {
    card: 'summary',
    title: 'Terre Étendue Islam',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={fontVariables}>
      <head>
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
      </head>
      <body className="bg-[#050A12] text-[#C8D8E8] min-h-screen flex flex-col antialiased">
        {/* Grid overlay */}
        <div className="fixed inset-0 pointer-events-none z-0 opacity-100" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 59px, rgba(0,200,255,0.03) 59px, rgba(0,200,255,0.03) 60px), repeating-linear-gradient(90deg, transparent, transparent 59px, rgba(0,200,255,0.03) 59px, rgba(0,200,255,0.03) 60px)'
        }} />

        <Navigation />
        <main className="flex-1 relative z-10">{children}</main>
        <Footer />
      </body>
    </html>
  );
}
