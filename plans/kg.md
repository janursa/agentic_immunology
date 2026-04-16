# Knowledge Graph Resources for Immune Aging

*Generated: 2026-04-15 | Updated: 2026-04-15 | Context: Building cell-type-specific KGs for immune aging analysis*

---

## Most Versatile KGs in the Field

### Tier 1 — The standards everyone uses

| KG | Node types | Edges | Strength | Access |
|---|---|---|---|---|
| **OmniPath** | Genes/proteins | 85K directed PPIs + TF regulons + L-R | Best for signaling directionality + evidence provenance | Free — **we have this** |
| **PrimeKG** (Chandak et al. 2022, *Sci Data*) | 10 types: disease, gene, drug, pathway, phenotype, side effect, etc. | 4M+ multiplex edges | Best all-rounder for ML/GNN — integrates 20 databases | Free, Harvard |
| **Hetionet** | 11 types | 2.2M edges | First widely-used heterogeneous biomedical KG; aged but extensively benchmarked | Free |
| **SPOKE** (UCSF) | 27 node types | ~50M edges | Broadest clinical scope; used for drug repurposing + EHR linkage | Free API |
| **INDRA KG** | Causal statements | ~10M | NLP-extracted + curated causality; edges have directionality and mechanism | Free |

**Winner for molecular precision**: OmniPath (which we have)  
**Winner for multiplex/ML tasks**: PrimeKG  
**Winner for clinical drug repurposing**: SPOKE  

---

### Tier 2 — Company KGs (mostly closed)

| Company / Product | Notes |
|---|---|
| **Causaly** | NLP-extracted causal biomedical KG; sells API access; strong for drug-mechanism chains |
| **Novo Nordisk / GSK internal KGs** | Not public |
| **Recursion** | Drug-phenotype KG from morphological screens; proprietary |
| **Elsevier GNBR** | Gene-NLP relations extracted from 2M+ papers; partially open |
| **TxGNN** (Harvard/Zitnik lab) | Drug-disease KG with GNN predictions — **we have `txgnn_prediction.pkl`** |

---

## Immune Cell-Type-Specific KGs

### What exists

| Resource | What it is | T cell specific? |
|---|---|---|
| **NicheNet** (Browaeys et al. 2019) | End-to-end ligand→receptor→TF→target network; general purpose, widely applied to immune cells | ⚠️ General — not immune-specific, but context-weighted per cell type from user data |
| **ImmPort** | Immune gene/pathway annotations; not a true molecular KG | ⚠️ Immune only, not T cell specific |
| **DICE database** | eQTLs per immune cell subtype (Th1, Th2, Tfh, Treg, naive/memory CD4, CD8...) | ✅ Most granular at subtype level — **we have this** (`datalake/dice/`) |
| **ImmGen** (mouse) | Gene regulatory networks per immune cell type from ATAC + RNA | ✅ Per T cell subtype, but mouse |
| **MSigDB C7** (immunologic gene sets) | 4,000+ curated immune perturbation gene sets | ✅ **We have this** (`msigdb_human_c7_immunologic_signature_geneset.parquet`) |
| **McPAS-TCR** | TCR sequences per disease/antigen | ✅ T cell only — **we have this** |

### What does NOT exist yet

A dedicated, published, molecularly-resolved **T cell aging KG** does not exist. The closest published attempts are:
- **Mogilenko et al. 2021** (*Immunity*): transcriptomic reprogramming of T cells with aging — data, not a KG
- **Callender et al. 2020** (*Nature Immunology*): metabolic reprogramming of aged T cells — narrative, not a KG

---

## What We Already Have That Could Seed a T Cell KG

From our data lake at `/vol/projects/CIIM/agentic_central/agentic/datalake/`:

