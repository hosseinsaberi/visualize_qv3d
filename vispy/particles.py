from scipy.constants import pi
import pandas as pd
from scipy.constants import pi, e, hbar, m_e, c, epsilon_0


def calculateBeamParameters(phase, wmg, stdev_g, W, em_y, em_z, lamdap):
    kp = 2*pi/lamdap
    position = phase/kp     # [m]
    charge=W*1.609e-19  # [C]
    energy=wmg*5.11e5   # [eV]
    energySpread = 100*stdev_g/wmg  # [%]
    emittance = (em_y*em_z)**0.5
    return position, energy, energySpread, charge, emittance


def beamParameters_inSingleRun(csvFile):
    # Load the DataFrame from a CSV file
    df = pd.read_csv(csvFile)
    #print(df.head(10))
    #keys = df.columns.tolist()
    #print(keys)

    wavelength = df['lamdap'][0] * 0.01 # wavlenght in metere
    wavelength = float(wavelength)
    wp = 2*pi*c/wavelength
    kp = wp/c
    n0 = wp**2 * epsilon_0 * m_e / e**2

    E_WB = c*m_e*wp/e # wavebreaking field
    

    #print('Plasma Density [/cm3] = ', f"{n0/1e6:.2e}")
    #print('Wavebreaking field [GV/m] = ', f"{E_WB:.2f}")

    position, energy, energySpread, charge, emittance = calculateBeamParameters(df['phase'], df['wmg'], df['stdev_g'], df['W'], \
                                                                            df['em_y'], df['em_z'], wavelength)

    # Create a dictionary with the arrays
    BeamParameters = {
        'position [cm]': position*100,
        'energy [MeV]': energy/1e6,
        'energySpread [%]': energySpread,
        'charge [pC]':charge/1e-12,
        'emittance [mm-mrad]':emittance  
    }

    # Create the DataFrame
    beam_df = pd.DataFrame(BeamParameters)

    # Display the first few rows of the DataFrame
    #print(beam_df.head(10))
    keys = beam_df.columns.tolist()
    #print(keys)
    return beam_df, keys, n0/1e6, E_WB/1e9, wavelength*100
