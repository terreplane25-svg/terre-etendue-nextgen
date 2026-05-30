// ═══════════════════════════════════════════════════════
// NEXUS DATA — Auto-generated from 24 articles
// Terre Étendue Islam — Graphe de connaissances
// ═══════════════════════════════════════════════════════

export interface NexusNodeData {
  id: string;
  title: string;
  category: 'headquarters' | 'observatory' | 'library' | 'lab';
  pillar: string;
  pillarNum: string;
  color: string;
  primaryDomain: string;
  topDomains: string[];
  quranRefs: number;
  wordCount: number;
  x?: number;
  y?: number;
  size?: number;
}

export interface NexusLinkData {
  source: string;
  target: string;
  score: number;
  strength: 'strong' | 'medium' | 'weak';
  sharedDomains: string[];
}

export const DOMAIN_LABELS: Record<string, string> = {
  "geometrie": "Géométrie",
  "astronomie": "Astronomie",
  "optique": "Optique & Vision",
  "gravite": "Gravité",
  "cartographie": "Cartographie",
  "hydrologie": "Hydrologie",
  "histoire_sciences": "Histoire des Sciences",
  "islam_sources": "Sources Islamiques",
  "epistemologie": "Épistémologie",
  "physique": "Physique Expérimentale",
  "cosmologie": "Cosmologie",
  "modelisation": "Modélisation"
};

