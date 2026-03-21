import os
import sys as _sys
import numpy as np
import pandas as pd
import scanpy as sc

_AGENTIC_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
if _AGENTIC_ROOT not in _sys.path:
    _sys.path.insert(0, _AGENTIC_ROOT)

from datalake import IMMUNE_GRN, TF_ALL

# ── CellTypist label mappings (from hiara preprocess helper) ──────────────────
_CELLTYPIST_MAJOR_MAPPING = {
    'Tcm/Naive helper T cells':      'CD4T',
    'Tem/Effector helper T cells':   'CD4T',
    'Regulatory T cells':            'CD4T',
    'Cycling T cells':               'CD4T',
    'Tem/Temra cytotoxic T cells':   'CD8T',
    'Tcm/Naive cytotoxic T cells':   'CD8T',
    'Tem/Trm cytotoxic T cells':     'CD8T',
    'MAIT cells':                    'CD8T',
    'CD8a/a':                        'CD8T',
    'CD16+ NK cells':                'NK',
    'NK cells':                      'NK',
    'Classical monocytes':           'MONO',
    'Non-classical monocytes':       'MONO',
    'Intermediate macrophages':      'MONO',
    'B cells':                       'B',
    'Naive B cells':                 'B',
    'Memory B cells':                'B',
    'Age-associated B cells':        'B',
    'Plasma cells':                  'B',
    'Plasmablasts':                  'B',
    'DC1':                           'DC',
    'DC2':                           'DC',
    'pDC':                           'DC',
    'HSC/MPP':                       'HSC',
    'Megakaryocytes/platelets':      'Megakaryocyte',
    'ILC':                           'ILC',
    'Double-positive thymocytes':    'T',
    'Late erythroid':                'Erythroid',
}

_CELLTYPIST_SUB_MAPPING = {
    'Tcm/Naive helper T cells':      'Tcm_Naive_CD4',
    'CD16+ NK cells':                'CD16_NK',
    'Classical monocytes':           'Classic_MONO',
    'Tem/Temra cytotoxic T cells':   'Tem_Temra_CD8',
    'Tem/Effector helper T cells':   'Tem_Effector_CD4',
    'Tcm/Naive cytotoxic T cells':   'Tcm_Naive_CD8',
    'Naive B cells':                 'Naive_B',
    'Tem/Trm cytotoxic T cells':     'Tem_Trm_CD8',
    'Memory B cells':                'Memory_B',
    'B cells':                       'Bcells',
    'Non-classical monocytes':       'NonClassic_MONO',
    'MAIT cells':                    'MAIT',
    'Regulatory T cells':            'Treg',
    'DC2':                           'DC2',
    'pDC':                           'pDC',
    'Intermediate macrophages':      'Int_Macrophage',
    'NK cells':                      'NK',
    'Plasma cells':                  'Plasma_B',
    'HSC/MPP':                       'HSC/MPP',
    'Age-associated B cells':        'Aged_B',
    'DC1':                           'DC1',
    'Megakaryocytes/platelets':      'Platelet',
    'Plasmablasts':                  'Plasmablasts_B',
    'ILC':                           'ILC',
    'CD8a/a':                        'CD8a/a',
    'Double-positive thymocytes':    'T',
    'Late erythroid':                'Late_Erythroid',
}

def identify_counts_layer(adata):
    """Identify which slot holds raw integer counts in an AnnData object.

    Checks, in order:
      1. ``adata.layers['counts']``
      2. ``adata.layers['count']``
      3. ``adata.X`` — tested on a random sample for non-negative integer values

    Parameters
    ----------
    adata : AnnData

    Returns
    -------
    str
        ``'counts'``, ``'count'``, or ``'X'``.

    Raises
    ------
    ValueError
        If no integer-count data can be found.
    """
    import scipy.sparse as sp

    def _is_integer_matrix(mat, n_sample: int = 500) -> bool:
        rows = min(n_sample, mat.shape[0])
        sample = mat[:rows]
        arr = sample.toarray() if sp.issparse(sample) else np.asarray(sample)
        return bool((arr >= 0).all() and np.allclose(arr, np.round(arr)))

    for key in ('counts', 'count'):
        if key in adata.layers:
            return key

    if _is_integer_matrix(adata.X):
        return 'X'

    raise ValueError(
        "No raw count data found. Expected adata.layers['counts'], "
        "adata.layers['count'], or integer-valued adata.X."
    )


