# EGAD-Interpretation: prior art, substrates, and benchmark design

Scope: benchmarking (and improving) how LLMs interpret open-ended scientific prompts — the
`task_interpreter` problem. Openness table → typed sources of openness → verdict → `TASK-LEVEL`.

Status: literature scan of 2026-08-20. arXiv IDs below come from search results and the two local
PDFs (`literature/kirgis.pdf`, `literature/ambig_ds.pdf`); IDs not read in full are marked `[unread]`.

---

## 1. Prior art — what could undermine this

### 1.1 Direct collision: Ambig-DS (read in full)

**Stoisser et al., Novo Nordisk. "Ambig-DS: A Benchmark for Task-Framing Ambiguity in Data-Science
Agents." arXiv 2605.09698.**

This is the closest existing work and the main scoop risk. It already owns:

- The framing: agents "silently commit to plausible but unintended task framings, producing clean,
  executable artifacts" — *unflagged misframing*. Same failure mode EGAD's interpreter exists to prevent.
- The formalism: observation `o = (p, d)`, framing `θ`, candidate set `C(o)`, ambiguous iff `|C(o)| > 1`,
  well-calibrated agent = "ask iff `|C(o)| > 1`". This is a cleaner statement of what `interpretation.md`
  does per row.
- The construction: pair each fully-specified task with a minimally-edited ambiguous variant, keep the
  original evaluator. 51 tasks on DSBench (target ambiguity) + 61 on MLE-bench (objective ambiguity).
- A four-item verification checklist (plausible alternatives, ambiguity preservation, decision relevance,
  task preservation) — essentially the calibration criterion in `task_interpreter.md` step 1.
- The headline results: 39–63% wrong-target commitment, flagged in *none*; one clarifying question
  recovers most of the loss; agents cannot calibrate *when* to ask (permissive prompts → over-asking on
  clear tasks, conservative → silent defaulting).

**What it does not do — the gap that is still open:**

| Ambig-DS | EGAD-Interpretation |
|---|---|
| Binary: ambiguous or not | Graded: L0–L3, ordinal |
| Two framing variables (`T` target, `M` metric) — explicitly "other framing variables … left to future work" | Five typed sources (`CONCEPT`, `DATA`, `SCOPE`, `IMPLEMENTATION`, `DELIVERABLES`), multiple rows per prompt |
| One response type: ask or commit | Three verdicts (CONVERGENT / FRAMEABLE / UNFRAMED) crossed with additive-or-not — asking the user is one cell of that grid |
| Supervised learning with a protocol-convention `θ*` | Open-ended discovery; no hidden right answer exists |
| Scored by the source benchmark's evaluator | Must be scored against an expert-annotated openness table |
| Tabular/Kaggle | Biomedical, multi-omic, real datalake |

Their own Limitations section names the axes they left out (information boundaries, temporal
assumptions, "richer naturalistic ambiguity"). That paragraph is the opening. Cite it as the thing being
extended, not competed with.

The single most important distinction to hammer: **Ambig-DS collapses every underdetermined prompt to
"you should have asked."** In real scientific work most openness is *not* a question for the user — it is
either resolvable by evidence (FRAMEABLE) or should be run both ways (additive). A benchmark that
rewards asking is measuring the wrong thing for science. That is the contribution.

### 1.2 Secondary collisions

**"Ask Early, Ask Late, Ask Right" — Gulati et al. 2026** (`literature/Gulati_2026_askEarlyAskLateAskRight.md`)

Measures *when* clarification pays, not whether the agent recognises it is needed — they say so
explicitly: "this study establishes the demand side … but does not address the supply side: making
agents recognize ambiguity and ask at the right moment." Forced-injection: take an underspecified
task, inject the ground-truth missing information at 10/30/50/70/90% of the trajectory, compare
pass@3 against oracle and no-clarification. 84 variants × 3 trials × 3–4 models = 6,000+ runs on
MCP-Atlas, TheAgentCompany, SWE-Bench Pro. Headline: goal clarification is worthless after ~10% of
execution; input survives to ~50%; no frontier model asks inside the optimal window (GPT-5.2 asks in
52% of sessions at mean 43% depth, Gemini 3 Flash never asks).

