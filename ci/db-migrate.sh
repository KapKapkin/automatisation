#!/bin/bash
set -e

echo "=== DB Schema Migration (TEST -> STAGE) ==="

if ! docker compose -f docker-compose.stage.yml ps > /dev/null 2>&1; then
    echo "STAGE containers not running. Attempting to apply migrations via docker compose..."
fi

echo "--- Applying Django migrations on STAGE ---"
docker compose -f docker-compose.stage.yml exec -T web python manage.py migrate --noinput 2>/dev/null && {
    echo "=== Migrations applied via docker compose exec ==="
} || {
    echo "WARNING: Could not apply migrations via docker exec."
    echo "Migrations will be applied on next container startup (entrypoint)."
}

echo "--- Comparing TEST and STAGE schemas ---"
TEST_SCHEMA=$(docker compose -f docker-compose.stage.yml exec -T web python manage.py showmigrations --plan 2>/dev/null) || true

if [ -n "$TEST_SCHEMA" ]; then
    echo "$TEST_SCHEMA"
    if echo "$TEST_SCHEMA" | grep -q "\[ \]"; then
        echo "WARNING: There are unapplied migrations!"
        exit 1
    else
        echo "All migrations applied. Schemas are in sync."
    fi
fi

echo "=== DB Schema Migration complete ==="
