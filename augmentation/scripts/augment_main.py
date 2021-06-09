from augment_classes.augmentation.scripts.augment_class import AugmentClass
import numpy as np
import sys

# Set TERMINAL to true if you want to use command line
TERMINAL = True
if TERMINAL:
    args = sys.argv[1:]
    save_path = args[0]
    directory = args[1]
    method = args[2]
    chunk_id = args[3]
else:
    # Example for testing
    save_path = '../file_dumps/'
    directory = "test_canonical/test_canonical_chunk_1_partition_0.csv"
    chunk_id = '0'
    method = 'normal'

# Get file name
data_name = directory.replace('.csv', '')
augment_save_path = save_path + data_name + '_' + method + '.csv'

# Instantiate AugmentClass object
aug = AugmentClass(save_path+directory)

# Run randomization
perms = aug.randomize(
    n_perms=10, save_path=augment_save_path, chunk_id=chunk_id, method=method, mode='pandas')
