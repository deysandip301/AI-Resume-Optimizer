
# Resume Optimizer (ATS Keyword Matcher)

Production-ready, privacy-focused resume optimizer for ATS compatibility. Built with FastAPI, Streamlit, Docker, and Kubernetes. CI/CD via GitHub Actions.

---

## Quick Start

1. **Clone the repo:**
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd "Resume Optimizer"
   ```
2. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```
3. **Run FastAPI backend:**
   ```bash
   uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```
4. **Run Streamlit UI:**
   ```bash
   streamlit run src/ui.py
   ```
5. **Run tests (optional):**
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

---

## Secrets Configuration


Set these GitHub repository secrets for CI/CD and deployment:

| Secret Name                  | Purpose                                 |
|------------------------------|-----------------------------------------|
| DOCKERHUB_USERNAME           | Docker registry user                    |
| DOCKERHUB_TOKEN              | Secure registry access                  |
| DIGITALOCEAN_ACCESS_TOKEN    | DigitalOcean API access for doctl/CI    |
| DIGITALOCEAN_CLUSTER_NAME    | Name of your DigitalOcean K8s cluster   |
| DIGITALOCEAN_REGISTRY        | DigitalOcean Container Registry name    |

**Never hardcode secrets in code or workflow files.**

---

## CI/CD Pipeline

CI/CD is managed by GitHub Actions:

- **CI:** Lint (flake8), test (pytest + coverage), SAST (CodeQL), SCA (Trivy), Docker build & push.
- **CD:** Deploys Docker image to Kubernetes, health checks, and rollout verification.

See [docs/ci.md](docs/ci.md) for full details.

---

## Documentation

- [Project Setup & Structure](docs/setup_and_structure.md)
- [CI/CD Pipeline](docs/ci.md)
- [Contributing Guide](docs/contributing.md)

---

## Project Structure

See [docs/setup_and_structure.md](docs/setup_and_structure.md) for a full breakdown.

---

## Contributing

See [docs/contributing.md](docs/contributing.md).

---

## License

MIT
