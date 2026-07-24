// ═══════════════════════════════════════════
// ARTICLE THUMBNAIL IMAGES
// Unsplash (free) + Hostinger assets
// ═══════════════════════════════════════════

const HOSTINGER = "https://green-gnat-134443.hostingersite.com/wp-content/uploads";
const UNSPLASH = "https://images.unsplash.com";

const IMG: Record<string, string> = {
  // ── Observatory: Analysis ──
  "lhorizon-la-perspective-et-la-refraction": `${HOSTINGER}/2026/07/persperctive_horizon-e1784751826124.png`,
  // merged into la-perspective-pourquoi-les-objets-disparaissent
  "leau-ne-ment-pas": `${HOSTINGER}/2026/06/mer_horizon-e1784751872495.png`,
  // les-horloges-atomiques-ne-prouvent-rien: merged into la-rotation-terrestre
  "pression-lumiere-halos-rayons-et-ondes": `${HOSTINGER}/2026/07/StockCake-Horizon_de_Lever_de_Soleil_Ethere-297875-standard.jpg`,
  "les-marees-contre-lheliocentrisme": `${HOSTINGER}/2026/07/maree.png`,
  // merged into la-perspective-pourquoi-les-objets-disparaissent
  "lespace-une-frontiere-infranchissable": `${HOSTINGER}/2026/06/frontiere_atmosphere_espace.jpg`,
  "cartes-routes-boussoles-et-le-mystere-antarctique": `${HOSTINGER}/2026/07/carte_boussole_2-e1784751599837.png`,
  "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas": `${UNSPLASH}/photo-1522030299830-16b8d3d049fe?w=600&h=400&fit=crop`,
  "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre": `${HOSTINGER}/2026/07/lune_soleil_etoile.png`,
  "le-pole-sud-nexiste-pas": `${HOSTINGER}/2026/07/pole_sud.png`,
  "le-theodolite-celeste": `${HOSTINGER}/2026/07/teodolite.png`,

  // ── Experiments ──
  "densite-pourquoi-les-choses-montent-et-descendent": `${HOSTINGER}/2026/06/ChatGPT-Image-21-juin-2026-00_39_16.png`,
  "la-pression-atmospherique-un-ocean-d-air-invisible": `${HOSTINGER}/2026/07/pression_atmos.png`,
  "experiences-sous-pression-reduite": `${HOSTINGER}/2026/07/chambre_a_vide.png`,
  "la-perspective-lineaire": `${UNSPLASH}/photo-1473654729523-203e25dfda10?w=600&h=400&fit=crop`,
  // merged into la-perspective-pourquoi-les-objets-disparaissent
  "la-perspective-atmospherique": `${UNSPLASH}/photo-1470071459604-3b5ec3a7fe05?w=600&h=400&fit=crop`,
  "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite": `${UNSPLASH}/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop`,
  "principe-action-reaction": `${UNSPLASH}/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop`,
  "magnetisme-et-electromagnetisme": `${UNSPLASH}/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop`,
  "electricite-statique-attraction-repulsion": `${UNSPLASH}/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop`,

  // ── Library (Islamic) ──
  "debut-de-la-creation-selon-le-coran-et-la-sunna": `${HOSTINGER}/2026/06/mer_horizon.png`,
  "debut-de-la-creation-le-soleil-mobile-la-terre-immobile": `${HOSTINGER}/2026/04/cosmologie-fonde-sur-textes-e1784752034269.png`,
  "la-terre-dans-le-coran": `${HOSTINGER}/2026/05/7_mots.jpg`,
  "pres-de-cent-savants-de-lislam": `${HOSTINGER}/2025/10/indra-projects-E4wh3Z4X4eU-unsplash-scaled-e1784883783988.jpg`,
  "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne": `${UNSPLASH}/photo-1564769625905-50e93615e769?w=600&h=400&fit=crop`,
  "la-qibla-et-la-direction-cote-ouest": `${UNSPLASH}/photo-1591604129939-f1efa4d9f7fa?w=600&h=400&fit=crop`,
  "levolution-et-lislam": `${UNSPLASH}/photo-1530026405186-ed1f139313f8?w=600&h=400&fit=crop`,
  "mise-en-garde-la-kaaba-et-saturne": `${UNSPLASH}/photo-1564769625905-50e93615e769?w=600&h=400&fit=crop`,
  "le-consensus-sur-la-sphericite": `${HOSTINGER}/2025/10/Ibn_Taymiyyah.jpg`,
  "sources-historiques-fonds-documentaire": `${UNSPLASH}/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop`,

  // ── Headquarters ──
  "la-gravite-70-theories-et-aucune-preuve": `${HOSTINGER}/2026/07/gravity_theorie.png`,
  "200-ans-de-resultats-nuls-darago-a-einstein": `${HOSTINGER}/2025/10/Solar_sys.jpg`,
  "chronologie-de-la-tromperie-du-globe": `${HOSTINGER}/2026/07/chronologie_de_tro-e1784751688322.png`,
  "dune-terre-plate-universelle-a-la-sphere-grecque": `${HOSTINGER}/2025/09/photo_2025-09-29_04-34-50-1.jpg`,
  "kings-dethroned-leffondrement-de-la-triangulation-stellaire": `${UNSPLASH}/photo-1419242902214-272b3f66ee7a?w=600&h=400&fit=crop`,
  "la-cosmologie-comme-instrument-de-domination": `${HOSTINGER}/2026/07/cosmoligie.png`,
  "la-rotation-terrestre-deux-experiences-zero-preuve": `${HOSTINGER}/2026/06/pantheon_pendule_de_foucault1.jpg`,
  "le-concordisme": `${HOSTINGER}/2026/07/concordiste.png`,
  "le-mouvement-zetetique-150-ans-de-resistance": `${HOSTINGER}/2026/07/resistance.png`,
  "le-mythe-deratosthene": `${HOSTINGER}/2026/07/myth_herato.jpg`,
  "lire-le-ciel-avant-le-globe": `${HOSTINGER}/2026/05/observatoire-scaled.jpeg`,
  "les-distances-cosmiques-au-dela-de-la-regle": `${HOSTINGER}/2026/04/mesure-soleil.jpg`,
  "les-trous-noirs-nexistent-pas": `${HOSTINGER}/2026/06/Black_Holes_-_Monsters_in_Space-scaled.jpg`,
  "lhypothese-nulle-dynamique-et-cinematique": `${UNSPLASH}/photo-1507413245164-6160d8298b31?w=600&h=400&fit=crop`,
  "ligo-londe-qui-nexistait-pas": `${UNSPLASH}/photo-1462332420958-a05d1e002413?w=600&h=400&fit=crop`,
  "neptune-et-pluton-les-faux-triomphes": `${HOSTINGER}/2026/04/pluto_neptune.jpeg`,
  "pourquoi-tout-remettre-en-question": `${HOSTINGER}/2026/04/interrogation.avif`,

  // ── Observatory extra ──
  "vols-avion-et-courbure-terrestre": `${HOSTINGER}/2026/06/Six_flight_instruments.jpg`,
  "la-perspective-pourquoi-les-objets-disparaissent": `${HOSTINGER}/2026/07/perspective.png`,

  // ── Meta ──
  "manifeste": `${UNSPLASH}/photo-1457364887197-9150188c107b?w=600&h=400&fit=crop`,
  "methodologie": `${UNSPLASH}/photo-1507413245164-6160d8298b31?w=600&h=400&fit=crop`,
  "ethique-intellectuelle": `${UNSPLASH}/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop`,
  "etat-des-lieux-ou-en-sommes-nous": `${UNSPLASH}/photo-1504711434969-e33886168d9c?w=600&h=400&fit=crop`,
  "glossaire": `${UNSPLASH}/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop`,
  "index-thematique": `${UNSPLASH}/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop`,
};

const FALLBACK = `${UNSPLASH}/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop`;

export function getArticleImage(slug: string): string {
  return IMG[slug] || FALLBACK;
}

// Version optimisée pour le partage social (Open Graph / Twitter Cards).
// Agrandit les vignettes Unsplash 600×400 vers ~1200×630 (grande carte).
export function getArticleOgImage(slug: string): string {
  const img = getArticleImage(slug);
  if (img.includes('images.unsplash.com')) {
    return img.replace(/w=\d+/, 'w=1200').replace(/h=\d+/, 'h=630');
  }
  return img;
}
