# A distinct monocyte transcriptional state links systemic immune dysregulation to pulmonary impairment in long COVID (Kumar et al., 2026) — Question 1

## Question
What immune changes are specifically associated with long COVID (LC) — as distinct from acute COVID severity or post-ICU complications — and how do those changes mechanistically explain persistent fatigue and lung impairment?

## Findings
- A distinct CD14+ monocyte transcriptional subcluster, LC-Mo (MC4), is specifically enriched in patients with long COVID following a mild/moderate acute infection (LCAM) — not in patients with long COVID after severe acute infection (LCAS), not in recovered LC (RLC), and not in non-infected controls (NI).
- MC4 is marked by IRF1, IRF8, TGFB1, CTNNB1 (β-catenin), ENG, NOTCH1, RUNX2, ITGAV, ITGA5, LMNA, and shows upregulated TGFβ and WNT–β-catenin signaling (persisting months 3–8.9) plus early TNF signaling (months 1.7–5.9).
- MC4 abundance correlates with clinical severity: positively with fatigue (FAS score, R=0.31, p=0.02) and inversely with blood oxygenation (pO2, R=-0.30, p=0.023); MC4hi individuals (>10% of CD14+ monocytes) have significantly higher fatigue than MC4lo or recovered individuals (p<0.01).
- Plasma CCL2, CXCL11, and TNF are persistently elevated in LC versus NI through month 9; TNF negatively correlates with pO2 in LCAM (but not LCAS) at all timepoints tested.
- Transcriptome-wide pseudobulk GSEA confirms persistent TNF-pathway upregulation and interferon-pathway downregulation across cell types in LCAM up to month 8.9, while CD8+ T and NK cells show upregulated TLR/IFNα/IFNβ induction pathways.
- Flow cytometry validates LC-Mo as a protein-level state: HLA-DQ, CD120b, CALR, CD99, and TGFβ1 are elevated (MFI) on CD14+ monocytes in LC, with CALR, CD120b, HLA-DQ and TGFβ1 increasing further with dyspnea and fatigue severity.
- In an independent public PBMC+BAL dataset (GSE263817), the LC-Mo signature maps to a TREM2+CALR+ PBMC monocyte cluster and to a profibrotic lung macrophage cluster (CI4: SPP1, CCL13, CCL2, FOLR2, TREM2, CALM1, LGMN, APOE), which is enriched in patients with respiratory PASC.
- snATAC-seq shows MC4 has the most differentially accessible chromatin among monocyte clusters, enriched for AP-1 (JUN/JUNB/FOS/FOSB), NF-κB1/RELA, SMAD3, and ETS-family (SPI1, GABPA, ETV1/4) motifs, linked to open chromatin at TGFB1, ENG, VEGFA, LMNA, ICAM1, SERPINE1 — indicating an epigenetically encoded profibrotic program.
- Ex vivo P. aeruginosa stimulation reveals functional immune suppression in LC-Mohi monocytes: blunted IFNα, IFNγ, IL-10, and cytokine-signaling responses (suppressed IRF9, XAF1, SAMD9L, CGAS) despite normal chemokine induction (CCL3, CCL4, CXCL3, IL6).

## Methodology

### Datasets
- **Cohort 1 (primary discovery, multiome)**: PBMCs from Hannover Medical School (MHH), Germany, recruited Apr 2020–Aug 2021; 78 samples / 45 donors (AIM n=7, AIS n=4, LCAM n=29, LCAS n=8, RLC n=8, NI n=6), ~118,000 cells; snRNA-seq + snATAC-seq (10x Multiome); EGA accessions EGAS50000000142/143, EGAS0000001215/1216.
- **Cohort 2 (plasma cytokines)**: MHH, May 2020–Aug 2021; 238 plasma samples (LCAM n=117, LCAS n=25, NI n=33); Quanterix HD SP-X 10-plex + Simoa 4-plex.
- **Cohort 3 (scRNA-seq validation, respiratory PASC)**: Pulmonary Rehabilitation Clinic, Schönau am Königssee, Germany, Oct–Nov 2023; PBMCs, LCAM n=8 (Resp-PASC n=5, Resp-PASC-BHR n=3); scRNA-seq.
- **Cohort 4 (flow cytometry protein validation)**: MHH, Aug 2020–Jun 2022; cryopreserved PBMCs, LCAM n=29, LCAS n=11, RA+NI n=10; 11-marker spectral flow panel.
- **Cohort 5 (public PBMC + BAL dataset)**: Mayo Clinic (Li et al., Sci. Transl. Med. 2024), GEO GSE263817; PBMCs n=11 + BAL n=9 (LCUN n=9: Resp-PASC n=5, nonResp-PASC n=4; NI n=2); scRNA-seq.
- **Functional stimulation subset (Cohort 1)**: LCAM n=7, LCAS n=5, RLC n=6, PBMCs stimulated 4h with heat-inactivated P. aeruginosa (2.5×10⁶ CFU/mL); scMultiome on stimulated/unstimulated cells.

### Analytics
- CellRanger-arc alignment (GRCh38), Souporcell demultiplexing + genotyping, QC filtering — uses Cohort 1.
- Seurat v5 RPCAIntegration, Azimuth celltype.l2 annotation, monocyte subclustering (resolution 0.2 → MC1–MC4) — uses Cohort 1.
- Pseudobulk DESeq2 differential gene expression + fgsea GSEA (Hallmark/REACTOME) — uses Cohort 1.
- AUCell pathway/signature scoring (LC-Mo marker genes) — uses Cohort 1 and Cohort 5.
- MiloR neighborhood differential abundance testing — uses Cohort 1.
- Pseudotime inference (destiny diffusion maps + Slingshot, NI-enriched cluster as root) — uses Cohort 1.
- Signac ATAC integration, Macs3 peak calling, LinkPeaks gene–chromatin linkage, ChromVar + JASPAR2020 TF motif enrichment — uses Cohort 1 snATAC-seq.
- Spearman correlation of MC4 proportion with clinical variables (FAS fatigue score, pO2) — uses Cohort 1.
- Multiplex cytokine quantification and correlation with pO2 over time — uses Cohort 2.
- Independent scRNA-seq clustering/validation of LC-Mo signature — uses Cohort 3.
- Flow cytometry MFI quantification and severity-gradient (dyspnea/fatigue) analysis — uses Cohort 4.
- Cross-dataset integration of PBMC + BAL clusters and AUCell scoring of the LC-Mo signature, comparison of Resp-PASC vs nonResp-PASC — uses Cohort 5.
- Ex vivo P. aeruginosa stimulation followed by scMultiome DGE/GSEA comparing LC-Mohi vs LC-Molo monocytes — uses Cohort 1 functional stimulation subset.
- Statistical testing throughout: Wilcoxon rank-sum tests, Spearman correlation, Benjamini-Hochberg multiple-testing correction.
