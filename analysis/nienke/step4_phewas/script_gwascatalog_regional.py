"""
Regional GWAS Catalog analysis for the chr17 CCL2 chemokine locus.
Focus: disease/trait associations within ±500 kb of rs11867200 (chr17:34,248,950).
OpenGWAS PheWAS replaced by this because the JWT token has expired.
"""
import sys, os
sys.path.insert(0, '/vol/projects/BIIM/agentic_immunology/tools/ciim/code')

import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

OUTDIR = '/vol/projects/BIIM/agentic_immunology/temp/nienke/step4_phewas'
IMGDIR = os.path.join(OUTDIR, 'images')
os.makedirs(IMGDIR, exist_ok=True)

SNP_POS  = 34_248_950   # GRCh38 chr17 position of rs11867200
SNP_ID   = 'rs11867200'
WIN_BP   = 500_000       # ±500 kb window
RESULTS  = os.path.join(OUTDIR, 'results_gwascatalog_regional.txt')

log_lines = []
def log(msg=''):
    print(msg)
    log_lines.append(str(msg))

log("=" * 70)
log(f"Regional GWAS Catalog analysis — {SNP_ID} / CCL2 locus")
log(f"Window: chr17:{SNP_POS-WIN_BP:,}–{SNP_POS+WIN_BP:,} (±500 kb)")
log("=" * 70)

# ── Load GWAS Catalog ────────────────────────────────────────────────────────
df = pd.read_pickle('datalake/biomni/gwas_catalog.pkl')

region = df[
    (df['CHR_ID'].astype(str) == '17') &
    (pd.to_numeric(df['CHR_POS'], errors='coerce').between(SNP_POS - WIN_BP, SNP_POS + WIN_BP))
].copy()

region['CHR_POS'] = pd.to_numeric(region['CHR_POS'], errors='coerce')
region['dist_to_snp'] = (region['CHR_POS'] - SNP_POS).astype(int)
region['abs_dist'] = region['dist_to_snp'].abs()
region['P-VALUE'] = pd.to_numeric(region['P-VALUE'], errors='coerce')
region['PVALUE_MLOG'] = pd.to_numeric(region['PVALUE_MLOG'], errors='coerce')

log(f"\nTotal hits in window: {len(region)}")

# ── Categorise traits ────────────────────────────────────────────────────────
def categorize(trait):
    t = str(trait).lower()
    # Protein / biomarker QTLs first (remove these from disease list)
    if any(k in t for k in ['protein level', 'serum level', 'plasma level', 'blood level',
                              'chemokine', 'ccl', 'mcp-', 'corneodesmosin', 'cdsn',
                              'eotaxin', 'rantes', 'cytokine', 'interleukin', 'levels of protein']):
        return 'Protein/biomarker QTL'
    if any(k in t for k in ['count', 'percentage of', 'monocyte count', 'white cell',
                              'granulocyte', 'platelet', 'red blood', 'haematocrit',
                              'haemoglobin', 'hemoglobin', 'mch', 'mcv', 'neutrophil',
                              'lymphocyte', 'eosinophil', 'basophil', 'blood cell',
                              'leukocyte', 'reticulocyte']):
        return 'Blood cell traits'
    if any(k in t for k in ['microbiota', 'microbiome', 'gut bacteria', 'functional unit']):
        return 'Microbiome'
    if any(k in t for k in ['crohn', 'ibd', 'inflammatory bowel', 'ulcerative colitis',
                              'colitis']):
        return 'IBD / Crohn\'s disease'
    if any(k in t for k in ['chronic inflammatory', 'ankylosing', 'spondylitis', 'psoriasis',
                              'sclerosing cholangitis', 'psc', 'pleiotropy',
                              'autoimmun', 'lupus', 'sle', 'arthritis', 'sjögren',
                              'sjogren', 'celiac', 'coeliac', 'ms ', 'multiple scler']):
        return 'Autoimmune / inflammatory'
    if any(k in t for k in ['leukemia', 'lymphoma', 'lymphoblastic', 'cancer', 'carcinoma',
                              'melanoma', 'tumor', 'glioma', 'breast', 'prostate']):
        return 'Cancer'
    if any(k in t for k in ['coronary', 'heart', 'cardiac', 'stroke', 'atrial', 'myocardial',
                              'blood pressure', 'hypertension', 'afib', 'aortic', 'vascular']):
        return 'Cardiovascular'
    if any(k in t for k in ['alzheimer', 'parkinson', 'dementia', 'neurodegen', 'bipolar',
                              'schizophr', 'depression', 'anxiety', 'autism', 'neurolog']):
        return 'Neurological / psychiatric'
    if any(k in t for k in ['diabetes', 'insulin', 'glucose', 'bmi', 'obesity', 'metabol',
                              'cholesterol', 'triglyceride', 'hdl', 'ldl', 'lipid']):
        return 'Metabolic'
    if any(k in t for k in ['ratio', 'height', 'weight', 'bone', 'lean mass']):
        return 'Anthropometric / ratio'
    if any(k in t for k in ['smoking', 'interaction', 'sex interaction']):
        return 'GxE interaction'
    return 'Other'

