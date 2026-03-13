#!/bin/bash
set -e

IMAGE_NAME="${DOCKER_USERNAME}/automatisation-web"

if [[ "$BRANCH_NAME" == "main" || "$BRANCH_NAME" == "prod" ]]; then
    TAG="prod"
elif [[ "$BRANCH_NAME" == "dev" ]]; then
    TAG="dev"
else
    TAG=$(echo "$BRANCH_NAME" | sed 's|/|-|g')
fi

echo "=== Building image: ${IMAGE_NAME}:${TAG} ==="
docker build -t "${IMAGE_NAME}:${TAG}" .