"""
Check sample sizes for GRN analysis:
- 4 groups: REF/REF × {RPMI, LPS} and ALT/ALT × {RPMI, LPS}
- Age filter: > 60
- Data: RNA-seq (TF expression) for TFs + CCL2
"""
import pandas as pd
import numpy as np

# --- File paths ---
DOSAGE = "/vol/projects/CIIM/cohorts/SI/genotype_processed/dosage/chr17.txt"
COVARIATES = "/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv"
RNA_NS = "/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_ns_cpm.tsv"
RNA_LPS = "/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/24h_lps_cpm.tsv"

SNP_ID = "chr17:34248950:C:T;rs11867200"

TFS_16 = ["CEBPB", "FOS", "FOSL2", "GATA2", "GATA3", "JUN", "JUND",
          "MAX", "MEF2A", "MYC", "NFIC", "PBX3", "TCF12",
          "SPI1", "SPIB", "ETV6"]
TARGET = "CCL2"

# --- Load dosage ---
print("Loading dosage file...")
dos = pd.read_csv(DOSAGE, sep="\t", index_col=0)
snp_row = dos.loc[SNP_ID]
dosage = snp_row.astype(float)
print(f"  Dosage: {len(dosage)} samples")

# Classify genotype (continuous dosage → 0/1/2)
genotype = pd.cut(dosage, bins=[-0.5, 0.5, 1.5, 2.5], labels=["REF", "HET", "ALT"])
genotype = genotype.dropna()
print(f"  Genotype counts (all): {genotype.value_counts().to_dict()}")

# --- Load covariates ---
print("Loading covariates...")
cov = pd.read_csv(COVARIATES, sep="\t", index_col=0)
# Transpose if needed (rows should be samples)
if "age" not in cov.index and "age" in cov.columns:
    pass  # rows=samples, cols=covariates
elif "age" in cov.index:
    cov = cov.T  # rows=covariates → transpose to rows=samples

print(f"  Covariates shape: {cov.shape}")
print(f"  Columns: {list(cov.columns[:10])}")

# Get age
age_col = [c for c in cov.columns if "age" in c.lower()][0]
age = pd.to_numeric(cov[age_col], errors="coerce")
print(f"  Age range: {age.min():.0f}–{age.max():.0f}, mean={age.mean():.1f}")

# Filter age > 60
old_samples = age[age > 60].index
print(f"  Samples with age > 60: {len(old_samples)}")

# Intersect with genotype
geno_old = genotype[genotype.index.isin(old_samples)]
print(f"\nGenotype × age>60:")
for g in ["REF", "HET", "ALT"]:
    n = (geno_old == g).sum()
    print(f"  {g}: n={n}")

# --- Load RNA-seq ---
print("\nLoading RNA-seq files (headers only)...")
# Check genes
rna_ns = pd.read_csv(RNA_NS, sep="\t", index_col=0, nrows=0)
rna_lps = pd.read_csv(RNA_LPS, sep="\t", index_col=0, nrows=0)
ns_samples = list(rna_ns.columns)
lps_samples = list(rna_lps.columns)
print(f"  NS samples: {len(ns_samples)}, LPS samples: {len(lps_samples)}")

# Check gene availability
rna_ns_full = pd.read_csv(RNA_NS, sep="\t", index_col=0)
rna_lps_full = pd.read_csv(RNA_LPS, sep="\t", index_col=0)
genes_check = TFS_16 + [TARGET]
ns_present = [g for g in genes_check if g in rna_ns_full.index]
lps_present = [g for g in genes_check if g in rna_lps_full.index]
ns_missing = [g for g in genes_check if g not in rna_ns_full.index]
lps_missing = [g for g in genes_check if g not in rna_lps_full.index]
print(f"  NS genes present: {len(ns_present)}/17 (missing: {ns_missing})")
print(f"  LPS genes present: {len(lps_present)}/17 (missing: {lps_missing})")

# --- Compute final group sizes ---
print("\n=== FINAL GROUP SIZES (age>60, RNA-seq) ===")

for stim, samples in [("RPMI/NS", ns_samples), ("LPS", lps_samples)]:
    rna_set = set(samples)
    for geno in ["REF", "ALT"]:
        geno_ids = set(geno_old[geno_old == geno].index)
        n = len(geno_ids & rna_set)
        print(f"  {geno} × {stim}: n={n}")

# Full breakdown table
print("\n=== DETAILED BREAKDOWN ===")
rows = []
for geno in ["REF", "HET", "ALT"]:
    geno_ids_all = set(genotype[genotype == geno].index)
    geno_ids_old = set(geno_old[geno_old == geno].index)
    n_geno = len(geno_ids_all)
    n_old = len(geno_ids_old)
    n_ns = len(geno_ids_old & set(ns_samples))
    n_lps = len(geno_ids_old & set(lps_samples))
    rows.append({"Genotype": geno, "All": n_geno, "Age>60": n_old, "Age>60+RNA_NS": n_ns, "Age>60+RNA_LPS": n_lps})

df = pd.DataFrame(rows)
print(df.to_string(index=False))

print("\n=== SAMPLE IDs FOR EACH GROUP ===")
for stim, samples in [("NS", ns_samples), ("LPS", lps_samples)]:
    for geno in ["REF", "ALT"]:
        geno_ids = set(geno_old[geno_old == geno].index)
        intersect = sorted(geno_ids & set(samples))
        print(f"  {geno}_{stim}: {intersect[:5]}... (n={len(intersect)})")
