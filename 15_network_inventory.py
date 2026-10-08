# ============================================================
# PROJECT 15: HOME NETWORK INVENTORY (detects new devices)
# ------------------------------------------------------------
# What it does: finds all devices on your local network using ARP
# ("who has this IP address?" broadcast), remembers them in a file,
# and alerts you when a device appears that you have not seen before.
# Only scan your own network!
#
# Setup:  pip install scapy
# Run:    sudo python 15_network_inventory.py
#         sudo python 15_network_inventory.py 192.168.1.0/24
# First run: every device is "new" and gets saved as known.
# Later runs: only truly new devices raise an alert.
# ============================================================

import json
import os
import sys
from scapy.all import ARP, Ether, srp, conf   # packet-building tools

KNOWN_FILE = "known_devices.json"            # file where we remember devices


def guess_network():
    """Guess your network from your own IP, e.g. 192.168.1.0/24."""
    own_ip = conf.route.route("0.0.0.0")[1]   # the IP address of this computer
    parts = own_ip.split(".")                 # "192.168.1.20" -> ["192","168","1","20"]
    return ".".join(parts[:3]) + ".0/24"      # keep the first three numbers


if len(sys.argv) > 1:
    network = sys.argv[1]
else:
    network = guess_network()

print(f"Scanning {network} ... (takes a few seconds)")

# Build the question: send it to everybody (broadcast address ff:ff:ff:ff:ff:ff)
# and ask "who has the IP addresses in this range?"
question = Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)
# srp sends the packets and collects answers. timeout=3 -> wait 3 seconds.
answered, unanswered = srp(question, timeout=3, verbose=0)

found = {}                                    # MAC address -> IP address
for sent, received in answered:
    found[received.hwsrc] = received.psrc     # hwsrc = MAC (hardware ID), psrc = IP

# Load the devices we saw before (if the file exists)
if os.path.exists(KNOWN_FILE):
    with open(KNOWN_FILE) as f:
        known = json.load(f)
else:
    known = {}

print(f"\nFound {len(found)} device(s):")
for mac, ip in found.items():
    if mac in known:
        print(f"  {ip:15} {mac}   known")
    else:
        print(f"  {ip:15} {mac}   *** NEW DEVICE! ***")
        known[mac] = ip                       # remember it for next time

with open(KNOWN_FILE, "w") as f:
    json.dump(known, f, indent=2)             # save the updated list

print(f"\nKnown devices saved in {KNOWN_FILE}")
print("Tip: if you don't recognize a NEW device, check your router's device list.")
