#!/usr/bin/env python3
"""Deterministic renderer for the fixed-structure review Artifact required by
ciim_agentic.md's "Interact with user using Artifact" section: one card per
`##` section of a design.md/report.md, its content copied verbatim (rendered
markdown, not a paraphrase), each followed by a Comment textarea, plus one
page-level "Overall" comment card and one page-level "Compile comments"
button. Structure is fixed by code; content comes straight from the file.

Usage:
    python3 render_review_artifact.py <design.md> <output.html> [--title "..."]

--title overrides the auto-derived title (first `#` line, else the filename).

Run `python3 render_review_artifact.py --self-test` to verify the template.
"""
import html
import re
import sys

import markdown

TEMPLATE = """<title>{title}</title>
<style>
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
  <footer class="note">No comment is sent automatically. Paste the compiled text back into the conversation once you've reviewed every card.</footer>
</div>
<script>
  document.getElementById('compileBtn').addEventListener('click', function () {{
    var areas = document.querySelectorAll('textarea.comment');
    var lines = [];
    areas.forEach(function (ta) {{
      var val = ta.value.trim();
      if (val) lines.push(ta.getAttribute('data-step') + ': ' + val);
    }});
    var status = document.getElementById('compileStatus');
    if (lines.length === 0) {{ status.textContent = 'no comments to compile'; return; }}
    navigator.clipboard.writeText(lines.join('\\n')).then(function () {{
      status.textContent = 'copied ' + lines.length + ' comment' + (lines.length > 1 ? 's' : '') + ' to clipboard';
    }}, function () {{
      status.textContent = 'copy failed — select and copy manually';
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


def render(md_text: str, source_path: str, title: str = None) -> str:
    preamble, sections = split_sections(md_text)
    if not sections:
        raise ValueError("no '## ' sections found in the input markdown")

    resolved_title = title or derive_title(preamble, source_path)

    cards = []
    for heading, body in sections:
        body_html = markdown.markdown(html.escape(body, quote=False), extensions=MD_EXTENSIONS) if body else ""
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
    with open(src_path) as f:
        md_text = f.read()
    html_out = render(md_text, src_path, title=title_arg)
    with open(out_path, "w") as f:
        f.write(html_out)
    print(f"wrote {out_path}")


def _self_test():
    demo = (
        "# Study Design: Demo\n\n"
        "## Literature-derived design inputs\n"
        "Some *markdown* with a <script> tag and a [link](https://example.com).\n\n"
        "## Execution plan\n"
        "| a | b |\n|---|---|\n| 1 | 2 |\n\n"
        "## Limitations\n"
        "- one\n- two\n"
    )
    out = render(demo, "/tmp/design.md")
    n_cards = out.count('<div class="card">') + out.count('<div class="card overall">')
    assert n_cards == 4, "expected one card per section plus the overall card"
    assert out.count('<textarea class="comment"') == 4, "expected one textarea per card"
    assert out.count('id="compileBtn"') == 1, "expected exactly one compile button"
    assert "sendPrompt" not in out, "must not auto-send comments"
    assert "&lt;script&gt;" in out, "section content must be HTML-escaped, not raw HTML"
    assert '<table>' in out, "markdown tables must render"
    assert 'data-step="Limitations"' in out
    assert 'data-step="Overall"' in out
    assert "Study Design: Demo" in out, "title should be derived from the leading # header"
    try:
        render("no headers here", "/tmp/x.md")
        raise AssertionError("markdown with no '## ' sections should raise")
    except ValueError:
        pass
    print("ok")


if __name__ == "__main__":
    main()
