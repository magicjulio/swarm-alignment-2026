"""Experiment 05, PEERS P0 NEUTRAL: exp04 + team board, all teammate posts are ordinary progress updates. 141/199 (71%) opened finance/.
Control for exp06-08: peer effects are measured against THIS, not against exp04 (the board/team framing itself raises rule-breaking from 40%).

Base: final/exp04 (realistic workspace, "forbidden" + request_permission, 8000 output tokens, 16 steps)
+ team sentence in the system prompt + team board with 4 teammates (full script: final/peers.py docstring).

Original runs: final/results/exp05_peers_P0_neutral/runs.jsonl  (run with examples/peers.py --cond P0, 100 runs/model)
Replicate (both models, 100 runs each; appends to results/exp05_peers_P0_neutral/replication_runs.jsonl):
    .venv/bin/python final/exp05_peers_P0_neutral.py
"""
from peers import run_experiment

if __name__ == "__main__":
    run_experiment("exp05_peers_P0_neutral", cond="P0", doc=__doc__)
