# mQTL Data Lake

## blueprint/
*BLUEPRINT immune cell mQTL (significant pairs) — Chen et al. 2016, Cell*

Cis-methylation QTL for 3 primary human immune cell types: monocyte (n=191), neutrophil (n=196), T cell (n=167). GRCh37. Methylation measured by 450k array (M-values). All SNP–CpG cis-pairs tested within ±1 Mb of each CpG site.

**Stored**: filtered to **FDR < 0.05** (streamed + filtered from EBI FTP full files; full files are 26 GB/cell type).

**Column schema** (TSV, gzipped):
`chr_pos_ref_alt | rsid | phenotypeID | p.value | beta | Bonferroni.p.value | FDR | alt_allele_frequency | std.error_of_beta`

- `chr_pos_ref_alt` — variant ID as `chr:pos_ref_alt` (GRCh37)
- `rsid` — variant rsID
- `phenotypeID` — CpG site ID (e.g. `cg00000165`)
- `beta`, `std.error_of_beta`, `p.value` — effect and standard error
- `FDR` — Benjamini-Hochberg FDR

For **coloc** (`generic_tsv` format): Note — significant-pairs only. For full-locus colocalization, stream regional data from EBI FTP (see note below).

| File | Cell type | Content |
|------|-----------|---------|
| `mono_meth_fdr05.tsv.gz` | Monocyte | FDR < 0.05 cis-mQTL |
| `neut_meth_fdr05.tsv.gz` | Neutrophil | FDR < 0.05 cis-mQTL |
| `tcel_meth_fdr05.tsv.gz` | T cell | FDR < 0.05 cis-mQTL |

**Full summary stats** (for per-locus coloc) available at EBI FTP — not stored locally due to size (26 GB each):
```
http://ftp.ebi.ac.uk/pub/databases/blueprint/blueprint_Epivar/qtl_as/QTL_RESULTS/mono_meth_M_peer_10_all_summary.txt.gz
http://ftp.ebi.ac.uk/pub/databases/blueprint/blueprint_Epivar/qtl_as/QTL_RESULTS/neut_meth_M_peer_10_all_summary.txt.gz
http://ftp.ebi.ac.uk/pub/databases/blueprint/blueprint_Epivar/qtl_as/QTL_RESULTS/tcel_meth_M_peer_10_all_summary.txt.gz
```
For a specific locus, extract on demand:
```bash
curl -s <url> | zcat | awk '$3 == "cg_site_of_interest"' | gzip > locus_mQTL.tsv.gz
```
