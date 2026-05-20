#!/bin/bash
## test_coloc.sh — smoke test for temp/coloc/coloc.R
##
## Runs coloc.abf on a 200-SNP IRF5 locus fixture (chr7:128954129 ± 1 Mb).
## SuSiE/LD step is intentionally skipped (invalid kg_bfile) — this test
## validates GWAS loading, eQTL loading, coloc.abf, and CSV/plot output only.
##
## Usage:
##   bash tests/coloc/test_coloc.sh
##
## Requirements:
##   singularity/genotype.sif (R, coloc, susieR, data.table, ggplot2, plink)
set -euo pipefail

REPO_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/../.." && pwd)"
FIXTURES="${REPO_DIR}/tests/coloc/fixtures"
OUTDIR="/tmp/coloc_test_$$"

echo "=== coloc.R smoke test ==="
echo "REPO    : $REPO_DIR"
echo "Fixtures: $FIXTURES"
echo "Outdir  : $OUTDIR"
echo ""

singularity exec \
  --bind /vol/projects:/vol/projects \
  "${REPO_DIR}/singularity/genotype.sif" \
  Rscript "${REPO_DIR}/tools/ciim/code/coloc.R" \
    --gene        IRF5 \
    --chr         7 \
    --pos         128954129 \
    --lead_rsid   rs10488631 \
    --window      1000000 \
    --gwas_file   "${FIXTURES}/test_gwas.tsv.gz" \
    --gwas_n      14267 \
    --gwas_s      0.3645 \
    --gwas_type   cc \
    --eqtl_dir    "${FIXTURES}/eqtl" \
    --eqtl_n      91 \
    --eqtl_format dice_vcf \
    --susie_n     1 \
    --kg_bfile    /nonexistent_kg_bfile \
    --outdir      "$OUTDIR"

echo ""
echo "--- Validating outputs ---"

PASS=0
FAIL=0

check() {
    local desc="$1"
    local cond="$2"
    if eval "$cond"; then
        echo "  PASS  $desc"
        PASS=$((PASS + 1))
    else
        echo "  FAIL  $desc"
        FAIL=$((FAIL + 1))
    fi
}

CSV="${OUTDIR}/coloc_abf_IRF5_results.csv"

check "coloc_abf CSV exists"           "[[ -f '$CSV' ]]"
check "coloc_abf CSV has data rows"    "[[ \$(tail -n +2 '$CSV' | wc -l) -ge 1 ]]"
check "coloc_abf CSV has cell_type col" "head -1 '$CSV' | grep -q 'cell_type'"
check "coloc_abf CSV has PP.H4 col"    "head -1 '$CSV' | grep -q 'PP.H4'"
check "PP.H4 barplot exists"           "[[ -f '${OUTDIR}/coloc_abf_IRF5_PP.H4_barplot.png' ]]"
check "posteriors stacked plot exists" "[[ -f '${OUTDIR}/coloc_abf_IRF5_posteriors_stacked.png' ]]"
check "regional GWAS plot exists"      "[[ -f '${OUTDIR}/regional_gwas_IRF5.png' ]]"

echo ""
echo "Results: PASS=$PASS  FAIL=$FAIL"
echo "Output files in: $OUTDIR"

if [[ $FAIL -gt 0 ]]; then
    exit 1
fi
