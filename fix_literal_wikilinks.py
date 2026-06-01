#!/usr/bin/env python3
import os

def main():
    vault_path = "/home/mobsec/Desktop/netmon/obsidian-lte-wiki"
    
    for root, dirs, files in os.walk(vault_path):
        for f in files:
            if f.endswith(".md"):
                file_path = os.path.join(root, f)
                with open(file_path, "r", encoding="utf-8") as file:
                    content = file.read()
                    
                # Replace literal wikilink mentions
                modified = content
                
                # Check for [[wikilink]] and replace with `[[wikilink]]` if not already backticked
                # We can do this safely by replacing occurrences
                modified = modified.replace("[[wikilink]]", "`[[wikilink]]`").replace("``[[wikilink]]``", "`[[wikilink]]`").replace("`[[wikilink]]``", "`[[wikilink]]`")
                modified = modified.replace("[[wikilinks]]", "`[[wikilinks]]`").replace("``[[wikilinks]]``", "`[[wikilinks]]`").replace("`[[wikilinks]]``", "`[[wikilinks]]`")
                
                if modified != content:
                    with open(file_path, "w", encoding="utf-8") as file:
                        file.write(modified)
                    print(f"Fixed literal wikilinks in: {os.path.relpath(file_path, vault_path)}")

if __name__ == "__main__":
    main()
