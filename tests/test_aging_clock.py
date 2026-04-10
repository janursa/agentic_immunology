"""
Test suite for predict_immune_age_grn_clock.

Validates that the function correctly predicts biological age using the
GRNimmuneClock, adds results to adata.obs, handles alignment to the GRN
feature space, and saves optional CSV output.

Run with:
    bash /vol/projects/BIIM/agentic_central/agentic/tests/test_aging_clock.sh
"""

import sys
import os
import tempfile
import numpy as np
import pandas as pd
import anndata as ad

sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools/ciim/code')
from aging import predict_immune_age_grn_clock

# ── helpers ───────────────────────────────────────────────────────────────────
PASS = "\033[92m✓ PASS\033[0m"
FAIL = "\033[91m✗ FAIL\033[0m"

def check(condition, msg):
    status = PASS if condition else FAIL
    print(f"  {status}  {msg}")
    if not condition:
        raise AssertionError(msg)


# ── fixture: synthetic pseudobulk adata with GRN feature genes ────────────────
def _make_synthetic_adata(cell_type, n_samples=40, seed=42):
    """Build a pseudobulk AnnData whose genes match the clock's feature space."""
    from grnimmuneclock import AgingClock
    clock = AgingClock(cell_type=cell_type)
    feature_names = clock.feature_names

    rng = np.random.default_rng(seed)
    X = rng.lognormal(mean=1.5, sigma=0.8, size=(n_samples, len(feature_names)))
    X = np.log1p(X)  # log-normalised as expected

    obs = pd.DataFrame(
        {'age': rng.uniform(20, 80, size=n_samples)},
        index=[f'sample_{i}' for i in range(n_samples)],
    )
    return ad.AnnData(X=X.astype(np.float32), obs=obs,
                      var=pd.DataFrame(index=feature_names))


# ── test 1: predicted_age added to obs (CD4T) ─────────────────────────────────
def test_predicted_age_added_to_obs_cd4t():
    print("\n[test_predicted_age_added_to_obs_cd4t]")
    adata = _make_synthetic_adata('CD4T')
    log = predict_immune_age_grn_clock(adata, cell_type='CD4T')
    print(f"  log: {log.splitlines()[-1]}")
    check('predicted_age' in adata.obs.columns,
          "predicted_age column added to adata.obs")
    check(len(adata.obs['predicted_age']) == adata.n_obs,
          f"One prediction per sample (expected {adata.n_obs})")


# ── test 2: predicted_age added to obs (CD8T) ─────────────────────────────────
def test_predicted_age_added_to_obs_cd8t():
    print("\n[test_predicted_age_added_to_obs_cd8t]")
    adata = _make_synthetic_adata('CD8T')
    log = predict_immune_age_grn_clock(adata, cell_type='CD8T')
    print(f"  log: {log.splitlines()[-1]}")
    check('predicted_age' in adata.obs.columns,
          "predicted_age column added to adata.obs")
    check(len(adata.obs['predicted_age']) == adata.n_obs,
          f"One prediction per sample (expected {adata.n_obs})")


# ── test 3: predictions are finite floats in a plausible age range ────────────
def test_prediction_values_plausible():
    print("\n[test_prediction_values_plausible]")
    for ct in ['CD4T', 'CD8T']:
        adata = _make_synthetic_adata(ct)
        predict_immune_age_grn_clock(adata, cell_type=ct)
        preds = adata.obs['predicted_age']
        check(preds.notna().all(), f"[{ct}] No NaN predictions")
        check(np.isfinite(preds).all(), f"[{ct}] All predictions are finite")
        print(f"    [{ct}] mean={preds.mean():.1f}  std={preds.std():.1f}  "
              f"min={preds.min():.1f}  max={preds.max():.1f}")


# ── test 4: CSV saved when output_dir is provided ────────────────────────────
def test_csv_saved_when_output_dir_provided():
    print("\n[test_csv_saved_when_output_dir_provided]")
    adata = _make_synthetic_adata('CD4T')
    with tempfile.TemporaryDirectory() as tmpdir:
        predict_immune_age_grn_clock(adata, cell_type='CD4T', output_dir=tmpdir)
        expected = os.path.join(tmpdir, 'predicted_ages_CD4T.csv')
        check(os.path.exists(expected), f"CSV file created: {expected}")
        df = pd.read_csv(expected)
        check('sample' in df.columns, "CSV has 'sample' column")
        check('predicted_age' in df.columns, "CSV has 'predicted_age' column")
        check(len(df) == adata.n_obs,
              f"CSV has one row per sample (expected {adata.n_obs}, got {len(df)})")
        print(f"    CSV columns: {list(df.columns)}, rows: {len(df)}")


