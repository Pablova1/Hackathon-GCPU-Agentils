#!/bin/bash

# Deploy Frontend to Cloud Run
# Usage: ./scripts/deploy-frontend.sh YOUR-PROJECT-ID

PROJECT_ID=$1
REGION="eu-west1"
SERVICE_NAME="agentils-frontend"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./scripts/deploy-frontend.sh YOUR-PROJECT-ID"
    exit 1
fi

echo "🔨 Building and deploying frontend to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo ""

# Build et déployer directement
gcloud run deploy $SERVICE_NAME \
    --source ./frontend \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --port 3000 \
    --memory 256Mi \
    --cpu 1 \
    --timeout 3600 \
    --set-env-vars "NEXT_PUBLIC_API_URL=https://agentils-backend-XXXXXXXX-ew.a.run.app" \
    --no-gen2

echo ""
echo "✅ Frontend déployé !"
echo "URL: https://$SERVICE_NAME-XXXXXXXX-ew.a.run.app"
echo ""
echo "Pour voir les logs:"
echo "gcloud run logs read $SERVICE_NAME --limit 50 --region $REGION"
