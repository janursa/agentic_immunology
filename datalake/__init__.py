"""
Datalake path registry.

All tools should import paths from here rather than constructing them manually.
Paths are resolved relative to this file so the package is location-independent.
"""
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENTIC_DIR = os.path.dirname(_DIR)

DATALAKE_DIR = _DIR

# ── Summary statistics ────────────────────────────────────────────────────────
_SS       = os.path.join(_DIR, 'summary_stats')
_SS_HIRA = os.path.join(_SS, 'hira')
_SS_SLE   = os.path.join(_SS, 'sle')
AGING_TF_SIGNATURES       = os.path.join(_SS_HIRA, 'immune_aging_tf_signatures_major_celltypes.csv')
AGING_TF_SIGNATURES_MINOR = os.path.join(_SS_HIRA, 'immune_aging_tf_signatures_minor_celltypes.csv')
AGING_GE_SIGNATURES       = os.path.join(_SS_HIRA, 'immune_aging_gene_expression_signatures_major_celltypes.csv')
AGING_CCC_SIGNATURES      = os.path.join(_SS_HIRA, 'immune_aging_ccc_signatures_major_celltypes.csv')
SLE_TF_SIGNATURES         = os.path.join(_SS_SLE, 'sle_tf_signatures_major_celltypes.csv')
SLE_TF_SIGNATURES_MINOR   = os.path.join(_SS_SLE, 'sle_tf_signatures_sub_celltypes.csv')
SLE_GE_SIGNATURES         = os.path.join(_SS_SLE, 'sle_gene_expression_signatures_major_celltypes.csv')
SLE_GE_SIGNATURES_MINOR   = os.path.join(_SS_SLE, 'sle_gene_expression_signatures_sub_celltypes.csv')
DRUG_TF_SIGNATURES        = os.path.join(_SS_HIRA, 'drug_tf_signatures_major_immune_celltypes.csv')
CYTOKINE_TF_SIGNATURES    = os.path.join(_SS_HIRA, 'cytokine_tf_signatures_major_immune_celltypes.csv')
IMMUNE_GRN                = os.path.join(_SS_HIRA, 'immune_gene_regulatory_networks_major_cts.csv')

# ── General references ────────────────────────────────────────────────────────
MARKER_GENES = os.path.join(_DIR, 'prior', 'marker_genes.json')
TF_ALL       = os.path.join(_DIR, 'prior', 'tf_all.csv')

