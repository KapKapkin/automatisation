#!/bin/bash
set -e

echo "=== SQL Security & Quality Check (sqlfluff) ==="

# Проверяем наличие SQL-файлов в директории db_schema/
SQL_FILES=$(find db_schema/ -name "*.sql" -type f 2>/dev/null)

if [ -z "$SQL_FILES" ]; then
    echo "No SQL files found in db_schema/ — skipping SQL check."
    echo "=== SQL check skipped (no files) ==="
    exit 0
fi

echo "Found SQL files:"
echo "$SQL_FILES"
echo ""

# Запуск sqlfluff lint для проверки SQL-файлов
echo "--- Running sqlfluff lint ---"
LINT_EXIT=0
python3 -m sqlfluff lint db_schema/ --dialect postgres 2>&1 || LINT_EXIT=$?

if [ "$LINT_EXIT" -gt 1 ]; then
    echo "=== CRITICAL SQL issues detected! Build FAILED ==="
    exit 1
fi

if [ "$LINT_EXIT" -eq 1 ]; then
    echo ""
    echo "--- sqlfluff found warnings (non-blocking) ---"
fi

echo ""
echo "=== SQL security check passed ==="
