import type { Metadata } from 'next';
import { getAllProjets } from '@/lib/projets';
import ProjetsClient from './ProjetsClient';

export const metadata: Metadata = {
  title: "Projets — Financez la prochaine expérience",
  description: "Expériences scientifiques financées par la communauté. Budget transparent, protocole détaillé, résultats publiés quoi qu'il arrive.",
};

export default function ProjetsPage() {
  const projets = getAllProjets();
  return <ProjetsClient projets={projets} />;
}
