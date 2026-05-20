

# Target identification and prioritization 
We use multiple lines of evidence and approaches to identify robust targets associated with conditions and prioritize them. 
## Open target GWAS/credible sets/and L2g analysis
First, query open targets for disease ID:

``` python 
q = '''
query {
  search(queryString: "{disease name}", entityNames: ["disease"], page: {index: 0, size: 3}) {
    hits { id name entity }
  }
}
'''
r = query_opentarget_platform(q)
hits = r['data']['search']['hits']
print('disease IDs in Platform:')
for h in hits:
    print(f"  {h['id']:25s}  {h['name']}")

```
Then, get the credible sets:
``` python
df_raw = get_disease_credible_sets(
    disease_id='MONDO_0007915',
    page_size=50,
    max_cs_pages=20,
    l2g_min_score=0.0,
)
```

- Check the trait names and only keep those that are relevant
``` python
TRAITS = {
    '{desired trait names}
}
df_raw = df_raw[df_raw['trait'].isin(TRAITS)].copy()
```
- Apply L2G score threshold
``` python
top_gene = df_raw[df_raw['l2g_score'] >= 0.5] 
```
- Deduplicate by lead variant across studies
``` python
top_gene['fm_rank'] = (top_gene['finemapping_method'] == 'SuSiE-inf').astype(int)

top_gene = (
    top_gene
    .sort_values(['fm_rank', 'n_samples', 'l2g_score'], ascending=[False, False, False])
    .groupby('variant_id', sort=False)
    .first()
    .reset_index()
    .drop(columns='fm_rank')
)
``` 

- (optional) filter for functional evidence from eQTL
``` python
def has_eqtl_coloc(shap_list):
    if not shap_list:
        return False
    for feat in shap_list:
        if feat['name'] == 'eQtlColocH4Maximum' and feat['value'] > 0:
            return True
    return False

top_gene['eqtl_coloc'] = top_gene['shap_features'].apply(has_eqtl_coloc)
```

## Association with disease at expression level
Find omics data relevant to given disease, run association analysis of genes with disease (e.g. DE analysis). Consider cell type in your analysis if single cell. Prioritize using data in datalake over those accessible using API. If possible, provide multiple line evidence (e.g. multiple datasets).

## Coloc analysis
Use ... code for the analysis.

## Fine mapping
TODO

## Locus 2 gene
TODO

## Mendelian randomization
use full summary stats of eQTL and GWAS, together with LD.
Use ... code for the analysis.

limitations: currently only SLE summary stats is available -> only european ancestry
*Option A* — 2-sample MR via OpenGWAS (most flexible): Add an R script (alongside coloc.R) using the TwoSampleMR package, which connects to the same OpenGWAS API
   already used for PheWAS. Instruments are clumped automatically from OpenGWAS; any exposure × outcome pair can be tested. Main tradeoff: you're bound to traits
   that exist in OpenGWAS, and the JWT token must be active.
  
*Option B* — eQTL → Disease MR (most coherent with existing workflow): Use DICE eQTLs as instruments for gene expression (the exposure) and the local SLE GWAS as
the outcome — same data used by run_coloc. This is a natural follow-up after colocalization: loci with H4 evidence can then be tested for causal effect
direction. Main tradeoff: narrower scope (gene expression → SLE only, unless other GWAS are added to the datalake).

## Mediation analysis
TODO
## Polygenic priority score (PoPS)
TODO

<!-- ## 

how to manage: rare disease, disease without genetic linkage, ancenstry/gender dependent disease, 

rare variant burden meta-analyses -> for variant that are too rare (e,g, <0.1  percent for the minor allele) -> it's for gene to disease assoaiction: for gene, we calculate rare variants on healthy vs disease and determine if the gene is sig or not

target essentiality -> how can we do this? (e.g. CRISPR knockout, and?)


The functional genomics and perturbation:
target essentiality -> TODO
pharmacological tractability -> TODO
 -->
