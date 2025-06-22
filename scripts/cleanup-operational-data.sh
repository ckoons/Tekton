#!/usr/bin/env bash
#
# cleanup-operational-data.sh
# Simple script to clean up old operational data files
#

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEKTON_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"

# Source environment
source "$TEKTON_ROOT/scripts/utils/env_setup.sh"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Parse arguments
DRY_RUN=""
VERBOSE=""

while [[ $# -gt 0 ]]; do
    case $1 in
        --dry-run)
            DRY_RUN="--dry-run"
            shift
            ;;
        --verbose)
            VERBOSE="--verbose"
            shift
            ;;
        --help)
            echo "Usage: $0 [options]"
            echo ""
            echo "Options:"
            echo "  --dry-run    Show what would be deleted without actually deleting"
            echo "  --verbose    Enable verbose logging"
            echo "  --help       Show this help message"
            echo ""
            echo "Configuration:"
            echo "  Edit $TEKTON_ROOT/.env.tekton to configure retention periods"
            echo ""
            echo "Current settings:"
            echo "  TEKTON_DATA_RETENTION_DAYS: ${TEKTON_DATA_RETENTION_DAYS:-2}"
            echo "  TEKTON_LANDMARK_RETENTION_DAYS: ${TEKTON_LANDMARK_RETENTION_DAYS:-2}"
            echo "  TEKTON_REGISTRATION_RETENTION_DAYS: ${TEKTON_REGISTRATION_RETENTION_DAYS:-1}"
            echo "  TEKTON_MESSAGE_RETENTION_DAYS: ${TEKTON_MESSAGE_RETENTION_DAYS:-3}"
            echo "  TEKTON_CI_MEMORY_RETENTION_DAYS: ${TEKTON_CI_MEMORY_RETENTION_DAYS:-7}"
            exit 0
            ;;
        *)
            echo -e "${RED}Unknown option: $1${NC}"
            exit 1
            ;;
    esac
done

# Display what we're about to do
echo -e "${BLUE}=== Tekton Operational Data Cleanup ===${NC}"
echo -e "${BLUE}TEKTON_ROOT: $TEKTON_ROOT${NC}"
echo ""

if [[ -n "$DRY_RUN" ]]; then
    echo -e "${YELLOW}Running in DRY RUN mode - no files will be deleted${NC}"
else
    echo -e "${RED}WARNING: This will DELETE old operational data files!${NC}"
    echo -e "${RED}Files older than configured retention periods will be removed.${NC}"
    echo ""
    read -p "Are you sure you want to continue? (yes/no): " -r
    if [[ ! $REPLY =~ ^[Yy][Ee][Ss]$ ]]; then
        echo -e "${YELLOW}Cleanup cancelled${NC}"
        exit 0
    fi
fi

echo ""

# Run the cleanup
echo -e "${GREEN}Starting cleanup...${NC}"
python3 -m shared.utils.delete_old_operational_records $DRY_RUN $VERBOSE

# Check exit code
if [ $? -eq 0 ]; then
    echo -e "${GREEN}Cleanup completed successfully${NC}"
else
    echo -e "${RED}Cleanup completed with errors${NC}"
    exit 1
fi