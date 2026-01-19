# Simple Python build for ATS Keyword Matcher
FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY src/ ./src/

# Create non-root user for security (UID 1000 to match K8s securityContext)
RUN useradd --create-home --shell /bin/bash --uid 1000 appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose ports: 8000 (API), 8501 (Streamlit UI)
EXPOSE 8000 8501

# Health check (check API)
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Create startup script to run both services
COPY --chown=appuser:appuser <<EOF /app/start.sh
#!/bin/bash
# Start FastAPI in background
uvicorn src.app:app --host 0.0.0.0 --port 8000 &
# Start Streamlit in foreground
streamlit run src/ui.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
EOF

RUN chmod +x /app/start.sh

# Run both services
CMD ["/bin/bash", "/app/start.sh"]
