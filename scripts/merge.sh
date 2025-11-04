#!/bin/bash
# Simple wrapper script for merging data files

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$( cd "$SCRIPT_DIR/.." && pwd )"

# Change to project root
cd "$PROJECT_ROOT"

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}================================${NC}"
echo -e "${BLUE}  Superconductor Data Merger${NC}"
echo -e "${BLUE}================================${NC}"
echo ""

# Run the merge script
python3 scripts/merge_data.py "$@"

# Check if successful
if [ $? -eq 0 ]; then
    echo ""
    echo -e "${GREEN}✓ Merge completed successfully!${NC}"
    echo ""
    echo "You can find the merged file in: data/raw/merged_documents_*.json"
else
    echo ""
    echo -e "${RED}✗ Merge failed. Check the error messages above.${NC}"
    exit 1
fi
