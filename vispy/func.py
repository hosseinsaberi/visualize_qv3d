import glob
import os
import re

# ////////////////////////////////////////////////////////////////
def find_files_in_directory(directory, pattern):
    # Ensure the directory exists
    if not os.path.isdir(directory):
        print(f"Error: The directory '{directory}' does not exist.")
        return []

    # Construct the search pattern
    search_pattern = os.path.join(directory, pattern)
    
    # Use glob to find all matching files
    matching_files = glob.glob(search_pattern)

    # Function to extract the numerical part of 'vs*' in the filename
    def extract_number_from_vs(filename):
        # Extract the part after 'vs' using regex (e.g., vs1, vs10, vs100)
        # Try matching with both patterns
        match_vs = re.search(r'vs(\d+)', filename)
        match_v3d = re.search(r'v3d_synchrotron_(\d+)', filename)
        if match_vs:
            return int(match_vs.group(1)) if match_vs else float('inf')  # Return inf if no number is found
        elif match_v3d:
            return int(match_v3d.group(1)) if match_v3d else float('inf')  # Return inf if no number is found

    # Sort using the custom key based on the numerical part after 'vs'
    sorted_files = sorted(matching_files, key=extract_number_from_vs)

    return sorted_files
    

# ////////////////////////////////////////////////////////////////
def find_folders_with_pattern(directory, pattern):
    """
    Search for folders matching a given pattern in a directory and save their paths.

    Args:
        directory (str): The root directory to search.
        pattern (str): The pattern to match folder names (e.g., 'density*').
    """
    # Use glob to search for folders matching the pattern
    # Add '*/' to match directories specifically
    search_pattern = os.path.join(directory, pattern + "*/")
    matching_folders = glob.glob(search_pattern)

    # Sort the list of folders using the sort_by_last_numeric function
    sorted_folders = sorted(matching_folders, key=lambda x: float(x.rstrip('\\/').split('-')[-1]))

    return sorted_folders

