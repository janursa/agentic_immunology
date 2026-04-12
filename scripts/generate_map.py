#!/usr/bin/env python3
"""
generate_map.py
---------------
Parses the agentic repo markdown files and generates agentic_map.html —
an interactive D3.js force-directed graph of all tools, data, know-how, and images.

Run: python3 generate_map.py
Output: /vol/projects/CIIM/agentic_central/agentic/agentic_map.html
"""

import re
import json
from pathlib import Path

BASE   = Path('/vol/projects/CIIM/agentic_central/agentic')
OUTPUT = BASE / 'agentic_map.html'

# ── PARSERS ───────────────────────────────────────────────────────────────────

def parse_tools(text: str) -> dict:
    """
    Parse tools.md.
    Returns {'biomni': [...], 'ciim': [...]}
    Each item: {id, module, pretty, subtitle, desc, functions}
    """
    result = {}

    # Split into top-level groups (## biomni / ## CIIM)
    group_blocks = re.split(r'\n## ', '\n' + text)
    for block in group_blocks:
        if not block.strip():
            continue
        lines = block.strip().split('\n')
        group_name = lines[0].strip().lower()
        if group_name not in ('biomni', 'ciim'):
            continue

        body = '\n'.join(lines[1:])
        modules = []

        # Each module separated by ---
        for section in re.split(r'\n---+\n?', body):
            section = section.strip()
            if not section:
                continue

            # Module name: ### `name` or ### name
            m_name = re.search(r'^###\s+`?(\w+)`?', section, re.MULTILINE)
            if not m_name:
                continue
            module = m_name.group(1)

            # Subtitle: *text*
            m_sub = re.search(r'^\*(.+?)\*', section, re.MULTILINE)
            subtitle = m_sub.group(1) if m_sub else module

            # Description: line after subtitle+blank, before functions
            # Find the description paragraph
            desc_match = re.search(
                r'\*.+?\*\n+(.+?)(?:\n\n|→|\Z)', section, re.DOTALL
            )
            desc = desc_match.group(1).strip().replace('\n', ' ') if desc_match else ''
            # Remove markdown links
            desc = re.sub(r'→\s*\[.*?\]\(.*?\)', '', desc).strip()

            # Functions: backtick-wrapped, separated by ·
            funcs = re.findall(r'`([\w_]+)`', section)
            # Remove things that look like paths or imports
            funcs = [f for f in funcs if not f.startswith('/') and '_' in f or len(f) > 4]

            modules.append({
                'id':       f'T_{group_name.upper()}_{module}',
                'module':   module,
                'pretty':   subtitle,
                'subtitle': subtitle,
                'desc':     desc,
                'functions': funcs,
                'group':    group_name,
            })

        result[group_name] = modules

    return result


def parse_datalake_list(text: str, cat_id_prefix: str) -> list:
    """
    Parse datalake/*/list.md.
    Returns list of {id, filename, pretty, desc}
    """
    items = []
    # Each entry: ## filename\n**Pretty Name**\nDescription
    blocks = re.split(r'\n## ', '\n' + text)
    for block in blocks:
        block = block.strip()
        if not block or block.startswith('#'):
            continue
        lines = block.split('\n')
        filename = lines[0].strip()
        rest = '\n'.join(lines[1:]).strip()

        # Pretty name: **Name**
        m_pretty = re.search(r'\*\*(.+?)\*\*', rest)
        pretty = m_pretty.group(1) if m_pretty else filename

        # Description: text after pretty name line
        desc_lines = []
        in_desc = False
        for line in rest.split('\n'):
            stripped = line.strip()
            if re.match(r'\*\*.+\*\*', stripped):
                in_desc = True
                continue
            if in_desc and stripped:
                desc_lines.append(stripped)
            elif in_desc and not stripped and desc_lines:
                break
        desc = ' '.join(desc_lines)

        # Safe ID from filename
        safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', filename)
        items.append({
            'id':       f'{cat_id_prefix}_{safe_id}',
            'filename': filename,
            'pretty':   pretty,
            'desc':     desc,
        })
    return items