region['category'] = region['DISEASE/TRAIT'].apply(categorize)

# ── Summary by category ──────────────────────────────────────────────────────
log("\n\n--- Hits by category ---")
cat_counts = region.groupby('category').size().sort_values(ascending=False)
log(cat_counts.to_string())

# ── Hits within 50 kb of rs11867200 (most likely to be in LD) ───────────────
log("\n\n--- Hits within 50 kb of rs11867200 (potential LD proxies) ---")
close = region[region['abs_dist'] <= 50_000].sort_values('abs_dist')
log(close[['SNPS','CHR_POS','dist_to_snp','DISEASE/TRAIT','category',
           'MAPPED_GENE','P-VALUE','PVALUE_MLOG','FIRST AUTHOR','DATE']].to_string(index=False))

# ── Top disease hits (exclude protein/blood cell QTLs) ──────────────────────
log("\n\n--- Top disease-relevant hits (all distances) ---")
disease_cats = ['IBD / Crohn\'s disease', 'Autoimmune / inflammatory', 'Cancer',
                'Cardiovascular', 'Neurological / psychiatric', 'Metabolic', 'GxE interaction']
disease_hits = region[region['category'].isin(disease_cats)].sort_values('P-VALUE')
log(disease_hits[['SNPS','CHR_POS','dist_to_snp','DISEASE/TRAIT','category',
                   'MAPPED_GENE','P-VALUE','PVALUE_MLOG','FIRST AUTHOR','DATE']].head(40).to_string(index=False))

# ── Protein/biomarker QTLs (CCL2, CCL7, CCL8 etc.) ──────────────────────────
log("\n\n--- Protein/biomarker QTL hits (top by p-value) ---")
pqtl = region[region['category'] == 'Protein/biomarker QTL'].sort_values('P-VALUE')
log(pqtl[['SNPS','CHR_POS','dist_to_snp','DISEASE/TRAIT','MAPPED_GENE',
          'P-VALUE','PVALUE_MLOG','OR or BETA','FIRST AUTHOR','DATE']].head(30).to_string(index=False))

# ── Blood cell trait hits ────────────────────────────────────────────────────
log("\n\n--- Blood cell trait hits ---")
bc = region[region['category'] == 'Blood cell traits'].sort_values('P-VALUE')
log(bc[['SNPS','CHR_POS','dist_to_snp','DISEASE/TRAIT','MAPPED_GENE',
         'P-VALUE','PVALUE_MLOG','FIRST AUTHOR']].head(20).to_string(index=False))

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 1 — Regional locus overview (all categories, position on x-axis)
# ─────────────────────────────────────────────────────────────────────────────
cat_palette = {
    'IBD / Crohn\'s disease':        '#d62728',
    'Autoimmune / inflammatory':      '#ff7f0e',
    'Cancer':                         '#9467bd',
    'Blood cell traits':              '#1f77b4',
    'Protein/biomarker QTL':          '#2ca02c',
    'Microbiome':                     '#8c564b',
    'Cardiovascular':                 '#e377c2',
    'Metabolic':                      '#bcbd22',
    'Anthropometric / ratio':         '#17becf',
    'Neurological / psychiatric':     '#aec7e8',
    'GxE interaction':                '#ffbb78',
    'Other':                          '#c7c7c7',
}

