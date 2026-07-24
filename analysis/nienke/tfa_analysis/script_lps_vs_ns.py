import sys, os
import numpy as np
import pandas as pd
from scipy.stats import mannwhitneyu
from statsmodels.stats.multitest import multipletests

BASE     = '/vol/projects/BIIM/agentic_immunology/temp/nienke/tfa_analysis'
TFA_PATH = os.path.join(BASE, 'results', 'tf_activity.tsv')
META_PATH= os.path.join(BASE, 'results', 'sample_metadata.tsv')

tfa  = pd.read_csv(TFA_PATH,  sep='\t', index_col=0)
meta = pd.read_csv(META_PATH, sep='\t', index_col=0)
shared = tfa.index.intersection(meta.index)
tfa  = tfa.loc[shared]
meta = meta.loc[shared]

TFS_13 = ["CEBPB","FOS","FOSL2","GATA2","GATA3","JUND",
          "MAX","MEF2A","NFIC","PBX3","SPI1","SPIB","ETV6"]

def test_lps_vs_ns(allele_label):
    lps_idx = meta[(meta['allele']==allele_label) & (meta['condition']=='LPS')].index
    ns_idx  = meta[(meta['allele']==allele_label) & (meta['condition']=='NS')].index
    lps = tfa.loc[lps_idx]
    ns  = tfa.loc[ns_idx]
    print(f"\n{allele_label}: LPS n={len(lps)}, NS n={len(ns)}")

    records = []
    for tf in tfa.columns:
        l = lps[tf].dropna().values
        n = ns[tf].dropna().values
        if len(l) < 3 or len(n) < 3:
            continue
        stat, pval = mannwhitneyu(l, n, alternative='two-sided')
        records.append({
            'TF': tf,
            'median_LPS': np.median(l),
            'median_NS':  np.median(n),
            'effect':     np.median(l) - np.median(n),
            'U': stat, 'p': pval,
        })
    df = pd.DataFrame(records)
    _, fdr, _, _ = multipletests(df['p'], method='fdr_bh')
    df['FDR'] = fdr
    df['sig']  = df['FDR'].apply(lambda q: '***' if q<0.001 else ('**' if q<0.01 else ('*' if q<0.05 else 'ns')))
    df = df.sort_values('FDR')
    df.to_csv(os.path.join(BASE, f'results/lps_vs_ns_stats_{allele_label}.csv'), index=False)

    sig = df[df['FDR'] < 0.05]
    print(f"  Significant TFs (FDR<0.05): {len(sig)} / {len(df)}")
    print(f"\n  Top 20 by FDR:")
    print(sig.head(20)[['TF','effect','p','FDR','sig']].to_string(index=False))

    print(f"\n  Candidate TFs (13):")
    cand = df[df['TF'].isin(TFS_13)][['TF','effect','p','FDR','sig']]
    print(cand.to_string(index=False))
    return df

ref_df     = test_lps_vs_ns('REF')
carrier_df = test_lps_vs_ns('Carrier')

# overlap
ref_sig     = set(ref_df[ref_df['FDR']<0.05]['TF'])
carrier_sig = set(carrier_df[carrier_df['FDR']<0.05]['TF'])
both   = ref_sig & carrier_sig
ref_only     = ref_sig - carrier_sig
carrier_only = carrier_sig - ref_sig

print(f"\n== Overlap (FDR<0.05) ==")
print(f"  Both:          {len(both)}")
print(f"  REF only:      {len(ref_only)}")
print(f"  Carrier only:  {len(carrier_only)}")
print(f"\n  Candidate TFs significant in either allele:")
cand_sig = (ref_sig | carrier_sig) & set(TFS_13)
for tf in TFS_13:
    in_ref = tf in ref_sig
    in_car = tf in carrier_sig
    if in_ref or in_car:
        print(f"    {tf}: REF={'sig' if in_ref else 'ns'}, Carrier={'sig' if in_car else 'ns'}")
if not cand_sig:
    print("    None of the 13 candidate TFs significant in either group")
