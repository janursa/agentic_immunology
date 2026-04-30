# genetics — GWAS & Genetic Variant Tools

Module: `tools/ciim/code/genetics.py`

---

## Functions

### `phewas_opengwas(snps, pval=5e-8, ...)`

PheWAS look-up across **all** OpenGWAS indexed studies. Best for comprehensive disease mapping of a list of lead SNPs.

```python
import sys
sys.path.insert(0, '/vol/projects/CIIM/agentic_central/tools/ciim/code')
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

## Notes

- Token must be stored in `/vol/projects/CIIM/agentic_central/.env` as `OPENGWAS_TOKEN=<jwt>`
- Tokens expire ~2 weeks after issue; renew at https://api.opengwas.io/
- Study ID prefixes: `ukb-b-*` = Neale Lab UKB, `ukb-d-*` = IEU disease, `ieu-b-*` = IEU curated, `eqtl-*` = eQTL studies (auto-filtered)
- See `knowhow/gwas.md` for full resource comparison and recommended thresholds
