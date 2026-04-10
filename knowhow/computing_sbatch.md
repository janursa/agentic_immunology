# Computing: Running Jobs with SBATCH

Use SLURM `sbatch` to run long or heavy jobs on the cluster instead of running them interactively. Edit them based on given task. CRITICAL: if you submit a job using sbatch, keep an eye on it (monitor every 10 mins), and continue the pipeline once it's finished.

---

## CPU Job

```bash
#!/bin/bash
#SBATCH --job-name={task name job}
#SBATCH --output={put the temp file of the tast}/logs/%j.out
#SBATCH --error={put the temp file of the tast}/%j.err
#SBATCH --ntasks=1
#SBATCH --cpus-per-task=10 -> adjust this based on the task
#SBATCH --time=20:00:00 -> adjust this based on the task
#SBATCH --mem=500GB -> adjust this based on the task
#SBATCH --partition=cpu

set -e

{running environment} {code script}
```

## GPU Job
same as above but relace the `--partition` and add `--gres=gpu:1`.
```bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1

set -e

```

---

