# Statistics 


---

## Guidelines


- **Confounders** -- always consider confounding factors in the main effect size and design your analysis to account for them. Do not account for factors such as sex, ansestry, etc when there is not enough samples or is not the point of the analysis to provide sex, ancestry-resolved analysis.

- **Multi-cohort conclusions → per-cohort analysis + meta-analysis, not pooling.** If a claim is meant to hold across multiple cohorts, run the analysis separately within each cohort, then combine the per-cohort effect estimates with a meta-analysis (e.g. fixed/random-effects model). Avoid pooling cohorts into one regression with cohort as a covariate as the default — per-cohort + meta-analysis surfaces heterogeneity that a pooled model can hide.

- **Prefer simpler models over mixed-effects models.** Reach for mixed-effects models only when the simpler approach (e.g. per-cohort analysis, plain linear/logistic regression) demonstrably fails to address the structure in the data. Keep the number of covariates low — fewer covariates keeps the biological signal interpretable.

- **Prefer simple statistical approaches over advanced ML models.** Default to standard statistical tests/regression; escalate to ML only when the simpler approach is shown to be insufficient for the question.

- **Prefer data-driven approaches over ML predictions.** When a direct measurement or association from the data is available, prefer it over a model-predicted/imputed value.

- **CRITICAL**: before designing a statistical experiment, always check the sample size *and the full distribution of the variable defining the comparison/contrast* (not just total N or its range) to check if the test is sufficiently powered. A cohort can have a large N and a wide-looking range yet be skewed (e.g. mostly senior donors) and unusable for the intended contrast (e.g. young-vs-old) — plot or tabulate the distribution, don't infer adequacy from N or range alone.

- **Granularity/modality compatibility** — before combining or meta-analyzing datasets, confirm they're at comparable resolution (e.g. bulk vs. cell-type-resolved, single-omic vs. multi-omic). If mismatched, do not pool them as equivalent evidence: either harmonize resolution (e.g. aggregate the finer dataset to match) or keep them as separate, non-pooled evidence tiers (e.g. one as discovery, the other as an orthogonal/functional layer at its native resolution).

- do not use aging clocks for marker discovery. Only for perturbation screening.


