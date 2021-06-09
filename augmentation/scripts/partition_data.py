from augment_classes.augmentation.scripts.sub_process_class import SubProcessClass
import pandas as pd
import sys


"""
Script is called from command line,
splits pandas datframe into chunks for multi CPU usage and sends to augment_data.sh
"""

# Grab dataset name from terminal
TERMINAL = True
if TERMINAL:
    args = sys.argv[1:]
    if len(args) < 3:
        raise Exception("Please provide 3 arguments: [filname, method, chunk_size]  e.g. *.csv normal 1000") 
    file_name = args[0]
    method = args[1]
    chunk_size = int(args[2])
else:
    # Debug
    file_name = 'test_canonical.csv'
    method = 'normal'
    chunk_size = 1000


sub_process = SubProcessClass(file_name=file_name,
                              method=method,
                              save_path='../file_dumps',
                              chunk_size=chunk_size)

sub_process.submit_sub_process(bash_file_name='augment_data.sh')
