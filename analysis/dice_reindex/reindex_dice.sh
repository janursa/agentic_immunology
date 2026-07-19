#!/usr/bin/env bash
# One-time: sort a DICE full_summary_stats VCF by position, bgzip, tabix-index.
# Files ship sorted by ascending Pvalue (most significant pair first), not by
# position, so they aren't tabix-indexable as distributed — this fixes that.
set -euo pipefail

CELL="$1"
REPO_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
EQTL_DIR="$REPO_ROOT/datalake/dice/eqtls/full_summary_stats"
SCRATCH="$REPO_ROOT/temp/dice_reindex/scratch/${CELL}"
IN="${EQTL_DIR}/${CELL}.vcf.gz"
OUT_TMP="${SCRATCH}/${CELL}.vcf.bgz"
OUT_FINAL="${EQTL_DIR}/${CELL}.vcf.bgz"
THREADS="${SLURM_CPUS_PER_TASK:-6}"

mkdir -p "$SCRATCH"

echo "[$(date)] $CELL: extracting header"
# head truncates the zcat|grep pipe early, so zcat exits via SIGPIPE (141) —
# expected here, not a real failure, so don't let pipefail abort the script.
zcat "$IN" | head -20 | grep '^#' > "${SCRATCH}/header.txt" || true

echo "[$(date)] $CELL: sort + bgzip (threads=$THREADS)"
{
  cat "${SCRATCH}/header.txt"
  zcat "$IN" | grep -v '^#' | LC_ALL=C sort -k1,1 -k2,2n -S 20G --parallel="$THREADS" -T "$SCRATCH"
} | bgzip -@ "$THREADS" > "$OUT_TMP"

echo "[$(date)] $CELL: tabix index"
tabix -p vcf "$OUT_TMP"

echo "[$(date)] $CELL: moving into place"
mv "$OUT_TMP" "$OUT_FINAL"
mv "${OUT_TMP}.tbi" "${OUT_FINAL}.tbi"
rm -rf "$SCRATCH"

echo "[$(date)] $CELL: DONE"
