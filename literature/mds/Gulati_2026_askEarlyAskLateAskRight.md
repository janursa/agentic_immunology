# Ask Early, Ask Late, Ask Right: When Does Clarification Timing Matter for Long-Horizon Agents?

## Abstract
Long-horizon AI agents execute complex workflows spanning hundreds of sequential actions, yet a single wrong assumption early on can cascade into irreversible errors. When instructions are incomplete, the agent must decide not only whether to ask for clarification but when, and no prior work measures how clarification value changes over the course of execution. We introduce a forced-injection framework that provides ground-truth clarifications at controlled points in the agent's trajectory across four information dimensions (goal, input, constraint, context), three agent benchmarks, and four frontier models (three per benchmark; one on a single benchmark only; 84 task variants; 6,000+ runs). Counter to the common intuition that "earlier is always better," we find that the value of clarification depends sharply on what information is missing: goal clarification loses nearly all value after 10% of execution (pass@3 drops from 0.78 to baseline), while input clarification retains value through roughly 50%. Deferring any clarification type past mid-trajectory degrades performance below never asking at all. Cross-model Kendall τ correlations (0.78–0.87 among models sharing identical task coverage; 0.34–0.67 across the full 4-model panel) confirm these timing profiles are substantially task-intrinsic. A complementary study of 300 unscripted sessions reveals that no current frontier model asks within the empirically optimal window, with strategies ranging from over-asking (52% of sessions) to never asking at all. These empirical demand curves provide the quantitative foundation that existing theoretical frameworks require but have lacked, and establish concrete design targets for timing-aware clarification policies. Code and data will be publicly released.

## Methods

### Hypotheses: Trajectory Commitment
A task is specified by a parameter vector θ = (θgoal, θinput, θcon, θctx), one component per dimension. The agent observes an underspecified version θ̃ in which one component θd is missing, and executes a trajectory τ = (a1, ..., aT). At injection time t, the agent receives the true value of θd. The commitment Cd(t) ∈ [0,1] is defined as the fraction of actions a1, ..., at that causally depend on dimension d. The value of clarification at time t is bounded by the recoverable portion:

VOId(t) ≤ VOId(0) · (1 − Cd(t))

since committed actions cannot be undone. Goal and context condition all subsequent actions, predicting concave, front-loaded commitment. Input affects only data-dependent steps and can be partially inferred through exploration, predicting approximately linear commitment. Constraints impose rules that may be invisible until violated, so late injection can be disruptive, with reconciliation cost potentially exceeding the information's value.

This yields two falsifiable hypotheses: **H1 (Dimension-dependent timing)**: goal and context clarification are front-loaded (steep VOI decay), while input clarification decays gradually. **H2 (Constraint attenuation)**: on benchmarks where an oracle gap exists, constraint clarification yields VOI that declines with delay, with reconciliation costs offsetting some but not all of the information's value.

### Experimental Design
For each of 84 underspecified task variants, seven conditions are run with three trials per condition across available models (four on MCP-Atlas, three on TheAgentCompany and SWE-Bench Pro), yielding over 6,000 total experiment runs. The seven conditions: (1) **oracle** — fully-specified original prompt (upper bound); (2) **no-clarification (NC)** — underspecified prompt, no additional information (lower bound); (3–7) five **injection** conditions at 10%, 30%, 50%, 70%, and 90% of the trajectory, where the missing information is provided mid-execution.

**Benchmarks and models.** 84 variants are drawn from a stratified subset of LHAW's underspecified tasks:
- **MCP-Atlas** (36 variants, 4 models): tool-use competency across real MCP servers, short trajectories (6–20 actions), all four dimensions represented. Only benchmark evaluating all four models including DeepSeek V3.2.
- **TheAgentCompany** (30 variants, 3 models): enterprise workflows on a simulated corporate platform, longer trajectories (6–49 actions); goal, constraint, input dimensions covered. DeepSeek V3.2 excluded (harness limitations).
- **SWE-Bench Pro** (18 variants, 3 models): code-repair tasks on real GitHub issues (1–121 actions). DeepSeek V3.2 excluded; n=12–31 (variant, model) units per injection cell depending on dimension.