def parse_datalake_categories(text: str) -> list:
    """
    Parse datalake.md top-level categories.
    Returns list of {id, name, desc}
    """
    cats = []
    blocks = re.split(r'\n### ', '\n' + text)
    for block in blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split('\n')
        name = lines[0].strip()
        desc = ' '.join(l.strip() for l in lines[1:] if l.strip() and not l.startswith('Files'))
        cats.append({'id': f'DCAT_{name.lower()}', 'name': name, 'desc': desc.strip()})
    return cats


def parse_summary_stats(text: str) -> dict:
    """
    Parse summary_stats.md.
    Returns {'module_name': [list of {id, filename, pretty, desc}], ...}
    Grouped by ## module sections (e.g. ## hiara).
    """
    result = {}
    # Split by ## module headings
    module_blocks = re.split(r'\n## ', '\n' + text)
    for block in module_blocks:
        block = block.strip()
        if not block:
            continue
        lines = block.split('\n')
        module_name = lines[0].strip().lower()
        body = '\n'.join(lines[1:])

        items = []
        for section in re.split(r'\n### ', '\n' + body):
            section = section.strip()
            if not section or not section.startswith('`'):
                continue
            sec_lines = section.split('\n')
            m_fn = re.match(r'`([^`]+)`', sec_lines[0])
            if not m_fn:
                continue
            filename = m_fn.group(1)
            rest = '\n'.join(sec_lines[1:]).strip()

            m_pretty = re.search(r'^\*(.+?)\*', rest, re.MULTILINE)
            pretty = m_pretty.group(1) if m_pretty else filename

            m_loader = re.search(r'\*\*Load:\*\*\s*`([^`]+)`', rest)
            loader = m_loader.group(1) if m_loader else ''

            desc_lines = []
            capture = False
            for line in rest.split('\n'):
                s = line.strip()
                if re.match(r'^\*.+\*$', s):
                    capture = True
                    continue
                if capture and s and not s.startswith('**'):
                    desc_lines.append(s)
                elif capture and s.startswith('**'):
                    break
            desc = ' '.join(desc_lines)
            if loader:
                desc += f"<br><span style='color:#8b949e;font-size:11px'>Load: <code>{loader}</code></span>"

            safe_id = re.sub(r'[^a-zA-Z0-9_]', '_', filename)
            items.append({'id': f'SS_{safe_id}', 'filename': filename, 'pretty': pretty, 'desc': desc})

        if items:
            result[module_name] = items
    return result


def parse_images(text: str) -> list:
    """Parse images.md table rows."""
    images = []
    for m in re.finditer(r'`([\w.]+\.sif)`\s*\|\s*([^|]+)\|\s*([^|]+)', text):
        name = m.group(1).strip()
        desc = m.group(3).strip()
        images.append({'id': f'IMG_{name.replace(".","_")}', 'name': name, 'desc': desc})
    return images


def parse_knowhow(folder: Path) -> list:
    """Read first # heading from each .md file."""
    guides = []
    for f in sorted(folder.glob('*.md')):
        text = f.read_text()
        m = re.search(r'^#\s+(.+)', text, re.MULTILINE)
        title = m.group(1).strip() if m else f.stem
        # First paragraph after title
        paragraphs = [p.strip() for p in text.split('\n\n') if p.strip() and not p.startswith('#')]
        desc = paragraphs[0] if paragraphs else ''
        desc = re.sub(r'\n', ' ', desc).strip()
        guides.append({'id': f'KH_{f.stem}', 'name': title, 'desc': desc, 'file': f.name})
    return guides


# ── BIOMNI DATA GROUPING ──────────────────────────────────────────────────────
# The biomni datalake has ~70 files; group them into logical clusters for the graph.

