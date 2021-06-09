#!/bin/bash
# Change these IOs
#SBATCH -o /PATH/TO/CODE/augmentation/slurm_dumps/batch_%j.output
#SBATCH -e /PATH/TO/CODE/augmentation/slurm_dumps/batch_%j.error
#SBATCH --workdir=/PATH/TO/CODE/augmentation/scripts
#SBATCH --mail-type=ALL
#SBATCH -t 05:00:00
#SBATCH --mem=20gb
#SBATCH --cpus-per-task=1

echo submitting job
# Chunk master csv file and ranomize using subprocess, replace with your own env/path

# DO NOT MODIFY THESE BASH VARIABLES
~/miniconda3/envs/pytorch/bin/python augment_main.py $1 $2 $3 $4
