import os
import sys as _sys
import numpy as np
import pandas as pd
import scanpy as sc

_AGENTIC_ROOT = os.path.normpath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', '..'))
if _AGENTIC_ROOT not in _sys.path:
    _sys.path.insert(0, _AGENTIC_ROOT)

from datalake import IMMUNE_GRN, TF_ALL, DATALAKE_DIR
PRIOR_DIR = os.path.join(DATALAKE_DIR, 'prior')

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


# ── CellxGene Census ──────────────────────────────────────────────────────────

def _cellxgene_open(census_version: str = "stable"):
    import cellxgene_census
    return cellxgene_census.open_soma(census_version=census_version)


def _cellxgene_filter(*clauses) -> str | None:
    parts = [c for c in clauses if c]
    return " and ".join(parts) if parts else None


def _cellxgene_in(col, val) -> str | None:
    if val is None:
        return None
    if isinstance(val, str):
        return f"{col} == '{val}'"
    quoted = ", ".join(f"'{v}'" for v in val)
    return f"{col} in [{quoted}]"


def cellxgene_query_obs(
    cell_type=None,
    tissue=None,
    disease=None,
    sex: str | None = None,
    organism: str = "homo_sapiens",
    extra_filter: str | None = None,
    columns: list | None = None,
    census_version: str = "stable",
) -> pd.DataFrame:
    """Query cell-level metadata from CellxGene Census without downloading expression data.

    Parameters
    ----------
    cell_type : str or list[str]
        Cell Ontology label(s), e.g. "CD4-positive, alpha-beta T cell".
    tissue : str or list[str]
        UBERON tissue label(s), e.g. "blood", "lung".
    disease : str or list[str]
        Disease label(s), e.g. "normal", "systemic lupus erythematosus".
    sex : str
        "male" or "female".
    organism : str
        "homo_sapiens" (default) or "mus_musculus".
    extra_filter : str
        Raw TileDB SOMA filter appended with AND.
    columns : list[str]
        Which obs columns to return. None → all available.
        Key columns: soma_joinid, dataset_id, cell_type, tissue, disease,
        sex, donor_id, development_stage, assay, self_reported_ethnicity.
    census_version : str
        "stable" = latest stable release.

    Returns
    -------
    pd.DataFrame
    """
    value_filter = _cellxgene_filter(
        _cellxgene_in("cell_type", cell_type),
        _cellxgene_in("tissue", tissue),
        _cellxgene_in("disease", disease),
        _cellxgene_in("sex", sex),
        extra_filter,
    )
    with _cellxgene_open(census_version) as census:
        df = (census["census_data"][organism].obs
              .read(value_filter=value_filter, column_names=columns)
              .concat().to_pandas())
    return df


def cellxgene_get_anndata(
    cell_type=None,
    tissue=None,
    disease=None,
    sex: str | None = None,
    genes: list | None = None,
    organism: str = "homo_sapiens",
    extra_filter: str | None = None,
    census_version: str = "stable",
    max_cells: int = 10_000,
    seed: int = 42,
):
    """Fetch a subsampled AnnData slice (raw counts) from CellxGene Census.

    Samples soma_joinids BEFORE downloading the expression matrix to avoid
    streaming the full matching set. Compatible with the scAnnotAgent QC and
    annotation pipeline (see scAnnotAgent/SKILL.md).

    Parameters
    ----------
    genes : list[str]
        HGNC gene symbols. None → all genes (very large — avoid without genes list).
    max_cells : int
        Subsample cap applied before X download (default 10_000).
    seed : int
        Random seed for reproducible subsampling.

    Returns
    -------
    AnnData  obs × var, X = raw counts (sparse).
    var has feature_name (HGNC) and feature_id (Ensembl).
    """
    import cellxgene_census

    obs_filter = _cellxgene_filter(
        _cellxgene_in("cell_type", cell_type),
        _cellxgene_in("tissue", tissue),
        _cellxgene_in("disease", disease),
        _cellxgene_in("sex", sex),
        extra_filter,
    )
    var_filter = None
    if genes:
        quoted = ", ".join(f"'{g}'" for g in genes)
        var_filter = f"feature_name in [{quoted}]"

    with _cellxgene_open(census_version) as census:
        joinids = (census["census_data"][organism].obs
                   .read(value_filter=obs_filter, column_names=["soma_joinid"])
                   .concat().to_pandas()["soma_joinid"].values)

        if len(joinids) > max_cells:
            rng = np.random.default_rng(seed)
            joinids = rng.choice(joinids, max_cells, replace=False)

        adata = cellxgene_census.get_anndata(
            census=census,
            organism=organism,
            obs_coords=joinids,
            var_value_filter=var_filter,
        )
    return adata


