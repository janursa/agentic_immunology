import os
import pandas as pd

from config import AGING_TF_SIGNATURES, AGING_TF_SIGNATURES_MINOR, AGING_GE_SIGNATURES, AGING_CCC_SIGNATURES, SLE_TF_SIGNATURES, DRUG_TF_SIGNATURES, CYTOKINE_TF_SIGNATURES

_CONTEXT_PATHS = {
    'sle':      SLE_TF_SIGNATURES,
    'drug':     DRUG_TF_SIGNATURES,
    'cytokine': CYTOKINE_TF_SIGNATURES,
}

_AGING_FEATURE_PATHS = {
    ('major', 'tf_activity'):     AGING_TF_SIGNATURES,
    ('minor', 'tf_activity'):     AGING_TF_SIGNATURES_MINOR,
    ('major', 'gene_expression'): AGING_GE_SIGNATURES,
    ('major', 'ccc'):             AGING_CCC_SIGNATURES,
}


def retrieve_summary_stats(
    context,
    feature_type='tf_activity',
    cell_resolution='major',
    cell_type=None,
    p_adj_threshold=None,
    trend=None,
    dataset=None,
    direction=None,
    age_group=None,
):
    """Unified loader for all immune summary statistics.

    Parameters
    ----------
    context : str
        Which summary stat to retrieve. One of: ``'aging'``, ``'sle'``, ``'drug'``, ``'cytokine'``.

        - ``'aging'``    : multi-cohort immune aging signatures (healthy donors; onek1k, abf300, aida, perez_sle)
        - ``'sle'``      : SLE vs healthy TF differential activity (Perez cohort)
        - ``'drug'``     : Ruxolitinib vs DMSO TF differential activity (OP ex-vivo)
        - ``'cytokine'`` : IL-10 vs PBS TF differential activity (ParseBioscience ex-vivo)

    feature_type : str, optional
        [``context='aging'`` only] Molecular feature type:

        - ``'tf_activity'``      (default): TF activity scores inferred via GRN
        - ``'gene_expression'`` : bulk gene expression (log-normalised counts)
        - ``'ccc'``             : cell-cell communication L-R pair scores (LIANA rank_aggregate).
                                  The ``gene`` column encodes interactions as
                                  ``source_ct__ligand__target_ct__receptor`` (double underscore).

    cell_resolution : str, optional
        [``context='aging'``, ``feature_type='tf_activity'`` only] Cell type resolution.
        One of: ``'major'`` (default; CD4T, CD8T, NK, B, MONO),
        ``'minor'`` (11 sub-types: CD16_NK, Classic_MONO, MAIT, Memory_B, Naive_B,
        NonClassic_MONO, Tcm_Naive_CD4, Tcm_Naive_CD8, Tem_Effector_CD4, Tem_Temra_CD8, Tem_Trm_CD8).

    cell_type : str or list of str, optional
        Filter by cell type. Valid values depend on context and cell_resolution.
        Not applicable for ``context='aging', feature_type='ccc'`` (cell_type column is always ``'all'``).

    p_adj_threshold : float, optional
        Significance filter (keep rows at or below threshold):

        - ``context='aging'``: filters ``meta_p_adj``
        - ``context`` in ``('sle', 'drug', 'cytokine')``: filters ``p_value_adj``

    trend : str or list of str, optional
        [``context='aging'`` only] Filter by aging trend.
        Valid values: ``'Increase in aging'``, ``'Decrease in aging'``, ``'Inconsistent'``.

    dataset : str or list of str, optional
        [``context='aging'`` only] Filter by cohort.
        Valid values: ``'onek1k'``, ``'abf300'``, ``'aida'``, ``'perez_sle'``.

    direction : str or list of str, optional
        [``context`` in ``('sle', 'drug', 'cytokine')``] Filter by effect direction.

        - ``'sle'``     : ``'Increase in SLE'``, ``'Decrease in SLE'``
        - ``'drug'``    : ``'Increase'``, ``'Decrease'``
        - ``'cytokine'``: ``'Increase'``, ``'Decrease'``

    age_group : str or list of str, optional
        [``context='sle'`` only] Filter by age group (e.g. ``'Both age groups'``).

    Returns
    -------
    pd.DataFrame
        Filtered statistics table. Columns depend on context:

        - Aging (tf_activity / gene_expression):
          ``gene``, ``p_value``, ``slope``, ``p_value_adj``, ``condition``, ``comparison``,
          ``dataset``, ``cell_type``, ``meta_p``, ``meta_p_adj``, ``neg_log10_adj_pval``, ``trend``
        - Aging (ccc): same columns; ``gene`` encodes ``src__ligand__tgt__receptor``
        - SLE:
          ``gene``, ``p_value``, ``slope``, ``p_value_adj``, ``neg_log10_adj_pval``,
          ``ctrl``, ``condition``, ``comparison``, ``age_group``, ``dataset``, ``cell_type``, ``direction``
        - Drug / Cytokine:
          ``gene``, ``p_value``, ``slope``, ``p_value_adj``, ``neg_log10_adj_pval``,
          ``ctrl``, ``condition``, ``comparison``, ``age_group``, ``cell_type``, ``direction``

    Examples
    --------
    # Significant TFs increasing with age in CD8T (major, TF activity)
    df = retrieve_summary_stats('aging', cell_type='CD8T', trend='Increase in aging', p_adj_threshold=0.05)

    # Gene expression aging signatures in minor cell types
    df = retrieve_summary_stats('aging', feature_type='gene_expression', cell_type='Tcm_Naive_CD4')

    # CCC aging signatures (parse gene column for components)
    df = retrieve_summary_stats('aging', feature_type='ccc', p_adj_threshold=0.05, dataset='abf300')
    parts = df['gene'].str.split('__', expand=True)
    df['source_ct'], df['ligand'], df['target_ct'], df['receptor'] = parts[0], parts[1], parts[2], parts[3]

    # SLE TFs increased in B cells
    df = retrieve_summary_stats('sle', cell_type='B', direction='Increase in SLE', p_adj_threshold=0.05)

    # Ruxolitinib-affected TFs in CD4T
    df = retrieve_summary_stats('drug', cell_type='CD4T', p_adj_threshold=0.05)

    # IL-10 cytokine signatures
    df = retrieve_summary_stats('cytokine', cell_type='B', direction='Increase', p_adj_threshold=0.05)
    """
    _VALID_CONTEXTS = ('aging', 'sle', 'drug', 'cytokine')
    if context not in _VALID_CONTEXTS:
        raise ValueError(f"context must be one of {_VALID_CONTEXTS}, got '{context}'")

    # ── aging ──────────────────────────────────────────────────────────────
    if context == 'aging':
        _VALID_FEATURE_TYPES = ('tf_activity', 'gene_expression', 'ccc')
        if feature_type not in _VALID_FEATURE_TYPES:
            raise ValueError(f"feature_type must be one of {_VALID_FEATURE_TYPES}, got '{feature_type}'")

        _VALID_RESOLUTIONS = ('major', 'minor')
        if cell_resolution not in _VALID_RESOLUTIONS:
            raise ValueError(f"cell_resolution must be one of {_VALID_RESOLUTIONS}, got '{cell_resolution}'")

        if cell_resolution == 'minor' and feature_type != 'tf_activity':
            raise ValueError("cell_resolution='minor' is only available for feature_type='tf_activity'")

        path = _AGING_FEATURE_PATHS[(cell_resolution, feature_type)]
        df = pd.read_csv(path)

        if cell_type is not None:
            cell_type = [cell_type] if isinstance(cell_type, str) else cell_type
            df = df[df['cell_type'].isin(cell_type)]

        if trend is not None:
            trend = [trend] if isinstance(trend, str) else trend
            df = df[df['trend'].isin(trend)]

        if p_adj_threshold is not None:
            df = df[df['meta_p_adj'] <= p_adj_threshold]

        if dataset is not None:
            dataset = [dataset] if isinstance(dataset, str) else dataset
            df = df[df['dataset'].isin(dataset)]

    # ── sle / drug / cytokine ──────────────────────────────────────────────
    else:
        df = pd.read_csv(_CONTEXT_PATHS[context])

        if cell_type is not None:
            cell_type = [cell_type] if isinstance(cell_type, str) else cell_type
            df = df[df['cell_type'].isin(cell_type)]

        if p_adj_threshold is not None:
            df = df[df['p_value_adj'] <= p_adj_threshold]

        if direction is not None:
            direction = [direction] if isinstance(direction, str) else direction
            df = df[df['direction'].isin(direction)]

        if age_group is not None and context == 'sle':
            age_group = [age_group] if isinstance(age_group, str) else age_group
            df = df[df['age_group'].isin(age_group)]

    return df.reset_index(drop=True)


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
    sys.path.insert(0, '/vol/projects/BIIM/agentic_central/agentic/tools/ciim/code')
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


