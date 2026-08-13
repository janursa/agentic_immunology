# pQTL Data Lake

All files are **tabix-indexed** (`*.cc.tsv.gz` + `*.cc.tsv.gz.tbi`) from the **eQTL Catalogue** (sumstats release).

**Shared column schema** (all files):
`molecular_trait_id | chromosome | position | ref | alt | variant | ma_samples | maf | pvalue | beta | se | type | ac | an | r2 | molecular_trait_object_id | gene_id | median_tpm | rsid`

- `molecular_trait_id` — SomaScan aptamer/SOMAmer ID (e.g. `ISG15.14148.2.3..1`)
- `gene_id` — Ensembl gene ID of the encoded protein
- `rsid` — variant rsID (use for coloc rsID-matching)
- `beta`, `se`, `pvalue` — effect size and standard error (protein abundance, aptamer-based)

For **coloc** (`generic_tsv` format): `col_gene=gene_id`, `col_rsid=rsid`, `col_beta=beta`, `col_se=se`, `col_pval=pvalue`

> **Note on aptamer IDs**: Multiple SomaScan aptamers may target the same protein. The same `gene_id` may appear multiple times with different `molecular_trait_id` values. Use `gene_id` to filter for the protein of interest.

---

## sun_2018/
*Plasma pQTL — Sun et al. 2018, Nature; eQTL Catalogue r7*

Plasma protein levels measured by SomaScan (3,622 aptamers → ~2,994 unique proteins). n=3,301 donors (INTERVAL cohort, healthy adults). GRCh37. The largest published pQTL dataset in the eQTL Catalogue. Enables GWAS × pQTL colocalization to test whether a GWAS locus acts through protein abundance.

| File | Tissue | N | Proteins | Size | eQTL Cat. ID |
|------|--------|---|----------|------|--------------|
| `plasma.cc.tsv.gz` | Plasma | 3,301 | ~2,994 | 207 MB | QTD000584 |