def annotate_celltype_celltypist(
    adata,
    model: str = 'Immune_All_Low.pkl',
    leiden_res: float = None,
    n_neighbors: int = 10,
    n_pcs: int = 50,
    gpu_cell_threshold: int = 200_000,
):
    """Annotate immune cell types using CellTypist with Leiden-based majority voting.

    Pipeline
    --------
    1. Locate raw counts via :func:`identify_counts_layer`.
    2. Normalize to 10k CPM + log1p on a working copy (for CellTypist input).
    3. Pre-cluster with a **single** Leiden partition (HVG → z-score → PCA → kNN):

       - Uses GPU (``rapids_singlecell``) when ``adata.n_obs >= gpu_cell_threshold``
         **and** the library is importable; falls back to scanpy (CPU) otherwise.
       - ``leiden_res`` auto-selects following CellTypist's over-clustering scale
         (5 / 10 / 15 / 20 / 25 / 30 for <5k / <20k / <40k / <100k / <200k / ≥200k).
       - Copies ``X_pca``, ``connectivities``, ``distances``, ``neighbors`` to ``adata``.

    4. Run CellTypist ``Immune_All_Low.pkl`` (98 fine types, ``majority_voting=False``).
    5. Map per-cell predictions through :data:`_CELLTYPIST_MAJOR_MAPPING` and
       :data:`_CELLTYPIST_SUB_MAPPING`; perform majority voting per Leiden cluster.
    6. Transfer all annotation columns to the original ``adata`` (no layer modification).

    Added ``adata.obs`` columns
    ---------------------------
    * ``leiden``          — cluster IDs
    * ``CT_Major``        — majority-voted coarse label (CD4T, CD8T, NK, MONO, B, DC…)
    * ``CT_Major_percell``— per-cell coarse label (before voting)
    * ``CT_Minor``        — majority-voted fine label (Tcm_Naive_CD4, CD16_NK…)
    * ``CT_Minor_percell``— per-cell fine label (before voting)

    Parameters
    ----------
    adata : AnnData
        AnnData with raw integer counts (auto-detected). Not modified beyond obs/obsm/obsp/uns.
    model : str
        CellTypist model file (default ``'Immune_All_Low.pkl'``, 98 cell types).
    leiden_res : float or None
        Leiden resolution. ``None`` auto-selects by cell count (default ``None``).
    n_neighbors : int
        kNN graph neighbours (default 10).
    n_pcs : int
        Number of PCs (default 50).
    gpu_cell_threshold : int
        Cell count above which GPU is attempted (default 200 000).

    Returns
    -------
    AnnData
        ``adata`` modified in-place.
    """
    import scipy.sparse as sp
    import anndata as ad
    import celltypist
    from celltypist import models

    log = []
    log.append(f"annotate_celltype_celltypist: {adata.n_obs} cells × {adata.n_vars} genes")

    # ── auto leiden_res ───────────────────────────────────────────────────────
    if leiden_res is None:
        n = adata.n_obs
        leiden_res = (5  if n < 5_000  else
                      10 if n < 20_000 else
                      15 if n < 40_000 else
                      20 if n < 100_000 else
                      25 if n < 200_000 else 30)
        log.append(f"leiden_res auto-set to {leiden_res} ({adata.n_obs} cells)")

    # ── 1. locate raw counts ──────────────────────────────────────────────────
    counts_key = identify_counts_layer(adata)
    log.append(f"Raw counts source: {counts_key!r}")
    raw = adata.layers[counts_key] if counts_key != 'X' else adata.X

    # ── 2. normalize → adata_norm (CPM + log1p, for CellTypist) ──────────────
    adata_norm = ad.AnnData(
        X=raw.copy() if sp.issparse(raw) else sp.csr_matrix(raw.copy()),
        obs=pd.DataFrame(index=adata.obs_names),
        var=adata.var.copy(),
    )
    sc.pp.normalize_total(adata_norm, target_sum=1e4)
    sc.pp.log1p(adata_norm)
    log.append("Normalization done (CPM + log1p); used for CellTypist only")

    # ── 3. cluster: HVG → z-score → PCA → kNN → Leiden ───────────────────────
    use_gpu = adata.n_obs >= gpu_cell_threshold
    if use_gpu:
        try:
            import rapids_singlecell as rsc
            log.append("Clustering backend: GPU (rapids_singlecell)")
        except ImportError:
            use_gpu = False
            log.append("rapids_singlecell not importable — falling back to CPU")

    if use_gpu:
        adata_clust = adata_norm.copy()  # copy needed: goes to GPU while adata_norm stays on CPU
        rsc.get.anndata_to_GPU(adata_clust)
        rsc.pp.highly_variable_genes(adata_clust, n_top_genes=3000)
        adata_clust = adata_clust[:, adata_clust.var['highly_variable']].copy()
        rsc.pp.scale(adata_clust, max_value=10)  # z-score per gene for PCA
        rsc.pp.pca(adata_clust, n_comps=n_pcs)
        rsc.pp.neighbors(adata_clust, n_neighbors=n_neighbors)
        rsc.tl.leiden(adata_clust, resolution=leiden_res, key_added='leiden')
        rsc.get.anndata_to_CPU(adata_clust)
    else:
        log.append("Clustering backend: CPU (scanpy)")
        sc.pp.highly_variable_genes(adata_norm, n_top_genes=3000, flavor='seurat')
        adata_clust = adata_norm[:, adata_norm.var['highly_variable']].copy()
        sc.pp.scale(adata_clust, max_value=10)  # z-score per gene for PCA
        sc.tl.pca(adata_clust, n_comps=n_pcs)
        sc.pp.neighbors(adata_clust, n_neighbors=n_neighbors, n_pcs=n_pcs)
        sc.tl.leiden(adata_clust, resolution=leiden_res, key_added='leiden',
                     flavor='igraph', n_iterations=2)

    adata.obs['leiden'] = adata_clust.obs['leiden'].values
    adata.obsm['X_pca'] = adata_clust.obsm['X_pca']
    for key in ('connectivities', 'distances'):
        if key in adata_clust.obsp:
            adata.obsp[key] = adata_clust.obsp[key]
    if 'neighbors' in adata_clust.uns:
        adata.uns['neighbors'] = adata_clust.uns['neighbors']
    log.append(f"leiden: {adata.obs['leiden'].nunique()} clusters (resolution={leiden_res})")

    # ── 4. CellTypist — single model, majority_voting=False ───────────────────
    models.download_models(force_update=False)
    log.append(f"Running CellTypist model: {model}")
    model_obj = models.Model.load(model=model)
    preds = celltypist.annotate(adata_norm, model=model_obj, majority_voting=False)
    raw_labels = preds.to_adata().obs['predicted_labels']  # raw CellTypist labels

    # ── 5. map labels and majority-vote per cluster ───────────────────────────
    def _majority_vote(cluster_series, label_series):
        df = pd.DataFrame({'cluster': cluster_series.values, 'label': label_series.values},
                          index=cluster_series.index)
        vote_map = df.groupby('cluster')['label'].agg(
            lambda x: x.value_counts().index[0])
        return cluster_series.map(vote_map)

    leiden = adata.obs['leiden'].astype(str)

    # CT_Major: map raw → coarse, then majority-vote
    major_percell = raw_labels.map(lambda x: _CELLTYPIST_MAJOR_MAPPING.get(x, 'Others'))
    adata.obs['CT_Major_percell'] = major_percell.values
    adata.obs['CT_Major'] = _majority_vote(leiden, major_percell).values
    log.append(f"CT_Major: {adata.obs['CT_Major'].value_counts().to_dict()}")

    # CT_Minor: map raw → standardised sub, then majority-vote
    minor_percell = raw_labels.map(lambda x: _CELLTYPIST_SUB_MAPPING.get(x, 'Others'))
    adata.obs['CT_Minor_percell'] = minor_percell.values
    adata.obs['CT_Minor'] = _majority_vote(leiden, minor_percell).values
    log.append(f"CT_Minor: {adata.obs['CT_Minor'].value_counts().to_dict()}")

    print("\n".join(log))
    return adata

