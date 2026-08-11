#!/usr/bin/env python3
"""Deterministic renderer for the fixed-structure review Artifact required by
ciim_agentic.md's "Interact with user using Artifact" section: one card per
`##` section of a design.md/findings.md, its content copied verbatim (rendered
markdown, not a paraphrase), each followed by a Comment textarea, plus one
page-level "Overall" comment card and one page-level "Compile comments"
button. Structure is fixed by code; content comes straight from the file.

Diagrams are ```graph <id>``` placeholders (see docs/design_graphs.md), backed by a sibling
<basename>.graphs.js file next to the source .md, rendered client-side with Cytoscape.js
(draggable nodes, pan/zoom, dagre layout) instead of mermaid.

Usage:
    python3 render_review_artifact.py <design.md> <output.html> [--title "..."]

--title overrides the auto-derived title (first `#` line, else the filename).

Run `python3 render_review_artifact.py --self-test` to verify the template.
"""
import html
import re
import sys
from pathlib import Path

import markdown

TEMPLATE = """<meta charset="utf-8">
<title>{title}</title>
<script src="https://cdn.jsdelivr.net/npm/cytoscape@3/dist/cytoscape.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/dagre@0.8.5/dist/dagre.min.js"></script>
<script src="https://cdn.jsdelivr.net/npm/cytoscape-dagre@2/cytoscape-dagre.js"></script>
<style>
  .cy-graph {{ width: 100%; height: 420px; background: var(--surface); border: 1px solid var(--border);
    border-radius: 4px; margin: 0.6rem 0; }}
  :root {{
    --bg: #f5f7f8; --surface: #ffffff; --text: #1a232a; --text-muted: #5c6b74;
    --text-faint: #8895a0; --accent: #276866; --accent-soft: #e4eeec;
    --border: #dbe2e5; --border-strong: #c2ccd0; --focus: #1c8f89;
    --sans: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Arial, sans-serif;
    --serif: ui-serif, Georgia, "Iowan Old Style", Palatino, serif;
    --mono: ui-monospace, "SF Mono", "Roboto Mono", Menlo, Consolas, monospace;
  }}
  @media (prefers-color-scheme: dark) {{
    :root {{ --bg:#12171a; --surface:#1a2124; --text:#e7ecee; --text-muted:#a3b0b6;
      --text-faint:#71828a; --accent:#6ec2bd; --accent-soft:#1e2f2e;
      --border:#2c373b; --border-strong:#3b484d; --focus:#6ec2bd; }}
  }}
  :root[data-theme="dark"] {{ --bg:#12171a; --surface:#1a2124; --text:#e7ecee; --text-muted:#a3b0b6;
    --text-faint:#71828a; --accent:#6ec2bd; --accent-soft:#1e2f2e;
    --border:#2c373b; --border-strong:#3b484d; --focus:#6ec2bd; }}
  :root[data-theme="light"] {{ --bg:#f5f7f8; --surface:#ffffff; --text:#1a232a; --text-muted:#5c6b74;
    --text-faint:#8895a0; --accent:#276866; --accent-soft:#e4eeec;
    --border:#dbe2e5; --border-strong:#c2ccd0; --focus:#1c8f89; }}

  * {{ box-sizing: border-box; }}
  body {{ background: var(--bg); color: var(--text); font-family: var(--sans); line-height: 1.5; margin: 0; }}
  .page {{ max-width: 860px; margin: 0 auto; padding: 3.5rem 1.5rem 6rem; }}
  header.masthead {{ margin-bottom: 2.5rem; padding-bottom: 1.5rem; border-bottom: 1px solid var(--border); }}
  .eyebrow {{ font-family: var(--mono); font-size: 0.72rem; letter-spacing: 0.09em; text-transform: uppercase;
    color: var(--accent); margin-bottom: 0.9rem; }}
  h1 {{ font-family: var(--serif); font-weight: 500; font-size: 1.95rem; line-height: 1.2; margin: 0 0 0.7rem;
    text-wrap: balance; }}
  .path-line {{ font-family: var(--mono); font-size: 0.78rem; color: var(--text-faint); word-break: break-all; }}
  .cards {{ display: flex; flex-direction: column; gap: 1rem; }}
  .card {{ background: var(--surface); border: 1px solid var(--border); border-left: 3px solid var(--accent);
    border-radius: 3px; padding: 1.5rem 1.6rem 1.6rem; }}
  .card.overall {{ border-left-color: var(--text-faint); background: var(--accent-soft); }}
  .card h2 {{ font-family: var(--serif); font-weight: 500; font-size: 1.12rem; margin: 0 0 0.7rem; }}
  .section-body {{ font-size: 0.94rem; }}
  .section-body :first-child {{ margin-top: 0; }}
  .section-body :last-child {{ margin-bottom: 0; }}
  .section-body img {{ max-width: 100%; height: auto; }}
  .section-body table {{ display: block; overflow-x: auto; border-collapse: collapse; font-size: 0.88rem; }}
  .section-body th, .section-body td {{ border: 1px solid var(--border); padding: 0.35rem 0.6rem; text-align: left; }}
  .section-body code {{ background: var(--bg); border-radius: 2px; padding: 0.05rem 0.3rem; font-family: var(--mono); font-size: 0.85em; }}
  .section-body pre {{ overflow-x: auto; background: var(--bg); padding: 0.7rem; border-radius: 3px; }}
  .section-body a {{ color: var(--accent); }}
  .field-label {{ font-family: var(--mono); font-size: 0.66rem; letter-spacing: 0.08em; text-transform: uppercase;
    color: var(--text-faint); margin: 0.95rem 0 0.35rem; }}
  textarea.comment {{ width: 100%; min-height: 3.4rem; resize: vertical; background: var(--bg);
    border: 1px solid var(--border); border-radius: 2px; color: var(--text); font-family: var(--sans);
    font-size: 0.88rem; padding: 0.6rem 0.7rem; }}
  textarea.comment:focus {{ outline: 2px solid var(--focus); outline-offset: 1px; border-color: var(--focus); }}
  .compile-bar {{ position: sticky; bottom: 1.1rem; display: flex; justify-content: center; margin-top: 2.5rem; }}
  .compile-inner {{ background: var(--surface); border: 1px solid var(--border-strong); border-radius: 4px;
    box-shadow: 0 6px 20px -6px rgba(0,0,0,0.25); padding: 0.7rem 0.9rem; display: flex; align-items: center; gap: 0.8rem; }}
  #compileBtn {{ background: var(--accent); color: var(--surface); border: none; font-weight: 600; font-size: 0.88rem;
    padding: 0.6rem 1.15rem; border-radius: 3px; cursor: pointer; }}
  #compileBtn:hover {{ filter: brightness(1.08); }}
  #compileBtn:focus-visible {{ outline: 2px solid var(--focus); outline-offset: 2px; }}
  #compileStatus {{ font-family: var(--mono); font-size: 0.78rem; color: var(--text-muted); min-width: 11rem; }}
  .compile-output {{ margin-top: 1.2rem; background: var(--surface); border: 1px solid var(--border);
    border-radius: 3px; padding: 1rem 1.1rem; font-family: var(--mono); font-size: 0.82rem;
    white-space: pre-wrap; word-break: break-word; color: var(--text); }}
  footer.note {{ margin-top: 2.5rem; font-size: 0.82rem; color: var(--text-faint); border-top: 1px solid var(--border);
    padding-top: 1.2rem; }}
</style>
<div class="page">
  <header class="masthead">
    <div class="eyebrow">{eyebrow}</div>
    <h1>{title_h1}</h1>
    {path_line_html}
  </header>
  <div class="cards">
{cards_html}
    <div class="card overall">
      <h2>Overall</h2>
      <p class="field-label">Comment</p>
      <textarea class="comment" data-step="Overall" placeholder="General comments not tied to one section"></textarea>
    </div>
  </div>
  <div class="compile-bar">
    <div class="compile-inner">
      <button id="compileBtn" type="button">Compile comments</button>
      <span id="compileStatus">only non-empty comments are copied</span>
    </div>
  </div>
  <pre id="compileOutput" class="compile-output" style="display:none"></pre>
  <footer class="note">No comment is sent automatically. Paste the compiled text back into the conversation once you've reviewed every card.</footer>
</div>
<script>
window.DESIGN_GRAPHS = window.DESIGN_GRAPHS || {{}};
{graphs_js}
</script>
<script>
  document.addEventListener('DOMContentLoaded', function () {{
    cytoscape.use(cytoscapeDagre);
    document.querySelectorAll('.cy-graph').forEach(function (el) {{
      var gid = el.getAttribute('data-graph-id');
      var g = window.DESIGN_GRAPHS[gid];
      if (!g) {{ el.textContent = 'graph not found: ' + gid; return; }}
      var elements = [];
      (g.nodes || []).forEach(function (n) {{
        elements.push({{ data: {{ id: n.id, label: n.label, type: n.type || '', parent: n.parent }} }});
      }});
      (g.edges || []).forEach(function (e, i) {{
        elements.push({{ data: {{ id: 'e' + i, source: e.from, target: e.to, kind: e.kind || 'flow', label: e.label || '' }} }});
      }});
      cytoscape({{
        container: el,
        elements: elements,
        layout: {{ name: 'dagre', rankDir: 'TB', nodeSep: 24, rankSep: 46 }},
        wheelSensitivity: 0.2,
        style: [
          {{ selector: 'node', style: {{ 'label': 'data(label)', 'text-wrap': 'wrap', 'text-max-width': '120px',
            'font-size': '11px', 'text-valign': 'center', 'text-halign': 'center', 'padding': '8px',
            'width': 'label', 'height': 'label', 'shape': 'round-rectangle',
            'background-color': '#4C78A8', 'color': '#fff' }} }},
          {{ selector: 'node[type="decision"]', style: {{ 'background-color': '#F2B701', 'color': '#000', 'shape': 'diamond' }} }},
          {{ selector: 'node[type="dataset"]', style: {{ 'background-color': '#54A24B', 'color': '#fff', 'shape': 'round-rectangle' }} }},
          {{ selector: 'node[type="method"]', style: {{ 'background-color': '#B07AA1', 'color': '#fff', 'shape': 'hexagon' }} }},
          {{ selector: 'node[type="stop"]', style: {{ 'background-color': '#E45756', 'color': '#fff' }} }},
          {{ selector: 'node:parent', style: {{ 'background-color': '#8895a0', 'background-opacity': 0.12,
            'border-width': 1, 'border-color': '#8895a0', 'shape': 'round-rectangle', 'text-valign': 'top',
            'font-weight': 'bold', 'padding': '18px' }} }},
          {{ selector: 'edge', style: {{ 'width': 1.5, 'line-color': '#8895a0', 'target-arrow-color': '#8895a0',
            'target-arrow-shape': 'triangle', 'curve-style': 'bezier', 'label': 'data(label)', 'font-size': '10px',
            'color': 'var(--text-muted)' }} }},
          {{ selector: 'edge[kind="flow"]', style: {{ 'line-color': '#4C78A8', 'target-arrow-color': '#4C78A8' }} }},
          {{ selector: 'edge[kind="data"]', style: {{ 'line-style': 'dashed', 'line-color': '#54A24B', 'target-arrow-color': '#54A24B' }} }},
        ],
      }});
      var legend = document.createElement('div');
      legend.style.cssText = 'font-size:11px;margin-top:4px;color:var(--text-muted)';
      legend.innerHTML = '<span style="color:#4C78A8">&#8212;&#9658;</span> flow (logical order) &nbsp; '
        + '<span style="color:#54A24B">&#8901;&#8901;&#9658;</span> data (input/output)';
      el.insertAdjacentElement('afterend', legend);
    }});
  }});
  document.getElementById('compileBtn').addEventListener('click', function () {{
    var areas = document.querySelectorAll('textarea.comment');
    var lines = [];
    areas.forEach(function (ta) {{
      var val = ta.value.trim();
      if (val) lines.push('[' + ta.getAttribute('data-step') + ']\\n' + val);
    }});
    var status = document.getElementById('compileStatus');
    var output = document.getElementById('compileOutput');
    if (lines.length === 0) {{
      status.textContent = 'no comments to compile';
      output.style.display = 'none';
      return;
    }}
    var text = lines.join('\\n\\n');
    output.textContent = text;
    output.style.display = 'block';
    navigator.clipboard.writeText(text).then(function () {{
      status.textContent = 'copied ' + lines.length + ' comment' + (lines.length > 1 ? 's' : '') + ' to clipboard (also shown below)';
    }}, function () {{
      status.textContent = 'shown below — select and copy manually';
    }});
  }});
</script>
"""

