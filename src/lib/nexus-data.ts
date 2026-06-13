// ═══════════════════════════════════════════════════════
// NEXUS DATA — Auto-generated from 63 articles
// Terre Étendue Islam — Graphe de connaissances
// ═══════════════════════════════════════════════════════

export interface NexusNodeData {
  id: string;
  title: string;
  category: 'headquarters' | 'observatory' | 'library' | 'lab' | 'meta';
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
  "modelisation": "Modélisation",
};

export const NEXUS_NODES: NexusNodeData[] = [
  {
    "id": "200-ans-de-resultats-nuls-darago-a-einstein",
    "title": "200 ans de résultats nuls : d'Arago à Einstein",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 50.8,
    "y": -359.5,
    "size": 8
  },
  {
    "id": "accommodation-oculaire",
    "title": "L'accommodation : la mise au point de l'œil",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "physique", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 246.4,
    "y": -297.7,
    "size": 8
  },
  {
    "id": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "title": "Cartes, routes, boussoles et le mystère antarctique",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#4CAF50",
    "primaryDomain": "cartographie",
    "topDomains": ["cartographie", "hydrologie", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 318.4,
    "y": -145.4,
    "size": 8
  },
  {
    "id": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "title": "Ce qu'on voit quand on ne devrait plus voir",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "hydrologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 257.8,
    "y": -268.3,
    "size": 8
  },
  {
    "id": "champ-visuel-central-peripherique",
    "title": "Le champ visuel : vision centrale et vision périphérique",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "physique", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 276.5,
    "y": -203.2,
    "size": 8
  },
  {
    "id": "chronologie-de-la-tromperie-du-globe",
    "title": "Chronologie de la tromperie du globe",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#9C27B0",
    "primaryDomain": "histoire_sciences",
    "topDomains": ["histoire_sciences", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 377.4,
    "y": 52.0,
    "size": 8
  },
  {
    "id": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "title": "Début de la Création : le Soleil mobile, la Terre immobile",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "astronomie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 305.8,
    "y": 226.8,
    "size": 8
  },
  {
    "id": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "title": "Début de la Création : Selon le Coran et la Sunna",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cosmologie", "astronomie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 342.3,
    "y": 281.4,
    "size": 8
  },
  {
    "id": "densite-pourquoi-les-choses-montent-et-descendent",
    "title": "Densité : la vraie raison pour laquelle les choses montent, flottent ou coulent",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 68.2,
    "y": -313.5,
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
    "topDomains": ["islam_sources", "cosmologie", "cartographie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 302.7,
    "y": 347.0,
    "size": 8
  },
  {
    "id": "diminution-angulaire-taille-apparente",
    "title": "Pourquoi les objets lointains paraissent plus petits",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 210.2,
    "y": -244.2,
    "size": 8
  },
  {
    "id": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "title": "D'une Terre plate universelle à la sphère grecque",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#3F51B5",
    "primaryDomain": "cosmologie",
    "topDomains": ["cosmologie", "geometrie", "histoire_sciences"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 127.9,
    "y": 330.8,
    "size": 8
  },
  {
    "id": "electricite-statique-attraction-repulsion",
    "title": "L'électricité statique : attraction et répulsion sans contact",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 64.7,
    "y": -242.5,
    "size": 8
  },
  {
    "id": "etat-des-lieux-ou-en-sommes-nous",
    "title": "État des lieux : où en sommes-nous ?",
    "category": "meta",
    "pillar": "META",
    "pillarNum": "00",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "geometrie", "hydrologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -52.6,
    "y": 330.2,
    "size": 8
  },
  {
    "id": "ethique-intellectuelle",
    "title": "Éthique intellectuelle",
    "category": "meta",
    "pillar": "META",
    "pillarNum": "00",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "histoire_sciences", "islam_sources"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -20.7,
    "y": 385.4,
    "size": 8
  },
  {
    "id": "experiences-sous-pression-reduite",
    "title": "Expériences sous pression réduite : ce qui se passe quand l'air disparaît",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 7.8,
    "y": -310.3,
    "size": 8
  },
  {
    "id": "glossaire",
    "title": "Glossaire",
    "category": "meta",
    "pillar": "META",
    "pillarNum": "00",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "islam_sources", "histoire_sciences"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -69.7,
    "y": 440.9,
    "size": 8
  },
  {
    "id": "index-thematique",
    "title": "Index thématique",
    "category": "meta",
    "pillar": "META",
    "pillarNum": "00",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "islam_sources"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -121.2,
    "y": 384.0,
    "size": 8
  },
  {
    "id": "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
    "title": "Kings Dethroned : l'effondrement de la triangulation stellaire",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#7B68EE",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -229.2,
    "y": 232.0,
    "size": 8
  },
  {
    "id": "la-cosmologie-comme-instrument-de-domination",
    "title": "La cosmologie comme instrument de domination",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -160.7,
    "y": 383.6,
    "size": 8
  },
  {
    "id": "la-gravite-70-theories-et-aucune-preuve",
    "title": "La Gravité : 70 théories, aucune preuve, et une crise que personne ne nomme",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#FF9800",
    "primaryDomain": "gravite",
    "topDomains": ["gravite", "epistemologie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -312.4,
    "y": 43.4,
    "size": 8
  },
  {
    "id": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "title": "La Lune, le Soleil et les étoiles : ce que le ciel nous montre",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#7B68EE",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "optique", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -272.3,
    "y": 297.9,
    "size": 8
  },
  {
    "id": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "title": "La Lune : six anomalies que le modèle standard ne résout pas",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "hydrologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 181.2,
    "y": -201.4,
    "size": 8
  },
  {
    "id": "la-perspective-atmospherique",
    "title": "La perspective atmosphérique : pourquoi le lointain devient bleu et flou",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 126.8,
    "y": -189.5,
    "size": 8
  },
  {
    "id": "la-perspective-lineaire",
    "title": "La perspective linéaire : le point de fuite et l'illusion de la convergence",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 157.0,
    "y": -263.9,
    "size": 8
  },
  {
    "id": "la-perspective-pourquoi-les-objets-disparaissent",
    "title": "La Perspective : pourquoi les objets disparaissent (et pourquoi ils reviennent au zoom)",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 114.3,
    "y": -275.4,
    "size": 8
  },
  {
    "id": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "title": "La Pression Atmosphérique : un océan d'air invisible qui n'a pas besoin de la gravité",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "hydrologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 75.9,
    "y": -328.5,
    "size": 8
  },
  {
    "id": "la-qibla-et-la-direction-cote-ouest",
    "title": "La qibla et la direction côté ouest",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cartographie", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 256.5,
    "y": 280.4,
    "size": 8
  },
  {
    "id": "la-rotation-terrestre-deux-experiences-zero-preuve",
    "title": "La Rotation Terrestre : deux expériences canoniques, zéro preuve",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -227.3,
    "y": 333.5,
    "size": 8
  },
  {
    "id": "la-terre-dans-le-coran",
    "title": "La Terre dans le Coran",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "cosmologie", "astronomie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 191.1,
    "y": 269.2,
    "size": 8
  },
  {
    "id": "le-concordisme",
    "title": "Le concordisme",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 140.8,
    "y": 224.6,
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
    "topDomains": ["islam_sources", "epistemologie", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 219.9,
    "y": 209.8,
    "size": 8
  },
  {
    "id": "le-mouvement-zetetique-150-ans-de-resistance",
    "title": "Le mouvement zététique : 150 ans de résistance (1849-2000)",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -127.5,
    "y": 308.2,
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
    "topDomains": ["geometrie", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -288.2,
    "y": -152.3,
    "size": 8
  },
  {
    "id": "le-pendule-de-foucault-une-preuve-contestee",
    "title": "Le pendule de Foucault : une preuve contestée",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "astronomie", "epistemologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -43.6,
    "y": -286.7,
    "size": 8
  },
  {
    "id": "le-pole-sud-nexiste-pas",
    "title": "Le pôle Sud n'existe pas",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "cartographie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -109.6,
    "y": -289.9,
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
    "topDomains": ["geometrie", "astronomie", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -362.1,
    "y": -144.6,
    "size": 8
  },
  {
    "id": "leau-ne-ment-pas",
    "title": "L'eau ne ment pas",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#00BCD4",
    "primaryDomain": "hydrologie",
    "topDomains": ["hydrologie", "geometrie", "optique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -189.2,
    "y": -294.4,
    "size": 8
  },
  {
    "id": "les-distances-cosmiques-au-dela-de-la-regle",
    "title": "Les distances cosmiques : au-delà de la règle",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#7B68EE",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -365.4,
    "y": 238.3,
    "size": 8
  },
  {
    "id": "les-horloges-atomiques-ne-prouvent-rien",
    "title": "Les horloges atomiques ne prouvent rien",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "epistemologie", "astronomie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -57.5,
    "y": -356.0,
    "size": 8
  },
  {
    "id": "les-marees-contre-lheliocentrisme",
    "title": "Les marées contre l'héliocentrisme",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "cartographie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -69.7,
    "y": -391.1,
    "size": 8
  },
  {
    "id": "les-telescopes-et-la-courbure-terrestre",
    "title": "Les télescopes et la courbure terrestre",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 144.9,
    "y": -326.9,
    "size": 8
  },
  {
    "id": "les-trous-noirs-nexistent-pas",
    "title": "Les trous noirs n'existent pas",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#3F51B5",
    "primaryDomain": "cosmologie",
    "topDomains": ["cosmologie", "epistemologie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 70.1,
    "y": 382.6,
    "size": 8
  },
  {
    "id": "lespace-une-frontiere-infranchissable",
    "title": "L'espace : une frontière infranchissable ?",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#3F51B5",
    "primaryDomain": "cosmologie",
    "topDomains": ["cosmologie", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 57.8,
    "y": 270.2,
    "size": 8
  },
  {
    "id": "levolution-et-lislam",
    "title": "L'évolution et l'Islam",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "epistemologie", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 246.1,
    "y": 145.6,
    "size": 8
  },
  {
    "id": "lhorizon-la-perspective-et-la-refraction",
    "title": "L'horizon, la perspective et la réfraction",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "geometrie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 138.8,
    "y": -372.5,
    "size": 8
  },
  {
    "id": "lhypothese-nulle-dynamique-et-cinematique",
    "title": "L'hypothèse nulle : dynamique et cinématique",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#7B68EE",
    "primaryDomain": "astronomie",
    "topDomains": ["astronomie", "gravite", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -257.0,
    "y": 184.5,
    "size": 8
  },
  {
    "id": "ligo-londe-qui-nexistait-pas",
    "title": "LIGO : l'onde qui n'existait pas",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#FF9800",
    "primaryDomain": "gravite",
    "topDomains": ["gravite", "epistemologie", "physique"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -367.9,
    "y": 108.7,
    "size": 8
  },
  {
    "id": "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite",
    "title": "L'Œil Humain : la machine à voir qui façonne notre réalité",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "physique", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 168.7,
    "y": -418.2,
    "size": 8
  },
  {
    "id": "magnetisme-et-electromagnetisme",
    "title": "Magnétisme et électromagnétisme : les forces invisibles",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "cartographie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -65.6,
    "y": -452.1,
    "size": 8
  },
  {
    "id": "manifeste",
    "title": "Manifeste",
    "category": "meta",
    "pillar": "META",
    "pillarNum": "00",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "islam_sources"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -115.1,
    "y": 263.1,
    "size": 8
  },
  {
    "id": "masse-et-volume",
    "title": "Masse et volume : solides, liquides et gaz",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 6.2,
    "y": -407.9,
    "size": 8
  },
  {
    "id": "methodologie",
    "title": "Méthodologie",
    "category": "meta",
    "pillar": "META",
    "pillarNum": "00",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "histoire_sciences", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -71.3,
    "y": 226.1,
    "size": 8
  },
  {
    "id": "mise-en-garde-la-kaaba-et-saturne",
    "title": "Mise en garde : la Kaaba et Saturne",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#D4A843",
    "primaryDomain": "islam_sources",
    "topDomains": ["islam_sources", "histoire_sciences", "epistemologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 304.7,
    "y": 113.0,
    "size": 8
  },
  {
    "id": "neptune-et-pluton-les-faux-triomphes",
    "title": "Neptune et Pluton : les faux triomphes",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#FF9800",
    "primaryDomain": "gravite",
    "topDomains": ["gravite", "astronomie", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -393.0,
    "y": -21.0,
    "size": 8
  },
  {
    "id": "persistance-retinienne",
    "title": "La persistance rétinienne : quand l'œil voit ce qui n'est plus là",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "physique", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 206.8,
    "y": -342.8,
    "size": 8
  },
  {
    "id": "pourquoi-les-choses-montent-et-descendent",
    "title": "Pourquoi les choses montent et descendent",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 48.1,
    "y": -418.8,
    "size": 8
  },
  {
    "id": "pourquoi-tout-remettre-en-question",
    "title": "Pourquoi tout remettre en question",
    "category": "headquarters",
    "pillar": "Q.G.",
    "pillarNum": "01",
    "color": "#E91E63",
    "primaryDomain": "epistemologie",
    "topDomains": ["epistemologie", "cosmologie", "histoire_sciences"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": -56.1,
    "y": 308.3,
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
    "topDomains": ["islam_sources", "histoire_sciences", "cosmologie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 311.6,
    "y": 200.2,
    "size": 8
  },
  {
    "id": "pression-lumiere-halos-rayons-et-ondes",
    "title": "Pression, lumière, halos, rayons et ondes",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "astronomie", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 242.8,
    "y": -362.7,
    "size": 8
  },
  {
    "id": "principe-action-reaction",
    "title": "Le principe d'action et de réaction",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF5722",
    "primaryDomain": "physique",
    "topDomains": ["physique", "gravite", "modelisation"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 100.7,
    "y": -416.9,
    "size": 8
  },
  {
    "id": "sources-historiques-fonds-documentaire",
    "title": "Sources historiques : le fonds documentaire (1865-1920)",
    "category": "library",
    "pillar": "BIBLIO",
    "pillarNum": "03",
    "color": "#9C27B0",
    "primaryDomain": "histoire_sciences",
    "topDomains": ["histoire_sciences", "epistemologie", "islam_sources"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 290.9,
    "y": 54.4,
    "size": 8
  },
  {
    "id": "vision-binoculaire-stereoscopie",
    "title": "La vision binoculaire : comment nous percevons la profondeur",
    "category": "observatory",
    "pillar": "OBS",
    "pillarNum": "02",
    "color": "#FF6B6B",
    "primaryDomain": "optique",
    "topDomains": ["optique", "physique", "geometrie"],
    "quranRefs": 0,
    "wordCount": 0,
    "x": 294.2,
    "y": -334.5,
    "size": 8
  },
];

export const NEXUS_LINKS: NexusLinkData[] = [
  {
    "source": "electricite-statique-attraction-repulsion",
    "target": "experiences-sous-pression-reduite",
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
    "source": "les-telescopes-et-la-courbure-terrestre",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 373.9,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "la-cosmologie-comme-instrument-de-domination",
    "target": "la-rotation-terrestre-deux-experiences-zero-preuve",
    "score": 373.4,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "source": "le-pendule-de-foucault-une-preuve-contestee",
    "target": "les-horloges-atomiques-ne-prouvent-rien",
    "score": 373.0,
    "strength": "strong",
    "sharedDomains": ["physique", "astronomie", "epistemologie"]
  },
  {
    "source": "la-perspective-lineaire",
    "target": "la-perspective-pourquoi-les-objets-disparaissent",
    "score": 372.8,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "accommodation-oculaire",
    "target": "la-perspective-atmospherique",
    "score": 372.7,
    "strength": "strong",
    "sharedDomains": ["optique", "physique", "geometrie"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "score": 371.6,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "astronomie", "cosmologie"]
  },
  {
    "source": "persistance-retinienne",
    "target": "vision-binoculaire-stereoscopie",
    "score": 371.5,
    "strength": "strong",
    "sharedDomains": ["optique", "physique", "geometrie"]
  },
  {
    "source": "la-perspective-lineaire",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 370.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "la-perspective-pourquoi-les-objets-disparaissent",
    "target": "les-telescopes-et-la-courbure-terrestre",
    "score": 369.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "masse-et-volume",
    "target": "pourquoi-les-choses-montent-et-descendent",
    "score": 368.6,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "methodologie",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 367.2,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences", "cosmologie"]
  },
  {
    "source": "la-perspective-lineaire",
    "target": "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite",
    "score": 362.2,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "la-perspective-pourquoi-les-objets-disparaissent",
    "target": "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite",
    "score": 359.8,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "champ-visuel-central-peripherique",
    "target": "diminution-angulaire-taille-apparente",
    "score": 359.0,
    "strength": "strong",
    "sharedDomains": ["optique", "physique", "geometrie"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "ligo-londe-qui-nexistait-pas",
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
    "target": "magnetisme-et-electromagnetisme",
    "score": 352.7,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "source": "champ-visuel-central-peripherique",
    "target": "la-perspective-atmospherique",
    "score": 351.1,
    "strength": "strong",
    "sharedDomains": ["optique", "physique", "geometrie"]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "score": 348.5,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "hydrologie"]
  },
  {
    "source": "diminution-angulaire-taille-apparente",
    "target": "la-perspective-atmospherique",
    "score": 346.9,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "accommodation-oculaire",
    "target": "champ-visuel-central-peripherique",
    "score": 339.4,
    "strength": "strong",
    "sharedDomains": ["optique", "physique", "geometrie"]
  },
  {
    "source": "les-marees-contre-lheliocentrisme",
    "target": "magnetisme-et-electromagnetisme",
    "score": 338.5,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "cartographie"]
  },
  {
    "source": "la-perspective-pourquoi-les-objets-disparaissent",
    "target": "lhorizon-la-perspective-et-la-refraction",
    "score": 338.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "masse-et-volume",
    "target": "principe-action-reaction",
    "score": 336.0,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "la-rotation-terrestre-deux-experiences-zero-preuve",
    "target": "le-mouvement-zetetique-150-ans-de-resistance",
    "score": 335.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie", "histoire_sciences"]
  },
  {
    "source": "la-cosmologie-comme-instrument-de-domination",
    "target": "le-mouvement-zetetique-150-ans-de-resistance",
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
    "source": "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
    "target": "les-distances-cosmiques-au-dela-de-la-regle",
    "score": 334.1,
    "strength": "strong",
    "sharedDomains": ["astronomie", "epistemologie", "cosmologie"]
  },
  {
    "source": "pourquoi-les-choses-montent-et-descendent",
    "target": "principe-action-reaction",
    "score": 333.3,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "les-telescopes-et-la-courbure-terrestre",
    "target": "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite",
    "score": 332.6,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "densite-pourquoi-les-choses-montent-et-descendent",
    "target": "electricite-statique-attraction-repulsion",
    "score": 331.4,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "experiences-sous-pression-reduite",
    "target": "le-pole-sud-nexiste-pas",
    "score": 329.7,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "la-perspective-lineaire",
    "target": "les-telescopes-et-la-courbure-terrestre",
    "score": 329.5,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "lhorizon-la-perspective-et-la-refraction",
    "target": "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite",
    "score": 329.3,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie", "physique"]
  },
  {
    "source": "ethique-intellectuelle",
    "target": "la-cosmologie-comme-instrument-de-domination",
    "score": 329.1,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "index-thematique",
    "target": "la-rotation-terrestre-deux-experiences-zero-preuve",
    "score": 327.6,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
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
    "target": "experiences-sous-pression-reduite",
    "score": 325.8,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite", "modelisation"]
  },
  {
    "source": "accommodation-oculaire",
    "target": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "score": 325.7,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "electricite-statique-attraction-repulsion",
    "target": "le-pole-sud-nexiste-pas",
    "score": 325.6,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "chronologie-de-la-tromperie-du-globe",
    "target": "sources-historiques-fonds-documentaire",
    "score": 324.3,
    "strength": "strong",
    "sharedDomains": ["histoire_sciences", "epistemologie"]
  },
  {
    "source": "ethique-intellectuelle",
    "target": "glossaire",
    "score": 323.5,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences", "islam_sources"]
  },
  {
    "source": "les-trous-noirs-nexistent-pas",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 323.0,
    "strength": "strong",
    "sharedDomains": ["cosmologie", "physique"]
  },
  {
    "source": "persistance-retinienne",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 322.3,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "manifeste",
    "target": "pourquoi-tout-remettre-en-question",
    "score": 321.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "accommodation-oculaire",
    "target": "diminution-angulaire-taille-apparente",
    "score": 321.2,
    "strength": "strong",
    "sharedDomains": ["optique", "physique", "geometrie"]
  },
  {
    "source": "electricite-statique-attraction-repulsion",
    "target": "les-marees-contre-lheliocentrisme",
    "score": 320.9,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 320.2,
    "strength": "strong",
    "sharedDomains": ["cosmologie", "geometrie"]
  },
  {
    "source": "pression-lumiere-halos-rayons-et-ondes",
    "target": "vision-binoculaire-stereoscopie",
    "score": 319.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "manifeste",
    "target": "methodologie",
    "score": 318.1,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "levolution-et-lislam",
    "score": 317.1,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "ethique-intellectuelle",
    "target": "le-mouvement-zetetique-150-ans-de-resistance",
    "score": 317.0,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "le-pendule-de-foucault-une-preuve-contestee",
    "score": 316.7,
    "strength": "strong",
    "sharedDomains": ["physique", "epistemologie"]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "champ-visuel-central-peripherique",
    "score": 316.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "glossaire",
    "target": "la-rotation-terrestre-deux-experiences-zero-preuve",
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
    "source": "experiences-sous-pression-reduite",
    "target": "magnetisme-et-electromagnetisme",
    "score": 313.1,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
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
    "source": "glossaire",
    "target": "index-thematique",
    "score": 304.8,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "islam_sources"]
  },
  {
    "source": "experiences-sous-pression-reduite",
    "target": "les-marees-contre-lheliocentrisme",
    "score": 303.3,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "lhorizon-la-perspective-et-la-refraction",
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
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "la-perspective-atmospherique",
    "score": 303.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "glossaire",
    "target": "la-cosmologie-comme-instrument-de-domination",
    "score": 302.5,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "les-horloges-atomiques-ne-prouvent-rien",
    "score": 301.8,
    "strength": "strong",
    "sharedDomains": ["physique", "epistemologie"]
  },
  {
    "source": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "target": "la-perspective-atmospherique",
    "score": 301.4,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "debut-de-la-creation-selon-le-coran-et-la-sunna",
    "target": "le-concordisme",
    "score": 298.4,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "densite-pourquoi-les-choses-montent-et-descendent",
    "target": "magnetisme-et-electromagnetisme",
    "score": 298.0,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "champ-visuel-central-peripherique",
    "target": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "score": 296.3,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
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
    "source": "ethique-intellectuelle",
    "target": "index-thematique",
    "score": 292.7,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "islam_sources"]
  },
  {
    "source": "la-perspective-lineaire",
    "target": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "score": 292.2,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne",
    "target": "le-concordisme",
    "score": 290.4,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite",
    "score": 286.3,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "ethique-intellectuelle",
    "target": "la-rotation-terrestre-deux-experiences-zero-preuve",
    "score": 285.9,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "debut-de-la-creation-le-soleil-mobile-la-terre-immobile",
    "target": "levolution-et-lislam",
    "score": 282.9,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "cosmologie"]
  },
  {
    "source": "diminution-angulaire-taille-apparente",
    "target": "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas",
    "score": 281.4,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "electricite-statique-attraction-repulsion",
    "target": "magnetisme-et-electromagnetisme",
    "score": 280.0,
    "strength": "strong",
    "sharedDomains": ["physique", "gravite"]
  },
  {
    "source": "index-thematique",
    "target": "la-cosmologie-comme-instrument-de-domination",
    "score": 279.4,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "target": "diminution-angulaire-taille-apparente",
    "score": 277.7,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "les-distances-cosmiques-au-dela-de-la-regle",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 277.6,
    "strength": "strong",
    "sharedDomains": ["astronomie", "cosmologie"]
  },
  {
    "source": "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 277.2,
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
    "source": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "target": "les-telescopes-et-la-courbure-terrestre",
    "score": 276.4,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
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
    "target": "le-mouvement-zetetique-150-ans-de-resistance",
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
    "source": "glossaire",
    "target": "le-mouvement-zetetique-150-ans-de-resistance",
    "score": 273.4,
    "strength": "strong",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "la-perspective-pourquoi-les-objets-disparaissent",
    "target": "la-pression-atmospherique-un-ocean-d-air-invisible",
    "score": 270.5,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "le-concordisme",
    "target": "le-consensus-sur-la-sphericite",
    "score": 270.2,
    "strength": "strong",
    "sharedDomains": ["islam_sources", "epistemologie"]
  },
  {
    "source": "accommodation-oculaire",
    "target": "ce-quon-voit-quand-on-ne-devrait-plus-voir",
    "score": 270.0,
    "strength": "strong",
    "sharedDomains": ["optique", "geometrie"]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "masse-et-volume",
    "score": 148.7,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "le-pendule-de-foucault-une-preuve-contestee",
    "target": "principe-action-reaction",
    "score": 148.4,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "lespace-une-frontiere-infranchissable",
    "target": "vision-binoculaire-stereoscopie",
    "score": 144.1,
    "strength": "medium",
    "sharedDomains": ["geometrie", "physique"]
  },
  {
    "source": "le-pendule-de-foucault-une-preuve-contestee",
    "target": "masse-et-volume",
    "score": 142.9,
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
    "source": "methodologie",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 142.6,
    "strength": "medium",
    "sharedDomains": ["histoire_sciences", "cosmologie"]
  },
  {
    "source": "manifeste",
    "target": "pres-de-cent-savants-de-lislam",
    "score": 141.2,
    "strength": "medium",
    "sharedDomains": ["cosmologie", "islam_sources"]
  },
  {
    "source": "lhypothese-nulle-dynamique-et-cinematique",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 140.6,
    "strength": "medium",
    "sharedDomains": ["astronomie", "gravite"]
  },
  {
    "source": "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
    "target": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "score": 140.1,
    "strength": "medium",
    "sharedDomains": ["astronomie"]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "manifeste",
    "score": 139.7,
    "strength": "medium",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "chronologie-de-la-tromperie-du-globe",
    "target": "le-mythe-deratosthene",
    "score": 139.7,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "leau-ne-ment-pas",
    "target": "vision-binoculaire-stereoscopie",
    "score": 139.3,
    "strength": "medium",
    "sharedDomains": ["geometrie", "optique"]
  },
  {
    "source": "les-horloges-atomiques-ne-prouvent-rien",
    "target": "principe-action-reaction",
    "score": 139.2,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "le-mythe-deratosthene",
    "score": 138.6,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "geometrie"]
  },
  {
    "source": "ligo-londe-qui-nexistait-pas",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 138.0,
    "strength": "medium",
    "sharedDomains": ["gravite"]
  },
  {
    "source": "manifeste",
    "target": "mise-en-garde-la-kaaba-et-saturne",
    "score": 137.8,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "islam_sources"]
  },
  {
    "source": "leau-ne-ment-pas",
    "target": "persistance-retinienne",
    "score": 137.3,
    "strength": "medium",
    "sharedDomains": ["geometrie", "optique"]
  },
  {
    "source": "leau-ne-ment-pas",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 136.2,
    "strength": "medium",
    "sharedDomains": ["geometrie", "optique"]
  },
  {
    "source": "le-theodolite-celeste",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 135.9,
    "strength": "medium",
    "sharedDomains": ["astronomie", "modelisation"]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "principe-action-reaction",
    "score": 135.7,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "les-distances-cosmiques-au-dela-de-la-regle",
    "target": "les-trous-noirs-nexistent-pas",
    "score": 134.9,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "le-theodolite-celeste",
    "target": "pression-lumiere-halos-rayons-et-ondes",
    "score": 132.2,
    "strength": "medium",
    "sharedDomains": ["geometrie", "astronomie"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "les-trous-noirs-nexistent-pas",
    "score": 131.5,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "physique"]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "leau-ne-ment-pas",
    "score": 131.0,
    "strength": "medium",
    "sharedDomains": ["hydrologie", "geometrie"]
  },
  {
    "source": "les-trous-noirs-nexistent-pas",
    "target": "ligo-londe-qui-nexistait-pas",
    "score": 130.8,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "physique"]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "les-trous-noirs-nexistent-pas",
    "score": 130.7,
    "strength": "medium",
    "sharedDomains": ["cosmologie"]
  },
  {
    "source": "chronologie-de-la-tromperie-du-globe",
    "target": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "score": 129.7,
    "strength": "medium",
    "sharedDomains": ["histoire_sciences", "cosmologie"]
  },
  {
    "source": "les-horloges-atomiques-ne-prouvent-rien",
    "target": "masse-et-volume",
    "score": 129.3,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "lespace-une-frontiere-infranchissable",
    "target": "persistance-retinienne",
    "score": 129.1,
    "strength": "medium",
    "sharedDomains": ["geometrie", "physique"]
  },
  {
    "source": "etat-des-lieux-ou-en-sommes-nous",
    "target": "methodologie",
    "score": 129.0,
    "strength": "medium",
    "sharedDomains": ["epistemologie"]
  },
  {
    "source": "dune-terre-plate-universelle-a-la-sphere-grecque",
    "target": "methodologie",
    "score": 128.5,
    "strength": "medium",
    "sharedDomains": ["cosmologie", "histoire_sciences"]
  },
  {
    "source": "pourquoi-tout-remettre-en-question",
    "target": "sources-historiques-fonds-documentaire",
    "score": 128.3,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "histoire_sciences"]
  },
  {
    "source": "chronologie-de-la-tromperie-du-globe",
    "target": "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
    "score": 128.2,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "neptune-et-pluton-les-faux-triomphes",
    "score": 127.4,
    "strength": "medium",
    "sharedDomains": ["gravite"]
  },
  {
    "source": "les-horloges-atomiques-ne-prouvent-rien",
    "target": "pourquoi-les-choses-montent-et-descendent",
    "score": 127.4,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "le-theodolite-celeste",
    "score": 127.4,
    "strength": "medium",
    "sharedDomains": ["astronomie", "geometrie"]
  },
  {
    "source": "le-mythe-deratosthene",
    "target": "le-theodolite-celeste",
    "score": 127.1,
    "strength": "medium",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "chronologie-de-la-tromperie-du-globe",
    "target": "les-distances-cosmiques-au-dela-de-la-regle",
    "score": 127.0,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 123.4,
    "strength": "medium",
    "sharedDomains": ["astronomie"]
  },
  {
    "source": "kings-dethroned-leffondrement-de-la-triangulation-stellaire",
    "target": "le-mythe-deratosthene",
    "score": 123.1,
    "strength": "medium",
    "sharedDomains": ["epistemologie", "cosmologie"]
  },
  {
    "source": "200-ans-de-resultats-nuls-darago-a-einstein",
    "target": "pourquoi-les-choses-montent-et-descendent",
    "score": 121.2,
    "strength": "medium",
    "sharedDomains": ["physique"]
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
    "source": "le-pendule-de-foucault-une-preuve-contestee",
    "target": "pourquoi-les-choses-montent-et-descendent",
    "score": 114.2,
    "strength": "medium",
    "sharedDomains": ["physique"]
  },
  {
    "source": "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre",
    "target": "les-distances-cosmiques-au-dela-de-la-regle",
    "score": 111.2,
    "strength": "medium",
    "sharedDomains": ["astronomie"]
  },
  {
    "source": "cartes-routes-boussoles-et-le-mystere-antarctique",
    "target": "le-theodolite-celeste",
    "score": 47.8,
    "strength": "weak",
    "sharedDomains": ["geometrie"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "lhypothese-nulle-dynamique-et-cinematique",
    "score": 44.1,
    "strength": "weak",
    "sharedDomains": ["gravite"]
  },
  {
    "source": "la-gravite-70-theories-et-aucune-preuve",
    "target": "lespace-une-frontiere-infranchissable",
    "score": 41.8,
    "strength": "weak",
    "sharedDomains": ["physique"]
  },
];

export const NEXUS_STATS = {
  "totalArticles": 63,
  "totalLinks": 152,
  "pillars": {
    "headquarters": 16,
    "observatory": 31,
    "library": 10,
    "meta": 6,
  },
  "domainCoverage": 11
};