def get_immune_grn(
    cell_type=None,
    promotor_based_only: bool = False,
    min_weight: float = None,
    source: str = None,
    target: str = None,
) -> pd.DataFrame:
    """Load pre-computed consensus immune GRN(s) for major immune cell types.

    Returns edges from the HIARA multi-cohort consensus gene regulatory networks
    (minDegree2 filtering applied; edges present in ≥2 cohort-level networks).
    Optionally restrict to promoter-supported edges only.

    Parameters
    ----------
    cell_type : str or list of str, optional
        Filter to one or more cell types. Valid values: 'CD4T', 'CD8T', 'NK', 'B', 'MONO'.
        If None, all cell types are returned.
    promotor_based_only : bool
        If True, return only edges also supported by promoter-based TF binding evidence
        (i.e. ``promotor_based == True``). Default False.
    min_weight : float, optional
        Keep only edges with ``|weight| >= min_weight``.
    source : str or list of str, optional
        Filter to specific TF source gene(s).
    target : str or list of str, optional
        Filter to specific target gene(s).

    Returns
    -------
    pd.DataFrame
        Columns: ``source``, ``target``, ``weight``, ``cell_type``, ``promotor_based``.

    Examples
    --------
    # All CD4T consensus edges
    df = get_immune_grn(cell_type='CD4T')

    # Promoter-supported edges for FOXP1 as source across all cell types
    df = get_immune_grn(source='FOXP1', promotor_based_only=True)

    # Strong NK edges (|weight| >= 0.1)
    df = get_immune_grn(cell_type='NK', min_weight=0.1)
    """
    path = IMMUNE_GRN
    df = pd.read_csv(path)

    if cell_type is not None:
        if isinstance(cell_type, str):
            cell_type = [cell_type]
        df = df[df['cell_type'].isin(cell_type)]

    if promotor_based_only:
        df = df[df['promotor_based']]

    if min_weight is not None:
        df = df[df['weight'].abs() >= min_weight]

    if source is not None:
        if isinstance(source, str):
            source = [source]
        df = df[df['source'].isin(source)]

    if target is not None:
        if isinstance(target, str):
            target = [target]
        df = df[df['target'].isin(target)]

    return df.reset_index(drop=True)


