"""
Datalake path registry.

All tools should import paths from here rather than constructing them manually.
Paths are resolved relative to this file so the package is location-independent.
"""
import os

_DIR = os.path.dirname(os.path.abspath(__file__))
_AGENTIC_DIR = os.path.dirname(_DIR)

DATALAKE_DIR = _DIR

# ── General references ────────────────────────────────────────────────────────
MARKER_GENES = os.path.join(_DIR, 'prior', 'marker_genes.json')
TF_ALL       = os.path.join(_DIR, 'prior', 'tf_all.csv')

