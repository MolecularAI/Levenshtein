**Please note: this repository is no longer being maintained.**

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
![status:archived](https://img.shields.io/badge/Status-Archived-lightgrey)

# Levenshtein Augmentation of SMILES datasets
> A tool to generate attention mediated SMILES augmentations. 

Consists of a Levenshtein augmenter class and SLURM/Bash/Python scripts for efficient embarassingly parallel execution. They partition a pandas dataset into thousands of small files, using slurm array job on the files, and then collect the results into separate augmented datasets for each epoch.

## Installation
A conda enviroment with the dependencies need to be created and the levenshtein augment modules installed.
```
conda env create -f conda_env.yml
conda activate levensthein_augment_env
pip install -e .
```

## Releases

The original code used for the preprint is available under the tag "Preprint". The main difference is that the preprint find the pairs from reactant1 to product and from product to reactant2, where the newcode picks randomly augmented SMILES for all reactants, and then finds the product that best match all of the picked reactants. 

### Optional ipykernel installation
```
pip install ipykernel
python -m ipykernel install --user --name levenshtein_augment_env --display-name "levenshtein_augment_env"
```

## Configuration and Running via Scripts
Copy the provided `scripts/config_template.INI` to `config.INI` and customize the settings, the datafile path and directory paths.

`config.INI` contains the settings. dataset, input and output column and directories that needs to be customized. Here the paths for the datafile, the scratch directories, and the final directory to collect the results.

The config file also contain paths for the miniconda enviroment for activation and the run conda environment.

The code expects rdkit sanitizable SMILES in two seperate columns. The augment scripts uses pandas dataframes, and the names of the input and output collumns must be defined in the `config.INI` file. 

All the `.` seperated smiles in the input column are augmented and selected randomly from the pool, whereafter the best sequence matching smiles string from the augmentations in the output column are selected.

The rest of the columns are kept as-is and transferred to the final datafiles. It is a good idea to define a column with the predefined train, validation and test-sets before running the script, as this will then be propagated to all the indiviual augmented files.

The `main.sh` script runs the steps 01-04 in succession, using slurm job control to wait for the previous steps. Otherwise single steps can be submitted using the `XX_submit_array_job.sh` scripts.

## Reference
Sumner, D.; He, J.; Thakkar, A.; Engkvist, O.; Bjerrum, E. J. Levenshtein Augmentation Improves Performance of SMILES Based Deep-Learning Synthesis Prediction. 2020. [https://doi.org/10.26434/chemrxiv.12562121.v1](https://doi.org/10.26434/chemrxiv.12562121.v1)


