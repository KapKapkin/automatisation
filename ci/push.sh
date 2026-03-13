#!/bin/bash
set -e

IMAGE_NAME="${DOCKER_USERNAME}/automatisation-web"

# Determine tag based on branch
if [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "prod" ]]; then
    TAG="prod"
elif [[ "$BRANCH_NAME" == "dev" ]]; then
    TAG="dev"
else
    echo "=== Branch '${BRANCH_NAME}' — skip push ==="
    exit 0
fi

echo "=== Logging into DockerHub ==="
echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

echo "=== Pushing ${IMAGE_NAME}:${TAG} ==="
docker push "${IMAGE_NAME}:${TAG}"

if [[ "$TAG" == "prod" ]]; then
    docker tag "${IMAGE_NAME}:${TAG}" "${IMAGE_NAME}:latest"
    docker push "${IMAGE_NAME}:latest"
    echo "Also pushed as: ${IMAGE_NAME}:latest"
fi

echo "=== Push complete ==="
