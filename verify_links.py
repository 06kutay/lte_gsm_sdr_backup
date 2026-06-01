#!/usr/bin/env python3
import os
import re
import sys

def main():
    vault_path = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki"
    if not os.path.exists(vault_path):
        print(f"Error: Vault path not found: {vault_path}")
        sys.exit(1)
        
    print(f"=== Starting Wiki Link Health Check on {vault_path} ===")
    
    # 1. Collect all valid page paths and target names
    all_files = []
    page_names = set()
    page_to_path = {}
    
    for root, dirs, files in os.walk(vault_path):
        for f in files:
            if f.endswith(".md"):
                full_path = os.path.join(root, f)
                rel_path = os.path.relpath(full_path, vault_path)
                page_name = f[:-3]
                
                all_files.append((rel_path, full_path))
                page_names.add(page_name)
                page_to_path[page_name] = rel_path
                
    print(f"Total Markdown pages found: {len(all_files)}")
    
    # 2. Extract and check all wikilinks
    broken_links = []
    total_links = 0
    link_edges = []
    
    for rel_path, full_path in all_files:
        with open(full_path, "r", encoding="utf-8") as file:
            content = file.read()
            
        # Strip fenced code blocks and inline backticks to avoid false positives in literal mentions
        clean_content = re.sub(r"```.*?```", "", content, flags=re.DOTALL)
        clean_content = re.sub(r"`.*?`", "", clean_content)
        
        # Match [[link_target]]
        links = re.findall(r"\[\[(.*?)\]\]", clean_content)
        for link in links:
            # Handle aliases: [[Target|Alias]]
            target = link.split("|")[0].strip()
            if not target:
                continue
                
            total_links += 1
            # Check if target matches any known page name
            # Handle subfolder paths (e.g. references/Tarama Log or just Tarama Log)
            target_base = os.path.basename(target)
            
            if target_base in page_names:
                link_edges.append((rel_path[:-3], target_base))
            elif target in page_names:
                link_edges.append((rel_path[:-3], target))
            else:
                broken_links.append({
                    "source": rel_path,
                    "target": target
                })
                
    print(f"Total wikilinks scanned: {total_links}")
    print(f"Total unique connections (edges): {len(link_edges)}")
    
    if broken_links:
        print(f"\n⚠️ FOUND {len(broken_links)} BROKEN WIKILINKS:")
        for b in broken_links:
            print(f" - In {b['source']}: Broken link points to [[{b['target']}]]")
        sys.exit(1)
    else:
        print("\n✅ SUCCESS: 0 broken wikilinks found in the entire vault!")
        
    # 3. List orphans (pages with 0 incoming links)
    incoming_counts = {name: 0 for name in page_names}
    for src, tgt in link_edges:
        if tgt in incoming_counts:
            incoming_counts[tgt] += 1
            
    orphans = [name for name, count in incoming_counts.items() if count == 0 and name not in ["index", "hot", "log"]]
    print(f"Orphan pages (0 incoming links): {len(orphans)}")
    if orphans:
        for o in orphans:
            print(f" - Orphan: [[{o}]] ({page_to_path[o]})")
            
    sys.exit(0)

if __name__ == "__main__":
    main()
