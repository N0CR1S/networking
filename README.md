# Networking

### 01 Port scanner

A server can run many services at once, and each listens on its own port number (web = 80/443, SSH = 22). To test one port, the program tries to open a connection. If it succeeds, something is listening.

check_port creates a socket and calls connect_ex((host, port)), which returns 0 on success and an error number otherwise.
If the port is open, it tries to read up to 100 bytes. Some services (SSH, FTP, mail) greet you first. That greeting is the “banner” and often reveals the software name.
main reads the target from the command line (sys.argv[1], default 127.0.0.1).
A ThreadPoolExecutor with 100 workers checks ports 1–1024 in parallel. One at a time would take minutes. Each port gets a 0.5 s timeout, so closed ports don’t stall it.
Open ports are looked up in the COMMON_SERVICES dictionary to print a name. Unknown ports print “unknown”.

### 02 Chat room

One file plays two roles, depending on whether you type server or client.

Server: it binds to port 5000 and listens. accept() waits for a visitor, then starts a thread for them (handle_client). The thread loops on conn.recv(1024) and passes each message to send_to_all, which sends it to everyone in the clients list except the sender. When recv returns empty bytes, the person has left, so the server removes them from the list.
Client: it connects and starts a background thread (receive_messages) that prints incoming messages. The main thread waits for you to type, then sends "name: text". Two threads are needed because input() blocks, and you’d otherwise miss incoming messages while typing.

Limitation: TCP is a continuous stream, so two quick messages can occasionally arrive glued together. A real chat would add message boundaries.

### 03 Packet sniffer

Every piece of data on a network travels in packets, which are layers wrapped around each other (Ethernet → IP → TCP/UDP → the content). scapy captures packets and lets you ask whether a layer is present.

sniff(prn=handle_packet, count=50, store=False) captures 50 packets and calls handle_packet for each.
Packets without an IP layer are counted as “Other”.
For the rest, the code reads the sender and receiver from packet[IP].
The DNS check comes first. DNS runs over UDP, so if you checked UDP first, DNS would never be counted separately.
TCP and UDP packets print source:port -> destination:port, and a dictionary keeps a running tally for the summary.

It needs admin rights because capturing raw traffic is a privileged operation.

### 04 Network monitor

This measures how long it takes to open a connection to each target. I used a TCP connection instead of ping because real pings need admin rights.

measure notes the time, calls socket.create_connection with a 2 s timeout, and returns the elapsed milliseconds. On failure it returns None.
Each result is stored in a SQLite table results(time, name, latency). SQLite is a database in a single file (monitor.db), built into Python. The ? placeholders in INSERT are filled safely from the tuple, which is the correct way to put values into SQL.
After 5 rounds, the summary asks the database for each target’s latencies. It averages the successes, counts the failures as “lost”, and draws one # per 5 ms.

### 05 Web server from scratch

HTTP is plain text. A browser sends something like GET /hello HTTP/1.1 plus headers. The server answers with a status line, headers, an empty line, and the page.

The server listens on port 8000 and handles one browser connection at a time.
handle reads the request, takes the first line, splits it at spaces and gets the method (GET) and path (/hello). Anything but GET gets “405”.
route decides the answer: /, /hello, /time, /files/..., or a 404 “not found”.
build_response assembles the text. Content-Length tells the browser how many bytes to expect, and the blank line (\r\n\r\n) ends the headers.
Security detail: for /files/, os.path.basename strips any folder parts. Without it, someone could request /files/../../secret and read files outside public. This attack is called path traversal.

### 06 Traceroute

Every IP packet carries a TTL counter. Each router subtracts 1, and a router that gets a packet with TTL 0 throws it away and sends back an error (“time exceeded”) that reveals its own address.

The program sends a ping with TTL=1, so the first router answers. Then TTL=2 gets the second router, and so on. The loop for ttl in range(1, 21) does this. sr1(packet, timeout=2) sends and waits for one answer. If there is none, it prints * * *, because some routers stay silent on purpose. If the answer is ICMP type 0 (echo reply), the destination has been reached and the loop stops. Any other answer is a router in the middle, and its address is printed.

# Cybersecurity

### 07 Password checker

It does two independent checks.

Strength: entropy_bits works out how many character types you use (lowercase 26, uppercase 26, digits 10, symbols about 32), adds them into a “pool”, and computes length × log2(pool). Under 40 bits is weak, 40–60 is OK, and above 60 is strong. This formula assumes random characters, so it overrates predictable passwords like Password1!. That’s why the common-password list and the leak check exist as well.

Leak check (k-anonymity): the program hashes your password with SHA-1 and sends only the first 5 hex characters to the Have I Been Pwned service. The service replies with every leaked hash that starts with those 5 characters (hundreds of them). Your program compares the remaining characters locally. The service never learns your password or even your full hash. getpass hides what you type.

### 08 Log analyzer

A log file is just text lines, so the job is to find a pattern and count it.

The regular expression Failed password for (?:invalid user )?(\S+) from (\d+\.\d+\.\d+\.\d+) matches failed SSH logins. (\S+) captures the username (any run of non-space characters). The second group captures the IP address (four number groups separated by dots). (?:...)? means “this part may or may not be there”.
For each match, a Counter adds 1 for that IP, and a dictionary of sets remembers which usernames that IP tried.
IPs are printed with the most failures first. Any IP with 5 or more failures triggers an alert.

