import type { Metadata, Viewport } from 'next';
import { fontVariables } from '@/lib/fonts';
import Navigation from '@/components/Navigation';
import { ThemeProvider, ThemeScript } from '@/components/ThemeProvider';
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
    default: 'Terre Étendue Islam — Plateforme de Recherche Académique',
    template: '%s | Terre Étendue Islam',
  },
  description: 'Plateforme de recherche académique réconciliant épistémologie, observations empiriques, sources sacrées islamiques et modélisation géométrique. 50 articles, 3 simulations 3D, 11 documents sources.',
  keywords: ['terre étendue', 'islam', 'cosmologie islamique', 'terre plate', 'science', 'coran', 'recherche', 'épistémologie', 'géocentrisme', 'observations empiriques', 'courbure terrestre'],
  authors: [{ name: 'Collectif Terre Étendue Islam' }],
  metadataBase: new URL('https://terre-etendue-islam.fr'),
  alternates: {
    canonical: 'https://terre-etendue-islam.fr',
  },
  openGraph: {
    title: 'Terre Étendue Islam',
    description: 'Plateforme de recherche académique — 50 articles, 3 simulations 3D, 11 documents sources',
    url: 'https://terre-etendue-islam.fr',
    siteName: 'Terre Étendue Islam',
    type: 'website',
    locale: 'fr_FR',
  },
  twitter: {
    card: 'summary_large_image',
    title: 'Terre Étendue Islam',
    description: 'Plateforme de recherche académique — épistémologie, observations, sources sacrées, modélisation',
  },
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-video-preview': -1,
      'max-image-preview': 'large',
      'max-snippet': -1,
    },
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={fontVariables}>
      <head>
        <ThemeScript />
        <link rel="preconnect" href="https://fonts.googleapis.com" />
        <link rel="preconnect" href="https://fonts.gstatic.com" crossOrigin="anonymous" />
        <script
          type="application/ld+json"
          dangerouslySetInnerHTML={{
            __html: JSON.stringify({
              '@context': 'https://schema.org',
              '@type': 'WebSite',
              name: 'Terre Étendue Islam',
              url: 'https://terre-etendue-islam.fr',
              description: 'Plateforme de recherche académique réconciliant épistémologie, observations empiriques, sources sacrées islamiques et modélisation géométrique.',
              publisher: {
                '@type': 'Organization',
                name: 'Collectif Terre Étendue Islam',
              },
              potentialAction: {
                '@type': 'SearchAction',
                target: 'https://terre-etendue-islam.fr/search?q={search_term_string}',
                'query-input': 'required name=search_term_string',
              },
            }),
          }}
        />
      </head>
      <body className="bg-[var(--void)] text-[var(--text)] min-h-screen flex flex-col antialiased transition-colors duration-400">
        {/* Grid overlay */}
        <div className="fixed inset-0 pointer-events-none z-0 opacity-100" style={{
          backgroundImage: 'repeating-linear-gradient(0deg, transparent, transparent 59px, var(--cyan-04) 59px, var(--cyan-04) 60px), repeating-linear-gradient(90deg, transparent, transparent 59px, var(--cyan-04) 59px, var(--cyan-04) 60px)'
        }} />

        <ThemeProvider>
          <Navigation />
          <main className="flex-1 relative z-10">{children}</main>
          <Footer />
        </ThemeProvider>
      </body>
    </html>
  );
}
