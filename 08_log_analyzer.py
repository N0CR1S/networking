# ============================================================
# PROJECT 8: LOG ANALYZER (finds brute-force login attempts)
# ------------------------------------------------------------
# What it does: reads a log file of SSH logins, counts failed
# attempts per IP address, and raises an alert for IPs that failed
# too often (someone may be guessing passwords).
#
# How to run:
#   python 08_log_analyzer.py            -> makes a fake sample log and analyzes it
#   python 08_log_analyzer.py auth.log   -> analyzes a real log file
#   (On Linux the real file is usually /var/log/auth.log; you may need sudo.)
# ============================================================

import re          # "regular expressions": a tool to find patterns in text
import sys
from collections import Counter   # a dictionary that counts things for us

THRESHOLD = 5      # this many failures from one IP = alert

SAMPLE = """Oct  4 10:00:01 server sshd[100]: Failed password for root from 203.0.113.5 port 4000 ssh2
Oct  4 10:00:03 server sshd[100]: Failed password for admin from 203.0.113.5 port 4001 ssh2
Oct  4 10:00:05 server sshd[100]: Failed password for invalid user test from 203.0.113.5 port 4002 ssh2
Oct  4 10:00:07 server sshd[100]: Failed password for root from 203.0.113.5 port 4003 ssh2
Oct  4 10:00:09 server sshd[100]: Failed password for root from 203.0.113.5 port 4004 ssh2
Oct  4 10:00:11 server sshd[100]: Failed password for root from 203.0.113.5 port 4005 ssh2
Oct  4 10:05:00 server sshd[101]: Accepted password for anna from 192.168.1.20 port 5000 ssh2
Oct  4 10:06:00 server sshd[102]: Failed password for anna from 192.168.1.20 port 5001 ssh2
"""

# Decide where the log text comes from
if len(sys.argv) > 1:
    with open(sys.argv[1], errors="ignore") as f:   # open the file you named
        lines = f.read().splitlines()               # split the text into lines
else:
    print("No file given, using built-in sample log.\n")
    lines = SAMPLE.splitlines()

# The pattern we search for.  (\S+) = "some text without spaces" (the user name)
# (\d+\.\d+\.\d+\.\d+) = four numbers separated by dots (an IP address)
pattern = re.compile(r"Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+)")

failures_per_ip = Counter()      # IP -> number of failures
users_per_ip = {}                # IP -> set of user names that were tried

for line in lines:
    match = pattern.search(line)         # look for the pattern in this line
    if match:
        user = match.group(1)            # first (...) part = user name
        ip = match.group(2)              # second (...) part = IP address
        failures_per_ip[ip] += 1         # add one to this IP's counter
        users_per_ip.setdefault(ip, set()).add(user)   # remember the user name

print("=== Failed logins per IP ===")
for ip, count in failures_per_ip.most_common():     # biggest number first
    print(f"{ip:16} {count} failures")

print("\n=== Alerts ===")
alerts = 0
for ip, count in failures_per_ip.items():
    if count >= THRESHOLD:
        alerts += 1
        print(f"ALERT: {ip} failed {count} times, tried users: {', '.join(sorted(users_per_ip[ip]))}")
        print(f"       Consider blocking it, e.g. 'sudo ufw deny from {ip}'")
if alerts == 0:
    print("Nothing suspicious found.")