CARD_TEMPLATE = """    <div class="card">
      <h2>{heading}</h2>
      <div class="section-body">{body_html}</div>
      <p class="field-label">Comment</p>
      <textarea class="comment" data-step="{step_attr}" placeholder=""></textarea>
    </div>"""

MD_EXTENSIONS = ["tables", "sane_lists", "fenced_code"]
GRAPH_RE = re.compile(r"```graph\n(.*?)```", re.DOTALL)


LIST_ITEM_RE = re.compile(r"^\s*(?:[-*+]|\d+\.)\s")


def ensure_blank_before_lists(text: str) -> str:
    """python-markdown (unlike CommonMark) won't start a list that isn't preceded
    by a blank line -- it gets swallowed into the prior paragraph instead."""
    lines = text.split("\n")
    out = []
    for line in lines:
        if LIST_ITEM_RE.match(line) and out and out[-1].strip() and not LIST_ITEM_RE.match(out[-1]):
            out.append("")
        out.append(line)
    return "\n".join(out)


def render_body_html(body: str, counter: list) -> str:
    """Markdown -> HTML, with ```graph <id>``` fences pulled out and replaced by a
    placeholder <div> that Cytoscape.js hydrates client-side from window.DESIGN_GRAPHS."""
    placeholders = []

    def stash(m):
        placeholders.append(m.group(1).strip())
        return f"\x00GRAPH{len(placeholders) - 1}\x00"

    stripped = ensure_blank_before_lists(GRAPH_RE.sub(stash, body))
    out = markdown.markdown(html.escape(stripped, quote=False), extensions=MD_EXTENSIONS) if stripped.strip() else ""
    for i, graph_id in enumerate(placeholders):
        counter[0] += 1
        div_html = f'<div class="cy-graph" id="cy-{counter[0]}" data-graph-id="{html.escape(graph_id, quote=True)}"></div>'
        out = re.sub(rf"<p>\x00GRAPH{i}\x00</p>|\x00GRAPH{i}\x00", div_html, out)
    return out


