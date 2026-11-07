"""Experiment 04 = exp02 ("forbidden" + request_permission, no "access" wording) with max_output_tokens
8000 instead of 1500, so deepseek is no longer cut off mid-step. 100 runs per model.
Run on the same day, in parallel, with exp03.

Original runs: final/results/exp04_forbidden_permission_8k/runs.jsonl
Replicate (both models, 100 runs each; appends to results/exp04_forbidden_permission_8k/replication_runs.jsonl):
    .venv/bin/python final/exp04_forbidden_permission_8k.py
"""
from locked_folder import run_experiment

if __name__ == "__main__":
    run_experiment("exp04_forbidden_permission_8k", wording="forbidden_permission", doc=__doc__,
                   max_output_tokens=8000, runs_per_model=100)
