# genetics — GWAS & Genetic Variant Tools

Module: `egad/tools/ciim/code/genetics.py`

---

## Functions

### `phewas_opengwas(snps, pval=5e-8, ...)`

PheWAS look-up across **all** OpenGWAS indexed studies. Best for comprehensive disease mapping of a list of lead SNPs.

```python
import sys
sys.path.insert(0, './egad/tools/ciim/code')
from genetics import phewas_opengwas

hits = phewas_opengwas(['rs10944479', 'rs1004870'], pval=1e-5)
hits[hits['is_ukb']].sort_values('p').head(10)
```

**Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `snps` | required | list of rsIDs |
| `pval` | `5e-8` | p-value cut-off |
| `batch_size` | 30 | SNPs per request (keep ≤50) |
| `sleep` | 1.0 | seconds between batches |
| `drop_expression` | `True` | removes eQTL/protein/metabolite studies |

**Returns** `pd.DataFrame` with columns: `rsid, id, trait, chr, position, ea, nea, eaf, beta, se, p, n, is_ukb`

---

### `query_gwas_catalog(snps, ukb_only=False)`

Look-up in the locally cached GWAS Catalog (622k published genome-wide significant associations, p<5e-8). Does **not** cover Neale Lab / Pan-UKBB; use `phewas_opengwas` for those.

```python
from genetics import query_gwas_catalog

hits = query_gwas_catalog(['rs10944479', 'rs1004870'])
hits[['SNPS', 'DISEASE/TRAIT', 'PVALUE_MLOG']].head()
```

---

---

### `run_coloc(gene, chr, pos, outdir, **kwargs)`

Python wrapper around `${CIIM_TEMP_DIR}/coloc/coloc.R`. Runs GWAS × eQTL colocalization for a single locus using **coloc.abf** (all cell types) and **coloc.susie** (top N cell types). Executed inside `${CIIM_SINGULARITY_DIR}/genotype.sif` (R 4.5, coloc, susieR, plink).

```python
import sys
sys.path.insert(0, 'egad/tools/ciim/code')
from genetics import run_coloc

# SLE × DICE eQTL colocalization at the IRF5 locus
run_coloc(
    gene='IRF5', chr=7, pos=128954129,
    outdir='/tmp/coloc_irf5',
    lead_rsid='rs10488631',
)
# Outputs written to /tmp/coloc_irf5/:
#   coloc_abf_IRF5_results.csv       — PP.H0–H4 per cell type
#   coloc_susie_IRF5_results.csv     — SuSiE credible-set signals (if any)
#   coloc_abf_IRF5_PP.H4_barplot.png
#   coloc_abf_IRF5_posteriors_stacked.png
#   regional_gwas_IRF5.png
#   regional_eqtl_{top_ct}_IRF5.png
```

**Mandatory parameters**

| Parameter | Description |
|-----------|-------------|
| `gene` | Gene symbol (e.g. `'IRF5'`) |
| `chr` | Chromosome number |
| `pos` | Lead-SNP position in bp (locus centre) |
| `outdir` | Output directory (created if absent) |

**GWAS kwargs** (defaults = SLE Bentham 2015, GCST003156)

| kwarg | Default | Description |
|-------|---------|-------------|
| `gwas_file` | Bentham 2015 | Path to harmonised GWAS `.tsv.gz`; expected columns: `hm_chrom`, `hm_pos`, `hm_rsid`, `hm_beta`, `standard_error`, `p_value`, `hm_code` |
| `gwas_n` | `14267` | Total GWAS sample size |
| `gwas_s` | `0.3645` | Proportion cases (cc studies only) |
| `gwas_type` | `'cc'` | `'cc'` (case-control) or `'quant'` (quantitative) |

**eQTL kwargs** (defaults = DICE, 15 immune cell types)

| kwarg | Default | Description |
|-------|---------|-------------|
| `eqtl_dir` | DICE dir | Directory with one eQTL file per cell type |
| `eqtl_n` | `91` | eQTL study sample size |
| `eqtl_sdy` | `1` | Expression SD (1 = inverse-normal normalised) |
| `eqtl_format` | `'dice_vcf'` | `'dice_vcf'` or `'generic_tsv'` (see below) |

**generic_tsv column-name kwargs** (only when `eqtl_format='generic_tsv'`)

