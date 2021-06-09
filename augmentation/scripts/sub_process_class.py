import pandas as pd
import subprocess
import os
import sys
import shutil


# Work in progress


class SubProcessClass:

    def __init__(self, file_name, save_path, method, chunk_size=1000):
        """
        Class for generating n-cpu jobs in parallel for preprocessing large datasets.

        :param file_name: name of file to partition, including extention
        :type file_name: str
        :param save_path: path to save partitions to
        :type save_path: str
        :param method: randomization method ['normal', 'levenshtein']
        :type method: str
        :param chunk_size: max number of examples in a given partiton, defaults to 1000
        :type chunk_size: int, optional
        """

        # Initialize field attributes
        self.file_name = file_name
        self.method = method
        self.data_name = file_name.replace('.csv', '')
        self.save_path = save_path
        self.chunk_size = chunk_size
        self.chunk_dict = {}

    def __build_directory(self):
        """
        Remvoes the content of the provided directory and resets directory structure.
        """

        # Remove
        if os.path.exists(self.save_path + '/' + self.data_name) == True:
            shutil.rmtree(self.save_path + '/' + self.data_name)
            os.mkdir(self.save_path + '/' + self.data_name)
        # Reset
        else:
            os.mkdir(self.save_path + '/' + self.data_name)

    def __chunk_data(self):
        """
        Uses pandas iterator to chunk the data into smaller partitions. 
        """

        # Load data into dataframe chunks with pandas file iterator
        pandas_iterator = pd.read_csv(
            '../data/' + self.file_name, chunksize=self.chunk_size)
        self.pandas_iterator = pandas_iterator

    def __generate_record(self):
        """
        Creates a dictionary record of all of the chunk file names while saving each chunk to its
        respective path.
        """

        # Record dataframe chunks to pass to subprocess
        for i, chunk in enumerate(self.pandas_iterator):

            # Name chunk appropriately
            name = self.data_name + '_chunk_' + \
                str(len(chunk)) + "_partition_" + str(i)+'.csv'

            # Save chunks to path
            chunk.to_csv(self.save_path + '/' +
                         self.data_name + '/' + name, index=False)

            # Update record with chunk_id and path to chunk
            self.chunk_dict.update({"chunk_" + str(i): name})

    def __spawn_sub_process(self, bash_file_name):
        """
        Constructs the subprocess proceedure

        :param bash_file_name: bash file name to call
        :type bash_file_name: str
        """

        # Send each chunk to slurm script to run randomization process in paralle
        chunk_counter = 0
        for chunk_name, chunk_path in self.chunk_dict.items():

            print("Submitting chunk_" + chunk_name)
            command = ['sbatch', bash_file_name,
                       str(self.save_path) + '/',
                       str(self.data_name + '/' + str(chunk_path)),
                       str(self.method),
                       str(chunk_counter)]
            # Launch sup-processes
            output = subprocess.run(command, stderr=subprocess.STDOUT)
            # Increment chunk counter
            chunk_counter += 1

    def submit_sub_process(self, bash_file_name):
        """
        Executes the sub-process command with the field variables

        :param bash_file_name: bash file to call
        :type bash_file_name: str
        """

        self.__build_directory()
        self.__chunk_data()
        self.__generate_record()
        self.__spawn_sub_process(bash_file_name)