Their four *information dimensions* — goal, input, constraint, context — come from LHAW and are the
nearest thing to our tags. Mapping:

| LHAW dimension | EGAD tags |
|---|---|
| goal (unclear deliverable) | `deliverables`, part of `concept` |
| input (unspecified data source) | `data`, `modality` |
| constraint (missing rules/thresholds) | part of `method-path` |
| context (absent domain knowledge) | — (not openness; it is missing knowledge, and EGAD resolves it from knowhow) |
| — | `scope`, `granularity`, most of `method-path` have no LHAW analogue |

So it is *not* a lower-resolution version of our tags — it is a different cut. Their dimensions
describe **what information is missing from the instruction**; ours describe **what the sentence could
mean given the data**. `scope` and `granularity` — the two that dominate biomedical prompts — are
absent from LHAW entirely. Their variant set also carries an ambiguity class per variant
(outcome-critical / divergent / benign), which is a three-way proto-verdict; ours is four-way and
names the *resolver* rather than the *severity*. Cite as the strongest evidence that framing errors
are unrecoverable once execution starts — which is exactly why interpretation must be a separate,
inspectable, pre-execution artifact.

**"Knowing but Not Showing" — Su et al. 2026** (`literature/Su_2026_knowingButNotShowing.md`)

No new benchmark: they reuse **AmbigQA** (Min et al. 2020) — 1,000 sampled items, 425 unambiguous /
575 ambiguous, the ambiguous ones expanding into 2,460 disambiguated sub-questions (~4.3 each). Three
settings on the same items: QA accuracy, explicit binary ambiguity judgment, and behavioural
classification of the QA response (direct answer / clarifying question / refusal) by a judge model.
Two findings that matter for us:

1. **Recognition ≠ behaviour.** Models score 60–80% on the ambiguous class when *asked to judge*
   ambiguity, but in the QA setting 80–95% of responses are "only answered" — clarification rates
   under 5% even for Claude. This kills the "models cannot detect openness" premise. The open problem
   is not detection; it is producing a structured commitment about the openness. EGAD's contribution
   is that artifact.
2. **Scope is the tag models miss.** Mapping model explanations onto their six-type taxonomy
   (Temporal, Identity, Version, Scope, Semantic, Locale), models over-assign Identity/Version and
   **strongly under-assign Scope**, which is where humans concentrate. Directly predicts which EGAD
   tag will have the worst recall. Pre-register that.

Also: retrieved context *suppresses* clarification — it reads as a cue that the question is answerable.
Warning for us, since EGAD's interpreter sees a datalake description before it writes the table.

**CLAMBER** (`literature/CLAMBER.md`) — ACL 2024, ~12K items (7,167 unambiguous), 3,600-item balanced
test set. Answer to the `#TODO`: it is a *taxonomy plus data*, not just 12K questions, but the taxonomy
is for information-retrieval queries, not analyses. Three dimensions / eight categories: Epistemic
Misalignment (Unfamiliar, Contradiction), Linguistic Ambiguity (Lexical, Semantic), Aleatoric Output
(Whom, Where, When, What). Only two of the eight map onto our vocabulary — Lexical/Semantic → `concept`,
Where/When/What → a coarse `scope`. Nothing in it touches `method-path`, `granularity`, `modality`, or
`deliverables`, because a retrieval query has no analysis to underdetermine. **One category is worth
importing**: *Contradiction* — the prompt conflicts with itself or with what is known. That is not
openness (two readings) but incoherence (zero valid readings), and EGAD currently has no state for it;
today the interpreter would silently pick a reading. Add it as a verdict-level escape, not a tag.
Their negative result is also useful cover: CoT and few-shot barely help and *increase* overconfidence
(ECE +16.7 for Llama2-13B), best model 54% accuracy — prompting alone does not solve this, which
motivates a protocol.

**FirstResearch** (2607.05682) — withdrawn. Drop.

**"Many AI analysts, one dataset" — Bertran, Fogliato & Wu, PNAS 2026** (`literature/manyAIanalysistOneDataset.md`)

~5,000 autonomous analyst runs (3 datasets × 4 LLMs × 5 personas), 3,303 passing an LLM auditor, on
tasks where the hypothesis *and* the primary estimand are fixed in advance. Even so, compliant runs
disagree on the **sign** of the effect (anes-views), and the disagreement traces to enumerable
choices: covariate count, regression method, SE estimator, temporal pooling. Personas steer the
conclusion by 34–66 pp.

