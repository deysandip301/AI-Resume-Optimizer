# Project Setup & Structure

## Setup Instructions

### Prerequisites
- Python 3.10+
- Docker
- kubectl
- (Optional) Access to a Kubernetes cluster

### Local Development
1. Clone the repository:
   ```bash
   git clone <YOUR_GITHUB_REPO_URL>
   cd "Resume Optimizer"
   ```
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Run FastAPI backend:
   ```bash
   uvicorn src.app:app --reload --host 0.0.0.0 --port 8000
   ```
4. Run Streamlit UI:
   ```bash
   streamlit run src/ui.py
   ```
5. Run tests with coverage:
   ```bash
   pytest --cov=src --cov-report=term-missing
   ```

### Docker & Kubernetes
- Build image: `docker build -t <your-username>/ats-matcher:latest .`
- Push image: `docker push <your-username>/ats-matcher:latest`
- Deploy: `kubectl apply -f k8s/`

## Project Structure
```
Resume Optimizer/
├── .github/workflows/      # CI/CD workflows
├── docs/                  # Documentation
├── k8s/                   # Kubernetes manifests
├── src/                   # Application source code
│   ├── app.py             # FastAPI backend
│   ├── ui.py              # Streamlit UI
│   └── ...
├── tests/                 # Pytest tests
├── Dockerfile             # Docker build file
├── requirements.txt       # Python dependencies
└── README.md              # Project overview
```

## Environment Variables
- See `.env.example` if present, or configure as needed for your environment.

## Notes
- For production, use your DockerHub username in image names.
- For custom deployments, update `k8s/deployment.yaml` accordingly.
