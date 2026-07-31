import os
import pandas as pd

from config import AGING_TF_SIGNATURES, AGING_TF_SIGNATURES_MINOR, AGING_GE_SIGNATURES, AGING_CCC_SIGNATURES, SLE_TF_SIGNATURES, SLE_TF_SIGNATURES_MINOR, SLE_GE_SIGNATURES, SLE_GE_SIGNATURES_MINOR, DRUG_TF_SIGNATURES, CYTOKINE_TF_SIGNATURES

_CONTEXT_PATHS = {
    ('sle',      'tf_activity',     'major'): SLE_TF_SIGNATURES,
    ('sle',      'tf_activity',     'minor'): SLE_TF_SIGNATURES_MINOR,
    ('sle',      'gene_expression', 'major'): SLE_GE_SIGNATURES,
    ('sle',      'gene_expression', 'minor'): SLE_GE_SIGNATURES_MINOR,
    ('drug',     'tf_activity',     'major'): DRUG_TF_SIGNATURES,
    ('cytokine', 'tf_activity',     'major'): CYTOKINE_TF_SIGNATURES,
}

_AGING_FEATURE_PATHS = {
    ('major', 'tf_activity'):     AGING_TF_SIGNATURES,
    ('minor', 'tf_activity'):     AGING_TF_SIGNATURES_MINOR,
    ('major', 'gene_expression'): AGING_GE_SIGNATURES,
    ('major', 'ccc'):             AGING_CCC_SIGNATURES,
}


def predict_immune_age_grn_clock(
    adata,
    cell_type,
    output_dir=None,
):
    """Predict biological age of immune cells using the GRN-based immune aging clock.

    Runs the GRNimmuneClock on a pseudobulk AnnData (samples × genes) and adds
    predicted ages to ``adata.obs['predicted_age']``. Supported cell types: CD4T, CD8T.

    The clock internally aligns input genes to the GRN feature space and applies a
    pre-trained elastic-net regression model (bundled with the package).

    Parameters
    ----------
    adata : AnnData
        Pseudobulk AnnData where rows are donors/samples and columns are genes.
        Expression values should be log-normalised (CPM + log1p). The obs index
        is used as sample identifiers in the output.
    cell_type : str
        Cell type to run the clock on. Must be one of: ``'CD4T'``, ``'CD8T'``.
    output_dir : str, optional
        Directory to save a ``predicted_ages_{cell_type}.csv`` file containing the
        sample index and predicted ages. If None, results are only stored in
        ``adata.obs``.

    Returns
    -------
    str
        Human-readable log of steps performed. Predicted ages are written to
        ``adata.obs['predicted_age']`` in-place.

    Raises
    ------
    ValueError
        If ``cell_type`` is not one of the supported values.
    ImportError
        If ``grnimmuneclock`` is not installed (requires ``ciim.sif``).

    Examples
    --------
    # Predict age for CD4T pseudobulk samples
    import sys
    from aging import predict_immune_age_grn_clock

    log = predict_immune_age_grn_clock(adata_cd4t, cell_type='CD4T', output_dir='/my/output/')
    print(log)
    print(adata_cd4t.obs[['predicted_age']])
    """
    try:
        from grnimmuneclock import AgingClock
    except ImportError:
        raise ImportError(
            "grnimmuneclock is not installed. Run inside ciim.sif or install with: "
            "pip install grnimmuneclock"
        )

    steps = []
    steps.append(f"[predict_immune_age_grn_clock] cell_type={cell_type}, n_samples={adata.n_obs}, n_genes={adata.n_vars}")

    if cell_type not in AgingClock.SUPPORTED_CELL_TYPES:
        raise ValueError(f"cell_type must be one of {AgingClock.SUPPORTED_CELL_TYPES}, got '{cell_type}'")

    clock = AgingClock(cell_type=cell_type)
    steps.append(f"  Loaded clock: {clock}")

    predicted = clock.predict(adata, return_adata=False)
    adata.obs['predicted_age'] = predicted
    steps.append(f"  Predictions added to adata.obs['predicted_age']")
    steps.append(f"  Mean predicted age: {predicted.mean():.1f} yrs  |  Std: {predicted.std():.1f} yrs")

    if output_dir is not None:
        os.makedirs(output_dir, exist_ok=True)
        out_path = os.path.join(output_dir, f"predicted_ages_{cell_type}.csv")
        df_out = pd.DataFrame({'sample': adata.obs.index, 'predicted_age': predicted})
        df_out.to_csv(out_path, index=False)
        steps.append(f"  Saved predictions to: {out_path}")

    return "\n".join(steps)
