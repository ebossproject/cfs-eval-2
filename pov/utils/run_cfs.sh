#!/bin/bash
set -Eeuo pipefail

LOG_FILE=$1

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

function on_exit {
  EXIT_CODE=$?
  if [ $EXIT_CODE -ge 128 ]; then
    SIGNAL=$((EXIT_CODE - 128))
    echo "cFS crashed with signal $SIGNAL (exit code $EXIT_CODE)" >> "$LOG_FILE"
    # Optional: append the last 20 lines of stdout/stderr if needed
  else
    echo "cFS exited normally with code $EXIT_CODE" >> "$LOG_FILE"
  fi
}

trap on_exit EXIT

/cfs/core-cpu1 "$@" > "$LOG_FILE" 2>&1

