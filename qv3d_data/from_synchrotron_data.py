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
import pickle
import numpy as np
import scipy as sp
import pandas as pd
from scipy import integrate
from func import find_files_in_directory
from scipy.constants import pi, e, hbar, m_e, c, epsilon_0


# ///////////////////////////////////////////////////////////////////
def calcNphoton_Phi_Theta_Energy(S, S_norm, Energy, n_phi, n_theta, Nphoton_Phi_Theta_EnergyCritical):
    len_w = len_wc = len(Energy)
    Nphoton_Phi_Theta_Energy = np.zeros( (n_phi, n_theta, len_w) )

    for i in range(len_w):
        for j in range(len_wc):
            Nphoton_Phi_Theta_Energy[:,:,i] += S[i, j]*Nphoton_Phi_Theta_EnergyCritical[:, :, j] / S_norm[i]

    return Nphoton_Phi_Theta_Energy

# ///////////////////////////////////////////////////////////////////
def synchrotronSpectra(Synchrotron3D):
    # Synchrotron3D is a 3D array with photon numbers per 'Phi, Theta, Energy' as axes of (0, 1, 2)
    #N = np.transpose(M) # return to Energy,Theta,Phi; axes(0,1,2)
    Nphoton_Phi_Theta_Energy = Synchrotron3D
    Nphoton_Phi_Energy = np.sum(Nphoton_Phi_Theta_Energy, axis=1)
    Nphoton_Theta_Energy = np.sum(Nphoton_Phi_Theta_Energy, axis=0)
    Nphoton_Energy = np.sum(Nphoton_Phi_Energy, axis=0)
    Nphoton_Theta = np.sum(Nphoton_Theta_Energy, axis=1)
    Nphoton_Phi = np.sum(Nphoton_Phi_Energy, axis=1)
    return Nphoton_Phi_Theta_Energy, Nphoton_Phi_Energy, Nphoton_Theta_Energy, Nphoton_Energy, Nphoton_Phi, Nphoton_Theta

# ///////////////////////////////////////////////////////////////////
def getSynchrotronData(h5):
    with h5py.File(h5, 'r') as hf:
        #print(hf.keys())
        Synchrotron3D = np.array(hf.get('Synchrotron3D'))
        Energy = np.array(hf.get('Energy'))
        Theta = np.array(hf.get('Theta'))
        Phi = np.array(hf.get('Phi'))
        phase = np.array(hf.get('phase'))
    return Synchrotron3D, Energy, Theta, Phi, phase

# ///////////////////////////////////////////////////////////////////
def synchrotronFunction(Energy):
    w = Energy*e/hbar
    wc = w
    S_2d = np.zeros( (len(w), len(wc)) )
    S_norm_1d = np.zeros(len(w))
    
    for i in range( len(w) ):
        for j in range( len(wc) ):
            K53 = lambda x: sp.special.kv(5/3, x)
            w_wc = w[i] / wc[j]
            integral = integrate.quad(K53, w_wc, np.inf)
            S_2d[i, j] = w_wc * integral[0]
        #print('S {0:0.1f}% complete'.format(100*i/len(w)), end="\r")
    S_norm_1d = np.sum(S_2d, axis = 1)        
    return S_2d, S_norm_1d

# ///////////////////////////////////////////////////////////////////
def analyze_synch_files(file_path):
    h5 = file_path

    # Get synchrotron data
    Synchrotron3D, Energy, Theta, Phi, phase = getSynchrotronData(h5)

    # Universal function
    S, S_norm = synchrotronFunction(Energy)

    # Calculate Nphoton_Energy
    Synchrotron3D = calcNphoton_Phi_Theta_Energy(S, S_norm, Energy, len(Phi), len(Theta), Synchrotron3D)
    Nphoton_Phi_Theta_Energy, Nphoton_Phi_Energy, Nphoton_Theta_Energy, Nphoton_Energy, Nphoton_Phi, Nphoton_Theta = synchrotronSpectra(Synchrotron3D)

    crit_fac = 8./(15.*np.sqrt(3.)) # see P. Walker on Synchrotron
    criticalEnergy = np.average(Energy,weights=Nphoton_Energy)/crit_fac

    return criticalEnergy, Nphoton_Energy, Nphoton_Theta, Nphoton_Phi, Energy, Theta, Phi, phase

# ///////////////////////////////////////////////////////////////////
def main():
    # Check if the correct number of arguments are provided
    if len(sys.argv) != 2:
        print("Usage: python vs3d_particles_extract_beam_parameters.py <simulation_dir>")
        sys.exit(1)

    # Access the input argument
    simulation_dir = sys.argv[1]
    synch_files = find_files_in_directory(simulation_dir, "v3d_synchrotron_*")
    
    # last synchrotron file will be analyzed synch_files[-1]
    last_file_path = synch_files[-1]
    last_file_name = os.path.basename(last_file_path)
    print(last_file_name)
    
    
    criticalEnergys, \
    Nphotons_Energy, Nphotons_Theta, Nphotons_Phi, \
    Energy, Theta, Phi, phase \
    = analyze_synch_files(last_file_path)

    # Create a dictionary of the variables
    variables_dict = {
        'criticalEnergy': criticalEnergys,
        'Nphoton_Energy': Nphotons_Energy,
        'Nphoton_Theta': Nphotons_Theta,
        'Nphoton_Phi': Nphotons_Phi,
        'Energy': Energy,
        'Theta': Theta,
        'Phi': Phi,
        'phase': phase
        }
        
    # Save the DataFrame to a pkl file    
    output_synchrotron  = os.path.join(simulation_dir, 'synchrotron.pkl')
    with open(output_synchrotron, 'wb') as file:
        pickle.dump(variables_dict, file)

   
if __name__ == "__main__":
    main()