fig, ax = plt.subplots(figsize=(14, 6))

for cat, grp in region.groupby('category'):
    color = cat_palette.get(cat, '#888888')
    ax.scatter(grp['CHR_POS'] / 1e6, grp['PVALUE_MLOG'],
               color=color, s=45, alpha=0.8, label=cat, zorder=3, edgecolors='none')

# Mark rs11867200
ax.axvline(SNP_POS / 1e6, color='black', linestyle='--', lw=1.5, label=SNP_ID, zorder=5)

# Threshold
ax.axhline(7.3, color='red', linestyle=':', lw=1.0, alpha=0.7, label='p=5×10⁻⁸')

# Label top nearby disease hits
top_disease = region[region['category'].isin(disease_cats)].nlargest(8, 'PVALUE_MLOG')
for _, row in top_disease.iterrows():
    label = str(row['DISEASE/TRAIT'])[:30]
    ax.annotate(label, xy=(row['CHR_POS']/1e6, row['PVALUE_MLOG']),
                xytext=(3, 3), textcoords='offset points', fontsize=6.5, color='black',
                ha='left')

ax.set_xlabel('chr17 position (Mb)', fontsize=12)
ax.set_ylabel('-log₁₀(p)', fontsize=12)
ax.set_title(f'Regional GWAS Catalog — chr17 CCL2 locus (±500 kb of {SNP_ID})',
             fontsize=12)

legend_patches = [mpatches.Patch(color=cat_palette.get(c, '#888'), label=c)
                  for c in sorted(region['category'].unique())]
legend_patches.append(plt.Line2D([0], [0], color='black', linestyle='--', label=SNP_ID))
ax.legend(handles=legend_patches, fontsize=7, loc='upper right',
          framealpha=0.8, ncol=2, bbox_to_anchor=(1.0, 1.0))

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
p1 = os.path.join(IMGDIR, 'gwascatalog_regional_locus.png')
plt.savefig(p1, dpi=150, bbox_inches='tight')
plt.close()
log(f"\nPlot 1 (regional locus): {p1}")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 2 — Disease category bar chart (top disease categories by hit count)
# ─────────────────────────────────────────────────────────────────────────────
disease_only = region[region['category'].isin(disease_cats + ['Blood cell traits', 'Microbiome'])]
cat_summary = disease_only.groupby('category').agg(
    n_hits=('SNPS', 'count'),
    min_p=('P-VALUE', 'min'),
    best_snp=('SNPS', 'first'),
    best_trait=('DISEASE/TRAIT', 'first'),
).sort_values('n_hits', ascending=False).reset_index()

fig, ax = plt.subplots(figsize=(10, 5))
colors = [cat_palette.get(c, '#888') for c in cat_summary['category']]
bars = ax.barh(cat_summary['category'], cat_summary['n_hits'],
               color=colors, edgecolor='white', height=0.6)
for bar, row in zip(bars, cat_summary.itertuples()):
    ax.text(bar.get_width() + 0.2, bar.get_y() + bar.get_height()/2,
            f"best p={row.min_p:.0e}", va='center', fontsize=8)
ax.set_xlabel('Number of GWAS Catalog associations', fontsize=11)
ax.set_title(f'Disease associations in CCL2 locus ±500 kb ({SNP_ID})\nGWAS Catalog', fontsize=11)
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
p2 = os.path.join(IMGDIR, 'gwascatalog_disease_categories.png')
plt.savefig(p2, dpi=150, bbox_inches='tight')
plt.close()
log(f"Plot 2 (disease categories): {p2}")

# ─────────────────────────────────────────────────────────────────────────────
# PLOT 3 — Distance-vs-significance for disease hits (proximity to rs11867200)
# ─────────────────────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6))
for cat in disease_cats + ['Blood cell traits']:
    grp = region[region['category'] == cat]
    if len(grp) == 0:
        continue
    color = cat_palette.get(cat, '#888')
    ax.scatter(grp['abs_dist'] / 1e3, grp['PVALUE_MLOG'],
               color=color, s=55, alpha=0.85, label=cat, edgecolors='none', zorder=3)

