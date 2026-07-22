/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  images: {
    unoptimized: true,
  },
  async redirects() {
    return [
      // Canonicalisation de l'hôte : www → apex (évite le contenu dupliqué www/non-www)
      {
        source: '/:path*',
        has: [{ type: 'host', value: 'www.terre-etendue-islam.fr' }],
        destination: 'https://terre-etendue-islam.fr/:path*',
        permanent: true,
      },
      // Anciennes URLs (migration WordPress/Elementor → Next) vers les pages actuelles
      { source: '/lobservatoire', destination: '/observatory', permanent: true },
      {
        source: '/comment-a-debute-la-creation',
        destination: '/article/debut-de-la-creation-selon-le-coran-et-la-sunna',
        permanent: true,
      },
      {
        source: '/lhorizon-la-perspective-et-la-refraction-ce-que-loptique-explique-vraiment',
        destination: '/article/lhorizon-la-perspective-et-la-refraction',
        permanent: true,
      },
    ];
  },
};

module.exports = nextConfig;
