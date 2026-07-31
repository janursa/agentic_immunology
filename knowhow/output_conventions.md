## Output conventions

### Folder layout

```
temp/{task}/
  phase_{n}/      # n = the PHASE this task belongs to (single-phase tasks still use phase_0/)
    {sub_task}/
      code/
        script.py     # (or script.R) — runs from scratch to reproduce all outputs
      results/
        images/       # all figures
        *.csv / *.tsv # data outputs
      LOG.md          # updated as you go: task prompt at top, then every step + tool call
```

- Use **absolute paths** for every file reference inside scripts.
- `/tmp/` is only for singularity scratch; all persistent outputs go in the task folder above.
- The orchestrator gives you your exact trajectory/subfolder (`temp/{task}/phase_{n}/{sub_task}/`) — use that as your root so parallel runs don't collide.
- `LOG.md` and `code/script.*` are updated **incrementally** — not written only at the end.
- Use `agentic_immunology/` as your only workspace, for both data exploration and code execution, unless told otherwise.

### Steps graph
⛔ HARD RULE — produce a graph of steps taken, results generated, and their connections, as node/edge JSON matching `knowhow/design_graphs.md`'s schema (`{nodes: [{id, label, type, parent}], edges: [{from, to, kind, label}]}`). Save it to `results/steps_graph.json`. A rendered static image alongside it is optional, not a substitute.

### Report back
Return to the orchestrator: key findings (grounded in data/tool outputs) + **absolute paths** of every output file.
