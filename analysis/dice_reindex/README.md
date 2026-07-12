# DICE eQTL VCF reindexing

## Problem
`tools/ciim/code/coloc.R`'s DICE eQTL loader (`load_eqtl_dice_vcf`) used to run
`zcat file.vcf.gz | grep -v '^##' | awk 'NR==1 || /GeneSymbol=<gene>;/'` — a full
decompression + text scan of the whole ~3.1–3.4 GB VCF per cell type, per gene,
because there was no positional index. A single-locus `run_coloc()` call (15 DICE
cell types) took 1–3 hours, and was observed to time out entirely (see
`temp/immune_aging_novel_target/round2/LOG.md`, ZEB2 locus, killed after 18+ min
with zero output).

Root cause: as distributed by DICE, `datalake/dice/eqtls/full_summary_stats/*.vcf.gz`
is plain gzip (not bgzip) and sorted by ascending p-value, not by genomic position —
so the files were never tabix-indexable as shipped.

## Fix
`reindex_dice.sh` re-sorts one DICE VCF by `CHROM`/`POS`, bgzip-compresses it, and
tabix-indexes it:

```
zcat {cell}.vcf.gz | grep -v '#' | sort -k1,1 -k2,2n | bgzip > {cell}.vcf.bgz
tabix -p vcf {cell}.vcf.bgz
```

`reindex_dice.sbatch` runs this as a 15-task SLURM array (one per DICE cell type),
inside `singularity/genotype.sif` (has `bgzip`/`tabix`).

`coloc.R`'s `load_eqtl_dice_vcf` was patched to do a regional `tabix` lookup on the
cis-window `run_coloc()` already computes (`chr:pos±window`) instead of scanning
the whole file — turning a 1–3 hr/gene scan into a sub-second lookup.

## Usage (one-time; already run)
```bash
sbatch analysis/dice_reindex/reindex_dice.sbatch
```
Output: `{cell_type}.vcf.bgz` + `.vcf.bgz.tbi` written in place into
`datalake/dice/eqtls/full_summary_stats/`, overwriting nothing (original
`.vcf.gz` files were removed separately after validating line counts matched).
Sort/merge scratch space is written to `temp/dice_reindex/scratch/` (ephemeral,
auto-created/removed per task) and per-task SLURM logs go to
`analysis/dice_reindex/logs/`.

## Result
Ran 2026-07-11. All 15 cell types reindexed (~10 min each, run in parallel;
line counts verified identical to the source `.vcf.gz`, e.g. B_CELL_NAIVE:
215,708,762 lines both before and after). Re-ran the ZEB2 locus
(chr2:144442710) that previously timed out at 18+ min — completed in 32
seconds with correct coloc.abf/susie output across all 15 cell types.

Total size dropped from 47 GB (`.vcf.gz`) to 31 GB (`.vcf.bgz` + `.tbi`); the
originals were deleted after validation.

## Files
- `reindex_dice.sh` — per-cell-type sort + bgzip + tabix pipeline
- `reindex_dice.sbatch` — SLURM array job driving `reindex_dice.sh` over all 15 DICE cell types
- `logs/` — SLURM stdout/stderr from the reindex array job and the ZEB2 validation runs
- `test_coloc_zeb2/` — output of the end-to-end `coloc.R` validation run (ZEB2 locus)