def split_sections(md_text: str):
    """Split on top-level `## ` headers. Returns (preamble, [(heading, body), ...])."""
    parts = re.split(r"(?m)^## (.+)$", md_text)
    preamble = parts[0].strip()
    sections = []
    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1] if i + 1 < len(parts) else ""
        sections.append((heading, body.strip()))
    return preamble, sections


def derive_title(preamble: str, fallback: str) -> str:
    m = re.search(r"(?m)^#\s+(.+)$", preamble)
    if m:
        return m.group(1).strip()
    m = re.search(r"(?m)^\S.*$", preamble)
    if m:
        return m.group(0).strip()
    return fallback


def render(md_text: str, source_path: str, title: str = None, graphs_js: str = None) -> str:
    preamble, sections = split_sections(md_text)
    if not sections:
        raise ValueError("no '## ' sections found in the input markdown")

    resolved_title = title or derive_title(preamble, source_path)

    counter = [0]
    cards = []
    for heading, body in sections:
        body_html = render_body_html(body, counter) if body else ""
        cards.append(
            CARD_TEMPLATE.format(
                heading=html.escape(heading),
                body_html=body_html,
                step_attr=html.escape(heading, quote=True),
            )
        )

    return TEMPLATE.format(
        title=html.escape(resolved_title),
        eyebrow="Design review · agentic_immunology",
        title_h1=html.escape(resolved_title),
        path_line_html=f'<p class="path-line">{html.escape(source_path)}</p>',
        cards_html="\n".join(cards),
        graphs_js=graphs_js or "",
    )


