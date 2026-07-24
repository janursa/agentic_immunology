"""
PheWAS for rs11867200 across OpenGWAS and GWAS Catalog.
Goal: find disease/trait associations for the CCL2-linked variant.
"""
import sys
import os

sys.path.insert(0, '/vol/projects/BIIM/agentic_immunology/tools/ciim/code')
from genetics import phewas_opengwas, query_gwas_catalog

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUTDIR = '/vol/projects/BIIM/agentic_immunology/temp/nienke/step4_phewas'
IMGDIR = os.path.join(OUTDIR, 'images')
os.makedirs(IMGDIR, exist_ok=True)

SNP = 'rs11867200'
RESULTS_FILE = os.path.join(OUTDIR, 'results.txt')

log_lines = []
def log(msg):
    print(msg)
    log_lines.append(msg)

log("=" * 70)
log(f"PheWAS — {SNP} (CCL2 locus, chr17:34,248,950 GRCh38)")
log("=" * 70)

# ─────────────────────────────────────────────────────────────────────────────
# 1. GWAS Catalog (local, published genome-wide significant associations)
# ─────────────────────────────────────────────────────────────────────────────
log("\n\n--- Section 1: GWAS Catalog (local, p < 5e-8) ---")
try:
    gwas_hits = query_gwas_catalog([SNP])
    if gwas_hits is None or len(gwas_hits) == 0:
        log("No hits in GWAS Catalog for rs11867200.")
    else:
        log(f"Found {len(gwas_hits)} GWAS Catalog hits.")
        log(gwas_hits[['SNPS', 'DISEASE/TRAIT', 'PVALUE_MLOG', 'OR or BETA', 'MAPPED_GENE']].to_string())
except Exception as e:
    log(f"GWAS Catalog query failed: {e}")

# ─────────────────────────────────────────────────────────────────────────────
# 2. OpenGWAS PheWAS — GWAS-significant threshold (p < 5e-8)
# ─────────────────────────────────────────────────────────────────────────────
log("\n\n--- Section 2: OpenGWAS PheWAS — p < 5e-8 ---")
try:
    hits_strict = phewas_opengwas([SNP], pval=5e-8, drop_expression=True)
    if hits_strict is None or len(hits_strict) == 0:
        log("No hits at p < 5e-8 in OpenGWAS.")
        hits_strict = pd.DataFrame()
    else:
        log(f"Found {len(hits_strict)} hits at p < 5e-8.")
        log(hits_strict.sort_values('p').to_string())
except Exception as e:
    log(f"OpenGWAS strict query failed: {e}")
    hits_strict = pd.DataFrame()

# ─────────────────────────────────────────────────────────────────────────────
# 3. OpenGWAS PheWAS — suggestive threshold (p < 1e-5)
# ─────────────────────────────────────────────────────────────────────────────
log("\n\n--- Section 3: OpenGWAS PheWAS — p < 1e-5 (suggestive) ---")
try:
    hits_suggestive = phewas_opengwas([SNP], pval=1e-5, drop_expression=True)
    if hits_suggestive is None or len(hits_suggestive) == 0:
        log("No hits at p < 1e-5 in OpenGWAS.")
        hits_suggestive = pd.DataFrame()
    else:
        log(f"Found {len(hits_suggestive)} hits at p < 1e-5.")
        log(hits_suggestive.sort_values('p').to_string())
except Exception as e:
    log(f"OpenGWAS suggestive query failed: {e}")
    hits_suggestive = pd.DataFrame()

# ─────────────────────────────────────────────────────────────────────────────
# 4. Combine and plot
# ─────────────────────────────────────────────────────────────────────────────
log("\n\n--- Section 4: Summary and plot ---")

all_hits = hits_suggestive if len(hits_suggestive) > 0 else hits_strict

if len(all_hits) == 0:
    log("No hits found at any threshold — no plot generated.")
