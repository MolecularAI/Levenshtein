#!/bin/bash

source config.INI

sbatch --array=0-$(expr $number_augmentations - 1) \
--output=$scratch_path/logs/Levenshtein_augment_collect_%A_%a.log \
--chdir=$script_path \
03_collect_array_job_bash.sh

