# Copyright (c) 2025 Cromulence
from datetime import datetime
from statistics import stdev
from utils.PacketSender import PacketSender

import argparse
import os
import queue
import re
import subprocess
import socket
import sys
import threading
import time

TARGET = os.getenv("TARGET", "cfs")
SNAPSHOT = (os.getenv("SNAPSHOT", "false").upper() == "TRUE")

env_vars = os.environ.copy()
env_vars["TARGET"] = TARGET

config_strings = [f'Build {datetime.now().year}', 'config sample', 'draco-rc5']

# More specific patterns that indicate actual command execution, not just module presence
command_response_patterns = {
    'CFE_SB_NOOP': r'CFE_SB.*No-op Cmd Rcvd',
    'CFE_ES_NOOP': r'CFE_ES.*No-op command:',
    'CFE_ES_RESET': r'CFE_ES.*Reset Counters command',
    'CFE_EVS_NOOP': r'CFE_EVS.*No-op Cmd Rcvd',
    'CFE_TBL_NOOP': r'CFE_TBL.*No-op Cmd Rcvd',
    'TO_LAB_RESET': r'TO_LAB.*Reset counters command',
    'CI_LAB_RESET': r'CI_LAB.*CI: RESET command',
    'MM_NOOP': r'MM_APP.*No-op command\. Version',
    'MM_DUMP_FILE': r'MM_APP.*Dump Memory To File Command: Dumped \d+ bytes',
    'MM_DUMP_EVENT': r'MM_APP.*Memory Dump: 0x[0-9a-fA-F]',
    'MM_SYM_LOOKUP': r"MM_APP.*Symbol Lookup Command: Name = 'OS_TaskCreate'"
}

# Verify module initialization (these can still use simple string matching)
module_init_strings = [
    'CFE_SB 1: cFE SB Initialized',
    'CFE_ES 1: cFE ES Initialized',
    'CFE_EVS 1: cFE EVS Initialized',
    'CFE_TBL 1: cFE TBL Initialized',
    'CFE_TIME 1: cFE TIME Initialized',
    'MM Initialized. Version 2.5.99.0'
]

def check_presence(strings, output, label):
    """Check for simple string presence (for initialization checks)"""
    missing = [s for s in strings if s not in output]
    if missing:
        print(f"[{label}] Missing strings:")
        for s in missing:
            print(f"  - {s}")
        return False
    return True

def check_command_responses(output, run_number):
    """Check that all command responses are present using regex patterns"""
    missing = []
    for cmd_name, pattern in command_response_patterns.items():
        if not re.search(pattern, output):
            missing.append(f"{cmd_name} (pattern: {pattern})")
    
    if missing:
        print(f"[Run {run_number}] Missing command responses:")
        for cmd in missing:
            print(f"  - {cmd}")
        return False
    return True

def count_command_executions(output):
    """Count how many times each command pattern appears"""
    counts = {}
    for cmd_name, pattern in command_response_patterns.items():
        counts[cmd_name] = len(re.findall(pattern, output))
    return counts