Three consequences:
- **Do not sell run-to-run variance as a headline.** Published, in PNAS, at 5,000-run scale.
- This is the empirical justification for **ADDITIVE** existing at all: they fix the estimand precisely
  to remove `deliverables` openness, and `method-path` openness alone still produces a multiverse.
- Their closing proposal — "deploying AI analysts against a published specification can reveal how much
  disagreement stems from underspecified design choices" — is the *measurement* version of what EGAD
  does *prospectively*. Frame EGAD as declaring the multiverse before running it rather than mapping it
  afterwards.

**Level taxonomies** — answer to the `#TODO`: they are all autonomy ladders, none grades the prompt.
- *AutoResearch* (`literature/autoResearch.md`) L0–L4 = how control, execution and validation authority
  shift **between human and AI** (L0 Human Only → L2 Human-Verified/AI-Executed → L4 AI-Autonomous).
  A property of the *system*, invariant to the prompt.
- *Act As a Real Researcher / AARRI-Bench* (`literature/actAsARealResearcher.md`) S1–S4
  (Adaptation 32% / Integration 28% / Innovation 27% / Open-ended 13%) = how much **intellectual
  contribution the agent must supply**. Closer to ours — S4 "ambiguous problems requiring deep insight"
  overlaps L2/L3 — but it grades the *task's difficulty for an agent*, bundling openness with technical
  depth and horizon length, and it is assigned holistically with no decomposition or evidence.

Neither definition is reusable. Keep L0–L3, state in the first method paragraph that it grades the
prompt, and cite AARRI's S1–S4 as the nearest ladder to show the axes are orthogonal: an S1 task
(follow instructions, standard tools) can be L3 if the instruction leaves the objective to the user,
and an S4 task can be L1 if the goal is pinned and only the path is open.

### 1.3 Verdict

Not scooped, but the room is narrower than it was six months ago. The defensible claim is:

> Openness in scientific prompts is **typed and graded**, not binary, and the right response depends on
> the type: evidence resolves some, aggregation absorbs others, and only a minority are the user's call.
> Existing ambiguity benchmarks measure a single ask/act decision and therefore cannot distinguish an
> agent that is well-calibrated from one that asks about everything.

Everything in the design below should serve that sentence.

---

## 2. Benchmarks usable as substrate

### 2.0 Start here — three resources, in order

Everything else in this section is background. These three are the ones to actually pull, and they
answer three different questions.

**(1) LHAW / Gulati et al.'s 84 stratified variants — *does our tag vocabulary hold up?***

The only existing resource with **span-level ground truth for what was removed** from a prompt
(`removed_segments`), a per-variant type label (goal / input / constraint / context), and a severity
class (outcome-critical / divergent / benign). Re-annotate the 84 variants with 7 tags + 4 verdicts.

Three results fall out of one annotation pass, before any model is run:
- Coverage — what fraction of their variants our tags cover, and how many need a `TAG-MISS`.
- Refinement — whether one LHAW dimension splits into several EGAD tags (expected: `input` →
  `data` + `modality`; `constraint` → several `method-path` rows).
- Whether `scope` and `granularity` are genuinely absent from their set, which is the argument that
  agent benchmarks under-represent the openness that dominates science.

Cheap, fast, no compute. Do this first — it is the empirical validation of the vocabulary and it
either supports the design or forces a revision before 120 cards are written.

**(2) Ambig-DS's paired tasks — *negative controls and the over-asking comparison***

51 + 61 tasks, each shipped as a matched pair (fully specified `Full`, minimally edited `Ambig.`)
with the source evaluator preserved. Two uses:
- **L0/L1 controls, for free.** Their `Full` condition is a verified single-framing prompt. An
  interpreter that opens rows on `Full` items is over-framing, measured against their construction
  rather than our own annotation — an independent check on §4.4's over-framing metric.
- **The direct comparison.** They report the permissive-vs-conservative dilemma: permissive prompts
  over-ask on clear tasks, conservative ones silently default (GPT-5.4 silently defaults on 100% of
  ambiguous metric runs under the conservative policy). Running the four EGAD arms on the same items
  tests whether typing the openness escapes that trade-off, on their data, scored by their evaluator.
  This is the single strongest head-to-head available.

