FROM python:3.11-slim

# Set environment variables for non-interactive installs
ENV DEBIAN_FRONTEND=noninteractive

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*


RUN useradd -m -u 1000 astraea_uid

# Install dependencies first (layer caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt


COPY --chown=astraea_uid:astraea_uid . .

# Expose HF Spaces port
EXPOSE 7860

# Environment Configuration
ENV PORT=7860 \
    HOST=0.0.0.0 \
    PYTHONPATH=/app \
    PYTHONUNBUFFERED=1

# Switch to the non-root user
USER astraea_uid

# Health check to ensure the API is ready
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
  CMD curl -f http://localhost:7860/health || exit 1

# Start the OpenEnv server (respecting the 2 vCPU limit with 1 worker)
CMD ["python", "run.py"]
