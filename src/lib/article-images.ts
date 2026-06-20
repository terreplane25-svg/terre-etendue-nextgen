// ═══════════════════════════════════════════
// ARTICLE THUMBNAIL IMAGES
// Unsplash (free) + Hostinger assets
// ═══════════════════════════════════════════

const HOSTINGER = "https://green-gnat-134443.hostingersite.com/wp-content/uploads";
const UNSPLASH = "https://images.unsplash.com";

const IMG: Record<string, string> = {
  // ── Observatory: Analysis ──
  "lhorizon-la-perspective-et-la-refraction": `${HOSTINGER}/2026/06/refraction.png`,
  // merged into la-perspective-pourquoi-les-objets-disparaissent
  "leau-ne-ment-pas": `${HOSTINGER}/2026/05/ea.png`,
  "les-horloges-atomiques-ne-prouvent-rien": `${HOSTINGER}/2026/06/48371867_2205216006163858_1771726137618071552_n.jpg`,
  "pression-lumiere-halos-rayons-et-ondes": `${UNSPLASH}/photo-1534088568595-a066f410bcda?w=600&h=400&fit=crop`,
  "les-marees-contre-lheliocentrisme": `${HOSTINGER}/2026/06/maree.jpg`,
  // merged into la-perspective-pourquoi-les-objets-disparaissent
  "lespace-une-frontiere-infranchissable": `${HOSTINGER}/2026/06/frontiere_atmosphere_espace.jpg`,
  "cartes-routes-boussoles-et-le-mystere-antarctique": `${HOSTINGER}/2026/04/boussole.png`,
  "la-lune-six-anomalies-que-le-modele-standard-ne-resout-pas": `${UNSPLASH}/photo-1522030299830-16b8d3d049fe?w=600&h=400&fit=crop`,
  "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre": `${UNSPLASH}/photo-1419242902214-272b3f66ee7a?w=600&h=400&fit=crop`,
  "le-pole-sud-nexiste-pas": `${UNSPLASH}/photo-1489549132488-d00b7eee80f1?w=600&h=400&fit=crop`,
  "le-theodolite-celeste": `${UNSPLASH}/photo-1507400492013-162706c8c05e?w=600&h=400&fit=crop`,

  // ── Experiments ──
  "densite-pourquoi-les-choses-montent-et-descendent": `${UNSPLASH}/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop`,
  "la-pression-atmospherique-un-ocean-d-air-invisible": `${UNSPLASH}/photo-1534088568595-a066f410bcda?w=600&h=400&fit=crop`,
  "experiences-sous-pression-reduite": `${UNSPLASH}/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop`,
  "la-perspective-lineaire": `${UNSPLASH}/photo-1473654729523-203e25dfda10?w=600&h=400&fit=crop`,
  // merged into la-perspective-pourquoi-les-objets-disparaissent
  "la-perspective-atmospherique": `${UNSPLASH}/photo-1470071459604-3b5ec3a7fe05?w=600&h=400&fit=crop`,
  "loeil-humain-la-machine-a-voir-qui-faconne-notre-realite": `${UNSPLASH}/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop`,
  "principe-action-reaction": `${UNSPLASH}/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop`,
  "magnetisme-et-electromagnetisme": `${UNSPLASH}/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop`,
  "electricite-statique-attraction-repulsion": `${UNSPLASH}/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop`,

  // ── Library (Islamic) ──
  "debut-de-la-creation-selon-le-coran-et-la-sunna": `${HOSTINGER}/2026/06/mer_horizon.png`,
  "debut-de-la-creation-le-soleil-mobile-la-terre-immobile": `${HOSTINGER}/2026/04/cosmologie-fonde-sur-textes.png`,
  "la-terre-dans-le-coran": `${UNSPLASH}/photo-1542816417-0983c9c7ad53?w=600&h=400&fit=crop`,
  "pres-de-cent-savants-de-lislam": `${UNSPLASH}/photo-1585036156171-384164a8c159?w=600&h=400&fit=crop`,
  "dhu-al-qarnayn-confins-terrestres-et-rupture-ptolemeenne": `${UNSPLASH}/photo-1564769625905-50e93615e769?w=600&h=400&fit=crop`,
  "la-qibla-et-la-direction-cote-ouest": `${UNSPLASH}/photo-1591604129939-f1efa4d9f7fa?w=600&h=400&fit=crop`,
  "levolution-et-lislam": `${UNSPLASH}/photo-1530026405186-ed1f139313f8?w=600&h=400&fit=crop`,
  "mise-en-garde-la-kaaba-et-saturne": `${UNSPLASH}/photo-1564769625905-50e93615e769?w=600&h=400&fit=crop`,
  "le-consensus-sur-la-sphericite": `${UNSPLASH}/photo-1504711434969-e33886168d9c?w=600&h=400&fit=crop`,
  "sources-historiques-fonds-documentaire": `${UNSPLASH}/photo-1524995997946-a1c2e315a42f?w=600&h=400&fit=crop`,

  // ── Headquarters ──
  "la-gravite-70-theories-et-aucune-preuve": `${UNSPLASH}/photo-1446776811953-b23d57bd21aa?w=600&h=400&fit=crop`,
  "200-ans-de-resultats-nuls-darago-a-einstein": `${UNSPLASH}/photo-1507413245164-6160d8298b31?w=600&h=400&fit=crop`,
  "chronologie-de-la-tromperie-du-globe": `${HOSTINGER}/2025/09/science_logo.png`,
  "dune-terre-plate-universelle-a-la-sphere-grecque": `${UNSPLASH}/photo-1569003339405-ea396a5a8a90?w=600&h=400&fit=crop`,
  "kings-dethroned-leffondrement-de-la-triangulation-stellaire": `${UNSPLASH}/photo-1419242902214-272b3f66ee7a?w=600&h=400&fit=crop`,
  "la-cosmologie-comme-instrument-de-domination": `${UNSPLASH}/photo-1504711434969-e33886168d9c?w=600&h=400&fit=crop`,
  "la-rotation-terrestre-deux-experiences-zero-preuve": `${HOSTINGER}/2026/06/pantheon_pendule_de_foucault1.jpg`,
  "le-concordisme": `${UNSPLASH}/photo-1530026405186-ed1f139313f8?w=600&h=400&fit=crop`,
  "le-mouvement-zetetique-150-ans-de-resistance": `${UNSPLASH}/photo-1504711434969-e33886168d9c?w=600&h=400&fit=crop`,
  "le-mythe-deratosthene": `${UNSPLASH}/photo-1569003339405-ea396a5a8a90?w=600&h=400&fit=crop`,
  "les-distances-cosmiques-au-dela-de-la-regle": `${UNSPLASH}/photo-1462332420958-a05d1e002413?w=600&h=400&fit=crop`,
  "les-trous-noirs-nexistent-pas": `${HOSTINGER}/2026/06/Black_Holes_-_Monsters_in_Space-scaled.jpg`,
  "lhypothese-nulle-dynamique-et-cinematique": `${UNSPLASH}/photo-1507413245164-6160d8298b31?w=600&h=400&fit=crop`,
  "ligo-londe-qui-nexistait-pas": `${UNSPLASH}/photo-1462332420958-a05d1e002413?w=600&h=400&fit=crop`,
  "neptune-et-pluton-les-faux-triomphes": `${UNSPLASH}/photo-1614732414444-096e5f1122d5?w=600&h=400&fit=crop`,
  "pourquoi-tout-remettre-en-question": `${UNSPLASH}/photo-1457364887197-9150188c107b?w=600&h=400&fit=crop`,

  // ── Observatory extra ──
  "vols-avion-et-courbure-terrestre": `${HOSTINGER}/2026/06/Six_flight_instruments.jpg`,
  "la-perspective-pourquoi-les-objets-disparaissent": `${UNSPLASH}/photo-1473654729523-203e25dfda10?w=600&h=400&fit=crop`,

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