def infer_grn_spearman(
    adata_path: str,
    output_file: str,
    data_type: str = "sc",
    group_col: str = None,
    group: str = None,
    tf_list_path: str = None,
    p_value_filter: bool = True,
    top_n_edges: int = 100_000,
    min_cells_per_gene: int = 10,
    min_genes_per_cell: int = 10,
    layer_norm: str = None,
    layer_count: str = None,
) -> str:
    """Infer a gene regulatory network (GRN) from expression data using Spearman correlation.

    Computes pairwise Spearman correlations between all genes, applies Benjamini-Hochberg
    FDR correction (optional), and restricts edges to those where the source gene is a
    known transcription factor (TF).  The resulting edge list is saved as a CSV.

    The prior TF list defaults to
    ``data_lake/ciim/tf_all.csv`` (1 638 human TFs), which can be overridden via
    *tf_list_path*.

    Parameters
    ----------
    adata_path : str
        Absolute path to an ``.h5ad`` AnnData file.
    output_file : str
        Absolute path where the inferred network (CSV) will be saved.
        Columns: ``source, target, weight`` (Spearman rho), and optionally
        ``promotor_based`` if the skeleton file is present.
    data_type : str, optional
        ``'sc'`` (single-cell, default) or ``'bulk'``.
    group_col : str, optional
        ``adata.obs`` column name used to subset cells (e.g. ``'Major_CT'``).
        Requires *group*.
    group : str, optional
        Value in *group_col* to keep (e.g. ``'CD4T'``).
    tf_list_path : str, optional
        Path to a plain-text file with one TF gene symbol per line.
        Defaults to ``data_lake/ciim/tf_all.csv``.
    p_value_filter : bool, optional
        Apply Benjamini-Hochberg FDR correction and keep only edges with
        adjusted p-value < 0.05.  Default ``True``.
    top_n_edges : int, optional
        Keep only the top N edges ranked by |Spearman rho|.  Default 100 000.
    min_cells_per_gene : int, optional
        Remove genes expressed in fewer than this many cells (sc only).  Default 10.
    min_genes_per_cell : int, optional
        Remove cells with fewer than this many detected genes (sc only).  Default 10.
    layer_norm : str, optional
        Name of a layer in ``adata.layers`` that already contains normalised /
        log-transformed expression.  When provided, this layer is used directly
        for correlation and the normalisation step is skipped entirely.
    layer_count : str, optional
        Name of a layer in ``adata.layers`` that contains raw counts to be used
        for normalisation instead of ``adata.X``.  Library-size normalisation +
        log1p will be applied to this layer.  Ignored if *layer_norm* is set.

    Returns
    -------
    str
        Human-readable log of steps performed and the path to the saved network.

    Examples
    --------
    >>> result = infer_grn_spearman(
    ...     adata_path='/data/pbmc.h5ad',
    ...     output_file='/output/grn_CD4T.csv',
    ...     cell_type_key='cell_type',
    ...     cell_type='CD4T',
    ... )
    >>> print(result)
    """
    import os
    import numpy as np
    import pandas as pd
    import anndata as ad
    import scanpy as sc
    from scipy.stats import spearmanr
    from scipy.sparse import issparse
    from statsmodels.stats.multitest import multipletests

    steps = []

    # ── prior paths ──────────────────────────────────────────────────────────
    if tf_list_path is None:
        tf_list_path = TF_ALL
    skeleton_path = os.path.join(PRIOR_DIR, "skeleton_promotor.csv") #TODO: make this vailable

    # ── load data ─────────────────────────────────────────────────────────────
    steps.append(f"Loading AnnData from: {adata_path}")
    adata = ad.read_h5ad(adata_path)
    steps.append(f"Loaded: {adata.n_obs} cells × {adata.n_vars} genes")

    # ── optional group subset ─────────────────────────────────────────────────
    if group_col is not None and group is not None:
        mask = adata.obs[group_col] == group
        adata = adata[mask].copy()
        steps.append(f"Subset to {group} ({adata.n_obs} cells)")

    # ── basic QC ──────────────────────────────────────────────────────────────
    if data_type == "sc":
        sc.pp.filter_genes(adata, min_cells=min_cells_per_gene)
        sc.pp.filter_cells(adata, min_genes=min_genes_per_cell)
        steps.append(f"After QC: {adata.n_obs} cells × {adata.n_vars} genes")

    # ── select & normalise expression matrix ──────────────────────────────────
    def _is_count_like(mat):
        """Return True if matrix looks like raw integer counts."""
        sample = mat[:100] if mat.shape[0] > 100 else mat
        if issparse(sample):
            sample = sample.toarray()
        else:
            sample = np.asarray(sample)
        return (sample >= 0).all() and np.allclose(sample, sample.astype(int))

    def _normalize(mat):
        tmp = ad.AnnData(X=mat if not issparse(mat) else mat)
        sc.pp.normalize_total(tmp, inplace=True)
        sc.pp.log1p(tmp)
        return tmp.X

    if layer_norm is not None:
        # Use a pre-normalised layer directly — no further transformation
        if layer_norm not in adata.layers:
            raise ValueError(f"layer_norm='{layer_norm}' not found in adata.layers. "
                             f"Available: {list(adata.layers.keys())}")
        X = adata.layers[layer_norm]
        steps.append(f"Using pre-normalised layer '{layer_norm}' (no further normalisation)")

    elif layer_count is not None:
        # Use specified layer as raw counts → normalise
        if layer_count not in adata.layers:
            raise ValueError(f"layer_count='{layer_count}' not found in adata.layers. "
                             f"Available: {list(adata.layers.keys())}")
        X = _normalize(adata.layers[layer_count])
        steps.append(f"Normalised layer '{layer_count}' (library-size + log1p)")

    elif data_type == "sc":
        # Auto-detect the right source:
        #   1. adata.layers['counts'] → use it as raw counts
        #   2. adata.X looks count-like → normalise it
        #   3. Otherwise assume adata.X is already normalised
        if "counts" in adata.layers:
            X = _normalize(adata.layers["counts"])
            steps.append("Auto-detected raw counts in adata.layers['counts']; applied library-size + log1p")
        elif _is_count_like(adata.X):
            X = _normalize(adata.X)
            steps.append("adata.X appears count-like; applied library-size + log1p")
        else:
            X = adata.X
            steps.append("adata.X appears already normalised; used as-is")

    else:
        # bulk — use adata.X as-is
        X = adata.X
        steps.append("Bulk mode: using adata.X as-is")


    if issparse(X):
        X = X.toarray()
    gene_names = np.array(adata.var_names)

    # ── remove zero-variance genes ────────────────────────────────────────────
    stds = X.std(axis=0)
    nonzero = stds > 0
    n_removed = int((~nonzero).sum())
    if n_removed:
        steps.append(f"Removed {n_removed} zero-variance genes")
    X = X[:, nonzero]
    gene_names = gene_names[nonzero]
    steps.append(f"Computing Spearman correlation: {X.shape[0]} samples × {X.shape[1]} genes")

    # ── spearman correlation ──────────────────────────────────────────────────
    corr, p_values = spearmanr(X, nan_policy="raise")
    # spearmanr returns a scalar when there are only 2 variables — guard against that
    if np.ndim(corr) == 0:
        raise ValueError("Need at least 2 genes with nonzero variance to compute a GRN.")
    steps.append(f"Spearman correlation matrix shape: {corr.shape}")

    # ── build directed edge list (A→B and B→A) ────────────────────────────────
    src, tgt = np.meshgrid(gene_names, gene_names, indexing="ij")
    mask = src.flatten() != tgt.flatten()  # exclude self-loops upfront
    net = pd.DataFrame({
        "source": src.flatten()[mask],
        "target": tgt.flatten()[mask],
        "weight": corr.flatten()[mask],
    }).reset_index(drop=True)

    # ── FDR correction ────────────────────────────────────────────────────────
    if p_value_filter:
        p_flat = p_values.flatten()[mask]
        _, fdr, _, _ = multipletests(p_flat, method="fdr_bh")
        net = net[fdr < 0.05].reset_index(drop=True)
        steps.append(f"After FDR < 0.05 filter: {len(net)} edges")

    # ── TF filter ─────────────────────────────────────────────────────────────
    tf_all = np.loadtxt(tf_list_path, dtype=str)
    n_before = len(net)
    net = net[net["source"].isin(tf_all)].reset_index(drop=True)
    steps.append(f"TF filter ({len(tf_all)} TFs): {n_before} → {len(net)} edges")

    # ── optional promoter-skeleton annotation ─────────────────────────────────
    if os.path.exists(skeleton_path):
        skeleton = pd.read_csv(skeleton_path)
        net["edge"] = net["source"] + "_" + net["target"]
        net["promotor_based"] = net["edge"].isin(skeleton["edge"])
        net = net.drop("edge", axis=1)
        steps.append(f"Annotated promoter-based edges ({net['promotor_based'].sum()} edges flagged)")

    # ── top-N edges ───────────────────────────────────────────────────────────
    net = net.sort_values("weight", ascending=False, key=abs).head(top_n_edges).reset_index(drop=True)
    steps.append(f"Kept top {len(net)} edges by |rho|")

    # ── save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_file)), exist_ok=True)
    net.to_csv(output_file, index=False)
    steps.append(f"Network saved to: {output_file}")

    return "\n".join(steps)