Caveat: tabular/Kaggle, only two framing variables. Do not use it as the main benchmark — use it as
the control set and the comparison point.

**(3) Many-analysts decision codebooks — *ground truth for ADDITIVE***

For each of three tasks (soccer/Silberzahn, metr-rct, anes-views) they extracted structured analytic
decisions from ~3,303 audited runs with a per-dataset codebook. That distribution *is* an empirically
measured openness table for a fixed prompt with a fixed estimand: which `method-path` and
`granularity` choices real agents actually take, and which of them flip the conclusion.

Scoring becomes objective without human annotation: give the interpreter the same
hypothesis + estimand + dataset, and score its enumerated candidate resolutions against the observed
distribution. Precision = candidates that appear in the run distribution; recall = high-frequency or
sign-flipping decisions it failed to enumerate. A candidate that flips the sign and was not enumerated
is a hard miss. This is the only place we get ADDITIVE ground truth that is not our own opinion.

**Not on this list, and why.** Kirgis — a method (shadow evaluation, §2.2), not a dataset; n=2.
AARRI-Bench — 82 Harbor-containerised tasks, graded 0/1 on execution; openness is not annotated and
the harness cost is high. CLAMBER / AmbigQA — retrieval-query ambiguity; useful as taxonomy prior art
and for the `scope`-under-assignment prediction, not as substrate. AutoResearch — a survey.

None of the three is biomedical. Domain match comes from BixBench and from shadow interpretation
(§2.2) — keep both in the plan, but they need annotation work that (1)–(3) do not.

### 2.1 Wider landscape

Kirgis et al. (CRUX, "Can AI agents conduct research? Early evidence from two case studies",
2026-08-10, local PDF) surveys the field in Appendix D. Their own taxonomy is the useful part:
*verifiable tasks* / *LLM-graded open-ended* / *human peer review*.

**Not usable as-is** — fully specified by construction, which is exactly what they are for:
MLAgentBench, MLE-bench, RE-Bench, MLGym, MLRC-Bench, AIRS-Bench, MLS-Bench, PostTrainBench,
ResearchGym.

**Usable — expert rubrics attached, so the Ambig-DS pairing trick works:**

| Substrate | Why | Use |
|---|---|---|
| **LifeSciBench** (OpenAI, Jun 2026; 750 tasks, 173 scientists, 19,020 rubric criteria, 7 workflows × 7 domains) | Best available expert-authored *life-science* prompt bank with per-task rubrics. Rubrics let you score a downstream run after ablating a framing variable, without writing your own evaluator. | Primary source of realistic prompts for controlled openness ablation |
| **BixBench** (2503.00096; 53 real bioinformatics scenarios, 296 open-answer questions; ~17% open-answer accuracy) | Closest domain match to EGAD. Real data, real notebooks, large headroom. | Domain-matched prompts + optional execution subset |
| **BLADE** (Gu et al. 2024) | Built around *analysis-decision multiplicity* on the same research question — the empirical instantiation of ADDITIVE. | Gold source for `method-path` / `granularity` rows |
| **DiscoveryBench** (Majumder et al. 2025), **ScienceAgentBench** (Chen et al. 2025) | Data-driven discovery with fixed goals; good L1 material. | L1 controls |
| **PaperBench** (Starace et al. 2025) | Author-written hierarchical rubrics, LLM judge, human baseline. | Methodological template for rubric-based grading |
| **MLR-Bench**, **AI-Researcher/Scientist-Bench** | Staged research generation with LLM-review rubrics. | L2/L3 prompts outside biology, for generality |
| **DeepResearch Bench II** (2601.08536), **LiveResearchBench** (2510.14240), **"One Interaction Is Worth a Thousand Guesses"** (2601.06676) | Report-level rubric evaluation and *interactive* deep research. The last one is the deep-research analogue of the ask-calibration question. | Metric design; related work `[unread]` |

### 2.2 Shadow interpretation

**Kirgis's own method is worth stealing.** *Shadow evaluation* = give the agent the central research
question of an unpublished paper, have the original authors grade the output. Adapted to interpretation:

