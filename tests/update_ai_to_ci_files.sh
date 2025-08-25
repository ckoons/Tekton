#!/bin/bash
# Script to replace " CI " with " CI " in a specified list of files
# Usage: ./update_ai_to_ci_files.sh file1 file2 file3 ...
#    or: ./update_ai_to_ci_files.sh -f filelist.txt
#    or: cat filelist.txt | ./update_ai_to_ci_files.sh -

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Initialize counters
TOTAL_FILES=0
MODIFIED_FILES=0
SKIPPED_FILES=0
ERROR_FILES=0

# Create backup directory with timestamp
BACKUP_DIR="backup_ai_to_ci_$(date +%Y%m%d_%H%M%S)"
mkdir -p "$BACKUP_DIR"
echo -e "${YELLOW}Backup directory created: $BACKUP_DIR${NC}"
echo "----------------------------------------"

# Function to process a single file
process_file() {
    local file="$1"
    
    # Check if file exists
    if [[ ! -f "$file" ]]; then
        echo -e "${RED}✗${NC} File not found: $file"
        ERROR_FILES=$((ERROR_FILES + 1))
        return 1
    fi
    
    TOTAL_FILES=$((TOTAL_FILES + 1))
    
    # Check if file contains " CI " (with spaces on both sides)
    if grep -q " AI " "$file" 2>/dev/null; then
        # Create backup maintaining directory structure
        backup_path="$BACKUP_DIR/${file#./}"
        mkdir -p "$(dirname "$backup_path")"
        cp "$file" "$backup_path"
        
        # Count occurrences before replacement
        count_before=$(grep -o " AI " "$file" | wc -l | tr -d ' ')
        
        # Perform the replacement
        sed -i.tmp 's/ AI / CI /g' "$file"
        
        # Remove the temporary backup created by sed
        rm -f "${file}.tmp"
        
        MODIFIED_FILES=$((MODIFIED_FILES + 1))
        echo -e "${GREEN}✓${NC} Modified: $file (${count_before} replacements)"
    else
        SKIPPED_FILES=$((SKIPPED_FILES + 1))
        echo -e "${BLUE}○${NC} Skipped: $file (no ' CI ' found)"
    fi
}

# Main processing logic
echo -e "${GREEN}Starting AI to CI conversion in specified files...${NC}"
echo "----------------------------------------"

# Check how the script was called
if [[ $# -eq 0 ]]; then
    echo -e "${RED}Error: No files specified${NC}"
    echo "Usage: $0 file1 file2 file3 ..."
    echo "   or: $0 -f filelist.txt"
    echo "   or: cat filelist.txt | $0 -"
    exit 1
fi

# Process based on input method
if [[ "$1" == "-f" ]]; then
    # Read from file list
    if [[ -z "$2" ]]; then
        echo -e "${RED}Error: No file list specified after -f${NC}"
        exit 1
    fi
    
    if [[ ! -f "$2" ]]; then
        echo -e "${RED}Error: File list '$2' not found${NC}"
        exit 1
    fi
    
    echo -e "${YELLOW}Reading files from: $2${NC}"
    echo "----------------------------------------"
    
    while IFS= read -r file; do
        # Skip empty lines and comments
        [[ -z "$file" || "$file" == \#* ]] && continue
        process_file "$file"
    done < "$2"
    
elif [[ "$1" == "-" ]]; then
    # Read from stdin
    echo -e "${YELLOW}Reading files from stdin...${NC}"
    echo "----------------------------------------"
    
    while IFS= read -r file; do
        # Skip empty lines and comments
        [[ -z "$file" || "$file" == \#* ]] && continue
        process_file "$file"
    done
    
else
    # Process command line arguments as filenames
    echo -e "${YELLOW}Processing ${#} files from command line...${NC}"
    echo "----------------------------------------"
    
    for file in "$@"; do
        process_file "$file"
    done
fi

# Final summary
echo "----------------------------------------"
echo -e "${GREEN}Conversion complete!${NC}"
echo "Total files processed: $TOTAL_FILES"
echo "Files modified: $MODIFIED_FILES"
echo "Files skipped: $SKIPPED_FILES"
if [[ $ERROR_FILES -gt 0 ]]; then
    echo -e "${RED}Files with errors: $ERROR_FILES${NC}"
fi
echo -e "${YELLOW}Backups saved in: $BACKUP_DIR${NC}"

echo ""
echo "To review changes:"
echo "  1. Check the backup directory: $BACKUP_DIR"
echo "  2. Use git diff to see all changes"
echo "  3. Restore from backup if needed: cp -r $BACKUP_DIR/* ."

# Exit with error if any files had errors
exit $([[ $ERROR_FILES -eq 0 ]] && echo 0 || echo 1)
