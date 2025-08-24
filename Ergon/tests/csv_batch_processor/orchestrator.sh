#!/bin/bash
# CSV Batch Processing Orchestrator
# Manages daily 100GB CSV processing pipeline

set -e

# Configuration
INPUT_DIR="${INPUT_DIR:-/data/input}"
PROCESSED_DIR="${PROCESSED_DIR:-/data/processed}"
LOG_DIR="${LOG_DIR:-/var/log/csv_processor}"
PARALLEL_JOBS="${PARALLEL_JOBS:-3}"

# Create directories
mkdir -p "$LOG_DIR" "$PROCESSED_DIR"

# Logging setup
LOG_FILE="$LOG_DIR/processor_$(date +%Y%m%d_%H%M%S).log"
exec 1> >(tee -a "$LOG_FILE")
exec 2>&1

echo "=========================================="
echo "CSV Batch Processor - Starting"
echo "Time: $(date)"
echo "Input: $INPUT_DIR"
echo "=========================================="

# Function to process a single CSV file
process_file() {
    local file="$1"
    local filename=$(basename "$file")
    
    echo "[$(date +%H:%M:%S)] Processing: $filename ($(du -h "$file" | cut -f1))"
    
    # Run the processor
    if python processor.py "$file"; then
        echo "[$(date +%H:%M:%S)] Success: $filename"
        # Move to processed directory
        mv "$file" "$PROCESSED_DIR/$filename.$(date +%Y%m%d_%H%M%S)"
        return 0
    else
        echo "[$(date +%H:%M:%S)] Error: Failed to process $filename"
        return 1
    fi
}

export -f process_file

# Check for CSV files
CSV_FILES=("$INPUT_DIR"/*.csv)

if [ ! -e "${CSV_FILES[0]}" ]; then
    echo "No CSV files found in $INPUT_DIR"
    exit 0
fi

echo "Found ${#CSV_FILES[@]} CSV files to process"
echo "Total size: $(du -sh "$INPUT_DIR" | cut -f1)"

# Process files in parallel
echo "Starting parallel processing (max $PARALLEL_JOBS jobs)..."

# Use GNU parallel if available, otherwise use background jobs
if command -v parallel &> /dev/null; then
    parallel -j "$PARALLEL_JOBS" process_file ::: "${CSV_FILES[@]}"
else
    # Fallback to background jobs
    job_count=0
    for file in "${CSV_FILES[@]}"; do
        process_file "$file" &
        
        job_count=$((job_count + 1))
        if [ $job_count -ge $PARALLEL_JOBS ]; then
            wait -n  # Wait for any job to finish
            job_count=$((job_count - 1))
        fi
    done
    
    # Wait for remaining jobs
    wait
fi

# Summary report
echo "=========================================="
echo "Processing Complete"
echo "Time: $(date)"
echo "Processed files moved to: $PROCESSED_DIR"
echo "Log file: $LOG_FILE"

# Check for any remaining files (errors)
REMAINING_FILES=("$INPUT_DIR"/*.csv)
if [ -e "${REMAINING_FILES[0]}" ]; then
    echo "WARNING: ${#REMAINING_FILES[@]} files were not processed successfully"
    for file in "${REMAINING_FILES[@]}"; do
        echo "  - $(basename "$file")"
    done
else
    echo "All files processed successfully!"
fi

echo "=========================================="