FROM python:3.10-slim

WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    gcc \
    libc6-dev \
    python3-dev \
    libffi-dev \
    g++ \
    make \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Docker CLI
RUN curl -fsSL https://get.docker.com -o get-docker.sh && \
    sh get-docker.sh && \
    rm get-docker.sh

# Create requests directory
RUN mkdir -p /app/requests && chmod 777 /app/requests

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 5000

ENV PYTHONUNBUFFERED=1
ENV FLASK_APP=app.py

# Use a single worker to ensure only one background worker thread
CMD chmod -R 777 /app/requests && gunicorn --bind 0.0.0.0:5000 --workers 1 app:app