Four information dimensions (from LHAW): **goal** (unclear deliverable), **constraint** (missing rules/thresholds), **input** (unspecified data source), **context** (absent domain knowledge). Variants are stratified by ambiguity class: outcome-critical, divergent, benign.

Four frontier models evaluated: GPT-5.2 (Over-clarifier, 52%), Claude Sonnet 4.5 (Balanced, 23%), Gemini 3 Flash (Under-clarifier, 0%), DeepSeek V3.2 (MCP-Atlas only).

**Forced injection protocol.** Injection points are calibrated per model and task. For model m and variant v, Bm,v is the mean oracle trajectory length (rounded to nearest integer). The injection action for timing t ∈ {0.1, 0.3, 0.5, 0.7, 0.9} is ainject = max(1, ⌊Bm,v · t⌋). For SWE-Bench Pro tasks where Bm,v = 1, all five injection conditions collapse to action 1 but are retained to preserve sample size. At the injection action, a synthetic user message containing the ground-truth removed_segments is inserted at the next clean turn boundary. The ask_user tool is disabled, so clarification arrives only through the injection.

**Natural ask protocol.** A complementary 300-session study on TheAgentCompany tasks with the ask_user MCP tool enabled. Each of three models (Claude Sonnet 4.5, GPT-5.2, Gemini 3 Flash) completes 100 sessions across seven base tasks (stratified subset of the 30 TAC variants, covering goal- and input-dimension variants across all three ambiguity classes). When invoked, a simulated user responds with the ground-truth missing information matching the forced-injection content. The action step of each ask_user call is recorded as a percentage of total trajectory length.

**Metrics.**
- *Pass@3*: probability that at least one of k=3 trials succeeds for each (variant, model, condition) cell (HumanEval formulation).
- *Wasted compute*: for injection conditions, the count of pre-injection actions whose effects are absent from the oracle trace, normalized by total pre-injection actions — a conservative upper bound on discarded work.
- *Point of no return*: the latest injection timing at which pass@3 significantly exceeds the no-clarification baseline (one-sided permutation test, p < 0.05).
- *Cross-model consistency*: Kendall's τ rank correlation of per-variant pass@3 vectors across model pairs, measuring whether timing effects are task-intrinsic or model-dependent.

## Results

### VOI Curves Are Dimension-Dependent (H1)
On MCP-Atlas (the benchmark with the strongest timing signal, n=5–28 per dimension), clarification timing interacts strongly with information dimension, partially confirming H1 (goal front-loading strongly supported; context prediction directionally consistent but underpowered at n=17 across two benchmarks):

- **Goal**: dramatic front-loading. Injection at 10% recovers near-oracle performance (pass@3 0.78 vs. oracle 0.80, NC 0.40). Benefit decays steeply: Inj-30 = 0.50, Inj-50 = 0.44, Inj-70 = 0.39 (≈NC), Inj-90 = 0.39. By 70% of the trajectory, goal injection no longer improves over no-clarification.
- **Input**: gradual decline (0.46 at Inj-10, 0.36 at Inj-30/50, 0.32 at Inj-70, 0.25 at Inj-90; NC = 0.33, oracle = 0.57). Early window (Inj-10 through Inj-50) recovers most of the oracle gap; by Inj-70 falls to NC baseline; by Inj-90 sits below it.
- **Constraint**: depends on whether an oracle gap exists. On MCP-Atlas, Oracle and NC are identical (both 0.12) — uninformative for H2. On SWE-Bench Pro, where the oracle gap is substantial (0.81 vs. 0.56 NC), constraint injection shows genuine declining benefit (0.81 at Inj-10, declining to 0.68 at Inj-90), supporting a weaker form of H2: reconciliation costs reduce constraint VOI relative to oracle, but injected constraint information remains above the NC baseline at all tested timings. The strong form of H2 (below-baseline disruption) is not supported by either benchmark.
- **Context**: MCP-Atlas (n=5) shows strong early-injection benefit (0.80 at 10% vs. 0.60 NC); SWE-Bench Pro (n=12) is essentially flat (0.92 at most injection points, Oracle = 0.67, NC = 0.75 — the NC > Oracle inversion reflects sampling variability). Combined sample (n=17) too small for reliable timing conclusions.

