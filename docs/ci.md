# CI/CD Pipeline Documentation

This document describes the Continuous Integration and Continuous Deployment (CI/CD) pipeline for the ATS Keyword Matcher project.

## Overview
- **CI**: Linting, testing, static analysis, SCA, Docker build, and image scan.
- **CD**: Deploys the Docker image to Kubernetes and performs health checks.

## CI Pipeline (GitHub Actions)
- **Lint**: Runs flake8 on source and test code.
- **Test**: Runs pytest with coverage reporting.
- **SAST**: Runs CodeQL for static code analysis.
- **SCA**: Runs Trivy for dependency vulnerability scanning (SARIF upload to GitHub Security).
- **Build & Push**: Builds Docker image and pushes to DockerHub.
- **Image Scan**: Trivy scans the built Docker image for vulnerabilities.

## CD Pipeline (GitHub Actions)
- **Kubernetes Deploy**: Applies updated manifests to the cluster.
- **Rollout Check**: Waits for deployment to become ready.
- **DAST**: Optionally checks health endpoints after deployment.

## Quality Gates
- All jobs must pass before deployment.
- Security scan failures block deployment.

## Key Files
- `.github/workflows/ci.yml` — CI pipeline definition
- `.github/workflows/cd.yml` — CD pipeline definition


## Secrets
- `DOCKERHUB_USERNAME`, `DOCKERHUB_TOKEN` — DockerHub credentials
- `DIGITALOCEAN_ACCESS_TOKEN`, `DIGITALOCEAN_CLUSTER_NAME`, `DIGITALOCEAN_REGISTRY` — DigitalOcean Kubernetes and Container Registry access

See the README for more details.
