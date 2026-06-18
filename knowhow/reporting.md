# Reporting — Reference

How to write the final user-facing report after analysis is complete (and peer-reviewed, if review was run). The orchestrator writes this report directly — no subagent delegation needed.

---

## What to produce

Write `report.md` in the same `temp/{task}/` folder used by the analysis:

1. **Restate the original question.**
2. **Answer it directly**, grounded in the data — phrase every claim as "{statement}, obtained from {x} and {y} data," citing the specific output files/figures that support it.
3. **List all generated files** with absolute paths: scripts, data outputs, images, `LOG.md`, steps graph.
4. **Evaluation against success criteria** — state how each main claim was evaluated (from `peer_review.md` if review was run), and include any caveats/limitations.

## Rules

- Do not re-run or modify any analysis script — only read existing outputs.
- Every claim must cite a specific output file or tool result, not general knowledge.
- Relay the absolute path of `report.md` to the user.
