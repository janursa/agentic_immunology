# Draw.io conventions

Applies to every `.drawio` file under `draw/`.

- Font: Arial everywhere (`fontFamily=Arial`).
- Default text size: 10px (`fontSize=10`). Exceptions: pictogram glyphs (🧑/🤖 actors — sized for visual weight, not real text) and diagram titles.
- Color coding:
  - User-facing step: fill `#EEF2FF`
  - Automated orchestrator/agent step: fill `#ECFDF5`
  - Peer-review / gating step: fill `#FFFBEB`
  - Memory store: fill `#F1F5F9`
  - Decision/branch point: fill `#F8FAFC`
- Box style: `rounded=1;arcSize=12;strokeColor=#000000;strokeWidth=2` for flow nodes; dashed border (`dashed=1`, no fill or white fill) for annotative callouts.
- Arrows: solid `#94A3B8` for main flow; dashed `#7C3AED` for memory retrieve/store; dashed `#D97706` for review/annotation ties.
