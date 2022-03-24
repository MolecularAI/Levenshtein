#!/bin/bash
##!!!!!!!!!!!!!!!!!!!!!!!!!
# Run this file using the 02_sub,it_array_job script to use configuration in config.INI
##!!!!!!!!!!!!!!!!!!!!!!!!!
## %a will be array task id, %A is the job ID
#SBATCH --job-name=Levenshtein_augment_%a
#SBATCH --ntasks=1
#SBATCH --mem=500mb
#SBATCH --time=04:00:00
#SBATCH --cpus-per-task=1

XDG_RUNTIME_DIR=""

date;hostname;pwd

source config.INI
source $conda_activate $conda_env
which python

python 02_augment.py $SLURM_ARRAY_TASK_ID
