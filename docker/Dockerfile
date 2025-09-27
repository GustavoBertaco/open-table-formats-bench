# Build stage for development environment
FROM python:3.11-slim as dev

# Set working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install Python development tools
RUN pip install --no-cache-dir \
    pytest \
    pytest-cov \
    black \
    flake8 \
    mypy

# Copy requirements files
COPY requirements.txt .
COPY requirements-dev.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt -r requirements-dev.txt

# Copy project files
COPY . .

# Expose API port
EXPOSE 8080

# Default command for development
CMD ["python", "-m", "pytest"]

# Production stage
FROM python:3.11-slim as prod

WORKDIR /app

# Copy only necessary files from dev stage
COPY --from=dev /app/requirements.txt .
COPY --from=dev /app/src ./src

# Install production dependencies only
RUN pip install --no-cache-dir -r requirements.txt

# Expose API port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV PYTHONDONTWRITEBYTECODE=1

# Default command for production
CMD ["python", "-m", "src.api.main"]