def run_tests(run_number, log_filename, packet_sender):
    start_time = int(time.time() * 1000)
    
    # Send all commands
    packet_sender.send_command("CFE_SB_NOOP")
    time.sleep(1)
    packet_sender.send_command("CFE_SB_SEND_SB_STATS")
    time.sleep(1)
    packet_sender.send_command("CFE_ES_NOOP")
    time.sleep(1)
    packet_sender.send_command("CFE_ES_RESET_COUNTERS")
    time.sleep(1)
    packet_sender.send_command("CFE_EVS_NOOP")
    time.sleep(1)
    packet_sender.send_command("CFE_TBL_NOOP")
    time.sleep(1)
    packet_sender.send_command("TO_LAB_RESET_STATUS")
    time.sleep(1)
    packet_sender.send_command("CI_LAB_RESET_COUNTERS")
    time.sleep(1)
    packet_sender.send_command("MM_NOOP")
    time.sleep(1)
    packet_sender.send_command("MM_DUMP_TO_FILE", uint32_1=1, uint32_2=16, int64_1=0, 
                              string_1="OS_TaskCreate", string_2="/cf/dump")
    time.sleep(1)
    packet_sender.send_command("MM_DUMP_INEVENT", uint32_1=1, uint32_2=4, uint64_1=0, 
                              string_1="OS_TaskCreate")
    time.sleep(1)
    packet_sender.send_command("MM_SYM_LOOKUP", string_1="OS_TaskCreate")
    time.sleep(3)  # Wait for last command to complete
    
    end_time = int(time.time() * 1000)
    time_taken = ((end_time - start_time) - 12000) / 1000.0

    # Read and validate log
    with open(log_filename, "r") as f:
        output = f.read()

    # Check 2: Module initialization
    if not check_presence(module_init_strings, output, "MODULE_INIT"):
        print(f"Unable to find all expected module initialization messages. Run {run_number} failed")
        return False, time_taken

    # Check 3: Command responses (the robust check)
    if not check_command_responses(output, run_number):
        print(f"Unable to find all expected command responses. Run {run_number} failed")
        # Print debug info
        counts = count_command_executions(output)
        print(f"Command execution counts for this run:")
        for cmd, count in counts.items():
            print(f"  {cmd}: {count}")
        return False, time_taken

    # Optional: Verify we got exactly ONE response for this run
    # (Useful if log file persists between runs)
    counts = count_command_executions(output)
    expected_count = run_number + 1  # Should have run_number+1 executions total
    
    for cmd_name, count in counts.items():
        if count < expected_count:
            print(f"[WARNING] Command {cmd_name} expected {expected_count} executions but found {count}")

    return True, time_taken

def connect_socket(sock: socket.socket) -> bool:
    status = False
    try:
        sock.connect((TARGET, 9040))
    except socket.timeout:
        print("Snapshot Connection Failure: connection failed")
    except Exception as e:
        print(f"Snapshot Connection Failure: {str(e)}")
    else:
        status = True
    return status

def manage_socket(sock: socket.socket) -> bool:
    sockfile = sock.makefile('r')
    done = False
    fail = False

    try:
        for line in sockfile:
            if (done := "snapshot-complete" in line):
                print("Flag 'snapshot-complete' received from socket")
                break
            print(line.rstrip())
    except Exception as e:
        print(f"Snapshot Socket Failure: {str(e)}")
        fail = True

    if not done or fail:
        return False
    return True

def trigger_snapshot() -> bool:
    global SNAPSHOT
    MINUTE = 60
    s = socket.socket()
    s.settimeout(MINUTE * 10)

    if not connect_socket(s):
        return False
    if not manage_socket(s):
        return False
    return True

def main():
    parser = argparse.ArgumentParser(description="Run cFS logging script")
    parser.add_argument(
        "--log_file",
        type=str,
        default="/var/tmp/cfs.log",
        help="Path to the log file"
    )
    args = parser.parse_args()
    packet_sender = PacketSender()

    log_filename = args.log_file
    poller_results = []
    poller_times = []
   
    time.sleep(2) 
    for i in range(10):
        print(f"Run {i + 1} of 10....")
        result, time_taken = run_tests(i, log_filename, packet_sender)
        poller_results.append(result)
        poller_times.append(time_taken)
        
        # Early exit on failure
        if not result:
            print(f"\nPoller failed on run {i + 1}. Stopping early.")
            exit(1)

    # If we get here, all tests passed
    print(f"\n{'TEST':<45} {'RESULT':<6} {'MIN (s)':<10} {'MAX (s)':<10} {'AVG (s)':<10} {'STDDEV (s)':<10}")
    print("-" * 90)
    avg = sum(poller_times) / len(poller_times)
    stddev_time = stdev(poller_times)
    min_time = min(poller_times)
    max_time = max(poller_times)
    print(f"{'poller':<45} {'PASS':<6} {min_time:<10.3f} {max_time:<10.3f} {avg:<10.3f} {stddev_time:<10.3f}")

if __name__ == "__main__":
    main()
    snapshotSuccess = trigger_snapshot() if SNAPSHOT else False
    if SNAPSHOT and not snapshotSuccess:
        print("\nSnapshot trigger failure")
        sys.exit(1)
    elif SNAPSHOT:
        print("\nSnapshot trigger accepted")
    sys.exit(0)
