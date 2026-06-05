// ═══════════════════════════════════════════
// ARTICLE THUMBNAIL IMAGES
// Unsplash (free) + Hostinger assets
// ═══════════════════════════════════════════

const IMG: Record<string, string> = {
  // ── Observatory: Analysis ──
  "lhorizon-la-perspective-et-la-refraction": "https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/04/horizon.jpg",
  "ce-quon-voit-quand-on-ne-devrait-plus-voir": "https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/06/structure_cache_1.jpg",
  "leau-ne-ment-pas": "https://green-gnat-134443.hostingersite.com/wp-content/uploads/2026/05/ea.png",
  "le-pendule-de-foucault-une-preuve-contestee": "https://images.unsplash.com/photo-1635070041078-e363dbe005cb?w=600&h=400&fit=crop",
  "les-horloges-atomiques-ne-prouvent-rien": "https://images.unsplash.com/photo-1509048191080-d2984bad6ae5?w=600&h=400&fit=crop",
  "pourquoi-les-choses-montent-et-descendent": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop",
  "pression-lumiere-halos-rayons-et-ondes": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=600&h=400&fit=crop",
  "les-marees-contre-lheliocentrisme": "https://images.unsplash.com/photo-1505142468610-359e7d316be0?w=600&h=400&fit=crop",
  "les-telescopes-et-la-courbure-terrestre": "https://images.unsplash.com/photo-1516339901601-2e1b62dc0c45?w=600&h=400&fit=crop",
  "lespace-une-frontiere-infranchissable": "https://images.unsplash.com/photo-1446776811953-b23d57bd21aa?w=600&h=400&fit=crop",
  "cartes-routes-boussoles-et-le-mystere-antarctique": "https://images.unsplash.com/photo-1524661135-423995f22d0b?w=600&h=400&fit=crop",
  "la-lune-fonction-et-anomalies": "https://images.unsplash.com/photo-1522030299830-16b8d3d049fe?w=600&h=400&fit=crop",
  "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre": "https://images.unsplash.com/photo-1419242902214-272b3f66ee7a?w=600&h=400&fit=crop",
  "le-pole-sud-nexiste-pas": "https://images.unsplash.com/photo-1489549132488-d00b7eee80f1?w=600&h=400&fit=crop",
  "le-theodolite-celeste": "https://images.unsplash.com/photo-1507400492013-162706c8c05e?w=600&h=400&fit=crop",

  // ── Experiments ──
  "densite-et-flottabilite": "https://images.unsplash.com/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop",
  "la-pression-atmospherique": "https://images.unsplash.com/photo-1534088568595-a066f410bcda?w=600&h=400&fit=crop",
  "masse-et-volume": "https://images.unsplash.com/photo-1532094349884-543bc11b234d?w=600&h=400&fit=crop",
  "experiences-sous-pression-reduite": "https://images.unsplash.com/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop",
  "la-perspective-lineaire": "https://images.unsplash.com/photo-1473654729523-203e25dfda10?w=600&h=400&fit=crop",
  "diminution-angulaire-taille-apparente": "https://images.unsplash.com/photo-1500534314209-a25ddb2bd429?w=600&h=400&fit=crop",
  "la-perspective-atmospherique": "https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=600&h=400&fit=crop",
  "champ-visuel-central-peripherique": "https://images.unsplash.com/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop",
  "vision-binoculaire-stereoscopie": "https://images.unsplash.com/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop",
  "accommodation-oculaire": "https://images.unsplash.com/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop",
  "persistance-retinienne": "https://images.unsplash.com/photo-1550684848-fac1c5b4e853?w=600&h=400&fit=crop",
  "principe-action-reaction": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop",
  "magnetisme-et-electromagnetisme": "https://images.unsplash.com/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop",
  "electricite-statique-attraction-repulsion": "https://images.unsplash.com/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop",

  // ── Library ──
  "debut-de-la-creation-selon-le-coran-et-la-sunna": "https://images.unsplash.com/photo-1585829365295-ab7cd400c167?w=600&h=400&fit=crop",
  "debut-de-la-creation-le-soleil-mobile-la-terre-immobile": "https://images.unsplash.com/photo-1504052434569-70ad5836ab65?w=600&h=400&fit=crop",
};

const FALLBACK = "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop";

export function getArticleImage(slug: string): string {
  return IMG[slug] || FALLBACK;
}
