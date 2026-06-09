import os
import re
import json
import yaml
from datetime import datetime

def parse_frontmatter(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception:
        return {}, ""
    
    if content.startswith('---'):
        parts = content.split('---', 2)
        if len(parts) >= 3:
            try:
                fm = yaml.safe_load(parts[1])
                return fm or {}, parts[2]
            except Exception:
                pass
    return {}, content

def main():
    vault_path = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki"
    export_dir = os.path.join(vault_path, "wiki-export")
    os.makedirs(export_dir, exist_ok=True)

    # 1. Glob all md files
    all_files = []
    for root, dirs, files in os.walk(vault_path):
        # Exclude directories
        if any(x in root for x in ["_archives", "_raw", ".obsidian", "wiki-export"]):
            continue
        for f in files:
            if f.endswith(".md"):
                # Exclude specific files
                if f in ["index.md", "log.md", "_insights.md", "hot.md"]:
                    continue
                all_files.append(os.path.join(root, f))

    # 2. Build lookups and node list
    nodes = []
    id_to_node = {}
    basename_to_id = {}

    for path in all_files:
        rel_path = os.path.relpath(path, vault_path)
        if rel_path.endswith(".md"):
            rel_path = rel_path[:-3]
        
        node_id = rel_path.lower().replace(" ", "-")
        basename = os.path.basename(path)[:-3]
        basename_lower = basename.lower().replace(" ", "-")
        
        basename_to_id[basename_lower] = node_id
        basename_to_id[node_id] = node_id  # self lookup

        # Extract frontmatter
        fm, body = parse_frontmatter(path)
        
        label = fm.get("title", basename)
        category = rel_path.split(os.sep)[0] if os.sep in rel_path else "misc"
        tags = fm.get("tags", [])
        if isinstance(tags, str):
            tags = [tags]
        summary = fm.get("summary", "")
        if not summary:
            # Try to get first sentence of body
            clean_body = re.sub(r'[\*#`\[\]]', '', body).strip()
            first_line = clean_body.split('\n')[0] if clean_body else ""
            summary = first_line[:120] + "..." if len(first_line) > 120 else first_line

        node_data = {
            "id": node_id,
            "label": label,
            "category": category,
            "tags": tags,
            "summary": summary,
            "path": path,
            "body": body,
            "fm_relationships": fm.get("relationships", [])
        }
        nodes.append(node_data)
        id_to_node[node_id] = node_data

    # 3. Community ID assignments by dominant tag clustering
    # Gather tags across all nodes
    tag_counts = {}
    for n in nodes:
        if n["tags"]:
            dom_tag = n["tags"][0]
            tag_counts[dom_tag] = tag_counts.get(dom_tag, 0) + 1
            
    # Sort tags descending
    sorted_tags = sorted(tag_counts.keys(), key=lambda x: tag_counts[x], reverse=True)
    tag_to_community = {tag: idx for idx, tag in enumerate(sorted_tags)}

    for n in nodes:
        if n["tags"]:
            dom_tag = n["tags"][0]
            n["community"] = tag_to_community[dom_tag]
        else:
            n["community"] = None

    # 4. Edge list extraction
    links = []
    seen_edges = set()

    for n in nodes:
        source_id = n["id"]
        body = n["body"]
        
        # Regex to parse [[target]] or [[target|display]]
        wikilinks = re.findall(r'\[\[([^\]]+)\]\]', body)
        for link in wikilinks:
            target_part = link.split("|")[0].strip()
            target_norm = target_part.lower().replace(" ", "-")
            if target_norm.endswith(".md"):
                target_norm = target_norm[:-3]
                
            # Resolve target_norm
            resolved_id = None
            if target_norm in id_to_node:
                resolved_id = target_norm
            elif target_norm in basename_to_id:
                resolved_id = basename_to_id[target_norm]
            else:
                # Try basename check
                for base, nid in basename_to_id.items():
                    if base.endswith(target_norm) or target_norm.endswith(base):
                        resolved_id = nid
                        break

            if resolved_id and resolved_id != source_id:
                edge_key = tuple(sorted([source_id, resolved_id]))
                if edge_key not in seen_edges:
                    seen_edges.add(edge_key)
                    links.append({
                        "source": source_id,
                        "target": resolved_id,
                        "relation": "wikilink",
                        "confidence": "EXTRACTED"
                    })

        # Typed relationships frontmatter block
        fm_rels = n["fm_relationships"]
        if isinstance(fm_rels, list):
            for rel in fm_rels:
                if isinstance(rel, dict) and "target" in rel and "type" in rel:
                    target_str = rel["target"].strip()
                    if target_str.startswith("[[") and target_str.endswith("]]"):
                        target_str = target_str[2:-2].strip()
                    target_norm = target_str.lower().replace(" ", "-")
                    if target_norm.endswith(".md"):
                        target_norm = target_norm[:-3]
                        
                    resolved_id = None
                    if target_norm in id_to_node:
                        resolved_id = target_norm
                    elif target_norm in basename_to_id:
                        resolved_id = basename_to_id[target_norm]
                        
                    if resolved_id and resolved_id != source_id:
                        # Find or add edge
                        found = False
                        for link in links:
                            if tuple(sorted([link["source"], link["target"]])) == tuple(sorted([source_id, resolved_id])):
                                link["relation"] = rel["type"]
                                link["typed"] = True
                                found = True
                                break
                        if not found:
                            links.append({
                                "source": source_id,
                                "target": resolved_id,
                                "relation": rel["type"],
                                "confidence": "EXTRACTED",
                                "typed": True
                            })

    # Remove temporary keys for clean JSON
    clean_nodes = []
    for n in nodes:
        clean_nodes.append({
            "id": n["id"],
            "label": n["label"],
            "category": n["category"],
            "tags": n["tags"],
            "summary": n["summary"],
            "community": n["community"]
        })

    # Compute node degrees for sizing
    degrees = {n["id"]: 0 for n in clean_nodes}
    for l in links:
        degrees[l["source"]] = degrees.get(l["source"], 0) + 1
        degrees[l["target"]] = degrees.get(l["target"], 0) + 1

    # 5. Write graph.json
    graph_json = {
        "directed": False,
        "multigraph": False,
        "graph": {
            "exported_at": datetime.now().isoformat(),
            "vault": vault_path,
            "total_nodes": len(clean_nodes),
            "total_edges": len(links)
        },
        "nodes": clean_nodes,
        "links": links
    }
    
    with open(os.path.join(export_dir, "graph.json"), "w", encoding="utf-8") as f:
        json.dump(graph_json, f, indent=2, ensure_ascii=False)

    # 6. Write graph.graphml
    graphml = []
    graphml.append('<?xml version="1.0" encoding="UTF-8"?>')
    graphml.append('<graphml xmlns="http://graphml.graphdrawing.org/graphml">')
    graphml.append('  <key id="label" for="node" attr.name="label" attr.type="string"/>')
    graphml.append('  <key id="category" for="node" attr.name="category" attr.type="string"/>')
    graphml.append('  <key id="tags" for="node" attr.name="tags" attr.type="string"/>')
    graphml.append('  <key id="community" for="node" attr.name="community" attr.type="int"/>')
    graphml.append('  <key id="relation" for="edge" attr.name="relation" attr.type="string"/>')
    graphml.append('  <key id="type" for="edge" attr.name="type" attr.type="string"/>')
    graphml.append('  <key id="confidence" for="edge" attr.name="confidence" attr.type="string"/>')
    graphml.append('  <graph id="wiki" edgedefault="undirected">')

    for n in clean_nodes:
        cid_str = str(n["community"]) if n["community"] is not None else "null"
        tags_str = ", ".join(n["tags"])
        graphml.append(f'    <node id="{n["id"]}">')
        graphml.append(f'      <data key="label">{n["label"]}</data>')
        graphml.append(f'      <data key="category">{n["category"]}</data>')
        graphml.append(f'      <data key="tags">{tags_str}</data>')
        graphml.append(f'      <data key="community">{cid_str}</data>')
        graphml.append(f'    </node>')

    for idx, l in enumerate(links):
        typed_str = f'      <data key="type">{l["relation"]}</data>\n' if l.get("typed") else ""
        graphml.append(f'    <edge id="e{idx}" source="{l["source"]}" target="{l["target"]}">')
        graphml.append(f'      <data key="relation">{l["relation"]}</data>')
        if typed_str:
            graphml.append(typed_str.strip())
        graphml.append(f'      <data key="confidence">{l["confidence"]}</data>')
        graphml.append(f'    </edge>')

    graphml.append('  </graph>')
    graphml.append('</graphml>')

    with open(os.path.join(export_dir, "graph.graphml"), "w", encoding="utf-8") as f:
        f.write("\n".join(graphml))

    # 7. Write cypher.txt
    cypher = []
    cypher.append(f"// Wiki knowledge graph export — {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    cypher.append("// Nodes")
    for n in clean_nodes:
        tags_json = json.dumps(n["tags"])
        cid_str = str(n["community"]) if n["community"] is not None else "null"
        cypher.append(f'MERGE (n:Page {{id: "{n["id"]}"}}) SET n.label = "{n["label"]}", n.category = "{n["category"]}", n.tags = {tags_json}, n.community = {cid_str};')
    
    cypher.append("\n// Relationships")
    for l in links:
        rel_type = l["relation"].upper().replace("-", "_")
        if not l.get("typed"):
            rel_type = "WIKILINK"
        cypher.append(f'MATCH (a:Page {{id: "{l["source"]}"}}), (b:Page {{id: "{l["target"]}"}}) MERGE (a)-[:{rel_type} {{relation: "{l["relation"]}", confidence: "{l["confidence"]}"}}]->(b);')

    with open(os.path.join(export_dir, "cypher.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(cypher))

    # 8. Write graph.html (vis.js Visualization)
    html_nodes = []
    colors = ["#4E79A7", "#F28E2B", "#E15759", "#76B7B2", "#59A14F", "#EDC948", "#B07AA1", "#FF9DA7", "#9C755F", "#BAB0AC"]
    
    for n in clean_nodes:
        deg = degrees.get(n["id"], 0)
        size = min(60, deg * 3 + 8)
        color = colors[n["community"] % len(colors)] if n["community"] is not None else "#666"
        tags_str = " ".join(f"#{t}" for t in n["tags"])
        title = f"{n['category']} | {tags_str}\n\n{n['summary']}"
        html_nodes.append({
            "id": n["id"],
            "label": n["label"],
            "color": {"background": color, "border": "#fff", "highlight": {"background": "#ff4d4d", "border": "#fff"}},
            "size": size,
            "title": title,
            "community": n["community"]
        })

    type_colors = {
        "extends": "#59A14F",
        "implements": "#4E79A7",
        "contradicts": "#E15759",
        "derived_from": "#F28E2B",
        "uses": "#76B7B2",
        "replaces": "#B07AA1",
        "related_to": "#BAB0AC"
    }

    html_edges = []
    for l in links:
        color = type_colors.get(l["relation"], "#666")
        width = 2 if l.get("typed") else 1
        label = l["relation"] if l.get("typed") else ""
        html_edges.append({
            "from": l["source"],
            "to": l["target"],
            "dashes": False,
            "width": width,
            "color": {"color": color, "opacity": 0.6, "highlight": "#ff4d4d"},
            "label": label,
            "font": {"size": 8, "color": "#ccc", "strokeWidth": 0},
            "title": l["relation"]
        })

    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>Wiki Knowledge Graph</title>
<script src="https://unpkg.com/vis-network/standalone/umd/vis-network.min.js"></script>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ background: #0f0f1a; color: #e0e0e0; font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; display: flex; height: 100vh; overflow: hidden; }}
  #graph {{ flex: 1; height: 100vh; }}
  #sidebar {{ width: 320px; background: #141424; border-left: 2px solid #23233c; padding: 20px; overflow-y: auto; display: flex; flex-direction: column; gap: 20px; }}
  #sidebar h2 {{ color: #2ec4b6; font-size: 18px; border-bottom: 2px solid #23233c; padding-bottom: 8px; margin: 0; }}
  #sidebar h3 {{ color: #a0aec0; font-size: 11px; text-transform: uppercase; letter-spacing: 0.08em; margin: 0; }}
  #info {{ line-height: 1.6; color: #e2e8f0; background: #1a1a2e; border: 1px solid #2a2a4a; padding: 12px; border-radius: 8px; font-size: 13px; min-height: 100px; }}
  .legend-item {{ display: flex; align-items: center; gap: 10px; padding: 4px 0; font-size: 12px; }}
  .dot {{ width: 12px; height: 12px; border-radius: 50%; flex-shrink: 0; border: 1px solid #fff; }}
  #stats {{ color: #718096; font-size: 11px; margin-top: auto; border-top: 1px solid #23233c; padding-top: 12px; }}
</style>
</head>
<body>
<div id="graph"></div>
<div id="sidebar">
  <h2>LTE Bilgi Deposu</h2>
  <div>
    <h3>Seçili Hücre / Sayfa</h3>
    <div id="info" style="margin-top: 8px;">Grafik üzerinde detaylarını görmek istediğiniz bir düğüme (node) tıklayın.</div>
  </div>
  <div>
    <h3>Etiket Kümelenmesi</h3>
    <div id="legend" style="margin-top: 8px;"><!-- populated by JS --></div>
  </div>
  <div id="stats"><!-- populated by JS --></div>
</div>
<script>
const NODES_DATA = {json.dumps(html_nodes, ensure_ascii=False)};
const EDGES_DATA = {json.dumps(html_edges, ensure_ascii=False)};
const COMMUNITY_COLORS = ["#4E79A7","#F28E2B","#E15759","#76B7B2","#59A14F","#EDC948","#B07AA1","#FF9DA7","#9C755F","#BAB0AC"];

const nodes = new vis.DataSet(NODES_DATA);
const edges = new vis.DataSet(EDGES_DATA);
const container = document.getElementById('graph');
const data = {{nodes, edges}};
const options = {{
  physics: {{
    solver: 'forceAtlas2Based',
    forceAtlas2Based: {{
      gravitationalConstant: -100,
      springLength: 140,
      springConstant: 0.08,
      damping: 0.4
    }},
    stabilization: {{ iterations: 250 }}
  }},
  interaction: {{ hover: true, tooltipDelay: 100, selectConnectedEdges: true }},
  nodes: {{ shape: 'dot', borderWidth: 1.5 }},
  edges: {{
    smooth: {{ type: 'continuous' }},
    arrows: {{ to: {{ enabled: true, scaleFactor: 0.5 }} }}
  }}
}};
const network = new vis.Network(container, data, options);
network.once('stabilizationIterationsDone', () => network.setOptions({{ physics: {{ enabled: false }} }}));

network.on('click', (params) => {{
  if (params.nodes.length > 0) {{
    const nid = params.nodes[0];
    const n = NODES_DATA.find(x => x.id === nid);
    if (n) {{
      const tagBadges = n.title.split('\\n')[0].split('|')[1].trim();
      document.getElementById('info').innerHTML = `
        <strong style="font-size: 15px; color: #2ec4b6;">${{n.label}}</strong><br>
        <span style="font-size: 11px; color: #a0aec0; text-transform: uppercase;">Kategori: ${{n.id.split('/')[0]}}</span><br>
        <span style="color: #ed64a6; font-size: 12px;">${{tagBadges}}</span><br><br>
        <p style="color: #cbd5e0; line-height: 1.5;">${{n.title.split('\\n\\n')[1] || ''}}</p>
      `;
    }}
  }} else {{
    document.getElementById('info').innerHTML = 'Grafik üzerinde detaylarını görmek istediğiniz bir düğüme (node) tıklayın.';
  }}
}});

// Legend population
const communities = {{}};
NODES_DATA.forEach(n => {{
  if (n.community !== null) {{
    communities[n.community] = (communities[n.community] || 0) + 1;
  }}
}});
const leg = document.getElementById('legend');
Object.entries(communities).sort((a,b)=>b[1]-a[1]).forEach(([cid, count]) => {{
  const color = COMMUNITY_COLORS[cid % COMMUNITY_COLORS.length];
  // Extract dominant tag for this community
  const sampleNode = NODES_DATA.find(x => x.community == cid);
  const domTag = sampleNode ? sampleNode.title.split('\\n')[0].split('|')[1].trim().split(' ')[0] : `Topluluk ${{cid}}`;
  leg.innerHTML += `
    <div class="legend-item">
      <div class="dot" style="background:${{color}}"></div>
      <span>${{domTag}} (${{count}} Sayfa)</span>
    </div>
  `;
}});
document.getElementById('stats').textContent = `${{NODES_DATA.length}} Sayfa · ${{EDGES_DATA.length}} Bağlantı · 100% Sağlıklı`;
</script>
</body>
</html>
"""

    with open(os.path.join(export_dir, "graph.html"), "w", encoding="utf-8") as f:
        f.write(html_content)

    print(f"Wiki export complete → wiki-export/")
    print(f"  graph.json    — {len(clean_nodes)} nodes, {len(links)} edges (NetworkX node_link format)")
    print(f"  graph.graphml — {len(clean_nodes)} nodes, {len(links)} edges (Gephi / yEd / Cytoscape)")
    print(f"  cypher.txt    — {len(clean_nodes)} MERGE nodes + {len(links)} MERGE relationships (Neo4j)")
    print(f"  graph.html    — interactive browser visualization (open in any browser)")

if __name__ == "__main__":
    main()
