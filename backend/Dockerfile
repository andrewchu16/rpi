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

# Create non-root user
RUN useradd -u 10001 -m app

# Copy pyproject.toml and uv.lock with proper ownership
COPY --chown=app:app pyproject.toml uv.lock ./

# Install dependencies using uv
RUN uv sync --frozen

# Copy logging config with proper ownership
COPY --chown=app:app logging_config.json ./

# Copy source code with proper ownership
COPY --chown=app:app src/ ./src

USER app

HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000 || exit 1

CMD ["uv", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]
