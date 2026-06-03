import type { Metadata } from 'next';
import '@/styles/globals.css';
import DashboardNav from '@/components/DashboardNav';
import DashboardFooter from '@/components/DashboardFooter';
import Grain from '@/components/ui/Grain';

export const metadata: Metadata = {
  title: { default: 'Terre Étendue Islam', template: '%s — TEI' },
  description: 'Revue indépendante de cosmologie.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Grain />
        <DashboardNav />
        <main style={{ flex: 1 }}>{children}</main>
        <DashboardFooter />
      </body>
    </html>
  );
}
