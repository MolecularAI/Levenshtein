#!/bin/bash
#SBATCH --job-name=Levenshtein_augment_copy_%A
#SBATCH --ntasks=1
#SBATCH --mem=10mb
#SBATCH --time=00:10:00
#SBATCH --cpus-per-task=1

source config.INI

mkdir -p $target_path
mkdir -p $target_path/augmentations
#mkdir -p $target_path/cleaned_partitions

cp -v $scratch_path/*csv $target_path
cp -v $scratch_path/augmentations/*csv.zip $target_path/augmentations
#cp -v $scratch_path/cleaned_partitions/*csv $target_path/cleaned_partitions 