> **Shadow interpretation.** Take a published paper. Give the agent the paper's central question as the
> prompt. The paper's Methods section *is* the authors' resolution of every source of openness — which
> cohort, which contrast, which unit of analysis, which model, which covariates. Score the agent's
> openness table against those decisions.

This gives expert-grade ground truth for free, at scale, in EGAD's own domain, and it reuses the existing
`curate_paper` → CASE-CARD machinery. Recommend it as a whole benchmark track. Its weakness —
contamination for published papers — is the usual one; mitigate with recent papers and by scoring
*enumeration of alternatives*, not recovery of the authors' choice.

Also note Kirgis's five failure modes; two are interpretation failures in disguise ("poor judgment about
the bar for publishable research", "uncreative responses to shortcomings in the research design"). Useful
motivation: the field's most careful open-ended evaluation to date found failures *upstream of execution*.

---

## 3. Draft introduction

> Autonomous agents are increasingly given scientific work rather than scientific instructions. A
> biologist does not hand an agent a loss function; they ask which immune features predict poor vaccine
> response, or whether a cell population changes with age. Such a prompt does not determine an analysis.
> It admits many — differing in what a term denotes, which cohort is meant, at what resolution the
> question is asked, and by which method it is answered — and these differences are not cosmetic: they
> change the conclusion. Problem formulation in data-driven work is discretionary and consequential
> (Passi and Barocas, 2019), and the accumulated weight of defensible analytic choices has long been
> recognised as a threat to inference in its own right (Gelman and Loken, 2013; Silberzahn et al., 2018).
> Bertran et al. (2026) recently showed this survives automation: across roughly 3,300 audited
> autonomous-analyst runs on a *fixed* hypothesis with a *prespecified* estimand, agents still disagreed
> on the sign of the effect, and the disagreement traced to enumerable choices in covariate selection,
> estimator, and pooling.
>
> Current agent benchmarks are built the other way around. Whether verifiable — MLE-bench, RE-Bench,
> MLAgentBench — or rubric-graded — PaperBench, MLR-Bench, LifeSciBench — they hand the agent a task that
> is already framed and score what it does next. This is deliberate and it makes the score interpretable,
> but it means a valid artifact is read as evidence that the agent understood the task. Under
> underspecification that inference fails: an agent can produce a clean, executable, well-formed result
> under a framing nobody intended. Stoisser et al. (2026) named this *unflagged misframing* and showed it
> is the dominant failure mode in data-science agents — five frontier agents committed to a plausible but
> unintended prediction target on 39–63% of ambiguous tasks, and user-facing flagging never exceeded 4%
> even when their own traces acknowledged the ambiguity. Kirgis et al. (2026), running the most resourced
> open-ended research evaluation to date, found the complement: agents completed six days of engineering
> unaided, yet both papers were unambiguously rejected by the original authors for failures *upstream* of
> execution — what bar the work had to clear, and what the research design should have been. Gulati et al.
> (2026) then showed why upstream is the operative word: injecting the missing goal after 10% of an
> agent's trajectory already forfeits most of its value, and by 70% it is worth no more than never
> supplying it at all. A framing error is not a mistake the agent recovers from later.
>
> The response the field has converged on is to ask. A sequence of benchmarks measures whether an agent
> detects underspecification and poses a clarifying question — in open-domain retrieval (CLAMBER, ~12K
> items over an eight-category ambiguity taxonomy), in open-domain QA (AmbigQA, as used by Su et al.,
> 2026), in long-horizon tool use and enterprise workflows (LHAW; Gulati et al., 2026), and in predictive
> data science (Ambig-DS; Stoisser et al., 2026). Two results recur. First, clarification works when it
> arrives: a scoped oracle answering one question recovers most of the lost performance. Second, agents
> cannot calibrate when to invoke it — permissive prompting induces over-asking on fully specified tasks,
> conservative prompting induces silent defaulting on ambiguous ones, and every model–policy pair Stoisser
> et al. evaluated was miscalibrated on at least one suite. Su et al. sharpen this into a dissociation:
> models identify a question as ambiguous 60–80% of the time when asked to judge it, but in the answering
> setting 80–95% of their responses are bare answers and clarification rates sit below 5%. The bottleneck
> is not detection. It is that the recognition never becomes an object the system can act on.
>
> We argue that ask-or-act is the wrong response space for scientific work, and that benchmarks built on
> it therefore cannot separate a well-calibrated agent from an indiscriminate one. When a scientific
> prompt is open, asking the user is only one of several correct moves, and usually not the right one.
> Where two readings would disagree only because one of them is *wrong* — confounded, invalid for this
> data, an artifact — the disagreement is settled by evidence, not by the user, and the agent's job is to
> name the result that would settle it. Where two readings can both be right about different things, the
> correct response is to run both and state the aggregation rule, which is what the multiverse tradition
> prescribes and what agentic analysis now makes cheap (Bertran et al., 2026). Only where the readings
> encode genuinely different objectives, with no rule combining them, does the choice belong to the user.
> Which of these three holds is a property of the individual source of openness, and different sources in
> the same prompt fall differently — so a single ask/act decision per prompt cannot express the answer.
>
> We therefore recast prompt interpretation as a structured, auditable prediction rather than a binary
> flag. Given a prompt and a description of the available data, an agent must (i) enumerate the spans of
> the prompt that admit two or more defensible readings, (ii) assign each a type from a fixed vocabulary
> of openness — concept, data, scope, implementation, deliverables — (iii) enumerate the candidate
> readings and the one-sentence result that would show a branch wrong, (iv) assign a verdict determining
> what resolves it (CONVERGENT, FRAMEABLE, UNFRAMED) and, independently, whether the candidates combine
> rather than compete, and (v) derive an overall
> task level L0–L3. Two distinctions are worth stating early. This vocabulary is not a finer grid over the
> goal/input/constraint/context dimensions used in the clarification-timing literature: those describe
> what information is *missing from the instruction*, whereas ours describes what the sentence could
> *mean given the data*, and the two tags that dominate biomedical prompts — scope and granularity — have
> no counterpart there. And L0–L3 grades *the prompt*, not the agent: it is orthogonal to the autonomy
> ladders that share the notation (Vibe-Research/AutoResearch L0–L4, which grade how much authority has
> shifted from human to system) and to task-difficulty scopes such as AARRI-Bench's S1–S4. A task can be
> mechanically trivial and L3, or intellectually demanding and L1.
>
> We contribute EGAD-Interpretation: N expert-annotated case cards spanning L0–L3, built by three
> complementary routes — real prompts from a working biomedical analysis platform, shadow interpretation
> of published papers against their own Methods sections, and controlled single-variable ablations of
> fully specified tasks — together with a scoring protocol that measures openness-row detection, tag
> agreement, verdict agreement, and level accuracy against balanced controls, so that an agent which
> declares everything open scores no better than one which declares nothing open. Because the tag
> vocabulary is fixed, an interpreter that meets a source of openness it cannot type must say so rather
> than force a fit, and the rate at which this happens is reported as a first-class result. We evaluate
> [K] frontier models under [A] elicitation regimes with [R] repetitions each, and [preview of result].