| kwarg | Default | Description |
|-------|---------|-------------|
| `col_gene` | `'gene_symbol'` | Gene-symbol column |
| `col_rsid` | `'rsid'` | Variant-ID column |
| `col_beta` | `'beta'` | Effect-size column |
| `col_se` | `'se'` | Standard-error column |
| `col_pval` | `'pval'` | P-value column |

**LD reference kwargs**

| kwarg | Default | Description |
|-------|---------|-------------|
| `kg_bfile` | bundled 1KG EUR | plink bfile prefix |
| `plink` | `'plink'` | plink binary path |

**Other kwargs**

| kwarg | Default | Description |
|-------|---------|-------------|
| `lead_rsid` | `NA` | Lead SNP rsID — highlighted in regional plots only |
| `window` | `1e6` | Locus half-width in bp |
| `susie_n` | `5` | Top N cell types passed to coloc.susie |

**Returns** `str` — path to `outdir`.

**Direct CLI** (via singularity):
```bash
singularity exec \
  --bind /vol/projects:/vol/projects \
  ${CIIM_SINGULARITY_DIR}/genotype.sif \
  Rscript egad/tools/ciim/code/coloc.R \
    --gene IRF5 --chr 7 --pos 128954129 \
    --lead_rsid rs10488631 \
    --outdir /tmp/coloc_irf5
```

---


---

### `query_opentarget_platform(query, variables=None, verbose=False)`

> **Replaces** the deprecated `query_opentarget` in `egad/tools/biomni/database_biomni.py`.  
> Open Targets Genetics Portal was shut down **9 July 2025**. All GWAS, credible-set, and L2G data is now in the unified Platform API at `api.platform.opentargets.org/api/v4/graphql`.

Direct GraphQL caller — send any valid Platform v4 query and get the raw JSON response back.

```python
import sys
sys.path.insert(0, 'egad/tools/ciim/code')
from genetics import query_opentarget_platform

q = 'query { disease(efoId: "EFO_0002690") { name } }'
result = query_opentarget_platform(q)
print(result['data']['disease']['name'])  # systemic lupus erythematosus
```

**Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `query` | required | GraphQL query string |
| `variables` | `None` | dict of variable bindings |
| `verbose` | `False` | print request/response info |

**Returns** `dict` — parsed JSON. Raises `ValueError` on GraphQL errors.

---

### `get_disease_credible_sets(efo_id, page_size=50, max_pages=10, l2g_min_score=0.0)`

Retrieves all GWAS credible sets and Locus-to-Gene (L2G) ML predictions for a disease. Handles pagination automatically.

```python
from genetics import get_disease_credible_sets

# SLE (EFO_0002690), only high-confidence L2G predictions
df = get_disease_credible_sets('EFO_0002690', l2g_min_score=0.5)
df.sort_values('l2g_score', ascending=False).head(10)
```

**Parameters**

| Parameter | Default | Description |
|-----------|---------|-------------|
| `efo_id` | required | EFO disease ID (e.g. `EFO_0002690` for SLE) |
| `page_size` | `50` | credible sets per API page |
| `max_pages` | `10` | max pages to fetch (10 × 50 = up to 500 loci) |
| `l2g_min_score` | `0.0` | minimum L2G score to include (0.5 = high-confidence) |

**Returns** `pd.DataFrame` — one row per (credible set × gene) pair.

| Column | Description |
|--------|-------------|
| `study_locus_id` | Unique credible set identifier |
| `study_id` | GWAS study ID |
| `trait` | Trait name from source |
| `author`, `year` | Publication info |
| `n_samples` | GWAS sample size |
| `variant_id` | Lead variant (`chr_pos_ref_alt`) |
| `rsids` | rsID(s) of lead variant |
| `chromosome`, `position` | Genomic coordinates (GRCh38) |
| `pval_mantissa`, `pval_exponent` | P-value components |
| `beta`, `se` | Effect size |
| `finemapping_method` | e.g. SuSiE, FINEMAP |
| `gene_id` | Ensembl gene ID of L2G prediction |
| `gene_symbol` | Gene symbol |
| `l2g_score` | L2G score 0–1 (≥0.5 = high confidence) |

**Common EFO IDs**

| Disease | EFO ID |
|---------|--------|
| Systemic lupus erythematosus (SLE) | `EFO_0002690` |
| Rheumatoid arthritis | `EFO_0000685` |
| Multiple sclerosis | `EFO_0003885` |
| Type 1 diabetes | `EFO_0001359` |
| Inflammatory bowel disease | `EFO_0003767` |

