# Disease & Aging Implication — Reference

Framework and methodology for assessing whether a gene/feature is causally implicated in a disease or aging phenotype, and evaluating its safety/tractability. Used by the `data_analyst_agent` when running disease implication tasks.

---

## Conceptual Framework

**Open Targets evidence model** (Ochoa et al. 2021, *Nucleic Acids Research*; Mountjoy et al. 2021, L2G). No single evidence type proves causality — each has a different confounding profile (genetic association is least confounded by reverse causation; expression can be a disease *consequence*; animal models don't always translate; literature is citation-biased). Confidence comes from **independent pillars agreeing**, because unrelated biases are unlikely to align by chance. Genetic evidence is weighted first; a finding backed by genetics + expression + a functional screen is far stronger than any single pillar alone.

**AstraZeneca's "5R" framework** (Cook et al. 2014, *Nature Reviews Drug Discovery*). Right target / right tissue / right safety / right patient / right commercial potential. Programs with strong prior **genetic evidence** tying the target to the disease had measurably higher clinical success rates — genetic support is empirically predictive of success. This is why causal evidence and safety/tractability must be assessed as **two separate axes**, not folded into one score.

**López-Otín et al. 2023 (*Cell*), "Hallmarks of Aging"**. For aging specifically, a feature must clear a stricter 3-part bar to be called a causal driver (not just an aging-associated marker):
1. It changes progressively with aging — correlative; necessary but not sufficient.
2. **Aggravating** it experimentally accelerates aging phenotypes.
3. **Suppressing/reversing** it experimentally extends healthy lifespan or reverses aging phenotypes.

Most omics pipelines (including this platform's) only satisfy leg 1. **Always state explicitly which leg(s) of this bar the evidence clears — do not conflate "aging-associated" with "aging-causal."**

---

## The 8 Evidence Pillars

Work through the pillars relevant to the task. Not every pillar applies to every task — state which ones you used and why, and **explicitly name pillars you skipped or that have no supporting tool**, rather than implying coverage you don't have.

1. **Genetic causal evidence**
   - Primarily use Open Targets for all steps.
   - Tools: `phewas_opengwas`, `query_gwas_catalog`, `query_opentarget_platform`, `get_disease_credible_sets`, `run_coloc`, `run_mr` (see `knowhow/genetics.md` for image selection and usage).

2. **Expression / multi-omics evidence**
   - Differential expression, cell-type-resolved association (see `knowhow/omics.md`).
   - Pathway/network context: `get_immune_grn`, `infer_grn_spearman`, `infer_tf_activity` (`tools/ciim/genomics.md`).

3. **Functional / perturbation evidence**
   - CRISPR-based: `analyze_crispr_genome_editing`, `analyze_cas9_mutation_outcomes` (`tools/biomni/genetics_biomni.md`).
   - Check available perturbation data in the datalake; apply omics knowhow for perturbation expression analysis.

4. **Literature / prior-evidence pillar**
   - Novelty and concordance check against published evidence: use `WebSearch`/`WebFetch` directly (PubMed, arXiv, Scholar). This is a targeted grounding check — a handful of queries to confirm concordance or flag contradiction, not a systematic review.

5. **Aging-specific causal bar**
   - Apply the López-Otín 3-part test explicitly. Leg 1 (progressive change) can be supported by `predict_immune_age_grn_clock` / `retrieve_summary_stats` (`tools/ciim/hiara.md`).
   - *Gap*: legs 2 and 3 (experimental aggravation/suppression) have no supporting tool on this platform. State plainly that aging-associated ≠ aging-causal when only leg 1 is covered.

6. **Statistical rigor / pitfalls**
   - MR: horizontal pleiotropy (MR-Egger intercept), weak instruments, winner's curse.
   - Multi-omics: multiple-testing correction across layers, population stratification, reverse causation.

7. **Safety & tractability**
   - Tissue specificity, druggability/tractability, target-family membership.
   - Essentiality, paralog redundancy.

8. **Evidence integration**
   - Combine all pillars into a single graded confidence statement per claim (Open Targets-style: agreement across independent pillars raises confidence; a single pillar alone does not).
   - The detailed report must include results from all layers assessed.

---

## Workflow

1. **Select** — identify which of the 8 pillars apply, the relevant tools, data-lake entries, and identifiers (gene symbols, rsIDs, EFO IDs).
2. **Code / run** — run genetics and omics pillars directly (using `knowhow/genetics.md` and `knowhow/omics.md`); for literature synthesis (pillar 4), use `WebSearch`/`WebFetch` directly (PubMed, arXiv, Scholar) as a targeted grounding check.
3. **Execute & observe** — run scripts, read stdout/errors, iterate.
4. **Integrate** — bring per-pillar results together (pillar 8): state which pillars agree, which are silent, and which are gaps. No single pillar result stands as the overall verdict.
5. **Report** — return key findings per pillar, the integrated confidence call, explicitly named gaps, and **absolute paths** of every output file.
