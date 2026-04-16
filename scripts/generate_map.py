#!/usr/bin/env python3
"""
generate_map.py
---------------
Reads map_schema.yaml and generates agentic_map.html —
an interactive D3.js force-directed graph of the full agentic ecosystem.

To change the graph:  edit map_schema.yaml (no code changes needed).
To add a new dataset: add a node under the right category in map_schema.yaml.
To run:               python3 scripts/generate_map.py

If you add a brand-new data source to the markdown files and want to
refresh map_schema.yaml from scratch, run:
    python3 scripts/build_map_schema.py
then edit map_schema.yaml to refine, then run generate_map.py.
"""

import json
import yaml
from pathlib import Path

BASE   = Path('/vol/projects/CIIM/agentic_central')
SCHEMA = BASE / 'map_schema.yaml'
OUTPUT = BASE / 'agentic_map.html'

# ── NODE DEFAULTS ──────────────────────────────────────────────────────────────
# type → (radius, default_type_name)
TYPE_R = {
    'core':          44,
    'category':      30,
    'tool_group':    20,
    'tool':          15,
    'tool_ciim':     15,
    'data_cat':      20,
    'data':          13,
    'sumstat_group': 18,
    'sumstat':       13,
    'knowhow':       15,
    'image':         17,
    'data_file':      9,
    'func':           9,
}

# infer node type from its position in the hierarchy + explicit 'type' field
def infer_type(node: dict, parent_type: str) -> str:
    if 'type' in node:
        return node['type']
    if parent_type == 'category':
        return 'tool_group' if 'tool' in node.get('id','').lower() else 'data_cat'
    if parent_type in ('tool_group',):
        return 'tool'
    if parent_type in ('tool', 'tool_ciim'):
        return 'func'
    if parent_type == 'data_cat':
        return 'data'
    if parent_type == 'data':
        return 'data_file'
    if parent_type == 'sumstat_group':
        return 'sumstat'
    return 'data'


# ── GRAPH BUILDER ──────────────────────────────────────────────────────────────

def build_graph(schema: dict) -> tuple:
    nodes, links = [], []

    def add_node(**kwargs):
        nodes.append(kwargs)

    def add_link(source, target, ltype='default'):
        links.append({'source': source, 'target': target, 'type': ltype})

    # ── Core node
    core = schema['core']
    add_node(id=core['id'], label=core['label'], type='core',
             r=TYPE_R['core'], desc=core.get('desc', ''))
    add_link(core['id'], 'CAT_TOOLS', 'category')   # explicit top-level links below

    def walk(node: dict, parent_id: str, parent_type: str, depth: int = 0):
        """
        Recursively walk the schema tree.

        Distinction between structural and expandable children:
        - A child is STRUCTURAL (rendered as its own graph node) if it has an 'id' field.
        - A child is an EXPANDABLE LEAF (hidden behind + button) if it has NO 'id' field.
          These are anonymous items like {label, desc} — e.g. individual .h5ad files,
          individual functions under a tool module.
        """
        ntype = infer_type(node, parent_type)
        nid   = node.get('id', f'AUTO_{parent_id}_{depth}')
        label = node.get('label', node.get('pretty', nid))
        desc  = node.get('desc', '')
        r     = TYPE_R.get(ntype, 11)

        children = node.get('children', [])

        # Split: structural children have 'id', expandable leaves do not
        structural_children  = [c for c in children if c.get('id')]
        expandable_children  = [c for c in children if not c.get('id')]

        # Build child summary for desc if children exist
        if expandable_children:
            preview = ', '.join(c.get('label', c.get('pretty', '')) for c in expandable_children[:4])
            if len(expandable_children) > 4:
                preview += f' +{len(expandable_children)-4} more'
            child_count_note = f"<br><span style='color:#8b949e;font-size:11px'>({len(expandable_children)} items: {preview})</span>"
            # Attach expandable children list to node for JS
            js_children = [
                {'label': c.get('label', c.get('pretty', '')), 'desc': c.get('desc', '')}
                for c in expandable_children
            ]
        else:
            child_count_note = ''
            js_children = []

        # nfuncs badge ring (for tool nodes) = total expandable children
        nfuncs = len(js_children) if ntype in ('tool', 'tool_ciim') else 0

        add_node(id=nid, label=label, type=ntype, r=r,
                 desc=desc + child_count_note,
                 **({'children': js_children} if js_children else {}),
                 **({'nfuncs': nfuncs} if nfuncs else {}),
                 **({'module': node['module']} if 'module' in node else {}))

        # Link from parent
        ltype = 'category' if parent_type in ('core', 'category') else 'default'
        add_link(parent_id, nid, ltype)

        # Recurse into structural (non-leaf) children
        for child in structural_children:
            walk(child, nid, ntype, depth + 1)

    # Walk all top-level categories
    for cat in schema['categories']:
        ntype = 'category'
        nid   = cat['id']
        add_node(id=nid, label=cat['label'], type=ntype,
                 r=TYPE_R['category'], desc=cat.get('desc', ''))
        add_link(core['id'], nid, 'category')

        for child in cat.get('children', []):
            walk(child, nid, ntype)

    return nodes, links


