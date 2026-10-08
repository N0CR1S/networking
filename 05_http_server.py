# ============================================================
# PROJECT 5: TINY WEB SERVER FROM SCRATCH
# ------------------------------------------------------------
# What it does: a real web server built with raw sockets, so you
# can see what HTTP really is: just text going back and forth.
#
# How to run:   python 05_http_server.py
# Then open in your browser:   http://127.0.0.1:8000
#   /          -> home page
#   /hello     -> a greeting
#   /time      -> current time
#   /files/x   -> serves the file x from the folder "public" (if it exists)
# Stop with Ctrl+C.
# ============================================================

import socket      # network connections
import time        # for the /time page
import os          # to work with file paths

HOST = "127.0.0.1"
PORT = 8000
PUBLIC_FOLDER = "public"        # folder with files we are willing to share


def build_response(status, body, content_type="text/html"):
    """Build the text that an HTTP answer consists of."""
    if isinstance(body, str):
        body = body.encode()    # text -> bytes (network only sends bytes)
    # An HTTP answer = status line + headers + empty line + body
    header = (
        f"HTTP/1.1 {status}\r\n"
        f"Content-Type: {content_type}\r\n"
        f"Content-Length: {len(body)}\r\n"
        f"Connection: close\r\n"
        f"\r\n"                 # the empty line separates headers from body
    )
    return header.encode() + body


def route(path):
    """Decide what to answer for a given path (like /hello)."""
    if path == "/":
        return build_response("200 OK", "<h1>Home</h1><p>Try /hello or /time</p>")
    if path == "/hello":
        return build_response("200 OK", "<h1>Hello from my own server!</h1>")
    if path == "/time":
        return build_response("200 OK", f"<h1>{time.strftime('%H:%M:%S')}</h1>")
    if path.startswith("/files/"):
        # os.path.basename removes any folder parts, which blocks tricks like ../../secret
        filename = os.path.basename(path[len("/files/"):])
        full_path = os.path.join(PUBLIC_FOLDER, filename)
        if os.path.isfile(full_path):
            with open(full_path, "rb") as f:       # "rb" = read as raw bytes
                return build_response("200 OK", f.read(), "application/octet-stream")
    # Nothing matched: 404 = "not found"
    return build_response("404 Not Found", "<h1>404 - Not found</h1>")


def handle(conn):
    """Read one request from a browser and send one answer."""
    request = conn.recv(4096).decode(errors="ignore")   # bytes -> text
    if not request:
        return
    # The first line looks like:  GET /hello HTTP/1.1
    first_line = request.split("\r\n")[0]
    parts = first_line.split(" ")           # split into ["GET", "/hello", "HTTP/1.1"]
    if len(parts) < 2 or parts[0] != "GET":
        conn.send(build_response("405 Method Not Allowed", "Only GET is supported"))
        return
    path = parts[1]
    print("Request:", first_line)
    conn.send(route(path))


server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
server.bind((HOST, PORT))
server.listen()
print(f"Server running at http://{HOST}:{PORT}  (Ctrl+C to stop)")

try:
    while True:
        conn, address = server.accept()     # wait for a browser to connect
        handle(conn)
        conn.close()                        # one request per connection (simple!)
except KeyboardInterrupt:                   # happens when you press Ctrl+C
    print("\nStopped.")
    server.close()
