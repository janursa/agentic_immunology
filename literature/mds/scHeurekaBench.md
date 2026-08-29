# HeurekaBench: A Benchmarking Framework for AI Co-Scientist

Panigrahi, Videnović, Brbić (EPFL / ETH Zurich) — ICLR 2026, arXiv:2601.01678v2.
Code + benchmark: https://github.com/mlbio-epfl/heurekabench · brbiclab.epfl.ch/projects/heurekabench

## Abstract
LLM-based reasoning models have enabled agentic systems that act as co-scientists, assisting in multi-step scientific analysis. Evaluating these systems is challenging, as it requires realistic, end-to-end research scenarios that integrate data analysis, interpretation, and the generation of new insights from experimental data. HEUREKABENCH is a framework to create benchmarks with **exploratory, open-ended research questions** for experimental datasets. Each question is grounded in a scientific study and its corresponding code repository, and is created using a semi-automated pipeline that leverages multiple LLMs to extract insights and generate candidate workflows, which are then verified against reported findings. Instantiated in single-cell biology as **sc-HEUREKABENCH**. Adding a **critic** module improves ill-formed responses for open-source LLM agents by up to 22% and closes the gap with closed-source counterparts.

## Methods

### The task formulation
A benchmark instance is a triplet **(D, Q, A)**: a dataset *D* (real experimental data plus auxiliary files, e.g. a gene count matrix and treatment metadata), an **open-ended research question** *Q* demanding multi-step reasoning over *D*, and a ground-truth answer *A* derived from a published finding. The paper's stated design principle is that "a co-scientist should autonomously plan these questions as sub-steps within the workflow, rather than [receive] explicit user instructions."

The explicit contrast with prior benchmarks is a contrast in *prompt specificity*. Named as what HeurekaBench is NOT: *"How many miRNAs remain significant at p ≤ 0.05 after Benjamini-Hochberg correction?"* (BixBench) and *"Train a VAE model and perform a 1-vs-all differential expression test for each cell type"* (ScienceAgentBench). Those are single computational questions with the method already chosen; a HeurekaBench question is *"What changes in cytokine expression are observed in the aging muscle microenvironment?"*, where selecting the analyses is the agent's job.

### Benchmark construction (the transferable part)
Grounded in the scientific process itself, not in LLM imagination. Two stages, four LLM modules:

**(a) Insight generation.** `InsightExtractor` proposes candidate insights from the paper, each represented as three linked components — a *summary*, the *experimental techniques* the paper used to establish it, and *grounding text* (verbatim statements from the paper as supporting evidence). `CodeDescriber` converts each script in the paper's repo into a natural-language summary. `CodeMatcher` links insights to the most relevant code descriptions. `CodeGenerator` composes the retrieved scripts into a multi-step workflow for the insight. **Human reviewers then run the code** (permitted minor edits: loading the dataset, mapping Ensembl IDs to common names, renaming variables/metadata) and an insight is **validated only if the workflow output reproduces the result reported in the paper**. Everything else is discarded — this is the explicit fix for BaisBench, which generates questions from a single LLM with no execution grounding.

**(b) Question generation.** Each validated insight yields two formats: **OEQs** (open-ended, the primary format — "intentionally less specific, allowing multiple approaches to reach the correct answer") and **MCQs** (a lightweight proxy for rapid prototyping, with deliberately hard distractors capturing plausible misinterpretations and common analytical errors). Two-stage filtering: **automatic** — GPT-4o and Claude-4-Sonnet both answer every question; MCQs both get right are discarded, OEQs scoring above 3.0 for both are discarded (this removes questions answerable from pretraining knowledge alone); then **manual** — remove hallucinations, duplicates, and questions derived from non-validated components of an insight.

### Evaluation: atomic-fact G-Eval
G-Eval with GPT-4o as judge, correctness 1–5. The judge is instructed to **decompose both the agent response and the ground truth into atomic facts** (conditions, trends, gene/pathway names, statistical evidence, conclusions), label each GT fact PRESENT / PARTIAL / MISSING / INCORRECT, and score from the coverage counts.

The load-bearing rule is what qualifies as PRESENT: the fact must be **"explicitly tied to dataset-derived quantitative/statistical outputs or cluster/subtype identifiers"** — percentages, fold changes, p-values, cluster IDs, enrichment scores. A fact that is correct but supported only by descriptive biology, a list of plausible markers, or hedged language ("likely", "typically", "e.g.") is downgraded to PARTIAL. This is the mechanism that **penalises answering from pretraining knowledge rather than from the data**. Additional non-GT findings, if non-contradictory, do not affect the score — novel discovery is not punished.

Scale: 5 = all GT facts PRESENT, no contradictions; 3 = some PRESENT, at least one PARTIAL/MISSING; 2 = none PRESENT, some PARTIAL, answer reads as recall not evidence; 1 = all MISSING, or major contradictions, or the agent states it cannot answer.

### sc-HeurekaBench instantiation
22 papers from *Nature* and *Cell* (2024–2025) with open code repos and open datasets (CellxGene or publication resources); recency chosen to mitigate memorisation. GPT-4o in `InsightExtractor`, Claude-4-Sonnet in the code modules; 10 candidate insights per paper → **41 validated insights across 13 papers** → **50 OEQs + 50 MCQs**. Domains span adipose tissue, neuroblastoma pre/post chemotherapy, myocarditis, brain development, embryonic limb, intestinal Treg, muscle aging, small-intestine nutrient absorption, mouse ovary aging, dementia, placenta/pathogens, microglia, uNK–trophoblast interaction.

