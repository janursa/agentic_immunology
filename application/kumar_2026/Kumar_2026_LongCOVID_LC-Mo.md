# A distinct monocyte transcriptional state links systemic immune dysregulation to pulmonary impairment in long COVID

**Authors:** Saumya Kumar, Chaofan Li, Liang Zhou, et al. (Yang Li, Jie Sun, Thomas Illig — co-senior)
**Journal / Venue:** Nature Immunology
**Year:** 2026
**DOI:** 10.1038/s41590-025-02387-1
**PDF:** `/Users/jno24/Documents/papers/s41590-025-02387-1.pdf`
**Tags:** #literature/reviewed

---

## What Is This Study About?

Long COVID (LC) affects 10–20% of people after SARS-CoV-2 infection. Patients suffer from persistent fatigue, breathing difficulties, and other symptoms for months to years — but the immune mechanisms driving this are poorly understood. Most prior studies did not separate patients by how severe their *original* acute infection was, which matters because severe COVID-19 leaves its own lasting immune imprint unrelated to long COVID per se.

**The central question:** What immune changes are specifically associated with long COVID — not acute COVID, not post-ICU complications — and how do those changes explain persistent fatigue and lung impairment?

**The approach:** Profile PBMCs from 5 independent cohorts using single-cell transcriptomics (RNA + chromatin accessibility), plasma cytokines, flow cytometry, and bronchoalveolar lavage (BAL) fluid. Critically, all patients are stratified by acute infection severity (mild/moderate WHO 1–5 vs. severe WHO 6–9) and long COVID patients are compared to both acute-infection controls and fully recovered individuals.

**The answer:** A distinct CD14⁺ monocyte transcriptional state — called **LC-Mo** (cluster MC4) — is specifically enriched in long COVID patients who had a *mild or moderate* acute infection. It is characterised by profibrotic TGFβ and WNT–β-catenin signalling, correlates with fatigue severity and blood oxygen levels, and maps to a profibrotic macrophage profile in the lungs of patients with severe respiratory symptoms. These same patients show blunted interferon responses upon monocyte stimulation, indicating functional immune suppression.

**Why it matters:** LC-Mo provides a specific cellular mechanism — not just an inflammatory marker, but a profibrotic, epigenetically encoded monocyte program — plausibly connecting circulating immune dysfunction to lung fibrosis and persistent symptoms. It also yields testable protein markers (TGFβ1, CALR, CD120b, HLA-DQ) and therapeutic targets (TGFβ, WNT, AP-1/NF-κB1 axis).

---

## TL;DR

A profibrotic CD14⁺ monocyte state (LC-Mo/MC4), driven by TGFβ/WNT/AP-1/NF-κB1 signalling and enriched specifically in mild-to-moderate long COVID, correlates with fatigue severity, impaired blood oxygenation, and profibrotic lung macrophage profiles — linking systemic immune dysfunction to persistent respiratory impairment.

## Background & Motivation

Long COVID is heterogeneous. Prior studies conflated patients with mild and severe acute infections, masking LC-specific molecular signatures. This study systematically stratifies by acute WHO severity score and uses multi-cohort, multi-modal profiling to isolate immune changes attributable to LC itself rather than to the severity of the original infection.

---

## Input Data — 5 Cohorts

### Cohort 1 — Primary discovery (single-cell multiome)

| Item | Detail |
|------|--------|
| Source | Hannover Medical School (MHH), Germany |
| Recruited | April 2020 – August 2021 |
| Sample type | PBMCs (frozen, Ficoll gradient) |
| Assay | snRNA-seq + snATAC-seq (10x Genomics Chromium Next GEM Single Cell Multiome ATAC + Gene Expression, protocol CG000338 Rev C) |
| Sequencing | Illumina NovaSeq 6000; min 20,000 read pairs/cell (RNA), 25,000 (ATAC) |
| Genome | GRCh38-2020-A-2.0.0 (10x Genomics) |
| Total samples | 78 (45 donors; 9 longitudinal, 36 cross-sectional) |
| Total cells | ~118,000 high-quality cells |
| Data access | EGA: EGAS50000000142, EGAS50000000143, EGAS0000001215, EGAS0000001216 |

**Groups:**

| Group | n donors | Notes |
|-------|---------|-------|
| AIM (acute, mild/moderate) | 7 | WHO 1–5; 42.8% women, median age 52 |
| AIS (acute, severe) | 4 | WHO 6–9; 50% women, median age 37 |
| LCAM (long COVID, mild/mod AI) | 29 | 8 longitudinal (2–3 tp), 21 single; 58% women, median age 49 |
| LCAS (long COVID, severe AI) | 8 | 3 longitudinal (2–4 tp), 5 single; 25% women, median age 46 |
| RLC (recovered from LC) | 8 | 4–8 months of LC, then recovered |
| NI (prepandemic non-infected) | 6 | 50% women, median age 40 |

