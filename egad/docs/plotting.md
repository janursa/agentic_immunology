# Plotting standards

CRITICAL: Apply all of the following rules whenever generating any plot:

## Font
- All text entities: Arial, size 10 (axis labels, tick labels, titles, colorbar labels, etc.)
- Exception — legend and annotations: one size smaller (size 9)

## Figure Size
- **Heatmap**: `figsize=(3, 3)` for ≤5 items on each axis. Add 0.5 per additional 2 items.
- **Barplot**: `figsize=(3, 3)`; prefer vertical orientation. For >10 items on the categorical axis, add 0.5 per additional 5 items.
- **Other plot types**: apply heatmap or barplot specs, whichever is more applicable to the plot geometry.

## Multi-Panel Figures
- Shared x-axis across panels: keep x-axis label on the first panel only, remove from others.
- Shared y-axis across panels: keep y-axis label on the first panel only, remove from others.
- Shared legend across panels: keep legend on the last panel only, placed outside the plot (upper right). Remove legends from all other panels.
- Reduce assembled figure size by 1 on the shared/assembled axis direction.

## Legend
- `frameon=False` always.
- Place outside the plot, upper right (`loc='upper left', bbox_to_anchor=(1, 1)`).
- If the legend is placed outside the plot boundary, add 1.5 to the figure width.

## Axis Labels & Ticks
- Rotate x-axis tick labels 45 degrees (`rotation=45, ha='right'`).
- Rotate y-axis label 90 degrees (default matplotlib behavior — verify it is not set to 0).

## Margins
- Always add margins: use `ax.margins()` or `plt.subplots_adjust()` — add 0.5 to 2 units of padding depending on plot size.

## Spines
- Remove top and right spines on every axis:
```python
ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
```

## Annotations on Plot Entities
Before annotating dots (or other plot entities) with text, assess the local density of the data:
- **Sparse / well-separated dots**: annotate all relevant entities directly next to each point.
- **Moderate density**: annotate only the most important entities (e.g. top N by significance, size, or rank). Use `arrowprops=dict(arrowstyle='->', color='gray', lw=0.8)` to connect label to point when labels need to be offset to avoid overlap.
- **High density / overlapping dots**: do not annotate individual dots with text. Instead:
  - Use a color scale or categorical color to encode the label information visually.
  - Or annotate only a small set (≤5) of the most extreme or biologically relevant points, with arrows and sufficient offset so labels are outside the dense region.
- Always set `clip_on=False` on annotations that may extend outside the axes.
- Prefer offsetting labels **away from the dense region** — e.g. if dots cluster in the lower-left, place labels to the upper-right.
- **Label length**: if the annotation text exceeds ~20 characters, skip text annotation entirely and rely on color encoding to identify the entity. Add a clear legend that maps colors to the full names.
