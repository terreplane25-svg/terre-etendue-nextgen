import type { Metadata } from 'next';
import { getReseau } from '@/lib/reseau';
import CarteClient from './CarteClient';

export const metadata: Metadata = {
  alternates: { canonical: '/carte' },
  title: 'La carte du réseau',
  description:
    "11 noyaux géodésiques clos sur cinq continents et trois océans, 70 points, 192 distances calculées — et les cinq paires où le modèle sphérique et le modèle plan cessent d'être d'accord.",
};

export default function CartePage() {
  return <CarteClient data={getReseau()} />;
}