# ── HTML TEMPLATE ──────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Agentic Ecosystem Map</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }

  body {
    --bg:           #0d1117;
    --fg:           #e6edf3;
    --panel-bg:     rgba(22,27,34,0.95);
    --panel-bg2:    rgba(22,27,34,0.97);
    --border:       #30363d;
    --muted:        #8b949e;
    --desc-fg:      #c9d1d9;
    --input-bg:     #21262d;
    --btn-bg:       #21262d;
    --btn-hover:    #30363d;
    --title-color:  #58a6ff;
    --node-label:   #e6edf3;
    --node-core-fg: #0d1117;
    --shadow:       rgba(0,0,0,0.6);
  }
  body.light {
    --bg:           #ffffff;
    --fg:           #1f2328;
    --panel-bg:     rgba(246,248,250,0.97);
    --panel-bg2:    rgba(246,248,250,0.99);
    --border:       #d0d7de;
    --muted:        #57606a;
    --desc-fg:      #424a53;
    --input-bg:     #f6f8fa;
    --btn-bg:       #f6f8fa;
    --btn-hover:    #e8ecf0;
    --title-color:  #0969da;
    --node-label:   #1f2328;
    --node-core-fg: #ffffff;
    --shadow:       rgba(0,0,0,0.15);
  }
  body {
    background: var(--bg); font-family: 'Segoe UI', system-ui, sans-serif;
    overflow: hidden; color: var(--fg); transition: background 0.3s, color 0.3s;
  }
  #title {
    position: absolute; top: 16px; left: 50%; transform: translateX(-50%);
    font-size: 17px; font-weight: 700; color: var(--title-color);
    letter-spacing: 1px; pointer-events: none; z-index: 10;
    text-shadow: 0 0 20px rgba(88,166,255,0.4);
  }
  #legend {
    position: absolute; bottom: 18px; left: 18px;
    background: var(--panel-bg); border: 1px solid var(--border);
    border-radius: 10px; padding: 12px 16px; font-size: 12px; z-index: 10;
    color: var(--fg); transition: background 0.3s, border-color 0.3s;
  }
  #legend h4 { color: var(--muted); margin-bottom: 8px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
  .legend-item { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
  .legend-dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
  #tooltip {
    position: absolute; pointer-events: none;
    background: var(--panel-bg2); border: 1px solid var(--border);
    border-radius: 8px; padding: 11px 14px;
    font-size: 12px; max-width: 320px; line-height: 1.55;
    z-index: 100; display: none;
    box-shadow: 0 6px 24px var(--shadow);
    color: var(--fg); transition: background 0.3s, border-color 0.3s;
  }
  #tooltip .tt-title { font-weight: 700; font-size: 13px; margin-bottom: 3px; }
  #tooltip .tt-badge { display: inline-block; font-size: 10px; padding: 1px 7px;
    border-radius: 10px; margin-bottom: 6px; font-weight: 600; }
  #tooltip .tt-desc  { color: var(--desc-fg); }
  #controls { position: absolute; top: 16px; right: 16px; display: flex; gap: 8px; z-index: 10; }
  #search-wrap { position: absolute; top: 16px; left: 16px; z-index: 10; }
  #search {
    background: var(--input-bg); border: 1px solid var(--border); color: var(--fg);
    padding: 6px 12px; border-radius: 6px; font-size: 12px; width: 180px;
    outline: none; transition: background 0.3s, border-color 0.3s, color 0.3s;
  }
  #search::placeholder { color: var(--muted); }
  button {
    background: var(--btn-bg); border: 1px solid var(--border); color: var(--fg);
    padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;
    transition: background 0.2s;
  }
  button:hover { background: var(--btn-hover); }
  svg { width: 100vw; height: 100vh; }
  .node { cursor: grab; }
  .node:active { cursor: grabbing; }
  .node circle { stroke-width: 2px; }
  .node text { pointer-events: none; user-select: none; }
  .link { stroke-opacity: 0.3; }
  .link-category { stroke-opacity: 0.55; }
  .node.dimmed circle { opacity: 0.15; }
  .node.dimmed text  { opacity: 0.1; }
  .link.dimmed { opacity: 0.05; }
  .expand-btn circle { cursor: pointer; }
  .expand-btn text { cursor: pointer; pointer-events: none; font-size: 11px; font-weight: 700; fill: #fff; }
  .node-leaf text { font-size: 8px; }
</style>
</head>
<body>
<div id="title">🧬 Agentic Ecosystem Map</div>
<div id="search-wrap"><input id="search" type="text" placeholder="🔍 Search nodes…"></div>
<div id="tooltip"></div>
<div id="controls">
  <button onclick="resetZoom()">⟳ Reset</button>
  <button onclick="toggleLabels()">🏷 Labels</button>
  <button onclick="relaxAll()">💫 Shake</button>
  <button id="theme-btn" onclick="toggleTheme()">☀️ Light</button>
</div>
<div id="legend">
  <h4>Node Types</h4>
  <div class="legend-item"><div class="legend-dot" style="background:#ff7b72"></div><span>LLM Core</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#79c0ff"></div><span>Category</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#56d364"></div><span>biomni Tool</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#3fb950"></div><span>CIIM Tool</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#ffa657"></div><span>Data Category</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#e3b341"></div><span>Dataset / Group</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#e879a0"></div><span>Stats Module</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#f778ba"></div><span>Summary Stats</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#d2a8ff"></div><span>Know-How</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#f0883e"></div><span>Singularity Image</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#c9a227"></div><span>Expanded Leaf</span></div>
  <div style="margin-top:8px;padding-top:8px;border-top:1px solid var(--border);color:var(--muted);font-size:10px">
    + badge = click to expand children
  </div>
</div>
<svg id="graph"></svg>
<script>
const NODES = __NODES__;
const LINKS = __LINKS__;

const W = window.innerWidth, H = window.innerHeight;
let showLabels = true;

const colorMap = {
  core:'#ff7b72', category:'#79c0ff', tool_group:'#a3d977',
  tool:'#56d364', tool_ciim:'#3fb950',
  data_cat:'#ffa657', data:'#e3b341',
  sumstat_group:'#e879a0', sumstat:'#f778ba',
  knowhow:'#d2a8ff', image:'#f0883e',
  func:'#3fb950', data_file:'#c9a227',
};
const strokeMap = {
  core:'#ff4444', category:'#1f6feb', tool_group:'#4a9a22',
  tool:'#238636', tool_ciim:'#196127',
  data_cat:'#d86a00', data:'#9e7500',
  sumstat_group:'#b5366d', sumstat:'#c4347a',
  knowhow:'#8b5cf6', image:'#c0622d',
  func:'#196127', data_file:'#7a6000',
};
const typeLabel = {
  core:'LLM Core', category:'Category', tool_group:'Tool Suite',
  tool:'biomni Tool', tool_ciim:'CIIM Tool',
  data_cat:'Data Category', data:'Dataset / Group',
  sumstat_group:'Stats Module', sumstat:'Summary Stats File',
  knowhow:'Know-How Guide', image:'Singularity Image',
  func:'Function', data_file:'Data File',
};

const svg = d3.select('#graph');
const g   = svg.append('g');
const zoom = d3.zoom().scaleExtent([0.1, 5])
  .on('zoom', e => g.attr('transform', e.transform));
svg.call(zoom);

const defs = svg.append('defs');
const glow = defs.append('filter').attr('id','glow');
glow.append('feGaussianBlur').attr('stdDeviation','5').attr('result','coloredBlur');
const fm = glow.append('feMerge');
fm.append('feMergeNode').attr('in','coloredBlur');
fm.append('feMergeNode').attr('in','SourceGraphic');

function linkDistance(d) {
  const tt = typeof d.target==='object' ? d.target.type : NODES.find(n=>n.id===d.target)?.type;
  if (d.type==='category') return 220;
  if (tt==='tool_group'||tt==='data_cat'||tt==='sumstat_group') return 150;
  if (tt==='tool'||tt==='tool_ciim') return 100;
  if (tt==='data') return 85;
  if (tt==='knowhow') return 120;
  if (tt==='image') return 130;
  if (tt==='sumstat') return 90;
  return 100;
}
function chargeStrength(d) {
  if (d.type==='core')       return -1800;
  if (d.type==='category')   return -800;
  if (d.type==='tool_group') return -450;
  if (d.type==='data_cat')   return -380;
  return -220;
}

const simulation = d3.forceSimulation(NODES)
  .force('link', d3.forceLink(LINKS).id(d=>d.id).distance(linkDistance).strength(0.55))
  .force('charge', d3.forceManyBody().strength(chargeStrength))
  .force('center', d3.forceCenter(W/2, H/2))
  .force('collision', d3.forceCollide().radius(d => d.r + 22));

const linkG = g.append('g');
const nodeG = g.append('g');

let allNodes = NODES.slice();
let allLinks = LINKS.slice();
const expanded = new Set();

const drag = d3.drag()
  .on('start', (e,d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
  .on('drag',  (e,d) => { d.fx=e.x; d.fy=e.y; })
  .on('end',   (e,d) => { if (!e.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; });

function updateGraph() {
  const linkSel = linkG.selectAll('line').data(allLinks, d => {
    const s = typeof d.source==='object' ? d.source.id : d.source;
    const t = typeof d.target==='object' ? d.target.id : d.target;
    return s + '→' + t;
  });
  linkSel.exit().remove();
  const linkEnter = linkSel.enter().append('line')
    .attr('class', d => 'link' + (d.type==='category' ? ' link-category' : ''))
    .attr('stroke', d => d.type==='category' ? '#79c0ff' : d.type==='leaf' ? '#3fb950' : '#484f58')
    .attr('stroke-width', d => d.type==='category' ? 2.5 : d.type==='leaf' ? 1 : 1)
    .attr('stroke-opacity', d => d.type==='leaf' ? 0.5 : null);
  linkSel.merge(linkEnter);

  const nodeSel = nodeG.selectAll('g.node').data(allNodes, d => d.id);
  nodeSel.exit().transition().duration(200).style('opacity', 0).remove();

  const nodeEnter = nodeSel.enter().append('g')
    .attr('class', d => 'node' + (['func','data_file'].includes(d.type) ? ' node-leaf' : ''))
    .call(drag)
    .on('mouseover', showTip)
    .on('mousemove', moveTip)
    .on('mouseout', hideTip);

  nodeEnter.append('circle')
    .attr('r', d => d.r)
    .attr('fill', d => (colorMap[d.type]||'#aaa') + 'cc')
    .attr('stroke', d => strokeMap[d.type]||'#555')
    .attr('filter', d => d.type==='core' ? 'url(#glow)' : null);

  // Badge ring for tool nodes (shows function count as arc)
  nodeEnter.filter(d => d.nfuncs > 0)
    .append('circle')
    .attr('r', d => d.r + 4)
    .attr('fill', 'none')
    .attr('stroke', d => colorMap[d.type])
    .attr('stroke-width', 1)
    .attr('stroke-opacity', 0.4)
    .attr('stroke-dasharray', d => {
      const circ = 2 * Math.PI * (d.r + 4);
      const filled = (d.nfuncs / 40) * circ;
      return `${Math.min(filled, circ)} ${circ}`;
    });

  // Labels
  const labelFg = getComputedStyle(document.body).getPropertyValue('--node-label').trim();
  const coreFg  = getComputedStyle(document.body).getPropertyValue('--node-core-fg').trim();
  nodeEnter.append('text')
    .attr('class','node-label')
    .attr('text-anchor','middle')
    .attr('dominant-baseline','central')
    .attr('fill', d => d.type==='core' ? coreFg : labelFg)
    .attr('font-size', d => d.type==='core' ? '13px' : d.type==='category' ? '11px' : ['func','data_file'].includes(d.type) ? '7.5px' : d.r > 18 ? '10px' : '8px')
    .attr('font-weight', d => ['core','category','tool_group'].includes(d.type) ? '700' : '500')
    .each(function(d) {
      const lines = d.label.split('\n');
      const lh = d.type==='core' ? 15 : 10;
      const el = d3.select(this);
      const offset = -(lines.length - 1) * lh / 2;
      lines.forEach((ln, i) => {
        el.append('tspan').attr('x',0).attr('dy', i===0 ? offset+'px' : lh+'px').text(ln);
      });
    });

  // Expand badge — any node that has children to expand
  nodeEnter.filter(d => d.children && d.children.length > 0)
    .append('g')
    .attr('class', 'expand-btn')
    .attr('transform', d => `translate(${d.r - 1}, ${-(d.r - 1)})`)
    .on('click', (e, d) => { e.stopPropagation(); toggleExpand(d); })
    .call(bg => {
      bg.append('circle').attr('r', 7)
        .attr('fill', d => colorMap[d.type] || '#56d364')
        .attr('stroke', d => strokeMap[d.type] || '#238636')
        .attr('stroke-width', 1.5);
      bg.append('text').attr('text-anchor','middle').attr('dominant-baseline','central').attr('dy','0.5px').text('+');
    });

  nodeSel.merge(nodeEnter);
  simulation.nodes(allNodes);
  simulation.force('link').links(allLinks);
  simulation.alpha(0.4).restart();
}

function toggleExpand(d) {
  const parentId = d.id;
  const kids     = d.children || [];
  const isTool   = d.type === 'tool' || d.type === 'tool_ciim';
  const leafType = isTool ? 'func' : 'data_file';

  if (expanded.has(parentId)) {
    expanded.delete(parentId);
    const childIds = new Set(kids.map((_, i) => `LEAF_${parentId}_${i}`));
    allNodes = allNodes.filter(n => !childIds.has(n.id));
    allLinks = allLinks.filter(l => {
      const s = typeof l.source==='object' ? l.source.id : l.source;
      const t = typeof l.target==='object' ? l.target.id : l.target;
      return !(childIds.has(s) || childIds.has(t));
    });
    nodeG.selectAll('g.node').filter(n => n.id === parentId)
      .select('.expand-btn text').text('+');
  } else {
    expanded.add(parentId);
    const angle  = (2 * Math.PI) / kids.length;
    const spread = d.r + 55;
    kids.forEach((child, i) => {
      const nid   = `LEAF_${parentId}_${i}`;
      const theta = i * angle - Math.PI / 2;
      allNodes.push({
        id:    nid,
        label: child.label || '',
        type:  leafType,
        r:     9,
        desc:  child.desc || '',
        x:     d.x + spread * Math.cos(theta),
        y:     d.y + spread * Math.sin(theta),
      });
      allLinks.push({ source: parentId, target: nid, type: 'leaf' });
    });
    nodeG.selectAll('g.node').filter(n => n.id === parentId)
      .select('.expand-btn text').text('−');
  }
  updateGraph();
}

simulation.on('tick', () => {
  linkG.selectAll('line')
    .attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
    .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
  nodeG.selectAll('g.node').attr('transform', d=>`translate(${d.x},${d.y})`);
});

function showTip(event, d) {
  const tt    = document.getElementById('tooltip');
  const color = colorMap[d.type] || '#aaa';
  const raw   = d.label.replace(/\n/g,' ');
  tt.innerHTML = `
    <div class="tt-title">${raw}</div>
    <span class="tt-badge" style="background:${color}33;color:${color}">${typeLabel[d.type]||d.type}</span>
    <div class="tt-desc">${d.desc||''}</div>
  `;
  tt.style.display = 'block';
  moveTip(event);
}
function moveTip(event) {
  const tt = document.getElementById('tooltip');
  const x  = event.pageX + 16, y = event.pageY - 12;
  tt.style.left = Math.min(x, window.innerWidth - tt.offsetWidth - 12) + 'px';
  tt.style.top  = Math.max(y, 8) + 'px';
}
function hideTip() { document.getElementById('tooltip').style.display='none'; }

const searchInput = document.getElementById('search');
searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) {
    nodeG.selectAll('g.node').classed('dimmed', false);
    linkG.selectAll('line').classed('dimmed', false);
    return;
  }
  const matched = new Set(allNodes.filter(n =>
    (n.label||'').toLowerCase().includes(q) ||
    (n.desc||'').toLowerCase().includes(q) ||
    (n.module||'').toLowerCase().includes(q)
  ).map(n => n.id));
  allLinks.forEach(l => {
    const sid = typeof l.source==='object' ? l.source.id : l.source;
    const tid = typeof l.target==='object' ? l.target.id : l.target;
    if (matched.has(tid)) matched.add(sid);
  });
  nodeG.selectAll('g.node').classed('dimmed', d => !matched.has(d.id));
  linkG.selectAll('line').classed('dimmed', d => {
    const sid = typeof d.source==='object' ? d.source.id : d.source;
    const tid = typeof d.target==='object' ? d.target.id : d.target;
    return !matched.has(sid) && !matched.has(tid);
  });
});

function resetZoom() {
  svg.transition().duration(600).call(zoom.transform, d3.zoomIdentity.translate(0,0).scale(1));
}
function toggleLabels() {
  showLabels = !showLabels;
  d3.selectAll('.node-label').style('display', showLabels ? null : 'none');
}
function relaxAll() {
  allNodes.forEach(d => { d.vx=(Math.random()-0.5)*80; d.vy=(Math.random()-0.5)*80; });
  simulation.alpha(0.5).restart();
}
function toggleTheme() {
  const isLight = document.body.classList.toggle('light');
  document.getElementById('theme-btn').textContent = isLight ? '🌙 Dark' : '☀️ Light';
  const labelFg = getComputedStyle(document.body).getPropertyValue('--node-label').trim();
  const coreFg  = getComputedStyle(document.body).getPropertyValue('--node-core-fg').trim();
  d3.selectAll('.node-label').attr('fill', d => d.type==='core' ? coreFg : labelFg);
}

updateGraph();
simulation.alpha(1).restart();
</script>
</body>
</html>
"""


def render_html(nodes: list, links: list) -> str:
    nodes_json = json.dumps(nodes, ensure_ascii=False)
    links_json = json.dumps(links, ensure_ascii=False)
    return HTML_TEMPLATE.replace('__NODES__', nodes_json).replace('__LINKS__', links_json)


if __name__ == '__main__':
    print(f'Reading {SCHEMA}...')
    schema = yaml.safe_load(SCHEMA.read_text())

    nodes, links = build_graph(schema)
    print(f'  → {len(nodes)} nodes, {len(links)} links')

    html = render_html(nodes, links)
    OUTPUT.write_text(html)
    print(f'  → Written to {OUTPUT}')

    by_type = {}
    for n in nodes:
        by_type[n['type']] = by_type.get(n['type'], 0) + 1
    print('\nNode breakdown:')
    for t, c in sorted(by_type.items()):
        print(f'  {t:20s}: {c}')
