# Libraries
import Levenshtein as lv
from difflib import SequenceMatcher
import string
import random
import pandas as pd
import numpy as np
import rdkit
from rdkit import Chem
from torch import matmul, rand, sspaddmm
import pandas as pd
import numpy as np
import seaborn as sns
from multiprocessing import Pool
from tabulate import tabulate
import glob
import h5py
import os


class AugmentClass():

    def __init__(self, filename):
        """
        Class responsible for augmenting a dataset using uniform 
        randomization or levenshtein distance based randomization.

        :param filename: path to file
        :type filename: string

        """

        # Initialize field attributes
        self.filename = filename
        self.data = pd.read_csv(filename)

        # HDF5 file categoricals
        self.counter = 0
        self.group = "obs_"
        self.dataset = None
        self.string_dt = h5py.special_dtype(vlen=str)

        # Pre-define variables
        # Check self.data upper range: limit to small upper bound for testing.
        self.data = self.data.iloc[0:, :]
        self.products_pools = None
        self.reactant_pools = None
        self.top_idx = None
        self.f = None
        self.collection = []
        self.reactant_series = pd.Series([])
        self.product_series = pd.Series([])
        self.pandas = {'source': [], 'target': []}
        self.df = pd.DataFrame({'source': [], 'target': []})
        self.largest = 0

    def __pairwise(self, src, tgt, n_perms, top_n, randomize_src=True):
        """
        Computes Levenshtein similarity between a source SMILES
        string and a target SMILES string.

        :param src: SMILES string source
        :type src: string
        :param tgt: SMILES string target
        :type tgt: string
        :param n_perms: number of permutations  to compute
        :type n_perms: int
        :param top_n: return the top-n similarities
        :type top_n: int
        :return: [top matching reactant, top matching target]
        :rtype: [string, string]
        """

        # Compute the similarity of a source string to target using levenshtein distance
        scores, source, target = self.__levenshtein_rand(
            src, tgt, n_perms=n_perms, top_n=top_n, randomize_src=randomize_src)
        return source, target, scores

    def __get_components(self, values):
        """
        Function to split a pandas DataFrame of reaction SMILES strings
        into reactant component(s) and product component.

        :param values: DataFrame values where columns == ['source', 'target']
        :type values: numpy array
        :return: [reactantA, reatantB, product] or [reactant, product] is reaction set is singular
        :rtype: tuple
        """
        collections = []
        # Append Products
        source = values[0]
        target = values[1]
        collections.append(target)

        if '.' in source:
            splits = source.split('.')
            for split in splits:
                collections.append(split)
        else:
            collections.append(source)

        source_values = collections[1:]
        target_values = collections[0]

        # Clear cache
        collections = []
        return [target_values], source_values if len(source_values) > 1 else [source_values[0]]

    def __uniform_rand(self, SMILES, n_perms):
        """
        Randomizes canonical SMILES [n_perms] times

        :param SMILES: SMILES string 
        :type SMILES: string
        :param n_perms: number of times to permute
        :type n_perms: int
        :return: list of randomized src SMILES
        :rtype: list
        """

        # Generate molelcule from SMILES string
        mol = Chem.MolFromSmiles(SMILES)
        # Extract atom numbers
        ans = list(range(mol.GetNumAtoms()))
        randomizations = []

        while len(randomizations) < n_perms:
            print(randomization)
            # Permute atom ordering
            np.random.shuffle(ans)
            # Renumber atoms
            rmol = Chem.RenumberAtoms(mol, ans)
            # Convert random mol back to SMILES
            rSMILES = Chem.MolToSmiles(rmol, canonical=False)
            randomizations.append(rSMILES)
        return randomizations

    def __levenshtein_rand(self, src, tgt, n_perms, top_n, randomize_src=True):
        """
        This function takes in a source list [src] and a target list [tgt] of SMILES, it randomizes each element in [src] and [tgt] [n-perms]-times,
        if randomize_src == False, only [tgt] is randomized.
        Then a randomly selected [src]-variant (or [src] If randomize_src== False) is selected and the similarity to each [tgt]-vairnat is computed.
        Only the top-n similar SMILES are retained, along with their similarity ratio e.g. [ratio, src-variant, tgt-variant].

        :param src: source SMILES (singular)
        :type src: string
        :param tgt: target SMILES string (list)
        :type tgt: list of smil strings
        :param n_perms: number of times to permute src smile
        :type n_perms: int
        :param top_n: return the best n src-target matches
        :type top_n: int
        :param randomize_src: whether to randomize source SMILES string or not, defaults to True
        :type randomize_src: bool, optional
        :return: best_n list of [similarity _ratio, src, tgt]
        :rtype: [float, string, string]
        """

        # Generate n-unique permutations of the src SMILE
        lv_list = []
        # Generate random permutations of src or use original
        if randomize_src:
            r_SMILE_set = self.__uniform_rand(src, n_perms)
            r = np.random.randint(0, len(r_SMILE_set))
            smi = r_SMILE_set[r]
        else:
            smi = src

        # Randomize tgt
        p_SMILE_set = self.__uniform_rand(tgt, n_perms)

        # Put original sequence in permutation list
        # if include_self:
        #     r_SMILE_set.append(src)

        for i in range(0, len(p_SMILE_set)):
            ratio = lv.ratio(smi, p_SMILE_set[i])
            lv_list.append([ratio, smi, p_SMILE_set[i]])

        # Sort similarity scores and return top-n
        ranks = sorted(lv_list, key=lambda x: x[0], reverse=True)
        best_perms = ranks[:top_n][0]
        return best_perms

    def __define_h5_file_groups(self, save_path, chunk_id):
        """
        Defines h5 groups to save observations to for data augmentation 

        :param save_path: path to save h5 to
        :type save_path: str
        :param chunk_id: chunk counter
        :type chunk_id: int
        """

        # Pre_define all groups in H5 file
        self.f = h5py.File(save_path, 'w')
        for idx, row in enumerate(range(np.shape(self.data)[0])):
            self.f.create_group(self.group + chunk_id + '_' + str(idx))

    def __get_levenshtein_SMILES(self, chunk_id, save_path, n_perms, mode='pandas'):
        """
        Data augmentation using Levenshtein rand

        :param chunk_id: don't set manually, partition counter
        :type chunk_id: int
        :param save_path: path to save augmentated files to
        :type save_path: str
        :param n_perms: nuber of randomizations
        :type n_perms: int
        :param mode: file type, ["pandas", "h5"], defaults to 'pandas'
        :type mode: str, optional
        :return: either pandas dataframe of h5 file containing augmented data (original canonical forms not included)
        :rtype: [pandas.DataFrame, hdf5]
        """

        collection = {'source': [], 'target': []}
        products = None
        reactants = None

        # Enumerate over all values in the DataFrame
        for i, row in enumerate(self.data.values):

            collection = {'source': [], 'target': []}
            prod, reacts = self.__get_components(row)
            reacts.sort()

            # Make n_permutation samples for each component
            for n in range(0, n_perms):
                if len(reacts) > 1:
                    # If there are multiple reactants, sample pool "recurssively" e.g. (RB:P, P:RA )
                    # Round 1
                    ra, p, _ = self.__pairwise(reacts[0], prod[0],
                                               top_n=1, n_perms=1000)
                    # Round 2
                    p, rb, _ = self.__pairwise(
                        p, reacts[1], top_n=1, n_perms=1000, randomize_src=False)

                    # Update variable names
                    reactants = ".".join([ra, rb])
                    products = p

                elif len(reacts) == 1:
                    # Single round
                    ra, p, _ = self.__pairwise(reacts[0], prod[0],
                                               top_n=1, n_perms=1000)
                    # Update variabble names
                    reactants = ra
                    products = p

                # Save to dictionary (suitable for extracting & exporting to H5 or pandas)
                if mode == 'h5':
                    collection['source'].append(reactants)
                    collection['target'].append(products)

                elif mode == 'pandas':
                    self.pandas['source'].append(reactants)
                    self.pandas['target'].append(products)

            if mode == 'h5':
                # Write to H5 file
                for i, (k, v) in enumerate(collection.items()):
                    if k == 'target':
                        v = pd.Series(v).values
                        self.f.create_dataset("/" + self.group + str(chunk_id) + '_' +
                                              str(self.counter) + "/" + k, data=v, dtype=self.string_dt)

                    elif k == 'source':
                        v = pd.Series(v).values
                        self.f.create_dataset("/" + self.group + str(chunk_id) + '_' +
                                              str(self.counter) + "/" + k, data=v, dtype=self.string_dt)

                # Increment group counter
                self.output = self.f
                self.counter += 1

            elif mode == 'pandas':
                self.output = pd.DataFrame(self.pandas)

        return self.output

    def __get_normal_rand_SMILES(self, chunk_id, save_path, n_perms, mode='pandas'):

        # For column in Dataframe
        for col_name in self.data.columns:
            # For value in column
            for val in self.data[col_name].values:

                # If reactant set, split on dot to create reactant sub strings (smi's)
                if '.' in val:
                    rand_sets = []
                    SMILE_sets = val.split('.')

                    for smi in SMILE_sets:
                        # Return list of n randomized reactant
                        partial_smi = self.__uniform_rand(smi, n_perms)
                        rand_sets.append(partial_smi)

                    # Zip all sub reactants together and join on dot
                    zipped_smis = list(zip(rand_sets[0], rand_sets[1]))
                    randomized = [".".join(x) for x in zipped_smis]
                    randomized = pd.Series(randomized)

                else:
                    # If no "." seperator present, randomize
                    randomized = self.__uniform_rand(val, n_perms)
                    randomized = pd.Series(randomized)

                # At this point we have all randomized forms for a value
                if mode == 'h5':
                    # Append the randomized smiles to the dataset
                    self.f.create_dataset("/" + self.group + chunk_id + '_' + str(self.counter)
                                          + "/" + col_name,
                                          data=randomized.values, dtype=self.string_dt)
                    self.counter += 1
                    self.output = self.f

                elif mode == 'pandas':
                    if col_name == 'source':
                        self.reactant_series = self.reactant_series.append(
                            randomized, ignore_index=True)

                    elif col_name == 'target':
                        self.product_series = self.product_series.append(
                            randomized, ignore_index=True)
                    self.output = pd.concat(
                        [self.reactant_series, self.product_series], axis=1)

            self.counter = 0
        return self.output

    def canonicalize(self, SMILES):
        """
        Will compute and return the canonical form of a SMILES string.

        :param SMILES: non-canonical SMILES string
        :type SMILES: string
        :return: canonicalized SMILES string
        :rtype: string
        """

        # Generate moleulce from SMILES string
        mol = Chem.MolFromSmiles(SMILES)
        # Canonicalize mol and tranlate to SMILES string
        cSMILES = Chem.MolToSmiles(mol, canonical=True)
        return cSMILES

    def randomize(self, chunk_id, save_path, n_perms, method='normal', mode='pandas'):
        """
        Will produce a "smart" levenshtein randomized H5 file of self.data,
        each group represents a sample, while each dataset represents
        randomized versions of this dataset.

        :param chunk_id: partition number, defaults to 0
        :type chunk_id: int
        :param save_path: path to save H5 file
        :type save_path: string
        :param n_perms: number of permutation to randomize
        :type n_perms: int
        :param method: ['normal', 'leventhshtein'], the randomization strategy to use, defaults to 'normal'
        :type method: str, optional
        :return: saves pandas.DataFrame or Hdf5 file to save directory
        :rtype: [pandas.DataFrame, hdf5]
        """

        # Initialize h5file
        if mode == 'h5':
            self.__define_h5_file_groups(save_path, chunk_id)

        if method == "levenshtein":
            randomized_data = self.__get_levenshtein_SMILES(
                chunk_id, save_path, n_perms, mode=mode)

        elif method == 'normal':
            randomized_data = self.__get_normal_rand_SMILES(
                chunk_id, save_path, n_perms, mode=mode)

        else:
            print("Method must be one of: ['normal', 'levenshtein']")

        # Close flie if mode is h5
        if mode == 'h5':
            self.f.close()
        else:
            randomized_data.to_csv(save_path, index=False, header=None)
        # print(randomized_data)
        return randomized_data
