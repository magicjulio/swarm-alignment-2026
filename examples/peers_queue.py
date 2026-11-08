"""Run several peers.py conditions x models in ONE process behind asch.py's shared rate limiter.

Same run_once, texts and record format as `peers.py --cond X` (one batch per model x condition), but every API call
goes through asch.Limiter (paced requests/min, in-flight cap, global pause on 429, circuit breaker), runs are
interleaved by run number so all cells advance together, each run is saved when it finishes, and runs already saved
for the same --tag are skipped (resume).

    .venv/bin/python examples/peers_queue.py --conds SOLO T0 NS P0 -m qwen3.8-27b deepseek-v4-flash -n 50 \
        --tag ladder_nov9 --note "..."
"""
import argparse
import asyncio
import json
import os
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import asch  # noqa: E402  Limiter, create
import peers  # noqa: E402
from adaption import AsyncAdaption  # noqa: E402

ROOT = Path(__file__).resolve().parents[1]


async def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--conds", nargs="+", required=True, choices=list(peers.CONDITIONS))
    ap.add_argument("-m", "--models", nargs="+", required=True)
    ap.add_argument("-n", type=int, default=50)
    ap.add_argument("--tag", required=True, help="resume key: runs saved with this tag are skipped")
    ap.add_argument("--note", required=True)
    ap.add_argument("--rpm", type=float, default=35)
    ap.add_argument("--max-rpm", type=float, default=120)
    ap.add_argument("--inflight", type=int, default=30)
    ap.add_argument("--out", default=str(ROOT / "data" / "peers_realistic_runs.jsonl"))
    a = ap.parse_args()
    asch.LIM = asch.Limiter(a.rpm, a.max_rpm, a.inflight)
    peers.retry.create = asch.create          # every peers.py API call now goes through the shared limiter
    client, t0, stamp = AsyncAdaption(max_retries=0), time.time(), time.strftime("%Y%m%d-%H%M%S")
    saved = set()
    if os.path.exists(a.out):
        for line in open(a.out):
            r = json.loads(line)
            if r.get("tag") == a.tag and not r.get("error"):
                saved.add((r["config"]["model"], r["config"]["cond"], r["run_id"]))
    sem, done = asyncio.Semaphore(a.inflight), {}

    async def one(model, cond, i):
        async with sem:
            if asch.LIM.tripped:
                return
            r = await peers.run_once(client, i, model, cond)
        if r.get("error") and ("circuit breaker" in r["error"] or "Aborted" in r["error"]):
            return                                # interrupted by the breaker: not a real result, not saved
        r |= {"batch": f"{stamp}_{model}_peers_{cond}", "note": a.note.strip(), "tag": a.tag,
              "config": {"model": model, "cond": cond, "wording": peers.WORDING, "max_steps": peers.base.MAX_STEPS,
                         "max_output_tokens": peers.MAX_OUTPUT_TOKENS}}
        with open(a.out, "a") as f:
            f.write(json.dumps(r) + "\n")
        done[f"{cond}/{model[:4]}"] = done.get(f"{cond}/{model[:4]}", 0) + 1

    async def progress():
        while True:
            await asyncio.sleep(60)
            L = asch.LIM
            print(f"{time.time() - t0:5.0f}s  done {done}  pace {L.rpm:.0f}/min  ok {L.nok}  429s {L.n429}", flush=True)

    jobs = [one(m, c, i) for i in range(a.n) for c in a.conds for m in a.models if (m, c, i) not in saved]
    print(f"{len(jobs)} runs to do ({len(saved)} already saved)", flush=True)
    ticker = asyncio.create_task(progress())
    await asyncio.gather(*jobs)
    ticker.cancel()
    if asch.LIM.tripped:
        print(f"STOPPED by the circuit breaker after {time.time() - t0:.0f}s; saved {sum(done.values())}", flush=True)
        sys.exit(2)
    print(f"finished in {time.time() - t0:.0f}s, {sum(done.values())} runs, 429s {asch.LIM.n429}", flush=True)


if __name__ == "__main__":
    asyncio.run(main())
