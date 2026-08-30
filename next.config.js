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
    ];
  },
};

module.exports = nextConfig;