def qc_sc_transcriptomics(
    adata_path: str,
    output_path: str,
    group_col: str = None,
    min_genes: int = 100,
    max_genes: int = 5000,
    max_pct_mt: float = 20.0,
) -> str:
    """Apply the standard single-cell RNA-seq QC protocol and save the filtered
    AnnData object.

    Steps (in order):
      1. Flag mitochondrial genes (``MT-`` prefix) and compute QC metrics.
      2. Filter cells: keep those with ``min_genes`` ≤ n_genes_by_counts ≤ ``max_genes``
         and ``pct_counts_mt`` ≤ ``max_pct_mt``.
      3. Filter genes: remove genes expressed in fewer than
         ``max(n_groups × 10, 10)`` cells (where ``n_groups`` is the number of
         unique values in ``group_col``, or 1 if not provided), and genes with
         ``total_counts < 1``.
      4. Assert ``adata.X`` contains raw integer counts before saving.

    Parameters
    ----------
    adata_path : str
        Path to input ``.h5ad`` file with raw counts in ``adata.X``.
    output_path : str
        Path where the filtered ``.h5ad`` will be written.
    group_col : str, optional
        ``obs`` column used to count bulk groups (donor × condition) for the
        per-gene min-cells threshold.  If ``None``, treated as 1 group.
    min_genes : int
        Minimum number of genes per cell (default 100).
    max_genes : int
        Maximum number of genes per cell (default 5000).
    max_pct_mt : float
        Maximum mitochondrial read percentage per cell (default 20.0).

    Returns
    -------
    str
        Log of QC steps and cell/gene counts before and after each filter.
    """
    import scanpy as sc
    import numpy as np

    steps = []

    adata = sc.read_h5ad(adata_path)
    steps.append(f"Loaded: {adata.shape[0]} cells × {adata.shape[1]} genes")

    # ── 1. mitochondrial QC metrics ───────────────────────────────────────────
    adata.var["mt"] = adata.var_names.str.startswith("MT-")
    sc.pp.calculate_qc_metrics(
        adata, qc_vars=["mt"], percent_top=None, log1p=False, inplace=True
    )
    steps.append(
        f"MT genes flagged: {adata.var['mt'].sum()}  "
        f"(median pct_counts_mt per cell: {adata.obs['pct_counts_mt'].median():.1f}%)"
    )

    # ── 2. cell filters ───────────────────────────────────────────────────────
    n_before = adata.n_obs
    sc.pp.filter_cells(adata, min_genes=min_genes)
    steps.append(
        f"Filter min_genes={min_genes}: {n_before} → {adata.n_obs} cells "
        f"(removed {n_before - adata.n_obs})"
    )

    n_before = adata.n_obs
    sc.pp.filter_cells(adata, max_genes=max_genes)
    steps.append(
        f"Filter max_genes={max_genes}: {n_before} → {adata.n_obs} cells "
        f"(removed {n_before - adata.n_obs})"
    )

    n_before = adata.n_obs
    adata = adata[adata.obs["pct_counts_mt"] <= max_pct_mt].copy()
    steps.append(
        f"Filter pct_counts_mt≤{max_pct_mt}%: {n_before} → {adata.n_obs} cells "
        f"(removed {n_before - adata.n_obs})"
    )

    # ── 3. gene filters ───────────────────────────────────────────────────────
    if group_col and group_col in adata.obs.columns:
        n_groups = adata.obs[group_col].nunique()
    else:
        n_groups = 1
    min_cells = max(n_groups * 10, 10)
    steps.append(
        f"Gene min_cells threshold: max({n_groups} groups × 10, 10) = {min_cells}"
    )

    n_before = adata.n_vars
    sc.pp.filter_genes(adata, min_cells=min_cells)
    steps.append(
        f"Filter min_cells={min_cells}: {n_before} → {adata.n_vars} genes "
        f"(removed {n_before - adata.n_vars})"
    )

    n_before = adata.n_vars
    sc.pp.filter_genes(adata, min_counts=1)
    steps.append(
        f"Filter min_counts=1: {n_before} → {adata.n_vars} genes "
        f"(removed {n_before - adata.n_vars})"
    )

    # ── 4. sanity-check raw counts ────────────────────────────────────────────
    X = adata.X
    if hasattr(X, "toarray"):
        X = X.toarray()
    X_sample = X[:200, :200]
    if not (X_sample >= 0).all():
        raise ValueError("adata.X contains negative values — expected raw counts.")
    if not np.allclose(X_sample, X_sample.astype(int)):
        steps.append(
            "WARNING: adata.X does not appear to contain integer counts. "
            "Ensure QC is run on raw counts."
        )
    else:
        steps.append("Sanity check passed: adata.X contains raw integer counts.")

    # ── save ──────────────────────────────────────────────────────────────────
    os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
    adata.write_h5ad(output_path)
    steps.append(f"Saved filtered AnnData: {output_path}")
    steps.append(f"Final shape: {adata.n_obs} cells × {adata.n_vars} genes")

    return "\n".join(steps)