| File | Layer |
|---|---|
| `omnipath/interactions_directed.tsv` | Molecular backbone (85K directed PPIs) |
| `omnipath/dorothea_tf_regulon.tsv` | TF → target regulatory layer |
| `omnipath/ligrec_interactions.tsv` | Incoming ligand-receptor signals |
| `biomni/msigdb_human_c7_immunologic_signature_geneset.parquet` | Immune perturbation gene sets |
| `biomni/msigdb_human_c8_celltype_signature_geneset.parquet` | Cell-type marker genes |
| `biomni/McPAS-TCR.parquet` | T cell antigen specificity |
| `biomni/txgnn_prediction.pkl` | Drug-disease predictions (drug node validation) |
| `kg/kg.csv` | PrimeKG — 8.1M edge multiplex KG (**now in datalake**) |
| `biomni/gwas_catalog.pkl` | GWAS associations (genetic anchors) |
| `biomni/DisGeNET.parquet` | Disorder-gene associations |
| `biomni/DepMap_CRISPRGeneDependency.csv` | Gene essentiality (perturbation layer) |
| `dice/` | Cell-type-specific eQTLs + expression baselines (**now in datalake**) |
| **Our aging TF + GE signatures per T cell subtype** | Cell-type-specific aging context — not in any public KG |

---

## Recommended Stack for a T Cell Aging KG

| Layer | Source | Status |
|---|---|---|
| Molecular backbone | OmniPath (directed PPIs + TF regulons) | ✅ Have it |
| Multiplex disease/drug/pathway nodes | PrimeKG (`kg/kg.csv`) | ✅ Have it |
| Cell-type-weighted L-R → TF paths | NicheNet prior model (`nichenet/`) | ✅ Have it |
| T cell subtype eQTLs + expression | DICE database (`dice/`) | ✅ Have it |
| Aging context layer | Our TF + GE signatures per subtype | ✅ Have it (unique asset) |
| Perturbation/drug reversal layer | Our Ruxolitinib + drug signatures + MSigDB C7 | ✅ Have it |

The **aging TF/GE signatures per cell subtype** are our unique contribution that no public KG has — they are the cell-type-specific edge weights that make this KG distinct from a generic filtered subgraph.

---

## Deep Dives on Key Resources

### IRIS — Status: No Longer Recommended

**Original reference**: Bhatt et al. 2012, *Science Signaling* (doi:10.1126/scisignal.2001877)

IRIS was a manually curated database of signaling pathways in primary immune cells. It is **not actively maintained** — last major curation was ~2012–2015, and it lacks all post-2015 biology (cGAS-STING, mTOR metabolic checkpoints, PD-1/LAG-3 checkpoint details, etc.).

**There is no direct successor called "IRIS 2.0"**. The functionality IRIS provided has been superseded by:
- **SIGNOR** (signor.uniroma2.it) — regularly updated, curated causal signaling database with immune cell pathway context; covers TCR, BCR, cytokine, and checkpoint signaling
- **Reactome "Immune System" module** (reactome.org) — comprehensive, regularly updated, covers T cell activation, cytokine signaling, innate/adaptive immunity in detail
- **WikiPathways** — community-updated immune pathways with curation versions
- These are all integrated into OmniPath and PrimeKG already

**Verdict**: Use Reactome pathways (already in PrimeKG) and SIGNOR (partially in OmniPath via SIGNOR source tags) rather than IRIS.

---

### NicheNet — General Purpose, Not Immune-Specific

**Reference**: Browaeys et al. 2020, *Nature Methods* (doi:10.1038/s41592-019-0667-5)  
**Location**: `datalake/nichenet/` — **in datalake** | See `datalake/nichenet/list.md` for full file listing

**NicheNet is a general-purpose cell-cell communication tool** — it was developed for any tissue, tumor, or organ context, not specifically for immunity. It has been heavily applied to immune datasets because CCC is biologically important in immune tissues, but its prior network has no immune-specific knowledge. The cell-type context comes entirely from the user's own scRNA-seq data.

| Aspect | OmniPath | NicheNet |
|---|---|---|
| Scope | Intracellular PPIs, TF regulons, L-R separately | **End-to-end**: ligand → receptor → intracellular → TF → target gene |
| Edge weighting | Evidence count / database of origin | **Empirically calibrated** — weighted by how well they predict observed transcriptional responses in ~600 published perturbation studies |
| L-R → downstream link | Not connected (separate tables) | ✅ Explicitly connected — trace from extracellular ligand to target gene |
| Immune specificity | None | ❌ None — general mammalian signaling |
| Cell-type context | None — generic | ✅ Activity scores computed per cell type from user's scRNA-seq |
| Ligand activity model | None | ✅ Predicts which ligands most likely drive observed gene expression changes in receiver cells |

