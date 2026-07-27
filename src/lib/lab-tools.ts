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
    id: 'flat',
    label: 'Terre Plane',
    desc: "Carte plane avec dôme céleste, éphémérides, terminateur, phases lunaires, boussole et géolocalisation.",
    icon: '🗺️',
    color: '#D4943A',
    num: '01',
    tags: ['3D', 'dôme', 'éphémérides', 'carte'],
  },
  {
    id: 'curvature',
    label: 'Calculateur de Courbure',
    desc: "Courbure théorique avec réfraction. Graphique interactif, 6 cas réels, export.",
    icon: '📐',
    color: '#3D9E7C',
    num: '02',
    tags: ['courbure', 'réfraction', 'graphique'],
  },
  {
    id: 'density',
    label: 'Simulateur de Densité',
    desc: "Colonne de fluides interactive. Lâchez des objets, observez la flottabilité.",
    icon: '⚗️',
    color: '#3D9E7C',
    num: '03',
    tags: ['densité', 'flottabilité', 'Archimède'],
  },
  {
    id: 'geo',
    label: 'Système Solaire',
    desc: "8 planètes, anneaux de Saturne, vitesses orbitales. Classique ou vortex.",
    icon: '🪐',
    color: '#3B8FD4',
    num: '04',
    tags: ['3D', 'planètes', 'orbites'],
  },
  {
    id: 'classifier',
    label: 'Fait / Modèle / Hypothèse',
    desc: "Classez 24 affirmations scientifiques. Feedback immédiat et sources.",
    icon: '🎯',
    color: '#2B7A5F',
    num: '05',
    tags: ['pédagogie', 'épistémologie', 'quiz', 'enseignants'],
  },
  {
    id: 'trilat',
    label: 'Carte par trilatération',
    desc: "Toile vierge : les villes se placent uniquement d'après les distances saisies. Aucun centre, aucune coordonnée.",
    icon: '📍',
    color: '#3D9E7C',
    num: '06',
    tags: ['trilatération', 'distances', 'carte', 'données brutes'],
  },
];
