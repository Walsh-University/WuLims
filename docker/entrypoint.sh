#!/usr/bin/env bash
set -euo pipefail

: "${DJANGO_SETTINGS_MODULE:=config.settings}"
export DJANGO_SETTINGS_MODULE

echo "Starting LIMS..."
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "PORT=${PORT:-8000}"

# Wait for DB if DATABASE_URL is set (optional)
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is set; waiting briefly for database..."
  uv run --no-sync python - <<'PY'
import os, time, sys, urllib.parse, socket
url = os.environ["DATABASE_URL"]
u = urllib.parse.urlparse(url)
host = u.hostname or "localhost"
port = u.port or 5432
deadline = time.time() + 60
while time.time() < deadline:
    try:
        with socket.create_connection((host, port), timeout=2):
            print("Database reachable.")
            sys.exit(0)
    except OSError:
        time.sleep(1)
print("Database not reachable after 60s.", file=sys.stderr)
sys.exit(1)
PY
fi

echo "Running migrations..."
uv run --no-sync python manage.py migrate --noinput

echo "Collecting static files..."
uv run --no-sync python manage.py collectstatic --noinput

echo "Launching gunicorn..."
exec uv run --no-sync gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile "-" \
  --error-logfile "-"
