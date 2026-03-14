#!/bin/bash
set -e

echo "=== DB Schema Migration (TEST -> STAGE) ==="

# Переменные окружения для подключения к БД
TEST_DB_HOST="${TEST_DB_HOST:-localhost}"
TEST_DB_PORT="${TEST_DB_PORT:-5432}"
TEST_DB_NAME="${TEST_DB_NAME:-university_db}"
TEST_DB_USER="${TEST_DB_USER:-postgres}"
TEST_DB_PASSWORD="${TEST_DB_PASSWORD:-postgres}"

STAGE_DB_HOST="${STAGE_DB_HOST:-localhost}"
STAGE_DB_PORT="${STAGE_DB_PORT:-5433}"
STAGE_DB_NAME="${STAGE_DB_NAME:-university_db}"
STAGE_DB_USER="${STAGE_DB_USER:-postgres}"
STAGE_DB_PASSWORD="${STAGE_DB_PASSWORD:-postgres}"

# 1. Выгрузить схемы обеих БД
echo "--- Dumping TEST DB schema ---"
PGPASSWORD="$TEST_DB_PASSWORD" pg_dump \
    -h "$TEST_DB_HOST" -p "$TEST_DB_PORT" \
    -U "$TEST_DB_USER" -s "$TEST_DB_NAME" \
    --no-owner --no-privileges \
    > /tmp/test_schema.sql 2>/dev/null || {
        echo "WARNING: Could not dump TEST DB schema. Running Django migrate instead."
        USE_DJANGO_MIGRATE=1
    }

if [ "${USE_DJANGO_MIGRATE:-0}" = "1" ]; then
    echo "--- Applying migrations via Django on STAGE ---"
    export POSTGRES_HOST="$STAGE_DB_HOST"
    export POSTGRES_PORT="$STAGE_DB_PORT"
    export POSTGRES_DB="$STAGE_DB_NAME"
    export POSTGRES_USER="$STAGE_DB_USER"
    export POSTGRES_PASSWORD="$STAGE_DB_PASSWORD"
    python3 manage.py migrate --noinput
    echo "=== Django migrations applied to STAGE ==="
    exit 0
fi

echo "--- Dumping STAGE DB schema ---"
PGPASSWORD="$STAGE_DB_PASSWORD" pg_dump \
    -h "$STAGE_DB_HOST" -p "$STAGE_DB_PORT" \
    -U "$STAGE_DB_USER" -s "$STAGE_DB_NAME" \
    --no-owner --no-privileges \
    > /tmp/stage_schema.sql 2>/dev/null || true

# 2. Сравнить схемы
echo "--- Comparing schemas ---"
if diff -q /tmp/test_schema.sql /tmp/stage_schema.sql > /dev/null 2>&1; then
    echo "Schemas are identical. No migration needed."
else
    echo "Schema differences detected. Applying migrations to STAGE..."

    # Применяем миграции Django на STAGE
    export POSTGRES_HOST="$STAGE_DB_HOST"
    export POSTGRES_PORT="$STAGE_DB_PORT"
    export POSTGRES_DB="$STAGE_DB_NAME"
    export POSTGRES_USER="$STAGE_DB_USER"
    export POSTGRES_PASSWORD="$STAGE_DB_PASSWORD"

    python3 manage.py migrate --noinput

    echo "--- Verifying schema sync ---"
    PGPASSWORD="$STAGE_DB_PASSWORD" pg_dump \
        -h "$STAGE_DB_HOST" -p "$STAGE_DB_PORT" \
        -U "$STAGE_DB_USER" -s "$STAGE_DB_NAME" \
        --no-owner --no-privileges \
        > /tmp/stage_schema_after.sql 2>/dev/null

    if diff -q /tmp/test_schema.sql /tmp/stage_schema_after.sql > /dev/null 2>&1; then
        echo "Schemas are now identical."
    else
        echo "WARNING: Schemas still differ after migration. Review manually."
        diff /tmp/test_schema.sql /tmp/stage_schema_after.sql || true
    fi
fi

# 3. Обновить schema.sql в репозитории
echo "--- Updating db_schema/schema.sql ---"
cp /tmp/test_schema.sql db_schema/schema.sql 2>/dev/null || true

echo "=== DB Schema Migration complete ==="
