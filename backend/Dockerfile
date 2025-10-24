FROM python:3.11-slim

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier l'application backend
COPY backend/ .

# Cloud Run écoute sur le port indiqué par la variable PORT
ENV PORT=8000

# Exposer le port
EXPOSE 8000

# Commande de démarrage
CMD ["uvicorn", "app.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