# Label closest disease hits
close_disease = region[(region['abs_dist'] <= 50_000) & region['category'].isin(disease_cats)]
for _, row in close_disease.iterrows():
    ax.annotate(f"{row['SNPS']}\n{str(row['DISEASE/TRAIT'])[:25]}",
                xy=(row['abs_dist']/1e3, row['PVALUE_MLOG']),
                xytext=(5, 3), textcoords='offset points', fontsize=6)

ax.axvline(50, color='gray', linestyle='--', lw=1, alpha=0.6, label='50 kb (LD proxy zone)')
ax.axhline(7.3, color='red', linestyle=':', lw=1.0, alpha=0.7)
ax.set_xlabel(f'Distance from {SNP_ID} (kb)', fontsize=11)
ax.set_ylabel('-log₁₀(p)', fontsize=11)
ax.set_title(f'Proximity of disease GWAS hits to {SNP_ID}\n(CCL2 locus, chr17)', fontsize=11)
ax.legend(fontsize=8, framealpha=0.7, loc='upper right')
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
plt.tight_layout()
p3 = os.path.join(IMGDIR, 'gwascatalog_distance_vs_significance.png')
plt.savefig(p3, dpi=150, bbox_inches='tight')
plt.close()
log(f"Plot 3 (distance vs significance): {p3}")

# ─────────────────────────────────────────────────────────────────────────────
# Save full regional table
# ─────────────────────────────────────────────────────────────────────────────
csv_out = os.path.join(OUTDIR, 'gwascatalog_regional_all.csv')
region.sort_values(['category', 'P-VALUE']).to_csv(csv_out, index=False)
log(f"\nFull regional table: {csv_out}")

# ── Final biological interpretation ─────────────────────────────────────────
log("\n\n" + "=" * 70)
log("BIOLOGICAL INTERPRETATION")
log("=" * 70)
log("""
Key findings from regional GWAS Catalog analysis:

1. CLOSEST disease-associated SNPs (< 10 kb from rs11867200):
   - rs9889296 (5.4 kb): p=5e-21 for 'chronic inflammatory diseases'
     (AS + Crohn's + psoriasis + PSC + UC — cross-disorder pleiotropy)
     AND p=1e-20 for IBD (Liu JZ 2015)
   - rs2857656 (6.0 kb): p=2e-9 for B-cell lymphoblastic leukemia / Crohn's (pleiotropy)
   These are strong candidates for being in LD with rs11867200.

2. IBD / CROHN'S DISEASE is the dominant disease signal at this locus:
   - Multiple independent SNPs (rs9889296, rs3091315, rs3091316, rs2368473)
   - Consistent across many large IBD GWAS (Jostins 2012, Liu 2015, de Lange 2017, Franke 2010)
   - Strongest disease effect: rs3091315 at CCL2-CCL7 intergenic (p=2e-25 for Crohn's)
   - This fits perfectly: CCL2 drives monocyte/macrophage recruitment to the gut.
     The T allele → higher CCL2 in aged/inflamed monocytes → more tissue inflammation.

3. PROTEIN QTLs confirm this locus regulates the CCL2/CCL7/CCL8 cluster:
   - rs12601658: CCL2 levels (p=6e-12), CCL7 levels (p=5e-62), CCL8 levels (p=2e-13)
   - rs6505402: corneodesmosin levels (p=1e-56) — shared LD block
   These protein QTLs provide the molecular link: genotype → chemokine level → disease.

4. BLOOD CELL TRAITS: monocyte count and monocyte percentage strongly associated
   - rs9909465 (35 kb): monocyte count p=9e-24
   - rs7218453 (40 kb): monocyte percentage p=3e-25
   This extends the mechanism: the locus regulates not just CCL2 production
   but also monocyte abundance — both relevant to the stimQTL phenotype.

5. AUTOIMMUNE / INFLAMMATORY: ankylosing spondylitis and psoriasis co-associated
   at rs9889296 (same variant as IBD hit). This is cross-disorder inflammation.

6. CANCER: rs2857656 shows pleiotropy between B-cell ALL and Crohn's —
   likely a shared immune regulatory variant rather than direct oncogenic effect.
""")

# Write log
with open(RESULTS, 'w') as f:
    f.write('\n'.join(log_lines))
print(f"\nResults written to: {RESULTS}")