def cellxgene_list_datasets(
    tissue=None,
    disease=None,
    organism: str = "homo_sapiens",
    census_version: str = "stable",
) -> pd.DataFrame:
    """List datasets in the CellxGene Census with optional tissue/disease filters.

    Returns a DataFrame with dataset_id, dataset_title, dataset_cell_count,
    and other collection-level metadata.
    """
    with _cellxgene_open(census_version) as census:
        datasets = census["census_info"]["datasets"].read().concat().to_pandas()

    if tissue:
        ids = cellxgene_query_obs(tissue=tissue, organism=organism,
                                  columns=["dataset_id"],
                                  census_version=census_version)["dataset_id"].unique()
        datasets = datasets[datasets["dataset_id"].isin(ids)]
    if disease:
        ids = cellxgene_query_obs(disease=disease, organism=organism,
                                  columns=["dataset_id"],
                                  census_version=census_version)["dataset_id"].unique()
        datasets = datasets[datasets["dataset_id"].isin(ids)]

    return datasets.reset_index(drop=True)


def infer_ccc(
    adata,
    groupby: str,
    sample_key: str,
    resource_name: str = "consensus",
    expr_prop: float = 0.1,
    n_jobs: int = 1,
    min_cell_types: int = 2,
) -> pd.DataFrame:
    """Infer cell-cell communication (CCC) scores per sample using LIANA rank_aggregate.

    Runs LIANA's ``rank_aggregate`` independently for each sample (donor/condition),
    aggregating L-R interaction scores across all cell type pairs. Returns a
    sample × L-R feature matrix analogous to TF activity from :func:`infer_tf_activity`.

    Parameters
    ----------
    adata : AnnData
        Cells × genes. ``adata.X`` must contain log-normalised expression
        (e.g. log1p(CPM)).  Raw counts will produce incorrect scores.
    groupby : str
        ``adata.obs`` column with cell type labels (e.g. ``'CT_Major'``).
    sample_key : str
        ``adata.obs`` column that identifies individual samples/donors
        (e.g. ``'donor_id'``).
    resource_name : str
        LIANA ligand-receptor database. Default ``'consensus'``
        (aggregated consensus resource).
    expr_prop : float
        Minimum fraction of cells in a cell type that must express the gene
        for it to be considered. Default 0.1.
    n_jobs : int
        Parallel jobs passed to LIANA. Default 1.
    min_cell_types : int
        Skip samples with fewer than this many cell types present. Default 2.

    Returns
    -------
    pd.DataFrame
        Shape (n_samples × n_lr_pairs). Columns are named
        ``source__ligand__target__receptor``. Rows are indexed by sample.
        Missing L-R pairs for a sample are NaN.

    Examples
    --------
    # Major cell types, one score per donor
    ccc_df = infer_ccc(adata, groupby='CT_Major', sample_key='donor_id')

    # Sub cell types with more parallelism
    ccc_df = infer_ccc(adata, groupby='CT_Minor', sample_key='donor_id', n_jobs=8)
    """
    import liana as li
    from tqdm import tqdm

    samples = sorted(adata.obs[sample_key].unique())
    comm_scores: dict[str, pd.Series] = {}

    for sample in tqdm(samples, desc="CCC per sample"):
        adata_s = adata[adata.obs[sample_key] == sample].copy()

        ct_counts = adata_s.obs[groupby].value_counts()
        if (ct_counts == 0).any() or len(ct_counts) < min_cell_types:
            continue

        lr_results = li.mt.rank_aggregate(
            adata_s,
            groupby=groupby,
            resource_name=resource_name,
            n_jobs=n_jobs,
            expr_prop=expr_prop,
            n_perms=None,
            verbose=False,
            use_raw=False,
            inplace=False,
        )

        for _, row in lr_results.iterrows():
            score = row["lrscore"]
            if pd.isna(score):
                continue
            feature = f"{row['source']}__{row['ligand_complex']}__{row['target']}__{row['receptor_complex']}"
            if feature not in comm_scores:
                comm_scores[feature] = pd.Series(index=samples, dtype=float)
            comm_scores[feature].loc[sample] = score

    if not comm_scores:
        return pd.DataFrame(index=samples)

    df = pd.DataFrame(comm_scores)
    df = df.dropna(how="all")
    return df


def cellxgene_get_schema(
    organism: str = "homo_sapiens",
    census_version: str = "stable",
) -> dict:
    """Return valid filter values for cell_type, tissue, disease and all obs column names.

    Use this to discover correct label strings before calling cellxgene_query_obs
    or cellxgene_get_anndata.

    Returns
    -------
    dict with keys: obs_columns, unique_cell_types, unique_tissues, unique_diseases
    """
    with _cellxgene_open(census_version) as census:
        obs = census["census_data"][organism].obs
        columns = obs.schema.names
        sample = (obs.read(column_names=["cell_type", "tissue", "disease"])
                  .concat().to_pandas())
    return {
        "obs_columns":        list(columns),
        "unique_cell_types":  sorted(sample["cell_type"].dropna().unique().tolist()),
        "unique_tissues":     sorted(sample["tissue"].dropna().unique().tolist()),
        "unique_diseases":    sorted(sample["disease"].dropna().unique().tolist()),
    }
