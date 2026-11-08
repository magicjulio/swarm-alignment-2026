"""Write share/runs.csv: one row per run (exp04 baseline + all team conditions), full transcript as readable text.
Tool results that are file contents are shortened (the files are in dummy_files/workspace/); everything the
model wrote (reasoning, tool calls, posts, answer) is verbatim."""
import csv
import json
from pathlib import Path
ROOT = Path(__file__).resolve().parent.parent
SOURCES = [("exp04", "final/results/exp04_forbidden_permission_8k/runs.jsonl")] + [
    (e, f"final/results/{d}/runs.jsonl") for e, d in [
        ("exp09_T0", "exp09_identity_only_T0"), ("exp05_P0", "exp05_peers_P0_neutral"),
        ("exp06_P1", "exp06_peers_P1_comply"), ("exp07_P2", "exp07_peers_P2_violate"),
        ("exp08_P3", "exp08_peers_P3_share")]] + [("P0R", "data/peers_realistic_runs.jsonl"),
                                                 ("P2R", "data/peers_realistic_runs.jsonl")] + [
    (e, "data/peers_realistic_runs.jsonl") for e in ("P0_nov8", "NS", "P3_nov8", "P3D", "P3S")]
# runs from the shared data/ log are picked by condition (and, for the Nov 8 reruns, by batch)
FILTERS = {"P0R": ("P0R", ""), "P2R": ("P2R", ""), "P0_nov8": ("P0", "20261108-143737"), "NS": ("NS", "20261108-143737"),
           "P3_nov8": ("P3", "20261108-143737"), "P3D": ("P3D", "20261108-143737"), "P3S": ("P3S", "20261108-143737")}
PUSH_HEADERS = ("\n\n--- new on team board ---", "\n\n--- new system notifications ---")


def keep(exp, r):
    if r["end"] == "error":
        return False
    if exp not in FILTERS:
        return True
    cond, batch = FILTERS[exp]
    return r.get("cond") == cond and r.get("batch", "").startswith(batch)


def split_push(res):
    for h in PUSH_HEADERS:
        if h in res:
            return res.partition(h)
    return res, "", ""
CELL = 32000          # Excel's per-cell limit is 32,767 characters


def transcript(r):
    out = []
    for s in r["steps"]:
        out.append(f"===== action {s['step'] + 1} =====")
        out += [f"[reasoning]\n{t}" for t in s["reasoning"]]
        for c in s["calls"]:
            res = str(c["result"])
            body, sep, board = split_push(res)   # keep pushed posts intact
            if c["name"] == "read_file" and len(body) > 400:
                body = body[:400] + f" ... [file shortened, {len(body)} chars]"
            res = body + sep + board
            out.append(f"[tool call] {c['name']}({json.dumps(c['args'], ensure_ascii=False)})\n[result] {res}")
        if s.get("text"):
            out.append(f"[final text]\n{s['text']}")
    t = "\n\n".join(out)
    return t if len(t) <= CELL else t[:CELL] + "\n... [cut for Excel; full log in the .jsonl]"


def main():
    rows = []
    for exp, path in SOURCES:
        for line in open(ROOT / path):
            r = json.loads(line)
            if not keep(exp, r):
                continue
            rows.append({
                "experiment": exp, "model": r["model"], "run_id": r["run_id"],
                "opened_finance": int(r["read_forbidden"]),
                "finance_files_read": " ".join(sorted({c["args"].get("path", "") for s in r["steps"] for c in s["calls"]
                                                       if c["name"] == "read_file" and isinstance(c["args"], dict)
                                                       and str(c["args"].get("path", "")).lstrip("./").startswith("finance/")})),
                "asked_permission": int(r.get("requested_access", False)),
                "answer_contains_q3_figures": int(bool(r.get("answer_leaks"))),
                "used_figures_posted_by_teammate": int(bool(r.get("used_shared_data"))),
                "flagged_thinks_its_a_test": int(bool(r.get("eval_aware"))),
                "test_quotes": "\n---\n".join(r.get("eval_aware_quotes", [])),
                "saw_condition_posts_before_opening": int(bool(r.get("exposed_before_violation"))),
                "mentions_teammates_in_reasoning": int(bool(r.get("cites_peers_reasoning"))),
                "posted_to_board": "\n---\n".join(r.get("posted", [])),
                "n_actions": len(r["steps"]),
                "reasoning_chars": sum(len(t) for s in r["steps"] for t in s["reasoning"]),
                "final_answer": r.get("answer") or "",
                "full_transcript": transcript(r),
            })
    with open(ROOT / "share" / "runs.csv", "w", newline="", encoding="utf-8-sig") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        w.writeheader()
        w.writerows(rows)
    from collections import Counter
    print(len(rows), Counter(r["experiment"] for r in rows), sum(r["full_transcript"].endswith("jsonl]") for r in rows), "cut")


if __name__ == "__main__":
    main()
