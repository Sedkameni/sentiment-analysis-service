# ── Stage 1: builder ────────────────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /app

# Install build dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Install Python packages into a prefix so we can copy them cleanly
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --prefix=/install --no-cache-dir -r requirements.txt

# ── Stage 2: runtime ─────────────────────────────────────────────────────────
FROM python:3.11-slim

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /install /usr/local

# Copy application source
COPY app.py model.py cli.py ./

# Pre-download the model weights at build time so the container is self-contained
# (avoids downloading on first request in production)
RUN python -c "\
from transformers import pipeline; \
pipeline('sentiment-analysis', \
         model='distilbert-base-uncased-finetuned-sst-2-english', \
         tokenizer='distilbert-base-uncased-finetuned-sst-2-english')"

# Expose the port App Runner / Flask will use
EXPOSE 8080

# Run with Gunicorn for production-grade serving
CMD ["gunicorn", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120", "app:app"]
