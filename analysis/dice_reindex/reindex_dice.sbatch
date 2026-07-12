#!/bin/bash
#SBATCH --job-name=dice_reindex
#SBATCH --output=/vol/projects/CIIM/agentic_immunology/analysis/dice_reindex/logs/%A_%a.out
#SBATCH --error=/vol/projects/CIIM/agentic_immunology/analysis/dice_reindex/logs/%A_%a.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=6
#SBATCH --time=04:00:00
#SBATCH --mem=32G
#SBATCH --partition=cpu
#SBATCH --array=0-14

set -e

CELLS=(B_CELL_NAIVE CD4_NAIVE CD4_STIM CD8_NAIVE CD8_STIM M2 MONOCYTES NK TFH TH1 TH17 TH2 THSTAR TREG_MEM TREG_NAIVE)
CELL="${CELLS[$SLURM_ARRAY_TASK_ID]}"

singularity exec --bind /vol/projects:/vol/projects \
  /vol/projects/CIIM/agentic_immunology/singularity/genotype.sif \
  bash /vol/projects/CIIM/agentic_immunology/analysis/dice_reindex/reindex_dice.sh "$CELL"
