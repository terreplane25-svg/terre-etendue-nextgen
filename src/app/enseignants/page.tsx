import type { Metadata } from 'next';
import EnseignantsClient from './EnseignantsClient';

export const metadata: Metadata = {
  title: "Espace Enseignants — Enseigner la science avec rigueur",
  description: "Ressources pédagogiques pour distinguer fait, modèle et hypothèse en classe. Fiches, simulateurs et guide téléchargeable.",
};

export default function EnseignantsPage() {
  return <EnseignantsClient />;
}
