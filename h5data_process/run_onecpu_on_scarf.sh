#!/bin/bash

# Check if exactly two arguments are provided
if [ "$#" -ne 1 ]; then
    echo "Usage: $0 <scan_directory>"
    echo "Error: This script requires exactly one arguments."
    exit 1  # Exit with an error code
fi


# Standard output and error:
#SBATCH -o output-%j.out
#SBATCH -e std-%j.err

# Initial working directory:
#SBATCH -D ./

# Job Name:
#SBATCH -J qv3d

# Queue (Partition):
#SBATCH -p scarf
#SBATCH -n 1
#SBATCH --cpus-per-task=1    # Number of CPUs per task (useful for tasks that are not parallelized and do not require multiple cores.)

# Wall clock limit:
###SBATCH --time=01:00:00  # Example: 1 hour
#SBATCH --time=05:00:00  # Example: 3 days



# Run the program:
# ###############
scan_directory="$1"
python from_particles_data.py "$scan_directory" Scan
python from_synchrotron_data.py "$scan_directory" scan

