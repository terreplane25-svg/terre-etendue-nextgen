/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  // Les trois pages « manifeste », « éthique intellectuelle » et « méthodologie »
  // ont été fusionnées en une seule : « Standards et méthode ». On redirige pour
  // ne pas casser les liens entrants.
  async redirects() {
    return [
      { source: '/article/manifeste', destination: '/article/standards-et-methode', permanent: true },
      { source: '/article/ethique-intellectuelle', destination: '/article/standards-et-methode', permanent: true },
      { source: '/article/methodologie', destination: '/article/standards-et-methode', permanent: true },
    ];
  },
};

module.exports = nextConfig;
