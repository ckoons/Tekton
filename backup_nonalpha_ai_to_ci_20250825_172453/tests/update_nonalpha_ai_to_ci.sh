#!/bin/bash
# Script to replace "AI " with "CI " when AI is preceded by a non-alphabetic character
# This catches patterns like " AI ", "[AI ", "(AI ", "-AI ", etc.
# But preserves words like "OpenAI " or "MAINTAIN "

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting AI to CI conversion (non-alpha prefix pattern)...${NC}"
echo "Pattern: [^a-zA-Z]AI → [^a-zA-Z]CI"
echo "----------------------------------------"

# Counter for tracking changes
TOTAL_FILES=0
MODIFIED_FILES=0
TOTAL_REPLACEMENTS=0

# Create backup directory with timestamp
BACKUP_DIR="backup_nonalpha_ai_to_ci_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}Backup directory created: $BACKUP_DIR${NC}"
echo "----------------------------------------"

# Find all text files (excluding binaries and backups)
find . -type f \
    -not -path "*/\.git/*" \
    -not -path "*/backup_*/*" \
    -not -path "*/node_modules/*" \
    -not -path "*/__pycache__/*" \
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
    
    # Check if file contains the pattern (non-alpha char followed by "AI ")
    # Using grep -E for extended regex
    if grep -E '[^a-zA-Z]AI ' "$file" 2>/dev/null >/dev/null; then
        # Create backup
        backup_path="$BACKUP_DIR/${file#./}"
        mkdir -p "$(dirname "$backup_path")"
        cp "$file" "$backup_path"
        
        # Count occurrences before replacement
        count_before=$(grep -oE '[^a-zA-Z]AI ' "$file" 2>/dev/null | wc -l | tr -d ' ')
        
        # Perform the replacement using sed with extended regex
        # \1 captures the non-alpha character and preserves it
        sed -i.tmp -E 's/([^a-zA-Z])AI /\1CI /g' "$file"
        
        # Also handle beginning of line case (where there's no preceding character)
        sed -i.tmp2 -E 's/^AI /CI /' "$file"
        
        # Remove the temporary backups created by sed
        rm -f "${file}.tmp" "${file}.tmp2"
        
        if [ "$count_before" -gt "0" ]; then
            MODIFIED_FILES=$((MODIFIED_FILES + 1))
            TOTAL_REPLACEMENTS=$((TOTAL_REPLACEMENTS + count_before))
            echo -e "${GREEN}✓${NC} Modified: $file (${count_before} replacements)"
        fi
    fi
done

echo "----------------------------------------"
echo -e "${GREEN}Conversion complete!${NC}"
echo "Files scanned: $TOTAL_FILES"
echo "Files modified: $MODIFIED_FILES"
echo "Total replacements: $TOTAL_REPLACEMENTS"
echo -e "${YELLOW}Backups saved in: $BACKUP_DIR${NC}"

# Show examples of what was changed
echo "----------------------------------------"
echo "Examples of changes made:"
echo ""

# Find some example changes to show
count=0
find . -type f -not -path "*/\.git/*" -not -path "*/backup_*/*" 2>/dev/null | while read -r file; do
    if [ $count -ge 5 ]; then
        break
    fi
    
    # Check if this file now has "CI " patterns that likely came from our changes
    if grep -E '[^a-zA-Z]CI ' "$file" 2>/dev/null >/dev/null; then
        # Show one example from this file
        example=$(grep -E '[^a-zA-Z]CI ' "$file" 2>/dev/null | head -1)
        if [ ! -z "$example" ]; then
            echo -e "${YELLOW}$file:${NC}"
            echo "  $example"
            echo ""
            count=$((count + 1))
        fi
    fi
done

echo "----------------------------------------"
echo -e "${GREEN}Script complete!${NC}"
echo ""
echo "To review changes:"
echo "  1. Check the backup directory: $BACKUP_DIR"
echo "  2. Use git diff to see all changes"
echo "  3. Search for remaining patterns: grep -rE '[^a-zA-Z]AI ' . --exclude-dir=.git --exclude-dir=backup_*"
echo "  4. Restore from backup if needed: cp -r $BACKUP_DIR/* ."