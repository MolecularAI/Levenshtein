import glob
import os
import sys
import pandas as pd
import numpy as np
import h5py
import shutil


class CollateClass:

    def __init__(self, dest_path, file_name):
        """
        This class aggregates seperate files of the same 
        extension into a master file.
        """

        # Initialize field attributes
        self.dest_path = dest_path
        self.file_name = file_name
        self.data_name = file_name.split('.')[0]
        self.dest_path_to_build = None

    def __build_directory(self, folder_name):
        """
        Clears the previous files in dest_path and re-creates the 
        directory structure when called. This keeps the directory clean from previous augmentaion runs.
        """

        # Remove the directory recurssively
        self.dest_path_to_build = self.dest_path + '/' + \
            self.data_name + folder_name

        if os.path.exists(self.dest_path_to_build) == True:
            shutil.rmtree(self.dest_path_to_build)
            os.mkdir(self.dest_path_to_build)

        else:
            # Reset/rebiuld directory
            os.mkdir(self.dest_path_to_build)
        print(self.dest_path_to_build)

    def collate_to_pandas(self, randomize='normal', include_original=False, verbose_level=0):
        # Pull in all csv files from file dump directory

        if os.path.exists('../file_dumps/collated_pandas_data /') == False:
            os.mkdir('../file_dumps/collated_pandas_data/')

        if randomize == "normal":
            rand_type = '_normal_collated.csv'
        else:
            rand_type = '_levenshtein_collated.csv'

        df_list = []
        for filename in glob.glob('../file_dumps/' + self.data_name + '/*.csv'):
            if "normal" in filename or "levenshtein" in filename:
                with open(filename) as pd_file:
                    data = pd.read_csv(pd_file, header=None)
                    df_list.append(data)

        # # Append all df's to original file
        # if include_original:
        #     origin = pd.read_csv('../data/' + self.file_name)
        #     df_list.append(origin)

        record = pd.concat(df_list, sort=False, ignore_index=True, axis=0)
        record.reset_index(drop=True, inplace=True)
        record.to_csv('../file_dumps/collated_pandas_data/' +
                      self.data_name + rand_type, index=False, header=None)
        if verbose_level == 1:
            print(np.shape(record))

    def collate_to_hdf5(self, randomize='normal'):
        opts = ['normal', 'levenshtein']

        if randomize not in opts:
            print("Please enter a valid randomization type: %s" % opts)

        if randomize == 'normal':
            rand_type = '_normal_collated.h5'

        elif randomize == 'levenshtein':
            rand_type = '_levenshtein_collated.h5'

        self.__build_directory('/collated_h5_data')
        dest_h5 = h5py.File(
            self.dest_path_to_build + '/' + self.data_name + rand_type, 'w')
        print("Creating directory:", self.dest_path_to_build)
        counter = 0

        for filename in glob.glob(
                '../file_dumps/' + self.data_name + '/*.h5'):

            # Open all h5 files in read mode
            h5 = h5py.File(filename, 'r')

            # Copy all groups in h5 to destination h5 and rename keys
            for gn in h5:
                h5.copy(gn, dest_h5, name='obs_' + str(counter))
                counter += 1

    def convert_hdf5_to_pandas(self, randomize='normal'):
        opts = ['normal', 'levenshtein']
        if randomize not in opts:
            print("Please enter a valid randomization type: %s" % opts)
        if randomize == 'normal':
            rand_type = '_normal_collated'

        elif randomize == 'levenshtein':
            rand_type = '_levenshtein_collated'

        print("Converting H5 file to pandas dataframe...")
        f = h5py.File(self.dest_path_to_build + '/' +
                      self.data_name + rand_type + '.h5', 'r+')

        # Instantiate DataFrame with first group of H5 file
        frame_pr = pd.DataFrame(f['obs_0']['target'][()])
        frame_re = pd.DataFrame(f['obs_0']['source'][()])

        # Add all of the groups to each df
        for i, gn in enumerate(f):
            print(gn)
            if gn != 'obs_0':
                products = pd.DataFrame(f[gn]['target'][()])
                reactants = pd.DataFrame(f[gn]['source'][()])
                frame_pr = frame_pr.append(products)
                frame_re = frame_re.append(reactants)

        # Concatenate the two dataframes (['products', 'reactants'])
        frame_pr.reset_index(inplace=True, drop=True)
        frame_re.reset_index(inplace=True, drop=True)

        master = pd.concat((frame_re, frame_pr), axis=1)
        master.reset_index(inplace=True, drop=True)
        master.columns = ['source', 'target']
        self.__build_directory('/collated_pandas_data')
        print("Creating directory:", self.dest_path_to_build)
        master.to_csv(self.dest_path_to_build + '/' +
                      self.data_name + rand_type + '.csv', index=False)
        print("Done.")