def annotate_celltype_ulm(
    adata,
    output_dir: str,
    marker_dict: dict,
    leiden_key_major: str = 'leiden_major',
    leiden_key_minor: str = 'leiden_minor',
    major_key: str = 'Major',
    minor_key: str = 'Minor',
    min_cells_per_cluster: int = 10,
) -> str:
    """Annotate cell types using decoupler ULM on pseudobulk profiles per cluster.

    For each granularity level (major, minor), pseudobulk profiles are computed by
    summing raw counts per Leiden cluster. ULM is then run on these pseudobulk profiles
    (not per cell), and each cluster is assigned the cell type with the highest ULM
    score. Labels are propagated back to individual cells.

    The Leiden clusters must already exist in ``adata.obs`` — typically computed by
    :func:`annotate_celltype_celltypist`.

    Parameters
    ----------
    adata : AnnData
        AnnData with raw integer counts and pre-computed Leiden cluster columns.
    output_dir : str
        Directory for output files.
    marker_dict : dict
        Nested dict mapping level key → {cell_type: [marker_genes]}.  Example::

            {
                'Major': {'CD8T': ['CD8A', 'CD8B', 'GZMB'],
                          'CD4T': ['CD4', 'IL7R', 'TCF7']},
                'Minor': {'Naive_CD4': ['TCF7', 'CCR7', 'SELL'],
                          'Treg':      ['FOXP3', 'IL2RA']}
            }

    leiden_key_major : str
        obs column with major-level Leiden clusters (default ``'leiden_major'``).
    leiden_key_minor : str
        obs column with minor-level Leiden clusters (default ``'leiden_minor'``).
    major_key : str
        Key in ``marker_dict`` for major cell types (default ``'Major'``).
    minor_key : str
        Key in ``marker_dict`` for minor cell types (default ``'Minor'``).
    min_cells_per_cluster : int
        Minimum cells required for a cluster to be included (default 10).

    Returns
    -------
    str
        Human-readable log of steps and output file paths.

    Outputs (in ``output_dir``)
    ---------------------------
    * ``ulm_cluster_summary_<level>.csv`` — per-cluster ULM scores + assigned label
    * ``ulm_activity_heatmap_<level>.png`` — heatmap of ULM scores (clusters × cell types)
    """
    import anndata as ad
    import scipy.sparse as sp
    import decoupler as dc
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt

    log = []
    os.makedirs(output_dir, exist_ok=True)
    log.append(f"annotate_celltype_ulm: {adata.n_obs} cells × {adata.n_vars} genes")

    # ── locate raw counts ────────────────────────────────────────────────────
    counts_key = identify_counts_layer(adata)
    log.append(f"Raw counts source: {counts_key!r}")

    # ── pseudobulk helper ────────────────────────────────────────────────────
    def _pseudobulk(leiden_col):
        raw = adata.layers[counts_key] if counts_key != 'X' else adata.X
        clusters = adata.obs[leiden_col].astype(str)
        unique_clusters = sorted(clusters.unique())
        rows, obs_rows, kept = [], [], []
        for cid in unique_clusters:
            mask = (clusters == cid).values
            n_cells = int(mask.sum())
            if n_cells < min_cells_per_cluster:
                continue
            summed = np.asarray(raw[mask].sum(axis=0)).flatten()
            rows.append(summed)
            obs_rows.append({'cluster_id': cid, 'cell_count': n_cells})
            kept.append(cid)
        X_bulk = np.vstack(rows)
        obs_df = pd.DataFrame(obs_rows, index=kept)
        adata_bulk = ad.AnnData(
            X=sp.csr_matrix(X_bulk),
            obs=obs_df,
            var=pd.DataFrame(index=adata.var_names),
        )
        sc.pp.normalize_total(adata_bulk, target_sum=1e6)
        sc.pp.log1p(adata_bulk)
        return adata_bulk, kept

    # ── network builder ──────────────────────────────────────────────────────
    def _build_net(marker_subdict, level_name):
        rows = []
        for ct, genes in marker_subdict.items():
            for g in genes:
                if g in adata.var_names:
                    rows.append({'source': ct, 'target': g, 'weight': 1.0})
        net = pd.DataFrame(rows)
        n_missing = sum(
            1 for ct, genes in marker_subdict.items()
            for g in genes if g not in adata.var_names
        )
        log.append(f"[{level_name}] network: {len(net)} pairs ({n_missing} genes absent)")
        return net

    # ── per-level runner ─────────────────────────────────────────────────────
    def _run_level(marker_subdict, level_name, leiden_col, ct_obs_col):
        if leiden_col not in adata.obs.columns:
            log.append(f"[{level_name}] '{leiden_col}' not in adata.obs — skipping")
            return
        net = _build_net(marker_subdict, level_name)
        if net.empty:
            log.append(f"[{level_name}] no valid markers — skipping")
            return

        adata_bulk, kept_clusters = _pseudobulk(leiden_col)
        log.append(f"[{level_name}] pseudobulk: {len(kept_clusters)} clusters "
                   f"(≥{min_cells_per_cluster} cells each)")

        dc.mt.ulm(adata_bulk, net=net, tmin=2, verbose=False)
        scores = adata_bulk.obsm['score_ulm'].copy()  # clusters × cell_types
        scores.index = kept_clusters

        # assign cluster label = argmax ULM score
        cluster_to_ct = scores.idxmax(axis=1)

        # propagate to individual cells
        cell_labels = adata.obs[leiden_col].astype(str).map(cluster_to_ct)
        adata.obs[ct_obs_col] = cell_labels.fillna('Unknown').values
        log.append(f"[{level_name}] label distribution: "
                   f"{adata.obs[ct_obs_col].value_counts().to_dict()}")

        # ── cluster summary CSV ───────────────────────────────────────────
        cell_types = scores.columns.tolist()
        clust_df = scores.copy()
        clust_df.index.name = 'cluster'
        clust_df.insert(0, 'assigned_ct', cluster_to_ct.values)
        clust_df.insert(1, 'cell_count', adata_bulk.obs['cell_count'].values)
        clust_path = os.path.join(output_dir, f"ulm_cluster_summary_{level_name}.csv")
        clust_df.to_csv(clust_path)
        log.append(f"[{level_name}] cluster summary: {clust_path}")

        # ── activity heatmap ──────────────────────────────────────────────
        fig, ax = plt.subplots(
            figsize=(max(4, len(cell_types) * 1.5), max(3, len(kept_clusters) * 0.5 + 1))
        )
        im = ax.imshow(scores.values, aspect='auto', cmap='viridis')
        ax.set_xticks(range(len(cell_types)))
        ax.set_xticklabels(cell_types, rotation=40, ha='right', fontsize=9)
        ax.set_yticks(range(len(kept_clusters)))
        ax.set_yticklabels(kept_clusters, fontsize=7)
        ax.set_xlabel('Cell type')
        ax.set_ylabel('Cluster')
        ax.set_title(f'ULM score (pseudobulk) — {level_name}')
        plt.colorbar(im, ax=ax, label='ULM score')
        plt.tight_layout()
        hmap_path = os.path.join(output_dir, f"ulm_activity_heatmap_{level_name}.png")
        fig.savefig(hmap_path, dpi=150, bbox_inches='tight')
        plt.close(fig)
        log.append(f"[{level_name}] heatmap: {hmap_path}")

    # ── run major ────────────────────────────────────────────────────────────
    if major_key in marker_dict:
        _run_level(marker_dict[major_key], major_key, leiden_key_major, 'ulm_Major_ct')
    else:
        log.append(f"'{major_key}' not in marker_dict — skipping major")

    # ── run minor ────────────────────────────────────────────────────────────
    if minor_key in marker_dict:
        _run_level(marker_dict[minor_key], minor_key, leiden_key_minor, 'ulm_Minor_ct')
    else:
        log.append(f"'{minor_key}' not in marker_dict — skipping minor")

    return "\n".join(log)


