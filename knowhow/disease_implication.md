# Disease & Aging Implication — Reference

Framework and methodology for assessing whether a gene/feature is implicated in a disease or aging phenotype, and evaluating its safety/tractability. 

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

## The Evidence Pillars

Work through the pillars relevant to the task. 

1. **Genetic evidence** 
2. **Omics evidence**
**CRITICAL**: your analysis should not be just DE gene expression. Use these:
    - Cell type composition analysis -> often a disease causes a shift in cell type composition. Identifying it and finding genes/markers responsible for that could land you in causal factors.
    - CCC -> often disease impairs CCC. Identifying these and evaluating them as targets could give a better insight than downstream DE gene expression
3. **Functional / perturbation evidence**
4. **Literature / prior-evidence pillar**
5. **Safety & tractability**

## Workflow

1. **Select** — identify which of the pillars apply. Use data available both local and accessibile online.
2. **Code / run** — run genetics and omics pillars directly (using `knowhow/genetics.md` and `knowhow/omics.md`); for literature synthesis, use `WebSearch`/`WebFetch` directly (PubMed, arXiv, Scholar) as a targeted grounding check. Use `safity_druggibility` knowhow. 
3. **Execute & observe** — run scripts, read stdout/errors, iterate.
4. **Integrate** — bring per-pillar results together
5. **Prioritization** - all candidates that have evidence in genetic or omics layer as well as do not pose critical safity/tractibility issues should be retained. From there, rank them based on line of evidence, strength of implications, druggibility, etc. At this point, for complex problems, before subsetting to a smaller set, consult the user. 


## Tips
- Have a multiomics analysis approach. Do not limit yourself to only RNA. If you dont have local data, look for online resources.
