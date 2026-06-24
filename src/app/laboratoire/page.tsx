import type { Metadata } from 'next';
import LaboratoireClient from './LaboratoireClient';

export const metadata: Metadata = {
  title: "Laboratoire d'Analyse — Terre Étendue Islam",
  description: "Analyse rigoureuse de vidéos et images : observation factuelle, explication scientifique, démarche méthodologique et checklist de rigueur.",
};

export default function LaboratoirePage() {
  return <LaboratoireClient />;
}
