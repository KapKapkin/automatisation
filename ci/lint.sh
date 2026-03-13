#!/bin/bash
set -e

echo "=== Installing dependencies ==="
pip install -r requirements.txt --quiet

echo "=== Running flake8 (code quality analysis) ==="
echo "Checking for BLOCKER-level issues (E9, F63, F7, F82)..."

flake8 . --count --select=E9,F63,F7,F82 --show-source --statistics

if [ $? -eq 0 ]; then
    echo "=== No BLOCKER issues found ==="
else
    echo "=== BLOCKER issues detected! Build FAILED ==="
    exit 1
fi

echo ""
echo "=== flake8 warnings (non-blocking) ==="
flake8 . --count --exit-zero --max-line-length=120 --statistics || true

echo "=== Lint check passed ==="
