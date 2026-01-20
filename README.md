# ATS Keyword Matcher: Production-Ready DevOps Project

---

#### Problem Background & Motivation
Modern recruitment relies on Applicant Tracking Systems (ATS) to filter resumes. Many qualified candidates are rejected due to formatting or keyword mismatches. This project helps users optimize their resumes for ATS compatibility, improving their chances of selection.

#### Application Overview
The ATS Keyword Matcher is a Python-based web application with a FastAPI backend and Streamlit UI. It parses resumes, redacts sensitive information, and provides actionable feedback for ATS optimization. The solution is containerized with Docker and orchestrated using Kubernetes, following DevOps best practices.

#### CI/CD Architecture Diagram
```
User Push/PR
  |
GitHub Actions (CI)
  |-- Lint, Test, Security Scan
  |-- Build & Push Docker Image
  |
GitHub Actions (CD)
  |-- Deploy to Kubernetes
  |-- Health Checks
```

#### CI/CD Pipeline Design & Stages
- **CI Pipeline**
  - Linting (Flake8)
  - Unit Testing (Pytest with coverage)
  - SAST (CodeQL)
  - Dependency Scan (Trivy)
  - Docker Build & Push (main branch)
- **CD Pipeline**
  - Deploys Docker image to Kubernetes
  - Health checks deployment
  - Manual image tag management (no sed automation)


#### Security & Quality Controls
- **CodeQL**: Static code analysis for vulnerabilities
- **Trivy**: Container and dependency scanning
- **Resource Limits**: Prevents resource exhaustion
- **Probes**: Ensures only healthy pods serve traffic
- **Non-root Containers**: Enhanced security

#### Results & Observations
- CI/CD pipeline automates quality and security checks, ensuring only safe, tested code is deployed.
- Kubernetes deployment with resource limits and probes ensures high availability and reliability.
- Application successfully parses and redacts resumes, providing actionable feedback for ATS optimization.

#### Limitations & Improvements
- Current deployment is single-replica; can be scaled for high availability.
- No persistent storage for user data (stateless by design).
- Future work: add more advanced NLP for resume analysis, multi-language support, and user authentication.

---

### 2. Additional Files
- **GitHub Actions Workflow**: `.github/workflows/ci.yml`, `.github/workflows/cd.yml`
- **Application Source Code**: `src/`
- **Dockerfile**: `Dockerfile`
- **README**: `README.md`
- **How to run locally**: See below
- **Secrets configuration**: See below
- **CI explanation**: See CI/CD Pipeline section above

---

### 3. Secrets Configuration (Mandatory)

Configure the following GitHub Secrets in your repository:

| Secret Name                  | Purpose                                 |
|------------------------------|-----------------------------------------|
| DOCKERHUB_USERNAME           | Docker registry user                    |
| DOCKERHUB_TOKEN              | Secure registry access                  |
| DIGITALOCEAN_ACCESS_TOKEN    | DigitalOcean API access for doctl/CI    |
| DIGITALOCEAN_CLUSTER_NAME    | Name of your DigitalOcean K8s cluster   |
| DIGITALOCEAN_KUBECONFIG      | (Optional) Kubeconfig for cluster auth  |

**Note:**
- Do NOT hardcode secrets in code or workflow files.

---

## Repository
- **GitHub:** [https://github.com/your-username/ats-keyword-matcher](https://github.com/your-username/ats-keyword-matcher)

---

## Appendix: Key Configurations

### k8s/service.yaml
```yaml
apiVersion: v1
kind: Service
metadata:
  name: ats-matcher-service
  labels:
    app: ats-matcher
spec:
  type: LoadBalancer
  ports:
    - port: 80
      targetPort: 8501
      protocol: TCP
      name: ui
    - port: 8000
      targetPort: 8000
      protocol: TCP
      name: api
  selector:
    app: ats-matcher
```

### k8s/deployment.yaml
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ats-matcher
  labels:
    app: ats-matcher
spec:
  replicas: 1
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxUnavailable: 1
      maxSurge: 0
  selector:
    matchLabels:
      app: ats-matcher
  template:
    metadata:
      labels:
        app: ats-matcher
    spec:
      securityContext:
        runAsNonRoot: true
        runAsUser: 1000
      containers:
        - name: ats-matcher
          image: ats-matcher:latest
          imagePullPolicy: Always
          ports:
            - containerPort: 8000
              name: api
            - containerPort: 8501
              name: ui
          resources:
            requests:
              memory: "256Mi"
              cpu: "100m"
            limits:
              memory: "512Mi"
              cpu: "500m"
          # ...probes and other settings...
```

---

*Replace `<IMAGE_NAME>:<TAG>` with your Docker image and tag if customizing.*

---

## Usage Instructions
### Prerequisites
- Docker
- kubectl
- Python 3.10+
- Access to a Kubernetes cluster (e.g., DigitalOcean)

### Local Development
1. Clone the repo:
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
5. (Optional) Run tests with coverage:
  ```bash
  pytest --cov=src --cov-report=term-missing
  ```

### Docker
1. Build image:
   ```bash
   docker build -t ats-matcher:latest .
   ```
2. Run container:
   ```bash
   docker run -p 8000:8000 -p 8501:8501 ats-matcher:latest
   ```

### Kubernetes
1. Deploy:
   ```bash
   kubectl apply -f k8s/deployment.yaml
   kubectl apply -f k8s/service.yaml
   ```
2. Get service IP:
   ```bash
   kubectl get svc
   ```

---

## Features
- **Resume Parsing**: Extracts and analyzes resume content.
- **Privacy Protection**: Redacts sensitive information.
- **Web UI**: User-friendly Streamlit interface.
- **REST API**: FastAPI backend for programmatic access.
- **Production-Grade DevOps**: CI/CD, containerization, and K8s deployment.

---

## Architecture
```
[User] <-> [Streamlit UI] <-> [FastAPI Backend]
```
- **Frontend**: Streamlit (`src/ui.py`)
- **Backend**: FastAPI (`src/app.py`)
- **Containerization**: Docker
- **Orchestration**: Kubernetes (`k8s/deployment.yaml`, `k8s/service.yaml`)

---

## Tech Stack
- **Python 3.10+**
- **FastAPI** (API backend)
- **Streamlit** (UI)
- **Docker** (Containerization)
- **Kubernetes** (Orchestration)
- **GitHub Actions** (CI/CD)
- **CodeQL, Trivy** (Security)
- **Pytest, Pytest-cov, Flake8** (Testing, Coverage & Linting)

---

## Project Structure
```
Resume Optimizer/
├── .github/
│   └── workflows/
│       ├── ci.yml
│       └── cd.yml
├── docs/
│   └── DIGITALOCEAN_SETUP.md
├── k8s/
│   ├── deployment.yaml
│   └── service.yaml
├── src/
│   ├── __init__.py
│   ├── app.py
│   ├── ui.py
│   └── constants/
├── tests/
│   ├── conftest.py
│   └── test_app.py
├── Dockerfile
├── requirements.txt
├── README.md
```

---

## Testing
- **Unit Tests with Coverage**: `pytest --cov=src --cov-report=term-missing`
- **Linting**: `flake8 src/`
- **Security**: `bandit -r src/`

---

## Contributing
1. Fork the repository
2. Create a feature branch
3. Commit changes with clear messages
4. Open a pull request

---

## License
This project is licensed under the MIT License.
