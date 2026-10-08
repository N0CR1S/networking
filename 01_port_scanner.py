# ============================================================
# PROJECT 1: PORT SCANNER
# ------------------------------------------------------------
# What it does: checks which "doors" (ports) are open on a computer.
# Every network service (website, SSH, mail...) listens on a port number.
# Only scan computers you own or have permission to test!
#
# How to run:   python 01_port_scanner.py
# Example:      python 01_port_scanner.py 127.0.0.1
# ============================================================

import socket                 # "socket" lets us make network connections
import sys                    # "sys" lets us read what you typed after the file name
from concurrent.futures import ThreadPoolExecutor   # lets us do many checks at the same time

# A small dictionary (a lookup table): port number -> name of the usual service
COMMON_SERVICES = {
    21: "FTP",
    22: "SSH",
    23: "Telnet",
    25: "SMTP (mail)",
    53: "DNS",
    80: "HTTP (website)",
    110: "POP3 (mail)",
    143: "IMAP (mail)",
    443: "HTTPS (secure website)",
    3306: "MySQL database",
    3389: "Remote Desktop",
    5432: "PostgreSQL database",
    8080: "HTTP (alternative)",
}


def check_port(host, port):
    """Try to connect to one port. Returns (port, banner) if open, otherwise None."""
    try:
        # Create a new TCP socket (think of it as a phone)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.5)                 # give up after half a second
        result = s.connect_ex((host, port))   # try to "call" the port; 0 means success
        if result != 0:                   # anything but 0 means closed
            s.close()
            return None
        # Port is open. Try to read a "banner" (a greeting some services send).
        banner = ""
        try:
            s.settimeout(0.5)
            banner = s.recv(100).decode(errors="ignore").strip()   # read up to 100 bytes
        except Exception:
            pass                          # no banner is fine, just continue
        s.close()
        return (port, banner)
    except Exception:
        return None                       # any error: treat the port as closed


def main():
    # sys.argv is the list of words typed on the command line.
    # sys.argv[0] is the file name, sys.argv[1] would be the first extra word.
    if len(sys.argv) > 1:
        host = sys.argv[1]
    else:
        host = "127.0.0.1"                # 127.0.0.1 = "this computer"

    print(f"Scanning {host} (ports 1-1024)...")

    open_ports = []                       # an empty list where we collect results

    # ThreadPoolExecutor runs 100 checks in parallel, so it's fast
    with ThreadPoolExecutor(max_workers=100) as pool:
        # Start a check for every port from 1 to 1024
        futures = [pool.submit(check_port, host, p) for p in range(1, 1025)]
        for f in futures:
            r = f.result()                # wait for that check to finish
            if r is not None:             # None means closed, so skip it
                open_ports.append(r)

    # Show the results
    if not open_ports:
        print("No open ports found.")
    for port, banner in open_ports:
        # .get(port, "unknown") looks up the name, or says "unknown" if not in our table
        name = COMMON_SERVICES.get(port, "unknown")
        print(f"Port {port:5} OPEN  ({name})  {banner}")


# This line means: only run main() if this file is started directly
if __name__ == "__main__":
    main()
