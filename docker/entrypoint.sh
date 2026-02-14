#!/usr/bin/env bash
set -euo pipefail

export PATH="/opt/venv/bin:${PATH}"

: "${DJANGO_SETTINGS_MODULE:=config.settings.prod}"
export DJANGO_SETTINGS_MODULE

echo "Starting LIMS..."
echo "DJANGO_SETTINGS_MODULE=$DJANGO_SETTINGS_MODULE"
echo "PORT=${PORT:-8000}"

# Wait for DB if DATABASE_URL is set (optional)
if [[ -n "${DATABASE_URL:-}" ]]; then
  echo "DATABASE_URL is set; waiting briefly for database..."
  echo "${DATABASE_URL:-}"
  python - <<'PY'
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
python manage.py migrate --noinput

echo "Creating Cache Table..."
python manage.py createcachetable

echo "Creating Superuser if not exists..."
if [ -n "${DJANGO_SUPERUSER_USERNAME:-}" ]; then
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

User = get_user_model()
username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
email = os.environ.get('DJANGO_SUPERUSER_EMAIL') or ''
password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')

if not username:
    raise SystemExit(0)

if User.objects.filter(username=username).exists():
    print('Superuser already exists:', username)
else:
    if not password:
        raise SystemExit('DJANGO_SUPERUSER_PASSWORD is required to create the superuser')
    User.objects.create_superuser(username=username, email=email, password=password)
    print('Superuser created:', username)
"
fi

echo "Collecting static files..."
python manage.py collectstatic --noinput

echo "Launching gunicorn..."
exec gunicorn config.wsgi:application \
  --bind "0.0.0.0:${PORT:-8000}" \
  --workers "${GUNICORN_WORKERS:-3}" \
  --timeout "${GUNICORN_TIMEOUT:-60}" \
  --access-logfile "-" \
  --error-logfile "-"
