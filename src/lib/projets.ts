import fs from 'fs';
import path from 'path';

export interface BudgetItem {
  poste: string;
  montant: number;
}

export interface Projet {
  id: string;
  titre: string;
  statut: 'financement' | 'preparation' | 'en-cours' | 'terminee' | 'publiee';
  question: string;
  protocole: string;
  budget: BudgetItem[];
  objectif: number;
  collecte: number;
  donateurs: number;
  articlesLies: string[];
  simulateur: string;
  dateCreation: string;
  dateObjectif: string;
  engagement: string;
}

const projetsPath = path.join(process.cwd(), 'content/projets/projets.json');

export function getAllProjets(): Projet[] {
  const raw = fs.readFileSync(projetsPath, 'utf8');
  return JSON.parse(raw) as Projet[];
}

export function getActiveProjet(): Projet | null {
  const projets = getAllProjets();
  const active = projets.find(p => p.statut === 'financement') || projets[0];
  return active || null;
}
