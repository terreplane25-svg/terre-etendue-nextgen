import type { Metadata } from 'next';
import '@/styles/globals.css';
import DashboardNav from '@/components/DashboardNav';
import DashboardFooter from '@/components/DashboardFooter';

export const metadata: Metadata = {
  title: { default: 'Terre Étendue Islam', template: '%s — TEI' },
  description: 'Revue indépendante de cosmologie. Examen critique, données empiriques, sources sacrées.',
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="fr">
      <body style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <DashboardNav />
        <main style={{ flex: 1 }}>{children}</main>
        <DashboardFooter />
      </body>
    </html>
  );
}
