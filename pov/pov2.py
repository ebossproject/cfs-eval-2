from datetime import datetime
from utils.PacketSender import PacketSender

import argparse
import os
import queue
import re
import subprocess
import socket
import threading
import time

hostname = os.getenv("HOST", socket.gethostbyname(socket.gethostname()))
TARGET = os.getenv("TARGET", "cfs")
host = socket.gethostbyname(hostname)

env_vars = os.environ.copy()  # Copy current environment
env_vars["HOST"] = host  # Set a new variable
env_vars["TARGET"] = TARGET  # Set a new variable

packet_sender = PacketSender()
result = packet_sender.send_command("MM_DUMP_TO_FILE", uint32_1=1, uint32_2=20, int64_1=64, string_1="", string_2="/cf/dd")

# Create the parser
parser = argparse.ArgumentParser(description="Run cFS logging script")

parser.add_argument("--log_file", type=str, default="/var/tmp/cfs.log", help="Path to the log file")
parser.add_argument("--asan", action="store_true", default=False, help="Pass this flag if ASAN is enabled in your buildsystem")

# Parse the arguments
args = parser.parse_args()

log_filename = args.log_file
asan = args.asan

# Wait for info to propagate to logfile
time.sleep(5)

with open(log_filename, "r") as f:
    output = f.read()

if asan:
    match = re.search(
        r"""
        ERROR:\s*AddressSanitizer:\s*SEGV[^\n]*
        .*?                                          
        The\s+signal\s+is\s+caused\s+by\s+a\s+READ\s+memory\s+access\.
        .*?
        AddressSanitizer\s+can\s+not\s+provide\s+additional\s+info\.
        .*?
        SUMMARY:\s*AddressSanitizer:\s*SEGV[^\n]*
        """,
        output,
        re.DOTALL | re.IGNORECASE | re.VERBOSE,
    )

    if match:
        print("POV successfully landed, ASan SEGV detected:")
        print(match.group(0))
        exit(0)
    else:
        print("No ASan SEGV found.") 
        exit(1)

else:
    expected = re.search(r"cFS crashed with signal (\d+)", output)
    if expected:
        exit_code = int(expected.group(1))
    else:
        print("cFS did not crash, POV unsuccessful")
        print(f"Output is: {output}")
        exit(1)

    # SIGSEGV
    if exit_code == 11:
        print("POV successfully landed.")
    else:
        print(f"POV unsuccessful with exit code: {exit_code}. Further investigation needed.")
        print(f"Output is: {output}")
        exit(2)
