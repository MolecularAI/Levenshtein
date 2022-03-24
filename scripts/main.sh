#!/bin/bash
#Source variables
source config.INI

#Initialize Conda environment
source $conda_activate $conda_env

#Split the datafile into partitions on the scratch directory
echo "Running 01_split.py"
python 01_split.py

#start Slurm array job to augment partitions, saving into n_augmentation files per partition
echo "Submitting job array for step 2"
jobid=$(sbatch --array=0-$(expr $n_partitions - 1)%2048 \
--output=$scratch_path/logs/Levenshtein_augment_%A_%a.log \
--chdir=$script_path \
02_slurm_array_job.sh)

#Get jobid of array job
#sbatch returns more than just the jobid: "Submitted batch job 15498242"
if [[ "$jobid" =~ Submitted\ batch\ job\ ([0-9]+) ]]; then
    jobid="${BASH_REMATCH[1]}"
else
    echo "sbatch failed"
    exit 1
fi

#Submit jobarray collecting results from the partitions in n_augmentation csv files
#Wait for previous arrays jobid to finish before starting
echo "submitting job array for collection of results"
jobid2=$(sbatch --array=0-$(expr $number_augmentations - 1) \
--output=$scratch_path/logs/Levenshtein_augment_collect_%A_%a.log \
--chdir=$script_path \
--dependency=afterok:$jobid \
03_collect_array_job_bash.sh)

#Get jobid from sbatch output
if [[ "$jobid2" =~ Submitted\ batch\ job\ ([0-9]+) ]]; then
    jobid2="${BASH_REMATCH[1]}"
else
    echo "sbatch failed"
    exit 1
fi

#Copy the final files from scratch directory to final destination directory,
#waiting on previous jobid to finish
echo "Submitting job for collection of results"
sbatch \
--output=$scratch_path/logs/Levenshtein_augment_copy_%A.log \
--chdir=$script_path \
--dependency=afterok:$jobid2 \
04_copy_from_scratch.sh