def immune_aging_signatures_major_celltypes(
    cell_type=None,
    trend=None,
    meta_p_adj_threshold=None,
    dataset=None,
    feature_type='tf_activity',
):
    """Deprecated wrapper — use ``retrieve_summary_stats('aging', ...)`` instead."""
    return retrieve_summary_stats(
        context='aging',
        feature_type=feature_type,
        cell_resolution='major',
        cell_type=cell_type,
        trend=trend,
        p_adj_threshold=meta_p_adj_threshold,
        dataset=dataset,
    )


def immune_aging_tf_signatures_minor_celltypes(
    cell_type=None,
    trend=None,
    meta_p_adj_threshold=None,
    dataset=None,
):
    """Deprecated wrapper — use ``retrieve_summary_stats('aging', cell_resolution='minor', ...)`` instead."""
    return retrieve_summary_stats(
        context='aging',
        feature_type='tf_activity',
        cell_resolution='minor',
        cell_type=cell_type,
        trend=trend,
        p_adj_threshold=meta_p_adj_threshold,
        dataset=dataset,
    )


def sle_tf_signatures_major_celltypes(
    cell_type=None,
    p_adj_threshold=None,
    direction=None,
    age_group=None,
):
    """Deprecated wrapper — use ``retrieve_summary_stats('sle', ...)`` instead."""
    return retrieve_summary_stats(
        context='sle',
        cell_type=cell_type,
        p_adj_threshold=p_adj_threshold,
        direction=direction,
        age_group=age_group,
    )


def drug_tf_signatures_major_celltypes(
    cell_type=None,
    p_adj_threshold=None,
    direction=None,
):
    """Deprecated wrapper — use ``retrieve_summary_stats('drug', ...)`` instead."""
    return retrieve_summary_stats(
        context='drug',
        cell_type=cell_type,
        p_adj_threshold=p_adj_threshold,
        direction=direction,
    )


def cytokine_tf_signatures_major_celltypes(
    cell_type=None,
    p_adj_threshold=None,
    direction=None,
):
    """Deprecated wrapper — use ``retrieve_summary_stats('cytokine', ...)`` instead."""
    return retrieve_summary_stats(
        context='cytokine',
        cell_type=cell_type,
        p_adj_threshold=p_adj_threshold,
        direction=direction,
    )