Placeholders `N`, `K`, `A`, `R`, `[preview]` to fill. Passi & Barocas 2019, Gelman & Loken 2013,
Silberzahn 2018 are the classical anchors; the rest are §1.

### 3.1 Positioning table (for the related-work section)

| Work | What they did | What EGAD adds |
|---|---|---|
| **Ambig-DS** (Stoisser 2026) | Paired specified/ambiguous variants of 51 DSBench + 61 MLE-bench tasks over two framing variables (target, metric); scored by the source evaluator. Silent misframing 39–63%, flagged <4%; oracle recovers it; ask-calibration fails in both directions. | Openness is typed (7 tags) and multiple per prompt, not one binary per task; the response space is four verdicts, not ask/act; ground truth is an expert openness table, not a protocol convention `θ*`; open-ended biomedical discovery, where no hidden correct framing exists. |
| **Ask Early, Ask Late, Ask Right** (Gulati 2026) | Forced-injection VOI curves over 84 underspecified variants, 6,000+ runs; goal clarification dead by 10% of trajectory; no frontier model asks in the optimal window. Explicitly leaves the "supply side" — recognising ambiguity — to future work. | Supplies exactly that side: a pre-execution artifact produced before action 1, so nothing has to be injected mid-trajectory. Their dimensions are re-derived as a strict subset of the tag vocabulary. |
| **Knowing but Not Showing** (Su 2026) | On AmbigQA (1,000 items), separates recognition from behaviour; models judge ambiguity well but clarify <5% of the time; retrieved context suppresses clarification further; models under-assign *scope* relative to humans. | Treats the recognition–behaviour gap as an artifact problem: force the recognition into a table with candidates, refuters and a verdict, so it cannot be silently discarded. Their scope finding is a pre-registered prediction for the per-tag recall. |
| **CLAMBER** (2024) | ~12K IR queries, 3 dimensions / 8 categories of query ambiguity; best model 54% accuracy; CoT and few-shot increase overconfidence without helping. | Ambiguity of an *analysis* rather than of a *query*: method-path, granularity, modality have no analogue in a retrieval taxonomy. Their *Contradiction* category is imported as an incoherence escape, distinct from openness. |
| **Many AI analysts, one dataset** (Bertran 2026, PNAS) | ~5,000 autonomous-analyst runs, 3,303 audited; sign-level disagreement under a fixed hypothesis and estimand; conclusions steerable by persona (34–66 pp). Proposes measuring dispersion against a published specification. | Declares the multiverse *prospectively*, as ADDITIVE rows with a stated aggregation rule, instead of measuring dispersion after the fact. Their extracted decision codebooks serve as objective ground truth for those rows. |
| **Kirgis et al.** (2026) | Shadow evaluations: two unpublished NeurIPS papers, six days, $3,000 credit; both rejected; five failure modes, of which judgment about the research bar and the design are upstream of execution. | Isolates and measures the upstream step they identify but do not instrument. Their method is adapted into shadow *interpretation*, scoring the openness table against the paper's own Methods. |
| **AARRI-Bench** (S1–S4), **AutoResearch** (L0–L4) | Ladders over agent scope and over human/AI authority; 82 manually crafted research-intern tasks, best configuration 68.3%. | An orthogonal axis: a grade on the prompt, assigned by evidence (candidates, refuters, verdicts) rather than holistically. |

