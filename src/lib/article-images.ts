// ═══════════════════════════════════════════
// ARTICLE THUMBNAIL IMAGES
// Unsplash (free) + Hostinger assets
// ═══════════════════════════════════════════

const HOSTINGER = "https://green-gnat-134443.hostingersite.com/wp-content/uploads";
const UNSPLASH = "https://images.unsplash.com";

const IMG: Record<string, string> = {
  // ── Observatory: Analysis ──
  "lhorizon-la-perspective-et-la-refraction": `${HOSTINGER}/2026/06/refraction.png`,
  "ce-quon-voit-quand-on-ne-devrait-plus-voir": `${HOSTINGER}/2026/06/3b-scaled.jpg`,
  "leau-ne-ment-pas": `${HOSTINGER}/2026/05/ea.png`,
  "le-pendule-de-foucault-une-preuve-contestee": `${HOSTINGER}/2026/06/pantheon_pendule_de_foucault1.jpg`,
  "les-horloges-atomiques-ne-prouvent-rien": `${HOSTINGER}/2026/06/48371867_2205216006163858_1771726137618071552_n.jpg`,
  "pourquoi-les-choses-montent-et-descendent": `${HOSTINGER}/2026/06/mongolfier_pomme.png`,
  "pression-lumiere-halos-rayons-et-ondes": `${UNSPLASH}/photo-1534088568595-a066f410bcda?w=600&h=400&fit=crop`,
  "les-marees-contre-lheliocentrisme": `${HOSTINGER}/2026/06/maree.jpg`,
  "les-telescopes-et-la-courbure-terrestre": `${HOSTINGER}/2026/06/Y4koCE7VcDdtZKbRf3b9Q8.jpg`,
  "lespace-une-frontiere-infranchissable": `${HOSTINGER}/2026/06/frontiere_atmosphere_espace.jpg`,
  "cartes-routes-boussoles-et-le-mystere-antarctique": `${HOSTINGER}/2026/04/boussole.png`,
  "la-lune-fonction-et-anomalies": `${UNSPLASH}/photo-1522030299830-16b8d3d049fe?w=600&h=400&fit=crop`,
  "la-lune-le-soleil-et-les-etoiles-ce-que-le-ciel-nous-montre": `${UNSPLASH}/photo-1419242902214-272b3f66ee7a?w=600&h=400&fit=crop`,
  "le-pole-sud-nexiste-pas": `${UNSPLASH}/photo-1489549132488-d00b7eee80f1?w=600&h=400&fit=crop`,
  "le-theodolite-celeste": `${UNSPLASH}/photo-1507400492013-162706c8c05e?w=600&h=400&fit=crop`,

  // ── Experiments ──
  "densite-et-flottabilite": `${UNSPLASH}/photo-1558618666-fcd25c85f82e?w=600&h=400&fit=crop`,
  "la-pression-atmospherique": `${UNSPLASH}/photo-1534088568595-a066f410bcda?w=600&h=400&fit=crop`,
  "masse-et-volume": `${UNSPLASH}/photo-1532094349884-543bc11b234d?w=600&h=400&fit=crop`,
  "experiences-sous-pression-reduite": `${UNSPLASH}/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop`,
  "la-perspective-lineaire": `${UNSPLASH}/photo-1473654729523-203e25dfda10?w=600&h=400&fit=crop`,
  "diminution-angulaire-taille-apparente": `${UNSPLASH}/photo-1500534314209-a25ddb2bd429?w=600&h=400&fit=crop`,
  "la-perspective-atmospherique": `${UNSPLASH}/photo-1470071459604-3b5ec3a7fe05?w=600&h=400&fit=crop`,
  "champ-visuel-central-peripherique": `${UNSPLASH}/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop`,
  "vision-binoculaire-stereoscopie": `${UNSPLASH}/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop`,
  "accommodation-oculaire": `${UNSPLASH}/photo-1494869042583-f6c911f04b4c?w=600&h=400&fit=crop`,
  "persistance-retinienne": `${UNSPLASH}/photo-1550684848-fac1c5b4e853?w=600&h=400&fit=crop`,
  "principe-action-reaction": `${UNSPLASH}/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop`,
  "magnetisme-et-electromagnetisme": `${UNSPLASH}/photo-1567427018141-0584cfcbf1b8?w=600&h=400&fit=crop`,
  "electricite-statique-attraction-repulsion": `${UNSPLASH}/photo-1461749280684-dccba630e2f6?w=600&h=400&fit=crop`,

  // ── Library ──
  "debut-de-la-creation-selon-le-coran-et-la-sunna": `${HOSTINGER}/2026/06/mer_horizon.png`,
  "debut-de-la-creation-le-soleil-mobile-la-terre-immobile": `${HOSTINGER}/2026/04/cosmologie-fonde-sur-textes.png`,
};

const FALLBACK = `${UNSPLASH}/photo-1451187580459-43490279c0fa?w=600&h=400&fit=crop`;

export function getArticleImage(slug: string): string {
  return IMG[slug] || FALLBACK;
}