def main():
    if len(sys.argv) == 2 and sys.argv[1] == "--self-test":
        _self_test()
        return
    args = [a for a in sys.argv[1:] if not a.startswith("--title=")]
    title_arg = next((a.split("=", 1)[1] for a in sys.argv[1:] if a.startswith("--title=")), None)
    if len(args) != 2:
        print("usage: render_review_artifact.py <design.md> <output.html> [--title=...]", file=sys.stderr)
        sys.exit(1)
    src_path, out_path = args
    src = Path(src_path)
    with open(src_path, encoding="utf-8") as f:
        md_text = f.read()
    graphs_path = src.with_name(src.stem + ".graphs.js")
    graphs_js = graphs_path.read_text(encoding="utf-8") if graphs_path.exists() else None
    html_out = render(md_text, src_path, title=title_arg, graphs_js=graphs_js)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(html_out)
    print(f"wrote {out_path}")
    if not graphs_path.exists() and GRAPH_RE.search(md_text):
        print(f"warning: {src_path} has ```graph placeholders but {graphs_path} does not exist", file=sys.stderr)


def _self_test():
    demo = (
        "# Study Design: Demo\n\n"
        "## Literature-derived design inputs\n"
        "Some *markdown* with a <script> tag and a [link](https://example.com).\n\n"
        "## Execution plan\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "```graph\nphase0\n```\n\n"
        "## Limitations\n"
        "- one\n- two\n\n"
        "ISSUES:\n- no blank line before this list\n- second item\n"
        "\n## Overview\n"
        "```graph\noverview\n```\n"
    )
    demo_graphs_js = (
        "window.DESIGN_GRAPHS.overview = { nodes: [{ id: 'P0', label: 'Phase 1', type: 'step' }], edges: [] };\n"
        "window.DESIGN_GRAPHS.phase0 = { nodes: [{ id: 'S1', label: 'Step 1', type: 'step' }], edges: [] };\n"
    )
    out = render(demo, "/tmp/design.md", graphs_js=demo_graphs_js)
    assert '<meta charset="utf-8">' in out, "must declare utf-8 charset so em-dashes etc. render correctly"
    assert 'id="compileOutput"' in out, "compiled comments must have a visible on-page output element"
    assert 'class="cy-graph" id="cy-1" data-graph-id="phase0"' in out, "graph placeholder must survive as a cy-graph div, in document order"
    assert 'class="cy-graph" id="cy-2" data-graph-id="overview"' in out, "second placeholder must get the next counter value"
    assert "cytoscape-dagre" in out and "cytoscape.min.js" in out, "cytoscape + dagre layout must be loaded"
    assert "cytoscape.use(cytoscapeDagre)" in out, "dagre layout must be registered with cytoscape"
    assert demo_graphs_js.strip() in out, "sibling .graphs.js content must be inlined verbatim"
    assert "mermaid" not in out.lower(), "mermaid must be fully retired from the render pipeline"
    n_cards = out.count('<div class="card">') + out.count('<div class="card overall">')
    assert n_cards == 5, "expected one card per section plus the overall card"
    assert out.count('<textarea class="comment"') == 5, "expected one textarea per card"
    assert out.count('id="compileBtn"') == 1, "expected exactly one compile button"
    assert "sendPrompt" not in out, "must not auto-send comments"
    assert "&lt;script&gt;" in out, "section content must be HTML-escaped, not raw HTML"
    assert '<table>' in out, "markdown tables must render"
    assert 'data-step="Limitations"' in out
    assert "<li>no blank line before this list</li>" in out, "list must render as <li> even with no blank line before it"
    assert 'data-step="Overall"' in out
    assert "Study Design: Demo" in out, "title should be derived from the leading # header"

    out_no_graphs = render(demo, "/tmp/design.md")
    assert 'data-graph-id="phase0"' in out_no_graphs, "placeholder still renders even with no graphs.js supplied"
    assert "window.DESIGN_GRAPHS = window.DESIGN_GRAPHS || {};\n\n" in out_no_graphs, "empty graphs block must not error"

    try:
        render("no headers here", "/tmp/x.md")
        raise AssertionError("markdown with no '## ' sections should raise")
    except ValueError:
        pass
    print("ok")


if __name__ == "__main__":
    main()
