import type { Metadata } from 'next';
import { Plus_Jakarta_Sans, JetBrains_Mono, Amiri } from 'next/font/google';
import '@/styles/globals.css';
import DashboardNav from '@/components/DashboardNav';
import DashboardFooter from '@/components/DashboardFooter';

const jakarta = Plus_Jakarta_Sans({
  subsets: ['latin'],
  weight: ['300', '400', '500', '600', '700', '800'],
  variable: '--font-main',
  display: 'swap',
});

const jetbrains = JetBrains_Mono({
  subsets: ['latin'],
  weight: ['400', '500', '600', '700'],
  variable: '--font-mono',
  display: 'swap',
});

const amiri = Amiri({
  subsets: ['arabic'],
  weight: ['400', '700'],
  style: ['normal', 'italic'],
  variable: '--font-arabic',
  display: 'swap',
});

const SITE_URL = 'https://terre-etendue-islam.fr';
const SITE_DESC = 'Revue indépendante de cosmologie : la cosmologie coranique et la science moderne examinées avec la même rigueur.';
const OG_IMAGE = 'https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/07/StockCake-Horizon_de_Lever_de_Soleil_Ethere-297875-standard.jpg';

export const metadata: Metadata = {
  metadataBase: new URL(SITE_URL),
  title: { default: 'Terre Étendue Islam', template: '%s — TEI' },
  description: SITE_DESC,
  robots: {
    index: true,
    follow: true,
    googleBot: {
      index: true,
      follow: true,
      'max-image-preview': 'large',
      'max-snippet': -1,
      'max-video-preview': -1,
    },
  },
  openGraph: {
    siteName: 'Terre Étendue Islam',
    type: 'website',
    locale: 'fr_FR',
    images: [{ url: OG_IMAGE, width: 1200, height: 630, alt: 'Terre Étendue Islam' }],
  },
  twitter: {
    card: 'summary_large_image',
    images: [OG_IMAGE],
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${jakarta.variable} ${jetbrains.variable} ${amiri.variable}`}>
      <body style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: 'var(--bg)' }}>
        <DashboardNav />
        <main style={{ flex: 1 }}>{children}</main>
        <DashboardFooter />
      </body>
    </html>
  );
}
