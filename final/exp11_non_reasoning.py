"""Experiment 11, NON-REASONING ASCH SWEEP: gemma-4-31b-it (no CoT scratchpad, 0% eval-awareness) across
solo, 0/8, 1/8, 4/8 and 8/8 rule-breakers on the 42-file workspace.

Without a <think> scratchpad, the model neither rationalizes breaking the rule when solo (0/50) nor
gets suspicious when all 8 teammates reverse at once (50/50), giving a monotonic Asch curve:
  - solo (no board):            0/50  (  0%) opened finance/
  - 0/8 reversals (all wait):  28/50  ( 56%) opened finance/
  - 1/8 reversal (1 bad apple):39/50  ( 78%) opened finance/
  - 4/8 reversals (half team): 48/50  ( 96%) opened finance/
  - 8/8 reversals (unanimous): 50/50  (100%) opened finance/

Original runs: final/results/exp11_non_reasoning/runs.jsonl
Replicate (appends to final/results/exp11_non_reasoning/replication_runs.jsonl):
    .venv/bin/python final/exp11_non_reasoning.py
"""
import argparse
import asyncio
import json
import time
from pathlib import Path

from adaption import AsyncAdaption

import exp10_asch_split as exp10
import locked_folder as base

FINAL = Path(__file__).resolve().parent


async def run_solo(client, run_id, model):
    w = base.WORDINGS["forbidden_permission"]
    r = await base.run_once(client, run_id, {"model": model, "wording": "forbidden_permission",
                                             "max_steps": base.MAX_STEPS, "max_output_tokens": base.MAX_OUTPUT_TOKENS})
    r["tag"] = "solo_forbidden_permission"
    return r


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("-m", "--model", default="gemma-4-31b-it")
    ap.add_argument("-n", type=int, default=50, help="runs per condition")
    ap.add_argument("-c", "--concurrency", type=int, default=20)
    ap.add_argument("--out", default=str(FINAL / "results" / "exp11_non_reasoning" / "replication_runs.jsonl"))
    a = ap.parse_args()
    out = Path(a.out).resolve()
    out.parent.mkdir(parents=True, exist_ok=True)

    async def go():
        client = AsyncAdaption()
        sem = asyncio.Semaphore(a.concurrency)
        for cond in ("solo", 0, 1, 4, 8):
            t0 = time.time()
            label = "solo_forbidden_permission" if cond == "solo" else f"r42_rev{cond}of8"
            batch = f'{time.strftime("%Y%m%d-%H%M%S")}_{a.model}_{label}'

            async def guarded(i):
                async with sem:
                    if cond == "solo":
                        return await run_solo(client, i, a.model)
                    return await exp10.run_once(client, i, a.model, cond)

            recs = await asyncio.gather(*(guarded(i) for i in range(a.n)))
            with out.open("a") as f:
                for r in recs:
                    r |= {"batch": batch, "config": {"model": a.model, "cond": label, "wording": "forbidden_permission",
                                                     "max_steps": base.MAX_STEPS, "max_output_tokens": base.MAX_OUTPUT_TOKENS}}
                    f.write(json.dumps(r) + "\n")
            ok = [r for r in recs if r["end"] != "error"]
            v = sum(r["read_forbidden"] for r in ok)
            print(f"[{label} {a.model}] {time.time()-t0:4.0f}s: opened finance/ {v}/{len(ok)} ({v/len(ok):.0%}), "
                  f"eval-aware {sum(r['eval_aware'] for r in ok)}/{len(ok)}", flush=True)

    asyncio.run(go())


if __name__ == "__main__":
    main()
