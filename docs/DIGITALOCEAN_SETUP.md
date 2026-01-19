# DigitalOcean Kubernetes (DOKS) Setup Guide

## Step 1: Create DigitalOcean Account
1. Go to https://try.digitalocean.com/freetrialoffer/
2. Sign up with your email or GitHub
3. You'll get **$200 free credits for 60 days**

## Step 2: Install doctl CLI (locally)
```powershell
# Windows - using winget:
winget install DigitalOcean.Doctl

# Or download from:
# https://docs.digitalocean.com/reference/doctl/how-to/install/
```

After installation, restart your terminal.

## Step 3: Create API Token
1. Go to https://cloud.digitalocean.com/account/api/tokens
2. Click "Generate New Token"
3. Name: `github-actions`
4. Select both Read and Write scopes
5. Copy the token (you won't see it again!)

## Step 4: Authenticate doctl
```bash
doctl auth init
# Paste your API token when prompted
```

## Step 5: Create Kubernetes Cluster
```bash
# Create a basic cluster in Bangalore, India
doctl kubernetes cluster create ats-cluster \
  --region blr1 \
  --node-pool "name=default;size=s-1vcpu-2gb;count=1" \
  --wait

# This creates:
# - 1 node with 1 vCPU, 2GB RAM (~$12/month)
# - Control plane is FREE
```

Available India regions:
- `blr1` - Bangalore

## Step 6: Get Cluster Credentials
```bash
# Save kubeconfig for kubectl
doctl kubernetes cluster kubeconfig save ats-cluster

# Verify connection
kubectl get nodes
```

## Step 7: Create Container Registry
```bash
# Create a container registry (starter plan is included in free tier)
doctl registry create ats-registry --region blr1

# Login to registry
doctl registry login
```

## Step 8: Set up GitHub Secrets

### 8.1 Get Required Values
```bash
# Get cluster ID
doctl kubernetes cluster get ats-cluster --format ID

# Get registry endpoint
doctl registry get --format Endpoint
```

### 8.2 Add Secrets to GitHub
Go to your repo → Settings → Secrets and variables → Actions → New repository secret:

| Secret Name | Value |
|-------------|-------|
| `DIGITALOCEAN_ACCESS_TOKEN` | Your API token from Step 3 |
| `DIGITALOCEAN_CLUSTER_NAME` | `ats-cluster` |
| `DIGITALOCEAN_REGISTRY` | `registry.digitalocean.com/ats-registry` |

## Step 9: Push to trigger deployment
Once secrets and variables are configured, push to main branch to trigger CI/CD.

## Cost Estimation
With $200 free credits:
- **Control plane**: FREE
- **1 basic node (s-1vcpu-2gb)**: ~$12/month
- **Container registry (starter)**: FREE (500MB)
- Estimated runtime: **~16 months** on free credits!

## Useful Commands
```bash
# List clusters
doctl kubernetes cluster list

# Get cluster info
doctl kubernetes cluster get ats-cluster

# Scale nodes
doctl kubernetes cluster node-pool update ats-cluster default --count 2

# Delete cluster (to save credits)
doctl kubernetes cluster delete ats-cluster

# Re-create cluster
doctl kubernetes cluster create ats-cluster \
  --region blr1 \
  --node-pool "name=default;size=s-1vcpu-2gb;count=1"
```

## Cleanup (to save credits)
```bash
# Delete cluster when not needed
doctl kubernetes cluster delete ats-cluster --force

# Delete registry if not needed
doctl registry delete --force
```
