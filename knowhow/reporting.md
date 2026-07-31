# Reporting — Reference

How to write `report.md`, the user-facing report for a task.
---

## Where and when

- Path: `temp/{task}/report.md`.
- Compiled (overwritten, not appended) after each phase completes — before that phase's dashboard user-feedback step. Reflects cumulative progress through the current phase, not just that phase alone.
- Source material: `log.md`, `design.md`, `peer_review.md`, and the absolute paths/findings returned by subagents.

## Fixed structure

Use exactly these `##`/`###` headers, in this order — `knowhow/render_review_artifact.py` turns every `## ` section into one review card, so don't add extra top-level `## ` sections or rename these.

```markdown
## Task
### Original prompt
{verbatim user prompt}

### Interpreted prompt
{your interpretation, if any}

## Code/files generated
{absolute paths of every file generated — planning, code, literature search, results, etc.}

## Summary of findings
{one paragraph}

## Detailed findings
{detailed writeup, with plots}

### Full analysis dependency graph
{a `` ```graph `` fence, per `knowhow/design_graphs.md` — built from the subagents' `results/steps_graph.json` file(s), assembled into `report.graphs.js`. Not a static image.}

## Issues
{any issues encountered — errors, blocked hooks, peer-review REVISE cycles, etc. "None" if none}
```

## Rules
- Relay the absolute path of `report.md` to the user.
- Images in "Detailed findings" must use markdown `![alt](path)` with the path **relative to `report.md`'s own directory** — the HTML render is served from `temp/`, so an absolute filesystem path won't resolve in the browser.
- The dependency graph is interactive, not a static image: convert each subagent's `results/steps_graph.json` into an entry of the sibling `report.graphs.js` (`window.DESIGN_GRAPHS`, same schema/mechanism as `design.md` → `design.graphs.js`, see `knowhow/design_graphs.md`), and reference it with a `` ```graph `` fence.
- Render to HTML per `ciim_agentic.md`'s "Interact with user" section (`render_review_artifact.py` already handles `report.md` the same way as `design.md`).