BIOMNI_GROUPS = {
    'DDInter Drug-Drug': {
        'desc': 'Drug-drug interaction files from DDInter 2.0 across therapeutic categories (alimentary, antineoplastic, antiparasitic, blood, dermatological, hormonal, respiratory, various).',
        'prefixes': ['ddinter_']
    },
    'DepMap CRISPR': {
        'desc': 'Broad DepMap gene dependency scores, CRISPR gene effects, cancer model metadata, and gene expression for cancer cell lines.',
        'prefixes': ['DepMap_']
    },
    'Gene Sets\n(MSigDB/MouseMine/GO)': {
        'desc': 'Human and mouse gene set collections: MSigDB (hallmarks, oncogenic, immunologic, cell type, ontology, positional, curated, TF targets) and MouseMine equivalents, plus GO-plus.',
        'prefixes': ['msigdb_', 'mousemine_', 'go-plus']
    },
    'Disease Associations\n(DisGeNET/OMIM/HPO)': {
        'desc': 'Gene-disease associations from DisGeNET, genetic disorders from OMIM, and Human Phenotype Ontology (HPO).',
        'prefixes': ['DisGeNET', 'omim', 'hp.obo']
    },
    'PPI Networks': {
        'desc': 'Protein-protein interactions: affinity capture MS/RNA, co-fractionation, proximity labeling MS, reconstituted complexes, yeast two-hybrid, synthetic lethality/rescue/growth defect, virus-host (P-HIPSTER), genetic interactions.',
        'prefixes': ['affinity_capture', 'co-frac', 'proximity', 'reconstituted', 'two-hybrid',
                     'synthetic_', 'dosage_', 'genetic_interaction', 'Virus-Host']
    },
    'Drug Discovery\n(BindingDB/Broad/EveBio)': {
        'desc': 'Drug binding affinities (BindingDB), Broad Drug Repurposing Hub molecules and targets, Enamine REAL library, EveBio pharmome assay/compound/result tables.',
        'prefixes': ['BindingDB', 'broad_repurposing', 'enamine_', 'evebio_']
    },
    'GWAS / Variants\n(GeneBass)': {
        'desc': 'GWAS Catalog association results, GeneBass missense/pLoF/synonymous variant annotations, and general variant table.',
        'prefixes': ['gwas_catalog', 'genebass_', 'variant_table']
    },
    'miRNA Databases': {
        'desc': 'miRDB predicted targets, miRTarBase experimentally validated interactions (with PubMed abstracts and binding sites).',
        'prefixes': ['miRDB', 'miRTarBase']
    },
    'Drug Repurposing\n(TxGNN)': {
        'desc': 'TxGNN drug repurposing name mapping and predictions for disease-drug associations.',
        'prefixes': ['txgnn_']
    },
    'Cell & Immune\nResources': {
        'desc': 'McPAS TCR sequences, cell type marker genes, CZI Cell Census datasets, GTEx tissue expression, Protein Atlas, sgRNA knockout data (human + mouse), gene info, precision medicine knowledge graph.',
        'prefixes': ['McPAS', 'marker_celltype', 'czi_census', 'gtex_', 'proteinatlas', 'sgRNA_', 'gene_info', 'kg.csv']
    },
}


def group_biomni_files(files: list) -> list:
    """Assign biomni files to logical groups and return group nodes."""
    # Track which files have been assigned
    assigned = set()
    groups = []
    for g_name, g_info in BIOMNI_GROUPS.items():
        matched_files = []
        for f in files:
            fn = f['filename']
            for prefix in g_info['prefixes']:
                if fn.startswith(prefix) or fn == prefix:
                    matched_files.append(f['pretty'])
                    assigned.add(f['filename'])
                    break
        if matched_files:
            safe = re.sub(r'[^a-zA-Z0-9]', '_', g_name)
            groups.append({
                'id':       f'DBG_{safe}',
                'pretty':   g_name,
                'desc':     g_info['desc'],
                'files':    matched_files,
            })
    return groups


# ── GRAPH BUILDER ─────────────────────────────────────────────────────────────

