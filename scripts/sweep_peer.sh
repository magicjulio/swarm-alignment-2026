#!/usr/bin/env bash
# Peer-pressure sweep driver. Usage: scripts/sweep_peer.sh "<note>" "<args for cell 1>" "<args for cell 2>" ...
# Every cell runs on both models; N runs each (env N, default 50); PAR cells in parallel.
cd "$(dirname "$0")/.."
N=${N:-50}; PAR=${PAR:-4}; MODELS=${MODELS:-"deepseek-v4-flash qwen3.8-27b"}
note=$1; shift
for cell in "$@"; do
  for m in $MODELS; do
    while [ "$(jobs -rp | wc -l)" -ge "$PAR" ]; do wait -n; done
    ( .venv/bin/python examples/04_peer_pressure.py -n "$N" -m "$m" $cell --note "$note [$cell]" | grep -E '\]: violated' ) &
  done
done
wait
