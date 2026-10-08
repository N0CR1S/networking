# ============================================================
# PROJECT 4: NETWORK MONITOR
# ------------------------------------------------------------
# What it does: regularly checks if some servers are reachable,
# measures how long the connection takes (latency), saves every
# result in a small database file, and shows a summary with bars.
#
# How to run:   python 04_network_monitor.py
# It checks 5 times (every 2 seconds), then prints a summary.
# Change the list TARGETS below to monitor your own devices.
# ============================================================

import socket      # network connections
import sqlite3     # a small database that lives in one file (built into Python)
import time        # to measure time and to wait

# What to watch: (name, address, port). Port 443 = HTTPS, port 53 = DNS.
TARGETS = [
    ("Google DNS", "8.8.8.8", 53),
    ("Cloudflare", "1.1.1.1", 443),
    ("Example site", "example.com", 443),
]

CHECKS = 5            # how many rounds to run
WAIT_SECONDS = 2      # pause between rounds


def measure(address, port):
    """Try to connect. Returns the time in milliseconds, or None if it failed."""
    start = time.time()                        # remember the current time
    try:
        # create_connection tries to open a TCP connection; timeout=2 -> give up after 2 s
        s = socket.create_connection((address, port), timeout=2)
        s.close()
        return (time.time() - start) * 1000    # seconds -> milliseconds
    except Exception:
        return None                            # None means "no answer"


# Open (or create) the database file and make a table if it doesn't exist yet
db = sqlite3.connect("monitor.db")
db.execute("CREATE TABLE IF NOT EXISTS results (time TEXT, name TEXT, latency REAL)")

for round_number in range(CHECKS):
    print(f"--- Round {round_number + 1} of {CHECKS} ---")
    for name, address, port in TARGETS:
        latency = measure(address, port)
        timestamp = time.strftime("%Y-%m-%d %H:%M:%S")   # current date and time as text
        # Save the result. The ? marks are filled with the values in the brackets.
        db.execute("INSERT INTO results VALUES (?, ?, ?)", (timestamp, name, latency))
        if latency is None:
            print(f"{name}: NO ANSWER")
        else:
            print(f"{name}: {latency:.1f} ms")
    db.commit()                                # make sure everything is really saved
    if round_number < CHECKS - 1:
        time.sleep(WAIT_SECONDS)               # wait before the next round

# ---- Summary: average latency and packet loss per target, with a text bar ----
print("\n=== SUMMARY (all data in monitor.db) ===")
for name, address, port in TARGETS:
    # Ask the database for every latency of this target
    rows = db.execute("SELECT latency FROM results WHERE name = ?", (name,)).fetchall()
    values = [r[0] for r in rows if r[0] is not None]    # only successful checks
    failed = len(rows) - len(values)                     # the rest are failures
    if values:
        average = sum(values) / len(values)
        bar = "#" * int(average / 5)                     # one # per 5 ms
        print(f"{name:14} avg {average:6.1f} ms  lost {failed}/{len(rows)}  {bar}")
    else:
        print(f"{name:14} never reachable")

db.close()
