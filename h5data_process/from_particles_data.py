"""
Description:
------------
	This script processes a single v2d_mframe_*.h5 file,
	extarcts and calculates densities and wakefields.

Created: January 22, 2025
--------

Usage:
------
    $ python plot_contour_densities.py <h5files_dir> <v2d_mframe_number> 
"""
# import libraries
# ################
import os
import sys
import subprocess
import pandas as pd
from from_input_deck import find_SkipSaveFlag
from func import find_files_in_directory
from func import find_folders_with_pattern

# ///////////////////////////////////////////////////////////////////
def getParameters(str_values):
    # Split the string into a list of numbers
    parameters = str_values.split()

    # Convert each element to integer (optional)
    parameters = [float(num) for num in parameters]
    phase = parameters[0]
    wmy =  parameters[1]
    wmz = parameters[2]
    wmvy = parameters[3]
    wmvz = parameters[4]
    stdev_y = parameters[5]
    stdev_z = parameters[6]
    stdev_vy = parameters[7]
    stdev_vz = parameters[8]
    em_y = parameters[9]
    em_z = parameters[10]
    wmg = parameters[11]       # gamma
    stdev_g = parameters[12]   # Dgamma
    N = parameters[13]
    W = parameters[14]         # calculate charge
    lamdap = parameters[15]/100    # [cm]

    emittance = (em_y*em_z)**0.5
    return phase, wmg, stdev_g, W, lamdap, emittance, lamdap

# ///////////////////////////////////////////////////////////////////
def calculateParameters(phase,wmg,stdev_g,W,lamdap):
    kp = 2*pi/lamdap
    dist = phase/kp     # [m]
    charge=W*1.609e-19  # [C]
    energy=wmg*5.11e5   # [eV]
    energySpread = 100*stdev_g/wmg  # [%]
    return energy, energySpread, dist, charge

# ///////////////////////////////////////////////////////////////////
def convert_text_to_csv(input_file, output_file):
    """
    Convert a text file containing space-separated numerical data to a CSV file.
    
    Args:
        input_file (str): Path to the input text file.
        output_file (str): Path to save the output CSV file.
    """
    try:
        # Read the text file and process it line by line
        with open(input_file, "r") as file:
            # Read all lines and split each line into a list of floats
            data = [[float(value) for value in line.split()] for line in file]

        # Create a pandas DataFrame from the list of data
        # Generate column names automatically
        column_names = [f"Column_{i+1}" for i in range(len(data[0]))]
        df = pd.DataFrame(data, columns=column_names)

        # Save the DataFrame to a CSV file
        df.to_csv(output_file, index=False)

        #print(f"Data has been successfully saved to {output_file}.")
    except Exception as e:
        print(f"An error occurred: {e}")

# ///////////////////////////////////////////////////////////////////
def extract_singleFile(simulation_dir, vs3d_particles_number):

    # Calculate driver beam parameters if available
    # #############################################
    driver_SkipSaveFlag = find_SkipSaveFlag(simulation_dir, '&Specie1')    
    driver_SkipSaveFlag = int(driver_SkipSaveFlag)
    output_driver  = os.path.join(simulation_dir, 'h5files', 'driver_parameters.txt')
    output_driver_csv  = os.path.join(simulation_dir, 'h5files', 'driver_parameters.csv')
    if driver_SkipSaveFlag == 0:
        # Define the command
        command = f"python em.py -ol {simulation_dir} {vs3d_particles_number} 1"

        # Open a text file to append the output
        with open(output_driver, "a") as output_file:
            try:
                # Execute the command and redirect the output to the file
                result = subprocess.run(command, shell=True, stdout=output_file, stderr=subprocess.STDOUT)

                if result.returncode != 0:
                   print(f"Command failed with return code {result.returncode}. Check 'output.txt' for details.")
            
            except Exception as e:
                print(f"An error occurred: {e}")
    
        convert_text_to_csv(output_driver, output_driver_csv)

    # Calculate witness beam parameters if available    
    # ##############################################
    witness_SkipSaveFlag = find_SkipSaveFlag(simulation_dir, '&Specie2')
    witness_SkipSaveFlag = int(witness_SkipSaveFlag)
    output_witness = os.path.join(simulation_dir, 'h5files', 'witness_parameters.txt')    
    output_witness_csv  = os.path.join(simulation_dir, 'h5files', 'witness_parameters.csv')
    if witness_SkipSaveFlag == 0:
        # Define the command
        command = f"python em.py -ol {simulation_dir} {vs3d_particles_number} 2"

        # Open a text file to append the output
        with open(output_witness, "a") as output_file:
            try:
                # Execute the command and redirect the output to the file
                result = subprocess.run(command, shell=True, stdout=output_file, stderr=subprocess.STDOUT)

                if result.returncode != 0:
                   print(f"Command failed with return code {result.returncode}. Check 'output.txt' for details.")
            
            except Exception as e:
                print(f"An error occurred: {e}")
         
        convert_text_to_csv(output_witness, output_witness_csv)
         
# ///////////////////////////////////////////////////////////////////        
def extract_AllFiles_singleRun(simulation_dir):
    h5files_path = os.path.join(simulation_dir, 'h5files')
    matching_files = find_files_in_directory(h5files_path, "*_3d_particles.h5")
    file_num = 0
    for h5 in matching_files:
        file_num = file_num + 1
        extract_singleFile(simulation_dir, file_num)
        os.remove(h5)


# ///////////////////////////////////////////////////////////////////
def extract_AllFiles_scan(simulation_dir, pattern):
    simulation_scan_folders = find_folders_with_pattern(simulation_dir, pattern)
    #print(simulation_scan_folders)
    for sim_dir in simulation_scan_folders:
        extract_AllFiles_singleRun(sim_dir)
    
    
# ///////////////////////////////////////////////////////////////////
def main():
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python vs3d_particles_extract_beam_parameters.py <simulation_dir> <vs3d_particles_number/AllFiles/Scan>")
        print("It is assumed that species 1 is driver and species 2 is witness")
        sys.exit(1)

    # Access the input argument
    simulation_dir = sys.argv[1]
    if sys.argv[2] == 'Scan':
        # if it is plasma density scan
        extract_AllFiles_scan(simulation_dir, 'density')
        
    elif sys.argv[2] == 'AllFiles':
        extract_AllFiles_singleRun(simulation_dir)

    else:
        vs3d_particles_number = int(sys.argv[2])
        extract_singleFile(simulation_dir, vs3d_particles_number)      
    
if __name__ == "__main__":
    main()
