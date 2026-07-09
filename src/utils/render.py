import json
import re
from datetime import datetime
from pathlib import Path

ASSETS_DIR = Path(__file__).resolve().parent / "render_assets"
OUTPUT_DIR = Path(__file__).resolve().parent.parent.parent / "outputs"

DOT_BLOCK_RE = re.compile(r"```dot\s*\n(.*?)```", re.DOTALL)

TEMPLATE = """<!doctype html>
<html>
<head>
<meta charset="utf-8">
<title>DGG Conversion Result</title>
<style>
{katex_css}
body {{ font-family: Georgia, serif; max-width: 52rem; margin: 2rem auto; padding: 0 1rem; line-height: 1.6; color: #222; }}
@media (prefers-color-scheme: dark) {{ body {{ color: #e8e6e0; background: #1c1b19; }} }}
h2 {{ font-family: -apple-system, "Segoe UI", system-ui, sans-serif; font-size: 0.8rem; text-transform: uppercase;
      letter-spacing: 0.08em; color: #888; margin-top: 2.2rem; }}
.panel {{ border: 1px solid rgba(127,127,127,0.3); border-radius: 6px; padding: 1.2rem 1.5rem; margin-bottom: 1.5rem; overflow-x: auto; }}
.graph {{ display: flex; justify-content: center; overflow-x: auto; }}
.graph svg {{ max-width: 100%; height: auto; }}
pre {{ white-space: pre-wrap; word-break: break-word; }}
</style>
</head>
<body>
<h2>Prose / Math</h2>
<div class="panel" id="prose"></div>

{graph_sections}

<script>{katex_js}</script>
<script>{auto_render_js}</script>
<script>{viz_js}</script>
<script>
const proseText = {prose_json};
document.getElementById("prose").innerHTML = proseText
  .replace(/</g, "&lt;")
  .split(/\\n{{2,}}/)
  .map(p => "<p>" + p.replace(/\\n/g, "<br>") + "</p>")
  .join("");
renderMathInElement(document.getElementById("prose"), {{
  delimiters: [
    {{left: "$$", right: "$$", display: true}},
    {{left: "\\\\[", right: "\\\\]", display: true}},
    {{left: "$", right: "$", display: false}},
    {{left: "\\\\(", right: "\\\\)", display: false}}
  ],
  throwOnError: false
}});

const graphs = {graphs_json};
Viz.instance().then(viz => {{
  graphs.forEach((dot, i) => {{
    const el = document.getElementById("graph-" + i);
    try {{
      el.appendChild(viz.renderSVGElement(dot));
    }} catch (e) {{
      el.innerHTML = "<pre>Graph render failed: " + e.message + "</pre><pre>" + dot.replace(/</g, "&lt;") + "</pre>";
    }}
  }});
}});
</script>
</body>
</html>
"""


def _extract_dot_blocks(text: str):
    blocks = [m.strip() for m in DOT_BLOCK_RE.findall(text)]
    prose = DOT_BLOCK_RE.sub("", text).strip()
    return prose, blocks


def render_result_to_html(text: str, label: str = "result") -> Path:
    """Renders agent output (prose/LaTeX + optional ```dot graph blocks) to a
    self-contained HTML file and returns its path."""
    prose, graphs = _extract_dot_blocks(text)

    graph_sections = "\n".join(
        f'<h2>Graph {i + 1}</h2><div class="panel graph" id="graph-{i}"></div>'
        for i in range(len(graphs))
    )

    html = TEMPLATE.format(
        katex_css=(ASSETS_DIR / "katex.inline.css").read_text(encoding="utf-8"),
        katex_js=(ASSETS_DIR / "katex.min.js").read_text(encoding="utf-8"),
        auto_render_js=(ASSETS_DIR / "auto-render.min.js").read_text(encoding="utf-8"),
        viz_js=(ASSETS_DIR / "viz-global.js").read_text(encoding="utf-8"),
        prose_json=json.dumps(prose),
        graphs_json=json.dumps(graphs),
        graph_sections=graph_sections,
    )

    OUTPUT_DIR.mkdir(exist_ok=True)
    out_path = OUTPUT_DIR / f"{label}_{datetime.now():%Y%m%d_%H%M%S}.html"
    out_path.write_text(html, encoding="utf-8")
    return out_path
