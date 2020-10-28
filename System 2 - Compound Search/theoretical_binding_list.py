import pandas as pd
import numpy as np
from itertools import combinations  
from tqdm import tqdm

import config


def create_binding_list(other_compounds_df, protein_df):

   #create binding list
    #binding list contains bonded compound and masses
    binding_df = pd.DataFrame([])
    number_of_compounds = other_compounds_df.shape[0]

    for k in tqdm(range(1, number_of_compounds+1)):

        #how many ways can you select k items from a list of n (where n=number of compounds, k=length of combinations)
        #use ID's as from ID's we can extract the masses and compound names
        combs = combinations(other_compounds_df.ID,k)
        #combs gives you the compounds to be bonded together

        #create binding elements and total masses
        for bonded_compound_ids in combs:
            unbounded_molecule_formula = protein_df["Formula"].values[0].translate(config.SUB) #Base Ub symbol
            unbounded_molecule_mass = protein_df["Mass"].values[0] #Base Ub mass

            if len(bonded_compound_ids) == 1:
                idx = bonded_compound_ids[0]

                molecule = other_compounds_df.loc[other_compounds_df.ID == idx, "Formula"].values[0].translate(config.SUB)

                min_value = other_compounds_df.loc[other_compounds_df.ID == idx, "Min"].values[0]
                max_value = other_compounds_df.loc[other_compounds_df.ID == idx, "Max"].values[0]

                if min_value == 0:
                    min_value = 1
                tolerance_seq = list(range(min_value, max_value+1))

                if max_value > 0:
                    for multiplier in tolerance_seq:
                        
                        #single compound bonding 
                        permutation_of_molecule = "(" + molecule + ")" + str(multiplier).translate(config.SUB)
                        bonded_compound = unbounded_molecule_formula + " + " + permutation_of_molecule
                        total_mass = unbounded_molecule_mass + (other_compounds_df.loc[other_compounds_df.ID == idx, "Mass"].values[0]*multiplier)
            
                        binding_df = binding_df.append(
                            pd.DataFrame({"Formula":bonded_compound, "Mass":total_mass, "Level":1, "Combs": str(bonded_compound_ids)}, index=range(1)),
                            ignore_index=True)
                        
            else:
                #if more than 1 molecule is being considered
                level = len(bonded_compound_ids)
                prev_level = level - 1
                compounds_considered_at_prev_level = bonded_compound_ids[:-1]
                compound_to_be_considered = bonded_compound_ids[-1]
                
                max_value = other_compounds_df.loc[other_compounds_df.ID == compound_to_be_considered, "Max"].values[0]
                min_value = other_compounds_df.loc[other_compounds_df.ID == compound_to_be_considered, "Min"].values[0]
                molecule = other_compounds_df.loc[other_compounds_df.ID == compound_to_be_considered, "Formula"].values[0].translate(config.SUB)
                molecule_mass = other_compounds_df.loc[other_compounds_df.ID == compound_to_be_considered, "Mass"].values[0]

                if min_value == 0:
                    min_value = 1
                tolerance_seq = list(range(min_value, max_value+1))

                #extract previous level
                search = binding_df[(binding_df["Level"] == prev_level) & (binding_df["Combs"] == str(compounds_considered_at_prev_level))]
                
                for row_idx in search.index:
                    bounded_compound_formula = search.loc[row_idx, "Formula"]
                    bounded_compound_mass = search.loc[row_idx, "Mass"]

                    if max_value > 0:
                        for multiplier in tolerance_seq:
                            permutation_of_molecule = "(" + molecule + ")" + str(multiplier).translate(config.SUB)
                            bonded_compound = bounded_compound_formula + " + " + permutation_of_molecule
                            total_mass = bounded_compound_mass + (molecule_mass*multiplier)
                
                            binding_df = binding_df.append(
                                pd.DataFrame({"Formula":bonded_compound, "Mass":total_mass, "Level":level, "Combs": str(bonded_compound_ids)}, index=range(1)),
                                    ignore_index=True)

    binding_df.index = range(binding_df.shape[0])
    
    return binding_df