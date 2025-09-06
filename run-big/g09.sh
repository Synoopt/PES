#!/bin/bash

echo "Checking Gaussian version in the system..."

# Detect available Gaussian version
GAUSSIAN_CMD=""
GAUSSIAN_VERSION=""
GAUSS_SCRDIR=""

# Check if g16 is available
if command -v g16 >/dev/null 2>&1; then
    GAUSSIAN_CMD="g16"
    GAUSSIAN_VERSION="Gaussian 16"
    echo "Detected Gaussian 16 (g16)"
    
    # Get g16 installation path
    G16_PATH=$(which g16)
    echo "g16 path: $G16_PATH"
    
    # Try to automatically set GAUSS_SCRDIR
    if [ -n "$G16_PATH" ]; then
        # Common scratch directory locations
        possible_scratch_dirs=(
            "/tmp/gaussian_scratch"
            "/scratch/gaussian"
            "/home/$USER/gaussian/scratch"
            "/home/$USER/.gaussian/scratch"
            "/var/tmp/gaussian_scratch"
            "/tmp"
        )
        
        for dir in "${possible_scratch_dirs[@]}"; do
            if [ -d "$dir" ] || mkdir -p "$dir" 2>/dev/null; then
                if [ -w "$dir" ]; then
                    GAUSS_SCRDIR="$dir"
                    echo "GAUSS_SCRDIR set to: $GAUSS_SCRDIR"
                    break
                fi
            fi
        done
        
        # If still not found, use temporary directory
        if [ -z "$GAUSS_SCRDIR" ]; then
            GAUSS_SCRDIR="/tmp/gaussian_scratch_$$"
            mkdir -p "$GAUSS_SCRDIR"
            echo "Using temporary scratch directory: $GAUSS_SCRDIR"
        fi
    fi

# Check if g09 is available
elif command -v g09 >/dev/null 2>&1; then
    GAUSSIAN_CMD="g09"
    GAUSSIAN_VERSION="Gaussian 09"
    echo "Detected Gaussian 09 (g09)"
    
    # Get g09 installation path
    G09_PATH=$(which g09)
    echo "g09 path: $G09_PATH"
    
    # Try to automatically set GAUSS_SCRDIR
    if [ -n "$G09_PATH" ]; then
        # Common scratch directory locations
        possible_scratch_dirs=(
            "/tmp/gaussian_scratch"
            "/scratch/gaussian"
            "/home/$USER/gaussian/scratch"
            "/home/$USER/.gaussian/scratch"
            "/var/tmp/gaussian_scratch"
            "/tmp"
        )
        
        for dir in "${possible_scratch_dirs[@]}"; do
            if [ -d "$dir" ] || mkdir -p "$dir" 2>/dev/null; then
                if [ -w "$dir" ]; then
                    GAUSS_SCRDIR="$dir"
                    echo "GAUSS_SCRDIR set to: $GAUSS_SCRDIR"
                    break
                fi
            fi
        done
        
        # If still not found, use temporary directory
        if [ -z "$GAUSS_SCRDIR" ]; then
            GAUSS_SCRDIR="/tmp/gaussian_scratch_$$"
            mkdir -p "$GAUSS_SCRDIR"
            echo "Using temporary scratch directory: $GAUSS_SCRDIR"
        fi
    fi

# Check if g03 is available (old version)
elif command -v g03 >/dev/null 2>&1; then
    GAUSSIAN_CMD="g03"
    GAUSSIAN_VERSION="Gaussian 03"
    echo "Detected Gaussian 03 (g03)"
    
    # Get g03 installation path
    G03_PATH=$(which g03)
    echo "g03 path: $G03_PATH"
    
    # Set scratch directory
    GAUSS_SCRDIR="/tmp/gaussian_scratch_$$"
    mkdir -p "$GAUSS_SCRDIR"
    echo "Using temporary scratch directory: $GAUSS_SCRDIR"

else
    echo "Error: No Gaussian version detected!"
    echo "Please ensure Gaussian is installed and added to the PATH environment variable"
    echo "Supported versions: g16, g09, g03"
    exit 1
fi

# Set environment variables
export GAUSS_SCRDIR="$GAUSS_SCRDIR"
echo "Environment variables set:"
echo "   GAUSS_SCRDIR=$GAUSS_SCRDIR"
echo "   GAUSSIAN_CMD=$GAUSSIAN_CMD"
echo "   GAUSSIAN_VERSION=$GAUSSIAN_VERSION"

# Check scratch directory permissions
if [ ! -w "$GAUSS_SCRDIR" ]; then
    echo "Warning: scratch directory $GAUSS_SCRDIR is not writable"
    echo "Trying to fix permissions..."
    chmod 755 "$GAUSS_SCRDIR" 2>/dev/null || {
        echo "Error: Unable to fix scratch directory permissions, please set manually"
        exit 1
    }
fi

echo ""
echo "Starting Gaussian input file processing..."

# Count files
total_files=$(find . -name "*.gjf" | wc -l)
if [ $total_files -eq 0 ]; then
    echo "No .gjf files found!"
    echo "Please run generate_gaussian_input.py to generate input files"
    exit 1
fi

echo "Found $total_files input files"

# Counters
success_count=0
fail_count=0

# Process all input files
for input in */*/*.gjf
do
    if [ ! -f "$input" ]; then
        continue
    fi
    
    output="${input%.gjf}.out"
    
    echo "Processing: $input"
    
    # Check disk space
    disk_usage=$(df -h . | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$disk_usage" -gt 90 ]; then
        echo "Disk space low (${disk_usage}%), stopping"
        break
    fi
    
    # Check scratch space
    scratch_usage=$(df -h "$GAUSS_SCRDIR" | tail -1 | awk '{print $5}' | sed 's/%//')
    if [ "$scratch_usage" -gt 95 ]; then
        echo "Scratch directory space low (${scratch_usage}%), cleaning..."
        rm -rf "$GAUSS_SCRDIR"/* 2>/dev/null
        echo "Scratch directory cleaned"
    fi
    
    # Run Gaussian
    echo "Running $GAUSSIAN_VERSION..."
    start_time=$(date +%s)
    
    if $GAUSSIAN_CMD < "$input" > "$output" 2>&1
    then
        end_time=$(date +%s)
        duration=$((end_time - start_time))
        echo "Success (time: ${duration}s)"
        echo "Output file: $output"
        ((success_count++))
        
        if grep -q "Error\|ERROR\|error" "$output"; then
            echo "Warning: Errors found in output file"
        fi
    else
        echo "Failed"
        echo "Check output file: $output"
        ((fail_count++))
    fi
    
    echo ""
done

# Clean up temporary scratch directory
if [[ "$GAUSS_SCRDIR" == *"gaussian_scratch_$$"* ]]; then
    echo "Cleaning up temporary scratch directory..."
    rm -rf "$GAUSS_SCRDIR"
fi

# Summary
echo "============================================================"
echo "Processing complete! Summary:"
echo "   Success: $success_count files"
echo "   Failed: $fail_count files"
echo "   Total: $total_files files"
echo "   Version used: $GAUSSIAN_VERSION"
echo "   Scratch directory: $GAUSS_SCRDIR"
echo "============================================================"

if [ $fail_count -gt 0 ]; then
    echo "$fail_count files failed, please check the output files"
    exit 1
else
    echo "All files processed successfully!"
    exit 0
fi