def build_graph() -> tuple:
    nodes, links = [], []

    def add_node(**kwargs):
        nodes.append(kwargs)

    def add_link(source, target, ltype='default'):
        links.append({'source': source, 'target': target, 'type': ltype})

    # ── Core
    add_node(id='LLM', label='🧬 LLM\nCore', type='core', r=44,
             desc='Central AI agent orchestrating all tools, data lake resources, know-how, and compute environments in the agentic ecosystem.')

    # ── Category nodes
    cats = [
        ('CAT_TOOLS',    '🔧 Tools',        'category', 30, 'Python tool modules for genomics, immunology, pharmacology, literature, databases, and genetics.'),
        ('CAT_DATA',     '📊 Data Lake',    'category', 30, 'Curated biomedical datasets: raw scRNA-seq cohorts, OmniPath signaling, and general reference databases.'),
        ('CAT_SUMSTATS', '📈 Summary Stats','category', 30, 'Precomputed CIIM signature files: aging, SLE, drug, cytokine TF/gene expression/CCC statistics and immune GRN models. Loaded via retrieve_summary_stats() or get_immune_grn().'),
        ('CAT_KNOWHOW',  '📚 Know-How',     'category', 30, 'Methodology guides and workflow documentation for common agentic tasks.'),
        ('CAT_IMAGES',   '🐳 Images',       'category', 30, 'Singularity container images with pre-installed environments for all tool modules.'),
    ]
    for nid, label, ntype, r, desc in cats:
        add_node(id=nid, label=label, type=ntype, r=r, desc=desc)
        if nid != 'CAT_IMAGES':
            add_link('LLM', nid, 'category')

    # ── Tools
    tools_text = (BASE / 'tools.md').read_text()
    tools_data = parse_tools(tools_text)

    # biomni sub-category
    add_node(id='CAT_BIOMNI', label='Biomni', type='tool_group', r=20,
             desc='Biomni tool suite — 6 modules covering databases, genetics, genomics, immunology, literature, and pharmacology.')
    add_link('CAT_TOOLS', 'CAT_BIOMNI')

    # ciim sub-category
    add_node(id='CAT_CIIM', label='CIIM', type='tool_group', r=20,
             desc='CIIM tool suite — 2 modules for immune single-cell genomics and HIaRA aging clock analysis.')
    add_link('CAT_TOOLS', 'CAT_CIIM')

    for t in tools_data.get('biomni', []):
        func_preview = ', '.join(t['functions'][:5])
        if len(t['functions']) > 5:
            func_preview += f' + {len(t["functions"]) - 5} more'
        full_desc = f"{t['desc']}<br><br><span style='color:#8b949e;font-size:11px'>Functions ({len(t['functions'])}): {func_preview}</span>"
        add_node(id=t['id'], label=t['pretty'], type='tool', r=15,
                 desc=full_desc, module=t['module'], nfuncs=len(t['functions']))
        add_link('CAT_BIOMNI', t['id'])

    for t in tools_data.get('ciim', []):
        func_preview = ', '.join(t['functions'][:5])
        if len(t['functions']) > 5:
            func_preview += f' + {len(t["functions"]) - 5} more'
        full_desc = f"{t['desc']}<br><br><span style='color:#8b949e;font-size:11px'>Functions ({len(t['functions'])}): {func_preview}</span>"
        add_node(id=t['id'], label=t['pretty'], type='tool_ciim', r=15,
                 desc=full_desc, module=t['module'], nfuncs=len(t['functions']))
        add_link('CAT_CIIM', t['id'])

    # ── Data Lake
    dl_text   = (BASE / 'datalake.md').read_text()
    dl_cats   = parse_datalake_categories(dl_text)

    dl_cat_map = {c['name'].lower(): c for c in dl_cats}

    # Filter to known real category names only
    dl_cats = [c for c in dl_cats if not c['name'].startswith('#') and
               c['name'].lower() in ('omics','prior','omnipath','biomni')]

    for c in dl_cats:
        label_map = {
            'omics':    '🧫 Omics',
            'prior':    '📋 Prior',
            'omnipath': '🔗 OmniPath',
            'biomni':   '🗄️ Biomni',
        }
        label = label_map.get(c['name'].lower(), c['name'])
        add_node(id=c['id'], label=label, type='data_cat', r=20, desc=c['desc'])
        add_link('CAT_DATA', c['id'])

    # Omics files
    omics_text  = (BASE / 'datalake/omics/list.md').read_text()
    omics_files = parse_datalake_list(omics_text, 'DO')

    # Group omics by cohort (SC + Bulk + BulkMinor → one node per cohort)
    cohort_map = {}
    for f in omics_files:
        fn = f['filename']
        for cohort in ['aida', 'abf300', 'onek1k', 'perez_sle', 'zhang', 'CXCL9', 'op']:
            if fn.startswith(cohort):
                if cohort not in cohort_map:
                    cohort_map[cohort] = {'files': [], 'pretty': None, 'desc': ''}
                cohort_map[cohort]['files'].append(f)
                if '_sc' in fn or fn == f'{cohort}.h5ad':
                    cohort_map[cohort]['pretty'] = f['pretty']
                    cohort_map[cohort]['desc']   = f['desc']
                break

    cohort_pretty = {
        'aida':     'AIDA', 'abf300': 'ABF300', 'onek1k': 'OneK1K',
        'perez_sle':'Perez SLE', 'zhang': 'Zhang', 'CXCL9': 'CXCL9', 'op': 'OP Drug'
    }
    for cohort, info in cohort_map.items():
        pretty = cohort_pretty.get(cohort, cohort)
        variants = [f['pretty'] for f in info['files']]
        desc = (info['desc'] or '') + f"<br><br><span style='color:#8b949e;font-size:11px'>Variants: {', '.join(variants)}</span>"
        add_node(id=f'DO_{cohort}', label=pretty, type='data', r=11, desc=desc)
        add_link('DCAT_omics', f'DO_{cohort}')

    # Prior files
    prior_text  = (BASE / 'datalake/prior/list.md').read_text()
    prior_files = parse_datalake_list(prior_text, 'DP')
    for f in prior_files:
        add_node(id=f['id'], label=f['pretty'], type='data', r=11, desc=f['desc'])
        add_link('DCAT_prior', f['id'])

    # OmniPath files
    omni_text  = (BASE / 'datalake/omnipath/list.md').read_text()
    omni_files = parse_datalake_list(omni_text, 'DOP')
    for f in omni_files:
        add_node(id=f['id'], label=f['pretty'], type='data', r=11, desc=f['desc'])
        add_link('DCAT_omnipath', f['id'])

    # Biomni files — grouped
    biomni_text  = (BASE / 'datalake/biomni/list.md').read_text()
    biomni_files = parse_datalake_list(biomni_text, 'DB')
    groups = group_biomni_files(biomni_files)
    for g in groups:
        files_preview = ', '.join(g['files'][:4])
        if len(g['files']) > 4:
            files_preview += f' + {len(g["files"]) - 4} more'
        full_desc = g['desc'] + f"<br><br><span style='color:#8b949e;font-size:11px'>Files ({len(g['files'])}): {files_preview}</span>"
        add_node(id=g['id'], label=g['pretty'], type='data', r=11, desc=full_desc)
        add_link('DCAT_biomni', g['id'])

    # ── Summary Stats
    ss_text   = (BASE / 'summary_stats.md').read_text()
    ss_groups = parse_summary_stats(ss_text)
    existing_node_ids = {n['id'] for n in nodes}
    for module_name, files in ss_groups.items():
        # Use existing CIIM tool node if present, otherwise create a hub node.
        tool_node_id = f'T_CIIM_{module_name.lower()}'
        if tool_node_id not in existing_node_ids:
            add_node(id=tool_node_id, label=module_name.capitalize(), type='tool_group', r=20,
                     desc=f'Summary stats module: {module_name}')
            existing_node_ids.add(tool_node_id)
        add_link('CAT_SUMSTATS', tool_node_id)
        for f in files:
            add_node(id=f['id'], label=f['pretty'], type='sumstat', r=13, desc=f['desc'])
            add_link(tool_node_id, f['id'])

    # ── Know-How
    guides = parse_knowhow(BASE / 'knowhow')
    for g in guides:
        add_node(id=g['id'], label=g['name'], type='knowhow', r=15, desc=g['desc'])
        add_link('CAT_KNOWHOW', g['id'])

    # ── Images
    images_text = (BASE / 'images.md').read_text()
    images = parse_images(images_text)
    for img in images:
        add_node(id=img['id'], label=img['name'], type='image', r=17, desc=img['desc'])
        # no links — images float freely

    # Cross-links: hiara loads summary stats (already wired via CAT_SUMSTATS → T_CIIM_hiara above)

    return nodes, links


