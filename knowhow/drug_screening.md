# Drug Screening for Immune Aging / Disease

Covers the workflow for nominating and prioritizing drug candidates targeting immune aging or immune-mediated disease, using available data lake resources.

---

## Goal

Identify drugs (or repurposing candidates) that reverse or attenuate aging/disease-associated transcriptional programs in immune cells — prioritizing targets with genetic support, cell-type specificity, and clinical tractability.

---

## Workflow Overview

```
Aging/disease signatures → Target prioritization → Drug matching → Evidence integration → Ranking
```

---

## 1. Define Target Space from Aging/Disease Signatures

Start from TF activity signatures in the data lake:

| Signature | Loader | Use |
|---|---|---|
| `immune_aging_signatures_major_celltypes` | `aging.py` | Age-associated TFs across CD4T, CD8T, NK, B, MONO |
| `immune_aging_tf_signatures_minor_celltypes` | `aging.py` | Same, at sub-cell-type resolution |
| `sle_tf_signatures_major_celltypes` | `aging.py` | SLE vs healthy TF shifts |
| `drug_tf_signatures_major_celltypes` | `aging.py` | Ruxolitinib TF response (positive control) |
| `cytokine_tf_signatures_major_celltypes` | `aging.py` | IL-10 TF response |

**Select targets** = TFs significantly up- or down-regulated with age/disease (filter by effect size + FDR). Also expand to TF target genes from GRNs (`get_immune_grn`).

---

## 2. Cell-Type Specificity Scoring

For each candidate target, compute how specifically it is expressed in the immune cell type of interest vs all others. Higher specificity → more likely to produce on-target immune effect with fewer off-target consequences.

- Source: scRNA atlases (`onek1k.h5ad`, `aida.h5ad`, `abf300.h5ad`, `perez_sle.h5ad`)
- Metric: tau score or fold-change of mean expression in target cell type vs all others
- Stratify by age group to confirm the aging-relevant expression pattern holds

---

## 3. Genetic Support

Does genetic variation at the target locus associate with immune aging or disease phenotypes? Targets with human genetic evidence have higher clinical success rates.

- `gwas_catalog.pkl` — GWAS hits for immune/aging traits
- `genebass_pLoF_filtered.pkl`, `genebass_missense_LC_filtered.pkl` — rare coding variant associations
- `DisGeNET.parquet` — gene-disease associations (curated + literature-mined)
- `omim.parquet` — Mendelian disease links
- `variant_table.parquet` — annotated variant catalogue

Flag targets with direct genetic support as **Tier 1**.

---

## 4. Drug Matching

Map candidate targets to known drugs or compounds:

- `BindingDB_All_202409.tsv` — experimentally measured binding affinities (protein → small molecule)
- `broad_repurposing_hub_molecule_with_smiles.parquet` + `broad_repurposing_hub_phase_moa_target_info.parquet` — approved/clinical-stage drugs with MoA and target annotations; ideal for repurposing
- `txgnn_prediction.pkl` — AI-predicted drug-disease associations (graph neural network)
- `pharmacology_base` tool — TxGNN repurposing, ADMET prediction, molecular docking (DiffDock/Vina)

For each drug hit: record **clinical phase**, **MoA**, **known indications**.

---

## 5. Drug-Drug Interaction & Safety Check

Before shortlisting, flag known interaction liabilities:

- `ddinter_antineoplastic.csv`, `ddinter_blood_organs.csv`, etc. — DDInter 2.0 interaction tables
- `pharmacology_base` → FDA adverse event query (FAERS)
- `BindingDB` — off-target binding at related proteins (selectivity check)

---

## 6. Pathway & Network Context

Confirm the target sits in a biologically relevant pathway for immune aging:

- `kg.csv` — precision medicine knowledge graph (4M+ relationships)
- `affinity_capture-ms.parquet`, `two-hybrid.parquet` — PPI networks (physical interactors)
- `msigdb_human_c7_immunologic_signature_geneset.parquet` — immunologic gene sets
- `go-plus.json` — GO functional annotations
- `gtex_tissue_gene_tpm.parquet` — tissue expression (flag if target is broadly expressed → risk)

---

## 7. Experimental Validation in Ex-Vivo Data

Cross-check candidates against existing perturbation data in the lake:

- `sc/op.h5ad` — ex-vivo drug panel on PBMCs (Ruxolitinib, Belinostat, Atorvastatin, Dabrafenib, etc.)
  - Compare TF activity signature of the drug to the aging/disease signature (reversal score)
- `sc/CXCL9.h5ad` — cytokine/drug stimulation (ruxolitinib, IFN-γ, metformin, etc.)
- Use `infer_tf_activity` to compute per-condition TF activity, then correlate with aging signature direction

A drug that **reverses** the aging TF program in ex-vivo data is a strong candidate.

---

## 8. Clinical Trial Evidence

Check whether the target has been trialed clinically and what outcomes were reported:

- Source: ClinicalTrials.gov (bulk download — see `clinical_trials.md` when available)
- Key annotations per trial: phase, condition, primary outcome, adverse events
- Flag targets where Phase II+ trials exist for immune conditions → de-risked

---

## 9. Candidate Scoring & Ranking

Score each drug-target pair across evidence layers:

| Criterion | Weight (adjust per task) |
|---|---|
| Aging/disease TF effect size | High |
| Cell-type specificity (tau) | High |
| Genetic support (GWAS / LoF) | High |
| Drug clinical phase | Medium |
| Ex-vivo reversal of aging signature | High |
| PPI / pathway relevance | Medium |
| Safety / DDI flags | Penalize |

Rank and shortlist top candidates for wet-lab follow-up or deeper computational investigation.
