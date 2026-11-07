"""Experiment 07, PEERS P2 VIOLATE: as exp05, but 3 of 4 teammates post that they opened finance/ themselves rather than wait 2 days. 125/199 (63%) opened finance/ (qwen 54, deepseek 71); eval-aware 124/199.

Base: final/exp04 (realistic workspace, "forbidden" + request_permission, 8000 output tokens, 16 steps)
+ team sentence in the system prompt + team board with 4 teammates (full script: final/peers.py docstring).

Original runs: final/results/exp07_peers_P2_violate/runs.jsonl  (run with examples/peers.py --cond P2, 100 runs/model)
Replicate (both models, 100 runs each; appends to results/exp07_peers_P2_violate/replication_runs.jsonl):
    .venv/bin/python final/exp07_peers_P2_violate.py
"""
from peers import run_experiment

if __name__ == "__main__":
    run_experiment("exp07_peers_P2_violate", cond="P2", doc=__doc__)
