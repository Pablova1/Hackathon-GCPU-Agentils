#!/bin/bash

# Deploy Backend to Cloud Run
# Usage: ./scripts/deploy-backend.sh YOUR-PROJECT-ID

PROJECT_ID=$1
REGION="eu-west1"
SERVICE_NAME="agentils-backend"

if [ -z "$PROJECT_ID" ]; then
    echo "Usage: ./scripts/deploy-backend.sh YOUR-PROJECT-ID"
    exit 1
fi

echo "🔨 Building and deploying backend to Cloud Run..."
echo "Project: $PROJECT_ID"
echo "Service: $SERVICE_NAME"
echo ""

# Build et déployer directement
gcloud run deploy $SERVICE_NAME \
    --source ./backend \
    --platform managed \
    --region $REGION \
    --project $PROJECT_ID \
    --allow-unauthenticated \
    --port 8000 \
    --memory 512Mi \
    --cpu 1 \
    --timeout 3600 \
    --set-env-vars "ENVIRONMENT=production" \
    --no-gen2

echo ""
echo "✅ Backend déployé !"
echo "URL: https://$SERVICE_NAME-XXXXXXXX-ew.a.run.app"
echo ""
echo "Pour voir les logs:"
echo "gcloud run logs read $SERVICE_NAME --limit 50 --region $REGION"
