#!/bin/bash

# Script to execute 'from_particles_data.py' and 'from_synchrotron_data.py' 
# with one command-line arguments

# Check if exactly two arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <scan_directory>"
    echo "Error: This script requires exactly one arguments."
    exit 1  # Exit with an error code
fi

# Store arguments in variables for clarity
scan_directory="$1"

cd h5data_process
# Execute the Python script with the provided arguments
#python from_particles_data.py "$scan_directory" Scan
python from_synchrotron_data.py "$scan_directory" scan

# End of script

