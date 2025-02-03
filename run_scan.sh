#!/bin/bash

# Script to execute 'from_particles_data.py' and 'from_synchrotron_data.py' 
# with one command-line arguments

# Check if exactly two arguments are provided
if [ "$#" -ne 2 ]; then
    echo "Usage: $0 <scan_directory> <which-machine [scarf]>"
    echo "Error: This script requires exactly two arguments."
    exit 1  # Exit with an error code
fi

# Store arguments in variables for clarity
scan_directory="$1"

cd h5data_process

if [ "$2" = 'scarf' ]; then
    sbatch run_onecpu_on_scarf.sh "$scan_directory" 
else 
    python from_particles_data.py "$scan_directory" Scan
    python from_synchrotron_data.py "$scan_directory" scan
fi
