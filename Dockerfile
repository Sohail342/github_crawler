# Builder Stage
FROM python:3.12-slim AS builder
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential curl \
    && rm -rf /var/lib/apt/lists/*

# Install uv
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Copy dependency files
COPY pyproject.toml ./

ARG INSTALL_EXTRAS=prod
# Install packages into a virtualenv
RUN uv lock && uv sync --${INSTALL_EXTRAS} --frozen --no-cache



# Runtime Stage
FROM python:3.12-slim
WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PATH="/app/.venv/bin:$PATH"

RUN apt-get update && apt-get install -y --no-install-recommends \
    && rm -rf /var/lib/apt/lists/* \
    && useradd -m appuser

#  copy uv binaries from builder stage
COPY --from=ghcr.io/astral-sh/uv:latest /uv /uvx /bin/

# Use --chown directly in the COPY command.
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv

# Copy application code
COPY --chown=appuser:appuser ./app ./app
COPY --chown=appuser:appuser ./alembic.ini ./
COPY --chown=appuser:appuser ./alembic ./alembic
COPY --chown=appuser:appuser scripts/docker-entrypoint.sh /usr/local/bin/

# Change ownership of app directory to appuser
RUN chown appuser:appuser /app

#chmod the specific file
RUN chmod +x /usr/local/bin/docker-entrypoint.sh

USER appuser

ENTRYPOINT ["/usr/local/bin/docker-entrypoint.sh"]

CMD ["gunicorn", "-k", "uvicorn.workers.UvicornWorker", "app.main:app", "-b", "0.0.0.0:8000", "--workers", "4", "--timeout", "120"]
