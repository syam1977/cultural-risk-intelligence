#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="${GCP_PROJECT_ID:?GCP_PROJECT_ID を設定してください}"
REGION="us-central1"
SERVICE_NAME="cultural-risk-intelligence"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"

echo "==> Building container image..."
gcloud builds submit --tag "${IMAGE}" .

echo "==> Deploying to Cloud Run (${REGION})..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --set-env-vars "GOOGLE_API_KEY=${GOOGLE_API_KEY:?GOOGLE_API_KEY を設定してください}" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --port 8080 \
  --timeout 300

echo "==> Done!"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)"
