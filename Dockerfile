# 1. Use a slim base image
FROM python:3.12-slim

# Install dev essentials for building wheels
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Make Python friendlier for logs in containers
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

# 2. Set the working directory
WORKDIR /app

# 3. Create the virtual environment (optional in containers, but fine)
RUN python3 -m venv /opt/venv

# 4. Use the venv by default
ENV PATH="/opt/venv/bin:$PATH"

# 5. Install dependencies
COPY requirements.txt .
# Upgrade pip and tooling in the venv, then install deps
RUN python -m pip install --no-cache-dir --upgrade pip setuptools wheel && \
    python -m pip install --no-cache-dir -r requirements.txt

# 6. Prepare a writable data dir and persist it even without bind mounts
RUN mkdir -p /app/data
VOLUME ["/app/data"]

# 7. Copy application code (respecting .dockerignore)
COPY . .

# 8. Run the application
CMD ["python3", "monitor_airport.py"]
