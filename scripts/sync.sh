#!/bin/bash
#SBATCH --job-name=sync
#SBATCH --output=logs/%j.out
#SBATCH --error=logs/%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=1
#SBATCH --time=20:00:00
#SBATCH --mem=50GB
#SBATCH --partition=cpu
#SBATCH --mail-type=END,FAIL      
#SBATCH --mail-user=jalil.nourisa@gmail.com   

# aws s3 sync datalake/biomni  s3://openproblems-data/resources/grn/temp/datalake/biomni --delete
# aws s3 sync datalake/omnipath  s3://openproblems-data/resources/grn/temp/datalake/omnipath 
aws s3 sync datalake/prior  s3://openproblems-data/resources/grn/temp/datalake/prior 
aws s3 sync datalake/prior  s3://openproblems-data/resources/grn/temp/datalake/prior 
aws s3 cp singularity/biomni_full.sif  s3://openproblems-data/resources/grn/temp/singularity/ 
aws s3 cp singularity/ciim.sif  s3://openproblems-data/resources/grn/temp/singularity/
 



# aws s3 sync  s3://openproblems-data/resources/grn/temp/datalake/  datalake/ 
# aws s3 sync  s3://openproblems-data/resources/grn/temp/singularity/ singularity/
 
