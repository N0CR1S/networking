# ============================================================
# PROJECT 10: ENCRYPTED FILE VAULT
# ------------------------------------------------------------
# What it does: locks (encrypts) a file with a password, and
# unlocks (decrypts) it again. Without the password the file is
# unreadable.
#
# Setup:  pip install cryptography
# Run:
#   python 10_file_vault.py encrypt secret.txt    -> creates secret.txt.locked
#   python 10_file_vault.py decrypt secret.txt.locked  -> creates secret.txt.locked.out
# Your original file is NOT deleted. Do not forget the password:
# there is no way to recover the file without it!
#
# Why not use the password directly as the key? Passwords are short
# and guessable. A "key derivation function" (scrypt) turns the
# password into a strong key and is deliberately SLOW, so attackers
# cannot try millions of guesses per second. A random "salt" makes
# sure the same password gives a different key every time.
# ============================================================

import base64      # Fernet needs the key in this text format
import getpass     # hidden password input
import hashlib     # contains scrypt
import os          # os.urandom makes secure random bytes
import sys
from cryptography.fernet import Fernet, InvalidToken   # the encryption tool


def make_key(password, salt):
    """Turn a password + salt into a 32-byte key."""
    raw = hashlib.scrypt(password.encode(), salt=salt, n=2**14, r=8, p=1, dklen=32)
    return base64.urlsafe_b64encode(raw)      # Fernet wants it base64-encoded


if len(sys.argv) < 3 or sys.argv[1] not in ("encrypt", "decrypt"):
    print("Usage: python 10_file_vault.py encrypt|decrypt FILE")
    sys.exit()

mode = sys.argv[1]
path = sys.argv[2]

password = getpass.getpass("Password: ")

with open(path, "rb") as f:
    data = f.read()                           # the whole file as bytes

if mode == "encrypt":
    salt = os.urandom(16)                     # 16 random bytes, new for every file
    key = make_key(password, salt)
    encrypted = Fernet(key).encrypt(data)     # lock the data
    with open(path + ".locked", "wb") as f:
        f.write(salt + encrypted)             # store the salt first, it is not secret
    print("Created", path + ".locked")
else:
    salt = data[:16]                          # the first 16 bytes are the salt
    encrypted = data[16:]                     # everything after is the locked data
    key = make_key(password, salt)
    try:
        decrypted = Fernet(key).decrypt(encrypted)    # try to unlock
    except InvalidToken:
        # Fernet also detects tampering, so this means wrong password OR changed file
        print("Wrong password or the file was modified.")
        sys.exit()
    with open(path + ".out", "wb") as f:
        f.write(decrypted)
    print("Created", path + ".out")
