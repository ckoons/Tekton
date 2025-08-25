#!/bin/bash
# Simple one-liner to replace " CI " with " CI " in all README.md files

# Create backup first
echo "Creating backup..."
tar -czf readme_backup_$(date +%Y%m%d_%H%M%S).tar.gz $(find . -name "README.md" -type f 2>/dev/null)

# Perform replacement
echo "Replacing ' CI ' with ' CI ' in all README.md files..."
find . -name "README.md" -type f -exec sed -i '' 's/ CI / CI /g' {} \;

echo "Done! Backup saved as readme_backup_*.tar.gz"
echo "Use 'git diff' to review changes"