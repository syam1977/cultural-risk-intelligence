#!/usr/bin/env bash
set -euo pipefail

PROJECT_ID="avex-corp-elearning"
REGION="us-central1"
SERVICE_NAME="cultural-risk-intelligence"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SA="cultural-risk-sa@${PROJECT_ID}.iam.gserviceaccount.com"

echo "==> Building container image..."
gcloud builds submit --tag "${IMAGE}" .

echo "==> Deploying to Cloud Run (${REGION})..."
gcloud run deploy "${SERVICE_NAME}" \
  --image "${IMAGE}" \
  --region "${REGION}" \
  --platform managed \
  --allow-unauthenticated \
  --service-account "${SA}" \
  --set-env-vars "GOOGLE_CLOUD_PROJECT=${PROJECT_ID},GOOGLE_CLOUD_LOCATION=global,GOOGLE_CLOUD_LIVE_LOCATION=us-central1" \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 10 \
  --port 8080 \
  --timeout 300

echo "==> Done!"
gcloud run services describe "${SERVICE_NAME}" --region "${REGION}" --format="value(status.url)"
