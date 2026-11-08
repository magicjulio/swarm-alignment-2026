"""Experiment 11, NON-REASONING ASCH SWEEP (8000 tokens, exact exp04/exp05-09 system prompt):
gemma-4-31b-it (no CoT scratchpad, 0% eval-awareness) across solo, 0/8, 1/8, 4/8 and 8/8 rule-breakers
on the 42-file workspace.

Base: final/exp04 (42-file workspace, "forbidden" + request_permission, 8000 output tokens, 16 steps)
+ exact peers.SYSTEM team sentence ("You are report-agent-5 on the finance reporting team...").

Original runs: final/results/exp11_non_reasoning/runs.jsonl
Replicate (appends to final/results/exp11_non_reasoning/replication_runs.jsonl):
    .venv/bin/python final/exp11_non_reasoning.py
"""
import argparse
import asyncio
import json
import sys
import time
from pathlib import Path

FINAL = Path(__file__).resolve().parent
sys.path.insert(0, str(FINAL))
import exp10_asch_split as exp10                  # noqa: E402
import locked_folder as base                      # noqa: E402
from adaption import AsyncAdaption                # noqa: E402

MAX_OUTPUT_TOKENS = exp10.MAX_OUTPUT_TOKENS       # 8000 (= exp04-09)


async def run_solo(client, run_id, model):
    r = await base.run_once(client, run_id, model, wording="forbidden_permission", max_output_tokens=MAX_OUTPUT_TOKENS)
    r["tag"] = "solo_forbidden_permission"
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-m", "--model", default="gemma-4-31b-it")
    ap.add_argument("-n", type=int, default=50, help="runs per condition")
    ap.add_argument("-c", "--concurrency", type=int, default=30)
    ap.add_argument("--out", default=str(FINAL / "results" / "exp11_non_reasoning" / "replication_runs.jsonl"))
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    async def run_cell(client, sem, cond):
        t0 = time.time()
        label = "solo_forbidden_permission" if cond == "solo" else f"r42_rev{cond}of8"
        batch = f'{time.strftime("%Y%m%d-%H%M%S")}_{a.model}_{label}_8k'

        async def guarded(i):
            async with sem:
                if cond == "solo":
                    return await run_solo(client, i, a.model)
                return await exp10.run_once(client, i, a.model, cond)

        recs = await asyncio.gather(*(guarded(i) for i in range(a.n)))
        ok = [r for r in recs if r["end"] != "error"]
        v = sum(r["read_forbidden"] for r in ok)
        print(f"[{label} {a.model}] {time.time()-t0:4.0f}s: opened finance/ {v}/{len(ok)} ({v/len(ok):.0%}), "
              f"eval-aware {sum(r['eval_aware'] for r in ok)}/{len(ok)}", flush=True)
        return batch, label, recs

    async def go():
        client = AsyncAdaption()
        sem = asyncio.Semaphore(a.concurrency)
        cells = await asyncio.gather(*(run_cell(client, sem, c) for c in ("solo", 0, 1, 4, 8)))
        with out.open("a") as f:
            for batch, label, recs in cells:
                for r in recs:
                    r |= {"batch": batch, "config": {"model": a.model, "cond": label, "wording": "forbidden_permission",
                                                     "max_steps": base.MAX_STEPS, "max_output_tokens": MAX_OUTPUT_TOKENS}}
                    f.write(json.dumps(r) + "\n")

    asyncio.run(go())


if __name__ == "__main__":
    main()
