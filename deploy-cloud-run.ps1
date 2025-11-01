# Script de déploiement sur Google Cloud Run
# Usage: .\deploy-cloud-run.ps1

$PROJECT_ID = "hale-silicon-474417-u1"
$REPO = "mon-repo"
$REGION = "europe-west1"

Write-Host "🚀 Déploiement sur Google Cloud Run" -ForegroundColor Green
Write-Host "Project ID: $PROJECT_ID" -ForegroundColor Cyan
Write-Host "Region: $REGION" -ForegroundColor Cyan
Write-Host ""

# Vérifier que les variables d'environnement sont définies
if (-not $env:MONGO_URI) {
    Write-Host "⚠️  MONGO_URI n'est pas défini" -ForegroundColor Yellow
    $env:MONGO_URI = Read-Host "Entrez votre MONGO_URI"
}

if (-not $env:GOOGLE_API_KEY) {
    Write-Host "⚠️  GOOGLE_API_KEY n'est pas défini" -ForegroundColor Yellow
    $env:GOOGLE_API_KEY = Read-Host "Entrez votre GOOGLE_API_KEY"
}

# Build et push backend
Write-Host "📦 Build de l'image backend..." -ForegroundColor Yellow
docker build -t europe-west1-docker.pkg.dev/$PROJECT_ID/$REPO/backend:latest -f backend/Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du build backend" -ForegroundColor Red
    exit 1
}

Write-Host "⬆️  Push de l'image backend..." -ForegroundColor Yellow
docker push europe-west1-docker.pkg.dev/$PROJECT_ID/$REPO/backend:latest
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du push backend" -ForegroundColor Red
    exit 1
}

# Déployer backend
Write-Host "🚢 Déploiement du backend sur Cloud Run..." -ForegroundColor Yellow
gcloud run deploy agentils-backend `
    --image europe-west1-docker.pkg.dev/$PROJECT_ID/$REPO/backend:latest `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --timeout 300 `
    --memory 1Gi `
    --cpu 1 `
    --set-env-vars "MONGO_URI=$env:MONGO_URI,GOOGLE_API_KEY=$env:GOOGLE_API_KEY,MONGO_DB=agentils_db"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du déploiement backend" -ForegroundColor Red
    exit 1
}

# Récupérer l'URL du backend
$BACKEND_URL = gcloud run services describe agentils-backend --region $REGION --format "value(status.url)"
Write-Host "✅ Backend déployé: $BACKEND_URL" -ForegroundColor Green

# Build et push frontend
Write-Host "📦 Build de l'image frontend..." -ForegroundColor Yellow
docker build -t europe-west1-docker.pkg.dev/$PROJECT_ID/$REPO/frontend:latest -f frontend/Dockerfile .
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du build frontend" -ForegroundColor Red
    exit 1
}

Write-Host "⬆️  Push de l'image frontend..." -ForegroundColor Yellow
docker push europe-west1-docker.pkg.dev/$PROJECT_ID/$REPO/frontend:latest
if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du push frontend" -ForegroundColor Red
    exit 1
}

# Déployer frontend
Write-Host "🚢 Déploiement du frontend sur Cloud Run..." -ForegroundColor Yellow
gcloud run deploy agentils-frontend `
    --image europe-west1-docker.pkg.dev/$PROJECT_ID/$REPO/frontend:latest `
    --region $REGION `
    --platform managed `
    --allow-unauthenticated `
    --port 8080 `
    --timeout 300 `
    --memory 512Mi `
    --cpu 1 `
    --set-env-vars "NEXT_PUBLIC_API_URL=$BACKEND_URL"

if ($LASTEXITCODE -ne 0) {
    Write-Host "❌ Erreur lors du déploiement frontend" -ForegroundColor Red
    exit 1
}

# Récupérer l'URL du frontend
$FRONTEND_URL = gcloud run services describe agentils-frontend --region $REGION --format "value(status.url)"

Write-Host ""
Write-Host "✅ Déploiement terminé avec succès!" -ForegroundColor Green
Write-Host "🌐 Frontend: $FRONTEND_URL" -ForegroundColor Cyan
Write-Host "🔧 Backend: $BACKEND_URL" -ForegroundColor Cyan
