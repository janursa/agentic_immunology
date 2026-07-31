# Design Graphs

Diagrams in `design.md`/`report.md` are no longer mermaid. A diagram is a placeholder fenced block
naming a graph id:

```graph
overview
```

The actual graph data lives in a sibling JS file, same basename, `.graphs.js` suffix
(`design.md` -> `design.graphs.js`, `report.md` -> `report.graphs.js`), next to the `.md` file.
It's a plain object keyed by graph id — one entry per placeholder used in the `.md`:

```js
window.DESIGN_GRAPHS = {
  overview: {
    nodes: [
      { id: "P0", label: "Phase 0: Compositional remodeling", type: "step" },
      { id: "CP0", label: "Checkpoint 0 met?", type: "decision" },
      { id: "P1", label: "Phase 1: Transcriptional remodeling", type: "step" },
    ],
    edges: [
      { from: "P0", to: "CP0", kind: "flow" },
      { from: "CP0", to: "P0", kind: "flow", label: "no, revise" },
      { from: "CP0", to: "P1", kind: "flow", label: "yes" },
    ],
  },
  phase0: {
    nodes: [
      { id: "Round0", label: "Phase 0: Compositional remodeling" },
      { id: "S1", label: "Step 1: QC / data prep", type: "step", parent: "Round0" },
      { id: "S2", label: "Step 2: Major_CT proportions", type: "step", parent: "Round0" },
      { id: "DS1", label: "sc/abf300.h5ad", type: "dataset", parent: "Round0" },
      { id: "CP", label: "Checkpoint 0", type: "decision", parent: "Round0" },
    ],
    edges: [
      { from: "S1", to: "S2", kind: "flow" },
      { from: "S1", to: "DS1", kind: "data" },
      { from: "S2", to: "CP", kind: "flow" },
    ],
  },
};
```

## Rules
- One placeholder per diagram, id matches a key in the `.graphs.js` file. Placeholders render in the
  order they appear in the `.md` — put them where the diagram should sit (Overview section, each
  phase's Execution plan section), same structure as before.
- **Node** — `id` (unique), `label` (few words — anything longer goes in prose, not the node), `type`
  (`step` | `decision` | `dataset` | `method` | `stop`; omit for a group/round box), `parent` (optional
  — id of the group node it sits inside, replaces mermaid's `subgraph`).
- **Edge** — `from`, `to`, `kind` (`flow` = solid blue, logical/sequential order between steps or a
  decision branch; `data` = dashed green, step-to-dataset-or-method input/output usage), `label`
  (optional, e.g. branch condition). Colors are fixed by `kind` (rendered by
  `render_review_artifact.py`) so different edge purposes stay visually distinct — don't invent new
  kinds without adding a style for them.
- Two kinds of diagram, never combined into one graph id: **overview** (multi-phase tasks only, one
  node per phase) and **per-phase** (one node per step, dataset/method nodes as `data`-kind edges,
  checkpoint as a `decision` node at the end). Same separation as before, just as separate graph ids
  instead of separate mermaid fences.
