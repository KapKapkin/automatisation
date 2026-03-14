#!/bin/bash
set -e

IMAGE_NAME="${DOCKER_USERNAME}/automatisation-web"

# Только prod ветка
if [[ "$BRANCH_NAME" != "refs/heads/main" && "$BRANCH_NAME" != "refs/heads/prod" && "$BRANCH_NAME" != "main" && "$BRANCH_NAME" != "prod" ]]; then
    echo "=== Branch '${BRANCH_NAME}' - skip PROD deploy ==="
    exit 0
fi

TAG="prod"

echo "=== Deploying ${IMAGE_NAME}:${TAG} to PROD ==="

echo "$DOCKER_PASSWORD" | docker login -u "$DOCKER_USERNAME" --password-stdin

# 1. Резервное копирование БД перед развертыванием
echo "=== Step 1: Backup PROD database ==="
export PROD_DB_HOST="${PROD_DB_HOST:-db}"
export PROD_DB_PORT="${PROD_DB_PORT:-5432}"
export PROD_DB_NAME="${PROD_DB_NAME:-university_db}"
export PROD_DB_USER="${PROD_DB_USER:-postgres}"
export PROD_DB_PASSWORD="${PROD_DB_PASSWORD:-postgres}"
export BACKUP_DIR="${BACKUP_DIR:-/backups}"

# Запускаем бэкап через контейнер БД (если он запущен)
docker compose -f docker-compose.prod.yml exec -T db \
    bash -c 'pg_dump -U postgres university_db | gzip > /backups/db_backup_$(date +%Y%m%d_%H%M%S).sql.gz' 2>/dev/null || {
    echo "WARNING: Could not backup via docker exec, trying direct connection..."
    bash ci/db-backup.sh || echo "WARNING: Backup failed, proceeding with deployment"
}

echo "=== Backup complete ==="

# 2. Подтянуть новый образ
echo "=== Step 2: Pull new image ==="
docker pull "${IMAGE_NAME}:${TAG}"

export DOCKER_USERNAME="${DOCKER_USERNAME}"
export DEPLOY_TAG="${TAG}"

# 3. Перезапустить приложение
echo "=== Step 3: Deploy application ==="
docker compose -f docker-compose.prod.yml down --remove-orphans 2>/dev/null || true
docker compose -f docker-compose.prod.yml up -d

echo "=== Waiting for application to start ==="
sleep 10

# 4. Применить миграции (схема от STAGE -> PROD)
echo "=== Step 4: Apply DB migrations ==="
docker compose -f docker-compose.prod.yml exec -T web python manage.py migrate --noinput || {
    echo "WARNING: Could not run migrations via exec, they should run on startup"
}

# 5. Проверить запуск
if docker compose -f docker-compose.prod.yml ps | grep -q "Up"; then
    echo "=== PROD Deploy successful! Application is running ==="
    docker compose -f docker-compose.prod.yml ps
else
    echo "=== PROD Deploy FAILED ==="
    docker compose -f docker-compose.prod.yml logs --tail=20
    exit 1
fi
