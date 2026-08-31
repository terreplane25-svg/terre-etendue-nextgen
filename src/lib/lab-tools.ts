// Source unique des simulateurs du Lab.
// Utilisé par la page /lab (LabClient) ET la page d'accueil (compteur dynamique).
export interface LabTool {
  id: string;
  label: string;
  desc: string;
  icon: string;
  color: string;
  num: string;
  tags: string[];
}

export const TOOLS: LabTool[] = [
  {
    id: 'curvature',
    label: 'Calculateur de Courbure',
    desc: "Courbure théorique avec réfraction. Graphique interactif, 6 cas réels, export.",
    icon: '📐',
    color: '#3D9E7C',
    num: '01',
    tags: ['courbure', 'réfraction', 'graphique'],
  },
  {
    id: 'density',
    label: 'Simulateur de Densité',
    desc: "Colonne de fluides interactive. Lâchez des objets, observez la flottabilité.",
    icon: '⚗️',
    color: '#3D9E7C',
    num: '02',
    tags: ['densité', 'flottabilité', 'Archimède'],
  },
  {
    id: 'classifier',
    label: 'Fait / Modèle / Hypothèse',
    desc: "Classez 24 affirmations scientifiques. Feedback immédiat et sources.",
    icon: '🎯',
    color: '#2B7A5F',
    num: '03',
    tags: ['pédagogie', 'épistémologie', 'quiz', 'enseignants'],
  },
];
