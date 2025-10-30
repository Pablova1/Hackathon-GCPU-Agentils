/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  
  // Optimisations de production
  compiler: {
    removeConsole: process.env.NODE_ENV === 'production',
  },
  
  // Optimiser les chunks pour réduire le temps de chargement
  webpack: (config, { dev, isServer }) => {
    // Optimiser la taille des chunks
    if (!dev && !isServer) {
      config.optimization = {
        ...config.optimization,
        splitChunks: {
          chunks: 'all',
          cacheGroups: {
            default: false,
            vendors: false,
            // Vendor chunk pour les dépendances node_modules
            vendor: {
              name: 'vendor',
              chunks: 'all',
              test: /node_modules/,
              priority: 20,
            },
            // Chunk commun pour le code partagé
            common: {
              name: 'common',
              minChunks: 2,
              chunks: 'all',
              priority: 10,
              reuseExistingChunk: true,
              enforce: true,
            },
          },
        },
      };
    }
    return config;
  },
  
  // Désactiver la génération de source maps en production pour accélérer
  productionBrowserSourceMaps: false,
  
  // Configuration des images
  images: {
    domains: ['localhost'],
    unoptimized: true,
  },
  
  // Optimiser le output
  output: 'standalone',
};

module.exports = nextConfig;