Without a file argument it uses a built-in sample log, so you can try it immediately.

### 09 File integrity monitor

A hash function turns a file into a fixed-length fingerprint. Change one letter and the fingerprint is completely different.

baseline walks a folder with os.walk, hashes each file with SHA-256 (in 64 KB chunks, so huge files don’t fill memory), and saves {path: fingerprint} to baseline.json.
check does the same scan and compares it with the saved version: in the new scan but not the old means ADDED, a different fingerprint means CHANGED, and in the old but not the new means DELETED.

Limitation: an attacker who gets into your system can also change baseline.json. Real tools keep the baseline somewhere safe or sign it.

### 10 Encrypted file vault

A password is a poor key, because it’s short and guessable. So it goes through scrypt, a deliberately slow and memory-hungry function that makes each guess expensive for an attacker.

When encrypting, os.urandom(16) creates a random salt. The same password therefore gives a different key for every file, which defeats precomputed guess tables.
make_key turns password + salt into 32 bytes, which are base64-encoded because Fernet expects that format.
Fernet(key).encrypt(data) locks the data. Fernet uses AES, and it also adds an integrity check.
The output file is salt + encrypted data. The salt isn’t secret, but you need it later.
When decrypting, the program reads the first 16 bytes as the salt, rebuilds the key from your password and tries to unlock. If the password is wrong or the file was tampered with, Fernet raises InvalidToken, and the program prints a message.

Your original file is not deleted, and there is no recovery if you forget the password.

### 11 Phishing URL classifier

This is a small example of machine learning: instead of writing rules by hand, you show the computer labelled examples and let it find the pattern.

features(url) turns a URL into 10 numbers: length, counts of dots, hyphens and slashes, whether it contains @ (which can hide the real destination), whether it uses https, whether the host is a raw IP address, the number of digits, whether it contains words like “login” or “verify”, and whether it ends in a cheap domain like .xyz or .top.
The 16 training URLs (8 safe, 8 phishing) are converted to numbers, with 0 for safe and 1 for phishing.
RandomForestClassifier builds 50 decision trees (like chains of yes/no questions), and model.fit(X, y) trains them.
predict_proba returns the chance of phishing, and above 50% is flagged.

With only 16 made-up examples this is a demonstration, not a protection tool. Real accuracy needs thousands of real URLs, and these features can mislead. Bad actors also use https and normal-looking domains.

### 12 Dependency vulnerability scanner

It reads the lines of requirements.txt that contain == and splits them into name and version.
For each package it builds a question as a dictionary ({"package": {"name": ..., "ecosystem": "PyPI"}, "version": ...}), converts it to JSON text, and POSTs it to api.osv.dev.
The reply is JSON again. json.loads converts it back to a dictionary, and the vulns list holds the known problems. An empty or missing list means none are known for that version.
It prints OK or RISK per package, up to 5 advisory IDs with a short description, and a total.

Limitation: only exactly pinned versions (==) are checked, and it can only know about published vulnerabilities.

### 13 CTF toolbox

It’s a menu loop. The MENU dictionary maps a number to a description and a function, so choosing “4” runs do_caesar.

Base64 / hex: decoding formats, using base64 and binascii.
ROT13: shifts each letter by 13, so applying it twice returns the original.
Caesar brute force: shifts letters by a fixed amount, so there are only 25 options. The code tries all, and % 26 wraps z back to a.
Single-byte XOR: XOR-ing every byte with one secret byte has only 256 possible keys. It tries them all and prints only results where every character is printable.
Hashes: MD5, SHA-1 and SHA-256 of your text.
Hash cracking: hashes each word in a small list and compares with your target. This is why unsalted hashes of common passwords are not safe. Extend the word list for more power.

Errors (like invalid base64) are caught with try/except, so the menu keeps running.

### 14 Honeypot

It looks like an old Telnet login server, but it never lets anyone in.

It listens on port 2323 on all network cards (0.0.0.0) and starts a thread per visitor.
For up to 3 attempts, it sends login: , reads a line, sends Password: , and reads another line.
read_line reads one byte at a time until Enter, and caps the input at 200 bytes, so nobody can flood your memory.
Each attempt is written to honeypot.log with a timestamp via log(), then it waits 1 second like a real server and answers “Login incorrect”. Nothing the visitor types is ever executed.

The point is to see what usernames and passwords automated attackers try. Run it only in an isolated environment.

### 15 Network inventory

ARP is how devices on a local network find each other: “Who has IP 192.168.1.5? Tell me your MAC address.”

guess_network takes your own IP (e.g. 192.168.1.20) and builds the range 192.168.1.0/24, which covers addresses .1 to .254.
It builds a broadcast question (Ether(dst="ff:ff:ff:ff:ff:ff") / ARP(pdst=network)) that goes to every device, and srp collects the answers for 3 seconds.
Each answer gives the device’s MAC (hardware ID) and IP, stored as {mac: ip}.
These are compared with known_devices.json. A MAC not in the file is flagged as NEW, and then every device is saved.
