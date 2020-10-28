import pandas as pd 
import numpy as np
from os import listdir
from itertools import combinations  
from scipy.signal import find_peaks 
from sklearn.preprocessing import MinMaxScaler 

import config
from file_io import read
from normalise import normalise_spectrums

def search(bound_file_path, unbound_file_path, compounds_file_path):

    bound_df, unbound_df, compounds = read(bound_file_path, unbound_file_path, compounds_file_path)

    #extract information about Ub and the other compounds
    other_compounds_df = compounds[compounds.Name != config.protein] #extract all compounds but Ub
    protein_df = compounds[compounds.Name == config.protein] #extract Ub information

    #Perform peak detection
    #scale spectrums between 0 and 1
    unbound_df, bound_df = normalise_spectrums(unbound_df, bound_df)

    #find peaks 
    peaks = peak_find(bound_df)

    #create theoretical binding site list
    binding_df = create_binding_list(other_compounds_df, protein_df)

    #filter list using max value
    max_binding_mass = np.max(binding_df["Mass"]) #maximum possible mass from all theoretical binding sites
    peaks_filtered = peaks[peaks["m/z"] < max_binding_mass] #remove incorrect peaks

    #match peaks to theoretical list
    



