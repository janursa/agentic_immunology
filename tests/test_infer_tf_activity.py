"""
Test suite for infer_tf_activity.

Tests cover:
  1. Basic smoke test — returns a DataFrame with the right shape
  2. Output index matches adata.obs_names
  3. All three methods (ulm, wsum, mlm) run and produce scores
  4. Works on single-cell data (many obs)
  5. Works on pseudobulk/bulk data (few obs)
  6. min_n filter removes TFs with too few targets in the data
  7. Missing weight column is handled gracefully (defaults to 1.0)
  8. Error raised for unknown method
  9. Error raised when no gene overlap between adata and net

Run with:
    bash /vol/projects/BIIM/agentic_central/agentic/tests/test_infer_tf_activity.sh
"""

import sys
import numpy as np
import pandas as pd
import anndata as ad

sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools/ciim/code')
from genomics import infer_tf_activity, get_immune_grn

# ── helpers ───────────────────────────────────────────────────────────────────
PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"

def check(condition, msg):
    status = PASS if condition else FAIL
    print(f"  {status}  {msg}")
    if not condition:
        raise AssertionError(msg)


# ── synthetic fixture ─────────────────────────────────────────────────────────
def _make_adata(n_obs=50, n_genes=200, seed=42):
    """Tiny synthetic AnnData with log-normalised expression."""
    rng = np.random.default_rng(seed)
    X = rng.exponential(scale=1.0, size=(n_obs, n_genes)).astype(np.float32)
    obs_names = [f'obs_{i}' for i in range(n_obs)]
    var_names = [f'GENE_{i}' for i in range(n_genes)]
    return ad.AnnData(X=X, obs=pd.DataFrame(index=obs_names),
                      var=pd.DataFrame(index=var_names))


def _make_net(adata, n_tfs=5, n_targets_per_tf=10, seed=0):
    """Synthetic network using gene names from adata."""
    rng = np.random.default_rng(seed)
    genes = list(adata.var_names)
    tfs = genes[:n_tfs]
    rows = []
    for tf in tfs:
        targets = rng.choice(genes[n_tfs:], size=n_targets_per_tf, replace=False)
        for t in targets:
            rows.append({'source': tf, 'target': t, 'weight': rng.uniform(0.1, 1.0)})
    return pd.DataFrame(rows)


# ── test 1: basic smoke test ──────────────────────────────────────────────────
def test_basic_smoke():
    print("\n[test_basic_smoke]")
    adata = _make_adata()
    net   = _make_net(adata)
    scores = infer_tf_activity(adata, net=net)
    check(isinstance(scores, pd.DataFrame), "Returns a DataFrame")
    check(scores.shape[0] == adata.n_obs,   f"Row count = n_obs ({scores.shape[0]} == {adata.n_obs})")
    check(scores.shape[1] > 0,              f"At least one TF scored ({scores.shape[1]} TFs)")
    print(f"  Shape: {scores.shape}")


# ── test 2: index matches obs_names ──────────────────────────────────────────
def test_index_matches_obs_names():
    print("\n[test_index_matches_obs_names]")
    adata  = _make_adata()
    net    = _make_net(adata)
    scores = infer_tf_activity(adata, net=net)
    check(list(scores.index) == list(adata.obs_names),
          "Output index matches adata.obs_names")


# ── test 3: all three methods run ────────────────────────────────────────────
def test_all_methods():
    print("\n[test_all_methods]")
    adata = _make_adata()
    net   = _make_net(adata)
    for method in ('ulm', 'waggr', 'mlm'):
        scores = infer_tf_activity(adata.copy(), net=net, method=method)
        check(isinstance(scores, pd.DataFrame), f"[{method}] Returns DataFrame")
        check(scores.shape[0] == adata.n_obs,   f"[{method}] Correct row count")
        check(not scores.isnull().all().all(),   f"[{method}] Not all NaN")
        print(f"  [{method}] shape={scores.shape}")


# ── test 4: works on single-cell scale (large n_obs) ─────────────────────────
def test_single_cell_scale():
    print("\n[test_single_cell_scale]")
    adata  = _make_adata(n_obs=2000, n_genes=300)
    net    = _make_net(adata, n_tfs=8, n_targets_per_tf=15)
    scores = infer_tf_activity(adata, net=net)
    check(scores.shape[0] == 2000, f"2000 cells scored (got {scores.shape[0]})")
    print(f"  Shape: {scores.shape}")


# ── test 5: works on pseudobulk/bulk scale (small n_obs) ─────────────────────
def test_pseudobulk_scale():
    print("\n[test_pseudobulk_scale]")
    adata  = _make_adata(n_obs=20, n_genes=300)
    net    = _make_net(adata, n_tfs=5, n_targets_per_tf=10)
    scores = infer_tf_activity(adata, net=net)
    check(scores.shape[0] == 20, f"20 donors scored (got {scores.shape[0]})")
    print(f"  Shape: {scores.shape}")


