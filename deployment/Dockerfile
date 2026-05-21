FROM python:3.11-slim

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends git && rm -rf /var/lib/apt/lists/*

COPY simulator/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY simulator/ .

# Expose port 8080 (GCP default)
EXPOSE 8080

# Run with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:8080", "-w", "4", "--timeout", "120", "app:app"]
