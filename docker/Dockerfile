############################
# Builder (Astral uv image)
############################
FROM ghcr.io/astral-sh/uv:python3.13-trixie-slim AS builder

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    VIRTUAL_ENV=/opt/venv \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    libpq-dev \
    pkg-config \
    libxmlsec1-dev \
    libxmlsec1-openssl \
 && rm -rf /var/lib/apt/lists/*

# Optional: you can keep this, or omit it and let uv create the venv
RUN python -m venv "${VIRTUAL_ENV}"

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev

COPY . .



############################
# Runtime (no uv)
############################
FROM python:3.13-slim-trixie AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8000 \
    VIRTUAL_ENV=/opt/venv \
    PATH="/opt/venv/bin:${PATH}"

WORKDIR /app

# runtime libs only
RUN apt-get update && apt-get install -y --no-install-recommends \
    libpq5 \
    bash \
    xmlsec1 \
    libxmlsec1-openssl \
 && rm -rf /var/lib/apt/lists/*

# Create an unprivileged runtime user.
RUN groupadd --system --gid 10001 app \
 && useradd --system --uid 10001 --gid app --create-home --home-dir /home/app app

COPY --chown=app:app --from=builder /opt/venv /opt/venv
COPY --chown=app:app --from=builder /app /app

RUN chown app:app /app \
 && mkdir -p /app/staticfiles \
 && chown app:app /app/staticfiles

RUN chmod +x docker/entrypoint.sh

EXPOSE 8000
USER app
CMD ["bash", "-c", "docker/entrypoint.sh"]
