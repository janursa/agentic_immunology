"""
Re-compute TF activity using allele-specific GRNs:
  - REF samples  → grn_ref.csv   (from SI_grn_analysis)
  - Carrier samples → grn_carrier.csv (from SI_grn_analysis)
Then test LPS vs NS within each allele group using the allele-matched GRN.
"""
import sys, os
import numpy as np
import pandas as pd
import anndata as ad
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

sys.path.insert(0, '/vol/projects/BIIM/agentic_immunology/tools/ciim/code')
from genomics import infer_tf_activity

# ── Paths ──────────────────────────────────────────────────────────────────
BASE     = '/vol/projects/BIIM/agentic_immunology/temp/nienke/tfa_analysis'
GRN_REF  = '/vol/projects/BIIM/agentic_immunology/temp/nienke/SI_grn_analysis/results/grn_ref.csv'
GRN_CAR  = '/vol/projects/BIIM/agentic_immunology/temp/nienke/SI_grn_analysis/results/grn_carrier.csv'
DOSAGE   = '/vol/projects/CIIM/cohorts/SI/genotype_processed/dosage/chr17.txt'
COV      = '/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv'
RNA_NS   = '/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_ns_cpm.tsv'
RNA_LPS  = '/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_lps_cpm.tsv'
SNP_ID   = 'chr17:34248950:C:T;rs11867200'

OUT_REF  = os.path.join(BASE, 'results', 'tfa_allelespecific_REF.tsv')
OUT_CAR  = os.path.join(BASE, 'results', 'tfa_allelespecific_Carrier.tsv')
OUT_META = os.path.join(BASE, 'results', 'tfa_allelespecific_metadata.tsv')
OUT_STAT_REF = os.path.join(BASE, 'results', 'lps_vs_ns_allelespecific_REF.csv')
OUT_STAT_CAR = os.path.join(BASE, 'results', 'lps_vs_ns_allelespecific_Carrier.csv')

TFS_13 = ["CEBPB","FOS","FOSL2","GATA2","GATA3","JUND",
          "MAX","MEF2A","NFIC","PBX3","SPI1","SPIB","ETV6"]

# ── Load genotype & age ────────────────────────────────────────────────────
dos = pd.read_csv(DOSAGE, sep='\t', index_col=0)
if SNP_ID not in dos.index:
    # try columns
    dos = dos.T
dosage = dos.loc[SNP_ID].astype(float)
allele_map = dosage.apply(lambda x: 'REF' if x <= 0.5 else 'Carrier')

cov = pd.read_csv(COV, sep='\t', index_col=0)
if 'age' in cov.columns:
    age_map = cov['age']
elif 'Age' in cov.columns:
    age_map = cov['Age']
else:
    age_map = cov.iloc[:, 0]

# ── Load RNA ───────────────────────────────────────────────────────────────
def load_rna(path, condition):
    df = pd.read_csv(path, sep='\t', index_col=0)
    if df.shape[0] > df.shape[1]:
        df = df.T      # ensure samples × genes
    df.index = df.index.astype(str) + f'_{condition}'
    return df

rna_ns  = load_rna(RNA_NS,  'NS')
rna_lps = load_rna(RNA_LPS, 'LPS')
rna_all = pd.concat([rna_ns, rna_lps], axis=0)

# ── Build metadata ─────────────────────────────────────────────────────────
meta_rows = []
for sample_id in rna_all.index:
    donor = sample_id.rsplit('_', 1)[0]
    cond  = sample_id.rsplit('_', 1)[1]
    if donor not in allele_map.index:
        continue
    allele = allele_map[donor]
    age    = age_map[donor] if donor in age_map.index else np.nan
    meta_rows.append({'sample': sample_id, 'donor': donor,
                      'condition': cond, 'allele': allele, 'age': age,
                      'group': f'{allele}_{cond}'})
meta = pd.DataFrame(meta_rows).set_index('sample')
meta = meta.loc[meta.index.intersection(rna_all.index)]
print(f'Total samples with genotype: {len(meta)}')
print(meta['group'].value_counts())

