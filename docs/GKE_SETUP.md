# GKE Setup Guide

## Step 1: Create Google Cloud Account
1. Go to https://cloud.google.com/free
2. Sign up with your Google account
3. You'll get **$300 free credits** for 90 days

## Step 2: Install Google Cloud CLI (locally)
```powershell
# Windows - download from:
# https://cloud.google.com/sdk/docs/install

# Or using winget:
winget install Google.CloudSDK
```

## Step 3: Create GKE Cluster (one-time setup)
```bash
# Login to Google Cloud
gcloud auth login

# Set your project (create one if needed)
gcloud projects create ats-matcher-project --name="ATS Matcher"
gcloud config set project ats-matcher-project

# Enable required APIs
gcloud services enable container.googleapis.com
gcloud services enable containerregistry.googleapis.com

# Create Autopilot cluster (cheapest, fully managed)
gcloud container clusters create-auto ats-cluster \
  --region=asia-south1 \
  --project=ats-matcher-project

# Get credentials for kubectl
gcloud container clusters get-credentials ats-cluster \
  --region=asia-south1 \
  --project=ats-matcher-project
```

## Step 4: Set up GitHub Secrets

### 4.1 Create Service Account
```bash
# Create service account for GitHub Actions
gcloud iam service-accounts create github-actions \
  --display-name="GitHub Actions"

# Grant permissions
gcloud projects add-iam-policy-binding ats-matcher-project \
  --member="serviceAccount:github-actions@ats-matcher-project.iam.gserviceaccount.com" \
  --role="roles/container.developer"

gcloud projects add-iam-policy-binding ats-matcher-project \
  --member="serviceAccount:github-actions@ats-matcher-project.iam.gserviceaccount.com" \
  --role="roles/storage.admin"

# Create and download key
gcloud iam service-accounts keys create ~/gcp-key.json \
  --iam-account=github-actions@ats-matcher-project.iam.gserviceaccount.com
```

### 4.2 Add Secrets to GitHub
Go to your repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|-------------|-------|
| `GCP_PROJECT_ID` | `ats-matcher-project` |
| `GCP_SA_KEY` | Contents of `~/gcp-key.json` (base64 encoded) |
| `GKE_CLUSTER` | `ats-cluster` |
| `GKE_ZONE` | `asia-south1` |

To base64 encode the key:
```bash
# Linux/Mac
base64 -i ~/gcp-key.json

# Windows PowerShell
[Convert]::ToBase64String([IO.File]::ReadAllBytes("$HOME\gcp-key.json"))
```

## Step 5: Push to trigger deployment
Once secrets are configured, push to main branch to trigger CI/CD.

## Cost Estimation
With $300 free credits, you can run:
- **Autopilot cluster**: ~$0.10/hour for basic workloads
- Estimated runtime: **3000+ hours** (4+ months of continuous running)
- For demo purposes: virtually free

## Cleanup (to save credits)
```bash
# Delete cluster when not needed
gcloud container clusters delete ats-cluster --region=asia-south1

# Re-create when needed
gcloud container clusters create-auto ats-cluster --region=asia-south1
```
