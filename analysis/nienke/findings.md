# Findings — rs11867200 / CCL2-CCL7 locus

## 1. Variant

**rs11867200** (chr17:34,248,950 GRCh38; REF=C, ALT=T)

- cQTL for CCL2 (MCP-1) after LPS stimulation: **T allele → lower CCL2** (β=−0.354, p=4.4×10⁻⁹, SI cohort pbmc_24h_mcp1_lps)
- CCL7 co-regulated from the same locus (pQTL p=1×10⁻⁷¹⁷ for CCL7; CCL8 eQTL in eQTLGen)
- Located 6.3 kb upstream of CCL2, within a distal enhancer cluster (7 dELS cCREs by ENCODE SCREEN)
- Effect is **LPS-specific and age/disease-dependent** (null in DICE young monocytes; significant in SI aged cohort)

---

## 2. TFs at the locus

### ChIP-seq evidence (ENCODE, ±500 bp of SNP)
CEBPB (33 bp), FOS (2 bp), FOSL2 (22 bp), JUND (45 bp), JUN (156 bp), MEF2A, NFIC, GATA2, GATA3, TCF12, MYC, MAX, PBX3

### Allele-specific binding loss C→T (GIMME vertebrate v5.0, ≥80% max score threshold)
| Motif | TFs | REF % | ALT % | Δ |
|---|---|---|---|---|
| GM.5.0.Unknown.0009 | NRF1/TCF12 disc | 100% | 27.2% | −10.0 |
| GM.5.0.Ets.0048 | ETS family (unnamed) | 99.8% | 10.0% | −8.8 |
| GM.5.0.Ets.0025 | ERG, ETS1, ETV2, ELF1, FLI1 | 85.8% | 25.7% | −7.3 |
| GM.5.0.E2F.0016 | E2F family (unnamed) | 87.7% | 8.5% | −5.5 |
| GM.5.0.Ets.0046 | ETS family (unnamed) | 100% | 29.0% | −4.9 |
| GM.5.0.Ets.0008 | SPIB / PU.1 | 93.0% | 68.8% | −3.2 |

### Allele-specific binding loss C→T (JASPAR 2022 human TFs, ≥80% max score threshold)
| TF | REF % | ALT % | Δ |
|---|---|---|---|
| SPI1 (PU.1) | 100% | 70.1% | −2.8 |
| SPIB | 94.8% | 68.4% | −3.0 |


---

## 3. TFs linked to LPS
### GRN model at ref 
13/16 candidate TFs recovered in GRN: CEBPB, FOS, FOSL2, GATA2, GATA3, JUND, MAX, MEF2A, NFIC, PBX3, SPI1, SPIB, ETV6. JUN, MYC, TCF12 fell outside the top 100k edges.

### TF activity change in response to LPS (decoupler ULM, SI cohort bulk PBMC 24h)

All 13 candidate TFs are significantly LPS-responsive in **both** REF and Carrier allele groups (Mann-Whitney U, BH FDR < 0.05). Effect size and direction are near-identical across alleles — the T allele does not alter which TFs respond to LPS or in which direction.

| TF | LPS effect (REF) | LPS effect (Carrier) | Direction | Motif disrupted? | ChIP at locus? |
|---|---|---|---|---|---|
| FOSL2 | +14.1 | +14.0 | ↑ LPS-induced | No | Yes |
| CEBPB | +8.1 | +7.5 | ↑ LPS-induced | No | Yes |
| GATA2 | +0.6 | +0.7 | ↑ LPS-induced | No | Yes |
| SPIB | +0.7 | +1.1 | ↑ LPS-induced | **Yes (−3.0)** | — |
| PBX3 | −15.4 | −15.5 | ↓ LPS-repressed | No | Yes |
| FOS | −8.4 | −8.6 | ↓ LPS-repressed | No | Yes |
| MAX | −2.9 | −2.9 | ↓ LPS-repressed | No | Yes |
| NFIC | −2.5 | −2.9 | ↓ LPS-repressed | No | Yes |
| MEF2A | −1.7 | −2.0 | ↓ LPS-repressed | No | Yes |
| JUND | −1.4 | −1.5 | ↓ LPS-repressed | No | Yes |
| SPI1 | −1.8 | −2.3 | ↓ LPS-repressed | **Yes (−2.8)** | — |
| GATA3 | −0.2 | −0.1 | ↓ LPS-repressed | No | Yes |
| ETV6 | −0.1 | −0.2 | ↓ LPS-repressed | No | — |

Effect = median ULM score (LPS) − median ULM score (NS). Source: `tfa_analysis/results/lps_vs_ns_stats_REF/Carrier.csv`.

---

## 4. Hypothesis — why T allele reduces CCL2 after LPS

### Critical intersection

Two TFs are simultaneously (a) LPS-regulated, (b) their motifs are disrupted by the T allele, and (c) they are ETS-family paralogs that share binding sites:

- **SPIB**: strongly **induced** by LPS (+0.7–1.1 units, FDR < 10⁻¹¹); motif affinity drops −3.0 (JASPAR) with T allele.
- **SPI1 (PU.1)**: strongly **repressed** by LPS (−1.8–2.3 units, FDR < 10⁻¹⁸); motif affinity drops −2.8 (JASPAR) with T allele.

No other TF with disrupted motif is strongly LPS-responsive among the candidates.

### Abundance-threshold model

The T allele degrades the ETS half-site for **both** SPI1 and SPIB. LPS-specificity arises not from a switch but from differential sensitivity to affinity loss:

- **SPI1** is constitutively expressed at high levels in monocytes/macrophages. Even with reduced motif affinity (−2.8), its high nuclear concentration sustains occupancy at baseline → minimal effect on NS-condition CCL2.
- **SPIB** is inducible — low at baseline, only modestly induced by LPS (+0.7–1.1 ULM units). It operates near the binding threshold. A −3.0 affinity drop is sufficient to prevent productive LPS-driven occupancy → blunted CCL2 induction.

In other words: the same single SNP has negligible functional consequence when the ETS TF is abundant (SPI1, basal), but becomes rate-limiting when the ETS TF is inducible and concentration-limited (SPIB, LPS).

This explains:
- **LPS-specificity**: SPIB is the rate-limiting ETS factor under LPS; its affinity loss matters. SPI1 abundance at baseline buffers the same affinity loss.
- **Age/disease dependence**: SPIB-driven enhancer activity may become more load-bearing for CCL2 in aged/inflammatory contexts where alternative regulatory elements are less active.

> Note: direct evidence that SPIB activates CCL2 transcription is still missing — this is an inference from motif disruption + LPS induction. Validation is needed (see below).

### Validation approaches

| Approach | What it tests | Feasibility in existing data |
|---|---|---|
| SPIB ChIP-seq at locus in LPS monocytes, REF vs Carrier | Direct binding difference | No — would need new experiment |
| ATAC-seq: accessibility of this enhancer NS→LPS per allele | Enhancer opening depends on allele | No — new experiment |
| H3K27ac allelic imbalance in heterozygous donors under LPS | Allele-specific enhancer activity | No — new experiment |
| SPIB/SPI1 expression QTL: does rs11867200 associate with SPIB or SPI1 mRNA? | Trans regulation confound | **Yes — check SI eQTL data** |
| Correlation: SPIB ULM score vs CCL2 protein (LPS), stratified by allele | Functional link in existing data | **Yes — SI TFA + pQTL data** |
| SPIB knockdown + LPS in monocytes → CCL2 change | Causal role of SPIB in CCL2 LPS response | No — new experiment |
