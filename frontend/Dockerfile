FROM node:18-alpine AS builder

WORKDIR /app

# Copier package.json et lock file depuis le dossier frontend
COPY frontend/package*.json ./

# Installer les dépendances
RUN npm ci

# Copier le code source du frontend
COPY frontend/ .

# Build Next.js
RUN npm run build

# Stage 2 : Runtime
FROM node:18-alpine

WORKDIR /app

ENV NODE_ENV=production
ENV PORT=3000

# Copier uniquement les fichiers nécessaires depuis builder
COPY --from=builder /app/node_modules ./node_modules
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

EXPOSE 3000

CMD ["npm", "start"]
