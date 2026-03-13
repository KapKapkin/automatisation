#!/bin/bash
# CI/CD Build Script: Build and push Docker image
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
    # For any other branch, use branch name sanitized
    TAG=$(echo "$BRANCH_NAME" | sed 's|refs/heads/||' | sed 's|/|-|g')
fi

echo "=== Building Docker image ==="
echo "Image: ${IMAGE_NAME}:${TAG}"
echo "Branch: ${BRANCH_NAME}"

# Build the image
docker build -t "${IMAGE_NAME}:${TAG}" .

# Also tag with commit hash for traceability
if [ -n "$BUILD_VCS_NUMBER" ]; then
    SHORT_HASH=$(echo "$BUILD_VCS_NUMBER" | cut -c1-7)
    docker tag "${IMAGE_NAME}:${TAG}" "${IMAGE_NAME}:${SHORT_HASH}"
    echo "Also tagged as: ${IMAGE_NAME}:${SHORT_HASH}"
fi

# Push to DockerHub only for dev and prod branches
if [[ "$TAG" == "dev" || "$TAG" == "prod" ]]; then
    echo "=== Logging into DockerHub ==="
    echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

    echo "=== Pushing to DockerHub ==="
    docker push "${IMAGE_NAME}:${TAG}"
    
    if [ -n "$SHORT_HASH" ]; then
        docker push "${IMAGE_NAME}:${SHORT_HASH}"
    fi

    # If prod, also push as latest
    if [[ "$TAG" == "prod" ]]; then
        docker tag "${IMAGE_NAME}:${TAG}" "${IMAGE_NAME}:latest"
        docker push "${IMAGE_NAME}:latest"
        echo "Also pushed as: ${IMAGE_NAME}:latest"
    fi

    echo "=== Push complete ==="
else
    echo "=== Branch '${TAG}' - build only, no push ==="
fi

echo "=== Done ==="
