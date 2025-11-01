# Stage 1: Builder
FROM python:3.11-slim as builder

WORKDIR /app

# Installer les dépendances système nécessaires pour la compilation
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copier uniquement requirements.txt pour profiter du cache Docker
COPY requirements.txt .

# Installer les dépendances Python dans un environnement virtuel
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Stage 2: Runtime
FROM python:3.11-slim

WORKDIR /app

# Copier l'environnement virtuel depuis le builder
COPY --from=builder /opt/venv /opt/venv

# Ajouter l'environnement virtuel au PATH
ENV PATH="/opt/venv/bin:$PATH"

# Créer un utilisateur non-root pour la sécurité
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

# Copier le code de l'application backend
COPY --chown=appuser:appuser backend/ /app/

# Créer les dossiers nécessaires
RUN mkdir -p /app/uploads /app/data && \
    chown -R appuser:appuser /app/uploads /app/data

# Basculer vers l'utilisateur non-root
USER appuser

# Variables d'environnement pour Cloud Run
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1
ENV PORT=8080

# Exposer le port (Cloud Run utilisera $PORT)
EXPOSE 8080

# Commande de démarrage optimisée pour production (sans health check qui pourrait échouer au démarrage)
CMD exec uvicorn app.api.main:app --host 0.0.0.0 --port ${PORT} --workers 1 --log-level info
