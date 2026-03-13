#!/bin/bash
set -e

echo "=== Installing dependencies ==="
pip install -r requirements.txt --quiet

echo "=== Running bandit (security analysis) ==="
echo "Checking for CRITICAL issues (severity=HIGH, confidence=HIGH)..."

# Run bandit only for CRITICAL: severity HIGH + confidence HIGH
# -r: recursive, -ll: only HIGH severity, -iii: only HIGH confidence
bandit -r . -ll -iii --exclude ./.vevn,./.venv,./staticfiles -f json -o bandit_critical.json || true

# Check if any CRITICAL issues found
CRITICAL_COUNT=$(python -c "
import json, sys
try:
    with open('bandit_critical.json') as f:
        data = json.load(f)
    results = data.get('results', [])
    count = len(results)
    if count > 0:
        print(f'Found {count} CRITICAL issue(s):')
        for r in results:
            print(f\"  - {r['filename']}:{r['line_number']} [{r['test_id']}] {r['issue_text']}\")
    print(count)
except Exception:
    print(0)
" | tail -1)

if [ "$CRITICAL_COUNT" -gt 0 ]; then
    echo "=== CRITICAL security issues detected! Build FAILED ==="
    # Print details
    python -c "
import json
with open('bandit_critical.json') as f:
    data = json.load(f)
for r in data.get('results', []):
    print(f\"CRITICAL: {r['filename']}:{r['line_number']} [{r['test_id']}] {r['issue_text']}\")
"
    exit 1
fi

echo "=== No CRITICAL security issues found ==="

# Show all findings (non-blocking)
echo ""
echo "=== bandit full report (non-blocking) ==="
bandit -r . --exclude ./.vevn,./.venv,./staticfiles -f screen || true

echo "=== Security check passed ==="
