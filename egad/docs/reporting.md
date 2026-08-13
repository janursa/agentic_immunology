# Reporting — Reference

How to write `findings.md`, the user-facing report for a task.
Named `findings.md`, not `report.md` — Claude Code blocks subagent writes to `report*.md`
(github.com/anthropics/claude-code/issues/44657).
---

## Where and when

- Path: `${CIIM_TEMP_DIR}/{task}/findings.md`. One file for the whole task.
- Each phase **appends** its own
  `### Phase {n}` block under `## Detailed findings` — never rewrite an earlier phase's block. The
  `## Summary` subsections are **rewritten** each phase against the cumulative results.
- Source material: that phase's `peer_review.md`, `design.md`, `log.md`, and the absolute
  paths/findings returned by subagents.

## Fixed structure

Use exactly these `##` headers, in this order — `${CIIM_MAIN_DIR}/scripts/render_review_artifact.py` turns every `## `
section into one review card, so don't add extra top-level `## ` sections or rename these.

```markdown
## Task
### Original prompt
{verbatim user prompt}

### Interpreted prompt
{your interpretation, if any}

## Summary
### Principal findings
{one bullet per verifiable biology finding, cumulative across phases so far. Plain biology claim only.}
CRITICAL: biology only — no test counts, FDR/permutation/split-half stats, artifact paths, or
confidence labels; those belong in Detailed findings / Concordance with prior expectation.

### Concordance with prior expectation
{per positive control (always) and per working hypothesis (`LITERATURE: on` only), from `design.md`: aligns | partial | contradicts. Every contradiction is attributed to a cause: wrong cohort, context, resolution, timing, power, or a genuine biological difference. Bulletins format.}

### Synthesis
{`FINAL_PHASE` only. What the findings jointly imply. This plays the role of mapping individual findigs to a bigger biological picture.}

### Alternative explanations
{`FINAL_PHASE` only. For the headline claim: what the design did exclude, and what remains unexcluded — confounding, batch/ascertainment, multiple testing, reverse causation, power. Never empty.}

### Derived hypotheses
{`FINAL_PHASE` only. 1-3. Each: the statement, a prediction that differs from the null, the discriminating test, the observation that would refute it, and whether it is testable with `docs/datalake.md`/`docs/tools.md` today or needs new data.}

## Detailed findings
### Phase {n}
{one seeprate block per phase, appended as phases complete: what this phase found, with plots. One bulletin per findings with details and relevant plots}
CRITICAL: this is not a summary findings but all important findings. 

#### Checkpoint outcome
{`peer_reviewer_agent`'s RESULTS-REVIEW output block for this phase, verbatim}

## Issues
{any issues encountered — errors, blocked hooks, peer-review REVISE cycles, etc. "None" if none}

## Code/files generated
{absolute paths of every file generated — planning, code, literature search, results, etc.}

```

## Rules
- **Before `FINAL_PHASE`**, write only `Principal findings` and `Concordance with prior expectation`
  under `## Summary`; the other three subsections are added at `FINAL_PHASE`. The `###` headers for
  them stay absent until then, not empty. `.claude/hooks/report_format_check.py` enforces this: once a
  `#### Checkpoint outcome` block in the file says `FINAL_PHASE: true`, all five subsections must be
  present and non-empty — so make the final phase's update **one write**, not an append followed by a
  separate summary edit.
- **Summary sourcing** — `Principal findings` and `Concordance with prior expectation` are transcribed
  from the phases' `#### Checkpoint outcome` blocks (the claims table and `POSITIVE CONTROLS:` line),
  not re-derived from the results dirs. 
- Relay the absolute path of `findings.md` to the user.
- Images in "Detailed findings" must use markdown `![alt](path)` with the path **relative to
  `findings.md`'s own directory** — the HTML render is served from `${CIIM_TEMP_DIR}/`, so an absolute filesystem
  path won't resolve in the browser. 
- Render to HTML per `egad.md`'s "Interact with user" section (`render_review_artifact.py`
  already handles `findings.md` the same way as `design.md`).