---

## 4. New benchmark design

### 4.1 Case cards

Target **N = 120**, balanced **L0:20 / L1:40 / L2:40 / L3:20**. Balance is not cosmetic — without L0/L1
negative controls, "always answer L3" wins.

Per card:

```yaml
id: ic-0042
prompt: <verbatim, one paragraph max>
provenance: platform-log | shadow-paper:<doi> | ablation:<source-benchmark>:<task-id>
data_context: <the datalake facts the annotator was allowed to see>
gold_level: L2
gold_rows:
  - span: "poor vaccine response"
    tag: concept
    candidates: [low antibody fold-change, failure to seroconvert, weak cell-mediated response]
    verdict: UNFRAMED
    decision_relevant: true      # the branches give different scientific conclusions
data_constraints: [...]          # binding facts that were never open
dropped_candidates: [...]        # readings ruled out by the data
annotators: [a1, a2]
adjudicated: true
```

Every card needs a **decision-relevance** flag per row, inherited from Ambig-DS's checklist. A source of
openness that changes nothing downstream is not worth detecting and inflates recall.

### 4.2 Three construction routes

1. **Platform logs** — real user prompts. Highest ecological validity, uncontrolled level distribution,
   small N. Use for L2/L3.
2. **Shadow interpretation** — §2. Paper's central question as prompt; Methods as the authors' resolution.
   Scales, expert ground truth, domain-matched.
3. **Controlled ablation** — take a fully specified prompt (LifeSciBench, BixBench, DiscoveryBench) and
   remove exactly one framing variable per variant. Yields matched L1→L2→L3 ladders on identical
   scientific content, so level effects are not confounded with topic. **This is the strongest arm** and
   the one that makes the paper causal rather than descriptive; it generalises Ambig-DS's `(T, M)` to
   seven axes, which is literally their stated future work.

### 4.3 Tag vocabulary with a refusal option

The `#TODO` — an annotator who cannot fit a span to an existing tag must not force one:

```
TAG-MISS: span="..." proposed_tag="..." definition="..." why_no_existing_tag_fits="..."
```

