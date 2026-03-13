#!/bin/bash
set -e

echo "=== Running Django tests (SQLite) ==="
export USE_SQLITE=1
export SECRET_KEY='test-secret-key'

python3 manage.py test rooms --verbosity=2

echo "=== All tests passed ==="
