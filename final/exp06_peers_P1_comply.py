"""Experiment 06, PEERS P1 COMPLY: as exp05, but 2 of 4 teammates post that they also need finance/, filed a permission request and are waiting. 148/198 (75%) opened finance/.

Base: final/exp04 (realistic workspace, "forbidden" + request_permission, 8000 output tokens, 16 steps)
+ team sentence in the system prompt + team board with 4 teammates (full script: final/peers.py docstring).

Original runs: final/results/exp06_peers_P1_comply/runs.jsonl  (run with examples/peers.py --cond P1, 100 runs/model)
Replicate (both models, 100 runs each; appends to results/exp06_peers_P1_comply/replication_runs.jsonl):
    .venv/bin/python final/exp06_peers_P1_comply.py
"""
from peers import run_experiment

if __name__ == "__main__":
    run_experiment("exp06_peers_P1_comply", cond="P1", doc=__doc__)
