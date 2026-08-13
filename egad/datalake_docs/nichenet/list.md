# NicheNet -- File List

All files located in `${CIIM_DATALAKE_DIR}/nichenet/`. Downloaded from Zenodo (doi:10.5281/zenodo.7074291).

**Reference**: Browaeys et al. 2020, *Nature Methods* (doi:10.1038/s41592-019-0667-5)  
**Version**: NicheNet v2 prior model (December 2021 networks + NSGA2R-optimised weights)  
**Scope**: General-purpose cell-cell communication tool — **not immune-specific**. Cell-type context is supplied by the user's own scRNA-seq data.  
**Format**: Parquet files (converted from original R `.rds`, which have been removed).

---

## Core Network Files
**Core Networks**

### lr_network_human.parquet
**Ligand-Receptor Network**  
4,986 ligand-receptor pairs. Columns: `from` (ligand), `to` (receptor), `database`, `source`. Source databases include CellChat, CellPhoneDB, ICELLNET, NicheNet v1, connectomeDB2020, and others. This is the entry layer of the NicheNet prior: the set of all possible extracellular L-R interactions.

### signaling_network_human.parquet
**Intracellular Signaling Network**  
5,169,518 directed edges. Columns: `from`, `to`, `source`, `database`. Represents the intracellular signaling paths that connect receptor activation to downstream molecules and TFs. Sources include OmniPath, Reactome, KEGG, PhosphoSitePlus, SIGNOR, and others. This is the middle layer: receptor → signaling cascade.

### gr_network_human.parquet
**Gene Regulatory Network**  
5,870,450 directed TF→target edges. Columns: `from` (TF), `to` (target gene), `source`, `database`. Represents the transcriptional regulation layer. Sources include DoRothEA, TRRUST, RegNetwork, ENCODE, and ChIP-Atlas. This is the final layer: TF → target gene expression.

---

## Weighted / Integrated Files
**Weighted Networks**

### weighted_networks_lr_sig.parquet + weighted_networks_gr.parquet
**Weighted Prior Network**  
The NicheNet prior model after empirical calibration. Edges from the signaling and GR networks are weighted by how well they predict observed gene expression changes in ~600 published perturbation experiments. Two tables:
- `weighted_networks_lr_sig.parquet`: 3,923,501 weighted L-R + signaling edges (`from`, `to`, `weight`)
- `weighted_networks_gr.parquet`: 4,640,268 weighted GR edges (`from`, `to`, `weight`)

### ligand_tf_matrix.parquet
**Ligand → TF Weight Matrix**  
33,354 ligands × 1,226 TFs. Each value = how strongly a ligand is predicted to regulate a given TF, based on path traversal through the weighted prior network. Rows = ligands (with a `ligand` column added), columns = TF names. Use to identify which ligands most likely drive observed TF activity changes.

### ligand_target_matrix_long.parquet
**Ligand → Target Gene Weight Matrix (long format)**  
34,326,358 rows. Columns: `ligand`, `target`, `weight`. Originally a 33,354 × 1,226 dense matrix, converted to long format (non-zero weights only) for efficient storage (353MB parquet vs. 250MB RDS). Each row = predicted regulatory influence of a ligand on a target gene. This is the primary output used in NicheNet ligand activity analysis.
