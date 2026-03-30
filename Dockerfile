# Use the official Python 3.12-slim as the base image
FROM python:3.12-slim

# Set the working directory
WORKDIR /app

# Set environment variables to prevent Python from generating .pyc files and to ensure unbuffered logging
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# Install system dependencies: Chromium and driver for Selenium tasks
RUN apt-get update && apt-get install -y \
    chromium \
    chromium-driver \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy high-performance package manager 'uv' from its official image
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency declaration files
COPY pyproject.toml uv.lock ./

# Install Python dependencies using uv (resolves torch, transformers, etc., from pyproject.toml)
# --frozen ensures installation strictly follows uv.lock for environment consistency
RUN uv sync --frozen --no-cache

# Copy the entire project source code
COPY . .

# Add the uv-created virtual environment to the system PATH
ENV PATH="/app/.venv/bin:$PATH"

# Switch working directory to /backend as main.py and configs are relative to this path
WORKDIR /app/backend

# Expose the FastAPI port
EXPOSE 8000

# Start the Uvicorn server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]