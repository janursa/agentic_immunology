# Guardrails


- **Statistical power**: before designing a statistical experiment, always check the sample size *and the full distribution of the variable defining the comparison/contrast* (not just total N or its range) to check if the test is sufficiently powered. A cohort can have a large N and a wide-looking range yet be skewed (e.g. mostly senior donors) and unusable for the intended contrast (e.g. young-vs-old) — consider the distribution, don't infer adequacy from N or range alone.

- **Statistical rigor — discovery/replication split**: when a design's central claim rests on convergence across cohorts/datasets (e.g. "N of M cohorts significant"), reserve at least one eligible cohort as a held-out replication set, chosen *before* running discovery — not folded into the same meta-analysis. Report discovery-set and replication-set results separately; convergence pooled into one meta-analysis is not replication and must not be described as such. If too few cohorts exist to split, state this as an explicit design limitation rather than treating full-pool meta-analysis as if it satisfies replication.

- **Statistical rigor — multi-stage selection inflation (winner's curse)**: per-round FDR/p-value control (e.g. discovery FDR<0.05, then a causal-gate p<0.05) is only valid for the tests run within that round — it does not compose into a pipeline-wide error rate across sequential filters. A candidate that survives discovery is already a biased subsample; a downstream test run only on survivors is not independent confirmation of it, and its effect size is inflated (winner's curse). Flag designs/analyses where every confirmatory stage is run exclusively on the prior stage's survivors with no independent data — prefer independent/held-out data at each confirmatory stage (see discovery/replication split above), or state pillar/check counts as hypothesis-generating rather than implying a calibrated global significance level.

- **Confounders** -- always consider confounding factors in the main effect size and design your analysis to account for them. Do not account for factors such as sex, ansestry, etc when there is not enough samples or is not the point of the analysis to provide sex, ancestry-resolved analysis.

- **Granularity/modality/condition compatibility** — before combining results from different analysis, confirm they're at comparable groups (e.g. bulk vs. cell-type-resolved, disease/healthy group, control versus stimulated). If mismatched, do not pool them as equivalent evidence: either harmonize resolution (e.g. aggregate the finer dataset to match) or keep them as separate, non-pooled evidence tiers (e.g. one as discovery, the other as an orthogonal/functional layer at its native resolution). Also consider if the measurements are at control or stimulated (e.g. LPS) as they are different.

- **Multi-cohort conclusions → per-cohort + meta-analysis, not pooling.**
  Run analysis per cohort, then combine — don't pool into one regression
  with cohort as covariate (hides heterogeneity).
  - **Default:** inverse-variance-weighted meta-analysis on β/SE per cohort
    (e.g. `metafor`), not p-value combination. Preserves effect size + gives a CI.
    - Fixed-effect: only if cohorts are near-replicates. Check with I²/Q first.
    - Random-effects (DerSimonian-Laird/REML): default when n varies a lot
      (e.g. 900 vs 60) or cohorts differ in population/platform — prevents
      one big cohort from steamrolling the rest.
  - **Only if β/SE unavailable** (p-values only, mixed test types): Stouffer
    with signed z (`sign(β)·Φ⁻¹(1−p/2)`), not Fisher's — Fisher is
    direction-blind and dominated by any single tiny p-value.
    - Unweighted Stouffer = noisy small cohort counts as much as precise large one.
    - √n-weighted Stouffer ≈ inverse-variance, but reintroduces large-cohort dominance.
  - **Sanity check only:** vote-counting (≥k of m cohorts, same direction) — low power, use as secondary evidence.

- **Prefer simpler models over complex statitical models.** Reach for complex models only when the simpler approach (e.g. per-cohort analysis, plain linear/logistic regression) demonstrably fails to address the structure in the data. Keep the number of covariates low — fewer covariates keeps the biological signal interpretable.

- **Prefer simple statistical approaches over advanced ML models.** Default to standard statistical tests/regression; escalate to ML only when the simpler approach is shown to be insufficient for the question.

- **Prefer data-driven approaches over ML predictions.** When a direct measurement or association from the data is available, prefer it over a model-predicted/imputed value.

- **Aging clocks** - do not use transcriptomics aging clocks for marker discovery. Only for perturbation screening.

- **Method choice** - do not limit yourself to basic approaches such as DE analysis. When applicable use more advanced approaches such as CCC, GRN, cell type compositional analysis.

- **Approach choice** - when applicable, the analysis should include:
    1. **Genetic evidence** 
    2. **Omics evidence**
    3. **Functional / perturbation evidence**
    4. **Literature / prior-evidence pillar**
    5. **Safety & tractability**
    for genetic analysis, prioritize Open Target's resources such as gene to disease, lucus to gene, coloc evidence for initial analysis and only use color and MR later in the analysis -> when the markers are prioritized

    These are independent evidence axes, not a sequential filter — do not restrict one pillar's search space (e.g. omics DE) to candidates surfaced by another (e.g. literature).
    
- **Data accountability.** For every pillar in the design, name which data resources (both public/external and integrated) were considered and state explicitly either "checked — used, see Round X" or "checked — excluded, because Y." 

- **Design scope: what to gather, not how to analyze it.** A design specifies evidence tiers,
  data sources, and pass/fail gating thresholds. It should not lock in a specific statistical
  method/package/function (that's the executing analyst's call, made against the real data) —
  flag it as a REVISE-DESIGN issue if a plan hard-codes an implementation detail instead of a requirement.

- **No pre-assigned evidence weights.** A design should not fix numeric weights across evidence
  pillars (e.g. "omics 30%, genetics 25%") before any evidence exists — that's a formula guessed
  in advance, not a synthesis. Final-round criteria should instead require the executing agent to
  reason over the collected evidence and either prioritize a candidate with a stated, checkable
  justification (e.g. "supported by 2 of 3 independent pillars") or state explicitly how to
  expand the analysis if the evidence doesn't support prioritization. 
- **Mechanistic leads** does the design references mechanistic leads from the literature and whether it's incorporated in the study design.