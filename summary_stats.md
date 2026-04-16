
# Summary Stats — Overview

Location: `summary_stats/`

All signature files are loaded via the unified `retrieve_summary_stats(context, ...)` function in `tools/ciim/code/hiara.py`, except GRNs which use `get_immune_grn()` in `tools/ciim/code/genomics.py`.

```python
import sys
sys.path.insert(0, '/vol/projects/BIIM/agentic_central/tools/ciim/code')
from hiara import retrieve_summary_stats
```

---

## hiara
*HIaRA*

### `immune_aging_tf_signatures_major_celltypes.csv`
*Aging TF Signatures — Major*

Per-TF aging statistics across 5 major immune cell types (CD4T, CD8T, NK, B, MONO) from multi-cohort TF activity analysis (cohorts: onek1k, abf300, aida, perez_sle; healthy donors only). 

**Load:** `retrieve_summary_stats('aging')`

---

### `immune_aging_tf_signatures_minor_celltypes.csv`
*Aging TF Signatures — Minor*

Per-TF aging statistics across 11 minor (sub) immune cell types (CD16_NK, Classic_MONO, MAIT, Memory_B, Naive_B, NonClassic_MONO, Tcm_Naive_CD4, Tcm_Naive_CD8, Tem_Effector_CD4, Tem_Temra_CD8, Tem_Trm_CD8) from multi-cohort TF activity analysis (cohorts: onek1k, abf300, aida, perez_sle; healthy donors only).

**Load:** `retrieve_summary_stats('aging', cell_resolution='minor')`

---

### `immune_aging_gene_expression_signatures_major_celltypes.csv`
*Aging Gene Expression Signatures*

Per-gene aging statistics across 5 major immune cell types from multi-cohort bulk gene expression analysis (cohorts: onek1k, abf300, aida, perez_sle; healthy donors only).

**Load:** `retrieve_summary_stats('aging', feature_type='gene_expression')`

---

### `immune_aging_ccc_signatures_major_celltypes.csv`
*Aging Cell-Cell Communication*

Cell-cell communication (L-R pair) aging statistics across major immune cell types (LIANA rank_aggregate). The `gene` column encodes interactions as `source_ct__ligand__target_ct__receptor` (double underscore) — parse in your analysis.

**Load:** `retrieve_summary_stats('aging', feature_type='ccc')`

---

### `sle_tf_signatures_major_celltypes.csv`
*SLE TF Signatures*

Differential TF activity statistics for SLE vs healthy across 5 major immune cell types (Perez cohort).

**Load:** `retrieve_summary_stats('sle')`

---

### `drug_tf_signatures_major_immune_celltypes.csv`
*Drug TF Signatures*

145 named drug perturbations (vs DMSO) differential TF activity from the OP ex-vivo drug study across 5 major immune cell types.

Drug names (`condition` / `comparison`): `5-(9-Isopropyl-8-methyl-2-morpholino-9H-purin-6-yl)pyrimidin-2-amine`, `ABT-199 (GDC-0199)`, `ABT737`, `AMD-070 (hydrochloride)`, `AT 7867`, `AT13387`, `AVL-292`, `AZ628`, `AZD-8330`, `AZD3514`, `AZD4547`, `Alogliptin`, `Amiodarone`, `Atorvastatin`, `Azacitidine`, `BAY 61-3606`, `BAY 87-2243`, `BI-D1870`, `BMS-265246`, `BMS-387032`, `BMS-536924`, `BMS-777607`, `BX 912`, `Belinostat`, `Bosutinib`, `Buspirone`, `CC-401`, `CEP-18770 (Delanzomib)`, `CEP-37440`, `CGM-097`, `CGP 60474`, `CHIR-99021`, `Cabozantinib`, `Canertinib`, `Ceritinib`, `Chlorpheniramine`, `Clemastine`, `Clomipramine`, `Clotrimazole`, `Colchicine`, `Colforsin`, `Crizotinib`, `Dabrafenib`, `Dactolisib`, `Dasatinib`, `Decitabine`, `Defactinib`, `Desloratadine`, `Disulfiram`, `Dovitinib`, `Doxorubicin`, `FK 866`, `Flutamide`, `Foretinib`, `GLPG0634`, `GO-6976`, `GSK-1070916`, `GSK256066`, `GW843682X`, `Ganetespib (STA-9090)`, `HMN-214`, `HYDROXYUREA`, `I-BET151`, `IKK Inhibitor VII`, `IMD-0354`, `IN1451`, `Idelalisib`, `Imatinib`, `Isoniazid`, `Ixabepilone`, `K-02288`, `Ketoconazole`, `LDN 193189`, `LY2090314`, `Lamivudine`, `Lapatinib`, `Linagliptin`, `MGCD-265`, `MK-5108`, `MLN 2238`, `Masitinib`, `Methotrexate`, `Midostaurin`, `Mometasone Furoate`, `Mubritinib (TAK 165)`, `Navitoclax`, `Nefazodone`, `Nilotinib`, `O-Demethylated Adapalene`, `OSI-930`, `Oprozomib (ONX 0912)`, `Oxybenzone`, `PD-0325901`, `PF-03814735`, `PF-04691502`, `PRT-062607`, `Palbociclib`, `Penfluridol`, `Perhexiline`, `Phenylbutazone`, `Pitavastatin Calcium`, `Pomalidomide`, `Porcn Inhibitor III`, `Prednisolone`, `Proscillaridin A;Proscillaridin-A`, `Protriptyline`, `Quizartinib`, `R428`, `RG7090`, `RG7112`, `RN-486`, `RVX-208`, `Raloxifene`, `Resminostat`, `Ricolinostat`, `Riociguat`, `Ruxolitinib`, `SB525334`, `SCH-58261`, `SLx-2119`, `STK219801`, `Saracatinib`, `Scriptaid`, `Selumetinib`, `Sgc-cbp30`, `Sunitinib`, `TGX 221`, `TIE2 Kinase Inhibitor`, `TL_HRAS26`, `TPCA-1`, `TR-14035`, `Tacalcitol`, `Tamatinib`, `Tipifarnib`, `Tivantinib`, `Tivozanib`, `Topotecan`, `Tosedostat`, `Trametinib`, `Vandetanib`, `Vanoxerine`, `Vardenafil`, `Vorinostat`, `YK 4-279`, `UNII-BXU45ZH6LI`.

