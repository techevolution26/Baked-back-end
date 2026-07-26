FROM python:3.12-slim

WORKDIR /app

# Install system dependencies if required for compiling certain python binary files
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Ensure execution flags are set for the automated startup orchestrator
RUN chmod +x docker-entrypoint.sh

EXPOSE 8000

# Swapped healthcheck to use standard lightweight curl utility pattern
HEALTHCHECK --interval=30s --timeout=5s --start-period=15s --retries=5 \
  CMD curl -f http://localhost:8000/health || exit 1

ENTRYPOINT ["./docker-entrypoint.sh"]
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