---

### `run_mr(gene, mode, outdir, **kwargs)`

Python wrapper around `egad/tools/ciim/code/mr.R`. Runs Mendelian Randomization in two modes. Executed inside `${CIIM_SINGULARITY_DIR}/genotype.sif` (R 4.5, data.table, ggplot2, plink). MR methods implemented from scratch: Wald ratio (n=1), IVW (n≥2), MR-Egger (n≥3), Weighted Median (n≥3).

```python
import sys
sys.path.insert(0, 'egad/tools/ciim/code')
from genetics import run_mr

# Mode A: eQTL → disease (DICE instruments → local GWAS)
run_mr(
    gene='IRF5', mode='eqtl',
    outdir='/tmp/mr_irf5',
    chr=7, pos=128954129,
    pval_iv=5e-8, pval_iv_fb=1e-3,  # fallback threshold for low-powered eQTL studies
)
# Outputs: mr_IRF5_eqtl_results.csv, mr_IRF5_eqtl_{scatter,forest,funnel}.png,
#          mr_IRF5_eqtl_celltype_summary.png

# Mode B: 2-sample MR via OpenGWAS API (requires valid JWT in .env)
run_mr(
    gene='SLE_RA', mode='opengwas',
    outdir='/tmp/mr_sle_ra',
    exposure_id='ieu-a-1011',   # SLE Bentham 2015
    outcome_id='ieu-a-833',     # RA Okada 2014
    exposure_label='SLE (Bentham 2015)',
    outcome_label='RA (Okada 2014)',
)

# Mode B with pre-fetched files (bypass API — useful when token is expired)
run_mr(
    gene='MyGene', mode='opengwas',
    outdir='/tmp/mr_out',
    exposure_file='/path/to/exposure.csv',   # snp,beta_exp,se_exp,ea_exp,nea_exp,eaf_exp
    outcome_file='/path/to/outcome.csv',     # snp,beta_out,se_out,ea_out,nea_out,eaf_out
    exposure_label='Exposure trait',
    outcome_label='Outcome trait',
)
```

**eqtl mode kwargs** (same GWAS/eQTL/LD defaults as `run_coloc`)

| kwarg | Default | Description |
|-------|---------|-------------|
| `chr`, `pos` | required | Locus centre |
| `pval_iv` | `5e-8` | IV p-value threshold |
| `pval_iv_fb` | `1e-3` | Fallback threshold (used when pval_iv yields 0 SNPs) |
| `clump_r2` | `0.1` | LD r² for instrument clumping |
| `clump_kb` | `10000` | Window (kb) for clumping |
| `gwas_file/n/s/type` | SLE Bentham | GWAS summary stats (same as run_coloc) |
| `eqtl_dir/n/format/col_*` | DICE | eQTL data (same as run_coloc) |
| `kg_bfile`, `plink` | bundled 1KG EUR | LD reference |

**opengwas mode kwargs**

| kwarg | Default | Description |
|-------|---------|-------------|
| `exposure_id` | required* | OpenGWAS study ID for exposure |
| `outcome_id` | required* | OpenGWAS study ID for outcome |
| `exposure_file` | — | Pre-fetched exposure CSV (skips API) |
| `outcome_file` | — | Pre-fetched outcome CSV (skips API) |
| `pval_iv` | `5e-8` | Instrument p-value threshold |
| `exposure_label` | study ID | Label for plots |
| `outcome_label` | study ID | Label for plots |

\* Required unless `exposure_file` + `outcome_file` are provided.

**OpenGWAS note:** JWT token must be stored in `.env` as `OPENGWAS_TOKEN=<jwt>`. Tokens expire ~2 weeks after issue; renew at https://api.opengwas.io/

**Output files** (per mode)

| File | Description |
|------|-------------|
| `mr_{gene}_{mode}_results.csv` | MR estimates per method (beta, SE, p, Cochran Q, I²) |
| `mr_{gene}_{mode}_scatter.png` | IV effect scatter with MR method lines |
| `mr_{gene}_{mode}_forest.png` | Forest plot: per-IV Wald ratios + overall estimates |
| `mr_{gene}_{mode}_funnel.png` | Funnel plot: IV precision vs ratio estimate |
| `mr_{gene}_eqtl_celltype_summary.png` | (eqtl only) IVW/Wald estimates across cell types |
