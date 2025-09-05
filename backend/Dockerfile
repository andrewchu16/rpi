FROM python:3.13-slim-trixie
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        curl \
        build-essential \
        cmake \
        git \
        pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy pyproject.toml and uv.lock
COPY pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Create non-root user
RUN useradd -u 10001 -m app

# Copy logging config
COPY logging_config.json ./

# Copy model files
COPY models/ ./models

# Copy source code
COPY src/ ./src

# Copy logs
COPY logs/ ./logs

# Fix permissions and ownership for the app user
RUN chown -R app:app /app

USER app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
