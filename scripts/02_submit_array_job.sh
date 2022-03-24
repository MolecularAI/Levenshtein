#!/bin/bash

source config.INI

sbatch --array=0-$(expr $n_partitions - 1)%2048 \
--output=$scratch_path/logs/Levenshtein_augment_%A_%a.log \
--chdir=$script_path \
02_slurm_array_job.sh