export const NEXUS_NODES: NexusNodeData[] = [
  {
    "id": "200-ans-de-resultats-nuls-darago-a-einstein",
    "title": "200 ans de résultats nuls : d'Arago à Einstein",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "physique",
    "topDomains": [
      "physique",
      "hydrologie",
      "cosmologie"
    ],
    "quranRefs": 0,
    "wordCount": 2422,
    "x": 191.5,
    "y": -160.7,
    "size": 8
  },
  {
    "id": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "title": "Cartes, routes, boussoles et le mystère antarctique",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "cartographie",
    "topDomains": [
      "cartographie",
      "hydrologie",
      "geometrie"
    ],
    "quranRefs": 0,
    "wordCount": 3876,
    "x": 160.7,
    "y": 191.5,
    "size": 8
  },
  {
    "id": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "title": "Ce qu'on voit quand on ne devrait plus voir",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "optique",
    "topDomains": [
      "optique",
      "geometrie",
      "hydrologie"
    ],
    "quranRefs": 0,
    "wordCount": 2064,
    "x": 157.8,
    "y": 289.8,
    "size": 8
  },
  {
    "id": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "title": "Début de la Création : le Soleil mobile, la Terre immobile",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "astronomie",
    "topDomains": [
      "astronomie",
      "islam_sources",
      "cosmologie"
    ],
    "quranRefs": 5,
    "wordCount": 1012,
    "x": -191.5,
    "y": 160.7,
    "size": 8
  },
  {
    "id": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "title": "Début de la Création : Selon le Coran et la Sunna",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "cosmologie",
    "topDomains": [
      "cosmologie",
      "astronomie",
      "islam_sources"
    ],
    "quranRefs": 3,
    "wordCount": 963,
    "x": -301.5,
    "y": 134.2,
    "size": 8
  },
  {
    "id": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "title": "Dhū al-Qarnayn : confins terrestres et rupture ptoléméenne",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": [
      "islam_sources",
      "cosmologie",
      "hydrologie"
    ],
    "quranRefs": 8,
    "wordCount": 1092,
    "x": -406.0,
    "y": 57.1,
    "size": 8
  },
  {
    "id": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "title": "D'une Terre plate universelle à la sphère grecque",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "cosmologie",
    "topDomains": [
      "cosmologie",
      "geometrie",
      "astronomie"
    ],
    "quranRefs": 7,
    "wordCount": 6253,
    "x": 285.8,
    "y": -165.0,
    "size": 8
  },
  {
    "id": "etat-des-lieux-ou-en-sommes-nous",
    "title": "État des lieux : où en sommes-nous ?",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "epistemologie",
    "topDomains": [
      "epistemologie",
      "geometrie",
      "hydrologie"
    ],
    "quranRefs": 4,
    "wordCount": 1558,
    "x": 385.3,
    "y": -140.2,
    "size": 8
  },
  {
    "id": "la-gravite-70-theories-et-aucune-certitude",
    "title": "La gravité : 70 théories et aucune certitude",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "gravite",
    "topDomains": [
      "gravite",
      "epistemologie",
      "histoire_sciences"
    ],
    "quranRefs": 0,
    "wordCount": 4186,
    "x": 246.2,
    "y": -43.4,
    "size": 8
  },
  {
    "id": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "title": "La Lune, le Soleil et les étoiles : ce que le ciel nous montre",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "astronomie",
    "topDomains": [
      "astronomie",
      "optique",
      "geometrie"
    ],
    "quranRefs": 7,
    "wordCount": 2271,
    "x": 120.8,
    "y": 391.8,
    "size": 8
  },
  {
    "id": "la-terre-dans-le-coran",
    "title": "La Terre dans le Coran",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "geometrie",
    "topDomains": [
      "geometrie",
      "cosmologie",
      "islam_sources"
    ],
    "quranRefs": 19,
    "wordCount": 2065,
    "x": -247.6,
    "y": -34.8,
    "size": 8
  },
  {
    "id": "le-concordisme",
    "title": "Le concordisme",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "islam_sources",
    "topDomains": [
      "islam_sources",
      "epistemologie",
      "cosmologie"
    ],
    "quranRefs": 29,
    "wordCount": 2178,
    "x": 330.0,
    "y": 0.0,
    "size": 8
  },
  {
    "id": "le-consensus-sur-la-sphericite",
    "title": "Le « consensus » sur la sphéricité",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": [
      "islam_sources",
      "epistemologie",
      "geometrie"
    ],
    "quranRefs": 4,
    "wordCount": 1146,
    "x": -301.5,
    "y": -134.2,
    "size": 8
  },
  {
    "id": "le-modele-geocentrique-a-plans-paralleles-mgpp",
    "title": "Le Modèle Géocentrique à Plans Parallèles (MGPP)",
    "category": "lab",
    "pillar": "LAB",
    "pillarNum": "04",
    "color": "#00C8FF",
    "primaryDomain": "hydrologie",
    "topDomains": [
      "hydrologie",
      "gravite",
      "modelisation"
    ],
    "quranRefs": 0,
    "wordCount": 2650,
    "x": -160.7,
    "y": -191.5,
    "size": 8
  },
  {
    "id": "le-mythe-deratosthene",
    "title": "Le mythe d'Ératosthène",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "geometrie",
    "topDomains": [
      "geometrie",
      "epistemologie",
      "cosmologie"
    ],
    "quranRefs": 0,
    "wordCount": 2240,
    "x": 403.8,
    "y": 71.2,
    "size": 8
  },
  {
    "id": "le-theodolite-celeste",
    "title": "Le théodolite céleste",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "geometrie",
    "topDomains": [
      "geometrie",
      "astronomie",
      "modelisation"
    ],
    "quranRefs": 1,
    "wordCount": 2220,
    "x": 24.9,
    "y": 248.8,
    "size": 8
  },
  {
    "id": "leau-ne-ment-pas",
    "title": "L'eau ne ment pas",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "hydrologie",
    "topDomains": [
      "hydrologie",
      "geometrie",
      "optique"
    ],
    "quranRefs": 0,
    "wordCount": 2257,
    "x": -32.9,
    "y": 328.4,
    "size": 8
  },
  {
    "id": "lespace-une-frontiere-infranchissable",
    "title": "L'espace : une frontière infranchissable ?",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "geometrie",
    "topDomains": [
      "geometrie",
      "cosmologie",
      "hydrologie"
    ],
    "quranRefs": 0,
    "wordCount": 1426,
    "x": -120.8,
    "y": 391.8,
    "size": 8
  },
  {
    "id": "lhorizon-la-perspective-et-la-refraction",
    "title": "L'horizon, la perspective et la réfraction",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "optique",
    "topDomains": [
      "optique",
      "geometrie",
      "hydrologie"
    ],
    "quranRefs": 0,
    "wordCount": 2517,
    "x": -119.6,
    "y": 219.6,
    "size": 8
  },
  {
    "id": "lhypothese-nulle-dynamique-et-cinematique",
    "title": "L'hypothèse nulle : dynamique et cinématique",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "astronomie",
    "topDomains": [
      "astronomie",
      "gravite",
      "cosmologie"
    ],
    "quranRefs": 0,
    "wordCount": 2503,
    "x": 234.9,
    "y": 85.5,
    "size": 8
  },
  {
    "id": "neptune-et-pluton-les-faux-triomphes",
    "title": "Neptune et Pluton : les faux triomphes",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "gravite",
    "topDomains": [
      "gravite",
      "geometrie",
      "modelisation"
    ],
    "quranRefs": 0,
    "wordCount": 1782,
    "x": 285.8,
    "y": 165.0,
    "size": 8
  },
  {
    "id": "pourquoi-tout-remettre-en-question",
    "title": "Pourquoi tout remettre en question",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#00C8FF",
    "primaryDomain": "epistemologie",
    "topDomains": [
      "epistemologie",
      "cosmologie",
      "histoire_sciences"
    ],
    "quranRefs": 1,
    "wordCount": 2790,
    "x": 314.1,
    "y": 263.5,
    "size": 8
  },
  {
    "id": "pres-de-cent-savants-de-lislam",
    "title": "Près de cent savants de l'islam",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": [
      "islam_sources",
      "geometrie",
      "cosmologie"
    ],
    "quranRefs": 2,
    "wordCount": 951,
    "x": -314.1,
    "y": -263.5,
    "size": 8
  },
  {
    "id": "pression-lumiere-halos-rayons-et-ondes",
    "title": "Pression, lumière, halos, rayons et ondes",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00C8FF",
    "primaryDomain": "geometrie",
    "topDomains": [
      "geometrie",
      "optique",
      "astronomie"
    ],
    "quranRefs": 0,
    "wordCount": 1713,
    "x": -212.1,
    "y": 252.8,
    "size": 8
  }
];

