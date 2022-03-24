#!/bin/bash
## %a will be array task id, %A is the job ID
#SBATCH --job-name=Levenshtein_augment_collect_%a
#SBATCH --ntasks=1
#SBATCH --mem=10mb
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1


XDG_RUNTIME_DIR=""

date;hostname;pwd

source config.INI
padded_augmentation=$(printf %03d $SLURM_ARRAY_TASK_ID)
target_file=$scratch_path/augmentations/data_aug$padded_augmentation.csv
source_files=$scratch_path/augmentations/$padded_augmentation/data_p*_aug$padded_augmentation.csv
header_file=$scratch_path/augmentations/headers.csv

echo $header_file
echo $target_file
echo $source_files

cat $header_file $source_files >> $target_file
zip -j $target_file.zip $target_file
rm $target_file