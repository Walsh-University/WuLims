# Docker

This guide explains Docker and how WuLims uses it for a repeatable, production-like environment.

## What Is Docker?

Docker packages an application and its dependencies into an **image**. When you run an image, it becomes a **container**. Containers are isolated, consistent, and easy to start on any machine.

Think of it like a sealed lab kit:
- **Image** = the kit (everything you need)
- **Container** = the kit opened and running

## How Docker Works in WuLims

WuLims has Docker files in `docker/` that define how the app is built and started.

### Dockerfile (Build Steps)

`docker/Dockerfile` builds the image in layers:

1. Starts from `python:3.13-slim` (small base image)
2. Installs system tools and `uv`
3. Installs Python dependencies with `uv sync`
4. Copies the project code
5. Sets the entrypoint script

This creates a lightweight image that contains everything needed to run Django.

### Entrypoint (Run Steps)

`docker/entrypoint.sh` runs every time the container starts:

1. Prints basic startup info
2. Waits for the database if `DATABASE_URL` is set
3. Runs migrations
4. Collects static files
5. Starts Gunicorn

This keeps startup consistent and avoids manual setup inside the container.

### .dockerignore

`.dockerignore` keeps large or local-only files out of the image (like `.venv/`, `__pycache__/`, and coverage reports). This keeps builds fast and images small.

### Django Settings for Docker

In `config/settings.py`, Docker-specific defaults include:
- `STATIC_ROOT` set so `collectstatic` can run inside the container
- `ALLOWED_HOSTS = ["*"]` for container networking
- Database switches to PostgreSQL when `DB_NAME` is set

These changes make the app work both locally and in containers.

---

## Build and Run the Container

From the project root:

```bash
# Build the image
docker build -f docker/Dockerfile -t wulims:dev .

# Run the container
docker run --rm -p 8000:8000 wulims:dev
```

Then visit: http://127.0.0.1:8000/

## Using PostgreSQL with Docker Compose

The repo includes `docker-compose.yml` for a local Postgres database:

```bash
docker compose up -d
```

Set environment variables so Django uses Postgres (example):

```bash
export DB_NAME=wulims
export DB_USER=wulims
export DB_PASSWORD=wulims_dev_password
export DB_HOST=localhost
export DB_PORT=5432
```

To stop the database:

```bash
docker compose down
```

## Common Troubleshooting

**Container fails to start**
- Check logs: `docker logs <container_id>`
- Make sure port 8000 is free

**Database errors**
- If using Postgres, confirm `DB_*` variables are set
- If using `DATABASE_URL`, ensure the host is reachable

**Static files not loading**
- `collectstatic` runs automatically, but confirm `STATIC_ROOT` is set and `staticfiles/` exists inside the container
