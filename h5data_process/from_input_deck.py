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
def extract_value_from_input_deck(directory, key):
    """
    Extracts the value of a given key from the input deck.

    Args:
        directory (str): Path to the directory containing the input deck.
        key (str): The parameter name to search for (e.g., 'Wavelength').

    Returns:
        float: The value of the given key if found, otherwise None.
    """
    input_deck_path = find_input_deck(directory)    
    try:
        with open(input_deck_path, 'r') as file:
            content = file.read()
        
        # Generalized regex pattern to match the key and extract its value
        pattern = rf'{key}\s*=\s*([\d.eE+-]+)'
        match = re.search(pattern, content)
        
        if match:
            return float(match.group(1))  # Convert to float
        else:
            raise ValueError(f"{key} not found in the file.")
    
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

# ////////////////////////////////////////////////////////////////////////
def find_species_parameter(directory, species_name, parameter):
    """Find the value of a given parameter within a specified species block."""
    input_deck = find_input_deck(directory)
    if not input_deck:
        print('ERROR - No input deck has been found.')
        return None
    
    with open(input_deck, 'r') as file:
        lines = file.readlines()
    
    inside_species = False
    for line in lines:
        if line.strip().startswith(species_name):
            inside_species = True
        elif line.strip().startswith("&") and inside_species:
            break  # Exit the species block when another species starts
        elif inside_species and parameter in line:
            match = re.search(r'(\S+)\s*=\s*([\d.eE+-]+)', line)
            if match and match.group(1) == parameter:
                return match.group(2)
    
    return None