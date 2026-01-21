FROM python:3.12-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source and create non-root user
COPY src/ ./src/
RUN useradd -u 1000 appuser && chown -R appuser:appuser /app
USER appuser

EXPOSE 8000 8501

# Run both services (API in background, UI in foreground)
CMD uvicorn src.app:app --host 0.0.0.0 --port 8000 & streamlit run src/ui.py --server.port 8501 --server.address 0.0.0.0 --server.headless true
