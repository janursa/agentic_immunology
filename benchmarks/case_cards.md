# Cases — `task_interpreter`

Gold rows are the rows an interpretation **must** contain. Extra rows count as over-framing only on
`L0`/`L1` cards. `Test` and `Refuter` are free text in the agent's output and are not scored;
`Additive` is, because it decides whether the run halts.

## A1
**Prompt:** `how many donors are in the abf300 cohort?`
**Task-level:** `L0`
**Table:** none 

## A2
**Prompt:** `plot the donor age distribution in abf300`
**Task-level:** `L0`
**Table:** none 

## A3
**Prompt:** `test whether CD8 TEMRA frequency increases with age in abf300`
**Task-level:** `L2`

| Span | Tag | Candidates | Verdict | Additive |
|---|---|---|---|---|
| "test whether ... increases with age" | `IMPLEMENTATION` | (a) unadjusted; (b) adjusted for sex/batch | `FRAMEABLE` | no |

The refuter selects: the unadjusted branch becomes a sensitivity check, not a half to combine.

## A4
**Prompt:** `characterize compositional changes with age in abf300 and give me the top hits`
**Task-level:** `L3`

| Span | Tag | Candidates | Verdict | Additive |
|---|---|---|---|---|
| "compositional changes with age" | `IMPLEMENTATION` | (a) per-cell-type regression; (b) compositional model (CLR / Dirichlet) | `FRAMEABLE` | no |
| cell annotation resolution | `SCOPE` | (a) coarse lineage; (b) fine-grained subset | `UNFRAMED` | combine |
| "top hits" | `DELIVERABLES` | (a) fixed n; (b) FDR cut-off; (c) effect-size cut-off | `UNFRAMED` | combine |

No `DATA` row (see A2). `L3` that does not halt — every `UNFRAMED` row is additive.

## A5
**Prompt:** `find novel targets for immune aging`
**Task-level:** `L3`

| Span | Tag | Candidates | Verdict | Additive |
|---|---|---|---|---|
| "novel" | `CONCEPT` | (a) unseen in this cohort; (b) absent from the literature; (c) no known drug | `UNFRAMED` | no |
| (implicit) cohort | `DATA` | any datalake cohort with age metadata | `UNFRAMED` | combine |

The `CONCEPT` row is the only halting row. The `DATA` row is combinable (`require replication in
≥2 cohorts`), and no result tells you which cohort was meant — a `FRAMEABLE` verdict there is wrong.

## A6
**Prompt:** `compare stimulated vs unstimulated cells in the unstimulated-only arm of abf300`
**Task-level:** `CLARIFY-NEEDED`
**Table:** none — self-contradiction, reported at step 0. Picking one side of it silently is the
failure mode.

## A7
**Prompt:** `normalize the abf300 counts and rank genes by their association with age`
**Task-level:** `L1`

| Span | Tag | Candidates | Verdict | Additive |
|---|---|---|---|---|
| "normalize" | `IMPLEMENTATION` | (a) CPM; (b) TPM | `CONVERGENT` | — |

A per-gene constant cancels in a within-gene, across-sample ranking. Planning or synthesising
branches that cannot differ is wasted compute.
