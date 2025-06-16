#!/bin/bash
# Migration script for Prometheus to use GlobalConfig and StandardComponentBase

echo "Migrating Prometheus to GlobalConfig pattern..."

# Backup current app.py
if [ -f "prometheus/api/app.py" ]; then
    cp prometheus/api/app.py prometheus/api/app_old.py
    echo "✓ Backed up current app.py to app_old.py"
fi

# Replace app.py with new version
if [ -f "prometheus/api/app_new.py" ]; then
    mv prometheus/api/app_new.py prometheus/api/app.py
    echo "✓ Replaced app.py with GlobalConfig version"
else
    echo "✗ Error: app_new.py not found"
    exit 1
fi

echo ""
echo "Migration complete! Please test by running:"
echo "  python -m prometheus"
echo ""
echo "If there are issues, restore the old version with:"
echo "  cp prometheus/api/app_old.py prometheus/api/app.py"