# ── Function: build AnnData and run TFA ───────────────────────────────────
def run_tfa(allele_label, grn_path):
    idx   = meta[meta['allele'] == allele_label].index
    expr  = rna_all.loc[idx]
    genes = expr.columns
    mat   = np.log1p(np.clip(np.nan_to_num(expr.values.astype(np.float32), nan=0.0), 0, None))
    adata = ad.AnnData(X=mat,
                       obs=meta.loc[idx],
                       var=pd.DataFrame(index=genes))
    net   = pd.read_csv(grn_path)
    print(f'\n--- {allele_label} (n={len(idx)}) using {os.path.basename(grn_path)} ---')
    tfa_df = infer_tf_activity(adata, net)
    print(f'  TFA shape: {tfa_df.shape}')
    return tfa_df

tfa_ref = run_tfa('REF',     GRN_REF)
tfa_car = run_tfa('Carrier', GRN_CAR)

tfa_ref.to_csv(OUT_REF, sep='\t')
tfa_car.to_csv(OUT_CAR, sep='\t')
meta.to_csv(OUT_META, sep='\t')
print(f'\nSaved: {OUT_REF}')
print(f'Saved: {OUT_CAR}')

# ── LPS vs NS within each allele group (allele-specific GRN) ──────────────
def lps_vs_ns_stats(tfa_df, allele_label, out_path):
    m = meta.loc[tfa_df.index]
    records = []
    for tf in tfa_df.columns:
        lps_vals = tfa_df.loc[m[m['condition']=='LPS'].index, tf].dropna().values
        ns_vals  = tfa_df.loc[m[m['condition']=='NS'].index,  tf].dropna().values
        if len(lps_vals) < 3 or len(ns_vals) < 3:
            continue
        stat, pval = mannwhitneyu(lps_vals, ns_vals, alternative='two-sided')
        records.append({'TF': tf,
                        'median_LPS': np.median(lps_vals),
                        'median_NS':  np.median(ns_vals),
                        'effect':     np.median(lps_vals) - np.median(ns_vals),
                        'U': stat, 'p': pval,
                        'n_LPS': len(lps_vals), 'n_NS': len(ns_vals)})
    df = pd.DataFrame(records)
    _, fdr, _, _ = multipletests(df['p'], method='fdr_bh')
    df['FDR'] = fdr
    df['sig']  = df['FDR'].apply(lambda q: '***' if q<0.001 else ('**' if q<0.01 else ('*' if q<0.05 else 'ns')))
    df = df.sort_values('FDR')
    df.to_csv(out_path, index=False)
    print(f'\n{allele_label} — LPS vs NS (allele-specific GRN)')
    print(f'  Significant TFs (FDR<0.05): {(df["FDR"]<0.05).sum()} / {len(df)}')
    print(f'\n  Candidate TFs (13):')
    cand = df[df['TF'].isin(TFS_13)][['TF','effect','p','FDR','sig']]
    print(cand.to_string(index=False))
    return df

stats_ref = lps_vs_ns_stats(tfa_ref, 'REF',     OUT_STAT_REF)
stats_car = lps_vs_ns_stats(tfa_car, 'Carrier', OUT_STAT_CAR)

# ── Compare candidate TF LPS effects between allele groups ────────────────
print('\n=== Candidate TF LPS effect: REF vs Carrier (allele-specific GRN) ===')
common_tfs = [t for t in TFS_13 if t in tfa_ref.columns and t in tfa_car.columns]
rows = []
for tf in common_tfs:
    ref_row = stats_ref[stats_ref['TF']==tf]
    car_row = stats_car[stats_car['TF']==tf]
    if len(ref_row) and len(car_row):
        rows.append({'TF': tf,
                     'effect_REF': ref_row.iloc[0]['effect'],
                     'sig_REF':    ref_row.iloc[0]['sig'],
                     'effect_Carrier': car_row.iloc[0]['effect'],
                     'sig_Carrier':    car_row.iloc[0]['sig'],
                     'delta_effect':   car_row.iloc[0]['effect'] - ref_row.iloc[0]['effect']})
comp = pd.DataFrame(rows).sort_values('delta_effect', key=abs, ascending=False)
print(comp.to_string(index=False))
comp.to_csv(os.path.join(BASE, 'results', 'candidate_tfs_allelespecific_comparison.csv'), index=False)
