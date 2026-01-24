set -e

echo "Building WuLims Docker image..."
docker build -f docker/Dockerfile -t lims:dev .

docker run --rm -p 8000:8000 \
  --env-file .env \
  -e DB_HOST=host.docker.internal \
  lims:dev