**Task prompt to agents (OEQs), verbatim:**
> Task: Analyze the provided single-cell dataset and answer the biology question.
> Input Data: {data paths}
> Question: {question}
> Output Format: Return the summary of an answer wrapped inside XML-style tags `<solution>` and `</solution>`.
> Guidelines: Base the answer strictly on the results derived from the dataset. Provide a fact-based summary (not a narrative or manuscript-style report). Do not use extra formatting such as bullet points or section headers. Include all key findings that directly address the question, emphasizing those most relevant to the answer.

**Six OEQ categories** (with counts, sc-HeurekaBench / Lite): heterogeneity analysis (18/10), cellular functioning (10/2), key gene analysis (9/4), condition-treatment analysis (6/3), pathway analysis (5/1), cell-cell communication (4/0). Questions frequently span categories.

**sc-HeurekaBench-TU (ToolUsage).** 12 OEQs built from insights that *could not be validated* because `CodeGenerator` hallucinated the use of domain-specific tools/databases (SCENIC, CellPhoneDB, CellChat, NMF). Repurposed as a benchmark for whether an agent reaches for the right specialised tool.

**sc-HeurekaBench-Lite.** 22 OEQs / 18 MCQs restricted to datasets under 750 MB, because CellVoyager took up to an hour per question and BixBench-Agent crashed on large datasets.

## Results

**Pipeline validation.** `InsightExtractor` against expert findings: FlyBase 44 strongly / 2 weakly / 4 unrelated out of 50; BixBench 14 / 4 / 3 out of 21. `CodeDescriber`+`CodeMatcher` on InsightBench: 158 of 215 scripts correctly matched, mean 74.6% of files retrieved correctly per insight.

**Agent comparison (sc-HeurekaBench-Lite, all on Claude-4-Sonnet).** Biomni OEQ 2.31 / MCQ 50.00%; BixBench-Agent OEQ **2.34** / MCQ 44.44%; CellVoyager OEQ 2.03 / MCQ 27.78%. The flexible agent loops beat CellVoyager's rigid fixed-step architecture, whose failure modes were restrictive code-fixing, difficulty incorporating multiple feedback per step, and a pre-specified step count that sometimes cut the workflow short.

**Planner ablation (Biomni, full sc-HeurekaBench, 3 runs).** Claude-4-Sonnet OEQ **2.58 ± 0.05** (MCQ 44.00), well ahead of the best open-weight GPT-OSS-120B at 2.08 ± 0.05; Qwen3-235B-THINKING 1.85, Qwen3-235B 1.57, Qwen3-32B 1.47, MedGemma-27B 1.53, GPT-4o 1.68. Scale helps, thinking mode helps (+0.28 over non-thinking). **Nothing clears 2.6 out of 5.**

**Agent vs bare LLM.** Claude-4-Sonnet alone: OEQ 1.90, MCQ 22.00%. Inside Biomni: OEQ 2.56, MCQ 44.00%. The agent loop is worth ~0.7 points, and a top LLM without one scores below 2.

**Critic ablation.** `End-critic` (critique when the planner decides to exit) lifts GPT-OSS-120B from 2.04 to 2.49 — close to Claude-4-Sonnet's 2.58 — with the gain concentrated on low-scoring questions (+0.6 across 30 cases), 16 improved / 9 worsened. `Plan-critic` (critique the initial plan) **consistently hurts**: −0.13 for GPT-OSS, −0.19 for Qwen3, degrading mid- and high-scoring questions (0/3 better/worse on high). For Qwen3-235B-THINKING even End-critic is roughly neutral (1.86 → 1.81) — it helps weak answers and damages strong ones. Conclusion: **critic placement is crucial — feedback at the end can improve poorer responses, while at the beginning it can disrupt reasoning trajectories.**

**Retriever ablation (sc-HeurekaBench-TU).** Tool retrieval before planning matters: GPT-OSS-120B 2.15 → 1.56 without it; Qwen3-235B-THINKING 1.92 → 1.80.

**Judge reliability.** Three LLM judges (GPT-4o, Claude-4.5-Sonnet, Gemini-2.5-Pro) agree on planner ranking. GPT-4o vs Claude-4.5-Sonnet: Spearman 0.84 ± 0.03, κ 0.81 ± 0.03; vs Gemini-2.5-Pro 0.79 / 0.71. **Human alignment**: 11 expert raters (PhD/postdoc, ≥1 yr single-cell experience, 4 universities / 6 labs) on 25 Biomni answers — LLM-judge within ≤1 point of the human score on 92% (mode) / 96% (median) of questions, Spearman 0.93 / 0.90, κ 0.85.

## Failure modes (manual analysis)
- **Incorrect scientific skills** — the agent recalls pretraining knowledge instead of calling the right tool: rather than running gene set enrichment, it recalls canonical markers for a pathway (sometimes lifted from the MCQ options) and takes their mean expression. It also frequently fails to explore all metadata columns and so never finds the relevant variable.
- **Lack of environment exploration** — uses only a few retrieved tools, never considers other components of the environment that would enable a more holistic response.
- **Hallucinations** — answers directly with no analysis or an incomplete one.
- **Other** — writing large code blocks instead of stepwise snippets; unable to take execution errors into account; using known literature to eliminate MCQ options, "which actively goes against the idea of data-driven discovery".

All are more prevalent in open-source than closed-source LLMs.

## Limitations
Evaluation relies **solely on the final agent response** — no verification of intermediate workflow steps and no partial credit for correct steps (the authors name this as the main limitation and future work). MCQ distractors are LLM-generated, so some "incorrect" options may be scientifically plausible — hence precision/recall are reported alongside accuracy. Invalidated insights were dropped for three reasons: insufficient dataset information (workflow assumes bulk RNA-seq, only scRNA-seq available), inconsistency between workflow requirements and the available data (references sub-cluster info the dataset lacks), and overly generic insights that yield no meaningful question. Extending to other domains requires domain experts for manual validation.