# ── test 6: min_n filters TFs with too few targets ───────────────────────────
def test_min_n_filter():
    print("\n[test_min_n_filter]")
    adata = _make_adata(n_obs=50, n_genes=50)
    # TF_A has 5 targets in data; TF_B has only 1
    net = pd.DataFrame([
        {'source': 'GENE_0', 'target': f'GENE_{i}', 'weight': 1.0} for i in range(10, 15)
    ] + [
        {'source': 'GENE_1', 'target': 'GENE_20', 'weight': 1.0}  # only 1 target
    ])
    scores_strict = infer_tf_activity(adata.copy(), net=net, min_n=2)
    scores_loose  = infer_tf_activity(adata.copy(), net=net, min_n=1)
    check('GENE_0' in scores_strict.columns, "GENE_0 (5 targets) passes min_n=2")
    check('GENE_1' not in scores_strict.columns, "GENE_1 (1 target) filtered by min_n=2")
    check('GENE_1' in scores_loose.columns,  "GENE_1 (1 target) passes min_n=1")


# ── test 7: missing weight column defaults gracefully ────────────────────────
def test_missing_weight_column():
    print("\n[test_missing_weight_column]")
    adata = _make_adata()
    net_no_weight = _make_net(adata)[['source', 'target']]   # drop weight
    check('weight' not in net_no_weight.columns, "weight column absent in input net")
    scores = infer_tf_activity(adata, net=net_no_weight)
    check(isinstance(scores, pd.DataFrame), "Runs successfully without weight column")
    check(scores.shape[0] == adata.n_obs,   "Correct row count")


# ── test 8: unknown method raises ValueError ──────────────────────────────────
def test_bad_method_raises():
    print("\n[test_bad_method_raises]")
    adata = _make_adata()
    net   = _make_net(adata)
    try:
        infer_tf_activity(adata, net=net, method='bogus')
        check(False, "Should have raised ValueError for unknown method")
    except ValueError as e:
        check("bogus" in str(e), f"ValueError mentions bad method name: {e}")


# ── test 9: no gene overlap raises an error ───────────────────────────────────
def test_no_gene_overlap_raises():
    print("\n[test_no_gene_overlap_raises]")
    adata = _make_adata()
    # network genes are completely disjoint from adata.var_names
    net_disjoint = pd.DataFrame([
        {'source': 'TFXYZ', 'target': 'TARGETABC', 'weight': 1.0},
        {'source': 'TFXYZ', 'target': 'TARGETDEF', 'weight': 1.0},
    ])
    try:
        infer_tf_activity(adata, net=net_disjoint)
        check(False, "Should have raised an error for no gene overlap")
    except Exception as e:
        check(True, f"Error raised as expected ({type(e).__name__})")


# ── test 10: real GRN from datalake ──────────────────────────────────────────
def test_real_grn():
    """Smoke-test with the actual immune GRN from the datalake."""
    print("\n[test_real_grn]")
    net = get_immune_grn(cell_type='CD8T')
    check(len(net) > 0, f"Loaded CD8T GRN ({len(net)} edges)")

    # Build synthetic adata whose var_names include real GRN target genes
    all_genes = list(set(net['target'].tolist() + net['source'].tolist()))
    n_genes = min(500, len(all_genes))
    genes = all_genes[:n_genes]
    rng = np.random.default_rng(7)
    X = rng.exponential(1.0, size=(30, n_genes)).astype(np.float32)
    adata = ad.AnnData(X=X, obs=pd.DataFrame(index=[f's{i}' for i in range(30)]),
                       var=pd.DataFrame(index=genes))

    scores = infer_tf_activity(adata, net=net)
    check(isinstance(scores, pd.DataFrame), "Returns DataFrame with real GRN")
    check(scores.shape[0] == 30,            f"30 obs scored (got {scores.shape[0]})")
    check(scores.shape[1] > 0,              f"At least one TF scored ({scores.shape[1]})")
    check(not scores.isnull().all().all(),   "Scores are not all NaN")
    print(f"  Shape: {scores.shape}  ({scores.shape[1]} TFs active)")


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("infer_tf_activity — Test Suite")
    print("=" * 60)

    tests = [
        test_basic_smoke,
        test_index_matches_obs_names,
        test_all_methods,
        test_single_cell_scale,
        test_pseudobulk_scale,
        test_min_n_filter,
        test_missing_weight_column,
        test_bad_method_raises,
        test_no_gene_overlap_raises,
        test_real_grn,
    ]

    failed = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed.append((t.__name__, str(e)))
        except Exception as e:
            failed.append((t.__name__, f"Unexpected error: {e}"))

    print("\n" + "=" * 60)
    if failed:
        print(f"RESULT: {len(failed)}/{len(tests)} tests FAILED")
        for name, msg in failed:
            print(f"  ✗ {name}: {msg}")
        sys.exit(1)
    else:
        print(f"RESULT: All {len(tests)} tests passed ✓")
        sys.exit(0)
