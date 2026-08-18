# ============================================================
# GCP Project Setup Script — Multi-Agent AI Code Reviewer
# ============================================================
# PowerShell version for Windows environments.
#
# This script automates the GCP infrastructure setup for Phase 1.
# It enables required APIs, creates service accounts, configures
# IAM roles, sets up Firestore, Cloud Storage, and Secret Manager.
#
# Prerequisites:
#   - Google Cloud SDK (gcloud) installed and on PATH
#   - Authenticated via `gcloud auth login`
#   - Billing enabled on the target GCP project
#
# Usage:
#   .\setup_gcp.ps1 -ProjectId <PROJECT_ID> [-Region <REGION>]
#
# Example:
#   .\setup_gcp.ps1 -ProjectId daring-fiber-408912 -Region us-central1
# ============================================================

param(
    [Parameter(Mandatory=$true)]
    [string]$ProjectId,

    [string]$Region = "us-central1"
)

$ErrorActionPreference = "Stop"

# ─── Fix PATH: ensure gcloud is resolvable when script is called from any shell ──
$gcloudPath = "$env:LOCALAPPDATA\Google\Cloud SDK\google-cloud-sdk\bin"
if (Test-Path $gcloudPath) {
    $env:Path = "$gcloudPath;" + $env:Path
} else {
    # fallback: refresh from registry
    $env:Path = [System.Environment]::GetEnvironmentVariable("Path","Machine") + ";" + [System.Environment]::GetEnvironmentVariable("Path","User")
}

