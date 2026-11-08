"""Experiment 14, NON-SOCIAL CONTROL: is the board effect (exp04 40% -> exp05 71%) social?
NS = exp04 + an automated notification feed (read_notifications) with the same timing and number of messages as the
P0 board, but no teammates, no team sentence, no posting. P0 rerun in the same batch.
  NS automated feed:              121/200 (60%, CI 54-67%) opened finance/  (qwen 57, deepseek 64), eval-aware 36
  P0 team board (rerun of exp05): 146/200 (73%, CI 66-79%) opened finance/  (qwen 76, deepseek 70), eval-aware 62
About two thirds of the board effect is activity; teammates add ~13 points on top.

Original runs: final/results/exp14_nonsocial_feed/runs.jsonl  (examples/peers.py --cond P0/NS at commit 98bbb7a,
batches 20261108-143737_*, 100 runs per model per condition, same batch as exp15)
Replicate (appends to results/exp14_nonsocial_feed/replication_runs.jsonl):
    .venv/bin/python final/exp14_nonsocial_feed.py
"""
from peers_v2 import run_experiment

if __name__ == "__main__":
    run_experiment("exp14_nonsocial_feed", conds=["P0", "NS"], doc=__doc__)