**The unique addition for our work**: NicheNet bridges the **CCC layer** with the **intracellular regulatory layer** in one connected prior network. If MONO→CD8T MIF signaling increases with aging, NicheNet traces: MIF → CD74/CXCR2 → NF-κB/MAPK → TFs → target genes. The prior network integrates OmniPath, KEGG, Reactome, and other generic signaling databases — but no immune cell-specific curation.

**How edge weights were derived**: The team took ~600 published perturbation experiments (ligand treatment + gene expression readout in various cell types, not just immune) and scored how well each path in the prior network predicted the observed DE genes. Edges that consistently appear in predictive paths got higher weights — empirical calibration, not just literature counting.

---

### DICE Database — In Datalake

**Reference**: Schmiedel et al. 2018, *Cell* (doi:10.1016/j.cell.2018.10.022)  
**Location**: `datalake/dice/` | See `datalake/dice/list.md` for full file listing

DICE profiled gene expression and eQTLs across **15 primary human immune cell subtypes** from 91 healthy donors.

**What DICE contributes to the KG**:
- **eQTLs per subtype** (`dice/eqtls/`): SNPs that causally regulate gene expression specifically in that T cell subset — cell-type-specific causal anchors for KG edges. If a SNP affects BACH2 only in naive CD4 T cells but not Th17, the regulatory context of BACH2 is naive-specific.
- **Expression baselines** (`dice/expression/`): TPM per cell type = filter to determine which nodes in the generic KG are actually expressed (actionable) in each subtype.
- **Activated vs. resting pairs**: CD4_NAIVE vs. CD4_STIM and CD8_NAIVE vs. CD8_STIM are built-in perturbation comparisons — differential expression directly maps the TCR activation program without requiring additional data.

---

### MSigDB C7 — Immunologic Signatures Collection

**File**: `datalake/biomni/msigdb_human_c7_immunologic_signature_geneset.parquet`  
**Reference**: Liberzon et al. 2015, *Cell Systems*; Subramanian et al. 2005, *PNAS*  
**Version**: MSigDB v2023.2.Hs | **Gene sets**: ~4,000+ immunologic signature sets

#### What it is

MSigDB C7 is a **compendium of gene signatures** — not a mechanistic model. Each entry is a list of genes that were significantly differentially expressed (up or down) in a specific immunological experiment published in the literature. The MSigDB team collected these from hundreds of studies and standardized them into a queryable database.

Think of it as: **"Here is what genes changed when X happened to immune cells in experiment Y."**

#### How the gene sets were derived — step by step

1. MSigDB curators searched the literature for microarray and RNA-seq studies involving human or mouse immune cells
2. For each study, they obtained either the published DE gene lists directly, or downloaded raw data from GEO/ArrayExpress and recomputed differential expression themselves
3. Each pairwise comparison (condition A vs. condition B) becomes **two gene sets**: `_UP` (genes significantly higher in A) and `_DN` (genes significantly lower in A)
4. Gene sets are named with a GEO accession number + the comparison description, e.g.:
   - `GSE22886_NAIVE_VS_MEMORY_CD4_TCELL_UP` → genes higher in naive vs. memory CD4 T cells (from GEO dataset GSE22886)
   - `GSE11924_TH1_VS_TH2_CD4_TCELL_UP` → genes higher in Th1 vs. Th2
   - `GSE22886_UNSTIM_VS_IL2_TREATED_NKCELL_UP` → genes higher in unstimulated vs. IL-2-treated NK cells

The perturbations covered include:
- **Cell state comparisons**: naive vs. memory, resting vs. activated, early vs. late effector
- **Cytokine treatments**: IFN-γ, IL-2, IL-4, IL-10, IL-12, TNF, TGF-β, etc.
- **TLR/PRR stimulation**: LPS, poly(I:C), CpG
- **TCR stimulation**: anti-CD3/CD28, PMA/ionomycin
- **T helper differentiation**: Th1, Th2, Th17, Treg polarization conditions
- **Disease comparisons**: healthy vs. autoimmune, infection, cancer
- **Genetic perturbations** (KO/OE of key immune regulators in some sets)