def analyze_cluster_celltype_annotation_quality(
    adata,
    output_dir: str,
    cluster_key: str = 'leiden',
    consistency_threshold: float = 0.8,
) -> str:
    """Assess annotation quality at the cluster level via two comparisons.

    1. **Per-cell CellTypist vs majority-voted** (``CT_Major_percell`` /
       ``CT_Minor_percell`` vs ``CT_Major`` / ``CT_Minor``):
       For each cluster, computes the fraction of cells whose per-cell CellTypist
       prediction matches the cluster's majority-voted label.  Clusters below
       *consistency_threshold* are flagged as ambiguous.

    2. **ULM vs CellTypist majority-voted** (``ulm_Major_ct`` / ``ulm_Minor_ct``
       vs ``CT_Major`` / ``CT_Minor``):
       For each cluster reports whether the ULM-assigned label agrees with the
       CellTypist majority-voted label.

    Added ``adata.obs`` columns
    ---------------------------
    * ``annotation_qc_pass_major`` — True if the cell's cluster has CT_Major
      per-cell consistency ≥ *consistency_threshold*
    * ``annotation_qc_pass_minor`` — same for CT_Minor

    Outputs
    -------
    * ``percell_consistency.csv``    — per-cluster per-cell consistency scores
    * ``method_agreement.csv``       — per-cluster ULM vs CT agreement
    * ``flagged_clusters.csv``       — clusters flagged by either check
    * ``consistency_barplot_CT_Major.png`` / ``_CT_Minor.png``
    * ``method_agreement_barplot_major.png`` / ``_minor.png``

    Parameters
    ----------
    adata : AnnData
        Annotated object with columns ``CT_Major``, ``CT_Minor``,
        ``CT_Major_percell``, ``CT_Minor_percell``, ``ulm_Major_ct``,
        ``ulm_Minor_ct``, and ``cluster_key`` in ``.obs``.
    output_dir : str
        Directory where all output files are saved.
    cluster_key : str
        ``adata.obs`` column with cluster assignments (default ``'leiden'``).
    consistency_threshold : float
        Per-cell consistency below this value flags a cluster (default 0.8).

    Returns
    -------
    str
        Human-readable summary.
    """
    import matplotlib
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    import os

    log = []
    os.makedirs(output_dir, exist_ok=True)

    log.append(f"analyze_cluster_celltype_annotation_quality: "
               f"{adata.n_obs} cells, cluster_key='{cluster_key}', "
               f"threshold={consistency_threshold}")

    if cluster_key not in adata.obs.columns:
        raise ValueError(f"cluster_key '{cluster_key}' not in adata.obs")

    clusters = sorted(
        adata.obs[cluster_key].astype(str).unique(),
        key=lambda x: int(x) if x.isdigit() else x,
    )

    # ── 1. per-cell CellTypist consistency ────────────────────────────────────
    pairs_ct = [
        ('CT_Major_percell', 'CT_Major', 'Major'),
        ('CT_Minor_percell', 'CT_Minor', 'Minor'),
    ]
    consistency_records = []
    flagged_consistency = []

    for percell_col, voted_col, level in pairs_ct:
        missing = [c for c in (percell_col, voted_col) if c not in adata.obs.columns]
        if missing:
            log.append(f"[{level}] skipping consistency — missing columns: {missing}")
            continue
        for cl in clusters:
            mask = adata.obs[cluster_key].astype(str) == cl
            n = int(mask.sum())
            voted_label = adata.obs.loc[mask, voted_col].iloc[0]
            percell = adata.obs.loc[mask, percell_col].astype(str)
            consistency = float((percell == voted_label).sum() / n)
            rec = {
                'cluster': cl, 'level': level,
                'voted_label': voted_label,
                'n_cells': n,
                'consistency': round(consistency, 4),
            }
            consistency_records.append(rec)
            if consistency < consistency_threshold:
                top2 = percell.value_counts().head(2)
                second = (f"{top2.index[1]} ({top2.iloc[1]/n:.1%})"
                          if len(top2) > 1 else '—')
                flagged_consistency.append({**rec, 'second_label': second})

    cons_df = pd.DataFrame(consistency_records)
    flagged_cons_df = pd.DataFrame(flagged_consistency) if flagged_consistency else pd.DataFrame()

    if not cons_df.empty:
        cons_path = os.path.join(output_dir, 'percell_consistency.csv')
        cons_df.to_csv(cons_path, index=False)
        log.append(f"Per-cell consistency saved: {cons_path}")

        for level in cons_df['level'].unique():
            sub = cons_df[cons_df['level'] == level].copy()
            mean_cons = sub['consistency'].mean()
            n_flagged = (sub['consistency'] < consistency_threshold).sum()
            log.append(f"  [{level}] mean consistency={mean_cons:.3f}, "
                       f"flagged={n_flagged}/{len(sub)} clusters")

            colors = ['#d73027' if c < consistency_threshold else '#4575b4'
                      for c in sub['consistency']]
            fig, ax = plt.subplots(figsize=(max(6, len(sub)*0.25), 4))
            ax.bar(sub['cluster'], sub['consistency'], color=colors)
            ax.axhline(consistency_threshold, color='black', linestyle='--',
                       linewidth=0.8, label=f'threshold={consistency_threshold}')
            ax.set_xlabel('Cluster')
            ax.set_ylabel('Consistency (per-cell vs majority-voted)')
            ax.set_title(f'CT_{level}: per-cell consistency per cluster')
            ax.tick_params(axis='x', rotation=90)
            ax.legend(fontsize=8)
            plt.tight_layout()
            plot_path = os.path.join(output_dir, f'consistency_barplot_CT_{level}.png')
            fig.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            log.append(f"  [{level}] plot saved: {plot_path}")

    # ── 2. ULM vs CellTypist majority-voted agreement ─────────────────────────
    pairs_ulm = [
        ('ulm_Major_ct', 'CT_Major', 'Major'),
        ('ulm_Minor_ct', 'CT_Minor', 'Minor'),
    ]
    agreement_records = []

    for ulm_col, ct_col, level in pairs_ulm:
        missing = [c for c in (ulm_col, ct_col) if c not in adata.obs.columns]
        if missing:
            log.append(f"[{level}] skipping agreement — missing columns: {missing}")
            continue
        for cl in clusters:
            mask = adata.obs[cluster_key].astype(str) == cl
            n = int(mask.sum())
            ct_label  = adata.obs.loc[mask, ct_col].iloc[0]
            ulm_label = adata.obs.loc[mask, ulm_col].iloc[0]
            agreement_records.append({
                'cluster': cl, 'level': level,
                'CT_label': ct_label,
                'ULM_label': ulm_label,
                'agree': ct_label == ulm_label,
                'n_cells': n,
            })

    agree_df = pd.DataFrame(agreement_records)
    flagged_agree_df = agree_df[~agree_df['agree']] if not agree_df.empty else pd.DataFrame()

    if not agree_df.empty:
        agree_path = os.path.join(output_dir, 'method_agreement.csv')
        agree_df.to_csv(agree_path, index=False)
        log.append(f"Method agreement saved: {agree_path}")

        for level in agree_df['level'].unique():
            sub = agree_df[agree_df['level'] == level]
            n_agree = sub['agree'].sum()
            log.append(f"  [{level}] ULM vs CT agreement: "
                       f"{n_agree}/{len(sub)} clusters ({n_agree/len(sub):.1%})")

            colors = ['#4575b4' if a else '#d73027' for a in sub['agree']]
            fig, ax = plt.subplots(figsize=(max(6, len(sub)*0.25), 4))
            ax.bar(sub['cluster'], sub['n_cells'], color=colors)
            ax.set_xlabel('Cluster')
            ax.set_ylabel('Cell count')
            ax.set_title(f'{level}: ULM vs CT agreement per cluster\n'
                         f'(blue=agree, red=disagree)')
            ax.tick_params(axis='x', rotation=90)
            plt.tight_layout()
            plot_path = os.path.join(output_dir, f'method_agreement_barplot_{level}.png')
            fig.savefig(plot_path, dpi=150, bbox_inches='tight')
            plt.close(fig)
            log.append(f"  [{level}] plot saved: {plot_path}")

        # disagreement details
        if not flagged_agree_df.empty:
            log.append("\n── ULM vs CT disagreements ──")
            for _, row in flagged_agree_df.iterrows():
                log.append(
                    f"  cluster={row['cluster']} [{row['level']}]  "
                    f"CT='{row['CT_label']}'  ULM='{row['ULM_label']}'  "
                    f"n_cells={row['n_cells']}"
                )

    # ── write per-cell QC pass flag back to adata.obs ────────────────────────
    if not cons_df.empty:
        for level, obs_col in [('Major', 'annotation_qc_pass_major'),
                                ('Minor', 'annotation_qc_pass_minor')]:
            sub = cons_df[cons_df['level'] == level][['cluster', 'consistency']]
            pass_clusters = set(
                sub.loc[sub['consistency'] >= consistency_threshold, 'cluster'].astype(str)
            )
            adata.obs[obs_col] = (
                adata.obs[cluster_key].astype(str).isin(pass_clusters)
            )
            n_pass = adata.obs[obs_col].sum()
            log.append(f"  [{level}] annotation_qc_pass: "
                       f"{n_pass}/{adata.n_obs} cells pass ({n_pass/adata.n_obs:.1%})")

    # ── combined flagged output ───────────────────────────────────────────────
    all_flagged = []
    if not flagged_cons_df.empty:
        flagged_cons_df['flag_reason'] = 'low_percell_consistency'
        all_flagged.append(flagged_cons_df[['cluster', 'level', 'voted_label',
                                            'n_cells', 'consistency', 'flag_reason']])
    if not flagged_agree_df.empty:
        tmp = flagged_agree_df[['cluster', 'level', 'CT_label', 'ULM_label', 'n_cells']].copy()
        tmp['flag_reason'] = 'ulm_ct_disagreement'
        all_flagged.append(tmp)
    if all_flagged:
        all_flagged_df = pd.concat(all_flagged, ignore_index=True)
        flag_path = os.path.join(output_dir, 'flagged_clusters.csv')
        all_flagged_df.to_csv(flag_path, index=False)
        log.append(f"\nTotal flagged clusters: {len(all_flagged_df)}")
        log.append(f"Flagged saved: {flag_path}")
    else:
        log.append("\nNo clusters flagged.")

    return "\n".join(log)