**Time strata (months post-infection):** T2 = 1.7–2.9, T3 = 3–5.9, T4 = 6–8.9, T5 = 9–11

**Clinical variables collected per visit:** blood gas (pO2), FAS fatigue score (threshold >21), mMRC dyspnea scale (0–4), pulmonary function tests (PFT), bronchial dilation test (BDT), ECG, quality-of-life (QoL)

### Cohort 2 — Plasma cytokines

| Item | Detail |
|------|--------|
| Source | MHH (May 2020 – August 2021) |
| Sample type | Plasma, 238 total samples |
| Assay | Quanterix HD SP-X (10-plex) + Simoa 4-plex |
| Cytokines measured | IL-12p70, IL-1β, IL-6, IL-8, TNF, IFNγ, IL-10, IL-22, CCL2, CXCL10, CCL19, CXCL11 (IL-4 and IL-5 excluded — below detection) |
| Groups | LCAM n=117, LCAS n=25, NI n=33 (prepandemic) |
| Time | 1.5–11 months post-infection |

### Cohort 3 — scRNA-seq validation (respiratory PASC)

| Item | Detail |
|------|--------|
| Source | Pulmonary Rehabilitation Clinic, Schönau am Königssee, Germany |
| Recruited | October–November 2023 |
| Sample type | PBMCs, single timepoint, 8–42 months post-infection |
| Assay | scRNA-seq (10x Chromium GEM-X 3' v4; NovaSeq 6000; min 20,000 read pairs/cell) |
| Groups | LCAM n=8 (all respiratory PASC): Resp-PASC n=5, Resp-PASC-BHR n=3 |

### Cohort 4 — Flow cytometry protein validation

| Item | Detail |
|------|--------|
| Source | MHH (August 2020 – June 2022) |
| Sample type | Cryopreserved PBMCs |
| Assay | Flow cytometry, Sony ID7000 spectral analyzer (5-laser), FlowJo v10.10 |
| 11 proteins | HLA-DR, HLA-DQ, CD105, CD51, TGFβ1, CD99, CD120b, CALR, IRF8, IFNGR1, CD163 |
| Groups | LCAM n=29, LCAS n=11, RA+NI n=10 |

### Cohort 5 — Public PBMC + BAL dataset

| Item | Detail |
|------|--------|
| Source | Mayo Clinic; Li et al., *Sci. Transl. Med.* 2024 |
| GEO accession | **GSE263817** (publicly available — no access application needed) |
| Sample type | PBMCs (n=11) + BAL fluid (n=9) |
| Assay | scRNA-seq |
| Groups | LCUN n=9 [Resp-PASC n=5, nonResp-PASC n=4]; NI n=2 |

### Functional stimulation assay (Cohort 1 subset)

PBMCs from LCAM n=7, LCAS n=5, RLC n=6 at timepoints T2 and T4.
Stimulated 4h with heat-inactivated *P. aeruginosa* (clinical isolate CH5464, **2.5×10⁶ CFU/mL**).
Assay: scMultiome on both stimulated and unstimulated cells.

---

## Bioinformatics Pipeline

| Step | Tool / Parameters |
|------|------------------|
| FASTQ | cellranger-arc mkfastq |
| Alignment | cellranger-arc count v2.0.2, GRCh38-2020-A-2.0.0 |
| Demultiplexing | Souporcell v2.4 + genotyping (GSA-MDv3 array, imputed via TOPMed r3 + Minimac4, 6,050,031 variants) |
| QC filters (C1) | nCount_RNA < 6,000; nCount_ATAC < 15,000; mito% < 20; RNA features < 3,000; TSS enrichment 1–10; nucleosome_signal < 2 |
| QC filters (C3) | nCount_RNA < 8,000; nFeature_RNA < 3,500; mito% < 20 |
| Integration | Seurat v5.0, RPCAIntegration, top 30 PCs |
| Cell annotation | Azimuth celltype.l2 + canonical markers |
| ATAC integration | Signac v1.13, rlsi, top 30 dims |
| Clustering | CD14+ monocytes: resolution 0.2 → 4 clusters (MC1–MC4); CD8+T & NK: resolution 0.4 → 5 clusters each |
| DGE | Seurat FindMarkers; pseudobulk via DESeq2 (adj P < 0.05, log2FC > 0.8) |
| GSEA | fgsea; Hallmark + REACTOME pathways; adj P < 0.1 |
| Pathway AUC per cell | AUCell R package (raw counts) |
| Neighborhood abundance | MiloR; k=50, d=50; spatial FDR < 0.1 |
| Pseudotime | destiny (diffusion maps, 40 PCs) + Slingshot (3 lineages; NI-enriched cluster as root) |
| Peak calling | Macs3 + Ensembl.Db.Hsapiens.v86; peaks linked to genes via LinkPeaks |
| TF motif enrichment | ChromVar + Jaspar2020 (human motifs only) |
| Statistics | Wilcoxon rank-sum; Spearman correlation; Benjamini-Hochberg correction throughout |

**Code:** github.com/CiiM-Bioinformatics-group/LongCOVID

---

## Key Results

### 1. LC-Mo transcriptional state (MC4) — the central finding

- **Identity:** CD14+ monocyte subcluster MC4, exclusively enriched in LCAM (not LCAS, not RLC, not NI)
- **Top marker genes vs MC1–3:** IRF1, IRF8, TGFB1, CTNNB1 (β-catenin), ENG, NOTCH1, RUNX2, NCOA3, ITGAV, KLF13, RBPJ, LGMN, ITGA5, LMNA
- **Upregulated pathways in MC4:** TGFβ signaling, WNT–β-catenin signaling (months 3–8.9); TNF signaling (months 1.7–5.9 only)
- **MC4hi threshold:** >10% of CD14+ monocytes in MC4
- **Clinical correlations:**
  - MC4 proportion ↑ with FAS score: R=0.31, p=0.02
  - MC4 proportion ↓ with pO2: R=-0.30, p=0.023
  - MC4hi individuals had significantly higher fatigue than MC4lo or RLC (p<0.01)

### 2. Plasma cytokines (Cohort 2)

- **CCL2, CXCL11, TNF** persistently elevated in LC vs NI through month 9 (p<0.00001 at all timepoints)
- TNF negatively correlates with pO2: R = -0.32 (T2), -0.34 (T3), -0.37 (T4) — significant in LCAM but not LCAS

### 3. Transcriptome-wide GSEA (Cohort 1 pseudobulk)

- LCAM vs AI/RLC: persistent **upregulation** of TNF signaling; persistent **downregulation** of IFN signaling across all cell types up to month 8.9
- CD14+ monocytes months 3–8.9: upregulation of TGFβ, WNT–β-catenin, NOTCH signaling
- CD8+ T cells + NK cells: TLR cascade, IFNα/IFNβ induction pathways upregulated

### 4. Flow cytometry — protein validation (Cohort 4)

- LC has significantly more CD14+ monocytes than RA+NI (both severity groups)
- Proteins significantly elevated in LC CD14+ monocytes (MFI): **HLA-DQ, CD120b, CALR, CD99, TGFβ1**
- Severity gradient: CALR, CD120b, HLA-DQ, TGFβ1 MFI increase with dyspnea score (DS1→DS3) and fatigue category

### 5. BAL + PBMC integration (Cohort 5 — GSE263817)

- PBMC CL5 (TREM2+CALR+ monocytes) = highest LC-Mo AUC score
- CI4 cluster (TREM2+CCL2+ mixed PBMC/BAL) = highest LC-Mo enrichment + highest profibrotic gene score
- Resp-PASC has higher CI4/CI5 and CI4/CI6 cell ratios
- **CI4 upregulated genes:** SPP1, CCL13, CCL2, FOLR2
- **Profibrotic signature in CI4:** TREM2, CALM1, LGMN, APOE

### 6. Epigenetics — snATAC-seq (Cohort 1)

- MC4 has the most differentially accessible chromatin regions of the four monocyte clusters
- Top TF motifs enriched in MC4: GABPA, ETV1, ETV4, SPI1, SPIC (ETS family); JUN, JUNB, FOSB, FOS (AP-1); NF-κB1, RELA, SMAD3
- Gene–chromatin links: IER3 (regulated by FOSB:JUNB + ETV6), LMNA (regulated by FOS:JUN + RFX3 + NF-κB1)
- Genes correlated with open chromatin in MC4: VEGFA, ENG, TGFB1, RXRA, ICAM1, ITGA5, TTC7A, LMNA, IER3, SERPINE1

### 7. Functional stimulation (*P. aeruginosa* 4h) — Cohort 1 subset

- LC-Mohi vs LC-Molo after stimulation:
  - **Upregulated in LC-Mohi:** DHFR, HMOX1, EREG, GCLC
  - **Downregulated pathways:** IFNα response, cytokine signaling, IL-10 signaling, IFNγ signaling
  - **IFN genes suppressed:** IRF9, ASCC3, XAF1, SAMD9L, LILRB4, CGAS
  - Chemokines induced in both: CCL3, CCL4, CXCL3, IL6

---

## Strengths

- Rigorous stratification by acute infection severity — isolates LC-specific signals from post-severe-COVID effects
- Five independent cohorts spanning discovery, scRNA-seq validation, protein validation, and lung tissue
- Multi-modal integration (transcriptome + chromatin + cytokines + flow cytometry + BAL) for the same phenotype
- Functional validation (ex vivo stimulation) shows LC-Mo has immune consequences, not just a marker state
- GSE263817 (Cohort 5) is publicly available for immediate replication

## Limitations / Caveats

- MC4–FAS correlations are modest; individual variability is high
- Causality between LC-Mo and symptoms is not established (correlational study)
- Only respiratory/fatigue symptoms studied — LC-Mo's role in neurological or other LC manifestations unknown
- No vaccination status or comorbidity control recorded
- Oxygen saturation in Cohort 1 was normal despite MC4 correlating with pO2 — lung involvement may be subtle at this stage

---

## Relevance to My Work — Agentic Immunology Framework

### Primary fit: Case 7 — CCL2 multiomics showcase

This paper is an ideal real-world template for **Case 7** ("Nienke CCL2 multiomics case") in `projs/agentic_immunology/plan.md`. The match is almost one-to-one:

| Case 7 step | This paper's evidence |
|-------------|----------------------|
| CCC agent identifies CCL2 elevated in monocytes | Plasma CCL2 persistently elevated in LC (Cohort 2); CI4 BAL macrophages upregulate CCL2 (Cohort 5) |
| GRN agent finds upstream TF in sender cell | AP-1 and NF-κB1 motifs enriched in MC4 open chromatin (snATAC-seq, Cohort 1) |
| Disease data cross-validation | LC-Mo signature scored in GSE263817 BAL data; Resp-PASC has higher profibrotic CI4 cluster |
| Clinical correlation | CCL2 / TNF anti-correlate with pO2; MC4 proportion correlates with FAS and pO2 |

**Concrete agent task formulation:**
> *"Investigate CCL2 as a disease-linked immune mediator in long COVID."*
> 1. CCC agent: finds CCL2 consistently elevated in monocytes across cohorts
> 2. GRN agent: recovers AP-1/NF-κB1 as upstream regulators in CD14+ monocytes from ATAC data
> 3. Disease agent: scores LC-Mo signature in GSE263817 → confirms CI4 profibrotic macrophages express CCL2 in lung
> 4. Clinical agent: correlates CCL2 plasma levels with pO2 and FAS across time
> 5. Output: convergent multi-modal evidence for CCL2 as a monocyte-to-lung mediator in LC

This is self-contained using publicly available data (GSE263817) and can serve as a **fully reproducible showcase** with a known ground truth.

### Secondary fit: Case 2 — Disease overlap (aging ↔ LC as accelerated immune aging)

The LC-Mo state strongly resembles canonical inflammaging features:
- TGFβ-driven profibrosis and NF-κB activation are hallmarks of aging immune cells
- Impaired IFN responses are a known feature of aged monocytes
- WNT–β-catenin signaling is implicated in age-related immune dysfunction

**Agent task formulation:**
> *"Do HIARA aging cohort CD14+ monocytes show directional overlap with the LC-Mo/MC4 signature? If yes, does long COVID represent a model of accelerated monocyte aging?"*
> — Score MC4 marker genes (TGFB1, IRF8, CTNNB1, ENG, NOTCH1) via AUCell in aging cohort data
> — Test whether AUC score increases with age in healthy donors
> — Quantify directional overlap between aging DE and LC-Mo signature per cell type
> — Punchline: LC accelerates a monocyte program that normally emerges gradually with aging

### As a replication benchmark

The pipeline is well-defined with a publicly available starting point. A scoped replication using GSE263817:
1. Download PBMC + BAL scRNA-seq data from GEO
2. Recluster CD14+ monocytes (Seurat v5, RPCAIntegration, resolution 0.2)
3. Score LC-Mo/MC4 signature via AUCell (marker genes listed above)
4. Stratify Resp-PASC vs. nonResp-PASC on LC-Mo AUC score
5. Integrate PBMC + BAL; reproduce CI4 profibrotic cluster enrichment in Resp-PASC

This is a concrete, end-to-end task with a known expected outcome — ideal for validating agent correctness before extending to novel in-house data.

## Notes

