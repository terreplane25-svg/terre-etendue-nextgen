// ═══════════════════════════════════════════
// LABORATOIRE D'ANALYSE — Données
// ═══════════════════════════════════════════

export interface AnalyseMedia {
  id: string;
  type: 'video' | 'image';
  category: string;
  title: string;
  location?: string;
  date?: string;
  source?: string;
  duration?: string;
  resolution?: string;
  embedUrl?: string;
  imageUrl?: string;
  observation: string;
  analyse: string;
  demarche: string[];
  checklist: string[];
  svgDiagram?: string;
  relatedArticle?: string;
}

export const CATEGORIES = [
  { id: 'atmospherique', label: 'Atmosphérique', icon: '🌫️', color: '#3B8FD4' },
  { id: 'optique', label: 'Optique & perspective', icon: '🔭', color: '#D4943A' },
  { id: 'mecanique', label: 'Physique mécanique', icon: '⚙️', color: '#8B7EC8' },
  { id: 'astronomique', label: 'Astronomique', icon: '🌙', color: '#C45E6A' },
  { id: 'hydrologique', label: 'Eau & fluides', icon: '🌊', color: '#3D9E7C' },
  { id: 'electromagnetique', label: 'Électromagnétisme', icon: '⚡', color: '#E8A838' },
] as const;

export type CategoryId = typeof CATEGORIES[number]['id'];

export const ANALYSES: AnalyseMedia[] = [
  {
    id: 'mirage-inferieur-route',
    type: 'video',
    category: 'atmospherique',
    title: 'Mirage inférieur sur une route droite',
    location: 'Route désertique, été',
    source: 'Observation amateur vérifiable',
    duration: '~2 min',
    embedUrl: 'https://www.youtube.com/embed/CF-gTmiVEz0',
    observation: `Sur une longue route droite par forte chaleur, la chaussée semble mouillée à quelques centaines de mètres. On aperçoit un « reflet » inversé des véhicules et du ciel sur la route. L'effet disparaît à mesure qu'on s'approche.`,
    analyse: `<p>L'air surchauffé au contact du bitume (60–70 °C) crée une couche d'air <strong>moins dense</strong> juste au-dessus de la route.</p>
<p>L'indice de réfraction de l'air diminue avec la température : <code>n ≈ 1 + 0,000293 × (P/T)</code>. Les rayons lumineux se courbent vers les couches plus denses (<strong>loi de Snell-Descartes</strong> appliquée en gradient continu).</p>
<p>À un angle rasant suffisant, la courbure est telle que la lumière « remonte » vers l'observateur → on voit le ciel projeté sur la route (apparence de flaque d'eau). L'image inversée en dessous de l'objet est caractéristique du <strong>mirage inférieur</strong>.</p>
<p>À distinguer du mirage <em>supérieur</em> (image au-dessus, inversion thermique en altitude) et de la <em>Fata Morgana</em> (couches multiples créant des images empilées et déformées).</p>`,
    demarche: [
      'Identifier le type de mirage : inférieur (sol chaud) vs supérieur (inversion thermique en altitude) vs Fata Morgana (couches multiples)',
      'Documenter les conditions : température au sol, température de l\'air, heure, ensoleillement, nature de la surface',
      'Mesurer si possible : distance d\'observation, angle d\'élévation, hauteur de l\'observateur par rapport au sol',
      'Comparer avec les modèles : le gradient thermique mesuré produit-il la courbure observée ?',
      'Tester la reproductibilité : le même effet se produit-il dans des conditions similaires ?',
    ],
    checklist: [
      'La vidéo montre-t-elle la scène complète (pas de zoom sélectif) ?',
      'Les conditions météo sont-elles documentées (T°, vent, humidité) ?',
      'La distance d\'observation est-elle connue ou estimable ?',
      'La hauteur de la caméra par rapport au sol est-elle précisée ?',
      'Le phénomène disparaît-il à l\'approche (test classique du mirage) ?',
      'A-t-on considéré d\'autres explications (eau réelle, reflet d\'objet) ?',
      'La focale/zoom de la caméra est-elle connue (effet de compression optique) ?',
    ],
    svgDiagram: `<svg viewBox="0 0 700 260" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:700px;border-radius:10px;background:#0d1117">
  <text x="350" y="25" text-anchor="middle" fill="#8B7EC8" font-size="13" font-weight="700" font-family="Plus Jakarta Sans,sans-serif">MIRAGE INFÉRIEUR — COURBURE DES RAYONS LUMINEUX</text>
  <rect x="40" y="200" width="620" height="40" rx="0" fill="#2a3140"/>
  <text x="350" y="225" text-anchor="middle" fill="#607890" font-size="10" font-family="JetBrains Mono,monospace">ROUTE (bitume chaud 60-70°C)</text>
  <text x="60" y="80" fill="#607890" font-size="9" font-family="JetBrains Mono,monospace">AIR FROID (dense)</text>
  <text x="60" y="185" fill="#C45E6A" font-size="9" font-family="JetBrains Mono,monospace">AIR CHAUD (peu dense)</text>
  <line x1="40" y1="95" x2="660" y2="95" stroke="#607890" stroke-width="0.5" stroke-dasharray="4,4"/>
  <line x1="40" y1="140" x2="660" y2="140" stroke="#607890" stroke-width="0.5" stroke-dasharray="4,4"/>
  <line x1="40" y1="175" x2="660" y2="175" stroke="#C45E6A" stroke-width="0.5" stroke-dasharray="4,4"/>
  <text x="670" y="98" fill="#607890" font-size="8" font-family="JetBrains Mono,monospace">n₁</text>
  <text x="670" y="143" fill="#607890" font-size="8" font-family="JetBrains Mono,monospace">n₂</text>
  <text x="670" y="178" fill="#C45E6A" font-size="8" font-family="JetBrains Mono,monospace">n₃</text>
  <circle cx="580" cy="60" r="6" fill="#D4943A"/>
  <text x="580" y="50" text-anchor="middle" fill="#D4943A" font-size="9" font-family="JetBrains Mono,monospace">objet réel</text>
  <path d="M 580,66 Q 400,195 120,150" fill="none" stroke="#D4943A" stroke-width="2"/>
  <path d="M 580,66 L 120,120" fill="none" stroke="#3B8FD4" stroke-width="1.5" stroke-dasharray="4,3"/>
  <circle cx="120" cy="150" r="8" fill="none" stroke="#e8edf4" stroke-width="1.5"/>
  <line x1="120" y1="158" x2="120" y2="190" stroke="#e8edf4" stroke-width="1.5"/>
  <text x="120" y="50" text-anchor="middle" fill="#e8edf4" font-size="9" font-family="JetBrains Mono,monospace">observateur</text>
  <text x="350" y="165" text-anchor="middle" fill="#D4943A" font-size="10" font-weight="600" font-family="Plus Jakarta Sans,sans-serif">rayon courbé par le gradient thermique</text>
  <text x="300" y="110" text-anchor="middle" fill="#3B8FD4" font-size="9" font-family="Plus Jakarta Sans,sans-serif">trajet direct (image réelle)</text>
  <line x1="120" y1="155" x2="200" y2="200" stroke="#3D9E7C" stroke-width="1.5" stroke-dasharray="3,3"/>
  <circle cx="210" cy="205" r="4" fill="#3D9E7C" opacity="0.6"/>
  <text x="260" y="250" fill="#3D9E7C" font-size="9" font-family="Plus Jakarta Sans,sans-serif">image inversée (mirage) : le ciel apparaît sur la route</text>
</svg>`,
    relatedArticle: 'pression-lumiere-halos-rayons-et-ondes',
  },
];
