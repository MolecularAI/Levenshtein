#!/bin/bash
# Change these IOs

#SBATCH --workdir=/PATH/TO/CODE/augmentation/scripts
#SBATCH -o ../slurm_dumps/collate_job_%j.output
#SBATCH -e ../slurm_dumps/collate_job_%j.error
#SBATCH --mail-type=ALL
#SBATCH -t 05:00:00
#SBATCH --mem=10gb
#SBATCH --cpus-per-task=1

echo 'submitting collate job'
# $1 is filename
# $2 is randomization type 
~/miniconda3/envs/pytorch/bin/python collate.py $1 $2
