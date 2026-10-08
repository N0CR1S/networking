# ============================================================
# PROJECT 2: CHAT ROOM (server + client in ONE file)
# ------------------------------------------------------------
# What it does: lets several people chat. One computer runs the
# "server" (the middleman), the others run "clients".
#
# How to run (open TWO or more terminal windows):
#   Window 1:  python 02_chat.py server
#   Window 2:  python 02_chat.py client
#   Window 3:  python 02_chat.py client
# Type a message and press Enter. Type "quit" to leave.
# ============================================================

import socket        # network connections
import sys           # to read what you typed after the file name
import threading     # lets two things happen at the same time

HOST = "127.0.0.1"   # "this computer". Use the server's real IP to chat across computers.
PORT = 5000          # the "door number" the server listens on


# ------------------------------------------------------------
# SERVER PART
# ------------------------------------------------------------
clients = []         # a list that remembers everybody who is connected


def send_to_all(message, sender):
    """Send a message to every connected client except the one who wrote it."""
    for c in clients:
        if c is not sender:
            try:
                c.send(message)
            except Exception:
                pass              # if sending fails, that person probably left


def handle_client(conn, address):
    """Runs once per connected person (each gets their own thread)."""
    print(f"{address} joined")
    clients.append(conn)          # add the person to our list
    try:
        while True:               # keep listening until they leave
            data = conn.recv(1024)    # wait for up to 1024 bytes
            if not data:          # empty data means the person disconnected
                break
            send_to_all(data, conn)   # pass the message on to the others
    except Exception:
        pass
    # Cleanup after the person left
    print(f"{address} left")
    if conn in clients:
        clients.remove(conn)
    conn.close()


def run_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # allows quick restart
    server.bind((HOST, PORT))     # claim the address and port
    server.listen()               # start waiting for visitors
    print(f"Server running on {HOST}:{PORT}. Press Ctrl+C to stop.")
    while True:
        conn, address = server.accept()   # wait here until somebody connects
        # Start a separate thread so this person doesn't block the others
        t = threading.Thread(target=handle_client, args=(conn, address), daemon=True)
        t.start()


# ------------------------------------------------------------
# CLIENT PART
# ------------------------------------------------------------
def receive_messages(sock):
    """Runs in the background and prints whatever the server sends."""
    while True:
        try:
            data = sock.recv(1024)
            if not data:
                break
            print("\n" + data.decode())       # bytes -> text, then print
        except Exception:
            break
    print("Disconnected from server.")


def run_client():
    name = input("Your name: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((HOST, PORT))                # connect to the server
    # Start the background listener so we can receive while typing
    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()
    print("Connected! Type messages. Type 'quit' to leave.")
    while True:
        text = input()                        # wait for you to type something
        if text == "quit":
            break
        message = f"{name}: {text}"
        sock.send(message.encode())           # text -> bytes, then send
    sock.close()


# ------------------------------------------------------------
# START: decide whether to be server or client
# ------------------------------------------------------------
if __name__ == "__main__":
    if len(sys.argv) < 2 or sys.argv[1] not in ("server", "client"):
        print("Usage: python 02_chat.py server   OR   python 02_chat.py client")
    elif sys.argv[1] == "server":
        run_server()
    else:
        run_client()
