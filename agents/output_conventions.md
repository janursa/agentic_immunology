## Output conventions

### Folder layout

```
temp/{task}/
  code/
    script.py     # (or script.R) — runs from scratch to reproduce all outputs
  results/
    images/       # all figures
    *.csv / *.tsv # data outputs
  LOG.md          # updated as you go: task prompt at top, then every step + tool call
```

- Use **absolute paths** for every file reference inside scripts.
- `/tmp/` is only for singularity scratch; all persistent outputs go in the task folder above.
- If the orchestrator gives you a trajectory/subfolder (e.g. `temp/{task}/{sub}/`), use that as your root instead so parallel runs don't collide.
- `LOG.md` and `code/script.*` are updated **incrementally** — not written only at the end.
- Use `agentic_immunology/` as your only workspace, for both data exploration and code execution, unless told otherwise.

### Steps graph
⛔ HARD RULE — produce a graph of steps taken, results generated, and their connections. Save it to `results/`.

### Report back
Return to the orchestrator: key findings (grounded in data/tool outputs) + **absolute paths** of every output file.
