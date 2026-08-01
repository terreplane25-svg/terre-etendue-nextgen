import type { Metadata } from 'next';
import { getReseau } from '@/lib/reseau';
import CarteClient from './CarteClient';

export const metadata: Metadata = {
  // Page mise de côté : plus liée depuis la navigation ni le sitemap.
  // Elle reste accessible par URL directe, mais n'est plus indexée.
  robots: { index: false, follow: true },
  alternates: { canonical: '/carte' },
  title: 'La carte du réseau',
  description:
    "21 noyaux géodésiques clos sur six continents et quatre océans, 130 points, 342 distances calculées — et les dix paires où le modèle sphérique et le modèle plan cessent d'être d'accord.",
};

export default function CartePage() {
  return <CarteClient data={getReseau()} />;
}
