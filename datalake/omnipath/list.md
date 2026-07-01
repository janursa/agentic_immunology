# OmniPath -- File List

All files located in `datalake/omnipath/`. Pulled via OmniPath REST API (omnipathdb.org). All files are TSV.

---

## interactions_directed.tsv
**Directed PPI**
Directed post-translational protein interactions (85,217 rows). Columns: source, target, source_genesymbol, target_genesymbol, is_directed, is_stimulation, is_inhibition, consensus_stimulation, consensus_inhibition, sources (contributing DBs), references, curation_effort. Sources include SIGNOR, HPRD, PhosphoSite, ProtMapper, iPTMnet, SPIKE, KEA, and ~15 others.

## enzyme_substrate.tsv
**Kinase-Substrate**
Kinase/enzyme to substrate phosphorylation sites (41,506 rows). Columns: enzyme, enzyme_genesymbol, substrate, substrate_genesymbol, residue_type, residue_offset, modification (phosphorylation 94%, dephosphorylation, acetylation, methylation, etc.), sources, references.

## intercell_annotations.tsv
**Intercellular Roles**
Per-gene intercellular role annotations from multiple databases (388,239 rows). Columns: category, parent, database, genesymbol, entity_type, consensus_score, transmitter, receiver, secreted, plasma_membrane_transmembrane. Useful for classifying signaling nodes as receptors, ligands, etc.

## intercell.tsv
**Intercell Summary**
Compact intercellular annotation table (9 rows). Subset or summary of intercell_annotations.tsv.

## ligrec_interactions.tsv
**Ligand-Receptor**
Ligand-receptor interaction pairs (6,890 rows). Columns: source, target, source_genesymbol, target_genesymbol, is_directed, is_stimulation, is_inhibition, consensus_direction, and others. Use to identify upstream ligand-receptor pairs driving signaling.

## dorothea_tf_regulon.tsv
**TF Regulons**
DoRothEA TF to target gene regulons (15,267 rows). Directed, with is_stimulation/is_inhibition flags.
