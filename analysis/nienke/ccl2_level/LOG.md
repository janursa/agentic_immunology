# LOG — CCL2 expression and protein levels in the SI cohort

**Main question:** How do CCL2 mRNA expression and protein (MCP-1) levels change from young to old, and from baseline to perturbation (per age group) in the SI cohort?

---

## Data sources

| Source | File | Content |
|--------|------|---------|
| Covariates | `/vol/projects/CIIM/meta_cQTL/data/SI/covariates.tsv` | Pr IDs with age, sex, BMI, age_group flag |
| RNA-seq | `/vol/projects/CIIM/cohorts/SI/RNAseq_processed/counts/2-norm/filter/` | log2 CPM per condition (baseline, 24h_LPS, 24h_polyIC, 24h_pam3cys, 24h_CPG, 24h/7d_influenza) |
| Cytokines | `/vol/projects/CIIM/cohorts/SI/cytokines_processed/cytokines_cleaned_log2.tsv` | log2-normalised cytokine protein levels; CCL2/MCP-1 columns prefixed `pbmc_{24h|7d}_mcp1_` |

### Age group definitions
- **Young**: age ≤ 40 (n = 101 in covariates; n = 2 in RNA baseline; n = 91–98 in cytokine data depending on stimulation)
- **Middle**: age 41–59 (n = 0 in this cohort — all intermediate ages were excluded from QTL analysis, not present in covariates)
- **Old**: age ≥ 60 (n = 558 in covariates; n = 97 in RNA baseline; n = 507–544 in cytokine data)

> Note: "young" donors are poorly represented in RNA-seq baseline (n=2) and some RNA conditions have zero young samples (influenza). Protein data has better young representation (91–98 per condition for 24h stimulations).

---

## Analysis steps

### Step 1 — Age group classification
- Loaded covariates.tsv (659 rows, Pr IDs)
- Classified: young ≤40, middle 41–59, old ≥60
- Joined with RNA/cytokine data by Pr ID

### Step 2 — RNA analysis
- Extracted CCL2 row from each condition's CPM matrix
- Merged with age data; compared young vs old using Mann-Whitney U
- Computed Spearman correlation with continuous age
- Compared baseline vs each stimulation condition per age group (Mann-Whitney; samples differ per condition → unpaired test)

### Step 3 — Protein analysis
- Extracted all `mcp1` columns from cytokines_cleaned_log2.tsv
- Compared young vs old per stimulation (Mann-Whitney U)
- Computed Spearman correlation with continuous age
- Compared RPMI (baseline) vs each stimulation per age group (paired Wilcoxon — same samples have both measurements)

---

## Key findings

### CCL2 RNA — young vs old

| Condition | Δ median (old−young) | p (MWU) | Spearman ρ (age) | p |
|-----------|---------------------|---------|------------------|---|
| baseline | +0.78 | n/a (n_young=2) | −0.09 | 0.38 |
| 24h_LPS | +0.05 | 0.73 | +0.06 | 0.30 |
| **24h_polyIC** | **+1.10** | **1.5e-3** | **+0.21** | **0.01** |
| 24h_pam3cys | +0.55 | 0.30 | +0.22 | 2.6e-3 |
| 24h_CPG | +0.25 | 0.06 | +0.12 | 0.14 |

→ At RNA level: **no significant age effect at baseline** (too few young donors). After polyIC stimulation, CCL2 RNA is significantly higher in old donors (+1.1 log2 CPM, p=1.5e-3).

### CCL2 RNA — baseline vs stimulation (old donors, n=97→261/145/173/145)

All stimulations induce massive CCL2 upregulation (Δ ~+6–10 log2 CPM, p<1e-7), consistent with CCL2 being a primary innate immune response gene.

### CCL2 protein (MCP-1) — young vs old

- RPMI (24h unstimulated): young median = 6.73, old = 7.06; Δ = +0.32, p = 0.75 → **no significant difference**
- Spearman ρ(age) = +0.08, p = 0.049 → weak but marginal positive trend
- LPS: young = 13.00, old = 12.60; Δ = −0.40, p = 0.10 → non-significant
- **pam3cys: Δ = −0.27 (young higher), p = 4.8e-3** — modest but significant: younger donors produce slightly more MCP-1 after pam3cys

### CCL2 protein — RPMI vs stimulation per age group (paired)

Strong induction by TLR ligands in both age groups:
- LPS: +5.74 log2 (young, p=3e-16), +5.27 log2 (old, p=4e-84)
- pam3cys: +6.35 (young), +5.81 (old) — both highly significant
- CPG / polyIC: similar large induction in both groups
- 7d CMV: +0.29 (old, p=3e-4); 7d CoV-N: −2.0 (old, p=8e-8) — suppression after CoV-N

**Age-group difference in stimulation response:** At RNA level, old donors show stronger CCL2 upregulation after polyIC. At protein level, young donors show slightly stronger induction after pam3cys. Effects are modest.

---

## Output files

| File | Description |
|------|-------------|
| `results.txt` | Full numerical tables for all comparisons |
| `rna_young_vs_old.tsv` | RNA: young vs old per condition with stats |
| `rna_baseline_vs_stim.tsv` | RNA: baseline vs stimulation per age group |
| `protein_young_vs_old.tsv` | Protein: young vs old per stimulation |
| `protein_baseline_vs_stim.tsv` | Protein: RPMI vs stimulation per age group |
| `images/rna_baseline_by_agegroup.png` | Boxplot — CCL2 RNA at baseline by age group |
| `images/rna_vs_age_scatter.png` | Scatter — CCL2 RNA vs continuous age |
| `images/rna_stim_response_by_agegroup.png` | Δ CCL2 RNA (stim − baseline) per condition, young vs old |
| `images/protein_rpmi_by_agegroup.png` | Boxplot — CCL2 protein (RPMI 24h) by age group |
| `images/protein_vs_age_scatter.png` | Scatter — CCL2 protein vs continuous age |
| `images/protein_stim_response_by_agegroup.png` | Δ CCL2 protein (stim − RPMI) per stimulation, young vs old |
| `images/protein_young_vs_old_allstim.png` | Horizontal bars — effect size + significance, all stimulations |