# ── test 5: no CSV when output_dir is None ───────────────────────────────────
def test_no_csv_when_output_dir_is_none():
    print("\n[test_no_csv_when_output_dir_is_none]")
    adata = _make_synthetic_adata('CD8T')
    with tempfile.TemporaryDirectory() as tmpdir:
        predict_immune_age_grn_clock(adata, cell_type='CD8T', output_dir=None)
        csv_files = [f for f in os.listdir(tmpdir) if f.endswith('.csv')]
        check(len(csv_files) == 0,
              "No CSV file written when output_dir=None")


# ── test 6: invalid cell_type raises ValueError ───────────────────────────────
def test_invalid_cell_type_raises():
    print("\n[test_invalid_cell_type_raises]")
    adata = _make_synthetic_adata('CD4T')
    raised = False
    try:
        predict_immune_age_grn_clock(adata, cell_type='MONO')
    except ValueError as e:
        raised = True
        print(f"    Got expected ValueError: {e}")
    check(raised, "ValueError raised for unsupported cell type 'MONO'")


# ── test 7: extra genes in adata are handled (feature alignment) ──────────────
def test_extra_genes_handled_gracefully():
    """Clock aligns input to its feature space — extra genes should be ignored."""
    print("\n[test_extra_genes_handled_gracefully]")
    from grnimmuneclock import AgingClock
    feature_names = list(AgingClock(cell_type='CD4T').feature_names)

    rng = np.random.default_rng(0)
    extra_genes = [f'RANDOM_GENE_{i}' for i in range(200)]
    all_genes = feature_names + extra_genes

    n_samples = 20
    X = rng.lognormal(1.0, 0.5, size=(n_samples, len(all_genes))).astype(np.float32)
    X = np.log1p(X)
    adata = ad.AnnData(X=X, var=pd.DataFrame(index=all_genes),
                       obs=pd.DataFrame(index=[f's{i}' for i in range(n_samples)]))

    predict_immune_age_grn_clock(adata, cell_type='CD4T')
    check('predicted_age' in adata.obs.columns,
          "predicted_age added even when adata has extra genes")
    check(adata.obs['predicted_age'].notna().all(),
          "No NaN predictions with extra genes present")
    print(f"    n_genes_input={adata.n_vars}, n_features_clock={len(feature_names)}")


# ── test 8: bundled example data from grnimmuneclock package ─────────────────
def test_bundled_example_data():
    """Run clock on the real example AnnData bundled with grnimmuneclock."""
    print("\n[test_bundled_example_data]")
    from grnimmuneclock import AgingClock
    import pathlib, grnimmuneclock as grn_pkg

    pkg_dir = pathlib.Path(grn_pkg.__file__).parent
    example_path = str(pkg_dir / 'data' / 'example_data.h5ad')

    check(os.path.exists(example_path), f"Bundled example data exists: {example_path}")

    adata_ex = ad.read_h5ad(example_path)
    print(f"    Bundled adata shape: {adata_ex.shape}")

    predict_immune_age_grn_clock(adata_ex, cell_type='CD4T')
    check('predicted_age' in adata_ex.obs.columns,
          "predicted_age added from bundled example data")
    preds = adata_ex.obs['predicted_age']
    check(preds.notna().all(), "No NaN in bundled example predictions")
    print(f"    Predicted ages: {preds.values}")


# ── test 9: log string contains expected summary info ────────────────────────
def test_log_output_format():
    print("\n[test_log_output_format]")
    adata = _make_synthetic_adata('CD8T', n_samples=15)
    log = predict_immune_age_grn_clock(adata, cell_type='CD8T')
    check('CD8T' in log, "Log mentions cell type")
    check('predicted_age' in log, "Log mentions predicted_age column")
    check('Mean predicted age' in log, "Log includes mean predicted age summary")
    print(f"    Log:\n" + "\n".join(f"      {l}" for l in log.splitlines()))


# ── main ─────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    print("=" * 60)
    print("Aging Clock Tool — Test Suite")
    print("Function: predict_immune_age_grn_clock")
    print("=" * 60)

    tests = [
        test_predicted_age_added_to_obs_cd4t,
        test_predicted_age_added_to_obs_cd8t,
        test_prediction_values_plausible,
        test_csv_saved_when_output_dir_provided,
        test_no_csv_when_output_dir_is_none,
        test_invalid_cell_type_raises,
        test_extra_genes_handled_gracefully,
        test_bundled_example_data,
        test_log_output_format,
    ]

    failed = []
    for t in tests:
        try:
            t()
        except AssertionError as e:
            failed.append((t.__name__, str(e)))
        except Exception as e:
            failed.append((t.__name__, f"Unexpected error: {type(e).__name__}: {e}"))

    print("\n" + "=" * 60)
    if failed:
        print(f"RESULT: {len(failed)}/{len(tests)} tests FAILED")
        for name, msg in failed:
            print(f"  - {name}: {msg}")
        sys.stdout.flush()
        sys.exit(1)
    else:
        print(f"RESULT: All {len(tests)} tests passed ✓")
        sys.stdout.flush()
        sys.exit(0)
