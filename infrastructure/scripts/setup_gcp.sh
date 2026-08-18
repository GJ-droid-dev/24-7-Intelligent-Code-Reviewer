#!/usr/bin/env bash
# ============================================================
# GCP Project Setup Script — Multi-Agent AI Code Reviewer
# ============================================================
# This script automates the GCP infrastructure setup for Phase 1.
# It enables required APIs, creates service accounts, configures
# IAM roles, sets up Firestore, Cloud Storage, and Secret Manager.
#
# Prerequisites:
#   - Google Cloud SDK (gcloud) installed and authenticated
#   - Billing enabled on the target GCP project
#
# Usage:
#   chmod +x setup_gcp.sh
#   ./setup_gcp.sh <PROJECT_ID> <REGION>
#
# Example:
#   ./setup_gcp.sh my-code-reviewer us-central1
# ============================================================

set -euo pipefail

# ─── Arguments ───────────────────────────────────────────────
PROJECT_ID="${1:?Usage: ./setup_gcp.sh <PROJECT_ID> <REGION>}"
REGION="${2:-us-central1}"

echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  Multi-Agent AI Code Reviewer — GCP Setup               ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Project:  ${PROJECT_ID}"
echo "║  Region:   ${REGION}"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""

# ─── Set Project ─────────────────────────────────────────────
echo "📌 Setting active project..."
gcloud config set project "${PROJECT_ID}"

# ─── Enable APIs ─────────────────────────────────────────────
echo ""
echo "🔌 Enabling required APIs..."
gcloud services enable \
    run.googleapis.com \
    firestore.googleapis.com \
    storage.googleapis.com \
    secretmanager.googleapis.com \
    cloudbuild.googleapis.com \
    logging.googleapis.com \
    monitoring.googleapis.com \
    cloudtrace.googleapis.com \
    artifactregistry.googleapis.com \
    firebase.googleapis.com \
    identitytoolkit.googleapis.com \
    appcheck.googleapis.com

echo "   ✓ All APIs enabled"

# ─── Create Service Accounts ────────────────────────────────
echo ""
echo "👤 Creating service accounts..."

# Backend service account
gcloud iam service-accounts create backend-sa \
    --display-name="Code Reviewer Backend" \
    --description="Service account for the FastAPI backend on Cloud Run" \
    2>/dev/null || echo "   (backend-sa already exists)"

# Frontend service account
gcloud iam service-accounts create frontend-sa \
    --display-name="Code Reviewer Frontend" \
    --description="Service account for the Next.js frontend on Cloud Run" \
    2>/dev/null || echo "   (frontend-sa already exists)"

echo "   ✓ Service accounts created"

# ─── Assign IAM Roles ───────────────────────────────────────
echo ""
echo "🔐 Assigning IAM roles..."

BACKEND_SA="backend-sa@${PROJECT_ID}.iam.gserviceaccount.com"
FRONTEND_SA="frontend-sa@${PROJECT_ID}.iam.gserviceaccount.com"

# Backend SA roles (least privilege)
for role in \
    "roles/datastore.user" \
    "roles/storage.objectViewer" \
    "roles/secretmanager.secretAccessor" \
    "roles/logging.logWriter" \
    "roles/cloudtrace.agent" \
    "roles/monitoring.metricWriter"; do
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${BACKEND_SA}" \
        --role="${role}" \
        --quiet
done

# Frontend SA roles (minimal)
for role in \
    "roles/logging.logWriter"; do
    gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
        --member="serviceAccount:${FRONTEND_SA}" \
        --role="${role}" \
        --quiet
done

echo "   ✓ IAM roles assigned"

# ─── Setup Firestore ────────────────────────────────────────
echo ""
echo "🗄️  Setting up Firestore..."
gcloud firestore databases create \
    --location="${REGION}" \
    --type=firestore-native \
    2>/dev/null || echo "   (Firestore database already exists)"

echo "   ✓ Firestore ready"

# ─── Create Cloud Storage Bucket ────────────────────────────
echo ""
echo "📦 Creating Cloud Storage bucket..."
BUCKET_NAME="${PROJECT_ID}-rules"

gcloud storage buckets create "gs://${BUCKET_NAME}" \
    --location="${REGION}" \
    --uniform-bucket-level-access \
    2>/dev/null || echo "   (Bucket ${BUCKET_NAME} already exists)"

echo "   ✓ Bucket: gs://${BUCKET_NAME}"

# ─── Upload Seed CSV ────────────────────────────────────────
echo ""
echo "📄 Uploading historical_reviews.csv..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CSV_PATH="${SCRIPT_DIR}/../seed/historical_reviews.csv"

if [ -f "${CSV_PATH}" ]; then
    gcloud storage cp "${CSV_PATH}" "gs://${BUCKET_NAME}/rules/historical_reviews.csv"
    echo "   ✓ CSV uploaded to gs://${BUCKET_NAME}/rules/historical_reviews.csv"
else
    echo "   ⚠ CSV not found at ${CSV_PATH} — upload manually"
fi

# ─── Create Secrets ──────────────────────────────────────────
echo ""
echo "🔑 Creating Secret Manager secrets (placeholders)..."

for secret_name in "firebase-admin-sdk-key" "firebase-api-key"; do
    gcloud secrets create "${secret_name}" \
        --replication-policy="automatic" \
        2>/dev/null || echo "   (${secret_name} already exists)"
done

echo "   ✓ Secrets created (add values via Console or gcloud)"
echo "   → gcloud secrets versions add firebase-admin-sdk-key --data-file=<path-to-key.json>"

# ─── Create VPC Connector ───────────────────────────────────
echo ""
echo "🌐 Creating serverless VPC connector..."
gcloud compute networks vpc-access connectors create code-reviewer-vpc \
    --region="${REGION}" \
    --range="10.8.0.0/28" \
    2>/dev/null || echo "   (VPC connector already exists)"

echo "   ✓ VPC connector ready"

# ─── Summary ────────────────────────────────────────────────
echo ""
echo "╔══════════════════════════════════════════════════════════╗"
echo "║  ✅ GCP Setup Complete                                  ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  APIs:             12 enabled                           ║"
echo "║  Service Accounts: backend-sa, frontend-sa              ║"
echo "║  Firestore:        Native mode (${REGION})              ║"
echo "║  Storage:          gs://${BUCKET_NAME}                  ║"
echo "║  Secrets:          firebase-admin-sdk-key, firebase-api-key ║"
echo "║  VPC Connector:    code-reviewer-vpc                    ║"
echo "╠══════════════════════════════════════════════════════════╣"
echo "║  Next steps:                                            ║"
echo "║  1. Add Firebase Admin SDK key to Secret Manager        ║"
echo "║  2. Run: firebase init (to deploy Firestore rules)      ║"
echo "║  3. Run: python seed/seed_firestore.py --project ${PROJECT_ID}  ║"
echo "╚══════════════════════════════════════════════════════════╝"
echo ""
