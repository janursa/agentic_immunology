import os as _os
import sys as _sys

_AGENTIC_ROOT = _os.path.normpath(_os.path.join(_os.path.dirname(_os.path.abspath(__file__)), '..', '..', '..'))
if _AGENTIC_ROOT not in _sys.path:
    _sys.path.insert(0, _AGENTIC_ROOT)

from datalake import (
    DATALAKE_DIR,
    AGING_TF_SIGNATURES,
    AGING_TF_SIGNATURES_MINOR,
    AGING_GE_SIGNATURES,
    AGING_CCC_SIGNATURES,
    SLE_TF_SIGNATURES,
    DRUG_TF_SIGNATURES,
    CYTOKINE_TF_SIGNATURES,
    IMMUNE_GRN,
    MARKER_GENES,
    TF_ALL,
)

# Legacy alias
DATA_LAKE = DATALAKE_DIR
