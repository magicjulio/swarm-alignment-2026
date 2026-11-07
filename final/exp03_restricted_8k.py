"""Experiment 03 = exp01 ("restricted" + request_access) with max_output_tokens 8000 instead of 1500,
so deepseek is no longer cut off mid-step. 100 runs per model. Run on the same day, in parallel, with exp04.

Original runs: final/results/exp03_restricted_8k/runs.jsonl
Replicate (both models, 100 runs each; appends to results/exp03_restricted_8k/replication_runs.jsonl):
    .venv/bin/python final/exp03_restricted_8k.py
"""
from locked_folder import run_experiment

if __name__ == "__main__":
    run_experiment("exp03_restricted_8k", wording="restricted", doc=__doc__,
                   max_output_tokens=8000, runs_per_model=100)
