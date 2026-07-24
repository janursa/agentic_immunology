"""
QUESTION: rs11867200 associates with CCL2/MCP-1 production after 24h LPS stimulation in PBMCs,
but ONLY in old or disease individuals. What is the mechanism?

STEP 3: Aging context from HiRA
- 3a: CCL2/CCL8 aging gene expression across major immune cell types
- 3b: Aging TF activity in monocytes (major + minor resolution)
- 3c: Cross-reference Step 1 TF candidates with aging TF signatures
- 3d: SLE gene expression for CCL2/CCL8 in monocytes (disease context)
- 3e: SLE TF activity in monocytes — cross-reference with Step 1 TFs
- 3f: LPS-relevant cytokine TF signatures in monocytes
Output: temp/nienke/step3_hira/results.txt
"""

import sys, os
sys.path.insert(0, '/vol/projects/BIIM/agentic_immunology/tools/ciim/code')
from hira import retrieve_summary_stats
import pandas as pd

BASE   = "/vol/projects/BIIM/agentic_immunology"
OUT    = f"{BASE}/temp/nienke/step3_hira"
RESULT = f"{OUT}/results.txt"

def log(msg):
    print(msg, flush=True)
    with open(RESULT, 'a') as f:
        f.write(msg + '\n')

def df_to_log(df, max_rows=30):
    """Write a DataFrame to the log as a readable table."""
    if df.empty:
        log("  (no rows)\n")
        return
    log(df.to_string(index=False, max_rows=max_rows))
    log("")

# TF candidates identified at rs11867200 locus in Step 1
# Sources: ENCODE ChIP-seq peaks (via RegulomeDB) + JASPAR motif query
STEP1_TFS = ['CEBPA', 'CEBPB', 'RELA', 'FOS', 'FOSL2', 'SPIC', 'GABPA',
             'NR3C1', 'ISL1', 'MYC', 'MAX', 'EP300']

# Initialise output file
with open(RESULT, 'w') as f:
    f.write("STEP 3 — Aging context from HiRA\n")
    f.write(f"Step 1 TF candidates: {', '.join(STEP1_TFS)}\n")
    f.write("=" * 70 + "\n\n")

# ══════════════════════════════════════════════════════════════════════
# 3a.  CCL2 / CCL8 aging gene expression — all major cell types
# ══════════════════════════════════════════════════════════════════════
log("=" * 70)
log("3a. CCL2/CCL7/CCL8 aging gene expression — major cell types (all cohorts)")
log("=" * 70)

df_ge = retrieve_summary_stats('aging', feature_type='gene_expression')
log(f"\n  Full aging gene expression dataset: {df_ge.shape[0]} rows, "
    f"cell types: {sorted(df_ge['cell_type'].unique().tolist())}")
log(f"  Columns: {df_ge.columns.tolist()}\n")

# Check CCL2 and its chromosomal neighbours (CCL7/CCL8 share the chr17 cluster)
ccl_genes = df_ge[df_ge['gene'].isin(['CCL2', 'CCL7', 'CCL8'])].copy()
if ccl_genes.empty:
    log("  CCL2/CCL7/CCL8 not found in aging gene expression data.\n")
else:
    log(f"  Found {len(ccl_genes)} rows for CCL2/CCL7/CCL8:\n")
    df_to_log(ccl_genes)

# Rank CCL2 specifically in MONO across datasets
log("\n  CCL2 in MONO — all cohorts, rank within monocyte aging DEGs:")
mono_ge = df_ge[df_ge['cell_type'] == 'MONO'].copy()
if not mono_ge.empty:
    ccl2_mono = mono_ge[mono_ge['gene'] == 'CCL2']
    if ccl2_mono.empty:
        log("  CCL2 not found in MONO aging signatures.")
        # Find where CCL2 ranks (by meta_p_adj if present, else p_adj or slope)
    else:
        log(f"  CCL2 MONO rows:\n")
        df_to_log(ccl2_mono)
    # Rank CCL2 by effect size among all MONO aging genes
    sort_col = 'meta_p_adj' if 'meta_p_adj' in mono_ge.columns else mono_ge.columns[-1]
    mono_ranked = mono_ge.dropna(subset=[sort_col]).sort_values(sort_col)
    ccl2_rank = mono_ranked.reset_index(drop=True)
    ccl2_idx = ccl2_rank[ccl2_rank['gene'] == 'CCL2'].index
    if len(ccl2_idx) > 0:
        log(f"\n  CCL2 ranks #{ccl2_idx[0]+1} of {len(ccl2_rank)} MONO aging genes "
            f"(sorted by {sort_col})")
    else:
        log("  CCL2 not rankable (not found or all NA).")
else:
    log("  MONO cell type not found in gene expression data.")

# ══════════════════════════════════════════════════════════════════════
# 3b.  Aging TF activity — MONO major + minor cell types
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("3b. Aging TF activity — MONO (major cell types, FDR<0.05)")
log("=" * 70)