**Load:** `retrieve_summary_stats('drug')`

---

### `cytokine_tf_signatures_major_immune_celltypes.csv`
*Cytokine TF Signatures*

90 cytokine perturbations (vs PBS) differential TF activity from the ParseBioscience ex-vivo cytokine stimulation study across 5 major immune cell types.

Cytokine names (`condition` / `comparison`): `4-1BBL`, `ADSF`, `APRIL`, `BAFF`, `C3a`, `C5a`, `CD27L`, `CD30L`, `CD40L`, `CT-1`, `Decorin`, `EGF`, `EPO`, `FGF-beta`, `FLT3L`, `FasL`, `G-CSF`, `GDNF`, `GITRL`, `GM-CSF`, `HGF`, `IFN-alpha1`, `IFN-beta`, `IFN-epsilon`, `IFN-gamma`, `IFN-lambda1`, `IFN-lambda2`, `IFN-lambda3`, `IFN-omega`, `IGF-1`, `IL-1-alpha`, `IL-1-beta`, `IL-10`, `IL-11`, `IL-12`, `IL-13`, `IL-15`, `IL-16`, `IL-17A`, `IL-17B`, `IL-17C`, `IL-17D`, `IL-17E`, `IL-17F`, `IL-18`, `IL-19`, `IL-1Ra`, `IL-2`, `IL-20`, `IL-21`, `IL-22`, `IL-23`, `IL-24`, `IL-26`, `IL-27`, `IL-3`, `IL-31`, `IL-32-beta`, `IL-33`, `IL-34`, `IL-35`, `IL-36-alpha`, `IL-36Ra`, `IL-4`, `IL-5`, `IL-6`, `IL-7`, `IL-8`, `IL-9`, `LIF`, `LIGHT`, `LT-alpha1-beta2`, `LT-alpha2-beta1`, `Leptin`, `M-CSF`, `Noggin`, `OSM`, `OX40L`, `PRL`, `PSPN`, `RANKL`, `SCF`, `TGF-beta1`, `TL1A`, `TNF-alpha`, `TPO`, `TRAIL`, `TSLP`, `TWEAK`, `VEGF`.

**Load:** `retrieve_summary_stats('cytokine')`

---

### `immune_gene_regulatory_networks_major_cts.csv`
*Immune GRN Models*

GRN models for 5 major immune cell types (CD4T, CD8T, NK, B, MONO) inferred from aging cohorts of AIDA, ABF300, OneK1K, and Perez_SLE.

**Load:** `get_immune_grn()` from `tools/ciim/code/genomics.py`

---

## virtualbiotech
*Virtual Biotech*

Three files summarising target-level biology and clinical trial outcomes, derived from the Virtual Biotech paper (Zhang et al. 2026) public data. Generated by `scripts/virtualbiotech_replication/run_analysis.py`.

---
### `virtualbiotech/target_sc_features.csv`
*Target expression features*

Expression features precomputed from the Tabula Sapiens healthy human atlas. Covers expression specificity, bimodality, and predicted AE risk per organ system.

Key columns:
- `ensembl_id` — Ensembl gene ID
- `tau_cell_type`, `tau_cell_type_max/min` — cell-type specificity (0 = ubiquitous, 1 = one cell type only)
- `tissue_tau` — tissue-level specificity
- `bimodality_score` — on/off expression pattern across cells (higher = cleaner switch)
- `ae_risk_cardiac/hepatic/renal/neural/...` — predicted adverse event risk per organ system
- `attrition_risk_phase1/2/3` — predicted trial attrition risk per phase
- `overall_safety_risk`, `multi_system_ae_count` — composite safety metrics

---

### `virtualbiotech/target_clinical_success_overall.csv`
*Target clinical success overall*

Empirical trial outcome rates per target gene across all diseases, derived from 56,707 ChEMBL-mapped trials.

Key columns:
- `targetId` — Ensembl gene ID
- `targetFromSourceId` — UniProt ID
- `n_trials` — number of trials involving this target
- `pct_reached_phase3` — % of trials that reached Phase III+
- `pct_terminated`, `pct_withdrawn` — % stopped prematurely
- `pct_endpoint_either` — % with positive primary or secondary endpoint
- `pct_phase1_to_phase2` — % of Phase I trials that progressed to Phase II

---

### `virtualbiotech/target_clinical_success_by_disease.csv`
*Target clinical success by disease*

Same as above but stratified by `disease_name` from ChEMBL. Useful for target-disease-specific queries, e.g. "how does EGFR perform in lung cancer vs breast cancer?"

Key columns: same as overall file plus `disease_name`.
