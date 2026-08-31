// ═══════════════════════════════════════════════════════
// NEXUS DATA — 53 articles, 119 liens
// Terre Étendue Islam — Graphe de connaissances
//
// Fichier généré. Ne pas éditer à la main :
//   python3 scripts/reparer-nexus.py
//
// Les titres et les catégories viennent de content/articles/*.json,
// seule source qui fasse foi. Les domaines et les liens sont conservés
// d'une génération à l'autre : ce sont eux le travail humain.
// ═══════════════════════════════════════════════════════

export interface NexusNodeData {
  id: string;
  title: string;
  category: 'headquarters' | 'observatory' | 'library' | 'experiences' | 'meta';
  primaryDomain: string;
  topDomains: string[];
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
  "modelisation": "Modélisation",
};

export const NEXUS_NODES: NexusNodeData[] = [
  {
    "id": "mesures-sous-le-ciel-trigonometrie-plane",
    "title": "11 320 mesures sous le ciel : L'épreuve de la trigonométrie plane",
    "category": "observatory",
    "primaryDomain": "geometrie",
    "topDomains": ["geometrie", "astronomie", "modelisation"]
  },
  {
    "id": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "title": "Cartes, routes, boussoles et le mystère antarctique",
    "category": "observatory",
    "primaryDomain": "cartographie",
    "topDomains": ["cartographie", "hydrologie", "geometrie"]
  },
  {
    "id": "chronologie-critique-du-modele-globe",
    "title": "Chronologie critique du modèle globe",
    "category": "headquarters",
    "primaryDomain": "histoire_sciences",
    "topDomains": ["histoire_sciences", "epistemologie", "cosmologie"]
  },
  {
    "id": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "title": "D'une Terre plate universelle à la sphère grecque",
    "category": "headquarters",
    "primaryDomain": "cosmologie",
    "topDomains": ["cosmologie", "geometrie", "histoire_sciences"]
  },
  {
    "id": "densite-pourquoi-les-choses-montent-et-descendent",
    "title": "Densité et flottabilité : pourquoi les choses montent, flottent ou coulent",
    "category": "experiences",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "id": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "title": "Dhū al-Qarnayn : confins terrestres et rupture ptoléméenne",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cosmologie", "cartographie"]
  },
  {
    "id": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "title": "Début de la Création : le Soleil mobile, la Terre immobile",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "astronomie", "cosmologie"]
  },
  {
    "id": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "title": "Début de la Création : Selon le Coran et la Sunna",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cosmologie", "astronomie"]
  },
  {
    "id": "financement-et-independance",
    "title": "Financement et indépendance",
    "category": "meta",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "id": "glossaire",
    "title": "Glossaire",
    "category": "meta",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "islam_sources", "histoire_sciences"]
  },
  {
    "id": "index-thematique",
    "title": "Index thématique",
    "category": "meta",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "islam_sources"]
  },
  {
    "id": "leau-ne-ment-pas",
    "title": "L'eau ne ment pas",
    "category": "experiences",
    "primaryDomain": "hydrologie",
    "topDomains": ["hydrologie", "geometrie", "optique"]
  },
  {
    "id": "lespace-une-frontiere-infranchissable",
    "title": "L'espace : une frontière infranchissable ?",
    "category": "observatory",
    "primaryDomain": "cosmologie",
    "topDomains": ["cosmologie", "geometrie", "physique"]
  },
  {
    "id": "lexperience-contre-la-theorie",
    "title": "L'expérience contre la théorie",
    "category": "headquarters",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "id": "lenigme-de-la-terre-immobile",
    "title": "L'énigme de la Terre immobile : Comment deux siècles d'échecs ont donné naissance à la Relativité",
    "category": "headquarters",
    "primaryDomain": "physique",
    "topDomains": ["physique", "epistemologie", "cosmologie"]
  },
  {
    "id": "levolution-et-lislam",
    "title": "L'évolution et l'Islam",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "epistemologie", "cosmologie"]
  },
  {
    "id": "loeil-humain-la-machine-a-voir",
    "title": "L'Œil humain : la machine à voir",
    "category": "experiences",
    "primaryDomain": "optique",
    "topDomains": ["optique", "physique", "geometrie"]
  },
  {
    "id": "la-cosmologie-comme-instrument-de-domination",
    "title": "La cosmologie comme instrument de domination",
    "category": "headquarters",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "id": "la-gravite-70-theories-et-aucune-preuve",
    "title": "La Gravité : 70 théories, aucune preuve, et une crise que personne ne nomme",
    "category": "headquarters",
    "primaryDomain": "gravite",
    "topDomains": ["gravite", "epistemologie", "physique"]
  },
  {
    "id": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "title": "La Lune : six anomalies que le modèle standard ne résout pas",
    "category": "observatory",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "hydrologie"]
  },
  {
    "id": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "title": "La Lune, le Soleil et les étoiles : ce que le ciel nous montre",
    "category": "observatory",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "optique", "geometrie"]
  },
  {
    "id": "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah",
    "title": "La mobilité de la Terre attribuée à Ibn Taymiyyah : anatomie d'un taṣḥīf",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "epistemologie", "histoire_sciences"]
  },
  {
    "id": "la-perspective-pourquoi-les-objets-disparaissent",
    "title": "La Perspective : pourquoi les objets disparaissent",
    "category": "observatory",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"]
  },
  {
    "id": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "title": "La Pression Atmosphérique : un océan d'air invisible qui n'a pas besoin de la gravité",
    "category": "experiences",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "hydrologie"]
  },
  {
    "id": "la-qibla-et-la-direction-cote-ouest",
    "title": "La qibla et la direction côté ouest",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cartographie", "geometrie"]
  },
  {
    "id": "la-rotation-terrestre-experiences-preuves-verdict",
    "title": "La rotation terrestre : les expériences, les preuves, le verdict",
    "category": "headquarters",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences", "physique"]
  },
  {
    "id": "la-terre-dans-le-coran",
    "title": "La Terre dans le Coran",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cosmologie", "astronomie"]
  },
  {
    "id": "le-concordisme",
    "title": "Le concordisme",
    "category": "headquarters",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "epistemologie", "cosmologie"]
  },
  {
    "id": "le-mythe-deratosthene",
    "title": "Le mythe d'Ératosthène",
    "category": "headquarters",
    "primaryDomain": "geometrie",
    "topDomains": ["geometrie", "epistemologie", "cosmologie"]
  },
  {
    "id": "le-pole-sud-nexiste-pas",
    "title": "Le pôle Sud n'existe pas",
    "category": "observatory",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "id": "le-consensus-sur-la-sphericite",
    "title": "Le « consensus » sur la sphéricité",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "epistemologie", "geometrie"]
  },
  {
    "id": "les-distances-cosmiques-au-dela-de-la-regle",
    "title": "Les distances cosmiques : au-delà de la règle",
    "category": "headquarters",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "epistemologie", "cosmologie"]
  },
  {
    "id": "les-forces-invisibles-a-faire-chez-soi",
    "title": "Les forces invisibles : électricité, magnétisme, action-réaction",
    "category": "experiences",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "id": "les-marees-contre-lheliocentrisme",
    "title": "Les marées contre l'héliocentrisme",
    "category": "observatory",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "id": "les-trous-noirs-existent-ils",
    "title": "Les trous noirs existent-ils ?",
    "category": "headquarters",
    "primaryDomain": "cosmologie",
    "topDomains": ["cosmologie", "epistemologie", "physique"]
  },
  {
    "id": "lire-le-ciel-avant-le-globe",
    "title": "Lire le ciel avant le globe",
    "category": "headquarters",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "histoire_sciences", "islam_sources"]
  },
  {
    "id": "mesurer-la-courbure-sur-l-eau-cinq-campagnes",
    "title": "Mesurer la courbure sur l'eau : cinq campagnes, et celle qui manque",
    "category": "observatory",
    "primaryDomain": "geometrie",
    "topDomains": ["geometrie", "optique", "hydrologie"]
  },
  {
    "id": "mise-en-garde-la-kaaba-et-saturne",
    "title": "Mise en garde : la Kaaba et Saturne",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "histoire_sciences", "epistemologie"]
  },
  {
    "id": "monter-l-experience-des-trois-mires",
    "title": "Monter l'expérience des trois mires",
    "category": "experiences",
    "primaryDomain": "geometrie",
    "topDomains": ["geometrie", "hydrologie", "optique"]
  },
  {
    "id": "neptune-et-pluton-les-faux-triomphes",
    "title": "Neptune et Pluton : les faux triomphes",
    "category": "headquarters",
    "primaryDomain": "gravite",
    "topDomains": ["gravite", "astronomie", "modelisation"]
  },
  {
    "id": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "title": "Où est Allah ? Le ʿuluww et la forme du monde",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cosmologie", "epistemologie"]
  },
  {
    "id": "par-rapport-a-quoi-mesure-t-on-une-altitude",
    "title": "Par rapport à quoi mesure-t-on une altitude ?",
    "category": "headquarters",
    "primaryDomain": "geometrie",
    "topDomains": ["geometrie", "epistemologie", "hydrologie"]
  },
  {
    "id": "participer-aux-campagnes-de-mesure",
    "title": "Participer : nos protocoles, et comment y prendre part",
    "category": "experiences",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "modelisation", "physique"]
  },
  {
    "id": "pourquoi-tout-remettre-en-question",
    "title": "Pourquoi tout remettre en question",
    "category": "headquarters",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "id": "pression-lumiere-halos-rayons-et-ondes",
    "title": "Pression, lumière, halos, rayons et ondes",
    "category": "experiences",
    "primaryDomain": "optique",
    "topDomains": ["optique", "astronomie", "geometrie"]
  },
  {
    "id": "pres-de-cent-savants-de-lislam",
    "title": "Près de cent savants de l'islam",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "histoire_sciences", "cosmologie"]
  },
  {
    "id": "les-protocoles-ce-que-c-est-et-pourquoi",
    "title": "Qu'est-ce qu'un protocole, et pourquoi nous en écrivons",
    "category": "experiences",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "geometrie", "optique"]
  },
  {
    "id": "corrections",
    "title": "Registre des corrections",
    "category": "meta",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie"]
  },
  {
    "id": "sources-historiques-fonds-documentaire",
    "title": "Sources historiques : le fonds documentaire (1865-1920)",
    "category": "library",
    "primaryDomain": "histoire_sciences",
    "topDomains": ["histoire_sciences", "epistemologie", "islam_sources"]
  },
  {
    "id": "standards-et-methode",
    "title": "Standards et méthode",
    "category": "meta",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie"]
  },
  {
    "id": "un-traite-ottoman-contre-la-sphericite-1314h",
    "title": "Un traité ottoman contre la sphéricité (1314 H)",
    "category": "library",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "geometrie", "histoire_sciences"]
  },
  {
    "id": "vols-avion-et-courbure-terrestre",
    "title": "Vols d'avion et courbure terrestre — ce que disent vraiment les instruments",
    "category": "observatory",
    "primaryDomain": "geometrie",
    "topDomains": ["geometrie", "astronomie", "epistemologie"]
  },
  {
    "id": "etat-des-lieux-ou-en-sommes-nous",
    "title": "État des lieux : où en sommes-nous ?",
    "category": "meta",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "geometrie", "hydrologie"]
  },
];

