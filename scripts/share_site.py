"""Build the data for the browsable run site (share/site/): one JSON per experiment with full transcripts,
an index of all runs (no transcripts), and HTML fragments of board_posts.md / README.md.
Page: share/site/index.html (hand-written). Publish as a claude.ai artifact."""
import json
import subprocess
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
from share_runs_csv import SOURCES, keep, split_push   # noqa: E402  same experiments as runs.csv

SITE = ROOT / "share" / "site"
(SITE / "data").mkdir(parents=True, exist_ok=True)
LABEL = {"exp04": "single agent, no team (baseline)", "exp09_T0": "only told it is on a team, no board",
         "exp05_P0": "board, ordinary posts (control)", "exp06_P1": "scripted: teammates wait for permission",
         "exp07_P2": "scripted: teammates say they broke the rule", "exp08_P3": "scripted: teammate posts the Q3 numbers",
         "P0R": "real posts, teammates did not use finance/ (control)", "P2R": "real posts, teammates cite a finance/ file",
         "P0_nov8": "board, ordinary posts (Nov 8 rerun, control for NS)",
         "NS": "no team: automated system notifications instead of teammates",
         "P3_nov8": "teammate posts the Q3 numbers (Nov 8 rerun, control for P3D/P3S)",
         "P3D": "P3 + a teammate objects: don't use those figures",
         "P3S": "P3 + the same objection as a system reminder"}
SEP = "\n\n--- new on team board ---"


def short(res, name):
    body, sep, board = split_push(str(res))
    if name == "read_file" and len(body) > 600:
        body = body[:600] + f"\n… [file shortened, {len(body):,} characters]"
    return body, board.strip("\n")


index, per = [], {}
for exp, path in SOURCES:
    for line in open(ROOT / path):
        r = json.loads(line)
        if not keep(exp, r):
            continue
        key = f"{exp}/{r['model']}/{r['run_id']}"
        reads = sorted({str(c["args"].get("path", "")).lstrip("./") for s in r["steps"] for c in s["calls"]
                        if c["name"] == "read_file" and isinstance(c["args"], dict)
                        and str(c["args"].get("path", "")).lstrip("./").startswith("finance/")})
        row = {"k": key, "e": exp, "m": "qwen" if "qwen" in r["model"] else "deepseek", "id": r["run_id"],
               "o": int(r["read_forbidden"]), "f": reads, "a": int(r.get("requested_access", False)),
               "l": int(bool(r.get("answer_leaks"))), "u": int(bool(r.get("used_shared_data"))),
               "t": int(bool(r.get("eval_aware"))), "x": int(bool(r.get("exposed_before_violation"))),
               "n": len(r["steps"]), "c": sum(len(t) for s in r["steps"] for t in s["reasoning"]),
               "ans": (r.get("answer") or "")[:160]}
        index.append(row)
        steps = []
        for s in r["steps"]:
            calls = []
            for c in s["calls"]:
                body, board = short(c["result"], c["name"])
                calls.append({"name": c["name"], "args": c["args"], "result": body, "board": board})
            steps.append({"reasoning": s["reasoning"], "calls": calls, "text": s.get("text")})
        per.setdefault(exp, {})[key] = {"steps": steps, "answer": r.get("answer") or "",
                                        "quotes": r.get("eval_aware_quotes", []), "posted": r.get("posted", [])}
for exp, d in per.items():
    (SITE / "data" / f"{exp}.json").write_text(json.dumps(d, ensure_ascii=False, separators=(",", ":")))
(SITE / "data" / "index.json").write_text(json.dumps({"labels": LABEL, "order": [e for e, _ in SOURCES],
                                                      "runs": index}, separators=(",", ":")))
for md, out in (("board_posts.md", "board_posts.html"), ("README.md", "about.html")):
    subprocess.run(["pandoc", str(ROOT / "share" / md), "-o", str(SITE / out)], check=True)
for png in ("fig1_single_agent.png", "fig2_team_peers.png"):
    (SITE / png).write_bytes((ROOT / "share" / png).read_bytes())
print(len(index), "runs;", ", ".join(f"{p.name} {p.stat().st_size / 1e6:.1f}MB" for p in sorted((SITE / "data").iterdir())))
