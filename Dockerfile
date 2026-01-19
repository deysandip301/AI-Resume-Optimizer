# Simple Python build for ATS Keyword Matcher
FROM python:3.10-slim

WORKDIR /app

# Install dependencies - clean old metadata to fix Trivy layer scanning
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    pip install --no-cache-dir --upgrade --force-reinstall "jaraco.context>=6.1.0" && \
    find /usr/local/lib -type d -name "jaraco.context-5*" -exec rm -rf {} + 2>/dev/null || true && \
    find /usr/local/lib -type d -name "pip-23*" -exec rm -rf {} + 2>/dev/null || true

# Copy application source
COPY src/ ./src/

# Create non-root user for security
RUN useradd --create-home --shell /bin/bash appuser && \
    chown -R appuser:appuser /app
USER appuser

# Expose API port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/health')" || exit 1

# Run the FastAPI application
CMD ["uvicorn", "src.app:app", "--host", "0.0.0.0", "--port", "8000"]