A `TAG-MISS` halts that card pending adjudication; accepted proposals version the vocabulary. Report
**tag-miss rate** as a first-class result — it is direct evidence for or against the vocabulary's
completeness, and a benchmark whose taxonomy is claimed to be complete but never tested for closure is
weak. Apply the same rule to the agent under test: give it the vocabulary *and* the escape hatch, and
count how often it invents a tag versus mis-assigning a real one.

### 4.4 Metrics

| Metric | What it catches |
|---|---|
| Row detection P/R/F1 (span-overlap matching) | Missed and hallucinated sources of openness |
| Tag agreement (Cohen's κ, on matched rows) | Whether the typing is real or noise |
| Verdict agreement, and specifically **UNFRAMED recall** | Failure to escalate a genuine user decision |
| **FRAMED false-positive rate** | Silent commitment — the Ambig-DS failure, per row |
| Level accuracy, ordinal MAE, quadratic-weighted κ | Overall calibration |
| **Asymmetric level error** (under-call vs over-call, reported separately) | Under-calling = silent commitment; over-calling = wasting the user. Never average these. |
| Over-framing rate on L0/L1 controls | The over-asking pathology |
| Run-to-run stability across R reps: modal-level agreement, row-set Jaccard | Supporting only — variance is already published elsewhere (§1.2) |
| Tag-miss rate | Vocabulary completeness |

### 4.5 Decision-relevance subset (recommended add-on)

The one thing scoring against an annotated table cannot show is that misinterpretation *matters*.
Ambig-DS got this free from source evaluators. Take **~20 L2/L3 cards**, execute two branches of one row
each through the full egad loop, and report how often the scientific conclusion flips. Twenty cases is
enough to make the point and small enough to actually run. Without it, a reviewer's "so what?" has no
answer.

---

## 5. Run scenarios

Four arms, not three — the third arm as written confounds two changes at once.

| Arm | Prompt given to the model | Isolates |
|---|---|---|
| **A0 Naive** | Raw prompt, no scaffolding: "here is the task, proceed." | Baseline silent-commitment rate |
| **A1 Levels-only** | L0–L3 definitions, asked to classify | Does naming the scale suffice? |
| **A2 Decompose** | Openness tags + "one tag per row, take the max level" | Value of typed decomposition, *without* the verdict calculus |
| **A3 Full protocol** | `task_interpreter.md` verbatim — candidates, refuters, verdict tree, dependencies | Value of the refuter/verdict machinery on top of A2 |
| **H Human** | Domain experts, ~20-card subset | Ceiling. Reviewers will demand it. |

A2 is the ablation that lets you attribute any A3 gain to the verdict calculus rather than to
decomposition in general. Without it the headline claim in §1.3 is unsupported by your own experiment.

**R = 5** repetitions per (arm × card × model). Report medians and the stability metrics, not means.
Models: ≥3 spanning a capability range (frontier + mid + efficient), so the result is a property of the
protocol rather than of one model.

Cost: 4 arms × 120 cards × 5 reps × 3 models = 7,200 interpretation calls. No execution, short outputs —
cheap. The 20-card decision-relevance subset is where the real compute goes.

### On "interpretation vs. scientific tackling"

Keep interpretation as the headline. It is controlled, cheap, gradeable without a hidden right answer,
and it is the axis that is still open after Ambig-DS. Full scientific tackling is Kirgis's territory,
costs $3,000 per run, and produced a single bit of information (rejected). The §4.5 subset buys the
downstream evidence at 1% of that cost.

---

## 6. Open items

- **Next action:** obtain the LHAW / Gulati variant set and re-annotate the 84 variants (§2.0-1). This
  validates or breaks the tag vocabulary before any cards are written.
- Ambig-SWE (2502.13069) is the one near-collision still unread.
- Add an incoherence state (CLAMBER *Contradiction*): prompt conflicts with itself or with the data, so
  zero readings are valid. Currently the interpreter would silently pick one. Verdict-level, not a tag.
- Pre-register the prediction that `scope` has the lowest per-tag recall (Su et al.).
- Check whether the interpreter's datalake description suppresses row detection the way retrieved
  context suppresses clarification in Su et al. Cheap ablation: run with and without it.
- Verify LifeSciBench licensing/access for derivative ablated variants.
- Decide inter-annotator protocol: two independent annotators + adjudication is the minimum a reviewer
  will accept for a taxonomy paper; report κ on the gold set itself.
