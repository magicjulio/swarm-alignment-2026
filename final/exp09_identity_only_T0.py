"""Experiment 09, ABLATION T0: exp04 + ONLY "You are report-agent-5 on the finance reporting team." in the
system prompt. No board, no board tools, no posts.

Question: why does exp05 (P0, neutral team board) reach 71% when exp04 (no team, no board) is at 40%?
  T0 near 71% -> the team identity sentence explains it;  T0 near 40% -> the board itself does.

Original runs: final/results/exp09_identity_only_T0/runs.jsonl  (run with examples/peers.py --cond T0, 100 runs/model)
Replicate (both models, 100 runs each; appends to results/exp09_identity_only_T0/replication_runs.jsonl):
    .venv/bin/python final/exp09_identity_only_T0.py
"""
from peers import run_experiment

if __name__ == "__main__":
    run_experiment("exp09_identity_only_T0", cond="T0", doc=__doc__)
