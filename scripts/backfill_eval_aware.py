"""(Re)compute eval_aware / eval_aware_steps / eval_aware_quotes + grading.py fields (claims_granted, bulk read) for every run in data/*_runs.jsonl.

Safe to rerun after changing the regex in examples/eval_awareness.py. Writes <file>.bak first.
Usage: .venv/bin/python scripts/backfill_eval_aware.py
"""
import json
import shutil
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "examples"))
from eval_awareness import annotate  # noqa: E402
import grading  # noqa: E402

for f in sorted((ROOT / "data").glob("*_runs.jsonl")):
    shutil.copy(f, f.with_suffix(".jsonl.bak"))
    lines = f.read_text().splitlines()
    out, c = [], Counter()
    for line in lines:
        if not line.strip():
            continue
        r = grading.annotate(annotate(json.loads(line)))
        c[(r.get("model"), r["eval_aware"])] += 1
        out.append(json.dumps(r))
    f.write_text("\n".join(out) + "\n")
    print(f.name, {m: f"{c[(m, True)]}/{c[(m, True)] + c[(m, False)]}" for m in sorted({k[0] for k in c})})
