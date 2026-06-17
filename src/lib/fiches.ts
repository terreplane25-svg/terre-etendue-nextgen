import fs from 'fs';
import path from 'path';

export interface FicheSource {
  source: string;
  citation: string;
  commentaire: string;
}

export interface FicheActivite {
  titre: string;
  duree: string;
  materiel: string;
  deroulement: string[];
}

export interface Fiche {
  id: string;
  cycle: string;
  niveau: string;
  matiere: string;
  chapitre: string;
  titre: string;
  accroche: string;
  cequeditrogram: string;
  cequeditlemanuel: string;
  cequedirlalitterature: FicheSource[];
  formulation: string;
  activite: FicheActivite;
  articlesLies: string[];
  simulateur: string;
}

const fichesPath = path.join(process.cwd(), 'content/fiches/fiches-pedagogiques.json');

export function getAllFiches(): Fiche[] {
  const raw = fs.readFileSync(fichesPath, 'utf8');
  return JSON.parse(raw) as Fiche[];
}

export function getFichesByCycle(cycle: string): Fiche[] {
  return getAllFiches().filter(f => f.cycle === cycle);
}