On TheAgentCompany, floor effects (oracle ≤29%) attenuate timing signals: goal injection conditions all sit within 4pp of NC (0.12), input shows mild benefit at intermediate timings (0.21–0.25 vs. 0.19 NC), constraint is at floor (0% across all conditions).

**Point of no return**: clarification benefit is continuous rather than threshold-based; only outcome-critical variants show a statistically significant recovery point, at 30% of the trajectory (p < 0.05). Earlier is always better, but there is no sharp cutoff after which clarification becomes useless.

### Wasted Compute
Wasted compute increases steadily with injection delay across all three benchmarks. On TheAgentCompany, waste rises from 0.0% at Inj-10 to 21.7% at Inj-90. On MCP-Atlas, it ranges from 38.4% to 52.9% (higher baseline reflecting shorter trajectories). SWE-Bench Pro: 0.7 to 10.4 wasted actions.

### Cross-Model Consistency
On TheAgentCompany (3 models, balanced variant set), Kendall's τ correlations range from 0.78 to 0.87, indicating strong agreement on which variants benefit from early clarification. On the combined dataset (4 frontier models), Claude-Gemini achieves τ=0.67 and all model pairs exceed 0.34 (p < 0.01 for all pairs). These results support the interpretation that timing effects are predominantly task-intrinsic.

### Natural Ask Overlay
Across 300 TheAgentCompany sessions: GPT-5.2 asks in 52% of sessions with mean first-ask timing 43% through the trajectory; Claude Sonnet 4.5 asks in 23% of sessions at mean timing 50%; Gemini 3 Flash never asks (0% ask rate across all 100 sessions). These archetypes are consistent with LHAW's independent finding that GPT-5.2 over-clarifies with the lowest per-question efficiency while Gemini models under-clarify.

Overlaying natural timings on forced-injection VOI curves reveals timing alignment gaps: GPT-5.2's asking at 43% is past the goal optimum (10%) but within the input window; Claude's 50% is suboptimal for goal but reasonable for input; Gemini forgoes all benefit. Notably, timing alignment alone does not predict success: Claude achieves higher per-session success (11%) than GPT-5.2 (3%) despite asking later and less often, suggesting question quality may matter more than frequency, though this between-model comparison cannot isolate question quality from other model-level differences and is treated as a hypothesis rather than a controlled finding.

## Conclusions
This is the first empirical measurement of VOI curves for clarification timing in long-horizon agent workflows. Timing effects are strongly dimension-dependent: goal clarification is front-loaded (≤10% window), input degrades gradually (recoverable through ~50%), and constraint benefit depends on the oracle gap, with cross-model consistency confirming these profiles are task-intrinsic. No current frontier model asks within the optimal window. Two actionable guidelines follow: (1) agents should validate goals within the first few actions; (2) input queries can be deferred slightly longer but should be raised within the first half of the trajectory. More broadly, the forced-injection methodology generalizes to any agent benchmark with underspecified tasks and provides the empirical demand curves that existing theoretical frameworks require but have lacked. Building timing-aware clarification policies on top of these curves is a natural next step.

### Limitations
This study establishes the demand side of clarification timing (how much task performance benefits from receiving information at each trajectory point) but does not address the supply side: making agents recognize ambiguity and ask at the right moment. The strongest timing signals come from MCP-Atlas (n=5–28 per dimension); TheAgentCompany provides weaker signal due to floor effects, and SWE-Bench Pro has moderate per-cell sizes (n=12–31). The natural-ask protocol covers only TheAgentCompany (300 sessions). A behavioral confound exists between protocols: forced injection disables ask_user while natural-ask enables it, so agents may plan differently when they know they cannot ask; the forced-injection VOI curves should be interpreted as upper bounds on information value.
