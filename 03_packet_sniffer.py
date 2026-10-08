# ============================================================
# PROJECT 3: PACKET SNIFFER
# ------------------------------------------------------------
# What it does: listens to network traffic on YOUR OWN network
# and shows who talks to whom (IP addresses, ports, DNS names),
# then prints a count per protocol.
# Only sniff on networks you own or have permission to monitor!
#
# Setup:  pip install scapy
# Run:    sudo python 03_packet_sniffer.py        (Linux/Mac, needs admin rights)
#         On Windows: run the terminal as Administrator and install Npcap.
# Stop with Ctrl+C or wait until 50 packets were captured.
# ============================================================

from scapy.all import sniff, IP, TCP, UDP, DNS, DNSQR   # tools from the scapy library

counts = {"TCP": 0, "UDP": 0, "DNS": 0, "Other": 0}     # a tally of what we have seen


def handle_packet(packet):
    """scapy calls this function once for every captured packet."""
    # Only look at packets that have an IP part (skip other kinds)
    if not packet.haslayer(IP):
        counts["Other"] += 1
        return

    source = packet[IP].src           # who sent it
    destination = packet[IP].dst      # who receives it

    if packet.haslayer(DNS) and packet.haslayer(DNSQR):
        # DNS = the "phone book" that turns names into IP addresses
        counts["DNS"] += 1
        name = packet[DNSQR].qname.decode(errors="ignore")   # the name being looked up
        print(f"DNS  {source} asks for {name}")
    elif packet.haslayer(TCP):
        counts["TCP"] += 1
        print(f"TCP  {source}:{packet[TCP].sport} -> {destination}:{packet[TCP].dport}")
    elif packet.haslayer(UDP):
        counts["UDP"] += 1
        print(f"UDP  {source}:{packet[UDP].sport} -> {destination}:{packet[UDP].dport}")
    else:
        counts["Other"] += 1


print("Sniffing 50 packets... (generate traffic by opening a website)")
# count=50 -> stop after 50 packets. store=False -> don't keep them in memory.
sniff(prn=handle_packet, count=50, store=False)

print("\n--- Summary ---")
for protocol, number in counts.items():
    print(f"{protocol}: {number}")
