# Kummerlowe Drug Perturbation — File List

All files located in `datalake/omics/Kummerlowe/`.  
**Reference:** Kummerlowe et al., *Nat Biotechnol* 42, 1693–1703 (2024). DOI: 10.1038/s41587-024-02403-z  
**Source:** Single Cell Portal SCP2622

---

## scp2622_val_sc.h5ad
**SCP2622 Compressed Drug Screen — Single-Cell**
Primary human PBMC drug perturbation screen (1 healthy donor). 90 small-molecule compounds (Broad Drug Repurposing Hub, known MOA) tested under Control (DMSO), IFNβ, and LPS stimulation. Compressed screen design: 6 drugs pooled per well, 3 replicate wells per drug. Individual drug assignment requires cNMF deconvolution.  
Cells: 120,174 | Genes: 15,313  
obs columns: sample_id, stimulation, is_assigned, well_id, dest_row, dest_col, drug_pool, is_control, CT_Major, CT_Minor, CT_Major_percell, CT_Minor_percell, leiden, n_genes_by_counts, total_counts, pct_counts_mt, disease, organ, sex  
layers: lognorm (normalize_total 1e4 + log1p)  
obsm: X_pca, X_umap  
Stimulation conditions: S1–S6 = Control · M1–M6 = IFNβ · W1–W6 = LPS

**90 compounds:** A-366, ABT-737, AMG 900, AMG 925, APY0201, AZ 191, AZD2014, AZD7545, Andarine, Apratastat, BI-78D3, BIO, BIX02188, BLU9931, BMS 564929, BMS 566419, BX-912, CHIR-99021, CP 724714, CPI-0610, Carmustine, Dothiepin hydrochloride, EPZ015666, FR 180204, Filanesib, Filgotinib, GDC-0879, GNF 5, GSK J4, GSK2334470, GW 3965 hydrochloride, GW 5074, Halopemide, Homochlorcyclizine 2HCl, Hydroxyzine (dihydrochloride), ICG-001, IOX 2, Ispinesib, KH-CB19, Ketotifen (fumarate), Lenvatinib, Linsitinib, MK-5108, ML 298 hydrochloride, ML-323, ML324, Maprotiline HCl, Merimepodib, NVP-AEW541, NVS-PAK1-1, Neflamapimod, Neratinib, Niraparib, ORPHENADRINE CITRATE, P005091, PD 198306, PF 477736, PFI-1, PHYSCION, PNU-74654, Pomalidomide, Ponatinib, Purmorphamine, RG-7112, RGFP966, Rapamycin, Romidepsin, Rosuvastatin calcium, Ruxolitinib, SAG, SCH900776, SGC 707, SGX-523, SHP 99.00, SU 3327, SU11274, Skepinone-L, T 0901317, THZ1, UNC0642, Valrubicin, Veliparib, WZ4003, XL413 (hydrochloride), delta-Tocotrienol, selumetinib, (2Z)-2-butenedioic acid compound with N,N-dimethyl-2-{3-[(1S)-1-(2-pyridinyl)ethyl]-1H-inden-2-yl}ethanamine (1:1), (3R)-6-chloro-3-methyl-1,5-dihydroimidazo[2,1-b]quinazolin-2(3H)-one, 2-((1H-pyrrolo[2,3-b]pyridin-5-yl)oxy)-4-(4-((4'-chloro-5,5-dimethyl-3,4,5,6-tetrahydro-[1,1'-biphenyl]-2-yl)methyl)piperazin-1-yl)-N-((3-nitro-4-(((tetrahydro-2H-pyran-4-yl)methyl)amino)phenyl)sulfonyl)benzamide, 3,6-diamino-10-methylacridinium chloride compound with 3,6-acridinediamine (1:1)