#### What it is NOT

- It is **not a signaling model** — it does not tell you what caused the gene expression change
- It is **not mechanistic** — "PRDM1 was up in Th1 cells" does not mean PRDM1 drove the Th1 program
- The gene sets come from **many different labs, protocols, and platforms** — between-set comparability is limited
- **Mouse and human** gene sets are mixed (though C7 is primarily human; mouse is in MSigDB M7)

#### How it is useful for our KG

| Use case | How C7 helps |
|---|---|
| **Validate aging state transition** | If our aging-UP genes in CD8T overlap strongly with "naive→effector" C7 sets, that independently validates the state transition hypothesis |
| **Edge weighting training signal** | A proposed regulatory path in the KG should predict C7 gene set membership — gene sets serve as positive labels |
| **Identify upstream regulators** | C7 sets from TF KO/OE experiments (e.g., "genes UP when PRDM1 is overexpressed in T cells") directly link a TF to its targets in a cell-type context |
| **Drug perturbation comparison** | Compare our Ruxolitinib reversal signatures to C7 JAK-inhibitor sets — if they match, validates the drug mechanism in our cohort |

---

### PrimeKG — In Datalake

**Reference**: Chandak et al. 2023, *Scientific Data* (doi:10.1038/s41597-023-01960-3)  
**Location**: `datalake/kg/kg.csv` | **License**: MIT | **Size**: 8.1M rows, 937MB

PrimeKG was already present in our datalake. See `datalake/kg/list.md` for full schema and edge type breakdown.

**What PrimeKG adds beyond OmniPath**:

| Node type | OmniPath | PrimeKG |
|---|---|---|
| Genes/proteins | ✅ | ✅ |
| Diseases (17,080) | ❌ | ✅ |
| Drugs | ❌ | ✅ |
| Phenotypes (HPO) | ❌ | ✅ |
| Pathways (Reactome, GO) | ❌ | ✅ |
| Side effects | ❌ | ✅ |
| Anatomy/tissue expression | ❌ | ✅ |

**Edge types added**: Disease→gene (OMIM, ClinVar, DisGeNET), Drug→target (DrugBank, ChEMBL), Drug→disease (indication + contraindication), Drug→side effect, Phenotype→disease, Anatomy→protein (tissue expression from GTEx).

**For our KG**: Adds the **disease and drug layers** OmniPath entirely lacks. Critical for drug repurposing — connecting "PRDM1↑ in aged T cells" → "PRDM1 associated with disease X" → "drug Y targets PRDM1" requires disease and drug nodes that PrimeKG provides at scale.

---

### Integrating CCC Signatures into the KG

Our CCC signatures (`immune_aging_ccc_signatures_major_celltypes.csv`) capture **intercellular signals that change with aging** in the format `sender__ligand__receiver__receptor`. These fit as the **extracellular communication layer** of the KG.

**Architecture**:

```
[Sender GE changes] → [Ligand↑/↓] → [Receptor on receiver] → [Intracellular signaling] → [TF changes] → [Target genes]
```

**Layer by layer**:

1. **Sender side**: Our aging GE signatures capture which ligands are up/down in the sender cell type (e.g., MONO upregulates S100A8/A9 with aging) → these become **node activity scores** on ligand nodes.

2. **Ligand → Receptor edge**: `omnipath/ligrec_interactions.tsv` provides these edges. Our CCC aging signatures indicate **which of these edges are active and changing** — they become aging-weighted edges rather than generic binary connections.

3. **Receptor → intracellular → TF**: This is where **NicheNet is the critical bridge**. It connects receptor activation to downstream TF changes with empirically calibrated path weights. OmniPath has the raw PPIs but NicheNet provides the end-to-end paths.

4. **Validation**: The TF changes observed in the **receiver** cell type (e.g., RELA↑, IRF1↑ in CD8T) should be explainable by the incoming CCC signals on that cell's receptor nodes. This creates a testable cross-layer prediction.

**Key question CCC integration enables**: "Can the observed increase in MONO→CD8T signaling of ligand X explain the PRDM1↑ in CD8T?" — answered by traversing the KG path from that ligand through NicheNet to PRDM1, then checking whether this path is empirically supported.
