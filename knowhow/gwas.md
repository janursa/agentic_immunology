# GWAS Analysis Know-How

## Overview

Two main resources for SNP → disease/trait associations:

| Resource | Coverage | Access | p-value threshold | Best for |
|----------|----------|--------|-------------------|----------|
| **GWAS Catalog** | ~130k published studies, 622k associations | Local pickle (`.pkl`) | p < 5e-8 (curated) | Quick look-up in published literature |
| **OpenGWAS** | >10k studies incl. Neale Lab UKB (~4k), Pan-UKBB (~7k), IEU curated | REST API (JWT auth) | Configurable (1e-5 → 5e-8) | Comprehensive PheWAS, UKB deep phenotyping |

---

## GWAS Catalog

**Local path**: `agentic_immunology/datalake/biomni/gwas_catalog.pkl`  
**Size**: 622,784 associations, 34 columns  
**UKB entries**: ~64k (filter by `INITIAL SAMPLE SIZE` containing `"UK Biobank"`)

Key columns:

| Column | Description |
|--------|-------------|
| `SNPS` | rsID |
| `DISEASE/TRAIT` | trait label |
| `PVALUE_MLOG` | -log10(p-value) |
| `INITIAL SAMPLE SIZE` | cohort description |
| `MAPPED_GENE` | nearest gene(s) |

**Limitations**: Does not include Neale Lab or Pan-UKBB results. Only genome-wide significant hits (p<5e-8). Use OpenGWAS for broader phenome-wide searches.

**Usage**:
```python
from genetics import query_gwas_catalog
hits = query_gwas_catalog(['rs10944479', 'rs1004870'])
hits[['SNPS', 'DISEASE/TRAIT', 'PVALUE_MLOG']].head()
```

---

## OpenGWAS

**Website**: https://api.opengwas.io  
**Authentication**: JWT token (free registration required)  
**Token storage**: `agentic_immunology/.env` as `OPENGWAS_TOKEN=<jwt>`  
**Token expiry**: ~2 weeks; renew at https://api.opengwas.io/

### API Details

- **Endpoint**: `POST https://api.opengwas.io/api/phewas`
- **Auth header**: `Authorization: Bearer <token>` (NOT `X-Api-Token`)
- **Request body**: `{"variant": ["rs123", "rs456"], "pval": 1e-5}`
- **Parameter name**: `variant` (not `variant_id`)
- **Batch size**: ≤30 SNPs per request to avoid timeouts

### Study ID Prefixes

| Prefix | Source | Phenotypes |
|--------|--------|------------|
| `ukb-b-*` | Neale Lab UKB (round 2) | ~4,000 |
| `ukb-d-*` | IEU UKB disease endpoints | ~800 |
| `ieu-b-*` | IEU curated GWAS | ~1,000 |
| `eqtl-*` | eQTL Catalogue | gene expression (filter these out for trait PheWAS) |
| `prot-*` | Protein GWAS | plasma proteomics |
| `met-*` | Metabolomics GWAS | metabolite levels |

### Recommended p-value Thresholds

| Use case | Threshold |
|----------|-----------|
| Strict replication (GWAS significant) | 5e-8 |
| Discovery / PheWAS | 1e-5 |
| Hypothesis generation | 1e-4 |

### Usage
```python
from genetics import phewas_opengwas

# All associations for a list of SNPs
hits = phewas_opengwas(['rs10944479', 'rs1004870'], pval=1e-5)

# UKB only
ukb_hits = hits[hits['is_ukb']].sort_values('p')

# Top trait per SNP
top = hits.sort_values('p').groupby('rsid').first().reset_index()
```

---

## When to Use Which

1. **Quick literature check**: Use GWAS Catalog → faster, no API needed, only published hits
2. **UKB phenome-wide scan**: Use OpenGWAS with `ukb-b-*` / `ukb-d-*` prefix filter
3. **Comprehensive PheWAS**: Use OpenGWAS with all studies and `drop_expression=True`
4. **Large SNP lists (>500)**: Use OpenGWAS in batches of 30; expect ~1 min per 100 SNPs

---

## CIIM Tool

See `tools/ciim/genetics.md` for the `phewas_opengwas` and `query_gwas_catalog` function signatures.
