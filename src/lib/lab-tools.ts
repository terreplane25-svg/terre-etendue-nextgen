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
  /**
   * Hors grille : accessible par un lien texte discret, pas par une carte.
   *
   * Ce n'est pas une mise au placard. Un outil discret est un outil dont
   * l'usage suppose qu'on ait déjà fait le reste — le générateur de fiche ne
   * sert qu'à monter un dossier une fois les mesures faites. Le mettre au même
   * rang que les simulateurs enverrait le visiteur remplir cinquante-six
   * champs avant d'avoir rien observé.
   */
  discret?: boolean;
}

export const TOOLS: LabTool[] = [
  {
    id: 'visee-optique',
    label: 'Simulateur de Visée',
    desc: "Deux points, deux hauteurs. Ce que les modèles sphérique et plat prédisent que vous devriez voir, et si l’écart entre les deux est assez grand pour être photographié.",
    icon: '📐',
    color: '#3D9E7C',
    num: '01',
    tags: ['simulateur', 'géodésie', 'relief', 'réfraction'],
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
    id: 'fiche-archive',
    label: 'Fiche d’observation et archive',
    desc: "Les cinquante-six champs du §33 — chacun exige une valeur ou la mention « indisponible » — et l’arborescence d’archive du §34, téléchargeable.",
    icon: '🗂️',
    color: '#8B7EC8',
    num: '—',
    tags: ['fiche', 'archive', 'traçabilité', 'SHA-256'],
    discret: true,
  },
  {
    id: 'metrologie-image',
    label: 'Analyse d’image par métrologie optique',
    desc: "Trois pointés sur une photo de visée, quatre grandeurs sourcées, et l’angle relevé est inversé en coefficient de réfraction effectif. L’image ne quitte pas votre machine.",
    icon: '🔭',
    color: '#3B8FD4',
    num: '03',
    tags: ['image', 'angles', 'réfraction', 'enveloppe'],
  },
  {
    id: 'density',
    label: 'Simulateur de Densité',
    desc: "Colonne de fluides interactive. Lâchez des objets, observez la flottabilité.",
    icon: '⚗️',
    color: '#3D9E7C',
    num: '04',
    tags: ['densité', 'flottabilité', 'Archimède'],
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
];

/**
 * Les outils de la grille, dans l'ordre d'affichage. La numérotation les suit :
 * un trou dans la suite ferait chercher un outil qui n'a pas disparu, il est
 * seulement ailleurs.
 */
export const OUTILS_GRILLE: LabTool[] = TOOLS.filter((t) => !t.discret);

/** Ceux qu'on atteint par un lien, pas par une carte. */
export const OUTILS_DISCRETS: LabTool[] = TOOLS.filter((t) => t.discret);