export const NEXUS_LINKS: NexusLinkData[] = [
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "le-theodolite-celeste",
    "score": 387.6,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "le-theodolite-celeste",
    "score": 360.4,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "score": 325.2,
    "strength": "strong",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "etat-des-lieux-ou-en-sommes-nous",
    "score": 308.9,
    "strength": "strong",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 305.8,
    "strength": "strong",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "leau-ne-ment-pas",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 239.2,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 236.6,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-certitude",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 223.6,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "le-theodolite-celeste",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 219.7,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-certitude",
    "target": "le-modele-geocentrique-a-plans-paralleles-mgpp",
    "score": 216,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "leau-ne-ment-pas",
    "score": 205.4,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 204.4,
    "strength": "strong",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-certitude",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 202.8,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "la-gravite-70-theories-et-aucune-certitude",
    "score": 200.2,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 193.7,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "le-theodolite-celeste",
    "target": "leau-ne-ment-pas",
    "score": 192.4,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "score": 188.4,
    "strength": "strong",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "le-modele-geocentrique-a-plans-paralleles-mgpp",
    "target": "leau-ne-ment-pas",
    "score": 188,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "lhypothese-nulle-dynamique-et-cinematique",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 172.9,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "le-modele-geocentrique-a-plans-paralleles-mgpp",
    "score": 170,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "le-modele-geocentrique-a-plans-paralleles-mgpp",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 169,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 165.1,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "la-terre-dans-le-coran",
    "score": 154.4,
    "strength": "strong",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "le-mythe-deratosthene",
    "score": 152.1,
    "strength": "strong",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 145.6,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 144.3,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "la-terre-dans-le-coran",
    "score": 143.5,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "le-mythe-deratosthene",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 143.0,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "la-terre-dans-le-coran",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 142.0,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "la-terre-dans-le-coran",
    "score": 126,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "score": 118.6,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "le-concordisme",
    "target": "le-mythe-deratosthene",
    "score": 105.3,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "le-mythe-deratosthene",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 96,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "score": 92.0,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "modelisation"
    ]
  },
  {
    "source": "le-consensus-sur-la-sphericite",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 92.0,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "le-concordisme",
    "target": "le-consensus-sur-la-sphericite",
    "score": 90.0,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "le-concordisme",
    "score": 89.7,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 88.9,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 88,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 87.4,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "le-concordisme",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 81.9,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "le-consensus-sur-la-sphericite",
    "score": 76.4,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "geometrie"
    ]
  },
  {
    "source": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "target": "le-consensus-sur-la-sphericite",
    "score": 74.9,
    "strength": "medium",
    "sharedDomains": [
      "islam_sources",
      "cosmologie",
      "epistemologie"
    ]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 59,
    "strength": "medium",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 46.8,
    "strength": "weak",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "lespace-une-frontiere-infranchissable",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 35,
    "strength": "weak",
    "sharedDomains": [
      "cosmologie",
      "geometrie",
      "modelisation"
    ]
  },
  {
    "source": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 22,
    "strength": "weak",
    "sharedDomains": [
      "cosmologie",
      "modelisation",
      "epistemologie"
    ]
  }
];

export const NEXUS_STATS = {
  "totalArticles": 24,
  "totalLinks": 47,
  "pillars": {
    "headquarters": 9,
    "observatory": 8,
    "library": 6,
    "lab": 1
  },
  "domainCoverage": 12
};