export const NEXUS_LINKS: NexusLinkData[] = [
  {
    "source": "standards-et-methode",
    "target": "corrections",
    "score": 445.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "target": "la-terre-dans-le-coran",
    "score": 438.0,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah",
    "target": "le-consensus-sur-la-sphericite",
    "score": 420.0,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "par-rapport-a-quoi-mesure-t-on-une-altitude",
    "target": "leau-ne-ment-pas",
    "score": 402.0,
    "strength": "strong",
    "sharedDomains": ["geometrie", "hydrologie"]
  },
  {
    "source": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "target": "le-consensus-sur-la-sphericite",
    "score": 396.0,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "par-rapport-a-quoi-mesure-t-on-une-altitude",
    "target": "monter-l-experience-des-trois-mires",
    "score": 388.0,
    "strength": "strong",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "les-forces-invisibles-a-faire-chez-soi",
    "target": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "score": 378.1,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "le-pole-sud-nexiste-pas",
    "target": "les-marees-contre-lheliocentrisme",
    "score": 374.2,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "source": "la-cosmologie-comme-instrument-de-domination",
    "target": "la-rotation-terrestre-experiences-preuves-verdict",
    "score": 373.4,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "score": 371.6,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "astronomie", "cosmologie"]
  },
  {
    "source": "par-rapport-a-quoi-mesure-t-on-une-altitude",
    "target": "mesurer-la-courbure-sur-l-eau-cinq-campagnes",
    "score": 371.0,
    "strength": "strong",
    "sharedDomains": ["geometrie", "hydrologie"]
  },
  {
    "source": "la-perspective-pourquoi-les-objets-disparaissent",
    "target": "loeil-humain-la-machine-a-voir",
    "score": 362.2,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "target": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "score": 362.0,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "les-trous-noirs-existent-ils",
    "score": 355.0,
    "strength": "strong",
    "sharedDomains": ["gravite", "epistemologie", "physique"]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "la-terre-dans-le-coran",
    "score": 354.3,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie", "astronomie"]
  },
  {
    "source": "le-pole-sud-nexiste-pas",
    "target": "les-forces-invisibles-a-faire-chez-soi",
    "score": 352.7,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "source": "la-perspective-pourquoi-les-objets-disparaissent",
    "target": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "score": 348.5,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "hydrologie"]
  },
  {
    "source": "les-marees-contre-lheliocentrisme",
    "target": "les-forces-invisibles-a-faire-chez-soi",
    "score": 338.5,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "source": "la-rotation-terrestre-experiences-preuves-verdict",
    "target": "lexperience-contre-la-theorie",
    "score": 335.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "source": "la-cosmologie-comme-instrument-de-domination",
    "target": "lexperience-contre-la-theorie",
    "score": 334.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "la-terre-dans-le-coran",
    "score": 334.3,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "astronomie", "cosmologie"]
  },
  {
    "source": "lire-le-ciel-avant-le-globe",
    "target": "mesures-sous-le-ciel-trigonometrie-plane",
    "score": 334.0,
    "strength": "strong",
    "sharedDomains": ["astronomie"]
  },
  {
    "source": "densite-pourquoi-les-choses-montent-et-descendent",
    "target": "les-forces-invisibles-a-faire-chez-soi",
    "score": 331.4,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "le-pole-sud-nexiste-pas",
    "score": 329.7,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "index-thematique",
    "target": "la-rotation-terrestre-experiences-preuves-verdict",
    "score": 327.6,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "corrections",
    "target": "etat-des-lieux-ou-en-sommes-nous",
    "score": 327.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "score": 326.1,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "densite-pourquoi-les-choses-montent-et-descendent",
    "target": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "score": 325.8,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "chronologie-critique-du-modele-globe",
    "target": "sources-historiques-fonds-documentaire",
    "score": 324.3,
    "strength": "strong",
    "sharedDomains": ["histoire_sciences", "epistemologie"]
  },
  {
    "source": "les-trous-noirs-existent-ils",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 323.0,
    "strength": "strong",
    "sharedDomains": ["cosmologie", "physique"]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 320.2,
    "strength": "strong",
    "sharedDomains": ["cosmologie", "geometrie"]
  },
  {
    "source": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "target": "le-concordisme",
    "score": 318.0,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "standards-et-methode",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 318.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "levolution-et-lislam",
    "score": 317.1,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "lenigme-de-la-terre-immobile",
    "target": "la-rotation-terrestre-experiences-preuves-verdict",
    "score": 316.7,
    "strength": "strong",
    "sharedDomains": ["physique", "epistemologie"]
  },
  {
    "source": "glossaire",
    "target": "la-rotation-terrestre-experiences-preuves-verdict",
    "score": 314.9,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "le-consensus-sur-la-sphericite",
    "target": "levolution-et-lislam",
    "score": 314.5,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "vols-avion-et-courbure-terrestre",
    "target": "la-perspective-pourquoi-les-objets-disparaissent",
    "score": 312.0,
    "strength": "strong",
    "sharedDomains": ["geometrie", "optique"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "le-concordisme",
    "score": 310.1,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "la-qibla-et-la-direction-cote-ouest",
    "target": "le-consensus-sur-la-sphericite",
    "score": 308.1,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "geometrie"]
  },
  {
    "source": "un-traite-ottoman-contre-la-sphericite-1314h",
    "target": "le-consensus-sur-la-sphericite",
    "score": 305.0,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "glossaire",
    "target": "index-thematique",
    "score": 304.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "islam_sources"]
  },
  {
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "les-marees-contre-lheliocentrisme",
    "score": 303.3,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "la-perspective-pourquoi-les-objets-disparaissent",
    "score": 303.2,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "le-consensus-sur-la-sphericite",
    "target": "mise-en-garde-la-kaaba-et-saturne",
    "score": 303.1,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "glossaire",
    "target": "la-cosmologie-comme-instrument-de-domination",
    "score": 302.5,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "standards-et-methode",
    "target": "la-gravite-70-theories-et-aucune-preuve",
    "score": 302.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "le-concordisme",
    "score": 298.4,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "lire-le-ciel-avant-le-globe",
    "target": "la-qibla-et-la-direction-cote-ouest",
    "score": 296.0,
    "strength": "medium",
    "sharedDomains": ["astronomie", "islam_sources"]
  },
  {
    "source": "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah",
    "target": "un-traite-ottoman-contre-la-sphericite-1314h",
    "score": 296.0,
    "strength": "medium",
    "sharedDomains": ["islam_sources", "histoire_sciences"]
  },
  {
    "source": "densite-pourquoi-les-choses-montent-et-descendent",
    "target": "le-pole-sud-nexiste-pas",
    "score": 295.9,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "densite-pourquoi-les-choses-montent-et-descendent",
    "target": "les-marees-contre-lheliocentrisme",
    "score": 295.4,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "la-terre-dans-le-coran",
    "target": "levolution-et-lislam",
    "score": 295.4,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "levolution-et-lislam",
    "target": "mise-en-garde-la-kaaba-et-saturne",
    "score": 294.4,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "target": "la-terre-dans-le-coran",
    "score": 294.2,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "target": "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah",
    "score": 294.0,
    "strength": "medium",
    "sharedDomains": ["islam_sources"]
  },
  {
    "source": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "target": "le-concordisme",
    "score": 290.4,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "la-mobilite-de-la-terre-attribuee-a-ibn-taymiyyah",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 288.0,
    "strength": "medium",
    "sharedDomains": ["islam_sources"]
  },
  {
    "source": "vols-avion-et-courbure-terrestre",
    "target": "leau-ne-ment-pas",
    "score": 287.0,
    "strength": "medium",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "loeil-humain-la-machine-a-voir",
    "score": 286.3,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "levolution-et-lislam",
    "score": 282.9,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "un-traite-ottoman-contre-la-sphericite-1314h",
    "target": "lexperience-contre-la-theorie",
    "score": 281.0,
    "strength": "medium",
    "sharedDomains": ["histoire_sciences", "epistemologie"]
  },
  {
    "source": "index-thematique",
    "target": "la-cosmologie-comme-instrument-de-domination",
    "score": 279.4,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "les-distances-cosmiques-au-dela-de-la-regle",
    "target": "la-gravite-70-theories-et-aucune-preuve",
    "score": 277.6,
    "strength": "strong",
    "sharedDomains": ["astronomie", "cosmologie"]
  },
  {
    "source": "mise-en-garde-la-kaaba-et-saturne",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 276.5,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "histoire_sciences"]
  },
  {
    "source": "ou-est-allah-le-uluww-et-la-forme-du-monde",
    "target": "un-traite-ottoman-contre-la-sphericite-1314h",
    "score": 276.0,
    "strength": "medium",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "target": "la-qibla-et-la-direction-cote-ouest",
    "score": 275.9,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cartographie"]
  },
  {
    "source": "la-terre-dans-le-coran",
    "target": "le-concordisme",
    "score": 275.5,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "index-thematique",
    "target": "lexperience-contre-la-theorie",
    "score": 274.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "score": 274.3,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "un-traite-ottoman-contre-la-sphericite-1314h",
    "target": "monter-l-experience-des-trois-mires",
    "score": 274.0,
    "strength": "medium",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "glossaire",
    "target": "lexperience-contre-la-theorie",
    "score": 273.4,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "lire-le-ciel-avant-le-globe",
    "target": "un-traite-ottoman-contre-la-sphericite-1314h",
    "score": 271.0,
    "strength": "medium",
    "sharedDomains": ["astronomie", "histoire_sciences"]
  },
  {
    "source": "le-concordisme",
    "target": "le-consensus-sur-la-sphericite",
    "score": 270.2,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "un-traite-ottoman-contre-la-sphericite-1314h",
    "target": "le-mythe-deratosthene",
    "score": 268.0,
    "strength": "medium",
    "sharedDomains": ["geometrie", "histoire_sciences"]
  },
  {
    "source": "participer-aux-campagnes-de-mesure",
    "target": "les-protocoles-ce-que-c-est-et-pourquoi",
    "score": 250.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "modelisation"]
  },
  {
    "source": "financement-et-independance",
    "target": "standards-et-methode",
    "score": 250.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "les-protocoles-ce-que-c-est-et-pourquoi",
    "target": "monter-l-experience-des-trois-mires",
    "score": 204.0,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "geometrie"]
  },
  {
    "source": "les-protocoles-ce-que-c-est-et-pourquoi",
    "target": "mesurer-la-courbure-sur-l-eau-cinq-campagnes",
    "score": 186.0,
    "strength": "medium",
    "sharedDomains": ["geometrie", "hydrologie"]
  },
  {
    "source": "monter-l-experience-des-trois-mires",
    "target": "mesurer-la-courbure-sur-l-eau-cinq-campagnes",
    "score": 186.0,
    "strength": "strong",
    "sharedDomains": ["geometrie", "hydrologie", "optique"]
  },
  {
    "source": "les-protocoles-ce-que-c-est-et-pourquoi",
    "target": "la-perspective-pourquoi-les-objets-disparaissent",
    "score": 178.0,
    "strength": "medium",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "mesurer-la-courbure-sur-l-eau-cinq-campagnes",
    "target": "leau-ne-ment-pas",
    "score": 168.0,
    "strength": "strong",
    "sharedDomains": ["geometrie", "hydrologie", "optique"]
  },
  {
    "source": "les-protocoles-ce-que-c-est-et-pourquoi",
    "target": "standards-et-methode",
    "score": 162.0,
    "strength": "medium",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "monter-l-experience-des-trois-mires",
    "target": "leau-ne-ment-pas",
    "score": 158.0,
    "strength": "strong",
    "sharedDomains": ["hydrologie", "geometrie"]
  },
  {
    "source": "mesurer-la-courbure-sur-l-eau-cinq-campagnes",
    "target": "la-perspective-pourquoi-les-objets-disparaissent",
    "score": 152.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "participer-aux-campagnes-de-mesure",
    "target": "monter-l-experience-des-trois-mires",
    "score": 150.0,
    "strength": "medium",
    "sharedDomains": ["geometrie", "epistemologie"]
  },
  {
    "source": "participer-aux-campagnes-de-mesure",
    "target": "standards-et-methode",
    "score": 150.0,
    "strength": "medium",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "financement-et-independance",
    "target": "corrections",
    "score": 150.0,
    "strength": "medium",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "la-rotation-terrestre-experiences-preuves-verdict",
    "target": "les-forces-invisibles-a-faire-chez-soi",
    "score": 148.4,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "la-qibla-et-la-direction-cote-ouest",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 142.8,
    "strength": "medium",
    "sharedDomains": ["islam_sources"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 140.6,
    "strength": "medium",
    "sharedDomains": ["astronomie", "gravite"]
  },
  {
    "source": "les-distances-cosmiques-au-dela-de-la-regle",
    "target": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "score": 140.1,
    "strength": "medium",
    "sharedDomains": ["astronomie"]
  },
  {
    "source": "chronologie-critique-du-modele-globe",
    "target": "le-mythe-deratosthene",
    "score": 139.7,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "le-mythe-deratosthene",
    "score": 138.6,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "geometrie"]
  },
  {
    "source": "les-trous-noirs-existent-ils",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 138.0,
    "strength": "medium",
    "sharedDomains": ["gravite"]
  },
  {
    "source": "leau-ne-ment-pas",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 136.2,
    "strength": "medium",
    "sharedDomains": ["geometrie", "optique"]
  },
  {
    "source": "mesures-sous-le-ciel-trigonometrie-plane",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 135.9,
    "strength": "medium",
    "sharedDomains": ["astronomie", "modelisation"]
  },
  {
    "source": "lenigme-de-la-terre-immobile",
    "target": "les-forces-invisibles-a-faire-chez-soi",
    "score": 135.7,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "les-distances-cosmiques-au-dela-de-la-regle",
    "target": "les-trous-noirs-existent-ils",
    "score": 134.9,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "mesures-sous-le-ciel-trigonometrie-plane",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 132.2,
    "strength": "medium",
    "sharedDomains": ["geometrie", "astronomie"]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "leau-ne-ment-pas",
    "score": 131.0,
    "strength": "medium",
    "sharedDomains": ["hydrologie", "geometrie"]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "les-trous-noirs-existent-ils",
    "score": 130.7,
    "strength": "medium",
    "sharedDomains": ["cosmologie"]
  },
  {
    "source": "chronologie-critique-du-modele-globe",
    "target": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "score": 129.7,
    "strength": "medium",
    "sharedDomains": ["histoire_sciences", "cosmologie"]
  },
  {
    "source": "pourquoi-tout-remettre-en-question",
    "target": "sources-historiques-fonds-documentaire",
    "score": 128.3,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "chronologie-critique-du-modele-globe",
    "target": "les-distances-cosmiques-au-dela-de-la-regle",
    "score": 128.2,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "mesures-sous-le-ciel-trigonometrie-plane",
    "score": 127.4,
    "strength": "medium",
    "sharedDomains": ["astronomie", "geometrie"]
  },
  {
    "source": "le-mythe-deratosthene",
    "target": "mesures-sous-le-ciel-trigonometrie-plane",
    "score": 127.1,
    "strength": "medium",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "la-gravite-70-theories-et-aucune-preuve",
    "score": 123.4,
    "strength": "medium",
    "sharedDomains": ["astronomie"]
  },
  {
    "source": "les-distances-cosmiques-au-dela-de-la-regle",
    "target": "le-mythe-deratosthene",
    "score": 123.1,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "etat-des-lieux-ou-en-sommes-nous",
    "score": 120.8,
    "strength": "medium",
    "sharedDomains": ["hydrologie", "geometrie"]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "leau-ne-ment-pas",
    "score": 120.6,
    "strength": "medium",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 120.4,
    "strength": "medium",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "la-qibla-et-la-direction-cote-ouest",
    "score": 115.4,
    "strength": "medium",
    "sharedDomains": ["cartographie", "geometrie"]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "le-mythe-deratosthene",
    "score": 115.1,
    "strength": "medium",
    "sharedDomains": ["cosmologie", "geometrie"]
  },
  {
    "source": "le-consensus-sur-la-sphericite",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 114.8,
    "strength": "medium",
    "sharedDomains": ["islam_sources"]
  },
  {
    "source": "la-qibla-et-la-direction-cote-ouest",
    "target": "mise-en-garde-la-kaaba-et-saturne",
    "score": 114.6,
    "strength": "medium",
    "sharedDomains": ["islam_sources"]
  },
  {
    "source": "financement-et-independance",
    "target": "participer-aux-campagnes-de-mesure",
    "score": 60.0,
    "strength": "weak",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "mesures-sous-le-ciel-trigonometrie-plane",
    "score": 47.8,
    "strength": "weak",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 41.8,
    "strength": "weak",
    "sharedDomains": ["physique"]
  },
];
