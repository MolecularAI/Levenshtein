#%% imports
import pandas as pd
import sys, os, copy

from levenshteinaugment.levenshtein import Levenshtein_augment

#Supress warnings from RDKit
from rdkit import rdBase
rdBase.DisableLog('rdApp.error')
rdBase.DisableLog('rdApp.warning')

from configobj import ConfigObj
config = ConfigObj('config.INI')

n_partitions = int(config["n_partitions"])
scratch_path = config["scratch_path"]
number_augmentations = int(config["number_augmentations"])
randomization_tries = int(config["randomization_tries"])
input_column = config["input_column"]
output_column = config["output_column"]

# %%
partition = int(sys.argv[1])
#partition = 1 #for testing
print("Running JobID %i"%partition)
sys.stdout.flush()

partition_path = scratch_path + "/partitions"

#TODO keep the preassigned "set column"
data = pd.read_csv(partition_path + "/data_p%05d.csv"%partition)


#%% Levenshtein augment data
augmenter = Levenshtein_augment(source_augmentation=number_augmentations, randomization_tries=randomization_tries)

#%%
data_collectors = []
for i in range(number_augmentations):
     data_collectors.append([])

# for i in range(number_augmentations):
#     data_collectors.append({
#         "reaction_hash":[],
#         "products":[],
#         "reactants":[],
#         "Levenshtein_distance":[],
#     })

#%% 
for i, row in data.iterrows():
    pairs = augmenter.levenshtein_pairing(row[input_column], row[output_column])
    augmentations = augmenter.sample_pairs(pairs)
    # %% Sort into different augmentation files
    for i, pair in enumerate(augmentations):
        new_row = copy.deepcopy(row)
        new_row[input_column] = pair[0]
        new_row[output_column] = pair[1]
        new_row["Levenshtein_distance"] = pair[2]
        data_collectors[i].append(new_row)

print("Levenshtein augmented data")

#%% Save files in augmentation directories
for i, collector in enumerate(data_collectors):
    df = pd.DataFrame(collector)

    #Save in directories for easier handling in shell scripts
    savepath = scratch_path + "/augmentations/%03d/"%i
    if not os.path.exists(savepath):
        os.makedirs(savepath)
    
    df.to_csv(savepath + "/data_p%05d_aug%03d.csv"%(partition, i), header=False, index=False)

# %% TODO save headers (is this dangerous to)
if partition == 0:
    df[:0].to_csv(scratch_path + "/augmentations/headers.csv", index=False)

#%% For reference if cleaned

# scratch_cleaned_path = path + "/cleaned_partitions/"
# scratch_if not os.path.exists(cleaned_path):
#     os.mkdir(cleaned_path)
# data.to_csv(cleaned_path + "/data_clean_p%05d.csv"%partition)
# print("Saved data")

