import os as _os

DATALAKE_DIR = _os.environ["CIIM_DATALAKE_DIR"]
MARKER_GENES = _os.path.join(DATALAKE_DIR, 'prior', 'marker_genes.json')
TF_ALL       = _os.path.join(DATALAKE_DIR, 'prior', 'tf_all.csv')

# Legacy alias
DATA_LAKE = DATALAKE_DIR
