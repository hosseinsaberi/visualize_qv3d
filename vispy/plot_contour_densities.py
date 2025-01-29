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
import h5py
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.colors import Normalize, LogNorm
from matplotlib.colors import LinearSegmentedColormap
from from_input_deck import extract_plasma_wavelength
E_WB = 1
def create_custom_cmap(color):
    # Create a color map that goes from transparent to the specified color
    # The gradient is defined as: (0, 0, 0, 0) -> (color with full opacity)
    cmap = LinearSegmentedColormap.from_list("custom_cmap", [(1, 1, 1, 0), color], N=256)
    return cmap
    
def plot_densities(filename):

    # Open the HDF5 file
    # ##################
    try:
        mframe_file = h5py.File(filename, 'r')
        print(f"file = {filename}")
    except IOError:
        sys.stderr.write(f"File does not exist:\n  {filename}\n")
        sys.exit(-1)
        
    # Read grid coordinates
    X = mframe_file["X"][:]
    Y = mframe_file["Y"][:]


    # Calculate plot limits
    Xmin = X[0] + 0.5 * (X[0] - X[1])
    Xmax = X[-1] + 0.5 * (X[-1] - X[-2])
    Ymin = Y[0] + 0.5 * (Y[0] - Y[1])
    Ymax = Y[-1] + 0.5 * (Y[-1] - Y[-2])


    # Custom cmap for proton bunch
    color = 'red'  # or any other color you want
    # Step 2: Create the custom colormap
    proton_cmap = create_custom_cmap(color)

    # Specify fields to plot
    fields = ["n0", "n1", "n2"]  
    cmaps = ["Greens", proton_cmap, "BuPu"]  # Set colormaps for densities


    # Create figure for plotting
    fig, ax = plt.subplots(figsize=(18, 10))  # Create a single subplot

    # Set the figure title
    fig.canvas.manager.set_window_title(f'{mframe_file} {2}')

    # Loop over the fields to create overlay plots
    for i, field in enumerate(fields):
        #data = np.transpose(file[field][:]) # Remove if the plot comes out sideways
        data = (mframe_file[field][:]) # Remove if the plot comes out sideways
    
        # Create a custom colormap
        cmap = plt.get_cmap(cmaps[i])
    
        # Normalize the data
        norm = Normalize(vmin=0, vmax=np.max(data))
    
        # Create a mask for low values (adjust threshold as necessary)
        low_value_mask = data < 0.005 * np.max(data)  # Mask values below 10% of the max
    
        # Create an RGBA array from the colormap
        rgba_data = cmap(norm(data))  # Apply the colormap
        rgba_data[low_value_mask, 3] = 0  # Set alpha channel to 0 for low values (transparent)
    
        # Plot the data using the RGBA array
        im = ax.imshow(rgba_data, extent=(Xmin, Xmax, Ymin, Ymax), aspect='auto', interpolation='nearest')

        # Add a color bar for the current field with its respective colormap
        # Move colour bars a little to the right to space them out more
        if i == 2:
            cbar = plt.colorbar(ScalarMappable(norm=norm, cmap=cmaps[i]), ax=ax, fraction=0.046, pad=0.14)
        else:
            cbar = plt.colorbar(ScalarMappable(norm=norm, cmap=cmaps[i]), ax=ax, fraction=0.046, pad=0.06)

    
        titles = [r"$n_{pe}/n_{0}$", r"$n_{bp}/n_{0}$", r"$n_{be}/n_{0}$"]
        cbar.set_label(titles[i], fontsize=18, labelpad=10)

     
    if field[0]=="n":
        #data = np.transpose(file[field][:]) # Remove if the plot comes out sideways
        # Plotting curves onto density map
        E_y_index = np.argmin(np.abs(Y))  # Finds the index of the closest value to y = 0
        Fy_y0_index = np.argmin(np.abs(Y-0.5951))  # Finds the index of the closest y = sigr = 0.0406 value 
        Ex_field = np.transpose(mframe_file["ex"])[:, E_y_index]
        Trans_field = np.transpose(mframe_file["ForceY"])[:, Fy_y0_index]
        X_array=X[:]
        ax2 = ax.twinx() # Field on right hand axis
        ax2.plot(X_array, Ex_field*E_WB, lw=3, color='tab:blue', label=r'Longitudinal E-field at $y=0$')
        #ax2.plot(X_array, 2*Trans_field*E_WB, lw=3, color='tab:red', label=r'Transverse Wakefield at $y = \sigma_{r}$')
        #ax2.set_ylabel(r"$E_{X}/E_{wb}, 10*W_{Y}/E_{wb}$", fontsize=20, labelpad=15)
        ax2.set_ylabel(r"$E_{X}/E_{wb}$", fontsize=20, labelpad=15)
        #ax2.set_ylim([-0.22, 0.22]) # Centres y-axis on 0 (hard coded)
        ax2.tick_params(axis='both', labelsize=15)
        ax2.legend(loc='lower center', frameon=False, fontsize=18)
    # Set limits for the axes
    ax.set_xlim(Xmin, Xmax)
    ax.set_ylim(Ymin, Ymax)
    ax.tick_params(axis='both', labelsize=15)


    # Set a title for the overall plot
    #ax.set_title(f"QV3D simulation of AWAKE Run 2 at " + str((int(third_arg)-1)*2) + "m", fontsize=22)
    ax.set_xlabel(r"$x k_{p}$", fontsize=20)
    ax.set_ylabel(r"$y k_{p}$", fontsize=20)

    plt.tight_layout()  # Adjust layout to prevent overlap

    # Save the plot as a PNG file with a fixed name followed by the 3rd argument value
    #output_filename = rf'C:\Users\jaspe\OneDrive - The University of Manchester\Documents\Physics\MPhys_Project\mphys_docs\Python_scripts\plots\overlay_field_plot_high_res_{third_arg}.png'
    plt.savefig('density_plot.png', format='png', dpi=300)  # Save at 300 DPI for high quality
    plt.savefig('density_plot.png', format='png', dpi=300)  # Save at 300 DPI for high quality

    mframe_file.close()




def main():
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 3:
        print("Usage: python plot_contour_densities.py <h5files_dir> <v2d_mframe_number>")
        sys.exit(1)

    # Access the input argument
    h5files_dir = sys.argv[1] 
    mframe_num = int(sys.argv[2])
    
    if mframe_num < 10:
        mframe_name = 'v2d_mframe_0000' + str(mframe_num) + '.h5'
    elif mframe_num < 100:
        mframe_name = 'v2d_mframe_000' + str(mframe_num) + '.h5'
    elif mframe_num < 1000:
        mframe_name = 'v2d_mframe_00' + str(mframe_num) + '.h5'
    else:
        print('ERROR: check the file_number.')
        
    mframe_file = os.path.join(h5files_dir, mframe_name)
    simulation_dir = os.path.dirname(h5files_dir)
    
    print(simulation_dir)    
    wavelength = extract_plasma_wavelength(simulation_dir)

    print(wavelength)
    plot_densities(mframe_file)


if __name__ == "__main__":
    main()