else:
    all_hits = all_hits.copy()
    all_hits['neglog10p'] = -np.log10(all_hits['p'].astype(float))

    # Assign broad trait categories based on trait name keywords
    def categorize(trait):
        t = str(trait).lower()
        if any(k in t for k in ['lupus', 'sle', 'autoimmun', 'arthritis', 'ms ', 'multiple scler',
                                  'crohn', 'ibd', 'bowel', 'psoriasis', 'sjögren', 'sjogren',
                                  'celiac', 'coeliac', 'ankylos']):
            return 'Autoimmune/inflammatory'
        if any(k in t for k in ['coronary', 'heart', 'cardiac', 'stroke', 'atrial', 'myocardial',
                                  'blood pressure', 'hypertension', 'afib', 'aortic', 'vascular']):
            return 'Cardiovascular'
        if any(k in t for k in ['alzheimer', 'parkinson', 'dementia', 'neurodegen', 'neurolog',
                                  'bipolar', 'schizophr', 'depression', 'anxiety', 'autism']):
            return 'Neurological/psychiatric'
        if any(k in t for k in ['cancer', 'carcinoma', 'melanoma', 'lymphoma', 'leukemia',
                                  'tumor', 'glioma', 'breast', 'prostate', 'colorectal', 'lung cancer']):
            return 'Cancer'
        if any(k in t for k in ['diabetes', 'insulin', 'glucose', 'bmi', 'obesity', 'metabol',
                                  'cholesterol', 'triglyceride', 'hdl', 'ldl', 'lipid']):
            return 'Metabolic'
        if any(k in t for k in ['infection', 'viral', 'bacterial', 'sepsis', 'covid', 'hiv',
                                  'influenza', 'immunity', 'immune', 'allerg', 'asthma', 'atopic']):
            return 'Infection/immunity'
        if any(k in t for k in ['height', 'weight', 'bmi', 'bone', 'lean mass', 'body mass']):
            return 'Anthropometric'
        if any(k in t for k in ['count', 'cell', 'white blood', 'red blood', 'platelet',
                                  'haemoglobin', 'hemoglobin', 'monocyte', 'lymphocyte', 'eosinophil',
                                  'neutrophil', 'basophil', 'mch', 'mcv', 'hematocrit']):
            return 'Blood cell traits'
        if any(k in t for k in ['creatinine', 'kidney', 'renal', 'egfr', 'urinary', 'albumin']):
            return 'Renal'
        if any(k in t for k in ['age', 'longevity', 'survival', 'aging', 'frailty', 'mortality']):
            return 'Aging/longevity'
        return 'Other'

    all_hits['category'] = all_hits['trait'].apply(categorize)

    log("\nHits by category:")
    for cat, grp in all_hits.groupby('category'):
        log(f"  {cat} ({len(grp)}): " + "; ".join(grp.sort_values('p')['trait'].head(5).tolist()))

    # ── PheWAS plot ──────────────────────────────────────────────────────────
    categories = sorted(all_hits['category'].unique())
    palette = plt.cm.tab20.colors
    color_map = {cat: palette[i % len(palette)] for i, cat in enumerate(categories)}
    all_hits['color'] = all_hits['category'].map(color_map)
    all_hits = all_hits.sort_values(['category', 'trait']).reset_index(drop=True)
    all_hits['x'] = range(len(all_hits))

    fig, ax = plt.subplots(figsize=(14, 6))
    for _, row in all_hits.iterrows():
        ax.scatter(row['x'], row['neglog10p'], color=row['color'], s=60, alpha=0.85, zorder=3)

    # Threshold lines
    ax.axhline(-np.log10(5e-8), color='red', linestyle='--', lw=1.2, label='p=5×10⁻⁸')
    ax.axhline(-np.log10(1e-5), color='orange', linestyle='--', lw=1.0, label='p=1×10⁻⁵')

    # Label top hits
    top = all_hits.nlargest(15, 'neglog10p')
    for _, row in top.iterrows():
        ax.text(row['x'], row['neglog10p'] + 0.1, row['trait'][:35],
                fontsize=6, ha='center', va='bottom', rotation=45)

    # Category x-tick labels
    cat_positions = all_hits.groupby('category')['x'].mean()
    ax.set_xticks(cat_positions.values)
    ax.set_xticklabels(cat_positions.index, rotation=30, ha='right', fontsize=9)

    legend_patches = [mpatches.Patch(color=color_map[c], label=c) for c in categories]
    ax.legend(handles=legend_patches, fontsize=7, loc='upper right',
              framealpha=0.7, ncol=2)

    ax.set_ylabel('-log₁₀(p)', fontsize=12)
    ax.set_title(f'PheWAS — {SNP} (CCL2 locus)\nOpenGWAS, p < 1×10⁻⁵, disease/trait studies only',
                 fontsize=12)
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.set_xlim(-1, len(all_hits))

    plt.tight_layout()
    plot_path = os.path.join(IMGDIR, 'phewas_rs11867200.png')
    plt.savefig(plot_path, dpi=150, bbox_inches='tight')
    plt.close()
    log(f"\nPheWAS plot saved to: {plot_path}")

    # ── Top hits table ───────────────────────────────────────────────────────
    log("\n\nTop 30 hits (sorted by p-value):")
    cols = ['rsid', 'trait', 'category', 'beta', 'se', 'p', 'n', 'is_ukb']
    available_cols = [c for c in cols if c in all_hits.columns]
    log(all_hits.sort_values('p')[available_cols].head(30).to_string(index=False))

    # Save CSV
    csv_path = os.path.join(OUTDIR, 'phewas_hits.csv')
    all_hits.sort_values('p').to_csv(csv_path, index=False)
    log(f"\nFull results CSV: {csv_path}")

# ─────────────────────────────────────────────────────────────────────────────
# Write results log
# ─────────────────────────────────────────────────────────────────────────────
with open(RESULTS_FILE, 'w') as f:
    f.write('\n'.join(log_lines))
print(f"\nResults written to: {RESULTS_FILE}")
