import glob
from augment_classes.augmentation.scripts.collate_class import CollateClass
import pandas as pd
import numpy as np
import h5py
import sys

"""
Scipt to collate all augmentatinos into either H5 or CSV formats.
Command line interface not currently supported.
"""
# Grab dataset name from terminal
TERMINAL = True
if TERMINAL:
    # Specify how many args you want to call, e.g. datafile, ** params
    print("Running with command line parameters")
    args = sys.argv[1:]
    if len(args) < 2:
        raise Exception("Please provide 2 arguments: [-filname, -method ]  e.g. *.csv normal") 
    
    file_name = args[0]
    method = args[1] if args[1] else 'normal'  # levenshtein or normal
else:
    print("Falling back to example run")
    file_name = 'test_file.csv'
    method = 'normal'

dest_path = '../file_dumps'
data_name = file_name.split('.')[0]

# Call collate class
collator = CollateClass(dest_path=dest_path, file_name=file_name)

# By default this is set to collate to pandas for speed
collator.collate_to_pandas(randomize=method)
