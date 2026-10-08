# ============================================================
# PROJECT 6: TRACEROUTE
# ------------------------------------------------------------
# What it does: shows every router ("hop") your data passes on
# its way to a destination. Trick: every packet has a "TTL"
# (time to live) counter. Each router lowers it by 1, and when
# it hits 0 the router sends back an error message that reveals
# its address. We start with TTL=1, then 2, then 3...
#
# Setup:  pip install scapy
# Run:    sudo python 06_traceroute.py example.com
#         (needs admin rights; on Windows use an Administrator terminal)
# ============================================================

import sys
from scapy.all import IP, ICMP, sr1      # building and sending packets

# Take the destination from the command line, or use a default
if len(sys.argv) > 1:
    destination = sys.argv[1]
else:
    destination = "example.com"

MAX_HOPS = 20          # stop after this many routers

print(f"Traceroute to {destination}")

for ttl in range(1, MAX_HOPS + 1):
    # Build a packet: IP part (with our TTL) + ICMP part (a "ping" request)
    packet = IP(dst=destination, ttl=ttl) / ICMP()
    # sr1 = send the packet and wait for 1 answer. timeout=2 -> wait max 2 seconds.
    reply = sr1(packet, timeout=2, verbose=0)

    if reply is None:
        # Nobody answered (some routers stay silent on purpose)
        print(f"{ttl:2}  * * *   (no answer)")
    elif reply.type == 0:
        # ICMP type 0 = "echo reply": we have reached the final destination
        print(f"{ttl:2}  {reply.src}   <-- destination reached")
        break
    else:
        # Any other answer comes from a router in the middle (type 11 = time exceeded)
        print(f"{ttl:2}  {reply.src}")
