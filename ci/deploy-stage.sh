#!/bin/bash
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

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

docker pull "${IMAGE_NAME}:${TAG}"

export DOCKER_USERNAME="${DOCKER_USERNAME}"
export DEPLOY_TAG="${TAG}"

docker compose -f docker-compose.stage.yml down --remove-orphans 2>/dev/null || true
docker compose -f docker-compose.stage.yml up -d

echo "=== Waiting for application to start ==="
sleep 10

if docker compose -f docker-compose.stage.yml ps | grep -q "Up"; then
    echo "=== Deploy successful! Application is running ==="
    docker compose -f docker-compose.stage.yml ps
else
    echo "=== Deploy FAILED ==="
    docker compose -f docker-compose.stage.yml logs --tail=20
    exit 1
fi

