import type { Metadata } from 'next';
import { getAllFiches } from '@/lib/fiches';
import EnseignantsClient from './EnseignantsClient';

export const metadata: Metadata = {
  alternates: { canonical: '/enseignants' },
  title: "Espace Enseignants — Enseigner la science avec rigueur",
  description: "Ressources pédagogiques pour distinguer fait, modèle et hypothèse en classe. Fiches, simulateurs et guide téléchargeable.",
};

export default function EnseignantsPage() {
  const fiches = getAllFiches();
  return <EnseignantsClient fiches={fiches} />;
}
