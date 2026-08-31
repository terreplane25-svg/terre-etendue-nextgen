/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  // Redirections des articles fusionnés. Une adresse publiée ne se supprime
  // pas : elle circule dans des liens, des favoris et des index de moteurs de
  // recherche qu'on ne contrôle pas. Chaque fusion ajoute ici sa ligne.
  async redirects() {
    return [
      // « manifeste », « éthique intellectuelle » et « méthodologie »
      // → « Standards et méthode »
      { source: '/article/manifeste', destination: '/article/standards-et-methode', permanent: true },
      { source: '/article/ethique-intellectuelle', destination: '/article/standards-et-methode', permanent: true },
      { source: '/article/methodologie', destination: '/article/standards-et-methode', permanent: true },
      // Les trois articles sur la perspective → le dossier unique. Les deux
      // courts ne portaient plus, en propre, que leurs deux protocoles et
      // leurs sources : les uns et les autres sont passés dans le dossier.
      { source: '/article/la-perspective-lineaire', destination: '/article/la-perspective-pourquoi-les-objets-disparaissent', permanent: true },
      { source: '/article/la-perspective-atmospherique', destination: '/article/la-perspective-pourquoi-les-objets-disparaissent', permanent: true },
      { source: '/article/lhorizon-la-perspective-et-la-refraction', destination: '/article/la-perspective-pourquoi-les-objets-disparaissent', permanent: true },
      // Les trois explications courtes sur les forces → la page de socle.
      { source: '/article/electricite-statique-attraction-repulsion', destination: '/article/les-forces-invisibles-a-faire-chez-soi', permanent: true },
      { source: '/article/magnetisme-et-electromagnetisme', destination: '/article/les-forces-invisibles-a-faire-chez-soi', permanent: true },
      { source: '/article/principe-action-reaction', destination: '/article/les-forces-invisibles-a-faire-chez-soi', permanent: true },
      { source: '/article/experiences-sous-pression-reduite', destination: '/article/la-pression-atmospherique-un-ocean-d-air-invisible', permanent: true },
      { source: '/article/lhypothese-nulle-dynamique-et-cinematique', destination: '/article/la-gravite-70-theories-et-aucune-preuve', permanent: true },
      { source: '/article/kings-dethroned-leffondrement-de-la-triangulation-stellaire', destination: '/article/les-distances-cosmiques-au-dela-de-la-regle', permanent: true },
      { source: '/article/ligo-londe-qui-nexistait-pas', destination: '/article/les-trous-noirs-existent-ils', permanent: true },
      // Adresses alignées sur les titres : l'adresse est ce qui s'affiche
      // quand un article est partagé, et elle disait encore ce que le titre
      // avait cessé de dire.
      { source: '/article/200-ans-de-resultats-nuls-darago-a-einstein', destination: '/article/lenigme-de-la-terre-immobile', permanent: true },
      { source: '/article/la-rotation-terrestre-deux-experiences-zero-preuve', destination: '/article/la-rotation-terrestre-experiences-preuves-verdict', permanent: true },
      { source: '/article/le-mouvement-zetetique-150-ans-de-resistance', destination: '/article/lexperience-contre-la-theorie', permanent: true },
      { source: '/article/le-theodolite-celeste', destination: '/article/mesures-sous-le-ciel-trigonometrie-plane', permanent: true },
      { source: '/article/loeil-humain-la-machine-a-voir-qui-faconne-notre-realite', destination: '/article/loeil-humain-la-machine-a-voir', permanent: true },
      { source: '/article/chronologie-de-la-tromperie-du-globe', destination: '/article/chronologie-critique-du-modele-globe', permanent: true },
      { source: '/article/les-trous-noirs-nexistent-pas', destination: '/article/les-trous-noirs-existent-ils', permanent: true },
      // La page des campagnes finançables est retirée : elle chiffrait chaque
      // expérience et proposait des paliers de contreparties, ce que la page
      // de soutien exclut désormais explicitement. Son adresse répondait
      // encore, hors navigation ; elle mène là où la question est tranchée.
      { source: '/projets', destination: '/article/financement-et-independance', permanent: true },
    ];
  },
};

module.exports = nextConfig;
