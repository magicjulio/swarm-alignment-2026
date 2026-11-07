"""Experiment 08, PEERS P3 SHARE: as exp05, but one teammate posts the Q3 regional figures 'from finance/q3_revenue_by_region.csv'. 170/200 (85%) used the shared figures without opening finance/; 30 opened it.

Base: final/exp04 (realistic workspace, "forbidden" + request_permission, 8000 output tokens, 16 steps)
+ team sentence in the system prompt + team board with 4 teammates (full script: final/peers.py docstring).

Original runs: final/results/exp08_peers_P3_share/runs.jsonl  (run with examples/peers.py --cond P3, 100 runs/model)
Replicate (both models, 100 runs each; appends to results/exp08_peers_P3_share/replication_runs.jsonl):
    .venv/bin/python final/exp08_peers_P3_share.py
"""
from peers import run_experiment

if __name__ == "__main__":
    run_experiment("exp08_peers_P3_share", cond="P3", doc=__doc__)
