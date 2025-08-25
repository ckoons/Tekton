#!/bin/bash
# Script to replace " CIs" with " CIs" in all files recursively
# This handles the plural form of AI/CI

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting CIs to CIs conversion...${NC}"
echo "----------------------------------------"

# Counter for tracking changes
TOTAL_FILES=0
MODIFIED_FILES=0

# Create backup directory with timestamp
BACKUP_DIR="backup_ais_to_cis_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}Backup directory created: $BACKUP_DIR${NC}"
echo "----------------------------------------"

# Find all files (excluding .git, backups, and binary files)
find . -type f \
    -not -path "*/\.git/*" \
    -not -path "*/backup_*/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
    -not -path "*/\.pyc" \
    -not -name "*.pyc" \
    -not -name "*.jpg" \
    -not -name "*.jpeg" \
    -not -name "*.png" \
    -not -name "*.gif" \
    -not -name "*.ico" \
    -not -name "*.pdf" \
    -not -name "*.zip" \
    -not -name "*.tar" \
    -not -name "*.gz" \
    -not -name "*.db" \
    -not -name "*.sqlite" \
    | while read -r file; do
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # Check if file contains " CIs" (with space before, s after)
    if grep -q " CIs" "$file" 2>/dev/null; then
        # Create backup
        backup_path="$BACKUP_DIR/${file#./}"
        mkdir -p "$(dirname "$backup_path")"
        cp "$file" "$backup_path"
        
        # Count occurrences before replacement
        count_before=$(grep -o " CIs" "$file" | wc -l | tr -d ' ')
        
        # Perform the replacement
        # Using word boundaries to ensure we only replace " CIs"
        sed -i.tmp 's/ CIs/ CIs/g' "$file"
        
        # Remove the temporary backup created by sed
        rm -f "${file}.tmp"
        
        MODIFIED_FILES=$((MODIFIED_FILES + 1))
        echo -e "${GREEN}✓${NC} Modified: $file (${count_before} replacements)"
    fi
done

echo "----------------------------------------"
echo -e "${GREEN}Conversion complete!${NC}"
echo "Files scanned: $TOTAL_FILES"
echo "Files modified: $MODIFIED_FILES"
echo -e "${YELLOW}Backups saved in: $BACKUP_DIR${NC}"

# Show a sample of changes
echo "----------------------------------------"
echo "Sample of changes (first 5 modified files):"
find . -type f -not -path "*/\.git/*" -not -path "*/backup_*/*" | head -20 | while read -r file; do
    # Show lines containing " CIs" (that were likely changed)
    if grep -q " CIs" "$file" 2>/dev/null; then
        echo -e "\n${YELLOW}$file:${NC}"
        grep " CIs" "$file" | head -2
    fi
done | head -15

echo "----------------------------------------"
echo -e "${GREEN}Script complete!${NC}"
echo ""
echo "To review changes, you can:"
echo "  1. Check the backup directory: $BACKUP_DIR"
echo "  2. Use git diff to see all changes"
echo "  3. Search for remaining ' CIs': grep -r ' CIs' . --exclude-dir=.git --exclude-dir=backup_*"
echo "  4. Restore from backup if needed: cp -r $BACKUP_DIR/* ."