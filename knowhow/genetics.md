# Genetics Analysis — Reference

Reference for genetic analyses in the platform: tools, images, hard rules, and workflow.

---

## Tools

- [`tools/ciim/genetics.md`](../tools/ciim/genetics.md) — `phewas_opengwas`, `query_gwas_catalog`, `query_opentarget_platform`, `get_disease_credible_sets`, `run_coloc`, `run_mr`.
- [`tools/biomni/genetics_biomni.md`](../tools/biomni/genetics_biomni.md) — liftover, fine-mapping, CRISPR analysis, TF binding site identification, phylogenetics.
- [`tools/biomni/pharmacology_biomni.md`](../tools/biomni/pharmacology_biomni.md) — `retrieve_topk_repurposing_drugs_from_disease_txgnn`, `query_drug_interactions`, `find_alternative_drugs_ddinter`, FDA adverse-event/label/recall tools.

Always prefer these existing tools over reimplementing methods yourself.

---

## Image Selection

- `biomni_full.sif` (default) — for `genetics_biomni`, `pharmacology_biomni`, and direct-API CIIM genetics functions (`phewas_opengwas`, `query_gwas_catalog`, `query_opentarget_platform`, `get_disease_credible_sets`).
- `genotype.sif` (`agentic_immunology/singularity/genotype.sif`) — required for `run_coloc` and `run_mr` (R 4.5, coloc, susieR, plink).

See [`images.md`](../images.md) for the exec command and hard rules.

> ⛔ Additional rule for `run_mr` in `opengwas` mode: the OpenGWAS JWT token must be in `agentic_immunology/.env` as `OPENGWAS_TOKEN=<jwt>`. If missing/expired → report and stop (or use `exposure_file`/`outcome_file` if pre-fetched files are available).

---

## Workflow

1. **Select** — identify the relevant tool functions, data-lake entries (e.g. DICE eQTLs, GWAS catalog), and identifiers (gene symbols, rsIDs, EFO IDs).
2. **Code** — write a self-contained `code/script.py` to `temp/{task}/code/`. Must run start-to-finish inside the singularity image with no manual steps.
3. **Execute & observe** — run it, read stdout/errors, iterate. If something fails, revise and rerun.
4. **Report** — return key findings (grounded in tool outputs) and **absolute paths** of every output file.

## Grounding
Ground every claim in data and tool outputs — e.g. "{statement}, obtained from run_coloc PP.H4 and GWAS catalog data." Report failures and skipped steps faithfully.

## Tips
- Prioritize Open Target's resources such as gene to disease, lucus to gene, coloc evidence for initial analysis and only use color and MR later in the analysis -> when the markers are prioritized