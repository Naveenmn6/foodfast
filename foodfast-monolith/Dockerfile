FROM python:3.12-slim

# Prevents Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install system build deps (if needed later) and clean up
RUN apt-get update \
    && apt-get install -y --no-install-recommends build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY . .

# Default SQLite DB location (overridable via env)
ENV DATABASE_URL=sqlite:////data/foodfast.db

# Create directory for SQLite DB
RUN mkdir -p /data

EXPOSE 8000

# Run using gunicorn and the Flask app factory
CMD ["gunicorn", "-b", "0.0.0.0:8000", "foodfast:create_app()"]
