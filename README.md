[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
[![Open Source Love svg2](https://badges.frapsoft.com/os/v2/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)
![stability-wip](https://img.shields.io/badge/stability-work_in_progress-lightgrey.svg)
![status:archived](https://img.shields.io/badge/Status-Archived-lightgrey)


# Levenshtein Augmentor
> A CML tool to generate attention mediated SMILES augmentations. 

## Important!
The augmentor currently only supports reactions consisting of a maximum of two reactant sub-components, leading to a single product.<br />Neither does it currently work with (re)agent or condition information.  

## General info
It is recommended to save and collate to pandas especially for large datasets i.e. where n > 1M.<br />
Please refer to any README.txt documents throughout this repository for further help.

## Setup
Download/clone Levenshtein and navigate to scripts directory. 
From scripts there are two steps: 

* Augmention: partition_data.py file
* Collation: collate.py file


## Usage
From inside scripts directory run the following (wait until augmentation is complete prior to running collation):  
<br />
Augmentation:  <br />
`$ python partition_data.py {filename}.csv {method} {chunk_size}`

Collation:  <br />
`$ python collate.sh {filename}.csv {method}`

## Outputs
Example of running test_canonical.csv with normal randomization
* Augmentation:
> ../file_dumps/test_canonical/test_canonical_chunk_5_partition_0.csv <br /> ../file_dumps/test_canonical/test_canonical_chunk_5_partition_0_normal.csv

* Collation:
> ../file_dumps/collated_pandas_data/test_canonical_normal_collated.csv

## Dependencies
* python                        3.7.3               
* pandas                        0.25.3             
* numpy                         1.17.3             
* h5py                          2.10.0             
* python-Levenshtein            0.12.0             
* rdkit                         2019.09.2 

## TODO
Add more CML args to specify h5 or pandas preferences.
## Reference
Sumner, D.; He, J.; Thakkar, A.; Engkvist, O.; Bjerrum, E. J. Levenshtein Augmentation Improves Performance of SMILES Based Deep-Learning Synthesis Prediction. 2020. https://doi.org/10.26434/chemrxiv.12562121.v1

