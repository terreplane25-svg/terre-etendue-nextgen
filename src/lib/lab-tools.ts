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
    id: 'visee-optique',
    label: 'Portion visible d’une cible éloignée',
    desc: "Fraction visible prédite par deux modèles concurrents, sur tout l’intervalle de réfraction déclaré, et condition de discrimination du §28.2. Chaque valeur exige sa source.",
    icon: '📐',
    color: '#3D9E7C',
    num: '01',
    tags: ['protocole', 'géodésie', 'réfraction', 'enveloppe'],
  },
  {
    id: 'integrite-image',
    label: 'Vérificateur d’intégrité d’image',
    desc: "Empreinte SHA-256 et métadonnées EXIF/GPS d’un fichier, calculées dans votre navigateur. Le fichier ne quitte pas votre machine.",
    icon: '🔒',
    color: '#3B8FD4',
    num: '02',
    tags: ['intégrité', 'SHA-256', 'EXIF', 'confidentialité'],
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
    id: 'classifier',
    label: 'Fait / Modèle / Hypothèse',
    desc: "Classez 24 affirmations scientifiques. Feedback immédiat et sources.",
    icon: '🎯',
    color: '#2B7A5F',
    num: '04',
    tags: ['pédagogie', 'épistémologie', 'quiz', 'enseignants'],
  },
];
