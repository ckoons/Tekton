#!/bin/bash
# Comprehensive script to replace "AI " with "CI " in all cases:
# - At the beginning of lines: ^AI 
# - After non-alphabetic characters: [^a-zA-Z]AI 
# This preserves words like "OpenAI" and "MAINTAIN"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting comprehensive AI to CI conversion...${NC}"
echo "Patterns:"
echo "  1. Start of line: ^AI → CI"
echo "  2. Non-alpha prefix: [^a-zA-Z]AI → [^a-zA-Z]CI"
echo "----------------------------------------"

# Counter for tracking changes
TOTAL_FILES=0
MODIFIED_FILES=0
TOTAL_REPLACEMENTS=0

# Create backup directory with timestamp
BACKUP_DIR="backup_all_ai_to_ci_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}Backup directory created: $BACKUP_DIR${NC}"
echo "----------------------------------------"

# Find all text files (including MetaData, excluding binaries and backups)
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
    -not -name "*.so" \
    -not -name "*.dylib" \
    -not -name "*.dll" \
    | while read -r file; do
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # Check if file contains either pattern
    has_start_line=false
    has_nonalpha=false
    
    # Check for "AI " at start of line
    if grep -E '^AI ' "$file" 2>/dev/null >/dev/null; then
        has_start_line=true
    fi
    
    # Check for "AI " after non-alpha character
    if grep -E '[^a-zA-Z]AI ' "$file" 2>/dev/null >/dev/null; then
        has_nonalpha=true
    fi
    
    # Process file if it has either pattern
    if [ "$has_start_line" = true ] || [ "$has_nonalpha" = true ]; then
        # Create backup
        backup_path="$BACKUP_DIR/${file#./}"
        mkdir -p "$(dirname "$backup_path")"
        cp "$file" "$backup_path"
        
        # Count total occurrences before replacement
        count_start=$(grep -cE '^AI ' "$file" 2>/dev/null || echo 0)
        count_nonalpha=$(grep -oE '[^a-zA-Z]AI ' "$file" 2>/dev/null | wc -l | tr -d ' ')
        count_before=$((count_start + count_nonalpha))
        
        # Perform replacements
        # 1. Replace "AI " at the beginning of lines
        sed -i.tmp1 -E 's/^AI /CI /g' "$file"
        
        # 2. Replace "AI " after non-alphabetic characters
        sed -i.tmp2 -E 's/([^a-zA-Z])AI /\1CI /g' "$file"
        
        # Remove temporary backups created by sed
        rm -f "${file}.tmp1" "${file}.tmp2"
        
        if [ "$count_before" -gt "0" ]; then
            MODIFIED_FILES=$((MODIFIED_FILES + 1))
            TOTAL_REPLACEMENTS=$((TOTAL_REPLACEMENTS + count_before))
            echo -e "${GREEN}✓${NC} Modified: $file (${count_before} replacements)"
            
            # Show what types of replacements were made
            if [ "$has_start_line" = true ] && [ "$has_nonalpha" = true ]; then
                echo "    └─ Both start-of-line and non-alpha patterns"
            elif [ "$has_start_line" = true ]; then
                echo "    └─ Start-of-line patterns"
            else
                echo "    └─ Non-alpha prefix patterns"
            fi
        fi
    fi
done

echo "----------------------------------------"
echo -e "${GREEN}Conversion complete!${NC}"
echo "Files scanned: $TOTAL_FILES"
echo "Files modified: $MODIFIED_FILES"
echo "Total replacements: $TOTAL_REPLACEMENTS"
echo -e "${YELLOW}Backups saved in: $BACKUP_DIR${NC}"

# Show examples of changes
echo "----------------------------------------"
echo "Examples of changes made (first 10):"
echo ""

# Show some examples
count=0
find . -type f -not -path "*/\.git/*" -not -path "*/backup_*/*" 2>/dev/null | while read -r file; do
    if [ $count -ge 10 ]; then
        break
    fi
    
    # Check for "CI " patterns that were likely our changes
    if grep -E '(^CI |[^a-zA-Z]CI )' "$file" 2>/dev/null >/dev/null; then
        # Get one example line
        example_line=$(grep -E '(^CI |[^a-zA-Z]CI )' "$file" 2>/dev/null | head -1)
        if [ ! -z "$example_line" ]; then
            # Trim long lines
            if [ ${#example_line} -gt 80 ]; then
                example_line="${example_line:0:77}..."
            fi
            echo -e "${YELLOW}$file:${NC}"
            echo "  $example_line"
            count=$((count + 1))
        fi
    fi
done

echo ""
echo "----------------------------------------"
echo -e "${GREEN}Script complete!${NC}"
echo ""
echo "To review changes:"
echo "  1. Check the backup directory: $BACKUP_DIR"
echo "  2. Use git diff to see all changes"
echo "  3. Search for remaining 'AI ' patterns:"
echo "     grep -rE '(^AI |[^a-zA-Z]AI )' . --exclude-dir=.git --exclude-dir=backup_*"
echo "  4. Restore from backup if needed: cp -r $BACKUP_DIR/* ."