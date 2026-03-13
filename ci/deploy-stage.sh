#!/bin/bash
# CI/CD Deploy Script: Deploy application on stage server
# Used by TeamCity build configuration
#
# Required environment variables:
#   DOCKER_USERNAME - DockerHub username
#   DOCKER_PASSWORD - DockerHub password/token
#   BRANCH_NAME     - Git branch name (set by TeamCity)

set -e

IMAGE_NAME="${DOCKER_USERNAME}/automatisation-web"

# Determine tag based on branch
if [[ "$BRANCH_NAME" == "refs/heads/main" || "$BRANCH_NAME" == "refs/heads/prod" || "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "prod" ]]; then
    TAG="prod"
elif [[ "$BRANCH_NAME" == "refs/heads/dev" || "$BRANCH_NAME" == "dev" ]]; then
    TAG="dev"
else
    echo "=== Branch '${BRANCH_NAME}' - skip deploy ==="
    exit 0
fi

echo "=== Deploying ${IMAGE_NAME}:${TAG} to stage ==="

# Login to DockerHub
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# Pull the latest image
docker pull "${IMAGE_NAME}:${TAG}"

# Deploy using docker-compose.stage.yml
export DOCKER_USERNAME="${DOCKER_USERNAME}"
export DEPLOY_TAG="${TAG}"

docker compose -f docker-compose.stage.yml down --remove-orphans 2>/dev/null || true
docker compose -f docker-compose.stage.yml up -d

echo "=== Waiting for application to start ==="
sleep 10

# Health check
if docker compose -f docker-compose.stage.yml ps | grep -q "Up"; then
    echo "=== Deploy successful! Application is running ==="
    docker compose -f docker-compose.stage.yml ps
else
    echo "=== Deploy FAILED ==="
    docker compose -f docker-compose.stage.yml logs --tail=20
    exit 1
fi
