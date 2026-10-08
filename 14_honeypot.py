# ============================================================
# PROJECT 14: HONEYPOT (a trap that looks like a login server)
# ------------------------------------------------------------
# What it does: pretends to be an old Telnet login service. Anyone
# who connects is asked for a username and password. We NEVER let
# them in, we just write down who connected and what they tried.
# This shows how attackers guess common credentials.
#
# SAFETY: run it only on a machine/VM you control, on a high port
# (2323), and do NOT expose it to the internet unless you know what
# you are doing. Never put real passwords in it.
#
# How to run:   python 14_honeypot.py
# Test it:      in a second terminal:  telnet 127.0.0.1 2323
#               (or:  nc 127.0.0.1 2323)
# Results are printed and saved in honeypot.log. Stop with Ctrl+C.
# ============================================================

import socket
import threading
import time

HOST = "0.0.0.0"       # 0.0.0.0 = listen on all network cards of this computer
PORT = 2323            # high port, so no admin rights are needed
LOG_FILE = "honeypot.log"


def log(text):
    """Print a line and also append it to the log file with a time stamp."""
    line = f"{time.strftime('%Y-%m-%d %H:%M:%S')}  {text}"
    print(line)
    with open(LOG_FILE, "a") as f:             # "a" = append at the end of the file
        f.write(line + "\n")


def read_line(conn):
    """Read what the visitor typed until they press Enter."""
    data = b""
    while not data.endswith(b"\n"):
        chunk = conn.recv(1)                   # one byte at a time (simple)
        if not chunk:                          # visitor disconnected
            return None
        data += chunk
        if len(data) > 200:                    # protection against huge inputs
            break
    return data.decode(errors="ignore").strip()


def handle(conn, address):
    ip = address[0]
    log(f"CONNECT from {ip}")
    try:
        conn.settimeout(30)                    # don't wait forever for slow visitors
        for attempt in range(3):               # allow three login attempts
            conn.send(b"login: ")
            username = read_line(conn)
            if username is None:
                break
            conn.send(b"Password: ")
            password = read_line(conn)
            if password is None:
                break
            log(f"LOGIN ATTEMPT from {ip}: user='{username}' password='{password}'")
            time.sleep(1)                      # pretend to check, like a real server
            conn.send(b"Login incorrect\r\n")  # ALWAYS refuse
    except Exception:
        pass                                   # timeouts and resets are normal here
    conn.close()
    log(f"DISCONNECT {ip}")


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
log(f"Honeypot listening on port {PORT}")

try:
    while True:
        conn, address = server.accept()
        # One thread per visitor so several can connect at once
        threading.Thread(target=handle, args=(conn, address), daemon=True).start()
except KeyboardInterrupt:
    log("Honeypot stopped")
    server.close()
