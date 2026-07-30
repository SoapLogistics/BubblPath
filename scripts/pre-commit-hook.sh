#!/bin/sh
# Solomon SOSS Pre-Commit Verification Hook
# Standardizes quality assurance and blocks invalid formats before pushing upstream.

echo "🔍 Running Pre-Commit Style and Quality Checks..."

# 1. Run lint check
python3 scripts/solomon_dx.py lint
if [ $? -ne 0 ]; then
    echo "❌ Linting/formatting failed. Run 'python3 scripts/solomon_dx.py format' and retry."
    exit 1
fi

# 2. Run repository consistency check
python3 scripts/solomon_dx.py consistency-check
if [ $? -ne 0 ]; then
    echo "❌ Repository consistency scan failed."
    exit 1
fi

echo "✅ All checks passed successfully. Proceeding with commit."
exit 0