df_tf_mono = retrieve_summary_stats('aging', cell_type='MONO', p_adj_threshold=0.05)
log(f"\n  Significant TFs in MONO aging (FDR<0.05): {df_tf_mono['gene'].nunique()} unique TFs, "
    f"{len(df_tf_mono)} rows")
if not df_tf_mono.empty:
    log(f"  Columns: {df_tf_mono.columns.tolist()}\n")
    # Show increasing TFs
    if 'trend' in df_tf_mono.columns:
        inc = df_tf_mono[df_tf_mono['trend'] == 'Increase in aging']
        dec = df_tf_mono[df_tf_mono['trend'] == 'Decrease in aging']
        log(f"  Increasing with age in MONO: {inc['gene'].nunique()} unique TFs")
        log(f"  Decreasing with age in MONO: {dec['gene'].nunique()} unique TFs\n")
        log("  Top increasing TFs (first 40 rows):")
        df_to_log(inc.drop_duplicates('gene').head(40))
        log("  Top decreasing TFs (first 40 rows):")
        df_to_log(dec.drop_duplicates('gene').head(40))
    else:
        df_to_log(df_tf_mono.head(40))

log("\n" + "-" * 60)
log("3b-minor. Aging TF activity — Classic_MONO + NonClassic_MONO (minor, FDR<0.05)")
log("-" * 60)

df_tf_minor = retrieve_summary_stats(
    'aging', cell_resolution='minor',
    cell_type=['Classic_MONO', 'NonClassic_MONO'],
    p_adj_threshold=0.05
)
log(f"\n  Minor MONO significant TFs: {df_tf_minor['gene'].nunique()} unique TFs, "
    f"{len(df_tf_minor)} rows")
if not df_tf_minor.empty:
    if 'trend' in df_tf_minor.columns:
        for ct in df_tf_minor['cell_type'].unique():
            sub = df_tf_minor[df_tf_minor['cell_type'] == ct]
            inc = sub[sub['trend'] == 'Increase in aging']
            dec = sub[sub['trend'] == 'Decrease in aging']
            log(f"\n  [{ct}] Increasing: {inc['gene'].nunique()} TFs | "
                f"Decreasing: {dec['gene'].nunique()} TFs")
            log(f"  [{ct}] Increasing TFs:")
            df_to_log(inc.drop_duplicates('gene').head(30))
    else:
        df_to_log(df_tf_minor.head(40))

# ══════════════════════════════════════════════════════════════════════
# 3c.  Cross-reference Step 1 TF candidates × aging signatures (all CTs)
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("3c. Cross-reference Step 1 TF candidates with aging TF signatures (all cell types, FDR<0.05)")
log(f"    TFs to check: {', '.join(STEP1_TFS)}")
log("=" * 70)

df_tf_all = retrieve_summary_stats('aging', p_adj_threshold=0.05)
log(f"\n  All aging TF significant rows: {len(df_tf_all)}")
step1_hits = df_tf_all[df_tf_all['gene'].isin(STEP1_TFS)].copy()
log(f"  Step 1 TFs found in aging signatures (FDR<0.05): "
    f"{step1_hits['gene'].nunique()} / {len(STEP1_TFS)}")
if not step1_hits.empty:
    log(f"  TFs found: {sorted(step1_hits['gene'].unique().tolist())}\n")
    log("  Full table (gene, cell_type, trend, meta_p_adj / effect):")
    df_to_log(step1_hits)
else:
    log("  None of the Step 1 TF candidates are significant at FDR<0.05 in any cell type.\n")
    # Try without threshold to see direction
    log("  Checking without p-value filter (all trends):")
    df_tf_all_unfiltered = retrieve_summary_stats('aging')
    step1_unfiltered = df_tf_all_unfiltered[df_tf_all_unfiltered['gene'].isin(STEP1_TFS)].copy()
    if not step1_unfiltered.empty:
        # Pick cols that are most informative
        cols = [c for c in ['gene', 'cell_type', 'trend', 'meta_p_adj', 'slope', 'dataset']
                if c in step1_unfiltered.columns]
        df_to_log(step1_unfiltered[cols].drop_duplicates().sort_values(['gene', 'cell_type']))

# ══════════════════════════════════════════════════════════════════════
# 3d.  SLE gene expression for CCL2/CCL8 in monocytes
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("3d. SLE gene expression for CCL2/CCL8 in MONO (Perez cohort)")
log("=" * 70)

df_sle_ge = retrieve_summary_stats('sle', feature_type='gene_expression', cell_type='MONO')
log(f"\n  SLE gene expression MONO rows: {len(df_sle_ge)}")
if not df_sle_ge.empty:
    log(f"  Columns: {df_sle_ge.columns.tolist()}")
