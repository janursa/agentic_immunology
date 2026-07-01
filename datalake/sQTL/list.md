# sQTL Data Lake

All files are **tabix-indexed** (`*.cc.tsv.gz` + `*.cc.tsv.gz.tbi`) from the **eQTL Catalogue** (sumstats release).

**Shared column schema** (all files):
`molecular_trait_id | chromosome | position | ref | alt | variant | ma_samples | maf | pvalue | beta | se | type | ac | an | r2 | molecular_trait_object_id | gene_id | median_tpm | rsid`

- `molecular_trait_id` — leafcutter intron cluster ID (e.g. `1:10000:20000:clu_1_+`)
- `gene_id` — Ensembl gene ID of the host gene
- `rsid` — variant rsID (use for coloc rsID-matching)
- `beta`, `se`, `pvalue` — effect size and standard error (normalised expression, sdy=1)

For **coloc** (`generic_tsv` format): `col_gene=gene_id`, `col_rsid=rsid`, `col_beta=beta`, `col_se=se`, `col_pval=pvalue`

---

## blueprint/
*BLUEPRINT sQTL — Chen et al. 2016, Cell; eQTL Catalogue r7*

3 primary human immune cell types. Donors: monocyte (n=191), neutrophil (n=196), CD4+ T cell (n=167). GRCh38. Leafcutter intron excision events.

| File | Cell type | Size | eQTL Cat. ID |
|------|-----------|------|--------------|
| `monocyte.cc.tsv.gz` | Monocyte | 260 MB | QTD000025 |
| `neutrophil.cc.tsv.gz` | Neutrophil | 199 MB | QTD000030 |
| `cd4_t_cell.cc.tsv.gz` | CD4+ T cell | 605 MB | QTD000035 |

---

## schmiedel_2018/
*DICE sQTL — Schmiedel et al. 2018, Cell (same cohort as DICE eQTL); eQTL Catalogue r7*

10 primary human immune cell types. N=88–91 donors. GRCh38. Leafcutter intron excision events.

| File | Cell type | Size | eQTL Cat. ID |
|------|-----------|------|--------------|
| `b_cell.cc.tsv.gz` | B cell | 19 MB | QTD000478 |
| `cd4t_naive.cc.tsv.gz` | CD4+ T naive | 23 MB | QTD000483 |
| `cd4t_stim.cc.tsv.gz` | CD4+ T stimulated | 13 MB | QTD000488 |
| `cd8t_naive.cc.tsv.gz` | CD8+ T naive | 19 MB | QTD000493 |
| `cd8t_stim.cc.tsv.gz` | CD8+ T stimulated | 13 MB | QTD000498 |
| `cd16_monocyte.cc.tsv.gz` | CD16+ monocyte | 22 MB | QTD000503 |
| `monocyte.cc.tsv.gz` | Monocyte | 23 MB | QTD000508 |
| `nk_cell.cc.tsv.gz` | NK cell | 14 MB | QTD000513 |
| `treg_memory.cc.tsv.gz` | Treg memory | 24 MB | QTD000468 |
| `treg_naive.cc.tsv.gz` | Treg naive | 15 MB | QTD000473 |

---

## gtex_v8/
*GTEx v8 whole blood sQTL — GTEx Consortium 2020, Science; eQTL Catalogue r7*

Whole blood, n=670. GRCh38. Leafcutter intron excision events. Largest powered sQTL study available.

| File | Tissue | Size | eQTL Cat. ID |
|------|--------|------|--------------|
| `whole_blood.cc.tsv.gz` | Whole blood | 576 MB | QTD000360 |
