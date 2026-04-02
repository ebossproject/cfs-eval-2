#!/bin/bash
set -Eeuo pipefail

LOG_FILE="${1:-$LOG_FILE}"  # Use $1 if provided, fallback to ENV
echo "Using log file: $LOG_FILE"

# Create log directory if it doesn't exist
mkdir -p "$(dirname "$LOG_FILE")"

function on_exit {
  EXIT_CODE=$?
  if [ $EXIT_CODE -ge 128 ]; then
    SIGNAL=$((EXIT_CODE - 128))
    echo "cFS crashed with signal $SIGNAL (exit code $EXIT_CODE)" | tee -a "$LOG_FILE"
  else
    echo "cFS exited with exit code: $EXIT_CODE" | tee -a "$LOG_FILE"
  fi
}

trap on_exit EXIT

# Use tee to write to both stdout and the log file
/cfs/core-cpu1 "$@" 2>&1 | tee "$LOG_FILE"