def infer_tf_activity(
    adata,
    net: pd.DataFrame,
    method: str = 'ulm',
    use_raw: bool = False,
    min_n: int = 2,
    verbose: bool = False,
) -> pd.DataFrame:
    """Infer transcription factor (TF) activity from expression data using decoupler.

    Wraps ``decoupler`` enrichment methods to score TF activity across observations
    (cells, pseudobulk samples, or bulk donors). Works with any AnnData regardless
    of whether the data is single-cell or bulk/pseudobulk — the caller is responsible
    for providing appropriately normalised expression in ``adata.X``.

    Parameters
    ----------
    adata : AnnData
        Expression matrix (obs × genes). ``adata.X`` should be log-normalised values
        (e.g. log1p(CPM)). Raw integer counts also work but may give noisier results.
    net : pd.DataFrame
        Regulatory network with columns ``source`` (TF), ``target`` (gene), and
        optionally ``weight`` (numeric; defaults to 1.0 if absent). Typically loaded
        via :func:`get_immune_grn`.
    method : str
        Decoupler enrichment method. One of ``'ulm'``, ``'waggr'``, ``'mlm'``.
        Default is ``'ulm'`` (Univariate Linear Model).
    use_raw : bool
        If True, use ``adata.raw.X`` instead of ``adata.X``. Default False.
    min_n : int
        Minimum number of targets per TF required to run the method. TFs with fewer
        targets in the data are dropped. Default 2.
    verbose : bool
        Print decoupler progress. Default False.

    Returns
    -------
    pd.DataFrame
        Activity score matrix (obs × TFs). Index matches ``adata.obs_names``.

    Examples
    --------
    # Single-cell: TF activity per cell
    from genomics import get_immune_grn, infer_tf_activity
    net = get_immune_grn(cell_type='CD8T')
    tf_scores = infer_tf_activity(adata, net=net)

    # Pseudobulk/bulk: TF activity per donor
    tf_scores = infer_tf_activity(adata_bulk, net=net, method='ulm')
    """
    import decoupler as dc

    if 'weight' not in net.columns:
        net = net.copy()
        net['weight'] = 1.0

    method_fn = {
        'ulm':   dc.mt.ulm,
        'waggr': dc.mt.waggr,
        'mlm':   dc.mt.mlm,
    }
    if method not in method_fn:
        raise ValueError(f"method must be one of {list(method_fn)}, got '{method}'")

    method_fn[method](adata, net=net, tmin=min_n, raw=use_raw, verbose=verbose)

    score_key = f'score_{method}'
    if score_key not in adata.obsm:
        raise RuntimeError(
            f"Expected '{score_key}' in adata.obsm after running decoupler, but it was not found. "
            "Check that your net has overlapping genes with adata.var_names."
        )

    scores = adata.obsm[score_key].copy()
    scores.index = adata.obs_names
    return scores
