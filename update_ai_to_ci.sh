#!/bin/bash
# Script to replace " AI " with " CI " in all README.md files recursively
# This preserves words like "OpenAI" and "MAINTAIN" by only replacing isolated " AI "

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI to CI conversion in README.md files...${NC}"
echo "----------------------------------------"

# Counter for tracking changes
TOTAL_FILES=0
MODIFIED_FILES=0

# Create backup directory with timestamp
BACKUP_DIR="backup_ai_to_ci_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}Backup directory created: $BACKUP_DIR${NC}"
echo "----------------------------------------"

# Find all README.md files and process them
find . -name "README.md" -type f | while read -r file; do
    # Skip backup directories and .git
    if [[ "$file" == *"/backup_"* ]] || [[ "$file" == *"/.git/"* ]]; then
        continue
    fi
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # Check if file contains " AI " (with spaces on both sides)
    if grep -q " AI " "$file" 2>/dev/null; then
        # Create backup
        backup_path="$BACKUP_DIR/${file#./}"
        mkdir -p "$(dirname "$backup_path")"
        cp "$file" "$backup_path"
        
        # Count occurrences before replacement
        count_before=$(grep -o " AI " "$file" | wc -l)
        
        # Perform the replacement
        # Using word boundaries to ensure we only replace standalone " AI "
        sed -i.tmp 's/ AI / CI /g' "$file"
        
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

# Optional: Show a sample of changes
echo "----------------------------------------"
echo "Sample of changes (first 5 files):"
find . -name "README.md" -type f | head -5 | while read -r file; do
    if [[ "$file" == *"/backup_"* ]] || [[ "$file" == *"/.git/"* ]]; then
        continue
    fi
    
    # Show lines containing " CI " (that were likely changed)
    if grep -q " CI " "$file" 2>/dev/null; then
        echo -e "\n${YELLOW}$file:${NC}"
        grep " CI " "$file" | head -2
    fi
done

echo "----------------------------------------"
echo -e "${GREEN}Script complete!${NC}"
echo ""
echo "To review changes, you can:"
echo "  1. Check the backup directory: $BACKUP_DIR"
echo "  2. Use git diff to see all changes"
echo "  3. Restore from backup if needed: cp -r $BACKUP_DIR/* ."