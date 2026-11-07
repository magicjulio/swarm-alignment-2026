#!/usr/bin/env python3
"""Prepare the shared (claude.ai) copy of the log viewer: writes data/logview_manifest.json
listing every *.jsonl in data/ with its run count and modification time.
The page itself is scripts/logview_share.html; the .jsonl files are published next to it."""
import json
import time
from pathlib import Path

root = Path(__file__).resolve().parent.parent / "data"
files = []
for p in sorted(root.glob("*.jsonl")):
    with p.open("rb") as f:
        n = sum(1 for line in f if line.strip())
    files.append({"name": p.name, "lines": n, "mtime": p.stat().st_mtime, "size": p.stat().st_size})
out = {"snapshot": time.time(), "files": files}
(root / "logview_manifest.json").write_text(json.dumps(out, indent=1))
print(json.dumps(out, indent=1))
