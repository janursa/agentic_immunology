# Analysis Plan — rs11867200 / CCL2 age/disease-dependent stimulation QTL

**Question:** rs11867200 associates with CCL2/MCP-1 production after 24h LPS stimulation in PBMCs, but **only in old or disease individuals**. What is the mechanism, and what does this tell us about the variant's biology?

---

## What we already know

| Item | Detail |
|------|--------|
| **Variant** | rs11867200 |
| **Trait** | CCL2/MCP-1 protein production, measured 24h post-LPS in PBMCs |
| **Effect structure** | Association is **context-dependent**: present in aged or disease individuals only; absent in young healthy |
| **eQTL (Nienke, past)** | **Negative** — the variant does NOT show a conventional eQTL signal for CCL2 or nearby genes in standard (resting or mildly stimulated) datasets |

**Interpretation of the eQTL null:** This is informative, not a dead end. A variant can regulate cytokine production without being a detectable eQTL in resting cells if:
- Its regulatory element is only open/active under an inflammatory + aged chromatin state
- The effect is on mRNA stability / translational efficiency / post-transcriptional regulation rather than transcription rate alone
- The variant acts through a cell-composition shift (monocyte subsets differ in aged PBMCs) rather than per-cell expression level

---

## Biological model

The most parsimonious hypothesis:

> rs11867200 lies in (or tags) a regulatory element for CCL2 that requires BOTH (1) TLR4/LPS stimulation AND (2) an epigenetically primed (aged/inflamed) chromatin state. Young cells satisfy condition 1 but not 2 after acute LPS; aged/disease cells satisfy both. The variant alters a TF binding site whose occupancy is only measurable when chromatin is accessible — which only happens in the aged/disease inflammatory context ("inflammaging").

Key biology underpinning this:
- **Inflammaging**: chronic NF-κB and AP-1 activation in aged monocytes pre-opens enhancers
- **Epigenetic clock**: age-associated CpG demethylation can expose regulatory elements
- **LPS 24h vs. 4h**: the late CCL2 response depends on sustained AP-1/STAT signaling, not just the NF-κB burst — more sensitive to chromatin context

---

## Analysis Plan

### Step 1 — Variant annotation [← START HERE]
**Goal:** Characterise rs11867200 at the DNA/regulatory level.

- [ ] 1a. dbSNP: position (GRCh38), alleles, minor allele frequency
- [ ] 1b. Ensembl: nearby genes, variant consequence (coding / regulatory / intronic)
- [ ] 1c. RegulomeDB: regulatory score (0–7) — is this variant in a functional regulatory element?
- [ ] 1d. SCREEN (ENCODE cCRE): which class of cis-regulatory element overlaps? (PLS=promoter, pELS/dELS=enhancer, CTCF-only)
- [ ] 1e. GWAS Catalog (local + API): what disease/trait associations are known for this SNP?
- [ ] 1f. gnomAD: population allele frequencies, any selection signal
- [ ] 1g. REMAP: which TFs have ChIP-seq peaks overlapping this locus?
- [ ] 1h. JASPAR: does either allele disrupt a TF motif?

**Outputs:** `step1_annotation/results.txt`

---

### Step 2 — QTL sweep (beyond eQTL)
**Goal:** Since eQTL is negative, test whether the variant shows signal in other QTL modalities.

- [ ] 2a. **mQTL** (BLUEPRINT monocyte/T cell/neutrophil) — does rs11867200 affect DNA methylation? If yes → epigenetic mechanism confirmed
- [ ] 2b. **pQTL** (Sun et al. plasma proteins, n=3,301) — is it a pQTL for CCL2 protein in plasma?
- [ ] 2c. **sQTL** (BLUEPRINT / DICE / GTEx whole blood) — does it affect splicing of a nearby gene?
- [ ] 2d. **DICE eQTL** (resting vs. stimulated) — check specifically in monocytes (the main CCL2 producers); relaxed p-value threshold

**Key expectation:** mQTL in monocytes would directly support the epigenetic-priming model.

---

### Step 3 — Aging context from HiRA
**Goal:** Ground the age-dependency in our own aging data.

- [ ] 3a. Retrieve aging gene expression signatures across major immune cell types — where does CCL2 rank in aging DEGs?
- [ ] 3b. Retrieve aging TF activity signatures — which TFs drive the age-related CCL2 upregulation? (These are the TFs whose binding sites matter)
- [ ] 3c. Cross-reference TF candidates from Step 1g/1h with aging TF activity shifts

---

### Step 4 — LPS stimulation gene expression (Kummerlowe)
**Goal:** Understand the CCL2 transcriptional response to LPS at single-cell resolution.

- [ ] 4a. Load Kummerlowe LPS (4h) data; identify cell types expressing CCL2
- [ ] 4b. Check which TFs are co-upregulated with CCL2 in monocytes under LPS → these are candidates for the allele-specific binding site

---

### Step 5 — Synthesis and mechanistic model
- [ ] 5a. Integrate: regulatory annotation + TF candidates (aging + LPS) + QTL evidence
- [ ] 5b. Draft testable mechanistic model: which TF, which regulatory element, which age-associated epigenetic change
- [ ] 5c. Propose experimental validation (ATAC-seq in young vs old monocytes at this locus; allele-specific ChIP in aged monocytes)

---

## Key data sources used

| Source | Relevance |
|--------|-----------|
| DICE eQTL (15 immune types) | eQTL in resting/stimulated immune cells |
| OneK1K eQTL (14 PBMC types) | Higher-power PBMC eQTL |
| eQTLGen (whole blood, n=31K) | Meta-analysis blood eQTL |
| BLUEPRINT mQTL (monocyte/T/neutrophil) | Epigenetic link |
| Sun et al. pQTL (plasma proteins) | CCL2 protein-level QTL |
| HiRA aging signatures | Age-related immune transcriptome/TF shifts |
| Kummerlowe LPS data | LPS stimulation single-cell resolution |
| SCREEN cCRE / RegulomeDB | Regulatory element annotation |
| REMAP / JASPAR | TF binding evidence |
