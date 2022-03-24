#%%
import os
import pandas as pd
import numpy as np

from configobj import ConfigObj
config = ConfigObj('config.INI')

n_partitions = int(config["n_partitions"])
scratch_path = config["scratch_path"]
datafile = config["datafile"]
sep = config["separator"]
#%%
data = pd.read_csv(datafile, sep=sep)
partitions = np.array_split(data, n_partitions)

# %%
save_path = scratch_path + "/partitions"
if not os.path.exists(save_path):
    os.makedirs(save_path)

#TODO index saved as Unnamed
for i in range(len(partitions)):
    df = partitions[i]
    df.to_csv(save_path + "/data_p%05d.csv"%i, index=False)

#Save unaugmented for reference
#train_data.to_csv(scratch_path + "/cleaned_data.csv")
print("Splits done")

#%%
log_path = scratch_path + "logs"
if not os.path.exists(log_path):
    os.makedirs(log_path)

# %%
