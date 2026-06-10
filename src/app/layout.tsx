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

export const metadata: Metadata = {
  title: { default: 'Terre Étendue Islam', template: '%s — TEI' },
  description: 'Revue indépendante de cosmologie.',
  openGraph: {
    siteName: 'Terre Étendue Islam',
    type: 'website',
    locale: 'fr_FR',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr" className={`${jakarta.variable} ${jetbrains.variable} ${amiri.variable}`}>
      <body style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column', background: '#fff' }}>
        <DashboardNav />
        <main style={{ flex: 1 }}>{children}</main>
        <DashboardFooter />
      </body>
    </html>
  );
}
