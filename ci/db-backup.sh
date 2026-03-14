#!/bin/bash
set -e

echo "=== DB Backup before PROD deployment ==="

PROD_DB_HOST="${PROD_DB_HOST:-localhost}"
PROD_DB_PORT="${PROD_DB_PORT:-5432}"
PROD_DB_NAME="${PROD_DB_NAME:-university_db}"
PROD_DB_USER="${PROD_DB_USER:-postgres}"
PROD_DB_PASSWORD="${PROD_DB_PASSWORD:-postgres}"

BACKUP_DIR="${BACKUP_DIR:-/backups}"
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
BACKUP_FILE="${BACKUP_DIR}/db_backup_${TIMESTAMP}.sql.gz"

mkdir -p "$BACKUP_DIR"

echo "--- Creating backup: ${BACKUP_FILE} ---"
PGPASSWORD="$PROD_DB_PASSWORD" pg_dump \
    -h "$PROD_DB_HOST" -p "$PROD_DB_PORT" \
    -U "$PROD_DB_USER" "$PROD_DB_NAME" \
    | gzip > "$BACKUP_FILE"

BACKUP_SIZE=$(du -h "$BACKUP_FILE" | cut -f1)
echo "--- Backup created: ${BACKUP_FILE} (${BACKUP_SIZE}) ---"

echo "--- Cleaning old backups (keeping last 10) ---"
ls -t "${BACKUP_DIR}"/db_backup_*.sql.gz 2>/dev/null | tail -n +11 | xargs rm -f 2>/dev/null || true

echo "=== DB Backup complete ==="