ccl_sle = df_sle_ge[df_sle_ge['gene'].isin(['CCL2', 'CCL7', 'CCL8'])]
if ccl_sle.empty:
    log("  CCL2/CCL7/CCL8 not significant in SLE MONO.\n")
    # Check without threshold
    df_sle_ge_all = retrieve_summary_stats('sle', feature_type='gene_expression', cell_type='MONO')
    ccl_sle_any = df_sle_ge_all[df_sle_ge_all['gene'].isin(['CCL2', 'CCL7', 'CCL8'])]
    if not ccl_sle_any.empty:
        log("  (No p-value filter) CCL2/CCL7/CCL8 in SLE MONO:")
        df_to_log(ccl_sle_any)
    else:
        log("  CCL2/CCL7/CCL8 not tested or not present in SLE MONO dataset.")
else:
    log("  CCL2/CCL7/CCL8 in SLE MONO:")
    df_to_log(ccl_sle)

# SLE — all MONO gene expression with relaxed threshold (show where CCL2 ranks)
df_sle_ge_full = retrieve_summary_stats('sle', feature_type='gene_expression', cell_type='MONO')
if not df_sle_ge_full.empty:
    sort_col = 'p_value_adj' if 'p_value_adj' in df_sle_ge_full.columns else 'p_value'
    sle_mono_ranked = df_sle_ge_full.dropna(subset=[sort_col]).sort_values(sort_col)
    ccl2_sle_idx = sle_mono_ranked.reset_index(drop=True)
    ccl2_row = ccl2_sle_idx[ccl2_sle_idx['gene'] == 'CCL2']
    if len(ccl2_row) > 0:
        rank = ccl2_row.index[0] + 1
        total = len(ccl2_sle_idx)
        log(f"\n  CCL2 ranks #{rank} of {total} in SLE MONO (sorted by {sort_col})")
        df_to_log(ccl2_row)
    else:
        log("  CCL2 not found in SLE MONO gene expression.")

# ══════════════════════════════════════════════════════════════════════
# 3e.  SLE TF activity in MONO × Step 1 candidates
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("3e. SLE TF activity in MONO — cross-reference with Step 1 TF candidates")
log("=" * 70)

df_sle_tf_mono = retrieve_summary_stats('sle', cell_type='MONO')
log(f"\n  All SLE TF MONO rows: {len(df_sle_tf_mono)}")
if not df_sle_tf_mono.empty:
    log(f"  Columns: {df_sle_tf_mono.columns.tolist()}")

step1_sle = df_sle_tf_mono[df_sle_tf_mono['gene'].isin(STEP1_TFS)].copy()
log(f"\n  Step 1 TFs in SLE MONO signatures (all p-values): "
    f"{step1_sle['gene'].nunique()} / {len(STEP1_TFS)}")
if not step1_sle.empty:
    log(f"  TFs found: {sorted(step1_sle['gene'].unique().tolist())}\n")
    df_to_log(step1_sle)

# Also get significant SLE MONO TFs (FDR<0.05)
df_sle_tf_sig = retrieve_summary_stats('sle', cell_type='MONO', p_adj_threshold=0.05)
log(f"\n  Significant SLE MONO TFs (FDR<0.05): {df_sle_tf_sig['gene'].nunique()} unique")
if not df_sle_tf_sig.empty:
    if 'direction' in df_sle_tf_sig.columns or 'slope' in df_sle_tf_sig.columns:
        log("  Top significant SLE MONO TFs:")
        df_to_log(df_sle_tf_sig.head(40))

# ══════════════════════════════════════════════════════════════════════
# 3f.  Cytokine TF signatures in MONO — LPS-relevant cytokines
# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("3f. LPS-relevant cytokine TF signatures in MONO (ParseBio, FDR<0.05)")
log("    Focus: TNF-alpha, IL-1-beta, IL-6, IL-8, M-CSF (LPS-induced milieu)")
log("=" * 70)

df_cyto_all = retrieve_summary_stats('cytokine', cell_type='MONO', p_adj_threshold=0.05)
log(f"\n  All significant cytokine TF rows in MONO: {len(df_cyto_all)}")
if not df_cyto_all.empty:
    log(f"  Columns: {df_cyto_all.columns.tolist()}")

lps_cytokines = ['TNF-alpha', 'IL-1-beta', 'IL-6', 'M-CSF', 'IL-8']
for cyto in lps_cytokines:
    sub = df_cyto_all[df_cyto_all['condition'] == cyto] if 'condition' in df_cyto_all.columns else \
          df_cyto_all[df_cyto_all['comparison'] == cyto] if 'comparison' in df_cyto_all.columns else \
          pd.DataFrame()
    if sub.empty:
        log(f"\n  [{cyto}] No significant TF hits in MONO.")
        continue
    step1_cyto = sub[sub['gene'].isin(STEP1_TFS)]
    log(f"\n  [{cyto}] {sub['gene'].nunique()} significant TFs; "
        f"Step 1 overlap: {step1_cyto['gene'].nunique()} TFs")
    if not step1_cyto.empty:
        log(f"  Step 1 TFs: {sorted(step1_cyto['gene'].unique().tolist())}")
        df_to_log(step1_cyto)

# ══════════════════════════════════════════════════════════════════════
log("\n" + "=" * 70)
log("STEP 3 COMPLETE")
log(f"Output: {RESULT}")
log("=" * 70)
