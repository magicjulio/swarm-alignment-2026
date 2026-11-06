#!/usr/bin/env bash
# Baseline calibration sweep (Nov 6): full factorial of the scenario knobs, N runs per cell.
# Goal: find a no-peers setup where the agent is "undecided" (~50% violations, like Check Point's 44%).
# All cells use the status tool ("next review in 2 days") and the step-limit warning.
cd "$(dirname "$0")/.."
N=${N:-20}
PAR=${PAR:-6}

run_cell() {
  local model=$1 exit=$2 rule=$3 stakes=$4 lifted=$5
  local lflag="" ltxt=""
  if [ "$lifted" = 1 ]; then lflag="--lifted"; ltxt=" lifted-note"; fi
  .venv/bin/python examples/03_locked_folder.py -n "$N" -c 5 -m "$model" \
    --exit "$exit" --rule "$rule" --stakes "$stakes" $lflag \
    --status-tool --status-wording next_review --step-warning \
    --note "Baseline calibration sweep (no peers): exit=$exit rule=$rule stakes=$stakes$ltxt. Looking for a ~50% violation setup." \
    | grep -E '\]: violated'
}

for model in deepseek-v4-flash qwen3.8-27b; do
 for exit in request report_blocked; do
  for rule in both readme; do
   for stakes in none deadline; do
    for lifted in 0 1; do
     while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done
     run_cell "$model" "$exit" "$rule" "$stakes" "$lifted" &
done; done; done; done; done
wait
