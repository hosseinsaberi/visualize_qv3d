"""
Description:
------------
	This script contains functions to extract data from v.ini file

Created: January 22, 2025
--------

Usage:
------
    import and use functions in other scripts
"""
# import libraries
# ################
import os
import re
import sys

def find_input_deck(directory):
    """
    Finds *.ini files in the specified directory.
    Raises an error if more than one .ini file is found.
    
    Args:
        directory (str): The directory to search.
        
    Returns:
        str: The full path of the .ini file if exactly one is found.
    """
    try:
        # Check if directory exists
        if not os.path.exists(directory):
            raise FileNotFoundError(f"The directory '{directory}' does not exist.")
        
        # Find all .ini files in the directory
        ini_files = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith('.ini')]

        # Check the number of .ini files
        if len(ini_files) > 1:
            raise RuntimeError(f"Error: Found more than one .ini file in '{directory}': {ini_files}")
        elif len(ini_files) == 0:
            raise FileNotFoundError(f"No .ini files found in '{directory}'.")
        else:
            return ini_files[0]

    except Exception as e:
        print(f"An error occurred: {e}")
        sys.exit(1)

# ////////////////////////////////////////////////////////////////////////
def extract_plasma_wavelength(directory):
    """
    Extracts the value of 'Wavelength' from input deck.
    
    Args:
        file_path (str): Path to the file.
        
    Returns:
        float: The value of 'Wavelength' if found.
    """
    input_deck_path = find_input_deck(directory)    
    try:
        # Open and read the file
        with open(input_deck_path, 'r') as file:
            content = file.read()
        
        # Use regex to find the value of Wavelength
        match = re.search(r'Wavelength\s*=\s*([\d.eE+-]+)', content)
        if match:
            wavelength_value = float(match.group(1))  # Convert to float
            return wavelength_value
        else:
            raise ValueError("Wavelength not found in the file.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        return None

# ////////////////////////////////////////////////////////////////////////
def find_SkipSaveFlag(directory, species):
    input_deck_path = find_input_deck(directory)
    try:
        with open(input_deck_path, 'r') as file:
            lines = file.readlines()

        current_species = None
        skip_save_flag = "Not Found"  # Default value if not found

        for line in lines:
            stripped_line = line.strip()

            # Check if the line starts with &Specie1
            if stripped_line.startswith(species):
                current_species = species
            
            # If inside &Specie1 block and SkipSaveFlag is found
            if current_species == species and "SkipSaveFlag" in stripped_line:
                parts = stripped_line.split('=')
                if len(parts) > 1:
                    value = parts[1].split('#')[0].strip()  # Get value before comment
                    skip_save_flag = value  # Store the value of SkipSaveFlag
                break  # Exit once we find SkipSaveFlag for Specie1
            
        # Print the result
        if skip_save_flag != "Not Found":
            #print(f"{species}: SkipSaveFlag = {skip_save_flag}")
            return skip_save_flag
        else:
            #print("{species} not found or SkipSaveFlag not found.")
            return -1

    except FileNotFoundError:
        print(f"Error: File '{file_path}' not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

