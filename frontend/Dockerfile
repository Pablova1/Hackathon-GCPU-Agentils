# Stage 1: Dependencies
FROM node:18-alpine AS deps

WORKDIR /app

# Copier les fichiers de dépendances
COPY frontend/package*.json ./

# Installer les dépendances de production uniquement
RUN npm ci --only=production && \
    cp -R node_modules /tmp/node_modules && \
    npm ci

# Stage 2: Builder
FROM node:18-alpine AS builder

WORKDIR /app

# Argument de build pour l'URL de l'API
ARG NEXT_PUBLIC_API_URL
ENV NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL

# Copier les dépendances depuis deps
COPY --from=deps /app/node_modules ./node_modules
COPY frontend/ .

# Build Next.js avec optimisations
ENV NEXT_TELEMETRY_DISABLED=1
RUN echo "Building with NEXT_PUBLIC_API_URL=$NEXT_PUBLIC_API_URL" && npm run build

# Stage 3: Runtime
FROM node:18-alpine AS runner

WORKDIR /app

# Créer un utilisateur non-root
RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Variables d'environnement pour production
ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=8080

# Copier uniquement les fichiers nécessaires pour la production
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json

# Copier les fichiers Next.js buildés
COPY --from=builder --chown=nextjs:nodejs /app/.next/standalone ./
COPY --from=builder --chown=nextjs:nodejs /app/.next/static ./.next/static

# Basculer vers l'utilisateur non-root
USER nextjs

# Exposer le port (Cloud Run utilisera $PORT)
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD node -e "require('http').get('http://localhost:' + process.env.PORT, (r) => {process.exit(r.statusCode === 200 ? 0 : 1)})"

# Démarrage optimisé pour Cloud Run
CMD node server.js