# Verify gcloud is available
try { $null = Get-Command gcloud -ErrorAction Stop }
catch {
    Write-Host "ERROR: gcloud not found. Install Google Cloud SDK and re-run." -ForegroundColor Red
    Write-Host "  Download: https://cloud.google.com/sdk/docs/install" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  Multi-Agent AI Code Reviewer - GCP Setup                  " -ForegroundColor Cyan
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host "  Project:  $ProjectId" -ForegroundColor White
Write-Host "  Region:   $Region" -ForegroundColor White
Write-Host "===========================================================" -ForegroundColor Cyan
Write-Host ""

# ─── Set Project ─────────────────────────────────────────────
Write-Host "Setting active project..." -ForegroundColor Yellow
gcloud config set project $ProjectId
Write-Host ""

# ─── Billing check (via REST API — no beta component needed) ─
Write-Host "Checking billing status..." -ForegroundColor Yellow
try {
    $token = (gcloud auth print-access-token 2>&1)
    $billingUri = "https://cloudbilling.googleapis.com/v1/projects/$ProjectId/billingInfo"
    $resp = Invoke-RestMethod -Uri $billingUri -Headers @{ Authorization = "Bearer $token" } -ErrorAction Stop
    $skipApis = -not $resp.billingEnabled
    if ($skipApis) {
        Write-Host ""
        Write-Host "  [!] BILLING IS NOT ENABLED on project $ProjectId" -ForegroundColor Red
        Write-Host ""
        Write-Host "  To fix this:" -ForegroundColor Yellow
        Write-Host "  1. Open: https://console.cloud.google.com/billing/projects?project=$ProjectId" -ForegroundColor Cyan
        Write-Host "  2. Click 'Link a billing account' and select or create one" -ForegroundColor White
        Write-Host "  3. Re-run this script after billing is enabled" -ForegroundColor White
        Write-Host ""
        Write-Host "  Skipping API enablement. All other steps will proceed..." -ForegroundColor DarkYellow
        Write-Host ""
    } else {
        Write-Host "  Billing is enabled" -ForegroundColor Green
    }
} catch {
    Write-Host "  Could not check billing status - proceeding anyway" -ForegroundColor DarkYellow
    $skipApis = $false
}
Write-Host ""

# ─── Enable APIs ─────────────────────────────────────────────
Write-Host "Enabling required APIs..." -ForegroundColor Yellow
$apis = @(
    "run.googleapis.com",
    "firestore.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "logging.googleapis.com",
    "monitoring.googleapis.com",
    "cloudtrace.googleapis.com",
    "artifactregistry.googleapis.com",
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com"
    # Note: appcheck.googleapis.com is optional (Firebase premium).
    # Enable manually via Console if your project supports it:
    # https://console.cloud.google.com/apis/library/appcheck.googleapis.com
)

if ($skipApis) {
    Write-Host "  Skipped (billing not enabled)" -ForegroundColor DarkYellow
} else {
    $failedApis = @()
    foreach ($api in $apis) {
        Write-Host "  Enabling $api..." -NoNewline
        $out = gcloud services enable $api --project $ProjectId 2>&1
        if ($LASTEXITCODE -eq 0) {
            Write-Host " OK" -ForegroundColor Green
        } else {
            Write-Host " FAILED" -ForegroundColor Red
            $failedApis += $api
        }
    }
    if ($failedApis.Count -gt 0) {
        Write-Host "  Warning: $($failedApis.Count) API(s) failed to enable:" -ForegroundColor Yellow
        $failedApis | ForEach-Object { Write-Host "    - $_" -ForegroundColor Yellow }
    } else {
        Write-Host "  All 12 APIs enabled successfully" -ForegroundColor Green
    }
}
Write-Host ""

# ─── Create Service Accounts ────────────────────────────────
Write-Host "Creating service accounts..." -ForegroundColor Yellow

try {
    gcloud iam service-accounts create backend-sa `
        --display-name="Code Reviewer Backend" `
        --description="Service account for the FastAPI backend on Cloud Run" 2>$null
    Write-Host "  backend-sa created" -ForegroundColor Green
} catch {
    Write-Host "  backend-sa already exists" -ForegroundColor DarkGray
}

try {
    gcloud iam service-accounts create frontend-sa `
        --display-name="Code Reviewer Frontend" `
        --description="Service account for the Next.js frontend on Cloud Run" 2>$null
    Write-Host "  frontend-sa created" -ForegroundColor Green
} catch {
    Write-Host "  frontend-sa already exists" -ForegroundColor DarkGray
}
Write-Host ""

# ─── Assign IAM Roles ───────────────────────────────────────
Write-Host "Assigning IAM roles..." -ForegroundColor Yellow

$backendSA = "backend-sa@${ProjectId}.iam.gserviceaccount.com"
$frontendSA = "frontend-sa@${ProjectId}.iam.gserviceaccount.com"

$backendRoles = @(
    "roles/datastore.user",
    "roles/storage.objectViewer",
    "roles/secretmanager.secretAccessor",
    "roles/logging.logWriter",
    "roles/cloudtrace.agent",
    "roles/monitoring.metricWriter"
)

foreach ($role in $backendRoles) {
    $null = gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$backendSA" `
        --role="$role" `
        --quiet 2>&1
}
Write-Host "  Backend SA roles assigned" -ForegroundColor Green

$frontendRoles = @(
    "roles/logging.logWriter"
)

foreach ($role in $frontendRoles) {
    $null = gcloud projects add-iam-policy-binding $ProjectId `
        --member="serviceAccount:$frontendSA" `
        --role="$role" `
        --quiet 2>&1
}
Write-Host "  Frontend SA roles assigned" -ForegroundColor Green
Write-Host ""

# ─── Setup Firestore ────────────────────────────────────────
Write-Host "Setting up Firestore..." -ForegroundColor Yellow
try {
    gcloud firestore databases create `
        --location="$Region" `
        --type=firestore-native 2>$null
    Write-Host "  Firestore database created" -ForegroundColor Green
} catch {
    Write-Host "  Firestore database already exists" -ForegroundColor DarkGray
}
Write-Host ""

# ─── Create Cloud Storage Bucket ────────────────────────────
Write-Host "Creating Cloud Storage bucket..." -ForegroundColor Yellow
$bucketName = "${ProjectId}-rules"

try {
    gcloud storage buckets create "gs://${bucketName}" `
        --location="$Region" `
        --uniform-bucket-level-access 2>$null
    Write-Host "  Bucket gs://$bucketName created" -ForegroundColor Green
} catch {
    Write-Host "  Bucket $bucketName already exists" -ForegroundColor DarkGray
}
Write-Host ""

# ─── Upload Seed CSV ────────────────────────────────────────
Write-Host "Uploading historical_reviews.csv..." -ForegroundColor Yellow
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$csvPath = Join-Path $scriptDir "..\seed\historical_reviews.csv"

if (Test-Path $csvPath) {
    $null = gcloud storage cp $csvPath "gs://${bucketName}/rules/historical_reviews.csv" 2>&1
    Write-Host "  CSV uploaded to gs://$bucketName/rules/historical_reviews.csv" -ForegroundColor Green
} else {
    Write-Host "  CSV not found at $csvPath - upload manually" -ForegroundColor Red
}
Write-Host ""

# ─── Create Secrets ──────────────────────────────────────────
Write-Host "Creating Secret Manager secrets (placeholders)..." -ForegroundColor Yellow

$secrets = @("firebase-admin-sdk-key", "firebase-api-key")
foreach ($secretName in $secrets) {
    try {
        gcloud secrets create $secretName `
            --replication-policy="automatic" 2>$null
        Write-Host "  $secretName created" -ForegroundColor Green
    } catch {
        Write-Host "  $secretName already exists" -ForegroundColor DarkGray
    }
}
Write-Host "  Add values: gcloud secrets versions add firebase-admin-sdk-key --data-file=<path>" -ForegroundColor DarkYellow
Write-Host ""

# ─── Create VPC Connector ───────────────────────────────────
Write-Host "Creating serverless VPC connector..." -ForegroundColor Yellow
try {
    gcloud compute networks vpc-access connectors create code-reviewer-vpc `
        --region="$Region" `
        --range="10.8.0.0/28" 2>$null
    Write-Host "  VPC connector created" -ForegroundColor Green
} catch {
    Write-Host "  VPC connector already exists" -ForegroundColor DarkGray
}
Write-Host ""

# ─── Summary ────────────────────────────────────────────────
Write-Host "==========================================================" -ForegroundColor Green
Write-Host "  GCP Setup Complete!                                       " -ForegroundColor Green
Write-Host "==========================================================" -ForegroundColor Green
if ($skipApis) {
    Write-Host "  APIs:             SKIPPED - enable billing first" -ForegroundColor Red
    Write-Host "  Billing URL:      https://console.cloud.google.com/billing/projects?project=$ProjectId" -ForegroundColor Cyan
} else {
    Write-Host "  APIs:             12 enabled" -ForegroundColor White
}
Write-Host "  Service Accounts: backend-sa, frontend-sa" -ForegroundColor White
Write-Host "  Firestore:        Native mode ($Region)" -ForegroundColor White
Write-Host "  Storage:          gs://$bucketName" -ForegroundColor White
Write-Host "  Secrets:          firebase-admin-sdk-key, firebase-api-key" -ForegroundColor White
Write-Host "  VPC Connector:    code-reviewer-vpc" -ForegroundColor White
Write-Host "==========================================================" -ForegroundColor Green
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Add Firebase Admin SDK key to Secret Manager" -ForegroundColor White
Write-Host "  2. Run: firebase deploy --only firestore:rules,firestore:indexes" -ForegroundColor White
Write-Host "  3. Run: python infrastructure/seed/seed_firestore.py --project $ProjectId" -ForegroundColor White
Write-Host ""