# ── HTML TEMPLATE ─────────────────────────────────────────────────────────────

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<title>Agentic Ecosystem Map</title>
<script src="https://d3js.org/d3.v7.min.js"></script>
<style>
  * { box-sizing: border-box; margin: 0; padding: 0; }
  body {
    background: #0d1117;
    font-family: 'Segoe UI', system-ui, sans-serif;
    overflow: hidden;
    color: #e6edf3;
  }
  #title {
    position: absolute; top: 16px; left: 50%;
    transform: translateX(-50%);
    font-size: 17px; font-weight: 700; color: #58a6ff;
    letter-spacing: 1px; pointer-events: none; z-index: 10;
    text-shadow: 0 0 20px rgba(88,166,255,0.4);
  }
  #legend {
    position: absolute; bottom: 18px; left: 18px;
    background: rgba(22,27,34,0.95); border: 1px solid #30363d;
    border-radius: 10px; padding: 12px 16px; font-size: 12px; z-index: 10;
  }
  #legend h4 { color: #8b949e; margin-bottom: 8px; font-size: 10px; text-transform: uppercase; letter-spacing: 0.5px; }
  .legend-item { display: flex; align-items: center; gap: 8px; margin: 4px 0; }
  .legend-dot { width: 11px; height: 11px; border-radius: 50%; flex-shrink: 0; }
  #tooltip {
    position: absolute; pointer-events: none;
    background: rgba(22,27,34,0.97); border: 1px solid #30363d;
    border-radius: 8px; padding: 11px 14px;
    font-size: 12px; max-width: 300px; line-height: 1.55;
    z-index: 100; display: none;
    box-shadow: 0 6px 24px rgba(0,0,0,0.6);
  }
  #tooltip .tt-title { font-weight: 700; font-size: 13px; margin-bottom: 3px; }
  #tooltip .tt-badge { display: inline-block; font-size: 10px; padding: 1px 7px;
    border-radius: 10px; margin-bottom: 6px; font-weight: 600; }
  #tooltip .tt-desc  { color: #c9d1d9; }
  #controls {
    position: absolute; top: 16px; right: 16px;
    display: flex; gap: 8px; z-index: 10;
  }
  #search-wrap {
    position: absolute; top: 16px; left: 16px; z-index: 10;
  }
  #search {
    background: #21262d; border: 1px solid #30363d; color: #e6edf3;
    padding: 6px 12px; border-radius: 6px; font-size: 12px; width: 180px;
    outline: none;
  }
  #search::placeholder { color: #8b949e; }
  button {
    background: #21262d; border: 1px solid #30363d; color: #e6edf3;
    padding: 6px 12px; border-radius: 6px; cursor: pointer; font-size: 12px;
    transition: background 0.2s;
  }
  button:hover { background: #30363d; }
  svg { width: 100vw; height: 100vh; }
  .node { cursor: grab; }
  .node:active { cursor: grabbing; }
  .node circle { stroke-width: 2px; }
  .node text { pointer-events: none; user-select: none; }
  .link { stroke-opacity: 0.3; }
  .link-category { stroke-opacity: 0.55; }
  .link-dependency { stroke-opacity: 0.5; stroke-dasharray: 5,4; }
  .node.dimmed circle { opacity: 0.15; }
  .node.dimmed text  { opacity: 0.1; }
  .link.dimmed { opacity: 0.05; }
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
</div>
<div id="legend">
  <h4>Node Types</h4>
  <div class="legend-item"><div class="legend-dot" style="background:#ff7b72"></div><span>LLM Core</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#79c0ff"></div><span>Category</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#56d364"></div><span>biomni Tool</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#3fb950"></div><span>CIIM Tool</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#ffa657"></div><span>Data Category</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#e3b341"></div><span>Dataset / Group</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#f778ba"></div><span>Summary Stats</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#d2a8ff"></div><span>Know-How</span></div>
  <div class="legend-item"><div class="legend-dot" style="background:#f0883e"></div><span>Singularity Image</span></div>
  <div style="margin-top:8px;padding-top:8px;border-top:1px solid #30363d;color:#8b949e;font-size:10px">
    ─ ─  dependency link
  </div>
</div>
<svg id="graph"></svg>
<script>
const NODES = __NODES__;
const LINKS = __LINKS__;

const W = window.innerWidth, H = window.innerHeight;
let showLabels = true;

const colorMap = {
  core:       '#ff7b72',
  category:   '#79c0ff',
  tool_group: '#a3d977',
  tool:       '#56d364',
  tool_ciim:  '#3fb950',
  data_cat:   '#ffa657',
  data:       '#e3b341',
  sumstat:    '#f778ba',
  knowhow:    '#d2a8ff',
  image:      '#f0883e',
};
const strokeMap = {
  core:       '#ff4444',
  category:   '#1f6feb',
  tool_group: '#4a9a22',
  tool:       '#238636',
  tool_ciim:  '#196127',
  data_cat:   '#d86a00',
  data:       '#9e7500',
  sumstat:    '#c4347a',
  knowhow:    '#8b5cf6',
  image:      '#c0622d',
};
const typeLabel = {
  core:'LLM Core', category:'Category', tool_group:'Tool Suite',
  tool:'biomni Tool', tool_ciim:'CIIM Tool',
  data_cat:'Data Category', data:'Dataset',
  sumstat:'Summary Stats File',
  knowhow:'Know-How Guide', image:'Singularity Image',
};

const svg = d3.select('#graph');
const g   = svg.append('g');

const zoom = d3.zoom().scaleExtent([0.15, 4])
  .on('zoom', e => g.attr('transform', e.transform));
svg.call(zoom);

// Glow filter
const defs = svg.append('defs');
const glow = defs.append('filter').attr('id','glow');
glow.append('feGaussianBlur').attr('stdDeviation','5').attr('result','coloredBlur');
const fm = glow.append('feMerge');
fm.append('feMergeNode').attr('in','coloredBlur');
fm.append('feMergeNode').attr('in','SourceGraphic');

function linkDistance(d) {
  const tt = typeof d.target === 'object' ? d.target.type : NODES.find(n=>n.id===d.target)?.type;
  if (d.type === 'category') return 200;
  if (tt === 'tool_group' || tt === 'data_cat') return 140;
  if (tt === 'tool' || tt === 'tool_ciim') return 95;
  if (tt === 'data') return 80;
  if (tt === 'knowhow') return 110;
  if (tt === 'image') return 120;
  return 100;
}
function chargeStrength(d) {
  if (d.type === 'core')       return -1600;
  if (d.type === 'category')   return -700;
  if (d.type === 'tool_group') return -400;
  if (d.type === 'data_cat')   return -350;
  return -200;
}

const simulation = d3.forceSimulation(NODES)
  .force('link', d3.forceLink(LINKS).id(d=>d.id).distance(linkDistance).strength(0.55))
  .force('charge', d3.forceManyBody().strength(chargeStrength))
  .force('center', d3.forceCenter(W/2, H/2))
  .force('collision', d3.forceCollide().radius(d => d.r + 20));

const link = g.append('g').selectAll('line').data(LINKS).join('line')
  .attr('class', d => 'link' + (d.type==='category' ? ' link-category' : d.type==='dependency' ? ' link-dependency' : ''))
  .attr('stroke', d => d.type==='dependency' ? '#58a6ff' : d.type==='category' ? '#79c0ff' : '#484f58')
  .attr('stroke-width', d => d.type==='category' ? 2.5 : d.type==='dependency' ? 1.5 : 1);

const node = g.append('g').selectAll('g').data(NODES).join('g')
  .attr('class', 'node')
  .call(d3.drag()
    .on('start', (e,d) => { if (!e.active) simulation.alphaTarget(0.3).restart(); d.fx=d.x; d.fy=d.y; })
    .on('drag',  (e,d) => { d.fx=e.x; d.fy=e.y; })
    .on('end',   (e,d) => { if (!e.active) simulation.alphaTarget(0); d.fx=null; d.fy=null; })
  )
  .on('mouseover', showTip)
  .on('mousemove', moveTip)
  .on('mouseout',  hideTip);

node.append('circle')
  .attr('r', d => d.r)
  .attr('fill', d => colorMap[d.type] + 'cc')
  .attr('stroke', d => strokeMap[d.type])
  .attr('filter', d => d.type==='core' ? 'url(#glow)' : null);

// Function count badge ring for tool nodes
node.filter(d => d.nfuncs > 0)
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

node.append('text')
  .attr('class','node-label')
  .attr('text-anchor','middle')
  .attr('dominant-baseline','central')
  .attr('fill', d => d.type==='core' ? '#0d1117' : '#e6edf3')
  .attr('font-size', d => d.type==='core' ? '13px' : d.type==='category' ? '11px' : d.r > 18 ? '10px' : '8px')
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

simulation.on('tick', () => {
  link.attr('x1',d=>d.source.x).attr('y1',d=>d.source.y)
      .attr('x2',d=>d.target.x).attr('y2',d=>d.target.y);
  node.attr('transform', d=>`translate(${d.x},${d.y})`);
});

// ── Tooltip
function showTip(event, d) {
  const tt = document.getElementById('tooltip');
  const color = colorMap[d.type];
  const raw = d.label.replace(/\n/g,' ');
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
  const x = event.pageX + 16, y = event.pageY - 12;
  tt.style.left = Math.min(x, window.innerWidth - tt.offsetWidth - 12) + 'px';
  tt.style.top  = Math.max(y, 8) + 'px';
}
function hideTip() { document.getElementById('tooltip').style.display='none'; }

// ── Search / highlight
const searchInput = document.getElementById('search');
searchInput.addEventListener('input', () => {
  const q = searchInput.value.trim().toLowerCase();
  if (!q) { node.classed('dimmed', false); link.classed('dimmed', false); return; }
  const matched = new Set(NODES.filter(n =>
    (n.label||'').toLowerCase().includes(q) ||
    (n.desc||'').toLowerCase().includes(q) ||
    (n.module||'').toLowerCase().includes(q)
  ).map(n => n.id));
  // also include parents of matched
  LINKS.forEach(l => {
    const sid = typeof l.source==='object'?l.source.id:l.source;
    const tid = typeof l.target==='object'?l.target.id:l.target;
    if (matched.has(tid)) matched.add(sid);
  });
  node.classed('dimmed', d => !matched.has(d.id));
  link.classed('dimmed', d => {
    const sid = typeof d.source==='object'?d.source.id:d.source;
    const tid = typeof d.target==='object'?d.target.id:d.target;
    return !matched.has(sid) && !matched.has(tid);
  });
});

// ── Controls
function resetZoom() {
  svg.transition().duration(600).call(zoom.transform, d3.zoomIdentity.translate(0,0).scale(1));
}
function toggleLabels() {
  showLabels = !showLabels;
  d3.selectAll('.node-label').style('display', showLabels ? null : 'none');
}
function relaxAll() {
  NODES.forEach(d => { d.vx = (Math.random()-0.5)*80; d.vy = (Math.random()-0.5)*80; });
  simulation.alpha(0.5).restart();
}

simulation.alpha(1).restart();
</script>
</body>
</html>
"""


def render_html(nodes: list, links: list) -> str:
    nodes_json = json.dumps(nodes, indent=None)
    links_json = json.dumps(links, indent=None)
    html = HTML_TEMPLATE.replace('__NODES__', nodes_json).replace('__LINKS__', links_json)
    return html


# ── MAIN ──────────────────────────────────────────────────────────────────────

if __name__ == '__main__':
    print('Building graph from markdown files...')
    nodes, links = build_graph()
    print(f'  → {len(nodes)} nodes, {len(links)} links')

    html = render_html(nodes, links)
    OUTPUT.write_text(html)
    print(f'  → Written to {OUTPUT}')

    # Summary
    by_type = {}
    for n in nodes:
        by_type[n['type']] = by_type.get(n['type'], 0) + 1
    print('\nNode breakdown:')
    for t, c in sorted(by_type.items()):
        print(f'  {t:15s}: {c}')
